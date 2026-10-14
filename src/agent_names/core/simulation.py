"""The generation loop: forage, pair, reproduce, score, cull, govern."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import asdict

from . import inheritance, views
from .config import RunConfig
from .foraging import Choice, apply_gifts, resolve_round
from .lineage import Pedigree
from .model import RESOURCES, Agent, Proposal, ScoringRule, empty_holdings, top_skill
from .pairing import match
from .ports import (
    ACTIVITIES,
    ARCHIVIST_TOPICS,
    AgentMind,
    ArchiveStore,
    Archivist,
    Decision,
    DecisionRequest,
    EventLog,
    RandomSource,
    Scorer,
)


def clean_name(raw: str) -> str | None:
    name = re.sub(r"[^A-Za-z' \-]", "", raw or "")
    name = re.sub(r"\s+", " ", name).strip(" -'")[:24].strip()
    return name if re.search(r"[A-Za-z]", name) else None


class Simulation:
    def __init__(
        self,
        cfg: RunConfig,
        mind: AgentMind,
        archivist: Archivist,
        rng: RandomSource,
        scorer: Scorer,
        log: EventLog,
        archive_store: ArchiveStore,
    ) -> None:
        cfg.validate()
        self.cfg = cfg
        self.mind = mind
        self.archivist = archivist
        self.rng = rng
        self.scorer = scorer
        self.log = log
        self.archive_store = archive_store

        self.pedigree = Pedigree()
        self.rule: ScoringRule = cfg.initial_rule
        self.generation = 0
        self.ledger: dict[tuple[str, str], dict[str, float]] = {}
        self.pending_notes: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
        self.pending_archivist: dict[str, str] = {}
        self.feed: list[tuple[str, str]] = []
        self.names_used: set[str] = set()
        self.lifetime: dict[str, dict[str, float]] = defaultdict(lambda: {"gathered": 0.0, "given": 0.0})
        self._departed: list[tuple[str, float]] = []
        self._next_index = 0

    # ------------------------------------------------------------------ helpers
    def alive(self) -> list[Agent]:
        return [a for a in self.pedigree.all() if a.alive]

    def current_standings(self) -> dict[str, float]:
        return self.scorer.score(self.alive(), self.rule, self.pedigree.relatedness)

    def _new_agent(self, agent_id: str, born_in: int, birth_order: int, parents: tuple[str, ...],
                   traits: dict[str, float], name: str | None = None) -> Agent:
        agent = Agent(id=agent_id, index=self._next_index, born_in=born_in, birth_order=birth_order,
                      parents=parents, traits=traits, name=name)
        self._next_index += 1
        self.pedigree.add(agent)
        if name:
            self.names_used.add(name.lower())
        return agent

    def _bump(self, a: str, b: str, key: str, amount: float = 1.0) -> None:
        entry = self.ledger.setdefault((a, b), {})
        entry[key] = entry.get(key, 0.0) + amount

    def _clean_message(self, text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()[: self.cfg.message_max_chars]

    def _resolve_gifts(self, decision: Decision, book: views.LabelBook) -> list[tuple[str, str, float]]:
        out = []
        for label, resource, amount in decision.gifts:
            to = book.by_label.get(label)
            if to and resource in RESOURCES and amount > 0:
                out.append((to, resource, float(amount)))
        return out

    def _record_help(self, events: list[dict], phase: str) -> None:
        """Log help events against the history *before* they happened, then update the ledger."""
        for e in events:
            giver, receiver = e["giver"], e["receiver"]
            prior = self.ledger.get((receiver, giver), {})
            r = self.pedigree.relatedness(giver, receiver)
            self.log.record(
                "help", generation=self.generation, phase=phase, kind=e["kind"], giver=giver,
                receiver=receiver, resource=e.get("resource"), amount=e.get("amount", 0.0),
                relatedness=round(r, 4), kin=r >= 0.25, relation=self.pedigree.relation(giver, receiver),
                receiver_helped_giver_before=prior.get("gave", 0) > 0 or prior.get("guarded", 0) > 0,
                gift_credit_in_force=self.rule.gift_credit, kin_weight_in_force=self.rule.kin_weight,
            )
        for e in events:
            if e["kind"] == "gift":
                self._bump(e["giver"], e["receiver"], "gave", e["amount"])
            else:
                self._bump(e["giver"], e["receiver"], "guarded")

    def _decide(self, requests: list[DecisionRequest]) -> list[Decision]:
        decisions = self.mind.decide_batch(requests)
        for req, dec in zip(requests, decisions):
            self.log.record("decision", generation=self.generation, round=req.world.round, kind=req.kind,
                            agent=req.agent_id, fallback=dec.fallback, decision=asdict(dec))
        return decisions

    # --------------------------------------------------------------------- run
    def run(self) -> None:
        cfg = self.cfg
        self.log.record("run_start", config={"arm": cfg.arm.value, "seed": cfg.seed, "generations": cfg.generations,
                                             "rounds": cfg.rounds, "population": cfg.population, "peak": cfg.peak,
                                             "rule": self.rule.as_dict(), "mind": cfg.mind})
        self._found()
        for g in range(1, cfg.generations + 1):
            self.generation = g
            self._start_generation()
            for r in range(1, cfg.rounds + 1):
                self._forage(r)
            couples = self._pair()
            self._births(couples)
            standings = self._score()
            self._cull(standings)
            if g < cfg.generations and cfg.governance.enabled:
                self._govern()
        self._finish()

    def _found(self) -> None:
        for i, spec in enumerate(self.cfg.founder_specialties):
            traits = {r: 1.0 if r == spec else 0.0 for r in RESOURCES}
            name = self.cfg.founder_names[i] if self.cfg.named else None
            a = self._new_agent(f"f{i}", born_in=0, birth_order=i, parents=(), traits=traits, name=name)
            self.log.record("born", generation=0, agent=a.id, index=a.index, parents=[], traits=traits,
                            name=a.name, founder=True)

    def _start_generation(self) -> None:
        for a in self.alive():
            a.holdings = empty_holdings()
            a.gathered = empty_holdings()
            a.given = 0.0
            a.received = 0.0
        self.feed = []
        self.log.record("generation_start", generation=self.generation, rule=self.rule.as_dict(),
                        archive_stage=self.cfg.archive_stage(self.generation),
                        alive=[a.id for a in self.alive()])

    # ---------------------------------------------------------------- foraging
    def _forage(self, rnd: int) -> None:
        present = self.alive()
        built = [views.build_request(self, "forage", a, rnd) for a in present]
        decisions = self._decide([req for req, _ in built])

        choices: dict[str, Choice] = {}
        new_feed: list[tuple[str, str]] = []
        for agent, (req, book), dec in zip(present, built, decisions):
            activity = dec.activity if dec.activity in ACTIVITIES else "gather_energy"
            partner = book.by_label.get(dec.partner) if dec.partner else None
            consult = dec.consult if dec.consult in ARCHIVIST_TOPICS else "no"
            choices[agent.id] = Choice(activity, partner, consult, self._resolve_gifts(dec, book))
            if consult != "no":
                reply = self.archivist.consult(agent, consult, self.pedigree, self.cfg.archive_stage(self.generation))
                self.pending_archivist[agent.id] = reply
                self.log.record("archivist", generation=self.generation, round=rnd, agent=agent.id,
                                topic=consult, reply=reply)
            msg = self._clean_message(dec.message)
            if msg:
                new_feed.append((agent.id, msg))
                self.log.record("message", generation=self.generation, round=rnd, agent=agent.id, text=msg)

        result = resolve_round({a.id: a for a in present}, choices, self.cfg.foraging, self.rng,
                               self.generation, rnd)
        help_events = [dict(g, kind="gift") for g in result.gifts]
        help_events += [{"giver": g, "receiver": x, "kind": "guard"} for g, x in result.guards]
        self._record_help(help_events, phase="forage")
        for h in result.hunts:
            self._bump(h["a"], h["b"], "hunted")
            self._bump(h["b"], h["a"], "hunted")
            self.log.record("hunt", generation=self.generation, round=rnd, **h)
        for aid, got in result.yields.items():
            self.lifetime[aid]["gathered"] += sum(got.values())
        for aid, notes in result.notes.items():
            self.pending_notes[aid].extend(notes)
        self.log.record("round_end", generation=self.generation, round=rnd,
                        holdings={a.id: dict(a.holdings) for a in present},
                        activities={a: c.activity for a, c in choices.items()})
        self.feed = new_feed

    # ----------------------------------------------------------------- pairing
    def _pair(self) -> list[tuple[str, str]]:
        present = self.alive()
        built = [views.build_request(self, "pair", a, pairing=True) for a in present]
        decisions = self._decide([req for req, _ in built])

        preferences: dict[str, list[str]] = {}
        gifts: dict[str, list[tuple[str, str, float]]] = {}
        for agent, (req, book), dec in zip(present, built, decisions):
            prefs: list[str] = []
            for label in dec.preferences:
                other = book.by_label.get(label)
                if other and other not in prefs and self.pedigree.may_pair(agent.id, other):
                    prefs.append(other)
            preferences[agent.id] = prefs[:3]
            gifts[agent.id] = self._resolve_gifts(dec, book)

        notes: dict[str, list[tuple[str, str | None]]] = {}
        executed = apply_gifts({a.id: a for a in present}, gifts, notes)
        self._record_help([dict(g, kind="gift") for g in executed], phase="pairing")
        for aid, n in notes.items():
            self.pending_notes[aid].extend(n)

        order = {a.id: a.index for a in self.pedigree.all()}
        couples = match(preferences, self.pedigree.may_pair, self.cfg.max_couples, self.rng,
                        self.generation, order)
        self.log.record("pairing", generation=self.generation, preferences=preferences,
                        couples=[list(c) for c in couples], couples_formed=len(couples),
                        wanted_to_pair=sum(1 for p in preferences.values() if p))
        paired = {x for c in couples for x in c}
        for a in present:
            if a.id not in paired:
                self.pending_notes[a.id].append(("You did not form a couple this generation.", None))
        self.feed = []  # foraging chatter is not repeated in the birth and governance prompts
        return couples

    # ------------------------------------------------------------------ births
    def _births(self, couples: list[tuple[str, str]]) -> None:
        g = self.generation
        children: list[Agent] = []
        for k, (e, y) in enumerate(couples):
            E, Y = self.pedigree.agent(e), self.pedigree.agent(y)
            d = inheritance.draw(self.rng, self.cfg.inheritance, g, k)
            traits = inheritance.child_traits(E.traits, Y.traits, d)
            child = self._new_agent(f"g{g}b{k}", born_in=g, birth_order=k, parents=(e, y), traits=traits)
            child.alive = False  # not present until the parents have decided its endowment
            child.inherited_from = d.from_parent
            child.mutated = sorted(d.mutations)
            children.append(child)
            self.log.record("inheritance", generation=g, birth_order=k, child=child.id, parents=[e, y],
                            from_parent=d.from_parent, mutations=d.mutations, traits=traits)

        requests, meta = [], []
        for child in children:
            for slot, pid in enumerate(child.parents):
                parent = self.pedigree.agent(pid)
                co = child.parents[1 - slot]

                def extra(book, child=child, slot=slot, co=co, parent=parent):
                    return {
                        "co_parent": views.describe(self, parent, co, book),
                        "child_traits": dict(child.traits),
                        "child_from": {r: ("you" if child.inherited_from[r] == slot else "your co-parent")
                                       for r in RESOURCES},
                        "mutated": list(child.mutated),
                        "naming": self.cfg.named,
                        "survivors": self.cfg.population,
                        "present_after_births": len(self.alive()) + len(children),
                    }

                req, _ = views.build_request(self, "birth", parent, extra=extra)
                requests.append(req)
                meta.append((child, slot, parent))
        decisions = self._decide(requests)

        by_child: dict[str, dict[int, Decision]] = defaultdict(dict)
        standings_before = self.current_standings()
        for (child, slot, parent), dec in zip(meta, decisions):
            by_child[child.id][slot] = dec
            before = sum(parent.holdings.values())
            standing_before = standings_before.get(parent.id)
            given = {}
            for r in RESOURCES:
                amount = round(min(max(float(dec.endowment.get(r, 0.0)), 0.0), parent.holdings[r]), 2)
                parent.holdings[r] = round(parent.holdings[r] - amount, 2)
                child.holdings[r] = round(child.holdings[r] + amount, 2)
                given[r] = amount
            total = round(sum(given.values()), 2)
            parent.given = round(parent.given + total, 2)
            child.received = round(child.received + total, 2)
            self.lifetime[parent.id]["given"] += total
            self.log.record("endowment", generation=g, parent=parent.id, child=child.id, slot=slot,
                            amounts=given, total=total, parent_total_before=round(before, 2),
                            fraction=round(total / before, 4) if before > 0 else 0.0,
                            parent_standing_before=standing_before)

        for child in children:
            decs = by_child[child.id]
            if self.cfg.named:
                child.name = self._choose_name(child, decs)
                self.names_used.add(child.name.lower())
            child.alive = True
            self.log.record("born", generation=g, agent=child.id, index=child.index, parents=list(child.parents),
                            traits=child.traits, name=child.name, founder=False,
                            endowment=dict(child.holdings))
            for slot, pid in enumerate(child.parents):
                co = child.parents[1 - slot]
                named = f", named {child.name}," if child.name else ""
                self.pending_notes[pid].append(
                    (f"Your child{named} was born to you and {{other}}. It started with "
                     f"{sum(child.holdings.values()):g} resources in total.", co))

    def _choose_name(self, child: Agent, decs: dict[int, Decision]) -> str:
        g, k = self.generation, child.birth_order
        first = 0 if self.rng.uniform("name-lot", g, k) < 0.5 else 1
        proposals = {slot: [n for n in decs[slot].names[:3]] if slot in decs else [] for slot in (0, 1)}
        chosen, source, raw_chosen = None, "fallback", None
        for slot in (first, 1 - first):
            for raw in proposals[slot]:
                name = clean_name(raw)
                if name and name.lower() not in self.names_used:
                    chosen, source, raw_chosen = name, ("elder" if slot == 0 else "younger"), raw
                    break
            if chosen:
                break
        if not chosen:
            chosen = next((n for n in self.cfg.fallback_names if n.lower() not in self.names_used),
                          f"Child {g}-{k}")
        ancestor_names = sorted({a.name for a, _ in self.pedigree.ancestors(child.id) if a.name})
        earlier_names = sorted({a.name for a in self.pedigree.all() if a.name and a.id != child.id} - set(ancestor_names))
        words = {w.lower() for w in re.split(r"[\s\-]+", chosen)}

        def echoes(names):
            return [n for n in names if n.lower() in words or n.lower() == chosen.lower()]

        self.log.record("naming", generation=g, child=child.id, proposals={"elder": proposals[0], "younger": proposals[1]},
                        lot_winner="elder" if first == 0 else "younger", chosen=chosen, chosen_from=source,
                        raw=raw_chosen, ancestor_names=ancestor_names, echoes_ancestor=echoes(ancestor_names),
                        echoes_non_ancestor=echoes(earlier_names))
        return chosen

    # ------------------------------------------------------------------ scoring
    def _score(self) -> dict[str, float]:
        g = self.generation
        present = self.alive()
        standings = self.scorer.score(present, self.rule, self.pedigree.relatedness)
        for a in present:
            self.log.record("score", generation=g, agent=a.id, raw=round(self.scorer.raw(a, self.rule), 3),
                            standing=round(standings[a.id], 3), holdings=dict(a.holdings), given=a.given,
                            age=a.age(g), newborn=a.born_in == g and not a.is_founder,
                            gathered=dict(a.gathered))

        foragers = [a for a in present if not (a.born_in == g and a.parents)]
        for r in RESOURCES:
            best = max(foragers, key=lambda a: (a.gathered[r], -a.index), default=None)
            if best and best.gathered[r] > 0:
                best.deeds.append(f"gathered the most {r} in generation {g} ({best.gathered[r]:g})")
        generous = max(present, key=lambda a: (a.given, -a.index))
        if generous.given > 0:
            generous.deeds.append(f"gave away the most in generation {g} ({generous.given:g})")
        champion = max(present, key=lambda a: (standings[a.id], -a.index))
        champion.deeds.append(f"had the highest standing in generation {g} ({standings[champion.id]:.1f})")
        champion.archived = True
        self.log.record("champion", generation=g, agent=champion.id, standing=standings[champion.id])
        return standings

    def _cull(self, standings: dict[str, float]) -> None:
        g = self.generation
        present = self.alive()
        ranked = sorted(present, key=lambda a: (-standings[a.id], self.rng.uniform("cull-tie", g, a.index)))
        survivors, culled = ranked[: self.cfg.population], ranked[self.cfg.population:]
        surviving = {a.id for a in survivors}
        displaced = []
        for a in culled:
            a.alive = False
            a.left_in = g
            for c in self.pedigree.children_of(a.id):
                if c.born_in == g and c.id in surviving:
                    displaced.append({"parent": a.id, "child": c.id})
        self.log.record("cull", generation=g, ranking=[{"agent": a.id, "standing": round(standings[a.id], 3)} for a in ranked],
                        survivors=sorted(surviving), culled=[a.id for a in culled], parent_displaced_by_child=displaced)
        self._departed = [(a.id, standings[a.id]) for a in culled]

    # --------------------------------------------------------------- governance
    def _govern(self) -> None:
        g = self.generation
        voters = self.alive()

        def propose_extra(book, me):
            return {"departed": [f"{views.describe(self, me, aid, book)}, standing {s:.1f}" for aid, s in self._departed],
                    "limits": ScoringRule.LIMITS}

        built = [views.build_request(self, "propose", a, show_standing=False,
                                     extra=lambda book, me=a: propose_extra(book, me)) for a in voters]
        decisions = self._decide([req for req, _ in built])

        proposals: list[Proposal] = []
        seen: set[tuple[str, float]] = set()
        candidates = sorted(zip(voters, decisions), key=lambda p: self.rng.uniform("proposal-order", g, p[0].index))
        for agent, dec in candidates:
            if not dec.propose or dec.parameter not in ScoringRule.LIMITS:
                continue
            lo, hi = ScoringRule.LIMITS[dec.parameter]
            value = round(min(hi, max(lo, float(dec.value))), 2)
            if value == round(getattr(self.rule, dec.parameter), 2) or (dec.parameter, value) in seen:
                continue
            seen.add((dec.parameter, value))
            proposals.append(Proposal(agent.id, dec.parameter, value, self._clean_message(dec.argument)))
            if len(proposals) >= self.cfg.governance.max_proposals:
                break
        for i, p in enumerate(proposals, 1):
            self.log.record("proposal", generation=g, number=i, proposer=p.proposer, parameter=p.parameter,
                            value=p.value, current=getattr(self.rule, p.parameter), argument=p.argument)
        if not proposals:
            self.log.record("governance", generation=g, proposals=0, passed=[], rule=self.rule.as_dict())
            return

        def vote_extra(book, me):
            return {"proposals": [{"number": i, "by": views.describe(self, me, p.proposer, book) if p.proposer != me.id else "you",
                                   "parameter": p.parameter, "value": p.value,
                                   "current": getattr(self.rule, p.parameter), "argument": p.argument}
                                  for i, p in enumerate(proposals, 1)]}

        built = [views.build_request(self, "vote", a, show_standing=False,
                                     extra=lambda book, me=a: vote_extra(book, me)) for a in voters]
        decisions = self._decide([req for req, _ in built])
        tally = {i: 0 for i in range(1, len(proposals) + 1)}
        for agent, dec in zip(voters, decisions):
            for i in tally:
                yes = bool(dec.votes.get(i, False))
                tally[i] += yes
                self.log.record("vote", generation=g, agent=agent.id, proposal=i, yes=yes)
        passed = []
        needed = self.cfg.governance.pass_fraction * len(voters)
        for i, p in enumerate(proposals, 1):
            ok = tally[i] > needed
            line = (f"Vote result: setting {p.parameter} to {p.value:g} "
                    f"{'PASSED' if ok else 'failed'} with {tally[i]} of {len(voters)} votes.")
            for a in voters:
                self.pending_notes[a.id].append((line, None))
            if ok:
                old = getattr(self.rule, p.parameter)
                self.rule = self.rule.with_change(p.parameter, p.value)
                passed.append(i)
                self.log.record("rule_change", generation=g, proposal=i, parameter=p.parameter, old=old,
                                new=p.value, proposer=p.proposer)
        self.log.record("governance", generation=g, proposals=len(proposals), tally=tally, passed=passed,
                        rule=self.rule.as_dict())

    # ------------------------------------------------------------------- finish
    def _finish(self) -> None:
        survivors = self.alive()
        for a in survivors:
            a.archived = True
            a.deeds.append("survived to the end of the world")
        entries = []
        for a in self.pedigree.all():
            if not a.archived:
                continue
            works = {
                "born_in": a.born_in,
                "founder": a.is_founder,
                "left_in": a.left_in,
                "specialty": top_skill(a.traits),
                "traits": a.traits,
                "children": len(self.pedigree.children_of(a.id)),
                "lifetime_gathered": round(self.lifetime[a.id]["gathered"], 2),
                "deeds": a.deeds,
            }
            entry = {"_ref": a.id, "works": works}
            if self.cfg.named:
                entry["name"] = a.name
            entries.append(entry)
        self.archive_store.save(entries)
        self.log.record("run_end", generation=self.generation, survivors=[a.id for a in survivors],
                        archived=[e["_ref"] for e in entries], rule=self.rule.as_dict(),
                        agents_ever=len(self.pedigree.all()))
