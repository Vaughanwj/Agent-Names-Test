"""Write the data behind the paper's figures, from the event logs in data/.

For each arm and measure: the mean over seeds and its standard error, after the exclusion rule.
Usage, from the repo root: python paper/make_figures.py
"""
from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from agent_names.adapters.storage import event_files, read_events  # noqa: E402
from agent_names.analysis import MAX_FALLBACK_SHARE, METRICS, load_runs  # noqa: E402

OUT = REPO / "paper" / "figdata"

# Studies 1-3: five arms on the confirmatory seeds, run in three batches.
EARLY = [REPO / "data/confirm-20261014/main", REPO / "data/confirm-20261014/replacements",
         REPO / "data/stable-id-20261014/runs", REPO / "data/two-by-two-20261014/runs"]
EARLY_ARMS = ["named", "parent_id", "world_name", "stable_id", "unnamed"]

# Study 4: eleven arms on fresh seeds, one batch.
ROUND5 = [REPO / "data/round5-20261015/runs"]
ROUND5_ARMS = ["named", "parent_id", "parent_id_plain", "world_name", "world_name_shown", "world_namesake",
               "stable_id_parental", "stable_id", "stable_id_banded", "band_only", "unnamed"]

LABELS = {"named": "Named", "parent_id": "Parent ID", "parent_id_plain": "Parent ID, plain",
          "world_name": "World name", "world_name_shown": "World name, shown", "world_namesake": "Namesake",
          "stable_id_parental": "Stable ID, parental", "stable_id": "Stable ID", "stable_id_banded": "Stable ID + band",
          "band_only": "Band only", "unnamed": "Unnamed"}

MEASURES = {"pair_hunts": "pair hunts", "couples": "couples per generation",
            "endowment": "mean endowment fraction", "kill_share": "share of kills shared",
            "commons": "commons contribution share"}


def usable(s: dict) -> bool:
    return s["completed"] and not (s["decisions"] and s["fallback_decisions"] / s["decisions"] > MAX_FALLBACK_SHARE)


def write(name: str, batches: list[Path], arms: list[str]) -> None:
    if not all(b.exists() for b in batches):
        print("skipped", name, "(no data yet)")
        return
    runs = load_runs(batches)
    vals: dict[tuple[str, str], list[float]] = defaultdict(list)
    for s in runs.values():
        if s["arm"] not in arms or not usable(s):
            continue
        for key, m in MEASURES.items():
            v = METRICS[m](s)
            if v is not None:
                vals[(s["arm"], key)].append(v)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["x", "arm", "label"] + [c for k in MEASURES for c in (k, f"{k}_se", f"{k}_n")])
        for i, arm in enumerate(arms):
            row = [i, arm, LABELS[arm]]
            for key in MEASURES:
                xs = vals[(arm, key)]
                if xs:
                    mean = sum(xs) / len(xs)
                    se = math.sqrt(sum((x - mean) ** 2 for x in xs) / (len(xs) - 1) / len(xs)) if len(xs) > 1 else 0.0
                    row += [round(mean, 4), round(se, 4), len(xs)]
                else:
                    row += ["nan", "nan", 0]
            w.writerow(row)
    print("wrote", path)


def write_commons_by_generation(batches: list[Path], arms: list[str]) -> None:
    """Mean commons contribution share in each generation, over usable runs, for each arm and all arms."""
    if not all(b.exists() for b in batches):
        print("skipped commons_by_generation (no data yet)")
        return
    ok = {k.split("/")[-1] for k, s in load_runs(batches).items() if usable(s)}
    per_run: dict[tuple[str, int], list[float]] = defaultdict(list)
    for batch in batches:
        for ev_path in event_files(batch):
            if ev_path.parent.name not in ok:
                continue
            by_gen: dict[int, list[float]] = defaultdict(list)
            arm = None
            for e in read_events(ev_path):
                if e["type"] == "commons":
                    by_gen[e["generation"]].append(e["fraction"])
                    arm = e.get("arm", arm)
            arm = arm or ev_path.parent.name.rsplit("-s", 1)[0]
            for g, xs in by_gen.items():
                per_run[(arm, g)].append(sum(xs) / len(xs))
                per_run[("all", g)].append(sum(xs) / len(xs))
    gens = sorted({g for _, g in per_run})
    cols = ["all"] + arms
    path = OUT / "commons_by_generation.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["generation"] + cols)
        for g in gens:
            w.writerow([g] + [round(sum(per_run[(c, g)]) / len(per_run[(c, g)]), 4) if per_run[(c, g)] else "nan"
                              for c in cols])
    print("wrote", path)


if __name__ == "__main__":
    write("early", EARLY, EARLY_ARMS)
    write("round5", ROUND5, ROUND5_ARMS)
    write_commons_by_generation(ROUND5, ROUND5_ARMS)
