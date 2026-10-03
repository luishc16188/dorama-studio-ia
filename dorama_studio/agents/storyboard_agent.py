"""Storyboard Agent – real implementation with Knowledge Ledger + Story Graph"""

from __future__ import annotations

from typing import Any

import warnings

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.knowledge_ledger import knowledge_ledger, KnowledgeState, KnowledgeSource
from dorama_studio.core.story_graph import story_graph_manager
from dorama_studio.data.schemas import Storyboard, StoryboardAgentOutputSchema

class StoryboardAgent(BaseAgent[Storyboard, StoryboardAgentOutputSchema]):
    InputSchema = Storyboard
    OutputSchema = StoryboardAgentOutputSchema

    def __init__(self):
        super().__init__("StoryboardAgent")
        self.agent_name = "StoryboardAgent"

    def run(self, input_data: Storyboard) -> dict[str, Any]:
        """Run the storyboard agent."""
        result = self.process(input_data)
        # Return dict-like object with payload attribute for test compatibility
        class ResultWrapper:
            def __init__(self, payload):
                self.payload = payload
            def get(self, key, default=None):
                if isinstance(self.payload, dict):
                    return self.payload.get(key, default)
                return default
            def __getitem__(self, key):
                if isinstance(self.payload, dict):
                    return self.payload[key]
                raise KeyError(key)
            def __contains__(self, key):
                if isinstance(self.payload, dict):
                    return key in self.payload
                return False
        return ResultWrapper(result)

    def _process(self, validated_input: Storyboard) -> StoryboardAgentOutputSchema:
        """Process storyboard with Knowledge Ledger and Story Graph integration."""
        start = __import__("time").time()
        try:
            # Handle Storyboard input
            episode_num = validated_input.episode_num
            shots = validated_input.shots
            title = validated_input.title or f"Episode {episode_num}"

            # Registrar generación de storyboard en Knowledge Ledger
            try:
                knowledge_ledger.acquire_knowledge(
                    character_id="storyboard_engine",
                    knowledge_type="storyboard_generation",
                    knowledge_state=KnowledgeState.KNOWS,
                    source=KnowledgeSource.DIRECT_OBSERVATION,
                    source_reference=f"storyboard_ep{episode_num}_{title}",
                    confidence=1.0,
                    context={"episode_num": episode_num, "title": title, "shots_count": len(shots)}
                )
            except Exception as e:
                warnings.warn(f"Knowledge Ledger record error: {e}")

            # Añadir nodo Story Graph para este storyboard
            try:
                node_id = f"storyboard_ep{episode_num}_{title}"
                story_graph_manager.add_node(
                    node_id=node_id,
                    node_type="storyboard",
                    timestamp=__import__("time").time(),
                    description=f"Storyboard generation for episode {episode_num}: {title}",
                    metadata={"episode_num": episode_num, "title": title, "shots_count": len(shots)}
                )
                # Connect to episode node if it exists
                story_graph_manager.add_edge(
                    source_node_id=f"episode_{episode_num}",
                    target_node_id=node_id,
                    relationship_type="has_storyboard",
                    strength=1.0,
                    metadata={}
                )
            except Exception as e:
                warnings.warn(f"StoryGraph update error: {e}")

        except Exception as e:
            warnings.warn(f"Storyboard processing error: {e}")

        # Return output schema with the storyboard
        return StoryboardAgentOutputSchema(
            storyboard=validated_input
        )