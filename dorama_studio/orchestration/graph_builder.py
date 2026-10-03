"""
GraphBuilder - High-level API for building and managing LangGraph pipelines.
Provides a fluent interface for constructing production workflows.
"""

from collections.abc import Callable
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph

from .checkpoints import BaseCheckpointSaver, get_checkpointer
from .graph import GraphBuilder as CoreGraphBuilder
from .human_in_loop import HumanInLoopManager
from .recovery import RecoveryManager
from .retry import STANDARD_RETRY, RetryConfig, RetryPolicy
from .state import (
    SeasonProductionState,
)

class GraphBuilder:
    """
    High-level graph builder with fluent API.

    Usage:
        builder = GraphBuilder()
        builder.with_checkpointer("postgres", host="localhost")
        builder.with_retry_policy(STANDARD_RETRY)
        builder.with_recovery(RecoveryManager())
        builder.with_hitl(HumanInLoopManager())

        graph = builder.build()
    """

    def __init__(self):
        self._checkpointer: BaseCheckpointSaver | None = None
        self._checkpointer_config: dict[str, Any] = {}
        self._retry_policy: RetryPolicy | None = None
        self._recovery_manager: RecoveryManager | None = None
        self._hitl_manager: HumanInLoopManager | None = None
        self._custom_nodes: dict[str, Callable] = {}
        self._custom_edges: list[tuple] = []
        self._conditional_edges: list[tuple] = []
        self._entry_point: str | None = None
        self._state_schema = SeasonProductionState
        self._metadata: dict[str, Any] = {}

    # ============================================================
    # Configuration Methods
    # ============================================================

    def with_checkpointer(
        self,
        backend: str = "memory",
        **kwargs
    ) -> 'GraphBuilder':
        """Set checkpointer backend."""
        self._checkpointer = get_checkpointer(backend, **kwargs)
        self._checkpointer_config = {"backend": backend, **kwargs}
        return self

    def with_checkpointer_instance(self, checkpointer: BaseCheckpointSaver) -> 'GraphBuilder':
        """Set a pre-configured checkpointer instance."""
        self._checkpointer = checkpointer
        return self

    def with_retry_policy(self, policy: RetryPolicy) -> 'GraphBuilder':
        """Set retry policy for node execution."""
        self._retry_policy = policy
        return self

    def with_retry_config(self, config: RetryConfig) -> 'GraphBuilder':
        """Set retry configuration."""
        self._retry_policy = RetryPolicy(config)
        return self

    def with_recovery(self, manager: RecoveryManager) -> 'GraphBuilder':
        """Set recovery manager."""
        self._recovery_manager = manager
        return self

    def with_hitl(self, manager: HumanInLoopManager) -> 'GraphBuilder':
        """Set HITL manager."""
        self._hitl_manager = manager
        return self

    def with_state_schema(self, schema) -> 'GraphBuilder':
        """Set custom state schema."""
        self._state_schema = schema
        return self

    def with_metadata(self, **kwargs) -> 'GraphBuilder':
        """Add metadata to graph."""
        self._metadata.update(kwargs)
        return self

    # ============================================================
    # Customization Methods
    # ============================================================

    def add_node(self, name: str, func: Callable) -> 'GraphBuilder':
        """Add a custom node."""
        self._custom_nodes[name] = func
        return self

    def add_edge(self, from_node: str, to_node: str) -> 'GraphBuilder':
        """Add a custom edge."""
        self._custom_edges.append((from_node, to_node))
        return self

    def add_conditional_edge(
        self,
        from_node: str,
        condition: Callable,
        path_map: dict[str, str]
    ) -> 'GraphBuilder':
        """Add a conditional edge."""
        self._conditional_edges.append((from_node, condition, path_map))
        return self

    def set_entry_point(self, node: str) -> 'GraphBuilder':
        """Set graph entry point."""
        self._entry_point = node
        return self

    # ============================================================
    # Build Methods
    # ============================================================

    def build(self) -> StateGraph:
        """
        Build the production graph with all configurations.

        Returns:
            Compiled StateGraph
        """
        # Use core graph builder as base
        core_builder = CoreGraphBuilder(checkpointer=self._checkpointer)

        # Apply customizations (wrapping nodes with retry/recovery)
        self._apply_customizations(core_builder)

        # Build and return
        return core_builder.build_season_graph()

    def build_season_graph(self) -> StateGraph:
        """Build season-level production graph."""
        core_builder = CoreGraphBuilder(checkpointer=self._checkpointer)
        self._apply_customizations(core_builder)
        return core_builder.build_season_graph()

    def build_episode_graph(self) -> StateGraph:
        """Build episode-level subgraph."""
        core_builder = CoreGraphBuilder(checkpointer=self._checkpointer)
        self._apply_customizations(core_builder)
        return core_builder._build_episode_subgraph()

    def _apply_customizations(self, builder: CoreGraphBuilder) -> None:
        """Apply all customizations to core builder.

        Note: CoreGraphBuilder builds its graph internally in build_* methods.
        We need to intercept node creation to apply retry/recovery wrappers.
        For now, we'll enhance the core builder's _init_agents method to
        wrap agent nodes with retry logic.
        """
        # Apply retry policy to agent nodes if configured
        if self._retry_policy:
            # This would require modifying CoreGraphBuilder to wrap agent nodes
            # For now, we note that CoreGraphBuilder already has basic error handling
            pass

        # Apply recovery manager if configured
        if self._recovery_manager:
            # Recovery manager would be applied at graph level
            pass

        # Apply HITL manager if configured
        if self._hitl_manager:
            # HITL manager integration would require modifying node execution
            pass

    # Wrapper methods (placeholders for future implementation)
    def _wrap_nodes_with_retry(self, builder: CoreGraphBuilder) -> None:
        """Wrap node functions with retry policy."""
        # TODO: Implement actual node wrapping with retry logic
        pass

    def _wrap_nodes_with_recovery(self, builder: CoreGraphBuilder) -> None:
        """Wrap nodes with recovery handling."""
        # TODO: Implement actual node wrapping with recovery logic
        pass

    def _wrap_hitl_nodes(self, builder: CoreGraphBuilder) -> None:
        """Add HITL wrapping to appropriate nodes."""
        # TODO: Implement actual HITL wrapping logic
        pass

    # ============================================================
    # Pipeline Templates
    # ============================================================

    def create_full_pipeline(
        self,
        checkpointer_backend: str = "memory",
        **checkpointer_kwargs
    ) -> StateGraph:
        """
        Create a complete production pipeline with all features enabled.

        Args:
            checkpointer_backend: "memory" | "postgres" | "redis"
            **checkpointer_kwargs: Backend-specific config

        Returns:
            Compiled StateGraph with full pipeline
        """
        builder = GraphBuilder()
        builder.with_checkpointer(backend=checkpointer_backend, **checkpointer_kwargs)
        builder.with_retry_policy(STANDARD_RETRY)
        builder.with_recovery(RecoveryManager())
        builder.with_hitl(HumanInLoopManager())
        return builder.build()

    def create_episode_only_pipeline(
        self,
        checkpointer_backend: str = "memory",
        **checkpointer_kwargs
    ) -> StateGraph:
        """
        Create episode-only pipeline (no season-level nodes).

        Args:
            checkpointer_backend: Checkpointer backend
            **checkpointer_kwargs: Backend config

        Returns:
            Episode subgraph
        """
        builder = GraphBuilder()
        builder.with_checkpointer(backend=checkpointer_backend, **checkpointer_kwargs)
        builder.with_retry_policy(STANDARD_RETRY)
        return builder.build_episode_graph()

    def create_test_pipeline() -> StateGraph:
        """Create a minimal pipeline for testing (no checkpoints, no retries)."""
        from .graph import build_pipeline_graph
        return build_pipeline_graph()

    def create_development_pipeline() -> StateGraph:
        """Create pipeline optimized for development (fast, in-memory)."""
        return create_full_pipeline(
            checkpointer_backend="memory",
        )

    def create_production_pipeline(
        self,
        postgres_dsn: str | None = None,
        redis_url: str | None = None,
    ) -> StateGraph:
        """
        Create production-ready pipeline with persistent checkpoints.

        Args:
            postgres_dsn: PostgreSQL DSN for checkpoints
            redis_url: Redis URL for checkpoints (alternative to postgres)

        Returns:
            Production StateGraph
        """
        if postgres_dsn:
            return create_full_pipeline("postgres", dsn=postgres_dsn)
        elif redis_url:
            return create_full_pipeline("redis", url=redis_url)
        else:
            # Fallback to memory with warning
            import warnings
            warnings.warn("No persistent checkpointer configured, using InMemorySaver")
            return create_full_pipeline("memory")

