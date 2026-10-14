# Pre-registration: the stable-ID arm

**Registered:** 2026-10-14, before any stable-ID run with the real model. This file, the
analysis code and `configs/confirm-stable-id.yaml` are fixed at the commit that adds this file.

## Background

The confirmatory run ([confirmatory-results.md](confirmatory-results.md)) found that named
populations formed more couples and held more pair hunts than unnamed ones. A name is also a
stable handle: agents can address each other by it across rounds, while unnamed agents only see
numbers that are reshuffled at every prompt. The `stable_id` arm gives every agent a neutral ID
(for example "A47") that the world assigns at creation and that never changes. No parent
chooses it, and parents are never asked to name anyone.

## Questions

1. **Handle:** does a stable handle on its own increase coordination? This compares stable ID
   with unnamed.
2. **Name:** does a parent-given name increase coordination beyond what a stable handle does?
   This compares named with stable ID.

The second comparison bundles three things together: who chooses the label, the act of naming
at birth, and what a name can say (such as a family link, "Ember Three"). It can show that
parent-given names add something beyond a handle, but not which of these is responsible.

## Design

- **Runs:** 30 stable-ID runs on seeds 101–128, 131 and 132. These are the 30 seeds that
  completed in the confirmatory run.
- **Comparison data:** each new run is paired by seed with that seed's existing named and
  unnamed runs in `data/confirm-20261014/`. They share the seed, so they share the inheritance
  draws.
- **Configuration:** `configs/confirm-stable-id.yaml`, identical to `configs/confirm.yaml`
  except for the arm and the seeds. Every agent is Claude Haiku 5.5 at effort `low`.
- **Arm-specific text:** the merged code leaves the named and unnamed arms' prompts, logs and
  archives exactly as they were (pull request #1). The one place the stable-ID arm's text
  differs is its system prompt, which says an ID is kept for life and never shared. A name's
  permanence is taken for granted; an ID's is not.
- **Where it runs:** in Docker, with this command:

  ```bash
  docker compose run --rm pilot pilot --config configs/confirm-stable-id.yaml --name confirm-stable-id --parallel 4 --batch-budget 9
  ```

## Primary measures and tests

- **Measures:** the two that the confirmatory run supported, computed by
  `src/agent_names/analysis.py` as it stands at this commit:
  - couples per generation;
  - pair hunts.
- **Tests:** four in total.

  | Test | Comparison | Measure | Hypothesis |
  | --- | --- | --- | --- |
  | H1a | Stable ID vs unnamed | Couples per generation | Stable ID higher |
  | H1b | Stable ID vs unnamed | Pair hunts | Stable ID higher |
  | H2a | Named vs stable ID | Couples per generation | Named higher |
  | H2b | Named vs stable ID | Pair hunts | Named higher |

- **Each test:** a two-sided paired sign-flip test on the per-seed differences, using 100,000
  random sign patterns from a fixed seed.
- **Correction:** Holm–Bonferroni across all four tests, with α = 0.05.
- **When a test supports its hypothesis:** its four-way Holm-adjusted p is below 0.05 and the
  hypothesised arm has the higher mean.
- **Getting the p-values:** run these two commands, which give each test's unadjusted p:

  ```bash
  agent-names summarize data/confirm-20261014/main data/confirm-20261014/replacements runs/confirm-stable-id-<timestamp> --pair-by seed --arms stable_id,unnamed --primary "couples per generation,pair hunts" --out runs/stable-id-analysis
  ```

  ```bash
  agent-names summarize data/confirm-20261014/main data/confirm-20261014/replacements runs/confirm-stable-id-<timestamp> --pair-by seed --arms named,stable_id --primary "couples per generation,pair hunts" --out runs/stable-id-analysis
  ```

  The four-way correction is then `analysis.holm` applied to those four unadjusted p-values.
  The Holm-adjusted p each command prints corrects only within its own comparison, so it is not
  used for the decision.

## Reading the outcome

These readings are registered in advance:

| H1 (stable ID above unnamed) | H2 (named above stable ID) | Reading |
| --- | --- | --- |
| Supported on a measure | Not supported | A stable handle explains the effect on that measure |
| Supported | Supported | A handle helps, and parent-given names add something on top |
| Not supported | Supported | A handle alone is not enough; something about parent-given names matters |
| Not supported | Not supported | Inconclusive for that measure |

## Exclusions

- **When a run is excluded:** if it fails to complete or uses fallbacks for more than 5% of its
  decisions.
- **What happens then:** the same seed is re-run once, because a different seed would have no
  named or unnamed partner. If the re-run is also excluded, that seed is dropped from both
  comparisons.
- **Seeds without partners:** seeds 129 and 130 have no complete named or unnamed runs and are
  not run.

## Secondary measures (exploratory)

Everything else in the summary tables is reported unadjusted and labelled exploratory. That
includes gathered per forager, the share of holdings given to newborns, newborns surviving their
first cut, parents displaced by their own child, the share of gifts to kin, guards and archivist
take-up.

## Known limits

- **Timing:** the stable-ID runs happen hours after the named and unnamed runs they are paired
  with. The model and code for those arms are unchanged, but the provider's serving can't be
  held fixed.
- **Power:** named against unnamed was a large difference (pair hunts higher in 28 of 30
  pairs). Named against stable ID may be much smaller, and 30 pairs may not detect it, so a
  null result on H2 would be weak evidence.

## Budget

The expected cost is about $6. Each run stops at $0.40, and no new run starts once the batch has
spent $9.

## Deviations

Any deviation from this plan will be listed in the results with the reason.
