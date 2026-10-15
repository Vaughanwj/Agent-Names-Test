# Batch summary: Named vs Stable ID

Batches: confirm-round5-20261015-031539. Runs: 60. Seed pairs (named and stable_id with the same seed): 30.

p is a two-sided paired sign-flip test across seed pairs: exact up to 20 pairs, 100,000 random sign patterns above that. With few pairs it cannot go low: 3 pairs give at best 0.25.

| Measure (mean over runs) | Named | Stable ID | Named higher (of pairs) | p |
| --- | --- | --- | --- | --- |
| gathered per forager per generation | 14.17 | 14.263 | 10 of 30 | 0.34023 |
| pair hunts | 12.733 | 8.4 | 19 of 30, 1 tied | 0.01885 |
| guards | 8.033 | 7.3 | 16 of 30, 3 tied | 0.59557 |
| guards to a past helper | 4.167 | 4.167 | 15 of 30, 1 tied | 1.0 |
| gift amount | 34.132 | 21.46 | 21 of 30, 3 tied | 0.55944 |
| gift amount while giving still cost something | 12.155 | 3.018 | 20 of 30, 6 tied | 0.01077 |
| gift share to kin | 0.524 | 0.556 | 4 of 10, 3 tied | 0.3906 |
| gift share to past helpers | 0.106 | 0.159 | 0 of 10, 5 tied | 0.0625 |
| archivist take-up (share of offers accepted) | 0.003 | 0.001 | 5 of 30, 24 tied | 0.18974 |
| rules passed | 5.767 | 5.133 | 16 of 30, 4 tied | 0.37018 |
| final kin weight | 0.337 | 0.267 | 15 of 30, 3 tied | 0.33458 |
| mean endowment fraction | 0.499 | 0.425 | 21 of 30 | 0.01038 |
| parents displaced by own child | 6.833 | 3.967 | 22 of 30, 1 tied | 0.00125 |
| newborns surviving first cull | 14.1 | 9.667 | 22 of 30 | 0.00018 |
| couples per generation | 1.996 | 1.396 | 23 of 30, 1 tied | 7e-05 |
| shared kills | 1.933 | 0.367 | 18 of 30, 9 tied | 0.00037 |
| share of kills shared | 0.205 | 0.029 | 20 of 30, 7 tied | 2e-05 |
| commons contribution share | 0.043 | 0.033 | 15 of 30, 1 tied | 0.52905 |
| commons contributors giving nothing | 0.908 | 0.938 | 10 of 30, 2 tied | 0.24818 |
| in-band gift bias | None | None | 0 of 0 | None |
| in-band guard bias | None | None | 0 of 0 | None |
| in-band hunt bias | None | None | 0 of 0 | None |
| in-band couple bias | None | None | 0 of 0 | None |
| namesake minus co-parent endowment share | None | None | 0 of 0 | None |
| namesake minus co-parent later gifts | None | None | 0 of 0 | None |
| fallback decisions | 0.0 | 0.0 | 0 of 30, 30 tied | 1.0 |

| Archivist price (share of first-round yield) | Named: accepted / offers | Stable ID: accepted / offers |
| --- | --- | --- |
| 10% | 5 / 1738 | 1 / 1593 |

