"""The Claude adapter, against a fake client (no network)."""

from __future__ import annotations

import json
from types import SimpleNamespace

from agent_names.adapters import prompting
from agent_names.adapters.anthropic_mind import AnthropicMind
from agent_names.core.model import ScoringRule
from agent_names.core.ports import DecisionRequest, OtherView, SelfView, WorldView


class FakeLog:
    def __init__(self):
        self.rows = []

    def record(self, event_type, **data):
        self.rows.append((event_type, data))


def _request(kind="forage"):
    world = WorldView("named", 2, 8, 1, 5, 10, 15, ScoringRule(), "none")
    me = SelfView("Ash", "the world", 0, 2, "You are one of the first agents.",
                  {"energy": 1, "food": 0, "memory": 0}, {"energy": 2, "food": 0, "memory": 0},
                  {"energy": 2, "food": 0, "memory": 0}, 0.0, 2.0)
    other = OtherView(1, "Brook", "no known relation", 2, {"energy": 0, "food": 1, "memory": 0},
                      {"energy": 0, "food": 3, "memory": 0},
                      {"gave_you": 0, "you_gave": 0, "guarded_you": 0, "you_guarded": 0, "hunted_together": 0}, 3.0)
    return DecisionRequest(kind, "f0", world, me, [other])


def _response(payload, stop="end_turn"):
    usage = SimpleNamespace(input_tokens=100, output_tokens=50, cache_creation_input_tokens=0,
                            cache_read_input_tokens=900)
    return SimpleNamespace(stop_reason=stop, usage=usage, _request_id="req_test",
                           content=[SimpleNamespace(type="text", text=json.dumps(payload))])


def _mind(responses):
    log = FakeLog()
    mind = AnthropicMind("SYSTEM", log, concurrency=1)
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    mind.client = SimpleNamespace(messages=SimpleNamespace(create=create))
    return mind, calls, log


def test_request_shape_and_parse():
    answer = {"intent": "hunt", "activity": "hunt_together", "partner": 1,
              "gifts": [{"to": 1, "resource": "energy", "amount": 1}], "message": "hi"}
    mind, calls, log = _mind([_response(answer)])
    d = mind.decide(_request())
    assert d.activity == "hunt_together" and d.partner == 1 and d.gifts == [(1, "energy", 1.0)]
    kw = calls[0]
    assert kw["model"] == "claude-haiku-5-5"
    assert kw["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert kw["output_config"]["effort"] == "low"
    assert kw["output_config"]["format"]["type"] == "json_schema"
    assert "thinking" not in kw and "temperature" not in kw
    llm = [r for t, r in log.rows if t == "llm_call"][0]
    assert llm["cache_read_input_tokens"] == 900 and llm["output_tokens"] == 50


def test_refusal_retries_then_falls_back():
    mind, calls, _ = _mind([_response({}, stop="refusal"), _response({}, stop="refusal")])
    d = mind.decide(_request())
    assert d.fallback and d.activity == "gather_energy"
    assert len(calls) == 2


def test_budget_stops_the_run():
    import pytest

    from agent_names.adapters.anthropic_mind import BudgetExceeded

    answer = {"intent": "", "activity": "gather_energy", "partner": 0,
              "gifts": [], "message": ""}
    mind, calls, _ = _mind([_response(answer) for _ in range(5)])
    mind.budget_usd = 0.0001  # one fake call costs $0.000044, so the fourth is refused
    for _ in range(3):
        mind.decide(_request())
    with pytest.raises(BudgetExceeded):
        mind.decide(_request())
    assert len(calls) == 3


def test_first_request_of_a_cold_kind_goes_alone():
    answer = {"intent": "", "activity": "gather_energy", "partner": 0,
              "gifts": [], "message": ""}
    mind, calls, _ = _mind([_response(answer) for _ in range(6)])
    mind.concurrency = 4
    order = []
    original = mind.decide

    def tracked(req):
        order.append(req.agent_id)
        return original(req)

    mind.decide = tracked
    reqs = [_request() for _ in range(3)]
    for i, r in enumerate(reqs):
        r.agent_id = f"a{i}"
    assert len(mind.decide_batch(reqs)) == 3
    assert order[0] == "a0"
    assert "forage" in mind._last_seen


def test_every_schema_is_strict():
    for kind in ("archivist", "forage", "pair", "birth", "propose", "vote"):
        req = _request(kind)
        req.extra = {"naming": True}
        s = prompting.schema(req)
        stack = [s]
        while stack:
            node = stack.pop()
            if node.get("type") == "object":
                assert node["additionalProperties"] is False
                assert set(node["required"]) == set(node["properties"])
                stack.extend(node["properties"].values())
            elif node.get("type") == "array":
                stack.append(node["items"])
