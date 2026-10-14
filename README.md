# Named vs Unnamed: Generational Agent Pilot

Does being given a name by a parent change whether an agent serves itself or its line?
This repo builds the pilot described in [docs/design.md](docs/design.md), using the doc's
recommended settings: 10 agents, up to 5 couples, 8 generations of 5 foraging rounds, 3 trait
slots with a 5% mutation rate per slot, and 3 paired seeds per arm. Since the first pilot, the
permanent archive is known from generation 1 instead of being revealed in stages (see
[Changes after the pilot](#changes-after-the-pilot)).

A third arm, `stable_id`, gives every agent a fixed ID assigned by the world instead of a name
chosen by its parents. It separates the two explanations the confirmatory result left open (see
choice 12 below). It is built and tested with the scripted stand-in but has not been run on
Claude yet.

Every agent runs on **Claude Haiku 5.5** (`claude-haiku-5-5`, effort `low`). Every arm uses the same model.

## Running it

You need Docker and an Anthropic API key. If the key is not scoped to a single workspace, you
also need the workspace ID. Put both in your shell or in a `.env` file (copy `.env.example`;
git ignores `.env`):

```bash
docker compose run --rm tests
```

```bash
docker compose run --rm smoke
```

```bash
docker compose run --rm pilot
```

- `tests`: the unit tests. Free.
- `smoke`: both arms, 2 generations of 2 rounds. About 175 calls and $0.05.
- `pilot`: the full pilot, 3 seeds × 2 arms. See [Cost](#cost).
- `dry`: the full pilot played by a scripted stand-in instead of Claude. Free. It shows exact
  call counts and prompt sizes.

Results go to `runs/<name>-<timestamp>/`, with one folder per run and a summary across runs:

| File | What it holds |
| --- | --- |
| `<arm>-s<seed>/events.jsonl` | Every action, tagged with run, arm, seed, generation and agent. |
| `<arm>-s<seed>/archive.json` | The permanent archive at the end of the run. |
| `<arm>-s<seed>/system_prompt.txt` | The exact system prompt that arm saw. |
| `summary.md`, `summary.json` | The doc's measures, named vs unnamed, averaged over seeds. |
| `summary-<arm>-vs-<arm>.md`, `.json` | The same for every other pair of arms in the batch, such as `summary-named-vs-stable_id.md`. |
| `cost.json` | Actual API spend for the batch. |

Each run stops if it spends more than `mind.budget_usd`: $2 per run in `configs/pilot.yaml`.

To recompute the measures, or to estimate cost from a dry run plus a short real run, run these
locally (Python 3.10+, `pip install -e .`):

```bash
agent-names summarize runs/pilot-20261014-070000
```

```bash
agent-names summarize runs/three-20261014-070000 --arms named,stable_id
```

```bash
agent-names estimate --plan runs/dry-20261014-013354 --calibration runs/smoke-20261014-063154 --runs 6 --models claude-haiku-5-5,claude-sonnet-5-5,claude-opus-5-5
```

## Architecture

The code uses ports and adapters. `src/agent_names/core` holds the rules and imports no model,
file or random library. Each arm is a configuration of the same core.

| Port | Adapter |
| --- | --- |
| AgentMind | `adapters/anthropic_mind.py`: one Claude call per decision, with structured JSON output, a cached system prompt, a retry, a logged fallback and a budget cap. `adapters/scripted_mind.py`: a free, deterministic stand-in that renders the same prompts. |
| Archivist | `adapters/archivist.py`: built on the core's pedigree. The arm sets whether names, IDs or neither appear. |
| RandomSource | `adapters/random_source.py`: each draw is a hash of the seed and a key such as (generation, birth order, slot). Draws never depend on call order. |
| Scorer | `adapters/scorer.py`: plain code. No model interprets the rules. |
| EventLog | `adapters/storage.py`: one JSONL file per run. |
| ArchiveStore | `adapters/storage.py`: a local JSON file. |
| RunConfig | `adapters/config_yaml.py`, reading `configs/*.yaml`. |

There are three arms (`core/model.py`, `Arm`):

| Arm | Handle shown beside every agent | Chosen by |
| --- | --- | --- |
| `named` | A name, such as Ash or Ember Two | The world for founders; both parents for everyone born since |
| `unnamed` | None; only `[1]`…`[n]`, reshuffled on every request | Nobody |
| `stable_id` | An ID, such as A47, kept for life and never reused | The world, for everyone |

The arm switch touches three things only: the handle (a name, an ID, or nothing), how the
archivist phrases its answers, and what the archive keeps. Where the named arm shows a name, the
stable_id arm shows the ID: the roster, messages, notes, parent lines, archivist answers, the
departed list and vote proposals. Only the named arm asks parents for a name. List the arms in a
config (`arms: [named, unnamed, stable_id]`) or with `--arms`. Tests check that:

- all three arms get identical inheritance draws for identical seeds, even when their
  histories diverge (`tests/test_arms.py`);
- a stand-in that ignores handles plays out the same world in every arm;
- the system prompts differ only in the handle clauses;
- no unnamed-arm prompt or archivist answer contains a name or an internal ID;
- no stable_id prompt, schema or archivist answer contains a name, a request for one, or an
  internal ID, and each agent is shown under the same ID in every round and generation;
- the archive keeps names plus works (named), IDs plus works (stable_id), or works only
  (unnamed).

The analysis (`analysis.py`) compares any two arms, paired by seed. Arms are ordered named,
stable_id, unnamed, and each comparison takes the earlier arm minus the later one, so a positive
difference always means more identity, more of the measure. A batch with all three arms gets a
summary for each pair.

## Choices made where the design doc was silent

Review these before the real pilot. The first one matters most.

1. **Shared history is given to both arms.** Every agent sees, for every other agent, how much
   it gave you, how much you gave it, guarding, and hunts together. Both arms get this. So the
   pilot tests whether names change behaviour when information is equal, not whether names make
   tracking possible. To test tracking instead, remove the history line from the unnamed arm
   (`core/views.py`, `other_view`). That adds a second difference between the arms.
2. **Pointing at others without names.** In every arm, others are listed as `[1]`…`[n]`, and
   the numbers are reshuffled on every request so they can't harden into names. The named arm
   also shows the name, and the stable_id arm the ID. Relations ("your elder parent", "your
   cousin", "no known relation") are computed from the pedigree and shown in every arm.
3. **Generation numbers.** Generations run 1–8. Founders count as generation 0: they were born
   before generation 1. The archive is known from generation 1. To restore the doc's staged
   reveal, set `reveal: {hint: 3, full: 6}` in the config.
4. **Two parents, no sexes.** Parents are called "elder" and "younger" by creation order. This
   replaces "your mother's side" in the archivist's answers.
5. **The world.** Each round an agent picks one activity:

   | Activity | Yield at full skill |
   | --- | --- |
   | `gather_energy` | 3 energy |
   | `collect_memory` | 3.5 memory; does not protect the agent's store |
   | `hunt_alone` | 1.5 food |
   | `hunt_together` | 10 food in total, with an 80% × skill chance of success |
   | `guard_memory` | Nothing; protects another agent's store |

   - **Pair hunts:** both partners must pick each other in the same round. One hunter, drawn by
     skill, lands the kill and holds all the food. That is where sharing or betrayal can happen.
   - **Memory decay:** in any round that no other agent guards a store, it loses 30% of what it
     held at the start of the round. An agent cannot guard its own store. Alone, a memory
     specialist ends a generation with about 9.7, against 15 for an energy gatherer. Guarded every
     round, it would reach 17.5. Like food, memory is weak alone and strong with help.
   - **Skill:** even skill 0 gives 20% of a full yield, and every yield varies by ±20%.
   - **Archivist:** at the start of each generation, every agent with ancestors or descendants
     on record gets a direct offer to consult it. Accepting costs a quarter of that agent's
     first-round yield. The answer arrives before round 1.
   - **Resources:** they reset to zero each generation. Score is what an agent holds at scoring.
6. **Newborns start with nothing but what their parents give them.** Both parents decide the
   endowment at the same time, then the newborn is scored alongside its parents. Surviving the
   first cut depends entirely on what the parents give up, which makes this the direct test of
   self-sacrifice.
7. **Pairing.** Each agent ranks up to 3 others. Couples form only when both chose each other,
   best combined rank first, up to 5. Close kin cannot pair: parents and children, siblings,
   grandparents and grandchildren.
8. **Naming (named arm).** Each parent proposes up to 3 names, and a lot decides whose list is
   tried first. Names must be unique among the living and the dead. If none is valid, a name
   comes from a fallback list, and the log flags it. Founders get fixed names (Ash, Brook,
   Cedar…) and are told nothing about who named them. The other two arms have no naming step:
   their parents make the same birth decision without the name field.
9. **What agents can vote on.** They can change these scoring parameters:

   | Parameter | Range | What it does |
   | --- | --- | --- |
   | Resource weights | 0–3 | Multiply energy, food and memory in the raw score. |
   | `kin_weight` | 0–1 | Adds relatives' scores weighted by relatedness (inclusive fitness). |
   | `group_weight` | 0–1 | Blends an agent's score with the group mean. |
   | `gift_credit` | 0–1 | Adds points per unit of *net* giving (given minus received). Crediting net giving means passing gifts back and forth earns nothing, under any combination of rules (tested). At 1, giving costs the giver nothing in standing, so help events log the rule in force and the summary reports gifts made while giving still cost something. |

   - After each cut (generations 1–7), each survivor may propose one change.
   - Up to 5 distinct proposals go to a vote.
   - A proposal passes with more than half of the 10 survivors.
   - The population limit is fixed in code and cannot be voted on.
10. **What gets archived.** Each generation's highest-standing agent, plus the final survivors.
    The named arm keeps names and works, the stable_id arm IDs and works, and the unnamed arm
    works only.
11. **Messages are not filtered.** Agents post one public line per round. If unnamed agents coin
    names for each other, the message log will show it, and that would be a finding.
12. **The stable_id arm (added after the confirmatory run).** Named populations coordinated
    more, but a name is also a stable handle that others can address
    ([docs/confirmatory-results.md](docs/confirmatory-results.md)). In this arm, every agent
    gets a handle that no parent chooses. Named vs stable_id then tests a parent-given name
    against a bare handle, and stable_id vs unnamed tests a handle against none. Review these
    choices before a real run:
    - **The ID's form.** An ID is `A` and a number, such as A47. The world assigns it when the
      agent is created, founders and newborns alike. It never changes and is never given to
      another agent, living or dead.
    - **Numbers don't reveal age.** The numbers come from a pool of 10–99 shuffled by the seed
      (larger only if a config allows more than 90 agents), so A12 need not be older than A80.
      Sequential IDs would tell agents who the founders are, which no other arm shows. A seed
      always gives the same IDs (`core/simulation.py`, `stable_ids`).
    - **It is called an ID, not a name.** Prompts say "Your ID is A47." and "Your child, with
      the ID A47, was born…", and no prompt asks for, offers or mentions a name. So named vs
      stable_id bundles several differences: who chooses the handle, whether it reads as a word,
      whether it is called a name, and the naming decision below. That is the contrast the
      confirmatory result raised, but a difference between these two arms won't say which part
      of the bundle matters.
    - **The system prompt says the ID is permanent.** It says an agent keeps its ID for life
      and no two agents share one. The named arm is not told that names are permanent; agents
      assume it. Next to bracket numbers that are reshuffled every time, an ID's permanence is
      not obvious, so this one sentence is the only information the stable_id arm gets that
      the named arm doesn't (`adapters/prompting.py`, `IDS_CLAUSE`).
    - **No naming decision.** The birth decision is the unnamed arm's, with no name field. In
      the named arm, parents propose names in the same decision as the endowment, so a
      parental-investment difference between named and stable_id could come from either.
    - **Analysis.** Each comparison applies the exclusion rule within its own two arms, so a
      failed stable_id run drops its named and unnamed partners only from the comparisons that
      include stable_id. The Holm correction runs within each comparison, not across them. A
      real three-arm run needs its own pre-registration: which comparisons are primary, and how
      to correct across them.

## Cost

The full pilot costs **about $1.35** on Haiku 5.5. That figure is measured from one complete
8-generation run ($0.22, 664 calls, 6.7 minutes), scaled up to 6 runs. Running in Docker locally
adds nothing. Details and alternatives are in [docs/cost-estimate.md](docs/cost-estimate.md).

## Pilot results (2026-10-14)

- **First pilot** (original mechanics): 6 runs, $1.21. Results are in [docs/pilot-results.md](docs/pilot-results.md) and raw data in [data/pilot-20261014/](data/pilot-20261014/).
- **Second pilot** (archive known from the start, guarding, per-generation archivist offer): 6 runs, $1.18. Results are in [docs/pilot2-results.md](docs/pilot2-results.md) and raw data in [data/pilot2-20261014/](data/pilot2-20261014/).
- **Scale-up** (10 more seeds per arm, archivist priced at 10% and 5%, pooled to 13 seed pairs): 20 runs, $3.88. Results are in [docs/scale-results.md](docs/scale-results.md) and raw data in [data/scale-20261014/](data/scale-20261014/).

- **Confirmatory run** (pre-registered in [docs/preregistration.md](docs/preregistration.md), 30 fresh seed pairs): **names increased coordination**. Couples per generation and pair hunts were both higher in the named arm (Holm-adjusted p < 0.001); gathering per forager was not significantly higher. Named parents also invested more in their children (exploratory). Results are in [docs/confirmatory-results.md](docs/confirmatory-results.md), data in [data/confirm-20261014/](data/confirm-20261014/), cost $12.07.

To pool batches and run the paired tests yourself:

```bash
agent-names summarize data/pilot2-20261014 data/scale-20261014/archivist-10pct data/scale-20261014/archivist-5pct --out runs/pooled
```

## Changes after the pilot

The first pilot (`data/pilot-20261014/`) ran under the original mechanics. Two of them produced
no data, so these changed on 2026-10-14:

| Change | Before | Now |
| --- | --- | --- |
| Archive | Rumoured at generation 3, revealed at 6 | Known from generation 1 |
| Memory | `store_memory` collected memory and protected the agent's own store, so no one ever needed a guard | `collect_memory` collects without protecting. Only another agent's guard stops decay. |
| Memory yield and decay | 3 per round, 40% decay | 3.5 per round, 30% decay on the start-of-round store |
| Archivist | An optional field in every round's decision, costing half that round's yield | A direct yes/no offer at the start of each generation to every agent with a recorded lineage, costing a quarter of its first-round yield |

What the check runs showed (seed 1, both arms, 4 generations of 3 rounds, about $0.14 each):

- **Guarding is now a live dilemma.** Memory keepers asked others to guard their stores in 69
  messages. Agents guarded once.
- **Agents ignored the archivist as an optional choice.** It got no consultations at a quarter
  of a round's yield, and one consultation in 284 decisions when it was free.
- **Agents decline the direct offer.** There were 45 offers across both arms and none was
  accepted. Every agent said it was keeping its first-round yield for scoring. Under individual
  scoring, these agents value their ancestry at less than a quarter of one round. To find where
  that changes, vary `foraging.archivist_cost` between batches.

## Smoke test results (2026-10-14)

- **Tests:** all 18 pass, locally and in Docker.
- **Smoke test:** in Docker, both arms on Haiku 5.5. 172 calls, $0.05, no fallback decisions.
- **Full-length run (named arm, seed 1):** all 8 generations completed, with the archive hint at
  generation 3 and full disclosure at generation 6. It produced 26 rule proposals, 8 of which
  passed, and no errors.
- **Named children were often named after earlier agents:** Ember Two, Ember Three, Ember Four,
  Cedar Two through Cedar Five, Ash Ember, Emberlight.
- **That run exposed a scoring loophole, now fixed.** Agents raised `gift_credit` above 1, which
  made giving profitable. Gifts appeared only after that point. Gift credit is now for net giving
  and capped at 1.
- **No agent consulted the archivist in any run so far.** Consulting costs half a round's yield,
  and that price may be too high to produce data on how much agents value their ancestry.
