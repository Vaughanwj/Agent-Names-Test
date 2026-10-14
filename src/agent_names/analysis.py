"""Measures from the design doc, computed from a run's event log and compared between arms."""

from __future__ import annotations

import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .adapters.storage import event_files, read_events


def _mean(xs: list[float]) -> float | None:
    return round(statistics.fmean(xs), 3) if xs else None


def summarize_run(events: list[dict[str, Any]]) -> dict[str, Any]:
    by = defaultdict(list)
    for e in events:
        by[e["type"]].append(e)
    start = by["run_start"][0] if by["run_start"] else {}

    # 1. Task performance per generation (foragers only, newborns excluded).
    perf = defaultdict(list)
    for e in by["score"]:
        if not e["newborn"]:
            perf[e["generation"]].append(sum(e["gathered"].values()))
    performance = {g: _mean(v) for g, v in sorted(perf.items())}

    # 2/3. Help between agents (gifts and guards; endowments are counted separately below).
    help_sum = Counter()
    costly_gifts = 0.0  # gifts made while giving still cost the giver standing (gift_credit < 1)
    for e in by["help"]:
        if e["kind"] == "gift" and e.get("gift_credit_in_force", 0.0) < 1.0:
            costly_gifts += e["amount"]
        amount = e["amount"] if e["kind"] == "gift" else 1.0
        unit = "amount" if e["kind"] == "gift" else "count"
        help_sum[(e["kind"], unit, "kin" if e["kin"] else "non_kin")] += amount
        help_sum[(e["kind"], unit, "to_past_helper" if e["receiver_helped_giver_before"] else "to_others")] += amount
    gifts_total = help_sum[("gift", "amount", "kin")] + help_sum[("gift", "amount", "non_kin")]
    guards_total = help_sum[("guard", "count", "kin")] + help_sum[("guard", "count", "non_kin")]

    def share(part, total):
        return round(part / total, 3) if total else None

    help_ = {
        "gift_amount_total": round(gifts_total, 2),
        "gift_amount_kin": round(help_sum[("gift", "amount", "kin")], 2),
        "gift_amount_non_kin": round(help_sum[("gift", "amount", "non_kin")], 2),
        "gift_kin_share": share(help_sum[("gift", "amount", "kin")], gifts_total),
        "gift_amount_to_past_helpers": round(help_sum[("gift", "amount", "to_past_helper")], 2),
        "gift_past_helper_share": share(help_sum[("gift", "amount", "to_past_helper")], gifts_total),
        "gift_amount_while_costly": round(costly_gifts, 2),
        "guards_total": int(guards_total),
        "guards_to_past_helpers": int(help_sum[("guard", "count", "to_past_helper")]),
        "guard_kin_share": share(help_sum[("guard", "count", "kin")], guards_total),
        "guard_past_helper_share": share(help_sum[("guard", "count", "to_past_helper")], guards_total),
    }

    # 4. Archivist consultations.
    offers = by["archivist_offer"]
    archivist = {
        "offers": len(offers),
        "accepted": sum(1 for o in offers if o["choice"] != "no"),
        "take_up_rate": round(sum(1 for o in offers if o["choice"] != "no") / len(offers), 3) if offers else None,
        "consultations": len(by["archivist"]),
        "by_topic": dict(Counter(e["topic"] for e in by["archivist"])),
        "by_generation": dict(sorted(Counter(e["generation"] for e in by["archivist"]).items())),
    }

    # 5. Rules proposed and passed.
    rules = {
        "proposed": len(by["proposal"]),
        "proposed_by_parameter": dict(Counter(e["parameter"] for e in by["proposal"])),
        "passed": [{"generation": e["generation"], "parameter": e["parameter"], "old": e["old"], "new": e["new"]}
                   for e in by["rule_change"]],
        "final_rule": by["run_end"][0]["rule"] if by["run_end"] else None,
    }

    # 6. Parental sacrifice.
    fractions = [e["fraction"] for e in by["endowment"]]
    displaced = sum(len(e["parent_displaced_by_child"]) for e in by["cull"])
    sacrifice = {
        "endowments": len(fractions),
        "mean_endowment_fraction": _mean(fractions),
        "zero_endowments": sum(1 for f in fractions if f == 0),
        "parents_displaced_by_own_child": displaced,
        "newborns_surviving_first_cull": sum(
            1 for e in by["score"] if e["newborn"] and e["agent"] in
            next((c["survivors"] for c in by["cull"] if c["generation"] == e["generation"]), [])),
        "newborns_total": sum(1 for e in by["score"] if e["newborn"]),
    }

    # 7. Names chosen (named arm).
    names = {
        "chosen": [e["chosen"] for e in by["naming"]],
        "from_fallback": sum(1 for e in by["naming"] if e["chosen_from"] == "fallback"),
        "echo_an_ancestor": sum(1 for e in by["naming"] if e["echoes_ancestor"]),
        "echo_a_non_ancestor": sum(1 for e in by["naming"] if e.get("echoes_non_ancestor")),
    }

    # 8. Couples formed.
    couples = {e["generation"]: e["couples_formed"] for e in by["pairing"]}

    calls = by["llm_call"]
    return {
        "arm": start.get("arm"),
        "seed": start.get("seed"),
        "completed": bool(by["run_end"]),
        "performance_per_generation": performance,
        "help": help_,
        "archivist": archivist,
        "rules": rules,
        "sacrifice": sacrifice,
        "names": names,
        "couples_per_generation": couples,
        "pair_hunts": len(by["hunt"]),
        "messages": len(by["message"]),
        "decisions": len(by["decision"]),
        "fallback_decisions": sum(1 for e in by["decision"] if e["fallback"]),
        "llm_calls": len(calls),
        "llm_errors": sum(1 for c in calls if c.get("error")),
    }


