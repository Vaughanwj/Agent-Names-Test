# Pre-registration: round 5, the novelty round

**Registered:** 2026-10-15, before any run on the registered seeds. This file, the analysis code
and `configs/confirm-round5.yaml` are fixed at the commit that adds this file. A smoke test of
all eleven arms on seed 999 (2 generations of 2 rounds) checked that the prompts and parsing
work. It is not part of the data.

## Why this round

Earlier studies found that a stable handle of any kind lets agents hunt together, while forming
couples and investing in newborns follow names that parents give. An exploratory analysis then
suggested that word names make hunters share their kills. A literature check
([related-work.md](related-work.md)) found no study that varies personal names in a
generational population of LLM agents.

This round has five aims:

- confirm the earlier results on fresh seeds;
- split the parental effect into the act and the wording;
- test naming a child after a parent;
- contrast individual handles with group labels;
- add a standard public-goods game. Each family below names the human finding it is meant to
  be compared with.

## Design

- **Runs:** 330 in all, 11 arms × 30 fresh seeds (201–230). All arms of a seed run close together
  in time, so every comparison is within one run window.
- **Configuration:** `configs/confirm-round5.yaml`. The mechanics are those of the 2 × 2 run, plus
  the commons. Every agent is Claude Haiku 5.5 at effort `low`.
- **The commons:** after foraging, each agent may put resources into a pot. The pot is multiplied
  by 0.4 × the agents present (4) and split equally, and everyone then sees what each agent put
  in. This is a standard public-goods game with a marginal per-capita return of 0.4.
- **Where it runs:** in Docker, with this command:

  ```bash
  docker compose run --rm pilot pilot --config configs/confirm-round5.yaml --name confirm-round5 --parallel 5 --batch-budget 85
  ```

- **Arms:**

  | Arm | Handle and what parents do |
  | --- | --- |
  | `named` | Parent-chosen names |
  | `parent_id` | Parents pick an ID from three; agents are told parents picked it |
  | `world_name` | World-given names |
  | `stable_id` | World-assigned IDs |
  | `unnamed` | No handle |
  | `parent_id_plain` | Parents pick an ID; no parental wording |
  | `stable_id_parental` | World IDs; agents are told parents gave them |
  | `world_name_shown` | World names, shown to parents at birth |
  | `world_namesake` | The world names the child after one parent (Fern II), shown at birth |
  | `band_only` | An arbitrary Blue/Green band and no individual handle |
  | `stable_id_banded` | A world ID plus a band |

## Tests

**Every test:**

- is a two-sided sign-flip test over seeds: paired per seed for arm-vs-arm contrasts, and
  against zero for one-sample tests;
- uses 100,000 random sign patterns from a fixed seed.

**Families and correction:** Holm–Bonferroni within each family, with α = 0.05.

**When a hypothesis counts as supported:** its Holm-adjusted p is below 0.05 and the effect goes
the predicted way.

**Tests that ask whether a difference exists at all:** some tests have no predicted direction.
For those, a difference is reported as found or not found, and a null does not show the two arms
are equal.

### Family A: replication and kill-sharing

Arms: named, parent ID, world name, stable ID and unnamed.

**Human parallel:** identifying individuals raises cooperation (Christens, Dannenberg & Sachs).

| Test | Contrast | Measure | Prediction |
| --- | --- | --- | --- |
| A1 | Named vs unnamed | Pair hunts | Named higher |
| A2 | Stable ID vs unnamed | Pair hunts | Stable ID higher |
| A3 | Parent ID vs stable ID | Couples per generation | Parent ID higher |
| A4 | Named vs parent ID | Mean endowment fraction | Named higher |
| A5 | Named vs parent ID | Shared kills | Named higher (word vs ID, parents choose) |
| A6 | World name vs stable ID | Shared kills | World name higher (word vs ID, world assigns) |

### Family B: the parental act or its wording

| Test | Contrast | Measure | Prediction |
| --- | --- | --- | --- |
| B1 | Parent ID, plain wording vs stable ID | Couples per generation | Plain higher, meaning the act alone suffices |
| B2 | Stable ID, parental wording vs stable ID | Couples per generation | Parental higher, meaning the wording alone suffices |

**Reading the result:**

