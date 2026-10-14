"""The arm switch must change names (or IDs) and nothing else."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from itertools import combinations

import pytest

from agent_names.adapters import config_yaml, prompting
from agent_names.adapters.scripted_mind import ScriptedMind
from agent_names.core import views
from agent_names.core.config import DEFAULT_FOUNDER_NAMES, FALLBACK_NAMES
from agent_names.core.inheritance import InheritanceConfig, draw
from agent_names.adapters.random_source import KeyedRandom

from .helpers import pilot_doc, run_sim

ARMS = ("named", "unnamed", "stable_id", "world_name", "parent_id")
STABLE_ID = re.compile(r"\bA\d+\b")


class ArmBiasedMind(ScriptedMind):
    """Behaves differently by arm so that the arms' histories diverge."""

    def _pair(self, req, u):
        d = super()._pair(req, u)
        if req.world.arm == "named":  # reverse preferences
            d.preferences = list(reversed(d.preferences))
        elif req.world.arm == "stable_id":  # rotate them
            d.preferences = d.preferences[1:] + d.preferences[:1]
        elif req.world.arm == "world_name":  # rotate the other way
            d.preferences = d.preferences[-1:] + d.preferences[:-1]
        elif req.world.arm == "parent_id":  # keep only the first choice
            d.preferences = d.preferences[:1]
        return d


def _inheritance(events):
    return {(e["generation"], e["birth_order"]): (e["from_parent"], e["mutations"])
            for e in events if e["type"] == "inheritance"}


def test_identical_inheritance_draws_for_identical_seeds(tmp_path):
    diverged = set()
    for seed in (1, 2, 3):
        events = {arm: run_sim(tmp_path, arm, seed, mind_cls=ArmBiasedMind)[2] for arm in ARMS}
        for a, b in combinations(ARMS, 2):
            draws_a, draws_b = _inheritance(events[a]), _inheritance(events[b])
            shared = set(draws_a) & set(draws_b)
            assert shared, "both arms should have births"
            for key in shared:
                assert draws_a[key] == draws_b[key], f"seed {seed} birth {key} drew differently in {a} and {b}"
            couples = [[e["couples"] for e in events[arm] if e["type"] == "pairing"] for arm in (a, b)]
            if couples[0] != couples[1]:
                diverged.add((a, b))
    assert diverged == set(combinations(ARMS, 2)), "the test needs histories that diverge between every two arms"


def test_draws_do_not_depend_on_call_order():
    cfg = InheritanceConfig(mutation_rate=0.5)
    r1, r2 = KeyedRandom(7), KeyedRandom(7)
    first = [draw(r1, cfg, g, k) for g in range(1, 4) for k in range(5)]
    second = [draw(r2, cfg, g, k) for g in reversed(range(1, 4)) for k in reversed(range(5))]
    assert first == list(reversed(second))


def _strip_names(events):
    out = []
    for e in events:
        if e["type"] in ("naming", "id_choice", "llm_call", "run_timing"):
            continue
        e = {k: v for k, v in e.items() if k not in ("ts", "run", "arm", "name", "t")}
        out.append(e)
    return out


@pytest.mark.parametrize("arm", ["named", "stable_id", "world_name", "parent_id"])
def test_name_blind_mind_gives_identical_worlds(tmp_path, arm):
    """With a mind that ignores names and IDs, every arm must play out the same world."""
    _, _, handled = run_sim(tmp_path, arm, 4)
    _, _, unnamed = run_sim(tmp_path, "unnamed", 4)
    a, b = _strip_names(handled), _strip_names(unnamed)
    # Decisions differ only in the name proposals (named) or ID picks (parent_id) parents make.
    for e in a:
        if e["type"] == "decision":
            e["decision"]["names"] = []
    for e in a + b:
        if e["type"] == "archivist":
            e.pop("reply")
        if e["type"] == "run_start":
            e["config"].pop("arm")
    assert a == b


def test_system_prompts_differ_only_in_the_handle_clauses():
    cfg = config_yaml.run_config(pilot_doc(), "named", 1, "x")
    named, unnamed, stable, world, parent = (prompting.system_prompt(arm, cfg) for arm in ARMS)
    assert named.replace(prompting.NAMES_CLAUSE, "").replace(prompting.NAMING_CLAUSE, "") == unnamed
    assert stable.replace(prompting.IDS_CLAUSE, "") == unnamed
    assert prompting.IDS_CLAUSE in stable and prompting.NAMING_CLAUSE not in stable
    assert world.replace(prompting.WORLD_NAMES_CLAUSE, "") == unnamed
    assert parent.replace(prompting.PARENT_IDS_CLAUSE, "").replace(prompting.ID_PICK_CLAUSE, "") == unnamed
    assert prompting.NAMING_CLAUSE not in world + parent and prompting.ID_PICK_CLAUSE not in named + world


class PromptRecorder(ScriptedMind):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompts = []
        self.schemas = []

    def decide(self, req):
        self.prompts.append(prompting.user_prompt(req))
        self.schemas.append(json.dumps(prompting.schema(req)))
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
    assert not STABLE_ID.search(text + replies)
    assert "name" not in mind.system_text.lower()


