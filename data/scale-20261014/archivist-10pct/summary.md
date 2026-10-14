# Batch summary

Batches: scale-p10-20261014-150854. Runs: 10. Seed pairs (named and unnamed with the same seed): 5.

p is an exact paired sign-flip test across seed pairs (two-sided). With few pairs it cannot go low: 3 pairs give at best 0.25.

| Measure (mean over runs) | Named | Unnamed | Named higher (of pairs) | p |
| --- | --- | --- | --- | --- |
| gathered per forager per generation | 14.485 | 13.809 | 4 of 5 | 0.125 |
| pair hunts | 18.0 | 5.2 | 4 of 5 | 0.125 |
| guards | 4.8 | 7.4 | 1 of 5 | 0.1875 |
| guards to a past helper | 1.2 | 2.6 | 0 of 5, 1 tied | 0.125 |
| gift amount | 29.592 | 28.768 | 1 of 5, 1 tied | 1.0 |
| gift amount while giving still cost something | 29.592 | 28.768 | 1 of 5, 1 tied | 1.0 |
| gift share to kin | 0.303 | 0.75 | 0 of 3 | 0.25 |
| gift share to past helpers | 0.246 | 0.044 | 1 of 3, 1 tied | 1.0 |
| archivist take-up (share of offers accepted) | 0.003 | 0.011 | 0 of 5, 4 tied | 1.0 |
| rules passed | 5.2 | 5.8 | 2 of 5, 1 tied | 0.875 |
| final kin weight | 0.4 | 0.42 | 1 of 5, 1 tied | 1.0 |
| mean endowment fraction | 0.503 | 0.498 | 3 of 5 | 0.875 |
| parents displaced by own child | 9.6 | 7.4 | 2 of 5 | 0.8125 |
| newborns surviving first cull | 16.0 | 13.4 | 3 of 5, 1 tied | 0.625 |
| couples per generation | 2.425 | 1.825 | 4 of 5 | 0.1875 |
| fallback decisions | 0.0 | 0.0 | 0 of 5, 5 tied | 1.0 |

| Archivist price (share of first-round yield) | Named: accepted / offers | Unnamed: accepted / offers |
| --- | --- | --- |
| 10% | 1 / 292 | 3 / 280 |

Names chosen in the named arm: Sprig, Sorrel, Lark, Thistle, Wren, Bramble, Thistlewren, Thorn, Sable, Wisp, Fernwick, Lichen, Moss, Kindle, Briar, Cinderlark, Cinder, Quill, Dusklark, Sparrowlight, Emberlin, Sprig, Sorrel, Sable, Kindle, Thistle, Wick, Spark, Tansy, Quill, Cinder, Flint, Briar, Rush, Wren, Soot, Yarrow, Fennel, Kestrel, Moss, Mallow, Sprig, Sorrel, Quill, Cinder, Thistle, Wren, Moss, Lichen, Lark, Bramble, Lumen, Sable, Sage, Tinder, Kestrel, Fennel, Yarrow, Wicket, Bryony, Thornlet, Linden, Sorrel, Sprig, Thistle, Cinder, Moss, Ashlet, Tansy, Clover, Kindle, Ashwick, Fernwick, Fennel, Sable, Bramble, Wren, Yarrow, Lark, Tallow, Nettle, Thimble, Sorrel, Moss, Sprig, Tansy, Thistle, Rue, Marrow, Fennel, Clover, Sorrow, Yarrow, Sorrelkin, Sage, Bramble, Wren
