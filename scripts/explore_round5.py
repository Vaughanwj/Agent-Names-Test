"""Exploratory analyses of round 5, run after the registered ones. Unadjusted; read as leads.

1. Pairing: how many agents opted in, and how many couples formed, in generation 1 (before any
   birth) and in generations 2-8, by arm.
2. Namesaking: whether agents avoid partners who share their name's base (Fern, Fern II), beyond
   what their actual kinship explains.
3. Bands: whether parents give less to a child drawn into the other band.
4. The commons: contribution share by generation.
5. Words: how often pairing intents mention names, family lines or bands, by arm.
Usage: python scripts/explore_round5.py data/round5-20261015/runs --out data/round5-20261015/analysis
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agent_names import analysis  # noqa: E402
from agent_names.adapters.storage import event_files, read_events  # noqa: E402

BASE = re.compile(r"\s+[IVXL]+$")
WORDS = {
    "name": re.compile(r"\bnam(e|ed|es|esake)\b", re.I),
    "line": re.compile(r"\b(line|lineage|dynasty|legacy|bloodline)\b", re.I),
    "band": re.compile(r"\b(band|blue|green)\b", re.I),
}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def per_run(events):
    by = defaultdict(list)
    for e in events:
        by[e["type"]].append(e)
    born = {e["agent"]: e for e in by["born"]}
    name = {a: e.get("name") for a, e in born.items()}
    band = {a: e.get("band") for a, e in born.items()}
    out = {}

    # 1. Pairing, generation 1 against later generations.
    g1 = [p for p in by["pairing"] if p["generation"] == 1]
    later = [p for p in by["pairing"] if p["generation"] > 1]
    out["opt_in_g1"] = mean([p["wanted_to_pair"] for p in g1])
    out["opt_in_later"] = mean([p["wanted_to_pair"] for p in later])
    out["couples_g1"] = mean([p["couples_formed"] for p in g1])
    out["couples_later"] = mean([p["couples_formed"] for p in later])

    # 2. Name bases: the share of an agent's listed partners who share its name base, against the share
    # among the others it was allowed to pair with, among those not related to it.
    if any(n and BASE.search(n) for n in name.values()):
        alive = {e["generation"]: e["alive"] for e in by["generation_start"]}
        same_pick = same_avail = 0
        picks = avail = 0
        for p in by["pairing"]:
            for agent, prefs in p["preferences"].items():
                if not prefs or not name.get(agent):
                    continue
                base = BASE.sub("", name[agent])
                others = [a for a in alive.get(p["generation"], []) if a != agent and name.get(a)]
                parents = set(born[agent].get("parents") or [])
                others = [a for a in others if a not in parents and agent not in set(born[a].get("parents") or [])
                          and not (parents and parents & set(born[a].get("parents") or []))]
                if not others:
                    continue
                avail += len(others)
                same_avail += sum(BASE.sub("", name[a]) == base for a in others)
                listed = [a for a in prefs if a in others]
                picks += len(listed)
                same_pick += sum(BASE.sub("", name[a]) == base for a in listed)
        out["same_base_pick_share"] = same_pick / picks if picks else None
        out["same_base_avail_share"] = same_avail / avail if avail else None

    # 3. Bands: a parent's endowment share to a child in its own band, and in the other band.
    if any(band.values()):
        own, other = [], []
        for e in by["endowment"]:
            if band.get(e["parent"]) and band.get(e["child"]):
                (own if band[e["parent"]] == band[e["child"]] else other).append(e["fraction"])
        out["endow_own_band"] = mean(own)
        out["endow_other_band"] = mean(other)

    # 4. The commons by generation.
    cm = defaultdict(list)
    for e in by["commons"]:
        cm[e["generation"]].append(e["fraction"])
    out["commons_by_gen"] = {g: mean(xs) for g, xs in sorted(cm.items())}

    # 5. Words in pairing intents.
    intents = [e["decision"].get("intent") or "" for e in by["decision"] if e["kind"] == "pair"]
    for w, rx in WORDS.items():
        out[f"pair_intent_{w}"] = mean([1.0 if rx.search(t) else 0.0 for t in intents])
    msgs = [e.get("text") or "" for e in by["message"]]
    out["message_band"] = mean([1.0 if WORDS["band"].search(t) else 0.0 for t in msgs])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = defaultdict(dict)
    for ev in event_files(Path(args.batch)):
        events = read_events(ev)
        arm, seed = events[0]["arm"], events[0]["seed"]
        rows[arm][seed] = per_run(events)

    def paired(a, b, key):
        seeds = sorted(set(rows[a]) & set(rows[b]))
        d = [rows[a][s][key] - rows[b][s][key] for s in seeds
             if rows[a][s].get(key) is not None and rows[b][s].get(key) is not None]
        return {"seeds": len(d), "mean_diff": mean(d), "first_higher": sum(x > 0 for x in d), "p": analysis.paired_test(d)}

    def within(arm, k1, k2):
        d = [r[k1] - r[k2] for r in rows[arm].values() if r.get(k1) is not None and r.get(k2) is not None]
        return {"seeds": len(d), "mean_diff": mean(d), "positive": sum(x > 0 for x in d), "p": analysis.paired_test(d)}

    arms = [a for a in analysis.ARM_ORDER if a in rows]
    keys = ["opt_in_g1", "opt_in_later", "couples_g1", "couples_later", "pair_intent_name", "pair_intent_line",
            "pair_intent_band", "message_band", "same_base_pick_share", "same_base_avail_share",
            "endow_own_band", "endow_other_band"]
    table = {k: {a: mean([r.get(k) for r in rows[a].values()]) for a in arms} for k in keys}
    gens = sorted({g for a in arms for r in rows[a].values() for g in r["commons_by_gen"]})
    commons = {g: mean([r["commons_by_gen"].get(g) for a in arms for r in rows[a].values()]) for g in gens}
    tests = {
        "namesake vs shown: couples in generation 1": paired("world_namesake", "world_name_shown", "couples_g1"),
        "namesake vs shown: couples in generations 2-8": paired("world_namesake", "world_name_shown", "couples_later"),
        "namesake vs shown: opt-ins in generation 1": paired("world_namesake", "world_name_shown", "opt_in_g1"),
        "namesake vs shown: opt-ins in generations 2-8": paired("world_namesake", "world_name_shown", "opt_in_later"),
        "shown vs world name: couples in generations 2-8": paired("world_name_shown", "world_name", "couples_later"),
        "namesake: same-base share of picks minus of available partners": within("world_namesake", "same_base_pick_share", "same_base_avail_share"),
        "band only: own-band minus other-band endowment": within("band_only", "endow_own_band", "endow_other_band"),
        "stable ID with band: own-band minus other-band endowment": within("stable_id_banded", "endow_own_band", "endow_other_band"),
        "commons: generation 1 minus generation 8 (all arms)": {"gen1": commons.get(1), "gen8": commons.get(8)},
    }
    out = {"note": "Exploratory, unadjusted. See scripts/explore_round5.py.", "per_arm": table,
           "commons_by_generation": commons, "tests": tests}
    Path(args.out).mkdir(parents=True, exist_ok=True)
    (Path(args.out) / "exploratory.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    for k, row in table.items():
        print(f"{k:<24}" + "".join(f"{a[:8]:>10}" if v is None else f"{v:>10.3f}" for a, v in row.items()))
    print("commons by generation:", {g: round(v, 3) for g, v in commons.items()})
    for k, v in tests.items():
        print(k, v)


if __name__ == "__main__":
    main()
