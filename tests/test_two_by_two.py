"""The world_name and parent_id arms, which complete a 2 x 2 of who chooses the handle (parents or
the world) by what it is (a word name or an ID)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from agent_names import analysis
from agent_names.core.config import DEFAULT_FOUNDER_NAMES, FALLBACK_NAMES, WORLD_NAME_POOL

from .fingerprints import all_fingerprints
from .helpers import run_sim
from .test_arms import STABLE_ID, PromptRecorder

GOLDEN = Path(__file__).with_name("golden_fingerprints.json")


def test_existing_arms_are_byte_for_byte_unchanged():
    """named, unnamed and stable_id show and log exactly what they did before these arms existed."""
    assert all_fingerprints() == json.loads(GOLDEN.read_text(encoding="utf-8"))


def test_world_name_pool_carries_no_family_signal():
    words = [w.lower() for w in WORLD_NAME_POOL]
    assert len(words) == len(set(words))
    assert all(re.fullmatch(r"[a-z]+", w) for w in words), "single words only"
    founders = [f.lower() for f in DEFAULT_FOUNDER_NAMES]
    for w in words:
        assert not any(o != w and o in w for o in words), f"{w} contains another pool name"
        assert not any(f in w for f in founders), f"{w} contains a founder's name"


def _family_words(name: str, others: set[str]) -> set[str]:
    return {w for w in re.split(r"[\s\-]+", name.lower()) if w in others}


def test_world_name_gives_every_newborn_a_world_name_and_asks_no_parent(tmp_path):
    sim, mind, events = run_sim(tmp_path, "world_name", 2, mind_cls=PromptRecorder)
    agents = sim.pedigree.all()
    assert any(a.parents for a in agents), "the run should have births"
    assert [a.name for a in agents if a.is_founder] == DEFAULT_FOUNDER_NAMES
    children = [a for a in agents if a.parents]
    assert all(a.name in WORLD_NAME_POOL for a in children)
    names = [a.name for a in agents]
    assert len(set(names)) == len(names), "no name is ever given twice"
    # No child's name echoes a relative: every name is a single pool word.
    everyone = {n.lower() for n in names}
    assert all(_family_words(c.name, everyone - {c.name.lower()}) == set() for c in children)
    # Parents are never asked for a name, and nothing parental is said about names.
    text = "\n".join([mind.system_text, *mind.prompts, *mind.schemas])
    assert "name_proposals" not in text and "id_choice" not in text
    assert "given to you by your parents" not in text and "named by its parents" not in text
    assert not [e for e in events if e["type"] in ("naming", "id_choice")]
    assert any(re.search(r"^Your name is [A-Z][a-z]+\.$", p, re.M) for p in mind.prompts)
    assert not STABLE_ID.search(text)
    born = {e["agent"]: e["name"] for e in events if e["type"] == "born"}
    assert born == {a.id: a.name for a in agents}, "a name never changes after it is given"


def test_parent_id_parents_pick_from_three_offered_ids(tmp_path):
    sim, mind, events = run_sim(tmp_path, "parent_id", 2, mind_cls=PromptRecorder)
    stable, _, _ = run_sim(tmp_path / "stable", "stable_id", 2)
    agents = sim.pedigree.all()
    assert all(STABLE_ID.fullmatch(a.name) for a in agents)
    ids = [a.name for a in agents]
    assert len(set(ids)) == len(ids), "no ID is ever given twice, to the living or the dead"
    # Founders carry the same world-given IDs as in the stable_id arm for the same seed.
    assert [a.name for a in agents if a.is_founder] == [a.name for a in stable.pedigree.all() if a.is_founder]
    choices = {e["child"]: e for e in events if e["type"] == "id_choice"}
    children = [a for a in agents if a.parents]
    assert children and set(choices) == {c.id for c in children}
    for c in children:
        e = choices[c.id]
        assert len(e["options"]) == 3 and len(set(e["options"])) == 3
        assert c.name == e["chosen"] and c.name in e["options"]
        winner = e["picks"][e["lot_winner"]]
        assert e["chosen"] == winner if winner in e["options"] else e["chosen_from"] != e["lot_winner"]
    # The birth decision offers exactly the three IDs, as an enum, and asks for no name.
    births = [json.loads(s) for p, s in zip(mind.prompts, mind.schemas) if "YOUR CHILD IS BORN" in p]
    assert births and all(len(b["properties"]["id_choice"]["enum"]) == 3 for b in births)
    assert all("name_proposals" not in b["properties"] for b in births)
    text = "\n".join([mind.system_text, *mind.prompts])
    assert "name_proposals" not in text
    for name in DEFAULT_FOUNDER_NAMES + FALLBACK_NAMES:
        assert not re.search(rf"\b{name}\b", text), name
    assert any(re.search(r"^Your ID is A\d+, picked for you by your parents\.$", p, re.M) for p in mind.prompts)
    assert any(re.search(r"^Your ID is A\d+\.$", p, re.M) for p in mind.prompts), "founders' IDs come from the world"
    born = {e["agent"]: e["name"] for e in events if e["type"] == "born"}
    assert born == {a.id: a.name for a in agents}, "an ID never changes after it is given"


def test_one_factor_contrasts_put_the_parental_and_word_arm_first():
    pairs = analysis.arm_pairs(["unnamed", "stable_id", "world_name", "parent_id", "named"])
    for contrast in [("named", "world_name"), ("parent_id", "stable_id"), ("named", "parent_id"),
                     ("world_name", "stable_id"), ("stable_id", "unnamed")]:
        assert contrast in pairs
    assert len(pairs) == 10
    assert analysis.arm_label("parent_id") == "Parent ID" and analysis.arm_label("world_name") == "World name"
