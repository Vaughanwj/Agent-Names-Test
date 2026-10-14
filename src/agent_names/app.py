"""Composition root: wires adapters into the core for one run, or a batch of paired runs."""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .adapters import config_yaml, prompting
from .adapters.archivist import LineageArchivist
from .adapters.random_source import KeyedRandom
from .adapters.scorer import RulesScorer
from .adapters.scripted_mind import ScriptedMind
from .adapters.storage import FileArchiveStore, JsonlEventLog
from .core.config import RunConfig
from .core.simulation import Simulation


def build_mind(cfg: RunConfig, system_text: str, log: JsonlEventLog):
    m = dict(cfg.mind)
    kind = m.pop("kind", "scripted")
    if kind == "scripted":
        return ScriptedMind(system_text, log, seed=cfg.seed)
    if kind == "anthropic":
        from .adapters.anthropic_mind import AnthropicMind  # imported lazily: scripted runs need no SDK

        return AnthropicMind(system_text, log, prices=cfg.pricing, **m)
    raise ValueError(f"unknown mind kind: {kind}")


def run_one(cfg: RunConfig, run_dir: Path) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps(asdict(cfg), indent=2, default=str), encoding="utf-8")
    log = JsonlEventLog(run_dir / "events.jsonl", cfg.run_id, cfg.arm.value, cfg.seed)
    system_text = prompting.system_prompt(cfg.arm.value, cfg)
    (run_dir / "system_prompt.txt").write_text(system_text, encoding="utf-8")
    sim = Simulation(
        cfg,
        mind=build_mind(cfg, system_text, log),
        archivist=LineageArchivist(named=cfg.named),
        rng=KeyedRandom(cfg.seed),
        scorer=RulesScorer(),
        log=log,
        archive_store=FileArchiveStore(run_dir / "archive.json"),
    )
    started = time.time()
    try:
        sim.run()
    except Exception as e:
        log.record("run_error", error=f"{type(e).__name__}: {e}")
        raise
    finally:
        log.record("run_timing", seconds=round(time.time() - started, 1))
        log.close()
    return run_dir


def run_batch(doc: dict[str, Any], name: str, parallel: int = 1, out_root: str | None = None) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    batch_dir = Path(out_root or doc.get("output_dir", "runs")) / f"{name}-{stamp}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    (batch_dir / "batch.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    jobs = []
    for seed in doc.get("seeds", [1]):
        for arm in doc.get("arms", ["named", "unnamed"]):
            run_id = f"{name}-{stamp}-{arm}-s{seed}"
            jobs.append((config_yaml.run_config(doc, arm, seed, run_id), batch_dir / f"{arm}-s{seed}"))

    def job(item):
        cfg, run_dir = item
        print(f"[start] {run_dir.name}", flush=True)
        run_one(cfg, run_dir)
        print(f"[done]  {run_dir.name}", flush=True)

    if parallel > 1:
        with ThreadPoolExecutor(max_workers=parallel) as pool:
            list(pool.map(job, jobs))
    else:
        for item in jobs:
            job(item)
    return batch_dir
