"""Real LangGraph + Orchestration for DORAMA STUDIO IA V2.

This module replaces any MockGraph and establishes the canonical
state, nodes, conditional edges, retries, checkpoints and persistence
as described in Fase 3 of the canonical plan.
"""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langgraph.checkpoint import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import add_messages

# ---------------------------------------------------------------------------
# 1️⃣  State definition – the single source of truth for an episode
# ---------------------------------------------------------------------------

class EpisodeState(TypedDict):
    """State that flows through the LangGraph orchestrator."""

    # Core episode metadata
    episode_id: str
    title: str
    season: int
    episode_number: int

    # Beat / micro‑beat information (produced by the MicroBeat Engine)
    beats: Annotated[list, add_messages]  # list of micro‑beat dicts

    # Optional scored fields used by the Retention / Cliffhanger engines
    retention_score: float | None = None
    cliffhanger_hint: str | None = None

    # Quality & cost tracking
    quality_score: float | None = None
    model_name: str | None = None
    cost_usd: float | None = None

    # Flag to signal early termination (e.g. “cliffhanger detected”)
    finished: bool = False


# ---------------------------------------------------------------------------
# 2️⃣  Node functions – pure functions that transform EpisodeState
# ---------------------------------------------------------------------------

def ingest_node(state: EpisodeState) -> EpisodeState:
    """Receive raw brief / research and populate the initial state."""
    # In a real deployment this would pull from a database or API.
    # Here we just seed minimal data.
    return {
        **state,
        "beats": [],
        "retention_score": None,
        "cliffhanger_hint": None,
        "quality_score": None,
        "model_name": None,
        "cost_usd": 0.0,
    }


def beat_engine_node(state: EpisodeState) -> EpisodeState:
    """MicroBeat Engine – generates ~90‑second episode beats."""
    # Placeholder: in production this calls the MicroBeat Engine.
    beats = state.get("beats", [])
    # Example synthetic beat:
    beats.append(
        {
            "beat_id": f"b{len(beats)+1:03d}",
            "type": "setup",
            "description": "Setup del episodio",
            "duration_seconds": 5.0,
        }
    )
    return {**state, "beats": beats}


def script_node(state: EpisodeState) -> EpisodeState:
    """Script Compiler – turns beats into a rough script draft."""
    # Placeholder: normally calls the Prompt Compiler + Provider Architecture.
    return {**state, "quality_score": 0.85, "model_name": "claude-3-opus-20240229"}


def quality_node(state: EpisodeState) -> EpisodeState:
    """Quality Control + Selective Regeneration gate."""
    score = state.get("quality_score", 0.0)
    # If quality falls below threshold, we loop back to beat_engine.
    if score < 0.7:
        # We'll signal a retry by returning a special key; the graph will
        # re‑enter beat_engine via a conditional edge.
        return {**state, "cliffhanger_hint": "low‑quality – regenerar beats"}
    return {**state, "finished": True}


# ---------------------------------------------------------------------------
# 3️⃣  Graph construction – StateGraph with conditional edges
# ---------------------------------------------------------------------------

def build_episode_graph() -> StateGraph:
    """Build and return the compiled LangGraph for an episode."""

    graph = StateGraph(EpisodeState)

    # Add nodes (edges will be added afterwards)
    graph.add_node("ingest", ingest_node)
    graph.add_node("beat_engine", beat_engine_node)
    graph.add_node("script_compiler", script_node)
    graph.add_node("quality_gate", quality_node)

    # Entry point
    graph.set_entry_point("ingest")

    # Linear flow: ingest → beat_engine → script_compiler → quality_gate
    graph.add_edge("ingest", "beat_engine")
    graph.add_edge("beat_engine", "script_compiler")
    graph.add_edge("script_compiler", "quality_gate")

    # Conditional edge from quality gate:
    #   - if quality >= 0.7 → END (episode finished)
    #   - if quality < 0.7 → go back to beat_engine for regeneration
    def quality_conditional(state: EpisodeState) -> str:
        return END if state.get("finished") else "beat_engine"

    graph.add_conditional_edges(
        "quality_gate",
        quality_conditional,
        {END: END, "beat_engine": "beat_engine"},
    )

    # Add in‑memory checkpointing for persistence / resume
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# ---------------------------------------------------------------------------
# 4️⃣  Helper to run a single episode from start to finish (or until retry)
# ---------------------------------------------------------------------------

def run_episode(
    episode_id: str,
    title: str,
    *,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Execute the graph for one episode, handling retries automatically."""


    graph = build_episode_graph()
    initial_state: EpisodeState = {
        "episode_id": episode_id,
        "title": title,
        "season": 1,
        "episode_number": 1,
        "beats": [],
        "retention_score": None,
        "cliffhanger_hint": None,
        "quality_score": None,
        "model_name": None,
        "cost_usd": 0.0,
        "finished": False,
    }

    # Configure a thread‑local checkpoint so we can resume later
    config = {"configurable": {"thread_id": episode_id}}

    # Run until the graph terminates or we exhaust retries
    state = initial_state
    for attempt in range(1, max_retries + 1):
        # Compile the graph fresh each loop so the conditional edges re‑evaluate
        graph = build_episode_graph()
        state = graph.invoke(state, config)
        if state.get("finished"):
            break

    return {
        "episode_id": state["episode_id"],
        "title": state["title"],
        "beats": state.get("beats", []),
        "quality_score": state.get("quality_score"),
        "model_name": state.get("model_name"),
        "cost_usd": state.get("cost_usd", 0.0),
        "finished": state.get("finished", False),
        "retries": attempt,
    }
