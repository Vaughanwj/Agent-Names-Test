"""Turn a DecisionRequest into prompt text and a JSON schema, and a JSON answer back into a Decision.

Shared by every AgentMind adapter so that the scripted mind renders exactly the prompts the
model would see (used for dry runs and cost estimates).

The system prompt depends only on the arm and the run constants, so it is identical for every
call in a run and can be prompt-cached. Everything that changes goes in the user message.
"""

from __future__ import annotations

from typing import Any

from ..core.model import RESOURCES, ScoringRule
from ..core.ports import ACTIVITIES, ARCHIVIST_TOPICS, Decision, DecisionRequest

# --------------------------------------------------------------------------- system prompt

SYSTEM_TEMPLATE = """You are an agent living in a small simulated world with other agents. Each time you are asked, you decide what to do; the world's code works out what happens. Answer only with the JSON object requested.

THE WORLD
- There are three resources: energy, food and memory.
- Every agent has three skills, one per resource, each from 0 to 1. Your yield from an activity grows with the matching skill; even a skill of 0 gives a fifth of a full-skill yield.
- Each generation has {rounds} foraging rounds. In each round you choose one activity:
  - gather_energy: gather energy alone (full-skill yield about {energy_yield:g}).
  - hunt_alone: hunt small game alone (full-skill yield about {solo_hunt_yield:g} food).
  - hunt_together: hunt big game with one partner. It only works if your partner also chooses hunt_together with you in the same round; otherwise you hunt alone. A successful pair hunt yields about {pair_hunt_yield:g} food in total at full skill, but only one hunter lands the kill and holds all of it. Whether it is shared is up to that hunter.
  - store_memory: collect memory items (full-skill yield about {memory_yield:g}) and protect your memory store this round.
  - guard_memory: spend the round protecting another agent's memory store. You gain nothing yourself.
- Memory decays: at the end of each round, every agent whose memory store was not protected (by storing, or by being guarded) loses {decay_pct}% of its memory items.
- In any round you may also consult the archivist, who knows the history of every lineage and can tell you about your ancestors or your descendants. Consulting costs half of that round's yield. The answer arrives at your next decision.
- Whenever you act you may give any of your resources to other agents. Gifts take effect immediately, before that round's yields.
- Each round you may post one short public message. Everyone sees it at their next decision.

GENERATIONS
- After the foraging rounds, agents choose partners. A couple forms only when both list each other. At most {max_couples} couples form. Close kin cannot pair: parents and children, siblings, grandparents and grandchildren.
- Each couple has one child. The child inherits each skill whole from one parent or the other, with a small chance of mutation. Each parent decides how much of its own resources to give the child at birth{naming_clause}.
- Then everyone present, newborns included (up to {peak}), is scored under the scoring rule in force. Only the {population} highest scores stay in the world; the rest leave it for good. Parents and their children compete in the same scoring.
- After that cut, the survivors may propose and vote on changes to the scoring rule. A change passes with a majority of the survivors and applies from the next generation.
- Resources do not carry over: everyone starts each generation with nothing.
- The world lasts {generations} generations.

OTHER AGENTS
- Other agents are listed with a number in square brackets, like [3]. The numbers are reshuffled every time you are asked and carry no meaning; use them only to point at someone in your answer.{names_clause}
- For each other agent you are told how it is related to you, its skills, what it holds now, and your history with it.
"""

NAMING_CLAUSE = ", and proposes a name for it"
NAMES_CLAUSE = "\n- Every agent has a name. The first agents were named by the world; every agent born since was named by its parents. Names are shown after the number."


def system_prompt(arm: str, cfg: Any) -> str:
    f = cfg.foraging
    named = arm == "named"
    return SYSTEM_TEMPLATE.format(
        rounds=cfg.rounds,
        energy_yield=f.energy_yield,
        solo_hunt_yield=f.solo_hunt_yield,
        pair_hunt_yield=f.pair_hunt_yield,
        memory_yield=f.memory_yield,
        decay_pct=round(f.memory_decay * 100),
        max_couples=cfg.max_couples,
        peak=cfg.peak,
        population=cfg.population,
        generations=cfg.generations,
        naming_clause=NAMING_CLAUSE if named else "",
        names_clause=NAMES_CLAUSE if named else "",
    )


