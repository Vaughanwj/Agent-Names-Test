# What the pilot will cost

**About $1.35 for the full pilot** (3 seeds × 2 arms, 8 generations of 5 rounds) on Claude Haiku
5.5 at effort `low`. The actual pilot came to **$1.21**. Budget **$2–3** to be safe. Running it in Docker on your own machine adds
nothing: all of the cost is Claude API usage. Expect about 40 minutes run one after another, or
about 15 minutes with `--parallel 3`.

## Where the number comes from

The estimate is based on one complete real run (named arm, seed 1), run in Docker on 2026-10-14.
The design doc says to budget from the cost of the first run.

| | Calls | Uncached input | Cache read | Cache write | Output | Cost | Time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Full run (named, seed 1) | 664 | 956K tokens | 997K tokens | 7K tokens | 229K tokens | **$0.221** | 6.7 min |
| Smoke test (2 gen × 2 rounds, both arms) | 172 | | | | | $0.050 | ~1 min |

- **The two arms cost the same, within 2%.** In the smoke test the named arm cost $0.0246 and
  the unnamed arm $0.0242. Unnamed prompts are about 4% shorter.
- **Pilot total:** 6 runs × about $0.22 = **about $1.33**.
- **Cost rises each generation**, from $0.023 in generation 1 to $0.033 in generation 8, because
  prompts grow as agents build up shared history.
- **Where the money goes:** output tokens (including the model's own thinking) are about 52% of
  the cost, uncached input about 43%, and the cache about 5%. The shared system prompt reaches a
  cache hit rate of about 98%.
- **Prices:** Haiku 5.5 costs $0.10 per million input tokens and $0.50 per million output tokens
  for prompts under 100K tokens. Cache reads are $0.01 and cache writes $0.125. This pilot's
  prompts are about 3K tokens. Prices were checked against
  platform.claude.com/docs/en/about-claude/pricing on 2026-10-14.

That full run used an earlier version of the gift-credit rule. Agents found a way to make giving
profitable, which has since been fixed. Gifts surged in its later generations, so the corrected
rules should cost the same or slightly less.

## What would change the number

| Change | Estimated pilot cost |
| --- | --- |
| As configured (Haiku 5.5, effort `low`) | ~$1.35 |
| Haiku 5.5 at effort `medium` (more thinking per decision) | ~$2–3 |
| Claude Sonnet 5.5, same token counts | ~$26 |
| Claude Opus 5.5, same token counts | ~$52 |
| More seeds | ~$0.45 per extra seed (one run per arm) |

The Sonnet and Opus rows reuse Haiku's token counts. Treat them as rough: other models think
for different lengths and count tokens slightly differently.

- **Batch API:** not used. It halves the price, but every decision depends on the round before
  it, so each round would wait up to 24 hours.
- **A local open-weight model:** no adapter is built. A model like Gemma would remove the API
  cost but needs a GPU. At $1.35 for the whole pilot, it isn't worth it yet.

## Safety rails

- `mind.budget_usd` in `configs/pilot.yaml` stops any single run that spends more than $2.
- `cost.json` in each batch folder records the actual spend.
- `agent-names estimate` re-estimates cost from any short real run plus a free dry run. On its
  own it came in about 35% low, because the scripted stand-in writes shorter messages than
  Claude does. Prefer a measured full run when one exists.

## Spent while building (2026-10-14)

| Run | Cost |
| --- | --- |
| First local smoke test | $0.062 |
| Docker smoke test | $0.049 |
| Full-length budgeting run | $0.221 |
| Final Docker smoke test | $0.051 |
| The pilot itself (6 runs, 3,936 calls) | $1.211 |
| Mechanics checks (three short runs) | $0.366 |
| Second pilot (6 runs, 4,274 calls) | $1.179 |
| Scale-up (20 runs, 8,606 calls) | $3.878 |
| **Total** | **$7.02** |
