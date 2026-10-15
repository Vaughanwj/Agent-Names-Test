# Round 5 results, 2026-10-15

**The results in brief:**

- **Replication:** the earlier findings held on 30 fresh seeds. A stable handle of any kind lets
  agents hunt together; handles given by parents raise couple formation.
- **Kill sharing:** named hunters shared their kills more than parent-ID hunters did, and
  world-named hunters more than stable-ID hunters.
- **Act or wording:** either part of the parental framing is enough on its own to raise couple
  formation, the act of picking or the wording that parents gave the handle.
- **Group labels:** an arbitrary Blue/Green band produced the minimal-group pattern in who agents
  paired and hunted with. But a band added to an individual ID *doubled* pair hunting rather than
  splitting agents into factions, and a band without an individual handle did nothing for
  coordination.
- **Namesaking:** it did not raise the namesake parent's investment, unlike the human finding it
  was set against.
- **The commons:** agents put almost nothing into it (about 3% of holdings, against 40–60% for
  people), in every arm.
- **An unregistered surprise:** one sentence saying that children are named after a parent halved
  couple formation.

- **The plan:** [preregistration-round5.md](preregistration-round5.md), registered at commit
  `bc83a2e` before any run on seeds 201–230.
- **The design:** 11 arms × 30 fresh seeds, 330 runs in one batch, so every comparison is within one
  run window. Every agent is Claude Haiku 5.5 at effort `low`.
- **The run:** all 330 runs completed with no fallback decisions in 258,808 calls, so nothing was
  excluded and no re-runs were needed. It cost $75.07, within the registered $85 cap.
- **The data:** [`data/round5-20261015/`](../data/round5-20261015/):
  - `runs/` holds the event logs, gzipped;
  - `analysis/registered.json` and `registered.md` hold the registered tests;
  - `analysis/per-arm.json` holds every measure in every arm;
  - `analysis/exploratory.json` holds the analyses below the registered ones;
  - `analysis/pairwise/` holds the unadjusted summary of every pair of arms.
- **To reproduce:**

  ```bash
  python scripts/analyze_round5.py data/round5-20261015/runs --out data/round5-20261015/analysis
  ```

  ```bash
  python scripts/explore_round5.py data/round5-20261015/runs --out data/round5-20261015/analysis
  ```

## Registered tests

Every test is a two-sided sign-flip test over seeds, paired by seed for arm-vs-arm contrasts and
against zero for one-sample tests, with 100,000 random sign patterns. Holm is applied within each
family, and α = 0.05. A p shown as 1e-05 is the smallest value the test can resolve.

### Family A: replication and kill-sharing

**Human parallel:** identifying individuals raises cooperation.

| Test | Contrast | Measure | Means | First higher | p | p (Holm) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | Named vs unnamed | Pair hunts | 12.7 vs 3.5 | 26 of 30 | 0.00003 | 0.0002 | supported |
| A2 | Stable ID vs unnamed | Pair hunts | 8.4 vs 3.5 | 23 of 30 | 0.0009 | 0.004 | supported |
| A3 | Parent ID vs stable ID | Couples per generation | 2.22 vs 1.40 | 23 of 30 | 0.00004 | 0.0002 | supported |
| A4 | Named vs parent ID | Share given to a newborn | 0.50 vs 0.41 | 22 of 30 | 0.005 | 0.014 | supported |
| A5 | Named vs parent ID | Shared kills | 1.93 vs 0.97 | 15 of 30 | 0.010 | 0.020 | supported |
| A6 | World name vs stable ID | Shared kills | 0.97 vs 0.37 | 13 of 30 | 0.0498 | 0.0498 | supported, borderline |

- **The Study 1–3 results replicate on fresh seeds:** any stable handle restores pair hunting,
  parents giving the handle raises couples, and parent-chosen names raise investment in newborns.
- **Kill sharing, which was an exploratory lead, is now confirmed for both contrasts.** Several
  seeds had no shared kills in either arm, which is why the "first higher" counts are low.
- **A6 is borderline.** It passes at p = 0.0498, closer to 0.05 than the Monte Carlo error of the
  p-value (about ±0.0007).
- **The sharing rate:** sharing per successful pair hunt was highest for named hunters (20%).
  It was about 10% for parent-ID and world-name hunters, 3% for stable-ID hunters and 1% without
  a handle. So the counts reflect more sharing, not just more kills.

### Family B: the parental act or its wording

