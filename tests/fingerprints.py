"""Fingerprints of what an arm shows and logs, for checking that other changes leave it untouched.

`python -m tests.fingerprints` (from the repo root, with src on the path) prints the current
fingerprints as JSON; tests/golden_fingerprints.json holds the ones recorded before the
world_name and parent_id arms were added.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

from agent_names.adapters import prompting
from agent_names.adapters.scripted_mind import ScriptedMind

from .helpers import run_sim

GOLDEN_ARMS = ("named", "unnamed", "stable_id")
GOLDEN_SEEDS = (1, 2)
GOLDEN_RUN = {"generations": 3, "rounds": 2}


class _Recorder(ScriptedMind):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen = []

    def decide(self, req):
        self.seen.append(prompting.user_prompt(req))
        self.seen.append(json.dumps(prompting.schema(req), sort_keys=True))
        return super().decide(req)


def fingerprint(tmp: Path, arm: str, seed: int) -> str:
    sim, mind, events = run_sim(tmp, arm, seed, mind_cls=_Recorder, **GOLDEN_RUN)
    events = [{k: v for k, v in e.items() if k != "ts"} for e in events if e["type"] != "run_timing"]
    archive = (tmp / f"{arm}-{seed}-archive.json").read_text(encoding="utf-8")
    blob = "\n".join([mind.system_text, *mind.seen, json.dumps(events, sort_keys=True), archive])
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def all_fingerprints() -> dict[str, str]:
    out = {}
    with tempfile.TemporaryDirectory() as d:
        for arm in GOLDEN_ARMS:
            for seed in GOLDEN_SEEDS:
                run_dir = Path(d) / f"{arm}-{seed}"
                run_dir.mkdir()
                out[f"{arm}-s{seed}"] = fingerprint(run_dir, arm, seed)
    return out


if __name__ == "__main__":
    json.dump(all_fingerprints(), sys.stdout, indent=2)
    print()
