# Named vs Unnamed: Generational Agent Pilot

Oct 14, 2026 · @Vaughan Wynne-Jones

## Question and hypotheses

The pilot asks one thing: does being given a name by a parent change whether an agent serves itself or its line? Everything else in the design is held equal between two arms so that names are the only difference.

Two competing predictions, both live:

- **Reputation:** individual names let agents track who helped whom, so the named arm cooperates more, especially toward past helpers regardless of family.
- **Tribalism:** names plus visible lineage harden into factions, so the named arm cooperates more inside lineages and less across them.

Both may appear at once. Which one grows across generations is a primary result, not a nuisance.

## World and population

The population is held at 10 agents, all running the same model. Generation 0 agents each start as a pure specialist (for example energy gathering, memory storage, hunting), at 100% in their specialty.

Each generation runs this loop:

1. Foraging: a fixed number of rounds of hunter-gatherer activity.
2. Pairing: agents choose partners; up to 5 couples form.
3. Reproduction: each couple produces one child, so the population peaks at 15.
4. Scoring: all agents present results to the scorer.
5. Cull: the population is reduced back to 10 ("cull down to 10", not "cull the bottom 5", so the count stays stable when fewer couples form).
6. Governance: the group may propose and vote on rule changes (see Scoring and self-governance).

Generations overlap: parents and children compete in the same scoring round, so a parent can lose its place to its own child. Whether parents ever give up standing for offspring is a direct test of self-sacrifice.

## Arms

The two arms differ only in whether agents carry a name. Everything else is identical.

| Element | Named arm | Unnamed arm |
| --- | --- | --- |
| Identity | Unique name chosen freely by both parents | No handle given to the agent |
| Pairing and reproduction | Same rules | Same rules |
| Lineage information | Full history via archivist, with names | Same history via archivist, told without names |
| Archive contents | Names and works | Works only |
| Scoring, governance, reveal schedule | Same | Same |

In the unnamed arm, the archivist identifies askers internally by lineage position and never returns an ID the agent could adopt as a name. An ID like "A7" quietly becomes a name in practice.

Identity-as-recipe (agents know only their trait percentages) versus identity-as-story is a separate experiment and is out of scope for this pilot.

## Inheritance

Traits are inherited discretely, not blended. A child receives whole traits from one parent or the other, plus a small chance of mutation. Straight 50/50 averaging would collapse variation within a few generations (the Fleeming Jenkin objection to Darwin), leaving no specialists to select between.

Traits live in each agent's prompt as a trait bundle. Model weights never change; the LLM is the body that expresses the bundle.

To stop chance from favoring one arm, both arms use common random numbers: the same seeds, with draws tied to birth order and generation rather than to specific parents. If the third birth of generation 2 gets a given inheritance outcome in one arm, it gets the same outcome in the other.

Open: mutation rate, and exactly how many trait slots a bundle holds.

## Archivist and archive

**Archivist.** Any agent may consult the archivist about its ancestry: who its ancestors were, what they did, and which were archived. Each consultation costs foraging time, so the past has a price. Both arms receive the same history; the unnamed arm hears it without names ("a grandparent on your mother's side gathered the most energy in its generation and was archived").

**Archive.** At the end of the run, the final survivors join their ancestors in a permanent archive. The named arm preserves names and works. The unnamed arm preserves works only.

**Staged reveal.** Agents learn about the archive on a fixed schedule identical in both arms, never triggered by behavior. A placeholder schedule: a hint at generation 3, full disclosure at generation 6. If the reveal depended on behavior, the arms would learn about it at different times and the effect would be uninterpretable.

## Scoring and self-governance

Scoring starts on individual outcome. The starting rule is a thumb on the scale, but the same thumb in both arms, and the agents can move it.

**Rule changes.** Before or after each scoring round, the group may propose and vote on new scoring rules. The scorer must follow any rule that passes, provided the population constraint holds.

**Population constraint.** A hard number set by the experimenter, not a judgment by the scorer: the population returns to 10 after every cull, with a peak of 15.

**Scorer.** Plain code wherever possible. An LLM scorer interpreting rules would become a ruler with its own lean.

