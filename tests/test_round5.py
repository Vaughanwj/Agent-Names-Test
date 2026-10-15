"""Round 5: the wording arms, the namesake arms, the band arms and the commons."""

from __future__ import annotations

import json
import re
from collections import Counter

import pytest

from agent_names import analysis, app
from agent_names.adapters import config_yaml, prompting
from agent_names.core.config import DEFAULT_FOUNDER_NAMES, FALLBACK_NAMES, WORLD_NAME_POOL

from .helpers import pilot_doc, run_sim
from .test_arms import STABLE_ID, ArmBiasedMind, PromptRecorder, _inheritance

NEW_ARMS = ("parent_id_plain", "stable_id_parental", "world_name_shown", "world_namesake", "band_only", "stable_id_banded")
ALL_ARMS = ("named", "parent_id", "world_name", "stable_id", "unnamed") + NEW_ARMS
COMMONS = {"commons": {"enabled": True, "mpcr": 0.4}}


def test_identical_inheritance_draws_across_all_eleven_arms(tmp_path):
    for seed in (1, 2):
        draws = {arm: _inheritance(run_sim(tmp_path, arm, seed, mind_cls=ArmBiasedMind)[2]) for arm in ALL_ARMS}
        for arm in ALL_ARMS[1:]:
            shared = set(draws["named"]) & set(draws[arm])
            assert shared, arm
            assert all(draws["named"][k] == draws[arm][k] for k in shared), arm


def _strip(events):
    out = []
    for e in events:
        if e["type"] in ("naming", "id_choice", "namesake", "llm_call", "run_timing"):
            continue
        e = {k: v for k, v in e.items() if k not in ("ts", "run", "arm", "name", "band", "t")}
        if e["type"] == "decision":
            e["decision"] = dict(e["decision"], names=[])
        if e["type"] == "archivist":
            e.pop("reply")
        if e["type"] == "run_start":
            e["config"] = {k: v for k, v in e["config"].items() if k != "arm"}
        out.append(e)
    return out


@pytest.mark.parametrize("arm", NEW_ARMS)
def test_new_arms_play_the_same_world_with_a_handle_blind_mind(tmp_path, arm):
    _, _, a = run_sim(tmp_path, arm, 4)
    _, _, b = run_sim(tmp_path, "unnamed", 4)
    assert _strip(a) == _strip(b)


def test_system_prompts_differ_only_in_their_clauses():
    cfg = config_yaml.run_config(pilot_doc(), "named", 1, "x")
    p = {arm: prompting.system_prompt(arm, cfg) for arm in ALL_ARMS}
    base = p["unnamed"]
    assert p["parent_id_plain"].replace(prompting.IDS_PLAIN_CLAUSE, "").replace(prompting.ID_PICK_CLAUSE, "") == base
    assert p["stable_id_parental"].replace(prompting.PARENTAL_IDS_CLAUSE, "") == base
    assert p["world_name_shown"].replace(prompting.WORLD_NAMES_CLAUSE, "") == base
    assert p["world_namesake"].replace(prompting.NAMESAKE_CLAUSE, "") == base
    assert p["band_only"].replace(prompting.BANDS_CLAUSE, "") == base
    assert p["stable_id_banded"].replace(prompting.IDS_CLAUSE + prompting.BANDS_CLAUSE, "") == base
    assert "parent" not in prompting.IDS_PLAIN_CLAUSE and "world" not in prompting.IDS_PLAIN_CLAUSE


def test_parent_id_plain_keeps_the_pick_and_drops_the_parental_wording(tmp_path):
    sim, mind, events = run_sim(tmp_path, "parent_id_plain", 2, mind_cls=PromptRecorder)
    assert [e for e in events if e["type"] == "id_choice"], "parents still pick IDs"
    text = "\n".join([mind.system_text, *mind.prompts])
    assert "picked for you by your parents" not in text and "given to you by your parents" not in text
    assert "given its ID by its parents" not in text
    assert any(re.search(r"^Your ID is A\d+\.$", p, re.M) for p in mind.prompts)
    ids = [a.name for a in sim.pedigree.all()]
    assert all(STABLE_ID.fullmatch(i) for i in ids) and len(set(ids)) == len(ids)


def test_stable_id_parental_credits_parents_without_any_pick(tmp_path):
    sim, mind, events = run_sim(tmp_path, "stable_id_parental", 2, mind_cls=PromptRecorder)
    stable, _, _ = run_sim(tmp_path / "s", "stable_id", 2)
    assert not [e for e in events if e["type"] == "id_choice"]
    assert not any("id_choice" in s for s in mind.schemas)
    assert any(re.search(r"^Your ID is A\d+, given to you by your parents\.$", p, re.M) for p in mind.prompts)
    assert [a.name for a in sim.pedigree.all()] == [a.name for a in stable.pedigree.all()], "same world-assigned IDs"