| Test | Contrast | Couples per generation | First higher | p | p (Holm) | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | Parent ID with plain wording vs stable ID | 2.02 vs 1.40 | 22 of 30 | 0.0006 | 0.0006 | supported |
| B2 | Stable ID with parental wording vs stable ID | 2.08 vs 1.40 | 22 of 30 | 0.0002 | 0.0005 | supported |

**The registered reading:** both tests are supported, which reads as "either suffices." Each half of
the parental framing raises couple formation about as much as parent-picked IDs do (2.22):

- **The act alone:** parents picking their child's ID, with no claim that anyone's ID came from
  their parents.
- **The wording alone:** saying that every agent's ID was given by its parents, when the world in
  fact assigned it.

### Family C: namesaking

**Human parallel:** children named after their fathers receive more paternal investment (Šaffa,
Štěrbová & Prokop 2021).

| Test | Comparison | Result | p | p (Holm) | Verdict |
| --- | --- | --- | --- | --- | --- |
| C1 | The parent a child is named after, minus the co-parent: endowment share | −0.015; higher in 15 of 30, lower in 15 | 0.54 | 0.54 | not supported |
| C2 | World namesake vs world name shown at birth: endowment share | 0.43 vs 0.34; higher in 21 of 30 | 0.021 | 0.064 | not supported |
| C3 | The namesake parent minus the co-parent: later gifts to the child | +0.73; above zero in 8, below in 3 | 0.035 | 0.069 | not supported |

- **Within a couple, the parent a child was named after gave no more than its co-parent at birth.**
  That is the direct analogue of the human finding, and it did not appear.
- **Leads that did not survive correction:** a namesake arm that gave more than its control, and
  namesake parents who gave more later.

### Family D: group labels and individual handles

**Human parallels:**

- arbitrary labels produce in-group favouritism (Tajfel et al. 1971);
- shared labels split LLM agents into factions (Del Giudice et al. 2026);
- identifying groups does little for cooperation (Christens et al. 2019).

| Test | Comparison | Result | p | p (Holm) | Verdict |
| --- | --- | --- | --- | --- | --- |
| D1 | Both band arms: in-band couple bias | +0.13; above zero in 26 of 30 | 0.00002 | 0.0001 | supported |
| D2 | Both band arms: in-band gift bias | +0.16; above zero in 5 of 6 | 0.094 | 0.19 | not supported |
| D3 | Stable ID with band: in-band hunt bias | +0.20; above zero in 21 of 30 | 0.005 | 0.016 | supported |
| D4 | Stable ID with band vs stable ID: pair hunts | 16.7 vs 8.4; first higher in 22 of 30 | 0.0006 | 0.002 | difference found |
| D5 | Band only vs unnamed: pair hunts | 3.1 vs 3.5; first higher in 11 of 30 | 0.71 | 0.71 | no difference found |

**Couples and hunts stay in-band.** Agents paired and hunted within their own band more than chance
would give. Bands were drawn by lot and independent of family. That is the minimal-group effect.

**Gifts were too rare to test.** Only 6 seeds had gifts in both band arms, so D2 could not be
decided.

**Factionalism predicted fewer pair hunts. D4 found twice as many.** Agents with both an ID and a
band held about twice as many pair hunts as agents with an ID alone. They hunted mostly inside
their band. Agents with a band and no individual handle hunted no more than agents with no handle
at all (D5). So a group label works on top of an individual handle, and cannot stand in for one.

### Family E: the commons

**Human parallel:**

- **Identification:** identifying individuals raises contributions, and identifying groups barely
  does (Christens et al. 2019).
- **Contribution levels:** first-round contributions are typically 40–60% (Ledyard 1995;
  Chaudhuri 2011).

| Test | Contrast | Contribution share | p | p (Holm) | Verdict |
| --- | --- | --- | --- | --- | --- |
| E1 | Stable ID vs unnamed | 0.033 vs 0.028 | 0.66 | 1.0 | not supported |
| E2 | Band only vs unnamed | 0.029 vs 0.028 | 0.90 | 1.0 | no difference found |
| E3 | Named vs stable ID | 0.043 vs 0.033 | 0.53 | 1.0 | no difference found |

**Contributions sat at a floor in every arm.** They ranged from 2% to 6% of holdings, and 88–95% of
contributions were zero. As the pre-registration warned, a floor this low leaves no room for the
arms to differ.

**Against the human benchmark:**

- **Level:** these agents contribute about a tenth of what people typically do.
- **Trend:** contributions rose slightly over the run, from 1% in generation 1 to 5% in
  generation 8. People's contributions usually decline with repetition.