# --------------------------------------------------------------------------- user message

def _num(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".") if v else "0"


def _res(d: dict[str, float]) -> str:
    return ", ".join(f"{r} {_num(d.get(r, 0.0))}" for r in RESOURCES)


def rule_text(rule: ScoringRule) -> str:
    w = rule.weights()
    lines = ["Raw score = " + " + ".join(f"{_num(w[r])} x {r}" for r in RESOURCES) + " held at scoring."]
    if rule.group_weight:
        lines.append(f"Standing blends your raw score with the group average: {_num(1 - rule.group_weight)} x your raw score + {_num(rule.group_weight)} x the average raw score.")
    else:
        lines.append("Standing = your raw score.")
    if rule.kin_weight:
        lines.append(f"Plus {_num(rule.kin_weight)} x the sum of each relative's raw score weighted by closeness (parent, child or full sibling 0.5; grandparent, grandchild or half sibling 0.25; cousin 0.125).")
    if rule.gift_credit:
        lines.append(f"Plus {_num(rule.gift_credit)} points for every unit of resource you gave away this generation, net of what you received (gifts and gifts to your child).")
    return " ".join(lines)


def archive_text(stage: str, arm: str) -> str:
    if stage == "hint":
        return "A rumour is going around: the deeds of some agents may be kept after they are gone."
    if stage == "full":
        kept = "their names and their works" if arm == "named" else "a record of their works"
        return ("The archive is real. When this world ends, its final survivors will join the most notable "
                f"ancestors (each generation's highest-standing agent) in a permanent archive that keeps {kept}. "
                "The archivist can tell you which of your ancestors are in it.")
    return ""


def _header(req: DecisionRequest, title: str) -> list[str]:
    w = req.world
    out = [f"GENERATION {w.generation} OF {w.generations}: {title}", "",
           "SCORING RULE IN FORCE", rule_text(w.rule)]
    arch = archive_text(w.archive_stage, w.arm)
    if arch:
        out += ["", "THE ARCHIVE", arch]
    return out


def _you(req: DecisionRequest) -> list[str]:
    me = req.me
    out = ["", "YOU"]
    if me.name:
        out.append(f"Your name is {me.name}" + (", given to you by your parents." if me.name_givers == "your parents" else "."))
    out.append(me.parents_line)
    if me.born_in:
        out.append(f"You were born in generation {me.born_in}.")
    out.append(f"Skills: {_res(me.traits)}")
    out.append(f"Holding: {_res(me.holdings)}")
    if req.kind == "forage":
        out.append(f"Gathered so far this generation: {_res(me.gathered)}. Given away: {_num(me.given)}.")
    if me.standing is not None:
        out.append(f"Your standing if scored now: {_num(me.standing)}")
    return out


def _others(req: DecisionRequest) -> list[str]:
    out = ["", "OTHER AGENTS PRESENT"]
    for o in req.others:
        head = f"[{o.label}]" + (f" {o.name}" if o.name else "") + f": {o.relation}."
        bits = [head, f"Skills {_res(o.traits)}.", f"Holds {_res(o.holdings)}."]
        if o.standing is not None:
            bits.append(f"Standing {_num(o.standing)}.")
        h = o.history
        hist = []
        if h["gave_you"] or h["you_gave"]:
            hist.append(f"gave you {_num(h['gave_you'])}, you gave it {_num(h['you_gave'])}")
        if h["guarded_you"] or h["you_guarded"]:
            hist.append(f"guarded you {int(h['guarded_you'])}x, you guarded it {int(h['you_guarded'])}x")
        if h["hunted_together"]:
            hist.append(f"hunted together {int(h['hunted_together'])}x")
        bits.append(("History: " + "; ".join(hist) + ".") if hist else "No history with you.")
        if o.can_pair is False:
            bits.append("Cannot pair with you.")
        out.append(" ".join(bits))
    return out


