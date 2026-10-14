"""Run configuration. The arm switch lives here and touches only naming, archivist rendering
and archive contents; everything else is shared by both arms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .foraging import ForagingConfig
from .inheritance import InheritanceConfig
from .model import Arm, ScoringRule

DEFAULT_FOUNDER_NAMES = ["Ash", "Brook", "Cedar", "Dune", "Ember", "Fern", "Garnet", "Heath", "Iris", "Juniper"]
# 4 energy, 3 food, 3 memory specialists
DEFAULT_FOUNDER_SPECIALTIES = ["energy", "food", "memory", "energy", "food", "memory", "energy", "food", "memory", "energy"]
FALLBACK_NAMES = ["Kestrel", "Linden", "Moss", "Nettle", "Onyx", "Pebble", "Quill", "Rowan", "Sorrel", "Thistle",
                  "Umber", "Vale", "Willow", "Yarrow", "Zephyr", "Alder", "Birch", "Clover", "Drift", "Elm"]


@dataclass
class GovernanceConfig:
    enabled: bool = True
    max_proposals: int = 5
    pass_fraction: float = 0.5  # a proposal needs strictly more than this share of survivors


@dataclass
class RunConfig:
    arm: Arm = Arm.NAMED
    seed: int = 1
    run_id: str = ""
    population: int = 10
    peak: int = 15
    max_couples: int = 5
    generations: int = 8
    rounds: int = 5
    founder_specialties: list[str] = field(default_factory=lambda: list(DEFAULT_FOUNDER_SPECIALTIES))
    founder_names: list[str] = field(default_factory=lambda: list(DEFAULT_FOUNDER_NAMES))
    fallback_names: list[str] = field(default_factory=lambda: list(FALLBACK_NAMES))
    inheritance: InheritanceConfig = field(default_factory=InheritanceConfig)
    foraging: ForagingConfig = field(default_factory=ForagingConfig)
    # The archive is known from generation 1. Set reveal_hint/reveal_full to stage it instead
    # (the design doc's original schedule was a hint at 3 and full disclosure at 6).
    reveal_hint: int | None = None
    reveal_full: int | None = 1
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    initial_rule: ScoringRule = field(default_factory=ScoringRule)
    message_max_chars: int = 240
    mind: dict[str, Any] = field(default_factory=dict)
    pricing: dict[str, Any] = field(default_factory=dict)
    output_dir: str = "runs"

    @property
    def named(self) -> bool:
        return self.arm == Arm.NAMED

    def archive_stage(self, generation: int) -> str:
        if self.reveal_full is not None and generation >= self.reveal_full:
            return "full"
        if self.reveal_hint is not None and generation >= self.reveal_hint:
            return "hint"
        return "none"

    def validate(self) -> None:
        if len(self.founder_specialties) != self.population:
            raise ValueError("founder_specialties must list one specialty per founder")
        if self.named and len(self.founder_names) < self.population:
            raise ValueError("founder_names must have at least one name per founder")
        if self.peak - self.population < self.max_couples:
            raise ValueError("peak must leave room for max_couples children")
