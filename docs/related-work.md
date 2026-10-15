# Related work (literature check, 2026-10-14)

This is a web search, not a systematic review. Several sources are preprints, and for some only
summaries were read. Before citing anything, read the full text of the starred items.

## The closest work

| Work | What it found | How it relates to this project |
| --- | --- | --- |
| ★ [Prompted Identity Degrades Cooperation in Multi-Agent LLM Systems](https://arxiv.org/abs/2609.35928) (Del Giudice et al.) | Showing agents a model-family label, or even an arbitrary one, splits them into factions. Coordination gets slower and less successful, and withholding the labels removes the effect. | Their labels mark **group membership**; ours are **unique individual handles**. Group labels hurt coordination, individual handles help it, and we saw no tribalism. This distinction appears new. |
| [Why LLM Agents Favor Their Group: Stakes, Observed Norms, and Reputation](https://arxiv.org/html/2610.11008) | A label alone produces little in-group favouritism when giving is costly. Shared interaction history matters more. | Consistent with our design: every arm sees the same history, which isolates the label. |
| [Cultural Evolution of Cooperation among LLM Agents](https://arxiv.org/abs/2412.10270) (Vallinder & Hughes, AAMAS 2025) | Generational populations playing the Donor Game. Claude-based societies develop cooperation; others don't. | Generational, but no names, no reproduction, no parenting. |
| ★ [Why Are We Moral? An LLM-based Agent Simulation Approach to Study Moral Evolution](https://arxiv.org/pdf/2509.17703) (ACL 2026) | Agents reproduce, and "kin-focused" agents prioritise offspring. | Closest on mechanics. Parenting comes from prompted moral types; names are not varied. |
| ★ [The Yerkes-Dodson Curve for AI Agents](https://arxiv.org/pdf/2603.07360) | Reproduction built on parental investment theory, with offspring inheriting averaged, mutated attributes. | Reproduction and mate choice, but no naming or identity manipulation. |
| [Behavioral Inheritance and Evolution in LLM-Controlled Agent Populations](https://zenodo.org/records/22909929) | Natural-language "genes" recombined across generations. | An alternative inheritance design: blending text, where ours inherits whole traits. |
| [Dissociative Identity: Language Model Agents Lack Grounding for Reputation Mechanisms](https://arxiv.org/html/2605.30169v3) | Reputation systems rely on persistent identities, which LLM agents often lack. | Fits our finding that a stable handle is what makes coordination possible. |
| [Trust, Lies, and Long Memories: Reputation in Multi-Round Avalon](https://arxiv.org/pdf/2604.20582) | Stable reputations form when agents remember earlier games. | Background on how reputation forms. |
| [Simulating Cooperative Prosocial Behavior with Multi-Agent LLMs](https://arxiv.org/pdf/2502.12504) | Calling a game by a different name primes LLM agents in the same direction as humans. | Names as primes. Agent names there are scaffolding, not a variable. |
| Emergence World 2 ([press summary](https://aigovernancelead.substack.com/p/emergence-world-experiment-responsible-ai-agent-governance-anarchy), [platform preprint](https://huggingface.co/papers/2606.08367)) | Agent towns with voting and self-amended rules. | The design doc's starting point. No naming manipulation. |

## Human research with parallels

- **Identifiability and cooperation:** identifying individuals raises cooperation; identifying groups
  does little ([Christens, Dannenberg & Sachs](https://kobra.uni-kassel.de/items/d814313f-f357-4818-9d9c-9ff5dfd4d163/full)).
  Names alone had no direct effect in [Sampaio et al. 2023](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10439960/).
- **Naming and parental investment:** children named after their fathers receive more paternal
  investment ([Šaffa, Štěrbová & Prokop 2021, *Human Nature*](https://philpapers.org/rec/AFFPII)).
  Namesaking has been described as advertising a kin link ([Obasi 2016, *Names*](https://ans-names.pitt.edu/ans/article/view/2083)).
  This parallels our finding that parent-chosen names go with more investment in newborns. Ours
  is in LLM agents, not people.

## What appears novel here

1. Parent-given personal names as the experimental variable in a generational, reproducing
   population of LLM agents.
2. Separating **addressability** from **naming** with a 2 × 2 of who chooses the handle (parents or
   world) by what it is (word or ID). Addressability is any stable handle, and it drives hunting
   together. Naming drives forming couples and investing in newborns.
3. Reconciling the factionalism result: shared group labels hurt coordination, and unique
   individual handles help it.

No study found here varies personal names alone in an LLM multi-agent simulation while holding
everything else fixed.
