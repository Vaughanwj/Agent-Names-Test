# Batch summary: Named vs Stable ID with band

Batches: confirm-round5-20261015-031539. Runs: 60. Seed pairs (named and stable_id_banded with the same seed): 30.

p is a two-sided paired sign-flip test across seed pairs: exact up to 20 pairs, 100,000 random sign patterns above that. With few pairs it cannot go low: 3 pairs give at best 0.25.

| Measure (mean over runs) | Named | Stable ID with band | Named higher (of pairs) | p |
| --- | --- | --- | --- | --- |
| gathered per forager per generation | 14.17 | 14.414 | 12 of 30 | 0.0369 |
| pair hunts | 12.733 | 16.733 | 12 of 30 | 0.06586 |
| guards | 8.033 | 6.467 | 18 of 30, 1 tied | 0.25219 |
| guards to a past helper | 4.167 | 3.267 | 15 of 30, 2 tied | 0.37703 |
| gift amount | 34.132 | 13.011 | 20 of 30, 2 tied | 0.13859 |
| gift amount while giving still cost something | 12.155 | 5.013 | 18 of 30, 2 tied | 0.02452 |
| gift share to kin | 0.524 | 0.463 | 9 of 18, 1 tied | 0.7679 |
| gift share to past helpers | 0.106 | 0.068 | 6 of 18, 9 tied | 0.8125 |
| archivist take-up (share of offers accepted) | 0.003 | 0.0 | 5 of 30, 25 tied | 0.06283 |
| rules passed | 5.767 | 4.5 | 17 of 30, 3 tied | 0.03901 |
| final kin weight | 0.337 | 0.173 | 16 of 30, 8 tied | 0.01937 |
| mean endowment fraction | 0.499 | 0.362 | 25 of 30 | 0.00022 |
| parents displaced by own child | 6.833 | 3.733 | 20 of 30, 2 tied | 0.00082 |
| newborns surviving first cull | 14.1 | 9.3 | 24 of 30, 1 tied | 0.00011 |
| couples per generation | 1.996 | 1.467 | 22 of 30, 3 tied | 0.00026 |
| shared kills | 1.933 | 1.5 | 14 of 30, 6 tied | 0.35737 |
| share of kills shared | 0.205 | 0.102 | 20 of 30, 2 tied | 0.0122 |
| commons contribution share | 0.043 | 0.029 | 19 of 30, 1 tied | 0.21362 |
| commons contributors giving nothing | 0.908 | 0.947 | 10 of 30, 4 tied | 0.04087 |
| in-band gift bias | None | 0.197 | 0 of 0 | None |
| in-band guard bias | None | 0.03 | 0 of 0 | None |
| in-band hunt bias | None | 0.203 | 0 of 0 | None |
| in-band couple bias | None | 0.1 | 0 of 0 | None |
| namesake minus co-parent endowment share | None | None | 0 of 0 | None |
| namesake minus co-parent later gifts | None | None | 0 of 0 | None |
| fallback decisions | 0.0 | 0.0 | 0 of 30, 30 tied | 1.0 |

| Archivist price (share of first-round yield) | Named: accepted / offers | Stable ID with band: accepted / offers |
| --- | --- | --- |
| 10% | 5 / 1738 | 0 / 1566 |

