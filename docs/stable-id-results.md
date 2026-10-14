# Stable-ID results, 2026-10-14

**The result: names do two separate jobs.** A stable handle of any kind is enough for
coordinating with others: stable IDs held as many pair hunts as names. Forming families needs a
parent-given name: named populations formed far more couples than stable-ID populations, and
stable IDs gave no lift over no handle at all.

- **The plan:** [preregistration-stable-id.md](preregistration-stable-id.md), registered at
  commit `6136b3e` before any stable-ID run.
- **The design:** 30 stable-ID runs on the 30 confirmatory seeds. Each is paired by seed with
  that seed's named and unnamed runs from [confirmatory-results.md](confirmatory-results.md).
- **The run:** all 30 completed, so nothing was excluded. It made 20,898 calls and cost $5.88.
- **The data:** [`data/stable-id-20261014/`](../data/stable-id-20261014/), including both
  comparison summaries and `holm-four-way.json`.

## Primary tests

These are pre-registered: two-sided paired sign-flip tests over 30 seed pairs, with a Holm
correction across all four tests and α = 0.05.

| Test | Comparison | Measure | Means | First arm higher | p | p (Holm, 4 tests) | Supported |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1b | Stable ID vs unnamed | Pair hunts | 13.1 vs 2.7 | 26 of 30 | ≤ 0.00001 | 0.00004 | yes |
| H2a | Named vs stable ID | Couples per generation | 2.38 vs 1.44 | 27 of 30 | ≤ 0.00001 | 0.00004 | yes |
| H1a | Stable ID vs unnamed | Couples per generation | 1.44 vs 1.74 | 11 of 30 | 0.046 | 0.092 | no |
| H2b | Named vs stable ID | Pair hunts | 13.4 vs 13.1 | 15 of 30 | 0.87 | 0.87 | no |

Each measure is read against the registered table:

- **Pair hunts** (H1 supported, H2 not): a stable handle explains the effect. Stable IDs
  restore the named arm's level of pair hunting almost exactly.
- **Couples per generation** (H1 not supported, H2 supported): a handle alone is not enough.
  Something about parent-given names matters. If anything, stable IDs formed slightly fewer
  couples than no handle at all, though not significantly after correction.

## Exploratory measures

These are unadjusted, so read them as leads.

| Measure | Named | Stable ID | Unnamed | Named vs stable ID p | Stable ID vs unnamed p |
| --- | --- | --- | --- | --- | --- |
| Gathered per forager per generation | 14.01 | 14.21 | 13.80 | 0.13 | 0.003 |
| Share of holdings given to a newborn | 0.55 | 0.43 | 0.47 | 0.0002 | 0.16 |
| Newborns surviving their first cut | 17.0 | 10.0 | 11.7 | ≤ 0.00001 | 0.11 |
| Parents displaced by their own child | 9.3 | 4.9 | 5.4 | ≤ 0.00001 | 0.56 |
| Final `kin_weight` | 0.45 | 0.27 | 0.36 | 0.0015 | 0.21 |
| Share of gifts to kin | 0.44 | 0.63 | 0.84 | 0.10 | 0.03 |
| Guards | 6.9 | 9.0 | 8.1 | 0.22 | 0.57 |

The exploratory measures split along the same line as the primary tests:

- **Working with others tracks the handle.** Stable IDs match names on pair hunting and lift
  gathering above the unnamed arm.
- **Family tracks the name.** Every family measure is high in the named arm and low in both
  other arms: couples formed, the share given to newborns, newborn survival, parents giving way
  to their children, and votes for more weight on kin. Stable IDs look like no handle at all on
  these.

## What it means

Being able to point at the same agent again is what lets agents coordinate a hunt. Names
supply that, but so does "A47". Choosing partners, investing in children and voting to reward
kin depend on something a name has and an ID lacks. Within the named arm that is one of three
things, which this design can't separate:

1. **Who chooses the label.** Parents choose names; the world assigns IDs.
2. **The naming act.** Named-arm parents propose a name in the same decision where they set the
   endowment. The system prompt also tells every named-arm agent in advance that parents name
   their children.
3. **What the label says.** A name can carry family ("Ember Three"); an ID can't.

The couples effect appears at pairing, before any child is born or named. So it can't come only
from the act of naming at birth. Knowing that one will name a child, or seeing kin names around,
may be enough.

## Limits

- **Timing:** the stable-ID runs happened hours after the named and unnamed runs they are paired
  with.
- **Different prompt text:** the stable-ID arm's system prompt says IDs are kept for life. The
  named arm says nothing equivalent about names.
- **Next arms:** separating the three candidates above would need more arms. For example,
  parents could choose from neutral IDs, or the world could assign word names that carry no
  family meaning.

## Cost

$5.88 for 30 runs. Spending for the whole project is now $24.97.
