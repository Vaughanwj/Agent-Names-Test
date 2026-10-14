"""Ports: the interfaces the core needs from the outside world.

The core calls these; adapters in agent_names.adapters implement them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence

from .model import Agent, ScoringRule

# ---------------------------------------------------------------------------
# What an agent is shown, and what it may answer. Built by core.views.
# ---------------------------------------------------------------------------

DECISION_KINDS = ("forage", "pair", "birth", "propose", "vote")
ACTIVITIES = ("gather_energy", "hunt_alone", "hunt_together", "store_memory", "guard_memory")
ARCHIVIST_TOPICS = ("no", "ancestors", "descendants")


@dataclass
class OtherView:
    label: int  # reshuffled every request; the only handle an agent can answer with
    name: str | None  # None in the unnamed arm
    relation: str  # "your elder parent", "no known relation", ...
    age: int
    traits: dict[str, float]
    holdings: dict[str, float]
    history: dict[str, float]  # gave_you, you_gave, guarded_you, you_guarded, hunted_together
    standing: float | None = None  # current score, shown only where it matters
    can_pair: bool | None = None  # pairing requests only


@dataclass
class SelfView:
    name: str | None
    name_givers: str  # "your parents" / "the world" / "" for unnamed
    born_in: int
    age: int
    parents_line: str
    traits: dict[str, float]
    holdings: dict[str, float]
    gathered: dict[str, float]
    given: float
    standing: float | None = None


@dataclass
class WorldView:
    arm: str
    generation: int
    generations: int
    round: int  # 0 outside foraging
    rounds: int
    population: int
    peak: int
    rule: ScoringRule
    archive_stage: str  # "none" | "hint" | "full"


@dataclass
class DecisionRequest:
    kind: str
    agent_id: str
    world: WorldView
    me: SelfView
    others: list[OtherView]
    notes: list[str] = field(default_factory=list)  # what happened to you since your last decision
    messages: list[str] = field(default_factory=list)  # public messages, already rendered
    archivist_reply: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)  # kind-specific context

    def label_map(self) -> dict[int, int]:
        return {o.label: i for i, o in enumerate(self.others)}


@dataclass
class Decision:
    """A mind's answer. Others are referred to by label; core resolves labels to agents."""

    kind: str
    intent: str = ""
    activity: str = "gather_energy"
    partner: int = 0
    consult: str = "no"
    gifts: list[tuple[int, str, float]] = field(default_factory=list)  # (label, resource, amount)
    message: str = ""
    preferences: list[int] = field(default_factory=list)
    endowment: dict[str, float] = field(default_factory=dict)
    names: list[str] = field(default_factory=list)
    propose: bool = False
    parameter: str = ""
    value: float = 0.0
    argument: str = ""
    votes: dict[int, bool] = field(default_factory=dict)  # proposal number -> yes
    fallback: bool = False  # True when the mind failed and a default answer was used


# ---------------------------------------------------------------------------
# Ports
# ---------------------------------------------------------------------------


class AgentMind(Protocol):
    def decide_batch(self, requests: Sequence[DecisionRequest]) -> list[Decision]:
        """Decide for several agents at once (they act simultaneously). Order is preserved."""


class Archivist(Protocol):
    def consult(self, asker: Agent, topic: str, world: "LineageReader", stage: str) -> str:
        """Answer a lineage question for one agent, rendered for the arm."""


class LineageReader(Protocol):
    """Read-only view of the population and pedigree that the archivist works from."""

    def agent(self, agent_id: str) -> Agent: ...
    def children_of(self, agent_id: str) -> list[Agent]: ...


class RandomSource(Protocol):
    def uniform(self, *key: Any) -> float:
        """A number in [0, 1) that depends only on the key, never on call order."""

    def gauss(self, *key: Any) -> float:
        """A standard normal draw that depends only on the key."""


class Scorer(Protocol):
    def score(
        self,
        agents: Sequence[Agent],
        rule: ScoringRule,
        relatedness: "RelatednessFn",
    ) -> dict[str, float]:
        """Standing of every agent present at scoring."""

    def raw(self, agent: Agent, rule: ScoringRule) -> float: ...


class RelatednessFn(Protocol):
    def __call__(self, a: str, b: str) -> float: ...


class EventLog(Protocol):
    def record(self, event_type: str, **data: Any) -> None: ...
    def close(self) -> None: ...


class ArchiveStore(Protocol):
    def save(self, entries: list[dict[str, Any]]) -> None: ...
