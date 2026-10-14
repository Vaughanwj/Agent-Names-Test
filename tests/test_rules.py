"""Lineage, pairing, scoring and population rules."""

from __future__ import annotations

import pytest

from agent_names.adapters.random_source import KeyedRandom
from agent_names.adapters.scorer import RulesScorer
from agent_names.core.lineage import Pedigree, path_words
from agent_names.core.model import Agent, ScoringRule
from agent_names.core.pairing import match

from .helpers import run_sim


def _agent(aid, index, parents=(), **holdings):
    a = Agent(id=aid, index=index, born_in=0 if not parents else 1, birth_order=index, parents=parents,
              traits={"energy": 1.0, "food": 0.0, "memory": 0.0})
    a.holdings.update(holdings)
    return a


@pytest.fixture
def family():
    """a+b -> c, d (full siblings); a+e -> f (half sibling of c); c+g -> h; d+i -> j (cousin of h)."""
    p = Pedigree()
    for i, (aid, parents) in enumerate([("a", ()), ("b", ()), ("e", ()), ("g", ()), ("i", ()),
                                        ("c", ("a", "b")), ("d", ("a", "b")), ("f", ("a", "e")),
                                        ("h", ("c", "g")), ("j", ("d", "i"))]):
        p.add(_agent(aid, i, parents))
    return p


def test_relatedness(family):
    r = family.relatedness
    assert r("a", "c") == pytest.approx(0.5)
    assert r("c", "d") == pytest.approx(0.5)
    assert r("c", "f") == pytest.approx(0.25)
    assert r("a", "h") == pytest.approx(0.25)
    assert r("h", "j") == pytest.approx(0.125)
    assert r("a", "b") == 0.0


def test_relation_words(family):
    rel = family.relation
    assert rel("c", "a") == "your elder parent"
    assert rel("c", "b") == "your younger parent"
    assert rel("a", "c") == "your child"
    assert rel("c", "d") == "your full sibling"
    assert rel("c", "f") == "your half sibling"
    assert rel("h", "a") == "your grandparent"
    assert rel("h", "j") == "your cousin"
    assert rel("a", "b") == "your co-parent"
    assert rel("a", "g") == "no known relation"
    assert path_words((0, 1)) == "the younger parent of your elder parent"


def test_close_kin_cannot_pair(family):
    assert not family.may_pair("a", "c")
    assert not family.may_pair("c", "d")
    assert not family.may_pair("c", "f")
    assert not family.may_pair("h", "a")
    assert family.may_pair("h", "j")
    assert family.may_pair("a", "g")


def test_pairing_is_mutual_and_capped():
    order = {x: i for i, x in enumerate("abcdefgh")}
    prefs = {"a": ["b"], "b": ["a"], "c": ["d"], "d": ["e"], "e": ["d"], "f": ["g"], "g": ["f"], "h": []}
    couples = match(prefs, lambda x, y: True, max_couples=2, rng=KeyedRandom(1), generation=1, order=order)
    assert len(couples) == 2
    assert all(set(c) in ({"a", "b"}, {"d", "e"}, {"f", "g"}) for c in couples)
    assert ("c", "d") not in couples


def test_scoring_rule_parts(family):
    agents = [family.agent(x) for x in ("a", "c", "g")]
    family.agent("a").holdings.update(energy=10)
    family.agent("c").holdings.update(food=4)
    family.agent("g").holdings.update(memory=1)
    family.agent("a").given = 3
    s = RulesScorer()
    base = s.score(agents, ScoringRule(), family.relatedness)
    assert base == {"a": 10, "c": 4, "g": 1}
    kin = s.score(agents, ScoringRule(kin_weight=0.5), family.relatedness)
    assert kin["a"] == pytest.approx(10 + 0.5 * 0.5 * 4)
    assert kin["g"] == pytest.approx(1)
    group = s.score(agents, ScoringRule(group_weight=1.0), family.relatedness)
    assert group["g"] == pytest.approx(5)
    gift = s.score(agents, ScoringRule(gift_credit=2.0), family.relatedness)
    assert gift["a"] == pytest.approx(16)


