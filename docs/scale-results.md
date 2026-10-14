# Scale-up: 13 seed pairs, 2026-10-14

**The batch:** 10 new seeds per arm (seeds 4–13) under the second pilot's mechanics, run in
Docker at commit `e52adf2`. They are pooled with the second pilot's seeds 1–3, for 13 seed pairs
in total. The archivist's price differed by seed:

| Seeds | Archivist price (share of first-round yield) |
| --- | --- |
| 1–3 (second pilot) | 25% |
| 4–8 | 10% |
| 9–13 | 5% |

Both runs in a pair always shared the same price, so the arm comparison is unaffected. The two
new batches made 8,606 calls and cost **$3.88**, with no errors and no fallback decisions.

- **Data:** [`data/scale-20261014/`](../data/scale-20261014/), with the pooled summary in
  `pooled-13-pairs/summary.md`.
- **The test:** each p below is an exact two-sided sign-flip test on the 13 paired differences
  (named minus unnamed, same seed).
- **How to read it:** about 15 measures were tested, so roughly one would fall under 0.05 by
  chance. Nothing here survives a correction for that.

## Named against unnamed

| Measure | Named | Unnamed | Named higher | p |
| --- | --- | --- | --- | --- |
| Couples per generation | 2.40 | 1.93 | 9 of 13 | 0.045 |
| Gathered per forager per generation | 14.30 | 13.93 | 10 of 13 | 0.058 |
| Pair hunts | 10.4 | 4.7 | 9 of 13 | 0.069 |
| Newborns surviving their first cull | 16.2 | 13.3 | 8 of 13 | 0.082 |
| Parents displaced by their own child | 8.8 | 6.2 | 8 of 13 | 0.11 |
| Share of gifts to kin (pairs with gifts in both arms) | 0.40 | 0.81 | 2 of 8 | 0.055 |
| Guards | 6.5 | 6.8 | 4 of 13 | 0.93 |
| Guards to a past helper | 3.0 | 1.9 | 5 of 13 | 0.46 |
| Rule changes passed | 7.0 | 6.4 | 6 of 13 | 0.65 |
| Final `kin_weight` | 0.45 | 0.49 | 1 of 13 | 0.30 |
| Mean share of holdings given at birth | 0.51 | 0.48 | 8 of 13 | 0.52 |

## What it says

1. **Coordination is the steadiest direction.** In the named arm, more couples formed, more
   pairs hunted together, foragers gathered more and more newborns survived. Each falls short
   of a corrected threshold, but they point the same way, and the hunting and output
   differences were also present in the first pilot. This fits the reputation prediction in
   its weakest form: names make it easier to find and keep partners.
2. **Reciprocal guarding did not replicate.** It was striking in two second-pilot runs (Cedar
   and Fern, Fern and Sorrel), but it does not separate the arms across 13 pairs.
3. **Tribalism is not supported.** If anything it runs the other way: where both arms gave
   gifts, unnamed agents directed more of them to kin. Few pairs had gifts to compare.
4. **The archivist is effectively ignored at every price:**

   | Price | Named: accepted / offers | Unnamed: accepted / offers |
   | --- | --- | --- |
   | 25% | 0 / 186 | 0 / 170 |
   | 10% | 1 / 292 | 3 / 280 |
   | 5% | 1 / 324 | 2 / 298 |

   Cutting the price fivefold moved take-up from 0 to about 0.5%. Under individual-first
   scoring, these agents put almost no value on their ancestry, named or not.

## Before a confirmatory run

- **Fix the primary measures in advance.** Choosing them after seeing the data inflates false
  positives. Couples per generation, pair hunts and gathered per forager are the obvious
  candidates.
- **Size it.** Effects this size need roughly 25–30 seed pairs to show clearly. At about $0.39
  per pair, 30 pairs is about $12.
- **Keep or drop the archivist.** It stays in the design as a measure, but it yields almost no
  data. To study ancestry, the more promising lever is the scoring rule, for example starting
  some batches with `kin_weight` above 0, rather than the archivist's price.
