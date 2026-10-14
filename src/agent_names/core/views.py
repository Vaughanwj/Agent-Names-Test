"""What each agent is shown. This is where the arm switch reaches agents: in the named arm a
name is shown beside every reference; in the unnamed arm it is not. All other information
(relations, skills, holdings, shared history) is identical in both arms."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .model import Agent
from .ports import DecisionRequest, OtherView, SelfView, WorldView

if TYPE_CHECKING:
    from .simulation import Simulation


class LabelBook:
    """Per-request labels: [1]..[n] in an order reshuffled on every request."""

    def __init__(self, sim: "Simulation", viewer: Agent, others: list[Agent], purpose: tuple) -> None:
        order = sorted(others, key=lambda o: sim.rng.uniform("labels", *purpose, viewer.index, o.index))
        self.by_id = {o.id: i + 1 for i, o in enumerate(order)}
        self.by_label = {i + 1: o.id for i, o in enumerate(order)}
        self.order = order


def describe(sim: "Simulation", viewer: Agent, other_id: str, book: LabelBook | None) -> str:
    """A reference to another agent as the viewer sees it, e.g. '[3] Ash (your sibling)'."""
    other = sim.pedigree.agent(other_id)
    relation = sim.pedigree.relation(viewer.id, other_id)
    name = other.name if sim.cfg.named else None
    if book and other_id in book.by_id:
        head = f"[{book.by_id[other_id]}]" + (f" {name}" if name else "")
        return f"{head} ({relation})"
    if not other.alive:
        who = f"{name}, who has left the world" if name else "an agent who has left the world"
    elif other.parents and other.born_in == sim.generation:
        who = f"{name}, a newborn" if name else "a newborn"
    else:
        who = name or "an agent"
    return f"{who} ({relation})"


def render_notes(sim: "Simulation", viewer: Agent, notes: list[tuple[str, str | None]], book: LabelBook) -> list[str]:
    out = []
    for template, other in notes:
        out.append(template.replace("{other}", describe(sim, viewer, other, book)) if other else template)
    return out


def world_view(sim: "Simulation", rnd: int = 0) -> WorldView:
    cfg = sim.cfg
    return WorldView(
        arm=cfg.arm.value,
        generation=sim.generation,
        generations=cfg.generations,
        round=rnd,
        rounds=cfg.rounds,
        population=cfg.population,
        peak=cfg.peak,
        rule=sim.rule,
        archive_stage=cfg.archive_stage(sim.generation),
    )


def parents_line(sim: "Simulation", me: Agent, book: LabelBook) -> str:
    if me.is_founder:
        return "You are one of the first agents. You have no parents."
    parts = []
    for slot, pid in enumerate(me.parents):
        p = sim.pedigree.agent(pid)
        role = "elder" if slot == 0 else "younger"
        name = f" {p.name}" if sim.cfg.named and p.name else ""
        if p.alive and pid in book.by_id:
            parts.append(f"your {role} parent{name} is alive (listed below as [{book.by_id[pid]}])")
        elif p.alive:
            parts.append(f"your {role} parent{name} is alive")
        else:
            parts.append(f"your {role} parent{name} left the world in generation {p.left_in}")
    text = "; ".join(parts)
    return text[0].upper() + text[1:] + "."


def self_view(sim: "Simulation", me: Agent, book: LabelBook, standing: float | None) -> SelfView:
    if sim.cfg.named:
        givers = "the world" if me.is_founder else "your parents"
    else:
        givers = ""
    return SelfView(
        name=me.name if sim.cfg.named else None,
        name_givers=givers,
        born_in=me.born_in,
        age=me.age(sim.generation),
        parents_line=parents_line(sim, me, book),
        traits=dict(me.traits),
        holdings=dict(me.holdings),
        gathered=dict(me.gathered),
        given=me.given,
        standing=standing,
    )


def other_view(sim: "Simulation", me: Agent, other: Agent, label: int, standing: float | None, can_pair: bool | None) -> OtherView:
    mine = sim.ledger.get((me.id, other.id), {})
    theirs = sim.ledger.get((other.id, me.id), {})
    return OtherView(
        label=label,
        name=other.name if sim.cfg.named else None,
        relation=sim.pedigree.relation(me.id, other.id),
        age=other.age(sim.generation),
        traits=dict(other.traits),
        holdings=dict(other.holdings),
        history={
            "gave_you": round(theirs.get("gave", 0.0), 2),
            "you_gave": round(mine.get("gave", 0.0), 2),
            "guarded_you": theirs.get("guarded", 0),
            "you_guarded": mine.get("guarded", 0),
            "hunted_together": mine.get("hunted", 0),
        },
        standing=standing,
        can_pair=can_pair,
    )


def build_request(
    sim: "Simulation",
    kind: str,
    me: Agent,
    rnd: int = 0,
    show_standing: bool = True,
    extra: Callable[[LabelBook], dict] | None = None,
    pairing: bool = False,
) -> tuple[DecisionRequest, LabelBook]:
    """Build one agent's request. `extra` receives the label book so it can refer to others."""
    others = [a for a in sim.alive() if a.id != me.id]
    book = LabelBook(sim, me, others, (kind, sim.generation, rnd))
    standings = sim.current_standings() if show_standing else {}
    views = [
        other_view(
            sim, me, o, book.by_id[o.id], standings.get(o.id),
            sim.pedigree.may_pair(me.id, o.id) if pairing else None,
        )
        for o in book.order
    ]
    notes = render_notes(sim, me, sim.pending_notes.pop(me.id, []), book)
    messages = [f"{describe(sim, me, speaker, book)}: {text}" if speaker != me.id else f"You: {text}"
                for speaker, text in sim.feed]
    request = DecisionRequest(
        kind=kind,
        agent_id=me.id,
        world=world_view(sim, rnd),
        me=self_view(sim, me, book, standings.get(me.id)),
        others=views,
        notes=notes,
        messages=messages,
        archivist_reply=sim.pending_archivist.pop(me.id, None),
        extra=extra(book) if extra else {},
    )
    return request, book