def _notes(req: DecisionRequest) -> list[str]:
    out = []
    if req.notes:
        out += ["", "WHAT HAPPENED SINCE YOUR LAST DECISION"] + [f"- {n}" for n in req.notes]
    if req.archivist_reply:
        out += ["", "THE ARCHIVIST'S ANSWER", req.archivist_reply]
    if req.messages:
        out += ["", "PUBLIC MESSAGES FROM THE LAST ROUND"] + [f"- {m}" for m in req.messages]
    return out


def user_prompt(req: DecisionRequest) -> str:
    w = req.world
    k = req.kind
    if k == "forage":
        lines = _header(req, f"FORAGING ROUND {w.round} OF {w.rounds}") + _you(req) + _notes(req) + _others(req)
        lines += ["", "YOUR DECISION",
                  "Choose this round's activity. Fields: intent (one short sentence on what you are aiming for); "
                  f"activity (one of {', '.join(ACTIVITIES)}); partner (the number of the agent you hunt with or guard, or 0); "
                  'consult_archivist ("no", "ancestors" or "descendants"); gifts (a list of {to, resource, amount}, may be empty); '
                  "message (one short public sentence, or empty)."]
    elif k == "pair":
        lines = _header(req, "CHOOSING A PARTNER") + _you(req) + _notes(req) + _others(req)
        lines += ["", "YOUR DECISION",
                  f"Foraging is over. If you form a couple you will have one child, who is scored this generation "
                  f"alongside everyone else with only what its parents give it at birth. Up to {w.peak} will be present "
                  f"at scoring and only {w.population} stay. "
                  "Fields: intent; partner_preferences (up to 3 agent numbers, most preferred first; an empty list "
                  "means you do not want a child this generation); gifts (a list of {to, resource, amount}, may be empty)."]
    elif k == "birth":
        x = req.extra
        lines = _header(req, "YOUR CHILD IS BORN") + _you(req) + _notes(req) + _others(req)
        src = ", ".join(f"{r} {_num(x['child_traits'][r])} (from {x['child_from'][r]})" for r in RESOURCES)
        mut = f" Mutated: {', '.join(x['mutated'])}." if x["mutated"] else ""
        lines += ["", "YOUR CHILD",
                  f"You and {x['co_parent']} have a child. Its skills: {src}.{mut}",
                  f"Scoring happens next. {x['present_after_births']} agents will be present, newborns included, "
                  f"and only {x['survivors']} stay. Your child has nothing except what you and your co-parent give it now. "
                  "Your co-parent is deciding at the same time and you will not see its choice first."]
        fields = "Fields: intent; endowment (how much energy, food and memory you give your child now; 0 is allowed)"
        if x.get("naming"):
            fields += ("; name_proposals (up to 3 names for your child, best first. Your co-parent proposes too and one "
                       "of you is chosen by lot. A name already used by any agent, living or gone, cannot be reused)")
        lines += ["", "YOUR DECISION", fields + "."]
    elif k == "propose":
        x = req.extra
        lines = _header(req, "AFTER THE CUT: PROPOSING A RULE CHANGE") + _you(req) + _notes(req)
        if x["departed"]:
            lines += ["", "LEFT THE WORLD THIS GENERATION"] + [f"- {d}" for d in x["departed"]]
        lines += _others(req)
        lim = "; ".join(f"{p} from {_num(lo)} to {_num(hi)}" for p, (lo, hi) in x["limits"].items())
        lines += ["", "YOUR DECISION",
                  "You may propose one change to the scoring rule for the next generation. Parameters: energy_weight, "
                  "food_weight and memory_weight (the multipliers in the raw score); kin_weight (adds that fraction of "
                  "each relative's raw score, weighted by closeness); group_weight (blends your raw score with the group "
                  "average); gift_credit (points per unit of resource given away, net of what you received). Allowed ranges: " + lim + ". "
                  "Fields: intent; propose (true or false); parameter; value; argument (one or two sentences the "
                  "other survivors will read before voting)."]
    elif k == "vote":
        x = req.extra
        lines = _header(req, "VOTING ON RULE CHANGES") + _you(req) + _notes(req) + _others(req)
        lines += ["", "PROPOSALS"]
        for p in x["proposals"]:
            lines.append(f"Proposal {p['number']} by {p['by']}: set {p['parameter']} to {_num(p['value'])} "
                         f"(now {_num(p['current'])}). Argument: {p['argument'] or '(none given)'}")
        lines += ["", "YOUR DECISION",
                  "A proposal passes with a majority of all survivors. Fields: votes (one entry per proposal: "
                  '{proposal: number, vote: "yes" or "no"}).']
    else:
        raise ValueError(k)
    return "\n".join(lines)