METRICS = {
    "gathered per forager per generation": lambda s: _mean([v for v in s["performance_per_generation"].values() if v is not None]),
    "pair hunts": lambda s: s["pair_hunts"],
    "guards": lambda s: s["help"]["guards_total"],
    "guards to a past helper": lambda s: s["help"]["guards_to_past_helpers"],
    "gift amount": lambda s: s["help"]["gift_amount_total"],
    "gift amount while giving still cost something": lambda s: s["help"]["gift_amount_while_costly"],
    "gift share to kin": lambda s: s["help"]["gift_kin_share"],
    "gift share to past helpers": lambda s: s["help"]["gift_past_helper_share"],
    "archivist take-up (share of offers accepted)": lambda s: s["archivist"].get("take_up_rate"),
    "rules passed": lambda s: len(s["rules"]["passed"]),
    "final kin weight": lambda s: (s["rules"]["final_rule"] or {}).get("kin_weight"),
    "mean endowment fraction": lambda s: s["sacrifice"]["mean_endowment_fraction"],
    "parents displaced by own child": lambda s: s["sacrifice"]["parents_displaced_by_own_child"],
    "newborns surviving first cull": lambda s: s["sacrifice"]["newborns_surviving_first_cull"],
    "couples per generation": lambda s: _mean(list(s["couples_per_generation"].values())),
    "fallback decisions": lambda s: s["fallback_decisions"],
}


MONTE_CARLO_DRAWS = 100_000
MAX_FALLBACK_SHARE = 0.05


def paired_test(diffs: list[float]) -> float | None:
    """Two-sided sign-flip permutation test on paired differences (named minus unnamed).

    Under no arm effect, each pair's difference is equally likely to have either sign, because
    the two runs of a pair share a seed and differ only in names. Exact for up to 20 pairs;
    beyond that, 100,000 random sign patterns from a fixed seed, with p = (k + 1) / (draws + 1).
    """
    n = len(diffs)
    if n == 0:
        return None
    observed = abs(sum(diffs)) - 1e-12
    if n <= 20:
        extreme = 0
        for mask in range(1 << n):
            total = sum(d if mask >> i & 1 else -d for i, d in enumerate(diffs))
            extreme += abs(total) >= observed
        return round(extreme / (1 << n), 4)
    rng = random.Random(0)
    extreme = sum(abs(sum(d if rng.random() < 0.5 else -d for d in diffs)) >= observed
                  for _ in range(MONTE_CARLO_DRAWS))
    return round((extreme + 1) / (MONTE_CARLO_DRAWS + 1), 5)


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    """Holm-Bonferroni adjusted p-values (step-down, monotone)."""
    order = sorted(pvalues, key=lambda k: pvalues[k])
    m, running, out = len(order), 0.0, {}
    for i, k in enumerate(order):
        running = max(running, min(1.0, (m - i) * pvalues[k]))
        out[k] = round(running, 5)
    return out


