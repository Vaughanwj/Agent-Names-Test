# Pre-registration: the 2 × 2 of who chooses by what the handle is

**Registered:** 2026-10-14, before any `world_name` or `parent_id` run with the real model. This
file, the analysis code and `configs/confirm-two-by-two.yaml` are fixed at the commit that adds
this file.

## Background

The stable-ID run ([stable-id-results.md](stable-id-results.md)) separated two effects of
names:

- **Pair hunting** needs only a stable handle. World-assigned IDs matched names.
- **Forming couples and investing in newborns** followed the parent-given name. They were high
  with names and low with world-assigned IDs. On investment this was exploratory: the share of
  holdings given to a newborn was 0.55 with names against 0.43 with IDs.

A parent-given name differs from a world-assigned ID in two ways at once: who chooses it, and
what it is. The arms added in pull request #2 vary each on its own:

| | Word name | ID |
| --- | --- | --- |
| **Parents choose** | `named` | `parent_id` |
| **The world assigns** | `world_name` | `stable_id` |

## Questions

For forming couples and for investing in newborns:

1. **Chooser:** does it matter that parents choose the handle?
2. **Label:** does it matter that the handle is a word name rather than an ID?

## Design

- **Runs:** 60 new runs, `world_name` and `parent_id`, each on seeds 101–128, 131 and 132. These
  are the 30 seeds of the confirmatory and stable-ID runs.
- **Comparison data:** each new run is paired by seed with the existing runs on that seed: named
  and unnamed from `data/confirm-20261014/`, and stable ID from `data/stable-id-20261014/`.
  Runs on one seed share the inheritance draws.
- **Configuration:** `configs/confirm-two-by-two.yaml`, identical to
  `configs/confirm-stable-id.yaml` except for the arms. Every agent is Claude Haiku 5.5 at effort
  `low`. The merged code leaves the named, unnamed and stable_id arms byte-for-byte as they were.
  This is checked against fingerprints recorded before the change.
- **Where it runs:** in Docker, with this command:

  ```bash
  docker compose run --rm pilot pilot --config configs/confirm-two-by-two.yaml --name confirm-two-by-two --parallel 4 --batch-budget 18
  ```

## Primary measures and tests

- **Measures:** both computed by `src/agent_names/analysis.py` as it stands at this commit:
  - couples per generation;
  - mean endowment fraction: the share of its holdings a parent gives its newborn, averaged over
    the run's births.
- **Tests:** eight in total, each contrast on each measure.

  | Contrast | Varies | Holds fixed | Hypothesis, on each measure |
  | --- | --- | --- | --- |
  | C1: `parent_id` vs `stable_id` | Who chooses | An ID | Parent ID higher |
  | C2: `named` vs `world_name` | Who chooses | A word name | Named higher |
  | C3: `world_name` vs `stable_id` | Word or ID | The world assigns | World name higher |
  | C4: `named` vs `parent_id` | Word or ID | Parents choose | Named higher |

- **Each test:** a two-sided paired sign-flip test on the per-seed differences, using 100,000
  random sign patterns from a fixed seed.
- **Correction:** Holm–Bonferroni across all eight tests, with α = 0.05.
- **When a test supports its hypothesis:** its eight-way Holm-adjusted p is below 0.05 and the
  hypothesised arm has the higher mean.
- **Getting the p-values:** run this command once for each contrast. It gives the unadjusted p
  for each measure.

  ```bash
  agent-names summarize data/confirm-20261014/main data/confirm-20261014/replacements data/stable-id-20261014/runs runs/confirm-two-by-two-<timestamp> --pair-by seed --arms <first>,<second> --primary "couples per generation,mean endowment fraction" --out runs/two-by-two-analysis
  ```

  The contrasts are `parent_id,stable_id`, `named,world_name`, `world_name,stable_id` and
  `named,parent_id`. The eight-way correction is then `analysis.holm` applied to the eight
  unadjusted p-values. The within-comparison Holm values the command prints are not used for
  the decision.

## Reading the outcome

For each measure separately:

| Chooser contrasts (C1, C2) | Label contrasts (C3, C4) | Reading |
| --- | --- | --- |
| Both supported | Neither | Parental choice drives it, whatever the label |
| Neither | Both supported | Word names drive it, whoever chooses |
| C2 only | C4 only, or neither | Parental choice matters only for word names. The likeliest source is the family meaning a parent can put into a name |
| C1 only | Any | Parental choice matters for IDs, where the label carries no meaning. The act of choosing is enough |
| Both supported | Both supported | Both matter |
| Neither | Neither | Inconclusive for that measure |

## Exclusions

- **When a run is excluded:** if it fails to complete or uses fallbacks for more than 5% of its
  decisions.
- **What happens then:** the same seed is re-run once in that arm. If the re-run is also excluded,
  that seed is dropped from every contrast that includes that arm.

## Secondary measures (exploratory)

Everything else in the summary tables is reported unadjusted and labelled exploratory. That
includes:

- pair hunts, where every handle arm is expected to match named;
- gathered per forager;
- newborns surviving their first cut;
- parents displaced by their own child;
- the final weight on kin;
- the share of gifts to kin;
- guards.

Also exploratory: in parent_id, how often the two parents pick the same ID; and in world_name,
whether agents comment on the names they are given.

## Known limits

- **Timing:** the new runs happen hours after the runs they are paired with.
- **One extra sentence:** the ID arms' system prompts say an ID is kept for life. The name arms
  say nothing equivalent, so the label contrasts also carry that sentence.
- **Power:** the stable-ID run showed a large named-vs-ID gap on couples (27 of 30 pairs). The
  single-factor gaps could each be much smaller, and 30 pairs may miss them.

## Budget

The expected cost is about $13. Each run stops at $0.40, and no new run starts once the batch has
spent $18.

## Deviations

Any deviation from this plan will be listed in the results with the reason.
