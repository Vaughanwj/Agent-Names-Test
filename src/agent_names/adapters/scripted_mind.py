"""A free, deterministic AgentMind for smoke tests and dry runs.

It renders the same prompts the model would see (so prompt sizes and call counts are real)
and answers with simple rules of thumb. It never calls an API.
"""

from __future__ import annotations

from typing import Sequence

from ..core.model import RESOURCES
from ..core.ports import Decision, DecisionRequest, EventLog
from . import prompting
from .random_source import KeyedRandom

SYLLABLES = ["ka", "ri", "lo", "mi", "sa", "te", "no", "va", "du", "el", "or", "an"]


class ScriptedMind:
    def __init__(self, system_text: str, log: EventLog, seed: int = 0) -> None:
        self.system_text = system_text
        self.log = log
        self.rng = KeyedRandom(seed)

    def decide_batch(self, requests: Sequence[DecisionRequest]) -> list[Decision]:
        return [self.decide(r) for r in requests]

    def decide(self, req: DecisionRequest) -> Decision:
        user_text = prompting.user_prompt(req)
        prompting.schema(req)  # exercise the schema builder too
        self.log.record("llm_call", kind=req.kind, agent=req.agent_id, generation=req.world.generation,
                        round=req.world.round, model="scripted", attempt=1, user_chars=len(user_text),
                        system_chars=len(self.system_text))
        u = lambda *k: self.rng.uniform(req.agent_id, req.kind, req.world.generation, req.world.round, *k)  # noqa: E731
        return getattr(self, f"_{req.kind}")(req, u)

    @staticmethod
    def _kin(req: DecisionRequest):
        return [o for o in req.others if o.relation != "no known relation"]

    def _forage(self, req, u) -> Decision:
        best = max(RESOURCES, key=lambda r: req.me.traits[r])
        d = Decision(kind="forage", intent=f"work my {best} skill")
        if best == "energy":
            d.activity = "gather_energy"
        elif best == "memory":
            d.activity = "collect_memory"
        else:
            hunters = [o for o in req.others if o.traits["food"] >= 0.5]
            if hunters and u("hunt") < 0.7:
                d.activity, d.partner = "hunt_together", hunters[int(u("who") * len(hunters))].label
            else:
                d.activity = "hunt_alone"
        if best == "energy":
            # Sometimes guard a relative's memory store instead of gathering.
            keepers = [o for o in self._kin(req) if o.holdings["memory"] > 2]
            if keepers and u("guard") < 0.15:
                d.activity, d.partner = "guard_memory", keepers[0].label
        kin = self._kin(req)
        if kin and u("gift") < 0.2:
            res = max(RESOURCES, key=lambda r: req.me.holdings[r])
            if req.me.holdings[res] > 1:
                d.gifts = [(kin[0].label, res, 1.0)]
        d.message = f"Round {req.world.round}: I will {d.activity.replace('_', ' ')}." if u("say") < 0.6 else ""
        return d

    def _archivist(self, req, u) -> Decision:
        d = Decision(kind="archivist", intent="learn about my line")
        if u("consult") < 0.3:
            d.consult = "ancestors" if req.extra["ancestors"] else "descendants"
        return d

    def _commons(self, req, u) -> Decision:
        share = 0.4 * u("give")
        return Decision(kind="commons", intent="put some in",
                        endowment={r: round(req.me.holdings[r] * share, 2) for r in RESOURCES})

    def _pair(self, req, u) -> Decision:
        eligible = sorted((o for o in req.others if o.can_pair), key=lambda o: -(o.standing or 0))
        prefs = [o.label for o in eligible[:3]] if u("want") < 0.85 else []
        return Decision(kind="pair", intent="pair with a strong partner", preferences=prefs)

    def _birth(self, req, u) -> Decision:
        share = 0.1 + 0.4 * u("share")
        d = Decision(kind="birth", intent="give my child a start",
                     endowment={r: round(req.me.holdings[r] * share, 2) for r in RESOURCES})
        if req.extra.get("id_options"):
            options = req.extra["id_options"]
            d.names = [options[int(u("id") * len(options))]]
        if req.extra.get("naming"):
            d.names = ["".join(SYLLABLES[int(u("syl", i, j) * len(SYLLABLES))] for j in range(2)).title()
                       for i in range(3)]
        return d

    def _propose(self, req, u) -> Decision:
        if u("propose") < 0.25:
            return Decision(kind="propose", intent="share more", propose=True, parameter="kin_weight",
                            value=round(0.1 + 0.4 * u("value"), 2), argument="Families should rise together.")
        return Decision(kind="propose", intent="keep the rule")

    def _vote(self, req, u) -> Decision:
        return Decision(kind="vote", votes={p["number"]: u("vote", p["number"]) < 0.5 for p in req.extra["proposals"]})