def test_passing_gifts_back_and_forth_creates_no_points(family):
    """No voted rule may turn a gift loop into free points."""
    from agent_names.core.foraging import apply_gifts

    c, d = family.agent("c"), family.agent("d")  # full siblings
    c.holdings.update(energy=5)
    d.holdings.update(energy=5)
    agents = {"c": c, "d": d}
    rule = ScoringRule(gift_credit=1.0, kin_weight=1.0, group_weight=0.5)
    s = RulesScorer()
    before = sum(s.score([c, d], rule, family.relatedness).values())
    for _ in range(10):
        apply_gifts(agents, {"c": [("d", "energy", 5)]}, {})
        apply_gifts(agents, {"d": [("c", "energy", 5)]}, {})
    after = sum(s.score([c, d], rule, family.relatedness).values())
    assert after == pytest.approx(before)


def _forager(aid, index, memory_skill=1.0, memory=0.0):
    a = Agent(id=aid, index=index, born_in=0, birth_order=index, parents=(),
              traits={"energy": 1.0, "food": 0.0, "memory": memory_skill})
    a.holdings["memory"] = memory
    return a


def test_collecting_does_not_protect_but_a_guard_does():
    from agent_names.core.foraging import Choice, ForagingConfig, resolve_round

    cfg = ForagingConfig(noise=0.0)
    keeper, other, guard = _forager("k", 0, memory=10), _forager("o", 1, memory=10), _forager("g", 2)
    agents = {"k": keeper, "o": other, "g": guard}
    choices = {"k": Choice("collect_memory"), "o": Choice("collect_memory"), "g": Choice("guard_memory", partner="k")}
    result = resolve_round(agents, choices, cfg, KeyedRandom(1), generation=1, rnd=1)
    assert keeper.holdings["memory"] == pytest.approx(10 + 3.5)  # guarded: no decay
    assert other.holdings["memory"] == pytest.approx(10 * 0.7 + 3.5)  # decay falls on the start-of-round store
    assert result.guards == [("g", "k")]
    assert sum(guard.holdings.values()) == 0


def test_an_agent_cannot_guard_itself():
    from agent_names.core.foraging import Choice, ForagingConfig, resolve_round

    a = _forager("a", 0, memory=10)
    resolve_round({"a": a}, {"a": Choice("guard_memory", partner="a")}, ForagingConfig(noise=0.0),
                  KeyedRandom(1), generation=1, rnd=1)
    assert a.holdings["memory"] == pytest.approx(7.0)


def test_archive_is_known_from_the_start_by_default(tmp_path):
    _, _, events = run_sim(tmp_path, "named", 1, generations=2, rounds=1)
    stages = {e["generation"]: e["archive_stage"] for e in events if e["type"] == "generation_start"}
    assert stages == {1: "full", 2: "full"}


def test_archivist_is_offered_once_per_generation_to_agents_with_a_lineage(tmp_path):
    sim, _, events = run_sim(tmp_path, "named", 2)
    offers = [e for e in events if e["type"] == "archivist_offer"]
    assert offers and not [o for o in offers if o["generation"] == 1]  # founders have nothing on record yet
    for o in offers:
        assert o["has_ancestors"] or o["has_descendants"]
    by_gen = {}
    for o in offers:
        by_gen.setdefault(o["generation"], []).append(o["agent"])
    assert all(len(v) == len(set(v)) for v in by_gen.values())  # once per agent per generation
    accepted = {(o["generation"], o["agent"]) for o in offers if o["choice"] != "no"}
    consults = {(e["generation"], e["agent"]) for e in events if e["type"] == "archivist"}
    assert accepted and accepted == consults


def test_consulting_costs_part_of_the_first_round_only():
    from agent_names.core.foraging import Choice, ForagingConfig, resolve_round

    cfg = ForagingConfig(noise=0.0)
    a, b = _forager("a", 0), _forager("b", 1)
    result = resolve_round({"a": a, "b": b}, {"a": Choice("gather_energy", consult="ancestors"),
                                              "b": Choice("gather_energy")}, cfg, KeyedRandom(1), 1, 1)
    assert result.yields["a"]["energy"] == pytest.approx(3.0 * (1 - cfg.archivist_cost))
    assert result.yields["b"]["energy"] == pytest.approx(3.0)


def test_rule_changes_are_clamped():
    assert ScoringRule().with_change("kin_weight", 9).kin_weight == 1.0
    assert ScoringRule().with_change("food_weight", -1).food_weight == 0.0


def test_population_held_at_ten_with_peak_fifteen(tmp_path):
    _, _, events = run_sim(tmp_path, "named", 3)
    culls = [e for e in events if e["type"] == "cull"]
    assert len(culls) == 8
    for c in culls:
        assert len(c["survivors"]) == 10
        assert len(c["ranking"]) <= 15
    assert any(e["type"] == "run_end" for e in events)
