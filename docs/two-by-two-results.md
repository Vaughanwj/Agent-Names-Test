# 2 × 2 results, 2026-10-14

**The result: having parents give the handle is what raises couple formation, and the type of
label mainly matters when the world assigns it.** Investment in newborns rose only in the named
arm: names chosen by parents.

- **The plan:** [preregistration-two-by-two.md](preregistration-two-by-two.md), registered at
  commit `0b92bed` before any run of the new arms.
- **The design:** 60 new runs, `world_name` and `parent_id` on the 30 confirmatory seeds. Each
  is paired by seed with that seed's `named`, `unnamed` and `stable_id` runs.
- **The run:** all 60 completed, so nothing was excluded. It made 43,007 calls and cost $12.19.
- **The data:** [`data/two-by-two-20261014/`](../data/two-by-two-20261014/), including the four
  comparison summaries and `holm-eight-way.json`.

## Primary tests

These are pre-registered: two-sided paired sign-flip tests over 30 seed pairs, with a Holm
correction across all eight tests and α = 0.05.

| Contrast | Measure | Means (first vs second) | First higher | p | p (Holm, 8 tests) | Supported |
| --- | --- | --- | --- | --- | --- | --- |
| C1 parent ID vs stable ID (who chooses, IDs) | Couples per generation | 2.53 vs 1.44 | 29 of 30 | ≤ 0.00001 | 0.00008 | **yes** |
| C3 world name vs stable ID (word or ID, world assigns) | Couples per generation | 2.01 vs 1.44 | 23 of 30 | 0.00007 | 0.0005 | **yes** |
| C4 named vs parent ID (word or ID, parents choose) | Share given to a newborn | 0.55 vs 0.47 | 19 of 30 | 0.006 | 0.037 | **yes** |
| C2 named vs world name (who chooses, words) | Couples per generation | 2.38 vs 2.01 | 21 of 30 | 0.008 | 0.039 | **yes** |
| C2 named vs world name (who chooses, words) | Share given to a newborn | 0.55 vs 0.46 | 19 of 30 | 0.014 | 0.058 | no |
| C4 named vs parent ID (word or ID, parents choose) | Couples per generation | 2.38 vs 2.53 | 11 of 30 | 0.17 | 0.50 | no |
| C1 parent ID vs stable ID (who chooses, IDs) | Share given to a newborn | 0.47 vs 0.43 | 19 of 30 | 0.18 | 0.50 | no |
| C3 world name vs stable ID (word or ID, world assigns) | Share given to a newborn | 0.46 vs 0.43 | 17 of 30 | 0.35 | 0.50 | no |

### All five arms side by side

| Measure | Named | Parent ID | World name | Stable ID | Unnamed |
| --- | --- | --- | --- | --- | --- |
| Couples per generation | 2.38 | **2.53** | 2.01 | 1.44 | 1.74 |
| Share given to a newborn | **0.55** | 0.47 | 0.46 | 0.43 | 0.47 |

## What it says

**Forming couples:**

- **Who chooses matters, whatever the label.** Parents giving their children the handle raised
  couple formation both with IDs (C1) and with word names (C2).
- **The label matters only when the world assigns it.** Among world-assigned handles, word names
  formed more couples than IDs (C3). Among parent-given handles, word names added nothing; parent
  IDs were if anything slightly higher (C4).
- **Either source is enough, and they don't add up.** A parental choice or a word name each
  lifts couple formation above a bare world-assigned ID. The parental choice lifts it more, and
  having both adds nothing.
- **This wasn't one of the registered readings.** The table in the pre-registration expected the
  chooser and label effects to line up symmetrically. The closest registered reading is "both
  matter", but the label effect appears in only one of its two contrasts.

**Investing in newborns:**

- **Only names chosen by parents stand out.** Named-arm parents gave about 0.55 of their holdings.
  Every other arm gave 0.43–0.47, including unnamed.
- **The supported test:** named against parent ID (C4).
- **The near miss:** named against world name (C2) fell just short after correction (p = 0.058).
- **No other combination raised investment:** neither a parental choice of an ID (C1) nor a
  word name from the world (C3) did.
- **How to read it:** the pattern fits the registered reading that family meaning a parent can
  put into a name drives investment. That reading needed C2 to pass correction, and it didn't
  quite, so it stays a strong lead rather than a confirmed result.

## The "choice" in parent_id is nominal

- **Parents almost always took the first ID offered:** 96% of picks were the first of the three
  IDs, and the two parents picked the same one in 94% of births.
- **What that means for couples:** the parent-ID lift in couples does not come from deliberating
  over which label to give. It comes from the parental role itself. Agents are told from the
  start that parents give their children IDs, and they are asked to do so at each birth.
- **The size of the lift:** that role alone, applied to a meaningless ID, lifted couple
  formation from 1.44 to 2.53 per generation.

## Exploratory

These are unadjusted.

| Measure | Named | Parent ID | World name | Stable ID | Unnamed |
| --- | --- | --- | --- | --- | --- |
| Pair hunts | 13.4 | 10.8 | 12.2 | 13.1 | 2.7 |
| Final `kin_weight` | 0.45 | 0.46 | 0.46 | 0.27 | 0.36 |
| Newborns surviving their first cut | 17.0 | 17.8 | 13.3 | 10.0 | 11.7 |
| Parents displaced by their own child | 9.3 | 10.5 | 4.8 | 4.9 | 5.4 |
| Share of gifts to kin | 0.44 | 0.60 | 0.66 | 0.63 | 0.84 |

- **Pair hunting needs only a stable handle.** All four handle arms hunt together at about the
  same rate, far above unnamed. This confirms the stable-ID finding.
- **Kin-weight votes follow couples.** They are low only in the stable-ID arm. Parent ID vs stable
  ID gives p = 0.004, and world name vs stable ID p = 0.0015.
- **Newborn survival and displacement track the number of births.** Both are highest where most
  couples form (named and parent ID), so they say little beyond couples.
- **World-named agents never talked about their names:** 0 of 12,000 messages.

## Across all the studies

| What agents do | What drives it |
| --- | --- |
| Hunting together | Any stable handle. Names, world names, parent IDs and world IDs all work. |
| Forming couples and voting weight to kin | Parents giving the handle, most strongly. Otherwise a word name. A bare world ID does no better than no handle. |
| Investing in each newborn | Only a word name chosen by parents |

## Limits

- **Timing:** the new runs happened hours after the runs they are paired with.
- **Different prompt text:** the ID arms' prompts say IDs are kept for life, and the name arms'
  prompts don't.
- **Correlated measures:** couples and kin-weight votes are tested on the same populations.
- **No tribalism:** unnamed agents still give the largest share of their gifts to kin.

## Cost

$12.19 for 60 runs. Spending for the whole project is now $37.16.