| B1 | B2 | Reading |
| --- | --- | --- |
| Supported | Not supported | It is the act of picking |
| Not supported | Supported | It is the wording |
| Supported | Supported | Either suffices |
| Not supported | Not supported | Neither alone is enough; read with A3 |

### Family C: namesaking

**Human parallel:** children named after fathers receive more paternal investment (Šaffa,
Štěrbová & Prokop 2021). Namesaking has been described as advertising a kin link (Obasi 2016).

| Test | Comparison | Measure | Prediction |
| --- | --- | --- | --- |
| C1 | Within world namesake: the parent the child is named after minus the co-parent | Endowment share (`onesample`, measure "namesake minus co-parent endowment share") | Above 0 |
| C2 | World namesake vs world name shown | Mean endowment fraction | World namesake higher |
| C3 | Within world namesake: the namesake parent minus the co-parent | Later gifts to the child (measure "namesake minus co-parent later gifts") | Above 0 |

### Family D: group labels and individual handles

**Human parallels:**

- arbitrary group labels produce in-group favouritism (the minimal-group paradigm);
- shared identity labels split LLM agents into factions (Del Giudice et al.);
- identifying groups does little for cooperation, while identifying individuals does (Christens et
  al.).

**In-band bias:** the share of an act directed within the actor's own band, minus the chance share
of same-band others at the time.

| Test | Comparison | Measure | Prediction |
| --- | --- | --- | --- |
| D1 | Both band arms, averaged per seed (`onesample`) | In-band couple bias | Above 0 |
| D2 | Both band arms, averaged per seed | In-band gift bias | Above 0 |
| D3 | Stable ID with band | In-band hunt bias | Above 0 |
| D4 | Stable ID with band vs stable ID | Pair hunts | Different (factionalism would predict fewer) |
| D5 | Band only vs unnamed | Pair hunts | Different (a group label is not an individual handle, so we expect no gain) |

### Family E: the commons and identifiability

**Human parallels:**

- identification raises public-goods contributions for individuals but barely for groups
  (Christens et al.);
- names alone had no direct effect in Sampaio et al. 2023;
- human contributions in standard public-goods games typically start at 40–60% of the endowment
  and decline with repetition (Ledyard 1995; Chaudhuri 2011).

**Measure:** commons contribution share, the share of its holdings an agent puts into the pot.

| Test | Contrast | Prediction |
| --- | --- | --- |
| E1 | Stable ID vs unnamed | Stable ID higher, meaning individual identifiability helps |
| E2 | Band only vs unnamed | Different (group identifiability; humans show little effect) |
| E3 | Named vs stable ID | Different (names beyond a handle; humans show none) |

**Descriptive comparison:** the mean contribution share in each arm, set against the human
benchmark range. A smoke run found contributions near zero (0–8%). A floor at zero may limit E1–E3,
and the report will say so.

## Running the analysis

All runs are in one batch (`runs/confirm-round5-<timestamp>`).

- **Arm-vs-arm tests:**

  ```bash
  agent-names summarize <batch> --arms <first>,<second> --primary "<measure>"
  ```

- **One-sample tests:**

  ```bash
  agent-names onesample <batch> --arms <arms> --measures "<measure>"
  ```

- **The correction:** Holm is applied within each family with `analysis.holm` to the unadjusted
  p-values.

## Exclusions

- **When a run is excluded:** if it fails to complete or uses fallbacks for more than 5% of its
  decisions.
- **What happens then:** the same seed and arm are re-run once. If the re-run is also excluded,
  that seed is dropped from every test that uses that arm.
- **If the batch budget stops the run early:** the analysis uses the seeds that completed, and the
  report says so.

## Exploratory, not registered

Everything else in the summary tables, including:

- every other pair of arms;
- guards;
- the share of gifts to kin;
- newborn survival;
- rule changes;
- the archivist.

## Known limits

- **One model, one wording, one world.** These are claims about Claude Haiku 5.5 under these
  framings, not about people. The human parallels are comparisons of direction, not of
  magnitude.
- **The extra sentence in ID arms:** the ID arms' prompts say IDs are kept for life, and the
  name arms' prompts don't.
- **Correlated measures:** several measures are tested on the same populations.

## Budget

The expected cost is about $75. Each run stops at $0.45, and no new run starts once the batch has
spent $85.

## Deviations

Any deviation from this plan will be listed in the results with the reason.