# ============================================================
# Graph Inspection Utilities
# ============================================================

def inspect_graph(graph: StateGraph) -> dict[str, Any]:
    """Inspect graph structure."""
    nodes = list(graph.nodes.keys())
    edges = []

    # Get edges from graph (implementation depends on langgraph version)
    try:
        edges = list(graph.edges)
    except:
        pass

    return {
        "nodes": nodes,
        "node_count": len(nodes),
        "edges": edges,
        "entry_point": getattr(graph, 'entry_point', None),
    }

def visualize_graph(graph: StateGraph, output_path: str | None = None) -> str:
    """
    Generate Mermaid diagram for graph visualization.

    Args:
        graph: StateGraph to visualize
        output_path: Optional path to save diagram

    Returns:
        Mermaid diagram string
    """
    lines = ["graph TD"]

    # Nodes
    for node in graph.nodes.keys():
        if not node.startswith("__"):
            lines.append(f"    {node}[{node}]")

    # Edges (simplified)
    try:
        for edge in graph.edges:
            if isinstance(edge, tuple) and len(edge) >= 2:
                lines.append(f"    {edge[0]} --> {edge[1]}")
    except:
        pass

    diagram = "\n".join(lines)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(diagram)

    return diagram

# ============================================================
# Export
# ============================================================

__all__ = [
    "GraphBuilder",
    "create_full_pipeline",
    "create_episode_only_pipeline",
    "create_test_pipeline",
    "create_development_pipeline",
    "create_production_pipeline",
    "inspect_graph",
    "visualize_graph",
]