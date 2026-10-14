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
