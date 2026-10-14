# Confirmatory results, 2026-10-14

**The result:** names increased coordination. Two of the three pre-registered primary measures
support the hypothesis, after a Holm correction, which meets the registered threshold for that
claim. The third measure did not.

- **The plan:** [preregistration.md](preregistration.md), registered at commit `a324dbc` before
  any data was collected.
- **The design:** 30 seed pairs on fresh seeds, each pair a named run and an unnamed run with
  the same seed, all on Claude Haiku 5.5, run in Docker.
- **The data:** [`data/confirm-20261014/`](../data/confirm-20261014/). The event logs are
  gzipped, and `agent-names summarize` reads them directly.

## Primary measures

These are pre-registered: a two-sided paired sign-flip test over 30 pairs, with a Holm
correction across the three measures and α = 0.05.

| Measure | Named | Unnamed | Named higher | p | p (Holm) | Supported |
| --- | --- | --- | --- | --- | --- | --- |
| Couples per generation | 2.38 | 1.74 | 23 of 30 | 0.00004 | 0.00008 | yes |
| Pair hunts | 13.4 | 2.7 | 28 of 30 | ≤ 0.00001 | 0.00003 | yes |
| Gathered per forager per generation | 14.01 | 13.80 | 19 of 30 | 0.11 | 0.11 | no |

- **Couples:** named populations formed about 37% more couples per generation.
- **Pair hunts:** named populations held about five times as many pair hunts.
- **Gathering:** per-forager output leaned the same way but was not significant. The extra
  hunting did not turn into clearly higher totals.

## Exploratory measures

These are unadjusted, so read them as leads. With about 13 of them, a Bonferroni threshold
would be about 0.004.

| Measure | Named | Unnamed | Named higher | p |
| --- | --- | --- | --- | --- |
| Newborns surviving their first cut | 17.0 | 11.7 | 26 of 30 | ≤ 0.00001 |
| Parents displaced by their own child | 9.3 | 5.4 | 25 of 30 | 0.00003 |
| Share of holdings given to a newborn | 0.55 | 0.47 | 21 of 30 | 0.003 |
| Share of gifts to kin (17 pairs with gifts in both arms) | 0.44 | 0.84 | 4 of 17 | 0.008 |
| Guards | 6.9 | 8.1 | 11 of 30 | 0.33 |
| Guards to a past helper | 3.0 | 4.5 | 9 of 30 | 0.14 |
| Rule changes passed | 6.9 | 5.9 | 14 of 30 | 0.19 |
| Final `kin_weight` | 0.45 | 0.36 | 12 of 30 | 0.08 |
| Archivist offers accepted at 10% | 6 of 1,837 | 3 of 1,692 | | 0.45 |

Two patterns stand out:

1. **Named parents invest more in their children.** They give a larger share of their holdings
   at birth, more of their newborns survive, and more of them are cut while their own child
   stays. The first pilot pointed the same way. The three measures overlap, because larger
   endowments drive both survival and displacement, so treat them as one finding, not three.
2. **There is no tribalism.** When unnamed agents gave gifts, they gave most of them to kin.
   Named agents gave a larger share to non-kin. That is the opposite of the tribalism
   prediction.

## What the effect might be

The two arms differ only in names, and agents in both arms see identical information about one
another. But a name is also a stable handle. Named agents can say "Brook, let's hunt this round"
and mean the same agent next round. Unnamed agents only have bracket numbers, which are
reshuffled at every prompt so they can't harden into names. When unnamed agents tried to use
them (5% of their messages), the number pointed at someone else by the next decision. About 10%
of named agents' messages addressed another agent by name.

So this result shows that **parent-given names increase coordination**. It does not yet show
whether that comes from **being named by a parent** or from **having any stable handle at
all**. The design doc anticipated this: an ID like "A7" quietly becomes a name in practice. A
third arm with stable assigned IDs, kept across rounds but not chosen by parents, would
separate the two. The parental-investment pattern has a similar ambiguity. In the named arm,
parents propose names in the same decision where they choose the endowment, so naming a child
and investing in it happen together.

## Deviations from the plan

1. **Four runs failed.** Seeds 129 and 130, in both arms, stopped when the Anthropic account
   reached its own API usage limit. As registered, both pairs were excluded and replaced by seeds
   131 and 132. These ran after the limit was raised, in a separate batch folder.
2. **The analysis covered two folders.** The registered command named one batch folder. It was
   run on the main batch and the replacement batch together.
3. **The exclusion rule was coded after registration.** It went into the analysis code at commit
   `88f52c1`, after data collection but before any primary measure was looked at. The rule
   itself is unchanged.
4. **Some p-values sit at the floor.** A p shown as ≤ 0.00001 is the smallest value 100,000
   random sign patterns can resolve.

## Cost

| Part | Cost |
| --- | --- |
| Main batch (60 runs, of which 4 failed) | $11.30 |
| Replacements (4 runs) | $0.77 |
| **Total** | **$12.07** |
