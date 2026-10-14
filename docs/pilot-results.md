# Pilot results, 2026-10-14

**The batch:** 3 seeds × 2 arms, using `configs/pilot.yaml` at commit `573f00d`. All agents ran
on Claude Haiku 5.5 at effort `low`. The pilot made 3,936 calls and cost **$1.21**, against an
estimate of $1.35. It took about 22 minutes with two runs at a time. There were no errors and no
fallback decisions. The raw data is in [`data/pilot-20261014/`](../data/pilot-20261014/).

**Read this with care.** There are only three runs per arm. Even when every named run lands
above every unnamed run, there is a 1-in-20 chance of that split with no real effect, and I
looked at more than a dozen measures. Treat everything below as leads for a properly sized
study, not as findings.

## Per run

| Run | Pair hunts | Gathered per forager per generation | Gifts (all) | Gifts while still costly | Parents displaced by own child | Final `kin_weight` | Rules passed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| named-s1 | 51 | 15.2 | 3 | 3 | 6 | 0.0 | 2 |
| named-s2 | 14 | 14.7 | 5 | 5 | 8 | 0.3 | 5 |
| named-s3 | 13 | 14.7 | 68 | 68 | 9 | 0.5 | 6 |
| unnamed-s1 | 9 | 13.4 | 479 | 0 | 3 | 0.6 | 7 |
| unnamed-s2 | 9 | 14.2 | 45 | 45 | 5 | 0.6 | 11 |
| unnamed-s3 | 3 | 14.0 | 65 | 65 | 2 | 0.6 | 6 |

## Where the arms split cleanly (every named run on one side of every unnamed run)

1. **Named agents hunted together more:** 51, 14 and 13 pair hunts, against 9, 9 and 3. Names
   make it easy to call a partner ("Brook, let's hunt big game together this round"). Pair hunts
   yield more, which probably explains why named runs also gathered slightly more per forager.
   This fits the reputation and coordination prediction for how names help.
2. **Named parents lost their place to their own child more often:** 6, 8 and 9 times, against
   3, 5 and 2. The average share of holdings given at birth does *not* split cleanly (named 0.52,
   0.47, 0.77; unnamed 0.68, 0.52, 0.30). So this is about which parents give enough to be
   displaced, not average generosity. It needs a closer look.
3. **Unnamed survivors voted more weight to kin:** all three unnamed runs ended with
   `kin_weight` at 0.6, while named runs ended at 0, 0.3 and 0.5. Unnamed runs also passed more
   rule changes. This runs against the tribalism prediction that names harden into factions.

## The same in both arms

- **Both arms moved away from pure individual scoring.** Every run passed `gift_credit`, and 5
  of 6 added `kin_weight`. The survivors of individual scoring did not simply vote to keep it.
- **Gifts show no arm difference once free gifts are removed.** The raw average (unnamed 196,
  named 25) comes from one run. Unnamed-s1 gave 479 units, all after it had voted `gift_credit`
  to 1, which made giving free. Counting only gifts that still cost the giver something gives
  named 3, 5 and 68, and unnamed 0, 45 and 65.
- **There is no sign of reputation-based reciprocity.** In 5 of 6 runs, at most 1.5% of help
  went to an agent that had helped the giver before.
- **Kills are kept.** Of 73 successful pair hunts, the hunter who landed the kill shared the
  food with its partner twice.

## Names and speech

- **Named agents speak about themselves by name.** About 70% of their messages begin with their
  own name ("Sorrel gathers energy this round…"). Unnamed agents never invented names for each
  other.
- **Names come from a small, recurring set.** Sorrel, Wren, Thistle and Tansy appear in all
  three named runs.
- **Few names honour earlier agents:** 3 of 51. An earlier test run, under the old gift rule,
  produced whole dynasties: Ember Two, Ember Three, Ember Four, Cedar Two through Cedar Five.

## Measures that produced no data

| Measure | Result | Likely reason | Possible fix |
| --- | --- | --- | --- |
| Archivist consultations | 0 in all 6 runs | Consulting costs half a round's yield, and nobody paid that. | Make it cheaper, or make the first consultation free. |
| Guarding another's memory | 0 in all 6 runs | Memory specialists store every round, so their stores never need a guard. | Make storing and collecting separate actions. |

## Next steps to consider

1. Fix the two mechanics that produced no data, so the next batch measures what the design asks.
2. Decide the shared-history question in the README (choice 1).
3. Scale up. Each extra seed (one run per arm) costs about $0.40. Ten seeds per arm, about $4,
   would test the three clean splits above properly.
