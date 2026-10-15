"""The registered analysis of round 5 (docs/preregistration-round5.md), families A-E.

Runs every registered test with the package's own functions, applies Holm within each family,
and writes registered.json plus a per-arm table of every measure (exploratory) to --out.
Usage: python scripts/analyze_round5.py <batch> [<batch> ...] --out data/round5-20261015/analysis
Extra batches hold re-runs of excluded runs; with more than one, runs are paired by seed.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agent_names import analysis  # noqa: E402

# (id, kind, arms, measure, prediction). kind "pair" compares two arms, first minus second;
# kind "one" tests a measure against zero, averaged per seed across the listed arms.
# prediction "higher" means first arm higher (pair) or above zero (one); "different" is two-sided
# with no predicted direction.
FAMILIES = {
    "A": [
        ("A1", "pair", ("named", "unnamed"), "pair hunts", "higher"),
        ("A2", "pair", ("stable_id", "unnamed"), "pair hunts", "higher"),
        ("A3", "pair", ("parent_id", "stable_id"), "couples per generation", "higher"),
        ("A4", "pair", ("named", "parent_id"), "mean endowment fraction", "higher"),
        ("A5", "pair", ("named", "parent_id"), "shared kills", "higher"),
        ("A6", "pair", ("world_name", "stable_id"), "shared kills", "higher"),
    ],
    "B": [
        ("B1", "pair", ("parent_id_plain", "stable_id"), "couples per generation", "higher"),
        ("B2", "pair", ("stable_id_parental", "stable_id"), "couples per generation", "higher"),
    ],
    "C": [
        ("C1", "one", ("world_namesake",), "namesake minus co-parent endowment share", "higher"),
        ("C2", "pair", ("world_namesake", "world_name_shown"), "mean endowment fraction", "higher"),
        ("C3", "one", ("world_namesake",), "namesake minus co-parent later gifts", "higher"),
    ],
    "D": [
        ("D1", "one", ("band_only", "stable_id_banded"), "in-band couple bias", "higher"),
        ("D2", "one", ("band_only", "stable_id_banded"), "in-band gift bias", "higher"),
        ("D3", "one", ("stable_id_banded",), "in-band hunt bias", "higher"),
        ("D4", "pair", ("stable_id_banded", "stable_id"), "pair hunts", "different"),
        ("D5", "pair", ("band_only", "unnamed"), "pair hunts", "different"),
    ],
    "E": [
        ("E1", "pair", ("stable_id", "unnamed"), "commons contribution share", "higher"),
        ("E2", "pair", ("band_only", "unnamed"), "commons contribution share", "different"),
        ("E3", "pair", ("named", "stable_id"), "commons contribution share", "different"),
    ],
}


def run_test(batches, runs, kind, arms, measure, pair_by):
    if kind == "pair":
        res = analysis.summarize_batch(batches, arms=arms, runs=runs, pair_by=pair_by)
        row = res["comparison"][measure]
        first, second = arms
        return {"first_mean": row[first], "second_mean": row[second], "seeds": row["pairs"],
                "first_higher": row[f"{first}_higher"], "ties": row["ties"], "p": row["p"],
                "excluded": res["excluded"]}
    res = analysis.one_sample(batches, list(arms), [measure])
    row = res["tests"][measure]
    return {"mean": row["mean"], "seeds": row["seeds"], "positive": row["positive"], "negative": row["negative"],
            "p": row["p"], "excluded": res["excluded"]}


def verdict(test, prediction, p_holm):
    if p_holm is None:
        return "no data"
    if prediction == "different":
        return "difference found" if p_holm < 0.05 else "no difference found"
    sign = (test["first_mean"] - test["second_mean"]) if "first_mean" in test else test["mean"]
    if p_holm < 0.05 and sign is not None and sign > 0:
        return "supported"
    if p_holm < 0.05:
        return "significant, opposite to prediction"
    return "not supported"


def per_arm_table(runs):
    """Mean and n of every measure in every arm, over usable runs (exploratory)."""
    vals = defaultdict(list)
    for s in runs.values():
        if not s["completed"] or (s["decisions"] and s["fallback_decisions"] / s["decisions"] > analysis.MAX_FALLBACK_SHARE):
            continue
        for name, f in analysis.METRICS.items():
            v = f(s)
            if v is not None:
                vals[(name, s["arm"])].append(v)
    arms = [a for a in analysis.ARM_ORDER if any(s["arm"] == a for s in runs.values())]
    return {name: {a: {"mean": analysis._mean(vals[(name, a)]), "n": len(vals[(name, a)])} for a in arms}
            for name in analysis.METRICS}


def _fmt(x, digits=3):
    if x is None:
        return "–"
    return f"{x:.{digits}g}" if abs(x) < 1 else f"{x:.{digits}g}" if abs(x) >= 100 else f"{x:.2f}"


def markdown(out) -> str:
    """The registered tests as one markdown table per family."""
    lines = []
    for fam, results in out["families"].items():
        lines += [f"### Family {fam}", "",
                  "| Test | Arms | Measure | Result | Seeds | p | p (Holm) | Verdict |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for tid, r in results.items():
            if r["kind"] == "pair":
                arms = " vs ".join(analysis.arm_label(a) for a in r["arms"])
                res = f"{_fmt(r['first_mean'])} vs {_fmt(r['second_mean'])}; first higher in {r['first_higher']}"
            else:
                arms = " + ".join(analysis.arm_label(a) for a in r["arms"])
                res = f"mean {_fmt(r['mean'])}; above 0 in {r['positive']}, below in {r['negative']}"
            lines.append(f"| {tid} | {arms} | {r['measure']} | {res} | {r['seeds']} | {r['p']} | {r['p_holm']} | {r['verdict']} |")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    batches = [Path(b) for b in args.batch]
    pair_by = "seed" if len(batches) > 1 else "batch"
    runs = analysis.load_runs(batches)

    out = {"batches": [str(b) for b in batches], "pair_by": pair_by, "runs": len(runs),
           "fallbacks": sum(s["fallback_decisions"] for s in runs.values()),
           "decisions": sum(s["decisions"] for s in runs.values()),
           "incomplete": sorted(k for k, s in runs.items() if not s["completed"]),
           "families": {}}
    for fam, tests in FAMILIES.items():
        results = {}
        for tid, kind, arms, measure, prediction in tests:
            results[tid] = dict(kind=kind, arms=list(arms), measure=measure, prediction=prediction,
                                **run_test(batches, runs, kind, arms, measure, pair_by))
        adjusted = analysis.holm({t: r["p"] for t, r in results.items() if r["p"] is not None})
        for tid, (_, _, _, _, prediction) in zip(results, tests):
            r = results[tid]
            r["p_holm"] = adjusted.get(tid)
            r["verdict"] = verdict(r, prediction, r["p_holm"])
        out["families"][fam] = results

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "registered.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (out_dir / "per-arm.json").write_text(json.dumps(per_arm_table(runs), indent=2), encoding="utf-8")

    (out_dir / "registered.md").write_text(markdown(out), encoding="utf-8")

    for fam, results in out["families"].items():
        print(f"\nFamily {fam}")
        for tid, r in results.items():
            if r["kind"] == "pair":
                eff = f"{r['first_mean']!s:>8} vs {r['second_mean']!s:<8} first higher {r['first_higher']}/{r['seeds']}"
            else:
                eff = f"mean {r['mean']!s:>8}  + {r['positive']} / - {r['negative']} of {r['seeds']}"
            arms = (" vs " if r["kind"] == "pair" else " + ").join(r["arms"])
            print(f"  {tid} {arms:<40} {r['measure']:<42} {eff}  p={r['p']}  holm={r['p_holm']}  {r['verdict']}")
    print(f"\nwrote {out_dir / 'registered.json'} and per-arm.json")


if __name__ == "__main__":
    main()