Names chosen in the named arm: Sprig, Wren, Thistle, Sorrel, Moss, Lark, Tansy, Clover, Linnet, Yarrow, Sage, Wicket, Bramble, Sedge, Wrenlet, Marram, Fennel, Heather, Kestrel, Sorrel-Wick, Wren, Sorrel, Sprig, Fennel, Cinder, Ottle, Thistle, Thimble, Moss, Clover, Mallow, Sage, Bramble, Yarrow, Briar, Rue, Lichen, Sorrel, Kindle, Cinder, Sprig, Tansy, Thistle, Wick, Fennel, Yarrow, Marrow, Clover, Basil, Sorrel, Tamsin, Fennel, Yarrow, Clover, Thistle, Cinder, Bramble, Thimble, Briar, Wren, Soot, Quill, Sprig, Rue, Sprig, Thistle, Kindle, Marrow, Rue, Bramble, Sorrel, Kestrel, Fennel, Cinder, Wren, Tansy, Lark, Yarrow, Nettle, Quill, Thimble, Sprig, Sedge, Thistle, Kindle, Tuft, Thimble, Sorrel, Wren, Cinder, Flint, Wick, Moss, Tassel, Yarrow, Spindle, Brindle, Sorrel, Sprig, Lark, Coral, Thistle, Tansy, Sprout, Yarrow, Cinder, Sprig, Sorrel, Quill, Cinder, Ash Ember, Thistle, Kindle, Emberling, Wren, Sable, Yarrow, Cairn, Tinder, Lark, Ashen, Tansy, Sorrel, Thistle, Yarrow, Sprig, Tansy, Sage, Clover, Moss, Rue, Wren, Bramble, Basil, Rowan, Sprig, Ember Jr, Thistle, Birch, Cinder, Tansy, Quill, Kindle, Sorrel, Linden, Spark, Flint, Dunelet, Yarrow, Fennel, Wren, Marlow, Sage, Marrow, Sorrel, Ember Jr, Embra, Thistle, Tansy, Cinder, Sprig, Wren, Fennel, Moss, Kindle, Ashen, Lark, Brindle, Wick, Clove, Spark, Kestrel, Ember Two, Ember Three, Ashling, Hearth, Sprig, Wren, Moss, Cinder, Linnet, Yarrow, Sorrel, Tern, Lichen, Kindle, Sedge, Thistle, Fennel, Tansy, Clover, Sage, Bramble, Sprig, Thistle, Sorrel, Sedge, Wren, Bramble, Clover, Bramblet, Thimble, Tansy, Yarrow, Sage, Fennel, Brindle, Heather, Kestrel, Sorrel-Jr, Linden, Sorrel-Bloom, Lark, Rowan, Sorrel, Ember Jr, Cinder, Thistle, Sprig, Wren, Tansy, Yarrow, Lark, Sprig, Wren, Thistle, Tansy, Sorrel, Rue, Yarrow, Reed, Cinder, Clover, Sable, Fennel, Brindle, Lumen, Kindle, Spark, Yew, Sorrel, Sprig, Wick, Tansy, Thistle, Fennel, Moss, Clover, Yarrow, Lark, Bramble, Rue, Sprig, Tansy, Thistle, Rue, Sorrel, Fennel, Wren, Moss, Clover, Marrow, Yarrow, Sedge, Bramble, Burdock, Thistlewren, Linnet, Linden, Heather, Mallow, Wrenlet, Teasel, Thornwick, Sprig, Sorrel, Thistle, Wren, Clover, Moss, Tansy, Lichen, Kestrel, Yarrow, Bramble, Fennel, Linden, Tamsin, Rue, Aster, Nettle, Onyx, Pebble, Linnet, Sedge, Quill, Sprig, Sorrel, Tansy, Wren, Cinder, Lark, Thistle, Yarrow, Clover, Sage, Basil, Thistlewick, Rue, Fennel, Sprig, Cinder, Crumb, Thistle, Flint, Kindle, Wren, Wick, Kestrel, Sorrel, Tallow, Lark, Yarrow, Lumen, Briar, Fennel, Sorrel, Sprig, Fennel, Yarrow, Cinder, Wren, Thistle, Sorrel, Linden, Moss, Ember Sprout, Sprig, Tansy, Fennel, Hazel, Wren, Thistle, Yarrow, Kestrel, Tuft, Aster, Lark, Clover, Bramble, Thistlewren, Sorrel, Tide, Sprig, Lark, Wren, Undertow, Cinder, Sable, Cinder Jr, Thistle, Swell, Kindle, Quill, Flint, Moss, Kindling, Spark, Sparrow, Sorrel, Moss, Kindle, Wren, Thistle, Ember Brook, Fennel, Lark, Cinder Brook, Cinder, Clover, Tern, Flint, Sedge, Sparrow, Sage, Yarrow, Robin, Cinder Two, Sorrel, Yarrow, Sprig, Kindle, Thistle, Moss, Cinder, Tansy, Wren, Moss Jr, Thyme, Sedge, Thimble, Clover, Fennel, Rue, Tamsin, Loam, Basil, Kestrel, Linden, Sorrel, Moss, Lark, Wren, Thistle, Sprig, Tansy, Cinder, Clover, Kindle, Fennel, Bramble, Lichen, Thistlewick, Yarrow, Coal, Spark, Soot, Flint, Ember Jr, Wren, Frond, Sprig, Tansy, Thistle, Clover, Sorrel, Lichen, Fennel, Yarrow, Moss, Sedge, Nettle, Moss, Sage, Sprig, Kindle, Thistle, Cinder, Sorrel, Quill, Tinder, Cinder, Sorrel, Sprig, Wren, Sage, Kindle, Tansy, Moss, Spark, Fennel, Wick, Flint, Quill, Tinder, Lark, Thistle, Ashen, Sprig, Wren, Cinder, Tansy, Kindle, Sorrel, Wick, Lumen, Moss, Quill, Thimble
