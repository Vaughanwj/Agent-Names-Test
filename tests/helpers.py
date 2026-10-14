from __future__ import annotations

from pathlib import Path

from agent_names.adapters import config_yaml, prompting
from agent_names.adapters.archivist import LineageArchivist
from agent_names.adapters.random_source import KeyedRandom
from agent_names.adapters.scorer import RulesScorer
from agent_names.adapters.scripted_mind import ScriptedMind
from agent_names.adapters.storage import FileArchiveStore, JsonlEventLog, read_events
from agent_names.core.simulation import Simulation

ROOT = Path(__file__).resolve().parents[1]


def pilot_doc(**overrides) -> dict:
    doc = config_yaml.load(ROOT / "configs" / "pilot.yaml")
    doc["mind"] = {"kind": "scripted"}
    doc.update(overrides)
    return doc


def run_sim(tmp_path: Path, arm: str, seed: int = 1, mind_cls=ScriptedMind, **overrides):
    cfg = config_yaml.run_config(pilot_doc(**overrides), arm, seed, f"test-{arm}-{seed}")
    log = JsonlEventLog(tmp_path / f"{arm}-{seed}.jsonl", cfg.run_id, arm, seed)
    system = prompting.system_prompt(arm, cfg)
    mind = mind_cls(system, log, seed=seed)
    sim = Simulation(cfg, mind, LineageArchivist(cfg.shows_handles), KeyedRandom(seed), RulesScorer(), log,
                     FileArchiveStore(tmp_path / f"{arm}-{seed}-archive.json"))
    sim.run()
    log.close()
    return sim, mind, read_events(tmp_path / f"{arm}-{seed}.jsonl")