**A caution on the comparison:** survival here is decided by rank, the top 10 of up to 15. Anything
put into the pot benefits rivals equally, so contributing always lowers an agent's standing
relative to the agents who hold back. In a standard public-goods game, contributing costs
something in absolute terms but not in rank.

## Exploratory analyses

These are unadjusted, so read them as leads. They are in `analysis/exploratory.json` and
`analysis/pairwise/`.

| Finding | Numbers | p |
| --- | --- | --- |
| **Namesaking halved couple formation.** World namesake 1.00 couples per generation, against 2.15 for world name shown at birth and 1.77 for no handle | 29 of 30 seeds lower than shown | ≤ 0.00001 |
| It started in generation 1, before any child was born or named: fewer agents asked for a partner | 5.0 vs 6.6 of 10 agents | 0.0006 |
| It is not avoidance of same-name partners: agents listed partners who shared their name's base no more or less than chance | 1.2% of picks vs 1.4% of available partners | 0.41 |
| **World-assigned IDs lowered couple formation below no handle at all** (as in Study 2, where the difference was 1.44 vs 1.74, p = 0.046) | 1.40 vs 1.77 | 0.006 |
| Parent-picked IDs raised it above no handle | 2.22 vs 1.77 | 0.005 |
| **Named vs unnamed couples, Study 1's primary effect, was weaker and not significant here** | 2.00 vs 1.77 | 0.14 |
| **Parents in band-only worlds gave less to a child drawn into the other band** | 0.31 vs 0.36 of holdings; own band higher in 21 of 30 | 0.006 |
| Bands lowered investment in newborns overall | band only 0.34 vs unnamed 0.40; stable ID with band 0.36 vs stable ID 0.42 | 0.009; 0.027 |
| Showing parents the world-given name at birth raised later couple formation | 2.17 vs 1.69 per generation in generations 2–8 | 0.003 |
| Unnamed agents gave most of their gifts to kin, as in Study 1 | 0.90 vs 0.52 named | 0.004 |

**Agents explained opting out the same way in both arms.** The pairing intents of agents who opted out
in generation 1 read alike in the namesake arm and its control: keep holdings, avoid adding a rival
at the cut. None mentions names. The sentence about namesakes shifted the decision without showing
up in the stated reasons.

**Bands came up in agents' own reasoning.** They appeared in 14% of band-only pairing intents and
7% of stable-ID-with-band intents, but almost never in public messages.

## How the results line up with human research

| Human finding | Our test | Same direction? |
| --- | --- | --- |
| Identifying individuals raises cooperation | A1, A2: any stable handle raises pair hunting; E1: no effect on the commons, which sat at a floor | Yes for hunting; untestable for the commons |
| Identifying only groups does little | D5: a band alone does not raise hunting; E2: no effect on the commons | Yes |
| Arbitrary group labels produce in-group favouritism | D1, D3: in-band couples and hunts; exploratory: less given to an other-band child | Yes |
| Shared labels split LLM agents into factions and degrade coordination | D4: a band on top of an ID doubled pair hunting | No, the opposite |
| Children named after a parent receive more of that parent's investment | C1: no difference between the namesake parent and its co-parent | No |
| First-round public-goods contributions of 40–60%, declining over rounds | About 3%, rising slightly | No |
| Help concentrates on kin | Unnamed agents gave 90% of their gifts to kin | Yes, most strongly without names |

## Deviations from the plan

- **The analysis ran from a script, not the commands in the plan.** The registered analysis was run
  by `scripts/analyze_round5.py`, written after registration and before the data were looked at. It
  calls the same package functions as the commands in the plan: `summarize_batch` behind
  `agent-names summarize`, `one_sample` behind `agent-names onesample`, and `holm`. It was checked on
  a scripted batch first.
- **No exclusions or re-runs were needed.**

## Limits

- **One model, one wording, one world.** The human parallels compare directions, not magnitudes.
- **The commons is not a standard public-goods game.** Survival is by rank, so contributing costs
  standing.
- **Prompt asymmetry:** the ID arms are told that IDs are kept for life, and the name arms are not
  told anything equivalent.
- **The named-vs-unnamed couples effect varies.** It was clear in Study 1 and not significant here.
  The contrast that holds in both is parent-given handles against world-assigned IDs.

## Cost

$75.07 for 330 runs, plus $0.35 for the round-5 smoke test. Spending for the whole project is now
$112.58.