def test_stable_id_prompts_carry_no_parent_chosen_names_or_naming_requests(tmp_path):
    sim, mind, events = run_sim(tmp_path, "stable_id", 2, mind_cls=PromptRecorder)
    assert any("YOUR CHILD IS BORN" in p for p in mind.prompts), "the run should have births"
    replies = "\n".join(e["reply"] for e in events if e["type"] == "archivist")
    assert replies, "the scripted mind should consult the archivist at least once"
    text = "\n".join([mind.system_text, *mind.prompts, *mind.schemas, replies])
    # Nothing asks for, offers or mentions a name. The one exception is a note shared by every
    # arm, "...but named no one", for a guard who picked no one to guard.
    assert "name" not in text.replace("named no one", "").lower()
    for name in DEFAULT_FOUNDER_NAMES + FALLBACK_NAMES:
        assert not re.search(rf"\b{name}\b", text), name
    for aid in {a.id for a in sim.pedigree.all()}:
        assert not re.search(rf"\b{aid}\b", text), aid
    assert not [e for e in events if e["type"] == "naming"]
    assert not any(e["decision"]["names"] for e in events if e["type"] == "decision")
    # Every agent, child or founder, carries a world-assigned ID instead, and is told so.
    assert all(STABLE_ID.fullmatch(a.name) for a in sim.pedigree.all())
    assert any(re.search(r"^Your ID is A\d+\.$", p, re.M) for p in mind.prompts)
    assert any("Your child, with the ID A" in p for p in mind.prompts)
    assert STABLE_ID.search(replies), "the archivist should name relatives by ID"


def test_stable_ids_never_change_and_are_never_shared(tmp_path, monkeypatch):
    seen = []  # one entry per request: generation, round, viewer, its own ID, others' IDs, labels
    real = views.build_request

    def spy(sim, kind, me, *args, **kwargs):
        req, book = real(sim, kind, me, *args, **kwargs)
        shown = {book.by_label[o.label]: o.name for o in req.others}
        seen.append((req.world.generation, req.world.round, me.id, req.me.name, shown, dict(book.by_id)))
        return req, book

    monkeypatch.setattr(views, "build_request", spy)
    sim, _, _ = run_sim(tmp_path, "stable_id", 3)

    shown_as: dict[str, set] = defaultdict(set)
    labels: dict[tuple, set] = defaultdict(set)
    for _, _, viewer, own, others, by_id in seen:
        shown_as[viewer].add(own)
        for aid, handle in others.items():
            shown_as[aid].add(handle)
        for aid, label in by_id.items():
            labels[(viewer, aid)].add(label)
    assert len({(g, r) for g, r, *_ in seen}) > 10, "requests should span many rounds and generations"
    assert all(len(h) == 1 for h in shown_as.values()), "an agent was shown under more than one ID"
    ids = [a.name for a in sim.pedigree.all()]  # the living and the dead
    assert all(STABLE_ID.fullmatch(i) for i in ids) and len(set(ids)) == len(ids)
    assert {aid: h.pop() for aid, h in shown_as.items()} == {a.id: a.name for a in sim.pedigree.all() if a.id in shown_as}
    assert any(len(v) > 1 for v in labels.values()), "the bracket numbers should still be reshuffled"


def test_stable_ids_are_fixed_by_the_seed_and_unrelated_to_birth_order(tmp_path):
    first, _, _ = run_sim(tmp_path / "a", "stable_id", 5)
    again, _, _ = run_sim(tmp_path / "b", "stable_id", 5)
    other, _, _ = run_sim(tmp_path / "c", "stable_id", 6)
    ids = [a.name for a in first.pedigree.all()]
    assert ids == [a.name for a in again.pedigree.all()]
    assert ids != [a.name for a in other.pedigree.all()]
    numbers = [int(i[1:]) for i in ids]
    assert numbers != sorted(numbers), "IDs should not reveal who came first"


def test_archive_keeps_handles_with_works(tmp_path):
    kept = {}
    for arm in ARMS:
        sim, _, _ = run_sim(tmp_path, arm, 2)
        entries = json.loads((tmp_path / f"{arm}-2-archive.json").read_text(encoding="utf-8"))
        assert entries and all("works" in e for e in entries)
        kept[arm] = {k for e in entries for k in e} - {"_ref", "works"}
        if arm == "stable_id":
            assert all(e["id"] == sim.pedigree.agent(e["_ref"]).name for e in entries)
    assert kept == {"named": {"name"}, "unnamed": set(), "stable_id": {"id"}, "world_name": {"name"}, "parent_id": {"id"}}


def test_archivist_offer_points_at_no_one(tmp_path):
    _, mind, _ = run_sim(tmp_path, "named", 2, mind_cls=PromptRecorder)
    offers = [p for p in mind.prompts if "THE ARCHIVIST'S OFFER" in p]
    assert offers
    assert not any("listed below" in p or "OTHER AGENTS PRESENT" in p for p in offers)


def test_named_prompts_show_names(tmp_path):
    _, mind, _ = run_sim(tmp_path, "named", 2, mind_cls=PromptRecorder)
    assert any("Your name is Ash" in p for p in mind.prompts)
    assert any("name_proposals" in p for p in mind.prompts)
