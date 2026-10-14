"""Pooled summaries, the paired test and config overrides."""

from __future__ import annotations

import argparse
import json

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