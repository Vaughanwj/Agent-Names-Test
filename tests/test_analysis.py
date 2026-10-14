"""Pooled summaries, the paired test and config overrides."""

from __future__ import annotations

import argparse
import json

import pytest
import yaml

from agent_names import analysis, app, cli
from agent_names.adapters import config_yaml

from .helpers import pilot_doc


def test_paired_test_is_exact():
    assert analysis.paired_test([1.0, 1.0, 1.0]) == 0.25  # all positive: 2 of 8 sign patterns as extreme
    assert analysis.paired_test([1.0] * 10) == round(2 / 1024, 4)
    assert analysis.paired_test([1.0, -1.0]) == 1.0
    assert analysis.paired_test([]) is None


def test_set_overrides_reach_the_run_config():
    args = argparse.Namespace(set=["foraging.archivist_cost=0.1", "generations=3"])
    o = cli._overrides(args)
    assert o == {"foraging": {"archivist_cost": 0.1}, "generations": 3}
    cfg = config_yaml.run_config(config_yaml.deep_merge(pilot_doc(), o), "named", 1, "x")
    assert cfg.foraging.archivist_cost == 0.1 and cfg.generations == 3


def test_pooled_summary_pairs_runs_by_batch_and_seed(tmp_path):
    for name, cost in (("a", 0.1), ("b", 0.05)):
        doc = pilot_doc(seeds=[1, 2], generations=2, rounds=1)
        doc["foraging"]["archivist_cost"] = cost
        app.run_batch(doc, name, out_root=str(tmp_path))
    batches = sorted(p for p in tmp_path.iterdir() if p.is_dir())
    out = analysis.write_batch_summary(batches, tmp_path / "pooled")
    summary = json.loads((tmp_path / "pooled" / "summary.json").read_text(encoding="utf-8"))
    assert summary["pairs"] == 4 and len(summary["runs"]) == 8
    assert set(summary["archivist_ladder"]) == {"0.05", "0.1"}
    assert "Named higher" in out.read_text(encoding="utf-8")


def test_monte_carlo_paired_test_beyond_twenty_pairs():
    assert analysis.paired_test([1.0] * 25) == round(1 / (analysis.MONTE_CARLO_DRAWS + 1), 5)
    mixed = [1.0, -1.0] * 12
    assert analysis.paired_test(mixed) == 1.0
    assert analysis.paired_test(mixed) == analysis.paired_test(mixed)  # fixed seed: reproducible


def test_holm_adjustment():
    adj = analysis.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == {"a": 0.03, "c": 0.06, "b": 0.06}


def test_a_failed_run_does_not_stop_the_batch(tmp_path, monkeypatch):
    real = app.run_one

    def flaky(cfg, run_dir):
        if cfg.seed == 2 and cfg.arm.value == "unnamed":
            raise RuntimeError("boom")
        return real(cfg, run_dir)

    monkeypatch.setattr(app, "run_one", flaky)
    batch = app.run_batch(pilot_doc(seeds=[1, 2], generations=1, rounds=1), "t", out_root=str(tmp_path))
    outcomes = json.loads((batch / "outcomes.json").read_text(encoding="utf-8"))
    assert outcomes["unnamed-s2"].startswith("failed") and outcomes["named-s1"] == "completed"
    assert sum(v == "completed" for v in outcomes.values()) == 3


def test_primary_measures_get_a_holm_table(tmp_path):
    batch = app.run_batch(pilot_doc(seeds=[1, 2], generations=2, rounds=1), "t", out_root=str(tmp_path))
    text = analysis.write_batch_summary([batch], batch, primary=["pair hunts", "couples per generation"]).read_text(encoding="utf-8")
    assert "Primary measures (pre-registered" in text and "p (Holm)" in text

def test_exclusion_rule_drops_an_incomplete_run_and_its_partner(tmp_path):
    batch = app.run_batch(pilot_doc(seeds=[1, 2], generations=2, rounds=1), "t", out_root=str(tmp_path))
    events = batch / "named-s2" / "events.jsonl"
    lines = [l for l in events.read_text(encoding="utf-8").splitlines() if '"run_end"' not in l]
    events.write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary = analysis.summarize_batch([batch])
    assert summary["pairs"] == 1
    assert summary["excluded"] == {"named-s2": "did not complete", "unnamed-s2": "its seed partner was excluded"}
    assert set(summary["runs"]) == {"named-s1", "unnamed-s1"}


THREE_ARMS = ["named", "unnamed", "stable_id"]