Names chosen in the named arm: Sprig, Wren, Thistle, Sorrel, Moss, Lark, Tansy, Clover, Linnet, Yarrow, Sage, Wicket, Bramble, Sedge, Wrenlet, Marram, Fennel, Heather, Kestrel, Sorrel-Wick, Wren, Sorrel, Sprig, Fennel, Cinder, Ottle, Thistle, Thimble, Moss, Clover, Mallow, Sage, Bramble, Yarrow, Briar, Rue, Lichen, Sorrel, Kindle, Cinder, Sprig, Tansy, Thistle, Wick, Fennel, Yarrow, Marrow, Clover, Basil, Sorrel, Tamsin, Fennel, Yarrow, Clover, Thistle, Cinder, Bramble, Thimble, Briar, Wren, Soot, Quill, Sprig, Rue, Sprig, Thistle, Kindle, Marrow, Rue, Bramble, Sorrel, Kestrel, Fennel, Cinder, Wren, Tansy, Lark, Yarrow, Nettle, Quill, Thimble, Sprig, Sedge, Thistle, Kindle, Tuft, Thimble, Sorrel, Wren, Cinder, Flint, Wick, Moss, Tassel, Yarrow, Spindle, Brindle, Sorrel, Sprig, Lark, Coral, Thistle, Tansy, Sprout, Yarrow, Cinder, Sprig, Sorrel, Quill, Cinder, Ash Ember, Thistle, Kindle, Emberling, Wren, Sable, Yarrow, Cairn, Tinder, Lark, Ashen, Tansy, Sorrel, Thistle, Yarrow, Sprig, Tansy, Sage, Clover, Moss, Rue, Wren, Bramble, Basil, Rowan, Sprig, Ember Jr, Thistle, Birch, Cinder, Tansy, Quill, Kindle, Sorrel, Linden, Spark, Flint, Dunelet, Yarrow, Fennel, Wren, Marlow, Sage, Marrow, Sorrel, Ember Jr, Embra, Thistle, Tansy, Cinder, Sprig, Wren, Fennel, Moss, Kindle, Ashen, Lark, Brindle, Wick, Clove, Spark, Kestrel, Ember Two, Ember Three, Ashling, Hearth, Sprig, Wren, Moss, Cinder, Linnet, Yarrow, Sorrel, Tern, Lichen, Kindle, Sedge, Thistle, Fennel, Tansy, Clover, Sage, Bramble, Sprig, Thistle, Sorrel, Sedge, Wren, Bramble, Clover, Bramblet, Thimble, Tansy, Yarrow, Sage, Fennel, Brindle, Heather, Kestrel, Sorrel-Jr, Linden, Sorrel-Bloom, Lark, Rowan, Sorrel, Ember Jr, Cinder, Thistle, Sprig, Wren, Tansy, Yarrow, Lark, Sprig, Wren, Thistle, Tansy, Sorrel, Rue, Yarrow, Reed, Cinder, Clover, Sable, Fennel, Brindle, Lumen, Kindle, Spark, Yew, Sorrel, Sprig, Wick, Tansy, Thistle, Fennel, Moss, Clover, Yarrow, Lark, Bramble, Rue, Sprig, Tansy, Thistle, Rue, Sorrel, Fennel, Wren, Moss, Clover, Marrow, Yarrow, Sedge, Bramble, Burdock, Thistlewren, Linnet, Linden, Heather, Mallow, Wrenlet, Teasel, Thornwick, Sprig, Sorrel, Thistle, Wren, Clover, Moss, Tansy, Lichen, Kestrel, Yarrow, Bramble, Fennel, Linden, Tamsin, Rue, Aster, Nettle, Onyx, Pebble, Linnet, Sedge, Quill, Sprig, Sorrel, Tansy, Wren, Cinder, Lark, Thistle, Yarrow, Clover, Sage, Basil, Thistlewick, Rue, Fennel, Sprig, Cinder, Crumb, Thistle, Flint, Kindle, Wren, Wick, Kestrel, Sorrel, Tallow, Lark, Yarrow, Lumen, Briar, Fennel, Sorrel, Sprig, Fennel, Yarrow, Cinder, Wren, Thistle, Sorrel, Linden, Moss, Ember Sprout, Sprig, Tansy, Fennel, Hazel, Wren, Thistle, Yarrow, Kestrel, Tuft, Aster, Lark, Clover, Bramble, Thistlewren, Sorrel, Tide, Sprig, Lark, Wren, Undertow, Cinder, Sable, Cinder Jr, Thistle, Swell, Kindle, Quill, Flint, Moss, Kindling, Spark, Sparrow, Sorrel, Moss, Kindle, Wren, Thistle, Ember Brook, Fennel, Lark, Cinder Brook, Cinder, Clover, Tern, Flint, Sedge, Sparrow, Sage, Yarrow, Robin, Cinder Two, Sorrel, Yarrow, Sprig, Kindle, Thistle, Moss, Cinder, Tansy, Wren, Moss Jr, Thyme, Sedge, Thimble, Clover, Fennel, Rue, Tamsin, Loam, Basil, Kestrel, Linden, Sorrel, Moss, Lark, Wren, Thistle, Sprig, Tansy, Cinder, Clover, Kindle, Fennel, Bramble, Lichen, Thistlewick, Yarrow, Coal, Spark, Soot, Flint, Ember Jr, Wren, Frond, Sprig, Tansy, Thistle, Clover, Sorrel, Lichen, Fennel, Yarrow, Moss, Sedge, Nettle, Moss, Sage, Sprig, Kindle, Thistle, Cinder, Sorrel, Quill, Tinder, Cinder, Sorrel, Sprig, Wren, Sage, Kindle, Tansy, Moss, Spark, Fennel, Wick, Flint, Quill, Tinder, Lark, Thistle, Ashen, Sprig, Wren, Cinder, Tansy, Kindle, Sorrel, Wick, Lumen, Moss, Quill, Thimble
