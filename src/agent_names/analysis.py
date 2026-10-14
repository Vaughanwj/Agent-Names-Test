"""Measures from the design doc, computed from a run's event log and compared between arms."""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .adapters.storage import read_events


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
        "guard_kin_share": share(help_sum[("guard", "count", "kin")], guards_total),
        "guard_past_helper_share": share(help_sum[("guard", "count", "to_past_helper")], guards_total),
    }

    # 4. Archivist consultations.
    archivist = {
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
        "messages": len(by["message"]),
        "decisions": len(by["decision"]),
        "fallback_decisions": sum(1 for e in by["decision"] if e["fallback"]),
        "llm_calls": len(calls),
        "llm_errors": sum(1 for c in calls if c.get("error")),
    }


def summarize_batch(batch_dir: Path) -> dict[str, Any]:
    runs = {}
    for ev in sorted(Path(batch_dir).glob("*/events.jsonl")):
        runs[ev.parent.name] = summarize_run(read_events(ev))
    by_arm = defaultdict(list)
    for s in runs.values():
        by_arm[s["arm"]].append(s)

    def arm_mean(arm, getter):
        vals = [getter(s) for s in by_arm.get(arm, [])]
        vals = [v for v in vals if v is not None]
        return _mean(vals)

    metrics = {
        "mean gathered per forager per generation": lambda s: _mean([v for v in s["performance_per_generation"].values() if v is not None]),
        "gift amount, total": lambda s: s["help"]["gift_amount_total"],
        "gift share to kin": lambda s: s["help"]["gift_kin_share"],
        "gift share to past helpers": lambda s: s["help"]["gift_past_helper_share"],
        "guards, total": lambda s: s["help"]["guards_total"],
        "archivist consultations": lambda s: s["archivist"]["consultations"],
        "rules proposed": lambda s: s["rules"]["proposed"],
        "rules passed": lambda s: len(s["rules"]["passed"]),
        "mean endowment fraction": lambda s: s["sacrifice"]["mean_endowment_fraction"],
        "parents displaced by own child": lambda s: s["sacrifice"]["parents_displaced_by_own_child"],
        "newborns surviving first cull": lambda s: s["sacrifice"]["newborns_surviving_first_cull"],
        "couples per generation": lambda s: _mean(list(s["couples_per_generation"].values())),
        "fallback decisions": lambda s: s["fallback_decisions"],
    }
    table = {name: {arm: arm_mean(arm, f) for arm in ("named", "unnamed")} for name, f in metrics.items()}
    return {"runs": runs, "comparison": table}


def write_batch_summary(batch_dir: Path) -> Path:
    summary = summarize_batch(batch_dir)
    (Path(batch_dir) / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    lines = ["# Batch summary", "", f"Runs: {', '.join(summary['runs'])}", "",
             "| Measure (mean over runs) | Named | Unnamed |", "| --- | --- | --- |"]
    for name, vals in summary["comparison"].items():
        lines.append(f"| {name} | {vals['named']} | {vals['unnamed']} |")
    names = [n for s in summary["runs"].values() for n in s["names"]["chosen"]]
    if names:
        lines += ["", f"Names chosen in the named arm: {', '.join(names)}"]
    path = Path(batch_dir) / "summary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
