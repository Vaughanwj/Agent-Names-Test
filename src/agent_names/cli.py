"""Command line: agent-names {pilot,run,summarize,cost,estimate}."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import analysis, app, cost
from .adapters import config_yaml


def _overrides(args) -> dict:
    o: dict = {}
    if getattr(args, "mind", None):
        o["mind"] = {"kind": args.mind}
    for key in ("generations", "rounds"):
        if getattr(args, key, None):
            o[key] = getattr(args, key)
    if getattr(args, "seeds", None):
        o["seeds"] = [int(s) for s in args.seeds.split(",")]
    if getattr(args, "arms", None):
        o["arms"] = args.arms.split(",")
    return o


def _doc(args) -> dict:
    doc = config_yaml.deep_merge(config_yaml.load(args.config), _overrides(args))
    if doc.get("mind", {}).get("kind") == "scripted":
        doc["mind"] = {"kind": "scripted"}  # drop model settings the scripted mind does not take
    return doc


def cmd_pilot(args) -> None:
    doc = _doc(args)
    batch = app.run_batch(doc, args.name, parallel=args.parallel, out_root=args.out)
    summary = analysis.write_batch_summary(batch)
    print(summary.read_text(encoding="utf-8"))
    events = sorted(batch.glob("*/events.jsonl"))
    spent = cost.actual(events, doc.get("pricing"))
    (batch / "cost.json").write_text(json.dumps(spent, indent=2), encoding="utf-8")
    print(f"API spend for this batch: ${spent['usd']:.4f} over {spent['calls']} calls")
    print(f"Results: {batch}")


def cmd_summarize(args) -> None:
    print(analysis.write_batch_summary(Path(args.batch)).read_text(encoding="utf-8"))


def cmd_estimate(args) -> None:
    doc = config_yaml.load(args.config) if args.config else {}
    cal = cost.calibrate(sorted(Path(args.calibration).glob("*/events.jsonl")))
    plan_paths = sorted(Path(args.plan).glob("*/events.jsonl"))
    models = args.models.split(",") if args.models else None
    est = cost.estimate(plan_paths, cal, runs=args.runs, prices=doc.get("pricing"), models=models)
    print(json.dumps({"calibration": cal, "estimate": est}, indent=2))


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="agent-names", description="Named vs unnamed generational agent pilot")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("pilot", help="run every seed x arm in a config (the pilot is 3 seeds x 2 arms)")
    sp.add_argument("--config", default="configs/pilot.yaml")
    sp.add_argument("--name", default="pilot")
    sp.add_argument("--mind", choices=["anthropic", "scripted"], help="override the config's mind")
    sp.add_argument("--generations", type=int)
    sp.add_argument("--rounds", type=int)
    sp.add_argument("--seeds", help="comma-separated, e.g. 1,2,3")
    sp.add_argument("--arms", help="comma-separated, e.g. named,unnamed")
    sp.add_argument("--parallel", type=int, default=1, help="runs to execute at once")
    sp.add_argument("--out", help="output root (default: config output_dir)")
    sp.set_defaults(func=cmd_pilot)

    ss = sub.add_parser("summarize", help="recompute the measures for a batch directory")
    ss.add_argument("batch")
    ss.set_defaults(func=cmd_summarize)

    se = sub.add_parser("estimate", help="estimate cost from a dry-run plan and a real calibration batch")
    se.add_argument("--plan", required=True, help="batch dir of a full-length scripted run")
    se.add_argument("--calibration", required=True, help="batch dir of a short real run")
    se.add_argument("--runs", type=int, default=6)
    se.add_argument("--config", help="config whose pricing table to use")
    se.add_argument("--models", help="comma-separated models to price, e.g. claude-haiku-5-5,claude-sonnet-5-5")
    se.set_defaults(func=cmd_estimate)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
