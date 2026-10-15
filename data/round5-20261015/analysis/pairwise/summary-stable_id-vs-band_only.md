# Batch summary: Stable ID vs Band only

Batches: confirm-round5-20261015-031539. Runs: 60. Seed pairs (stable_id and band_only with the same seed): 30.

p is a two-sided paired sign-flip test across seed pairs: exact up to 20 pairs, 100,000 random sign patterns above that. With few pairs it cannot go low: 3 pairs give at best 0.25.

| Measure (mean over runs) | Stable ID | Band only | Stable ID higher (of pairs) | p |
| --- | --- | --- | --- | --- |
| gathered per forager per generation | 14.263 | 14.041 | 20 of 30 | 0.0133 |
| pair hunts | 8.4 | 3.1 | 25 of 30, 1 tied | 1e-05 |
| guards | 7.3 | 6.633 | 15 of 30, 1 tied | 0.50013 |
| guards to a past helper | 4.167 | 3.0 | 16 of 30, 3 tied | 0.14326 |
| gift amount | 21.46 | 13.392 | 9 of 30, 15 tied | 0.72408 |
| gift amount while giving still cost something | 3.018 | 1.587 | 6 of 30, 18 tied | 0.47157 |
| gift share to kin | 0.556 | 0.473 | 1 of 3, 1 tied | 1.0 |
| gift share to past helpers | 0.159 | 0.137 | 0 of 3, 1 tied | 0.5 |
| archivist take-up (share of offers accepted) | 0.001 | 0.001 | 1 of 30, 28 tied | 1.0 |
| rules passed | 5.133 | 5.767 | 11 of 30, 3 tied | 0.39874 |
| final kin weight | 0.267 | 0.277 | 8 of 30, 9 tied | 0.90569 |
| mean endowment fraction | 0.425 | 0.337 | 24 of 30 | 0.00058 |
| parents displaced by own child | 3.967 | 5.067 | 14 of 30, 1 tied | 0.17709 |
| newborns surviving first cull | 9.667 | 10.933 | 10 of 30, 3 tied | 0.22198 |
| couples per generation | 1.396 | 1.933 | 6 of 30, 1 tied | 0.00032 |
| shared kills | 0.367 | 0.267 | 5 of 30, 22 tied | 0.686 |
| share of kills shared | 0.029 | 0.064 | 5 of 20, 11 tied | 0.625 |
| commons contribution share | 0.033 | 0.029 | 8 of 30, 3 tied | 0.70176 |
| commons contributors giving nothing | 0.938 | 0.929 | 22 of 30, 3 tied | 0.75361 |
| in-band gift bias | None | 0.067 | 0 of 0 | None |
| in-band guard bias | None | 0.222 | 0 of 0 | None |
| in-band hunt bias | None | 0.173 | 0 of 0 | None |
| in-band couple bias | None | 0.161 | 0 of 0 | None |
| namesake minus co-parent endowment share | None | None | 0 of 0 | None |
| namesake minus co-parent later gifts | None | None | 0 of 0 | None |
| fallback decisions | 0.0 | 0.0 | 0 of 30, 30 tied | 1.0 |

| Archivist price (share of first-round yield) | Stable ID: accepted / offers | Band only: accepted / offers |
| --- | --- | --- |
| 10% | 1 / 1593 | 1 / 1778 |
