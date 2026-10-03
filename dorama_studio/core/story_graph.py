"""
Story Graph - Represents story causality, setup/payoff relationships, and information flow.
Implements the story graph for tracking causal dependencies and information acquisition.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque

from dorama_studio.core.knowledge_ledger import KnowledgeState
from dorama_studio.core.persistence import PersistenceManager


@dataclass
class StoryNode:
    """A node in the story graph representing a beat or event."""
    node_id: str
    node_type: str  # "beat", "setup", "payoff", "revelation", "decision", etc.
    timestamp: str  # ISO timestamp
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StoryEdge:
    """An edge in the story graph representing a causal or informational relationship."""
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str  # "causes", "enables", "informs", "reveals", "prevents", etc.
    strength: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StoryGraph:
    """A directed graph representing story causality and information flow."""
    nodes: Dict[str, StoryNode] = field(default_factory=dict)
    edges: Dict[str, StoryEdge] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class StoryGraphManager:
    """
    Manages the story graph for tracking causal dependencies,
    setup/payoff relationships, and information flow.
    Prevents characters from using knowledge they haven't acquired.
    """

    def __init__(self, persistence_manager: Optional[PersistenceManager] = None):
        self.persistence_manager = persistence_manager or PersistenceManager()
        self.graph = StoryGraph()
        self._initialize_graph()

    def _initialize_graph(self) -> None:
        """Initialize the story graph."""
        # Start with an empty graph - will be built as story progresses
        pass

    def add_node(
        self,
        node_id: str,
        node_type: str,
        timestamp: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a node to the story graph.

        Args:
            node_id: Unique identifier for the node
            node_type: Type of node (beat, setup, payoff, etc.)
            timestamp: ISO timestamp when this node occurs
            description: Human-readable description
            metadata: Additional metadata about the node

        Returns:
            node_id: The ID of the added node
        """
        if metadata is None:
            metadata = {}

        node = StoryNode(
            node_id=node_id,
            node_type=node_type,
            timestamp=timestamp,
            description=description,
            metadata=metadata
        )

        self.graph.nodes[node_id] = node
        return node_id

    def add_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        edge_id: Optional[str] = None
    ) -> str:
        """
        Add an edge to the story graph representing a relationship between nodes.

        Args:
            source_node_id: ID of the source node
            target_node_id: ID of the target node
            relationship_type: Type of relationship (causes, informs, etc.)
            strength: Strength of the relationship (0.0-1.0)
            metadata: Additional metadata about the edge
            edge_id: Optional custom edge ID

        Returns:
            edge_id: The ID of the added edge
        """
        if metadata is None:
            metadata = {}
        if edge_id is None:
            import hashlib
            content = f"{source_node_id}:{target_node_id}:{relationship_type}:{datetime.utcnow().isoformat()}"
            edge_id = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Validate that both nodes exist
        if source_node_id not in self.graph.nodes:
            raise ValueError(f"Source node {source_node_id} does not exist")
        if target_node_id not in self.graph.nodes:
            raise ValueError(f"Target node {target_node_id} does not exist")

        edge = StoryEdge(
            edge_id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type,
            strength=max(0.0, min(1.0, strength)),
            metadata=metadata
        )

        self.graph.edges[edge_id] = edge
        return edge_id

    def get_node(self, node_id: str) -> Optional[StoryNode]:
        """Get a node by ID."""
        return self.graph.nodes.get(node_id)

    def get_edges_from(self, node_id: str) -> List[StoryEdge]:
        """Get all edges originating from a node."""
        return [
            edge for edge in self.graph.edges.values()
            if edge.source_node_id == node_id
        ]

    def get_edges_to(self, node_id: str) -> List[StoryEdge]:
        """Get all edges pointing to a node."""
        return [
            edge for edge in self.graph.edges.values()
            if edge.target_node_id == node_id
        ]

    def get_ancestors(self, node_id: str) -> Set[str]:
        """
        Get all ancestor nodes (nodes that have a path to this node).
        Used to check what events/information preceded this node.
        """
        visited = set()
        queue = deque([node_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            # Add all nodes that have edges pointing to current
            for edge in self.get_edges_to(current):
                if edge.source_node_id not in visited:
                    queue.append(edge.source_node_id)

        return visited

    def get_descendants(self, node_id: str) -> Set[str]:
        """
        Get all descendant nodes (nodes that this node has a path to).
        Used to check what events/information follow from this node.
        """
        visited = set()
        queue = deque([node_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            # Add all nodes that current has edges pointing to
            for edge in self.get_edges_from(current):
                if edge.target_node_id not in visited:
                    queue.append(edge.target_node_id)

        return visited

    def validate_setup_payoff(
        self,
        payoff_node_id: str,
        required_setup_node_ids: List[str],
        knowledge_ledger: Optional[Any] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate that a payoff has all required setups.

        Args:
            payoff_node_id: ID of the payoff node
            required_setup_node_ids: List of setup node IDs that must precede the payoff
            knowledge_ledger: Optional knowledge ledger to check knowledge acquisition

        Returns:
            Tuple of (is_valid, missing_setups)
        """
        if payoff_node_id not in self.graph.nodes:
            return False, [f"Payoff node {payoff_node_id} does not exist"]

        payoff_node = self.graph.nodes[payoff_node_id]
        if payoff_node.node_type != "payoff":
            return False, [f"Node {payoff_node_id} is not a payoff node"]

        # Get all ancestors of the payoff
        ancestors = self.get_ancestors(payoff_node_id)

        # Check which required setups are missing
        missing_setups = []
        for setup_id in required_setup_node_ids:
            if setup_id not in ancestors:
                missing_setups.append(setup_id)

        return len(missing_setups) == 0, missing_setups

    def validate_knowledge_acquisition(
        self,
        character_id: str,
        knowledge_type: str,
        usage_node_id: str,
        knowledge_ledger: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a character has acquired knowledge before using it.

        Args:
            character_id: ID of the character
            knowledge_type: Type of knowledge being used
            usage_node_id: ID of the node where knowledge is being used
            knowledge_ledger: Knowledge ledger instance

        Returns:
            Tuple of (is_valid, error_message)
        """
        if usage_node_id not in self.graph.nodes:
            return False, f"Usage node {usage_node_id} does not exist"

        usage_node = self.graph.nodes[usage_node_id]
        usage_time = usage_node.timestamp

        # Check if character has acquired this knowledge before or at usage time
        knows_before = knowledge_ledger.can_character_know(
            character_id, knowledge_type
        )

        if not knows_before:
            return False, f"Character {character_id} uses {knowledge_type} before acquiring it"

        # More precise check: get knowledge event timestamp and compare to usage time
        knowledge_event = knowledge_ledger.get_knowledge_events(
            character_id=character_id,
            knowledge_type=knowledge_type,
            limit=1
        )

        if knowledge_event:
            knowledge_time = knowledge_event[0].timestamp
            if knowledge_time > usage_time:
                return False, f"Character {character_id} acquires {knowledge_type} after using it"

        return True, None

    def detect_knowledge_anticipation(
        self,
        character_id: str,
        knowledge_type: str,
        knowledge_ledger: Any
    ) -> List[str]:
        """
        Detect instances where a character uses knowledge before acquiring it.

        Args:
            character_id: ID of the character
            knowledge_type: Type of knowledge to check
            knowledge_ledger: Knowledge ledger instance

        Returns:
            List of node IDs where knowledge anticipation occurs
        """
        anticipation_nodes = []

        # Get all nodes where this knowledge might be used
        # In practice, this would check agent outputs, prompts, etc.
        # For now, we'll check all nodes as a placeholder
        for node_id, node in self.graph.nodes.items():
            is_valid, error = self.validate_knowledge_acquisition(
                character_id, knowledge_type, node_id, knowledge_ledger
            )
            if not is_valid and "before acquiring it" in error:
                anticipation_nodes.append(node_id)

        return anticipation_nodes

    def get_story_summary(self) -> Dict[str, Any]:
        """Get a summary of the current story graph."""
        return {
            "node_count": len(self.graph.nodes),
            "edge_count": len(self.graph.edges),
            "nodes_by_type": dict(
                defaultdict(int, {
                    node.node_type: 0 for node in self.graph.nodes.values()
                })
            ),
            "edges_by_type": dict(
                defaultdict(int, {
                    edge.relationship_type: 0 for edge in self.graph.edges.values()
                })
            )
        }

    def export_to_dict(self) -> Dict[str, Any]:
        """Export the story graph to a dictionary for serialization."""
        return {
            "nodes": {
                node_id: {
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "timestamp": node.timestamp,
                    "description": node.description,
                    "metadata": node.metadata
                }
                for node_id, node in self.graph.nodes.items()
            },
            "edges": {
                edge_id: {
                    "edge_id": edge.edge_id,
                    "source_node_id": edge.source_node_id,
                    "target_node_id": edge.target_node_id,
                    "relationship_type": edge.relationship_type,
                    "strength": edge.strength,
                    "metadata": edge.metadata
                }
                for edge_id, edge in self.graph.edges.items()
            },
            "metadata": self.graph.metadata
        }

    def import_from_dict(self, data: Dict[str, Any]) -> None:
        """Import a story graph from a dictionary."""
        self.graph = StoryGraph(
            nodes={
                node_id: StoryNode(
                    node_id=node_data["node_id"],
                    node_type=node_data["node_type"],
                    timestamp=node_data["timestamp"],
                    description=node_data["description"],
                    metadata=node_data.get("metadata", {})
                )
                for node_id, node_data in data.get("nodes", {}).items()
            },
            edges={
                edge_id: StoryEdge(
                    edge_id=edge_data["edge_id"],
                    source_node_id=edge_data["source_node_id"],
                    target_node_id=edge_data["target_node_id"],
                    relationship_type=edge_data["relationship_type"],
                    strength=edge_data.get("strength", 1.0),
                    metadata=edge_data.get("metadata", {})
                )
                for edge_id, edge_data in data.get("edges", {}).items()
            },
            metadata=data.get("metadata", {})
        )


# Global story graph manager instance
story_graph_manager = StoryGraphManager()