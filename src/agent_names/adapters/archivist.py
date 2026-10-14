"""Archivist adapter: answers lineage questions from the core's pedigree.

Both arms get the same facts. The named arm hears names; the unnamed arm hears relations only
("your elder parent", "a grandparent on your younger parent's side") and is never given an ID
it could adopt as a name.
"""

from __future__ import annotations

from ..core.lineage import Pedigree, path_words
from ..core.model import Agent, top_skill

MAX_ANCESTOR_DEPTH = 3
MAX_DESCENDANT_DEPTH = 2


class LineageArchivist:
    def __init__(self, named: bool) -> None:
        self.named = named

    def consult(self, asker: Agent, topic: str, world: Pedigree, stage: str) -> str:
        if topic == "descendants":
            lines = self._descendants(asker, world, stage)
            empty = "You have no recorded descendants yet."
        else:
            lines = self._ancestors(asker, world, stage)
            empty = "You have no recorded ancestors. You were among the first agents."
        return "\n".join(lines) if lines else empty

    # -- rendering ------------------------------------------------------------
    def _who(self, words: str, agent: Agent) -> str:
        return f"{words}, {agent.name}," if self.named and agent.name else words

    def _facts(self, agent: Agent, stage: str) -> str:
        born = "was one of the first agents" if agent.is_founder else f"was born in generation {agent.born_in}"
        parts = [f"{born}, strongest at {top_skill(agent.traits)}"]
        if agent.deeds:
            parts.append("; ".join(d for d in agent.deeds if not d.startswith("survived")))
        parts.append("is still alive" if agent.alive else f"left the world in generation {agent.left_in}")
        if stage == "full":
            parts.append("is kept in the archive" if agent.archived else "is not in the archive")
        return ". It ".join(p for p in parts if p) + "."

    def _ancestors(self, asker: Agent, world: Pedigree, stage: str) -> list[str]:
        lines = []
        for ancestor, path in world.ancestors(asker.id, max_depth=MAX_ANCESTOR_DEPTH):
            subject = self._who(path_words(path), ancestor)
            lines.append(f"- {subject[0].upper()}{subject[1:]} {self._facts(ancestor, stage)}")
        return lines

    def _descendants(self, asker: Agent, world: Pedigree, stage: str) -> list[str]:
        lines = []
        for desc, depth in world.descendants(asker.id, max_depth=MAX_DESCENDANT_DEPTH):
            words = "your child" if depth == 1 else "your grandchild"
            subject = self._who(words, desc)
            lines.append(f"- {subject[0].upper()}{subject[1:]} {self._facts(desc, stage)}")
        return lines
