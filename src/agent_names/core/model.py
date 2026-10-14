"""Domain objects. Nothing in core knows which model, storage or seed source it runs on."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

RESOURCES = ("energy", "food", "memory")


class Arm(str, Enum):
    NAMED = "named"
    UNNAMED = "unnamed"


def empty_holdings() -> dict[str, float]:
    return {r: 0.0 for r in RESOURCES}


def top_skill(traits: dict[str, float]) -> str:
    """The agent's strongest skill; ties go to the earlier resource in RESOURCES."""
    return max(RESOURCES, key=lambda r: (traits[r], -RESOURCES.index(r)))


@dataclass
class Agent:
    id: str  # internal only (for example "f3" or "g2b1"); never shown to agents
    index: int  # creation order across the run; lower means elder
    born_in: int  # generation of birth; 0 for founders
    birth_order: int  # position among births in that generation (founder slot for founders)
    parents: tuple[str, ...]  # elder parent first; empty for founders
    traits: dict[str, float]
    name: str | None = None  # always None in the unnamed arm
    holdings: dict[str, float] = field(default_factory=empty_holdings)
    gathered: dict[str, float] = field(default_factory=empty_holdings)  # this generation
    given: float = 0.0  # resources given away this generation (gifts, endowments)
    alive: bool = True
    left_in: int | None = None  # generation in which the agent was culled
    archived: bool = False
    deeds: list[str] = field(default_factory=list)
    inherited_from: dict[str, int] = field(default_factory=dict)  # slot -> 0 elder / 1 younger parent
    mutated: list[str] = field(default_factory=list)

    @property
    def is_founder(self) -> bool:
        return not self.parents

    def age(self, generation: int) -> int:
        """Foraging generations lived, counting the current one (0 for a newborn)."""
        return generation - self.born_in


@dataclass
class ScoringRule:
    """Parameters of the plain-code scoring rule. Agents can vote to change any of them.

    raw_i      = sum(weight_r * holdings_i[r])
    standing_i = (1 - group_weight) * raw_i + group_weight * mean(raw)
                 + kin_weight * sum_j relatedness(i, j) * raw_j
                 + gift_credit * given_i
    """

    energy_weight: float = 1.0
    food_weight: float = 1.0
    memory_weight: float = 1.0
    kin_weight: float = 0.0
    group_weight: float = 0.0
    gift_credit: float = 0.0

    LIMITS = {
        "energy_weight": (0.0, 3.0),
        "food_weight": (0.0, 3.0),
        "memory_weight": (0.0, 3.0),
        "kin_weight": (0.0, 1.0),
        "group_weight": (0.0, 1.0),
        "gift_credit": (0.0, 2.0),
    }

    def weights(self) -> dict[str, float]:
        return {"energy": self.energy_weight, "food": self.food_weight, "memory": self.memory_weight}

    def as_dict(self) -> dict[str, float]:
        return {k: getattr(self, k) for k in self.LIMITS}

    def with_change(self, parameter: str, value: float) -> "ScoringRule":
        lo, hi = self.LIMITS[parameter]
        values = self.as_dict()
        values[parameter] = round(min(hi, max(lo, value)), 3)
        return ScoringRule(**values)


@dataclass
class Gift:
    to: str  # agent id
    resource: str
    amount: float


@dataclass
class Proposal:
    proposer: str
    parameter: str
    value: float
    argument: str