def test_a_three_arm_batch_gets_one_summary_per_pair_of_arms(tmp_path):
    batch = app.run_batch(pilot_doc(seeds=[1, 2], generations=2, rounds=1, arms=THREE_ARMS), "t", out_root=str(tmp_path))
    paths = analysis.write_batch_summaries([batch], batch)
    assert [p.name for p in paths] == ["summary-named-vs-stable_id.md", "summary.md", "summary-stable_id-vs-unnamed.md"]

    plain = json.loads((batch / "summary.json").read_text(encoding="utf-8"))  # named vs unnamed, as before
    assert set(plain["runs"]) == {"named-s1", "named-s2", "unnamed-s1", "unnamed-s2"} and plain["pairs"] == 2

    new = json.loads((batch / "summary-named-vs-stable_id.json").read_text(encoding="utf-8"))
    assert set(new["runs"]) == {"named-s1", "named-s2", "stable_id-s1", "stable_id-s2"} and new["pairs"] == 2
    assert set(new["comparison"]["pair hunts"]) == {"named", "stable_id", "pairs", "named_higher", "ties", "p"}
    text = paths[0].read_text(encoding="utf-8")
    assert "# Batch summary: Named vs Stable ID" in text
    assert "| Measure (mean over runs) | Named | Stable ID | Named higher (of pairs) | p |" in text
    assert "Seed pairs (named and stable_id with the same seed): 2." in text


def test_any_two_arms_compare_first_minus_second(tmp_path):
    batch = app.run_batch(pilot_doc(seeds=[1, 2], generations=2, rounds=1, arms=THREE_ARMS), "t", out_root=str(tmp_path))
    runs = analysis.load_runs([batch])
    forward = analysis.summarize_batch([batch], arms=("stable_id", "unnamed"), runs=runs)["comparison"]
    backward = analysis.summarize_batch([batch], arms=("unnamed", "stable_id"), runs=runs)["comparison"]
    for name in analysis.METRICS:
        f, b = forward[name], backward[name]
        assert (f["stable_id"], f["unnamed"], f["p"]) == (b["stable_id"], b["unnamed"], b["p"])
        assert f["stable_id_higher"] + b["unnamed_higher"] + f["ties"] == f["pairs"]


def test_exclusion_applies_within_each_comparison(tmp_path):
    batch = app.run_batch(pilot_doc(seeds=[1, 2], generations=2, rounds=1, arms=THREE_ARMS), "t", out_root=str(tmp_path))
    events = batch / "stable_id-s2" / "events.jsonl"
    lines = [l for l in events.read_text(encoding="utf-8").splitlines() if '"run_end"' not in l]
    events.write_text("\n".join(lines) + "\n", encoding="utf-8")
    plain = analysis.summarize_batch([batch])
    assert plain["excluded"] == {} and plain["pairs"] == 2  # a stable_id failure leaves named vs unnamed alone
    s = analysis.summarize_batch([batch], arms=("named", "stable_id"))
    assert s["pairs"] == 1
    assert s["excluded"] == {"stable_id-s2": "did not complete", "named-s2": "its seed partner was excluded"}


def test_a_config_can_list_three_arms(tmp_path, capsys):
    config = tmp_path / "three.yaml"
    config.write_text(yaml.safe_dump(pilot_doc(seeds=[1], arms=THREE_ARMS)), encoding="utf-8")
    cli.main(["pilot", "--config", str(config), "--name", "three", "--generations", "1", "--rounds", "1",
              "--out", str(tmp_path / "runs")])
    (batch,) = (tmp_path / "runs").iterdir()
    assert {p.name for p in batch.iterdir() if p.is_dir()} == {"named-s1", "unnamed-s1", "stable_id-s1"}
    assert (batch / "stable_id-s1" / "system_prompt.txt").read_text(encoding="utf-8").count("Every agent has an ID") == 1
    assert "# Batch summary: Stable ID vs Unnamed" in capsys.readouterr().out

    cli.main(["summarize", str(batch), "--arms", "stable_id,unnamed", "--out", str(tmp_path / "one")])
    assert sorted(p.name for p in (tmp_path / "one").iterdir()) == ["summary-stable_id-vs-unnamed.json",
                                                                   "summary-stable_id-vs-unnamed.md"]


def test_pairing_by_seed_across_batches(tmp_path):
    old = app.run_batch(pilot_doc(seeds=[1, 2], arms=["named", "unnamed"], generations=1, rounds=1), "old",
                        out_root=str(tmp_path))
    new = app.run_batch(pilot_doc(seeds=[1, 2], arms=["stable_id"], generations=1, rounds=1), "new",
                        out_root=str(tmp_path))
    by_batch = analysis.summarize_batch([old, new], arms=("named", "stable_id"))
    by_seed = analysis.summarize_batch([old, new], arms=("named", "stable_id"), pair_by="seed")
    assert by_batch["pairs"] == 0 and by_seed["pairs"] == 2
    with pytest.raises(ValueError, match="two completed"):
        again = app.run_batch(pilot_doc(seeds=[1], arms=["stable_id"], generations=1, rounds=1), "again",
                              out_root=str(tmp_path))
        analysis.summarize_batch([old, new, again], arms=("named", "stable_id"), pair_by="seed")