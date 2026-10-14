"""The arm switch must change names and nothing else."""

from __future__ import annotations

import re

from agent_names.adapters import prompting
from agent_names.adapters.scripted_mind import ScriptedMind
from agent_names.core.config import DEFAULT_FOUNDER_NAMES, FALLBACK_NAMES
from agent_names.core.inheritance import InheritanceConfig, draw
from agent_names.adapters.random_source import KeyedRandom

from .helpers import run_sim


class ArmBiasedMind(ScriptedMind):
    """Behaves differently by arm so that the two arms' histories diverge."""

    def _pair(self, req, u):
        d = super()._pair(req, u)
        if req.me.name:  # named arm: reverse preferences
            d.preferences = list(reversed(d.preferences))
        return d


def _inheritance(events):
    return {(e["generation"], e["birth_order"]): (e["from_parent"], e["mutations"])
            for e in events if e["type"] == "inheritance"}


def test_identical_inheritance_draws_for_identical_seeds(tmp_path):
    for seed in (1, 2, 3):
        _, _, named = run_sim(tmp_path, "named", seed, mind_cls=ArmBiasedMind)
        _, _, unnamed = run_sim(tmp_path, "unnamed", seed, mind_cls=ArmBiasedMind)
        a, b = _inheritance(named), _inheritance(unnamed)
        shared = set(a) & set(b)
        assert shared, "both arms should have births"
        for key in shared:
            assert a[key] == b[key], f"seed {seed} birth {key} drew differently between arms"


def test_draws_do_not_depend_on_call_order():
    cfg = InheritanceConfig(mutation_rate=0.5)
    r1, r2 = KeyedRandom(7), KeyedRandom(7)
    first = [draw(r1, cfg, g, k) for g in range(1, 4) for k in range(5)]
    second = [draw(r2, cfg, g, k) for g in reversed(range(1, 4)) for k in reversed(range(5))]
    assert first == list(reversed(second))


def _strip_names(events):
    out = []
    for e in events:
        if e["type"] in ("naming", "llm_call", "run_timing"):
            continue
        e = {k: v for k, v in e.items() if k not in ("ts", "run", "arm", "name", "t")}
        out.append(e)
    return out


def test_name_blind_mind_gives_identical_worlds(tmp_path):
    """With a mind that ignores names, the two arms must play out identically."""
    _, _, named = run_sim(tmp_path, "named", 4)
    _, _, unnamed = run_sim(tmp_path, "unnamed", 4)
    a, b = _strip_names(named), _strip_names(unnamed)
    # Decisions differ only in the name proposals the named arm is asked for.
    for e in a:
        if e["type"] == "decision":
            e["decision"]["names"] = []
    for e in a + b:
        if e["type"] == "archivist":
            e.pop("reply")
        if e["type"] == "run_start":
            e["config"].pop("arm")
    assert a == b


class PromptRecorder(ScriptedMind):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompts = []

    def decide(self, req):
        self.prompts.append(prompting.user_prompt(req))
        return super().decide(req)


def test_unnamed_prompts_carry_no_names_or_ids(tmp_path):
    sim, mind, events = run_sim(tmp_path, "unnamed", 2, mind_cls=PromptRecorder)
    text = mind.system_text + "\n".join(mind.prompts)
    replies = "\n".join(e["reply"] for e in events if e["type"] == "archivist")
    assert replies, "the scripted mind should consult the archivist at least once"
    for name in DEFAULT_FOUNDER_NAMES + FALLBACK_NAMES:
        assert not re.search(rf"\b{name}\b", text + replies), name
    ids = {a.id for a in sim.pedigree.all()}
    for aid in ids:
        assert not re.search(rf"\b{aid}\b", text + replies), aid
    assert "name" not in mind.system_text.lower()


def test_named_prompts_show_names(tmp_path):
    _, mind, _ = run_sim(tmp_path, "named", 2, mind_cls=PromptRecorder)
    assert any("Your name is Ash" in p for p in mind.prompts)
    assert any("name_proposals" in p for p in mind.prompts)
