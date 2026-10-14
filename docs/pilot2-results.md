# Second pilot, 2026-10-14

**The batch:** 3 seeds × 2 arms on Claude Haiku 5.5 at effort `low`, run at commit `f07cbff` with
the changed mechanics:

- the archive is known from generation 1;
- collecting memory no longer protects a store, so only another agent's guard stops decay;
- the archivist makes one direct offer per generation, costing a quarter of the first-round
  yield.

The pilot made 4,274 calls and cost **$1.18**, with no errors and no fallback decisions. The
raw data is in [`data/pilot2-20261014/`](../data/pilot2-20261014/), and the first pilot is
described in [pilot-results.md](pilot-results.md).

The same caution applies as before: three runs per arm makes these leads, not findings.

## Per run

| Run | Pair hunts | Guards | Guards to a past helper | Gathered per forager per generation | Parents displaced by own child | Final `kin_weight` | Rules passed | Archivist offers accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| named-s1 | 4 | 11 | 9 | 14.5 | 7 | 0.5 | 9 | 0 of 62 |
| named-s2 | 7 | 15 | 12 | 14.4 | 5 | 0.3 | 12 | 0 of 63 |
| named-s3 | 5 | 3 | 0 | 14.3 | 11 | 0.5 | 10 | 0 of 61 |
| unnamed-s1 | 2 | 3 | 0 | 13.4 | 4 | 0.5 | 7 | 0 of 50 |
| unnamed-s2 | 0 | 5 | 1 | 13.8 | 7 | 0.5 | 4 | 0 of 58 |
| unnamed-s3 | 1 | 6 | 2 | 14.2 | 3 | 0.6 | 6 | 0 of 62 |

## What the changed mechanics produced

- **Guarding works, and it is reciprocal in the named arm.** In two of the three named runs, a
  pair of memory keepers took turns guarding each other's stores. Cedar and Fern did it 10 times
  (named-s1), and Fern and Sorrel 11 times (named-s2), strictly alternating. They arranged it in
  messages ("I will guard your store if you guard mine"). In the named arm, 21 of 29 guards went
  to an agent that had helped the guard before. In the unnamed arm it was 3 of 14. Named-s3 had
  no such pair, so this is not a clean split.
- **The archivist offer is declined every time.** Across 356 offers in six runs, no agent
  accepted. Each one said it was keeping its first-round yield for scoring.

## The first pilot's three splits, re-tested

| Split in the first pilot | Second pilot |
| --- | --- |
| More pair hunts in the named arm | **Holds:** named 4, 7, 5 against unnamed 2, 0, 1. Pair hunting fell sharply in both arms. |
| More parents displaced by their own child in the named arm | **Weaker:** named 7, 5, 11 against unnamed 4, 7, 3. The averages still differ (7.7 against 4.7), but the runs overlap. |
| Higher final `kin_weight` in the unnamed arm | **Weaker:** unnamed 0.5, 0.5, 0.6 against named 0.5, 0.3, 0.5. They tie at 0.5. |

**Foraging output was higher in every named run, in both pilots.** All six named runs gathered
more per forager than any unnamed run (14.3–15.2 against 13.4–14.2). The mechanics differ
between the pilots, so pooling them is rough. Even so, this is the most consistent difference so
far, and it fits the coordination reading: named agents find partners for hunting and guarding
more easily.

**One measure flipped direction.** Named runs passed more rule changes this time (9, 12, 10
against 7, 4, 6), where the first pilot showed the reverse. Treat rule-change counts as noise.
All three named runs reweighted the resources themselves (energy, food, memory). No unnamed run
did.

**One pattern repeated within a seed.** In both pilots, unnamed-s1 voted the credit for giving
up to 1, then gave freely (174 units this time, 479 the first time).

## Suggested next steps

- **Scale up.** Coordination (pair hunts, reciprocal guarding, output) is the lead to test.
  Ten seeds per arm would cost about $4.
- **Keep the archivist offer, but vary its price between batches**, for example 10% and 5%, to
  find where agents start paying.