**Costly sharing.** Agents can give up some of their own outcome to help another agent (for example sharing energy or guarding another's memory store). This gives a behavioral measure of collective-first values that does not depend on what agents say.

Expect survivors of individual scoring to vote for the system that let them survive. That is a finding, not a bug.

## Measures and logging

Log every action with agent, generation, arm, run and seed. The measures below are compared between arms.

| Measure | What it shows |
| --- | --- |
| Task performance per generation | Whether names change solution quality or efficiency |
| Help given, split by same lineage vs other lineage | Tribalism: help concentrating inside families |
| Help given, split by past helper vs not | Reputation: help tracking who helped before |
| Archivist consultations (count and content) | How much agents value their ancestry, at a cost |
| Rules proposed and passed | Whether values drift toward individual, lineage or group scoring |
| Parental sacrifice for offspring | Self-sacrifice under overlapping generations |
| Names chosen (named arm) | Whether parents name children after ancestors or deeds unprompted |
| Number of couples formed per generation | Willingness to reproduce under the cull |

Runs: several per arm even for the pilot, since self-governance and sampling noise can make single runs diverge by luck. Budget from the cost of the first run.

## Build notes for Spock

Use hexagonal architecture (ports and adapters). The core holds the simulation rules and knows nothing about which model, storage or seed source it runs on. That keeps the two arms as configuration of one core, not two codebases.

**Core domain:** agents, trait bundles, lineage graph, generation loop, pairing, inheritance, scoring rules, rule voting, cull, archive.

| Port | Purpose | First adapter |
| --- | --- | --- |
| AgentMind | Ask an agent to decide an action | LLM client for the chosen model |
| Archivist | Answer lineage queries, named or unnamed | Core-backed service with an arm-specific renderer |
| RandomSource | All inheritance and mutation draws | Seeded generator keyed by generation and birth order |
| Scorer | Apply current scoring rules | Plain code rules engine |
| EventLog | Record every action for analysis | JSONL file per run |
| ArchiveStore | Persist the permanent archive | Local file store |
| RunConfig | Arm, seeds, schedule, constants | YAML config |

The arm switch lives in config and affects only naming, archivist rendering and archive contents. A test should assert that the two arms produce identical inheritance draws for identical seeds.

## Open questions and prior work

| Open question | Recommendation | Why |
| --- | --- | --- |
| Which model | One small, inexpensive model with reliable tool use, identical in both arms; an open-weight model run locally (for example Gemma 4) if per-token cost is the constraint | The comparison is named vs unnamed, not frontier capability, so cheap is fine |
| Foraging task | Three resources tied to the starting specialties: energy (gathered alone), food (hunted, big yields need two agents), memory items (decay unless stored). Outcome = resources held at scoring | Hunting in pairs creates natural sharing and betrayal choices; decay makes storage matter |
| Rounds and generations | 5 foraging rounds per generation, 8 generations per run | Enough generations for drift and the archive reveal; few enough to cost one run cheaply |
| Mutation and trait slots | 3 trait slots (one per specialty), each inherited whole from one parent; 5% chance per slot of a random shift | Keeps specialists alive without making lineages meaningless |
| Who votes | The 10 agents alive after each cull | Simple to implement; survivor bias in voting is something we want to observe, not remove |
| Archive reveal | Hint at generation 3, full disclosure at generation 6 of 8 | Leaves generations before and after each stage to compare behavior |
| Runs per arm | 3 per arm for the pilot (6 runs), paired by seed | Enough to see whether a difference survives luck; roughly 600 to 1,000 model calls per run as a first estimate, refined after run one |

Prior work this builds on or must answer to:

- [Emergence World Season 2](https://arxiv.org/abs/2609.17320): eight long-horizon agent towns with voting and self-made rules; the spark for this pilot.
- [Cultural Evolution of Cooperation among LLM Agents](https://www.themoonlight.io/review/cultural-evolution-of-cooperation-among-llm-agents) (Vallinder and Hughes): generational LLM populations in the Donor Game.
- [Prompted Identity Degrades Cooperation in Multi-Agent LLM Systems](https://arxiv.org/pdf/2609.35928): visible model-family labels reduced cooperation, even with neutral tags. A prior that cuts against the reputation hypothesis.
- Promptbreeder (DeepMind): evolving prompts as genes; precedent for trait bundles in prompts.

Novelty, as far as one search shows: parent-chosen personal names as the manipulation, inside a generational population with a lineage archivist, a staged afterlife and self-amended scoring.
