"""Run configuration. The arm switch lives here and touches only naming, archivist rendering
and archive contents; everything else is shared by all arms."""

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
# Word names the world hands out in the world_name arm, in the same style as the names parents
# choose in the named arm. Single words only: none contains another or a founder's name, so a
# name never signals family the way "Ember Two" does.
WORLD_NAME_POOL = ["Alder", "Aspen", "Basalt", "Birch", "Bramble", "Briar", "Calla", "Cinder", "Clover", "Cobalt",
                   "Coral", "Cove", "Dahlia", "Delta", "Drift", "Fennel", "Flint", "Gale", "Glen", "Hazel",
                   "Holly", "Indigo", "Ivy", "Jasper", "Kelp", "Kestrel", "Larch", "Laurel", "Linden", "Lotus",
                   "Maple", "Marsh", "Mica", "Moss", "Nettle", "Opal", "Pebble", "Quartz", "Quill", "Reed",
                   "Ridge", "Rowan", "Rue", "Sable", "Sage", "Sedge", "Shale", "Slate", "Sorrel", "Sparrow",
                   "Spruce", "Tansy", "Teal", "Thistle", "Thyme", "Vale", "Willow", "Wren", "Yarrow", "Zephyr"]


@dataclass
class GovernanceConfig:
    enabled: bool = True
    max_proposals: int = 5
    pass_fraction: float = 0.5  # a proposal needs strictly more than this share of survivors


@dataclass
class CommonsConfig:
    """A public-goods round after foraging: contributions are multiplied by mpcr x agents present
    and split equally (mpcr is the marginal per-capita return of standard public-goods games)."""
    enabled: bool = False
    mpcr: float = 0.4


WORD_NAME_ARMS = (Arm.NAMED, Arm.WORLD_NAME, Arm.WORLD_NAME_SHOWN, Arm.WORLD_NAMESAKE)
ID_ARMS = (Arm.STABLE_ID, Arm.PARENT_ID, Arm.PARENT_ID_PLAIN, Arm.STABLE_ID_PARENTAL, Arm.STABLE_ID_BANDED)


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
    commons: CommonsConfig = field(default_factory=CommonsConfig)
    initial_rule: ScoringRule = field(default_factory=ScoringRule)
    message_max_chars: int = 240
    mind: dict[str, Any] = field(default_factory=dict)
    pricing: dict[str, Any] = field(default_factory=dict)
    output_dir: str = "runs"

    @property
    def named(self) -> bool:
        """Parents name their children (the named arm only)."""
        return self.arm == Arm.NAMED

    @property
    def shows_handles(self) -> bool:
        """Every agent has a stable individual handle shown beside every reference to it: a word name
        or an ID. The unnamed and band_only arms have none."""
        return self.arm in WORD_NAME_ARMS + ID_ARMS

    @property
    def handle_is_id(self) -> bool:
        """The handle is a neutral ID like "A47" rather than a word name."""
        return self.arm in ID_ARMS

    @property
    def parents_choose(self) -> bool:
        """Parents choose their child's handle: a name (named) or one of three offered IDs."""
        return self.arm in (Arm.NAMED, Arm.PARENT_ID, Arm.PARENT_ID_PLAIN)

    @property
    def parents_credited(self) -> bool:
        """Agents are told that parents gave each newborn its handle (whether or not they chose it)."""
        return self.arm in (Arm.NAMED, Arm.PARENT_ID, Arm.STABLE_ID_PARENTAL)

    @property
    def world_assigns_ids(self) -> bool:
        """Every agent gets a world-assigned ID at creation, from the seed-shuffled pool."""
        return self.arm in (Arm.STABLE_ID, Arm.STABLE_ID_PARENTAL, Arm.STABLE_ID_BANDED)

    @property
    def parents_pick_ids(self) -> bool:
        """Founders get world IDs; each child's ID is picked by its parents from three offered."""
        return self.arm in (Arm.PARENT_ID, Arm.PARENT_ID_PLAIN)

    @property
    def world_names_children(self) -> bool:
        """Newborns get fresh names from the world name pool at creation."""
        return self.arm in (Arm.WORLD_NAME, Arm.WORLD_NAME_SHOWN)

    @property
    def founders_have_names(self) -> bool:
        return self.arm in WORD_NAME_ARMS

    @property
    def child_name_shown_at_birth(self) -> bool:
        """Parents see the child's world-given name when they decide its endowment."""
        return self.arm in (Arm.WORLD_NAME_SHOWN, Arm.WORLD_NAMESAKE)

    @property
    def shows_bands(self) -> bool:
        return self.arm in (Arm.BAND_ONLY, Arm.STABLE_ID_BANDED)

    @property
    def max_agents(self) -> int:
        """The most agents a run can ever create: the founders plus a full set of couples each generation."""
        return self.population + self.max_couples * self.generations

    def archive_stage(self, generation: int) -> str:
        if self.reveal_full is not None and generation >= self.reveal_full:
            return "full"
        if self.reveal_hint is not None and generation >= self.reveal_hint:
            return "hint"
        return "none"

    def validate(self) -> None:
        if len(self.founder_specialties) != self.population:
            raise ValueError("founder_specialties must list one specialty per founder")
        if self.founders_have_names and len(self.founder_names) < self.population:
            raise ValueError("founder_names must have at least one name per founder")
        if self.world_names_children:
            founders = {n.lower() for n in self.founder_names}
            if len([n for n in WORLD_NAME_POOL if n.lower() not in founders]) < self.max_couples * self.generations:
                raise ValueError("WORLD_NAME_POOL is too small for this many births")
        if self.peak - self.population < self.max_couples:
            raise ValueError("peak must leave room for max_couples children")