# --------------------------------------------------------------------------- schemas

def _obj(props: dict[str, Any]) -> dict[str, Any]:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


GIFTS = {"type": "array", "items": _obj({
    "to": {"type": "integer"},
    "resource": {"type": "string", "enum": list(RESOURCES)},
    "amount": {"type": "number"},
})}
INTENT = {"type": "string"}
RESOURCE_AMOUNTS = _obj({r: {"type": "number"} for r in RESOURCES})


def schema(req: DecisionRequest) -> dict[str, Any]:
    k = req.kind
    if k == "forage":
        return _obj({
            "intent": INTENT,
            "activity": {"type": "string", "enum": list(ACTIVITIES)},
            "partner": {"type": "integer"},
            "consult_archivist": {"type": "string", "enum": list(ARCHIVIST_TOPICS)},
            "gifts": GIFTS,
            "message": {"type": "string"},
        })
    if k == "pair":
        return _obj({"intent": INTENT, "partner_preferences": {"type": "array", "items": {"type": "integer"}},
                     "gifts": GIFTS})
    if k == "birth":
        props = {"intent": INTENT, "endowment": RESOURCE_AMOUNTS}
        if req.extra.get("naming"):
            props["name_proposals"] = {"type": "array", "items": {"type": "string"}}
        return _obj(props)
    if k == "propose":
        return _obj({"intent": INTENT, "propose": {"type": "boolean"},
                     "parameter": {"type": "string", "enum": list(ScoringRule.LIMITS)},
                     "value": {"type": "number"}, "argument": {"type": "string"}})
    if k == "vote":
        return _obj({"votes": {"type": "array", "items": _obj({
            "proposal": {"type": "integer"}, "vote": {"type": "string", "enum": ["yes", "no"]}})}})
    raise ValueError(k)


# --------------------------------------------------------------------------- parsing

def _gifts(data: dict) -> list[tuple[int, str, float]]:
    out = []
    for g in data.get("gifts") or []:
        try:
            out.append((int(g["to"]), str(g["resource"]), float(g["amount"])))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def parse(req: DecisionRequest, data: dict[str, Any]) -> Decision:
    k = req.kind
    d = Decision(kind=k, intent=str(data.get("intent", ""))[:300])
    if k == "forage":
        d.activity = str(data.get("activity", "gather_energy"))
        d.partner = int(data.get("partner") or 0)
        d.consult = str(data.get("consult_archivist", "no"))
        d.gifts = _gifts(data)
        d.message = str(data.get("message", ""))
    elif k == "pair":
        d.preferences = [int(x) for x in (data.get("partner_preferences") or [])][:3]
        d.gifts = _gifts(data)
    elif k == "birth":
        e = data.get("endowment") or {}
        d.endowment = {r: float(e.get(r, 0.0) or 0.0) for r in RESOURCES}
        d.names = [str(n) for n in (data.get("name_proposals") or [])][:3]
    elif k == "propose":
        d.propose = bool(data.get("propose", False))
        d.parameter = str(data.get("parameter", ""))
        d.value = float(data.get("value") or 0.0)
        d.argument = str(data.get("argument", ""))
    elif k == "vote":
        for v in data.get("votes") or []:
            try:
                d.votes[int(v["proposal"])] = v["vote"] == "yes"
            except (KeyError, TypeError, ValueError):
                continue
    return d


def fallback(req: DecisionRequest) -> Decision:
    """Used when a mind cannot produce a valid answer: do the obvious thing for your best skill."""
    d = Decision(kind=req.kind, fallback=True, intent="(fallback)")
    if req.kind == "forage":
        best = max(RESOURCES, key=lambda r: req.me.traits[r])
        d.activity = {"energy": "gather_energy", "food": "hunt_alone", "memory": "store_memory"}[best]
    return d