def test_world_name_shown_tells_parents_the_name_at_birth(tmp_path):
    sim, mind, _ = run_sim(tmp_path, "world_name_shown", 2, mind_cls=PromptRecorder)
    births = [p for p in mind.prompts if "YOUR CHILD IS BORN" in p]
    assert births
    shown = {m.group(1) for p in births for m in [re.search(r"The world has named your child ([A-Z][a-z]+)\.", p)] if m}
    assert shown and shown <= {a.name for a in sim.pedigree.all() if a.parents}
    assert shown <= set(WORLD_NAME_POOL)


def test_world_namesake_names_each_child_after_one_parent(tmp_path):
    sim, mind, events = run_sim(tmp_path, "world_namesake", 3, mind_cls=PromptRecorder)
    marks = {e["child"]: e for e in events if e["type"] == "namesake"}
    children = [a for a in sim.pedigree.all() if a.parents]
    assert children and set(marks) == {c.id for c in children}
    names = [a.name for a in sim.pedigree.all()]
    assert len(set(names)) == len(names)
    for c in children:
        parent = sim.pedigree.agent(marks[c.id]["parent"])
        base = re.sub(r"\s+[IVXL]+$", "", parent.name)
        assert re.fullmatch(rf"{re.escape(base)} [IVXL]+", c.name), (c.name, parent.name)
    births = [p for p in mind.prompts if "YOUR CHILD IS BORN" in p]
    assert any(", after you." in p for p in births) and any(", after your co-parent." in p for p in births)
    assert not [e for e in events if e["type"] == "naming"], "no parent proposes a name"


@pytest.mark.parametrize("arm", ["band_only", "stable_id_banded"])
def test_bands_are_assigned_by_lot_and_shown(tmp_path, arm):
    sim, mind, events = run_sim(tmp_path, arm, 2, mind_cls=PromptRecorder)
    founders = [a for a in sim.pedigree.all() if a.is_founder]
    assert Counter(a.band for a in founders) == {"Blue": 5, "Green": 5}
    assert all(a.band in ("Blue", "Green") for a in sim.pedigree.all())
    born = {e["agent"]: e.get("band") for e in events if e["type"] == "born"}
    assert born == {a.id: a.band for a in sim.pedigree.all()}
    text = "\n".join(mind.prompts)
    assert re.search(r"^You are in the (Blue|Green) band\.$", text, re.M)
    assert re.search(r"\]( A\d+)?: (Blue|Green) band; ", text)
    if arm == "band_only":
        assert not STABLE_ID.search(text)
        for name in DEFAULT_FOUNDER_NAMES + FALLBACK_NAMES:
            assert not re.search(rf"\b{name}\b", text), name
    else:
        assert STABLE_ID.search(text)


def test_bands_are_off_everywhere_else(tmp_path):
    for arm in ("named", "stable_id", "unnamed"):
        _, mind, events = run_sim(tmp_path, arm, 2, mind_cls=PromptRecorder)
        assert "band" not in "\n".join([mind.system_text, *mind.prompts]).lower()
        assert all("band" not in e for e in events if e["type"] == "born")


def test_commons_pot_is_multiplied_and_shared(tmp_path):
    sim, mind, events = run_sim(tmp_path, "named", 2, mind_cls=PromptRecorder, **COMMONS)
    assert "shared pot" in mind.system_text
    results = [e for e in events if e["type"] == "commons_result"]
    assert len(results) == 8
    for res in results:
        puts = [e for e in events if e["type"] == "commons" and e["generation"] == res["generation"]]
        assert len(puts) == res["present"] == 10
        assert res["multiplier"] == pytest.approx(4.0)
        assert res["each"] == pytest.approx(res["pot"] * 4.0 / 10, abs=0.06)
        assert all(0 <= e["fraction"] <= 1 for e in puts)
    assert any("into the commons." in p for p in mind.prompts)
    assert any("into the last commons." in p for p in mind.prompts)
    s = analysis.summarize_run(events)
    assert s["commons"]["contribution_share"] is not None


def test_commons_is_off_by_default(tmp_path):
    _, mind, events = run_sim(tmp_path, "named", 2, mind_cls=PromptRecorder)
    assert not [e for e in events if e["type"].startswith("commons")]
    assert "commons" not in mind.system_text and not any("commons" in p for p in mind.prompts)


def test_round5_measures_and_the_one_sample_test(tmp_path):
    doc = pilot_doc(seeds=[1, 2], arms=["band_only", "stable_id_banded", "world_namesake"], generations=3, rounds=1)
    doc.update(COMMONS)
    batch = app.run_batch(doc, "r5", out_root=str(tmp_path))
    runs = analysis.load_runs([batch])
    for s in runs.values():
        assert s["commons"] is not None
        if s["arm"] in ("band_only", "stable_id_banded"):
            assert s["bands"]["couple_bias"] is not None or s["bands"]["gift_bias"] is not None
        else:
            assert s["bands"] is None and s["namesake"]["births"] > 0
    out = analysis.one_sample([batch], ["band_only", "stable_id_banded"], ["in-band gift bias", "in-band couple bias"])
    assert set(out["tests"]) == {"in-band gift bias", "in-band couple bias"}
    out = analysis.one_sample([batch], ["world_namesake"], ["namesake minus co-parent endowment share"])
    assert out["tests"]["namesake minus co-parent endowment share"]["seeds"] == 2
    json.dumps(out)
