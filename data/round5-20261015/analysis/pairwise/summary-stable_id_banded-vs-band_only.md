# Batch summary: Stable ID with band vs Band only

Batches: confirm-round5-20261015-031539. Runs: 60. Seed pairs (stable_id_banded and band_only with the same seed): 30.

p is a two-sided paired sign-flip test across seed pairs: exact up to 20 pairs, 100,000 random sign patterns above that. With few pairs it cannot go low: 3 pairs give at best 0.25.

| Measure (mean over runs) | Stable ID with band | Band only | Stable ID with band higher (of pairs) | p |
| --- | --- | --- | --- | --- |
| gathered per forager per generation | 14.414 | 14.041 | 18 of 30 | 0.00436 |
| pair hunts | 16.733 | 3.1 | 29 of 30 | 1e-05 |
| guards | 6.467 | 6.633 | 14 of 30, 3 tied | 0.90612 |
| guards to a past helper | 3.267 | 3.0 | 14 of 30, 2 tied | 0.77823 |
| gift amount | 13.011 | 13.392 | 18 of 30, 9 tied | 0.99999 |
| gift amount while giving still cost something | 5.013 | 1.587 | 16 of 30, 11 tied | 0.00378 |
| gift share to kin | 0.463 | 0.473 | 2 of 6, 2 tied | 0.875 |
| gift share to past helpers | 0.068 | 0.137 | 1 of 6, 3 tied | 0.75 |
| archivist take-up (share of offers accepted) | 0.0 | 0.001 | 0 of 30, 29 tied | 1.0 |
| rules passed | 4.5 | 5.767 | 12 of 30, 3 tied | 0.13006 |
| final kin weight | 0.173 | 0.277 | 7 of 30, 8 tied | 0.16538 |
| mean endowment fraction | 0.362 | 0.337 | 17 of 30 | 0.2954 |
| parents displaced by own child | 3.733 | 5.067 | 10 of 30, 2 tied | 0.11085 |
| newborns surviving first cull | 9.3 | 10.933 | 9 of 30, 3 tied | 0.08885 |
| couples per generation | 1.467 | 1.933 | 7 of 30, 1 tied | 0.00139 |
| shared kills | 1.5 | 0.267 | 18 of 30, 10 tied | 0.00023 |
| share of kills shared | 0.102 | 0.064 | 10 of 20, 6 tied | 0.2517 |
| commons contribution share | 0.029 | 0.029 | 11 of 30 | 0.99529 |
| commons contributors giving nothing | 0.947 | 0.929 | 18 of 30, 1 tied | 0.18237 |
| in-band gift bias | 0.197 | 0.067 | 3 of 6 | 0.5938 |
| in-band guard bias | 0.03 | 0.222 | 10 of 29 | 0.03103 |
| in-band hunt bias | 0.203 | 0.173 | 12 of 23, 1 tied | 0.58243 |
| in-band couple bias | 0.1 | 0.161 | 12 of 30 | 0.15859 |
| namesake minus co-parent endowment share | None | None | 0 of 0 | None |
| namesake minus co-parent later gifts | None | None | 0 of 0 | None |
| fallback decisions | 0.0 | 0.0 | 0 of 30, 30 tied | 1.0 |

| Archivist price (share of first-round yield) | Stable ID with band: accepted / offers | Band only: accepted / offers |
| --- | --- | --- |
| 10% | 0 / 1566 | 1 / 1778 |