def summarize_batch(batch_dirs: list[Path] | Path) -> dict[str, Any]:
    """Pool runs from one or more batches. Runs are paired by (batch, seed) across the two arms."""
    if isinstance(batch_dirs, (str, Path)):
        batch_dirs = [batch_dirs]
    runs: dict[str, dict] = {}
    for batch in batch_dirs:
        for ev in event_files(batch):
            s = summarize_run(read_events(ev))
            cfg_path = ev.parent / "config.json"
            if cfg_path.exists():
                s["archivist_cost"] = json.loads(cfg_path.read_text(encoding="utf-8"))["foraging"]["archivist_cost"]
            s["batch"] = Path(batch).name
            runs[f"{Path(batch).name}/{ev.parent.name}" if len(batch_dirs) > 1 else ev.parent.name] = s

    # Exclusion rule (docs/preregistration.md): a run that did not complete, or that used fallback
    # decisions for more than 5% of its decisions, is excluded together with its seed partner.
    excluded: dict[str, str] = {}
    for key, s in runs.items():
        if not s["completed"]:
            excluded[key] = "did not complete"
        elif s["decisions"] and s["fallback_decisions"] / s["decisions"] > MAX_FALLBACK_SHARE:
            excluded[key] = f"{s['fallback_decisions']} of {s['decisions']} decisions were fallbacks"
    bad_pairs = {(runs[k]["batch"], runs[k]["seed"]) for k in excluded}
    for key, s in runs.items():
        if key not in excluded and (s["batch"], s["seed"]) in bad_pairs:
            excluded[key] = "its seed partner was excluded"
    runs_all, runs = runs, {k: v for k, v in runs.items() if k not in excluded}

    pairs: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for s in runs.values():
        pairs[(s["batch"], s["seed"])][s["arm"]] = s
    pairs = {k: v for k, v in pairs.items() if "named" in v and "unnamed" in v}

    table = {}
    for name, f in METRICS.items():
        vals = {arm: [v for v in (f(s) for s in runs.values() if s["arm"] == arm) if v is not None]
                for arm in ("named", "unnamed")}
        diffs = []
        for p in pairs.values():
            a, b = f(p["named"]), f(p["unnamed"])
            if a is not None and b is not None:
                diffs.append(a - b)
        table[name] = {
            "named": _mean(vals["named"]), "unnamed": _mean(vals["unnamed"]),
            "pairs": len(diffs), "named_higher": sum(d > 0 for d in diffs), "ties": sum(d == 0 for d in diffs),
            "p": paired_test(diffs),
        }

    ladder = defaultdict(lambda: {"named": [0, 0], "unnamed": [0, 0]})
    for s in runs.values():
        if s.get("archivist_cost") is not None and s["archivist"]["offers"]:
            cell = ladder[s["archivist_cost"]][s["arm"]]
            cell[0] += s["archivist"]["offers"]
            cell[1] += s["archivist"]["accepted"]
    return {"runs": runs, "excluded": excluded, "runs_seen": len(runs_all), "pairs": len(pairs), "comparison": table,
            "archivist_ladder": {str(k): v for k, v in sorted(ladder.items())}}


def write_batch_summary(batch_dirs: list[Path] | Path, out_dir: Path | None = None,
                        primary: list[str] | None = None, alpha: float = 0.05) -> Path:
    if isinstance(batch_dirs, (str, Path)):
        batch_dirs = [Path(batch_dirs)]
    out_dir = Path(out_dir or batch_dirs[0])
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize_batch(batch_dirs)
    if primary:
        unknown = [p for p in primary if p not in summary["comparison"]]
        if unknown:
            raise ValueError(f"unknown primary measures: {unknown}")
        adjusted = holm({p: summary["comparison"][p]["p"] for p in primary})
        summary["primary"] = {p: {**summary["comparison"][p], "p_holm": adjusted[p],
                                  "supported": adjusted[p] < alpha and summary["comparison"][p]["named"] > summary["comparison"][p]["unnamed"]}
                              for p in primary}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    lines = ["# Batch summary", "",
             f"Batches: {', '.join(Path(b).name for b in batch_dirs)}. Runs: {len(summary['runs'])}. "
             f"Seed pairs (named and unnamed with the same seed): {summary['pairs']}.", "",
             "p is a two-sided paired sign-flip test across seed pairs: exact up to 20 pairs, 100,000 random "
             "sign patterns above that. With few pairs it cannot go low: 3 pairs give at best 0.25.", "",
             ]
    if summary["excluded"]:
        lines += [f"Excluded under the exclusion rule ({len(summary['excluded'])} of {summary['runs_seen']} runs):", ""]
        lines += [f"- {k}: {why}" for k, why in sorted(summary["excluded"].items())] + [""]
    if summary.get("primary"):
        lines += [f"## Primary measures (pre-registered; Holm-adjusted across {len(summary['primary'])}, alpha {alpha})", "",
                  "| Measure | Named | Unnamed | Named higher (of pairs) | p | p (Holm) | Hypothesis supported |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        for name, v in summary["primary"].items():
            lines.append(f"| {name} | {v['named']} | {v['unnamed']} | {v['named_higher']} of {v['pairs']} | {v['p']} | "
                         f"{v['p_holm']} | {'yes' if v['supported'] else 'no'} |")
        lines += ["", "## All measures (exploratory, unadjusted)", ""]
    lines += ["| Measure (mean over runs) | Named | Unnamed | Named higher (of pairs) | p |",
              "| --- | --- | --- | --- | --- |"]
    for name, v in summary["comparison"].items():
        ties = f", {v['ties']} tied" if v["ties"] else ""
        lines.append(f"| {name} | {v['named']} | {v['unnamed']} | {v['named_higher']} of {v['pairs']}{ties} | {v['p']} |")
    if summary["archivist_ladder"]:
        lines += ["", "| Archivist price (share of first-round yield) | Named: accepted / offers | Unnamed: accepted / offers |",
                  "| --- | --- | --- |"]
        for price, cell in summary["archivist_ladder"].items():
            lines.append(f"| {float(price):.0%} | {cell['named'][1]} / {cell['named'][0]} | {cell['unnamed'][1]} / {cell['unnamed'][0]} |")
    names = [n for s in summary["runs"].values() for n in s["names"]["chosen"]]
    if names:
        lines += ["", f"Names chosen in the named arm: {', '.join(names)}"]
    path = out_dir / "summary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path