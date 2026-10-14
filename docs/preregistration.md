# Pre-registration: confirmatory run

**Registered:** 2026-10-14, before any confirmatory data was collected. This file, the analysis
code and `configs/confirm.yaml` are fixed at the commit that adds this file. The git history
records that commit's time.

## Background

An exploratory analysis of 13 seed pairs ([scale-results.md](scale-results.md)) found that named
populations leaned towards more coordination than unnamed ones on three measures. None
survived a correction for the roughly 15 measures examined. This run tests those three
measures on fresh seeds.

## Hypothesis

Agents given names by their parents coordinate more than agents without names. Each of the
three primary measures is expected to be higher in the named arm.

## Design

- **Seed pairs:** 30, seeds 101–130. None of these seeds has been run before. Each pair is one
  named run and one unnamed run with the same seed, so the two runs have identical inheritance
  draws and differ only in names.
- **Configuration:** `configs/confirm.yaml`. The mechanics are those of the exploratory
  scale-up:
  - the archive is known from generation 1;
  - only another agent's guard stops memory decay;
  - the archivist makes one offer per generation, at 10% of first-round yield.
- **Model:** every agent is Claude Haiku 5.5 (`claude-haiku-5-5`) at effort `low`.
- **Where it runs:** in Docker, with this command:

  ```bash
  docker compose run --rm pilot pilot --config configs/confirm.yaml --name confirm --parallel 4 --batch-budget 16
  ```

## Primary measures

Each measure is computed per run by `src/agent_names/analysis.py` as it stands at this commit:

1. **Couples per generation:** the mean, over the 8 generations, of couples formed.
2. **Pair hunts:** the number of pair hunts in the run, counting only rounds where both partners
   chose to hunt with each other.
3. **Gathered per forager per generation:** the mean, over generations, of resources gathered
   per agent present at scoring, newborns excluded.

## Analysis

- **Per pair:** the difference, named minus unnamed.
- **Per measure:** a two-sided sign-flip permutation test on the 30 differences, using 100,000
  random sign patterns from a fixed seed (`analysis.paired_test`).
- **Correction:** Holm–Bonferroni across the three primary measures, with α = 0.05.
- **When a measure supports the hypothesis:** its Holm-adjusted p is below 0.05 and its named
  mean is higher than its unnamed mean.
- **The overall claim:** "names increased coordination" is made only if at least two of the
  three primary measures support it. Each measure is also reported on its own.
- **The command:**

  ```bash
  agent-names summarize runs/confirm-<timestamp> --primary "couples per generation,pair hunts,gathered per forager per generation"
  ```

## Exclusions and stopping

- **When a pair is excluded:** if either run fails to complete (including by reaching its $0.40
  cap) or has more than 5% fallback decisions. There are no other exclusions.
- **Replacing excluded pairs:** with the next seeds from 131 upward, in order, until there are
  30 complete pairs or 10 replacements have been used. If fewer than 30 complete pairs remain,
  the analysis runs on those that completed, and the report says so.
- **No early looks:** during the run, only progress, spend and errors are monitored. No primary
  measure is looked at until every pair is complete.

## Secondary measures (exploratory)

Everything else in the summary table is reported unadjusted and labelled exploratory:

- archivist take-up at 10%;
- guards, and guards to a past helper;
- share of gifts to kin;
- parents displaced by their own child;
- newborns surviving their first cut;
- rule changes passed, and the final weight on kin.

## Power and interpretation

The exploratory paired effect sizes were 0.56–0.63. With 30 pairs, a simulation gives about
66–80% power at Holm's strictest threshold (0.05 / 3). Exploratory effects usually overestimate
true ones, so a null result here would not show that names have no effect. It would only show
that any effect is smaller than the exploratory data suggested.

## Budget

The expected cost is about $12. Each run stops at $0.40, and no new run starts once the batch has
spent $16.

## Deviations

Any deviation from this plan will be listed in the results with the reason.
