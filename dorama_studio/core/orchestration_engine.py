"""
Orchestration Engine - Coordinates agent execution with proper data flow, retries, and error handling.
"""

from __future__ import annotations

import logging
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext


class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class AgentNode:
    """Represents an agent in the orchestration DAG"""

    name: str
    agent_instance: BaseAgent
    dependencies: list[str] = field(default_factory=list)
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_seconds: float = 30.0
    status: AgentStatus = AgentStatus.PENDING
    result: AgentResult | None = None
    error: str | None = None


class OrchestrationEngine:
    """
    Executes agents in dependency order with retries, timeouts, and error handling.
    Maintains PipelineContext as the single source of truth.
    """

    def __init__(self):
        self.agents: dict[str, AgentNode] = {}
        self.execution_order: list[str] = []
        self.logger = logging.getLogger(__name__)

    def register_agent(
        self,
        name: str,
        agent_instance: BaseAgent,
        dependencies: list[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout_seconds: float = 30.0,
    ):
        """Register an agent with its dependencies"""
        self.agents[name] = AgentNode(
            name=name,
            agent_instance=agent_instance,
            dependencies=dependencies or [],
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout_seconds=timeout_seconds,
        )
        self._recalculate_order()

    def _recalculate_order(self):
        """Topological sort to determine execution order"""
        # Simple Kahn's algorithm for topological sorting
        in_degree = {name: 0 for name in self.agents}
        adj = {name: [] for name in self.agents}

        for name, node in self.agents.items():
            for dep in node.dependencies:
                if dep in adj:
                    adj[dep].append(name)
                    in_degree[name] += 1

        # Find nodes with no dependencies
        queue = [name for name, degree in in_degree.items() if degree == 0]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.agents):
            raise ValueError("Circular dependency detected in agent graph")

        self.execution_order = order

    def execute_pipeline(self, initial_context: PipelineContext) -> PipelineContext:
        """
        Execute the full agent pipeline starting with initial context.
        Returns the final context after all agents have processed it.
        """
        context = initial_context
        self.logger.info(
            f"Starting pipeline execution with {len(self.execution_order)} agents"
        )

        for agent_name in self.execution_order:
            agent_node = self.agents[agent_name]
            context = self._execute_agent_with_retry(agent_node, context)
            if agent_node.result and not agent_node.result.success:
                self.logger.error(
                    f"Agent {agent_name} failed: {agent_node.result.error}"
                )
                # Depending on policy, we might continue or stop
                # For now, we continue but log the error
                context.add_error(
                    agent_name, agent_node.result.error or "Unknown error"
                )

        self.logger.info("Pipeline execution completed")
        return context

    def _execute_agent_with_retry(
        self, agent_node: AgentNode, context: PipelineContext
    ) -> PipelineContext:
        """Execute an agent with retry logic"""
        last_error = None

        for attempt in range(agent_node.max_retries + 1):
            try:
                agent_node.status = AgentStatus.RUNNING
                start_time = time.time()

                # Validate dependencies are satisfied
                missing_deps = []
                for dep in agent_node.dependencies:
                    dep_node = self.agents.get(dep)
                    if not dep_node or dep_node.status != AgentStatus.SUCCESS:
                        missing_deps.append(dep)

                if missing_deps:
                    raise ValueError(f"Missing dependencies: {missing_deps}")

                # Execute the agent
                # We pass the context as input; the agent should return an AgentResult
                if hasattr(agent_node.agent_instance, "process"):
                    # Standard BaseAgent interface
                    raw_output = agent_node.agent_instance.process(context)
                else:
                    # Fallback for agents with different interface
                    raw_output = agent_node.agent_instance.run(context)

                # Wrap output in AgentResult if needed
                if isinstance(raw_output, AgentResult):
                    result = raw_output
                elif isinstance(raw_output, dict) and "success" in raw_output:
                    result = AgentResult(**raw_output)
                else:
                    # Assume successful dict output
                    result = AgentResult(
                        success=True,
                        agent_name=agent_node.name,
                        output_data=(
                            raw_output
                            if isinstance(raw_output, dict)
                            else {"result": raw_output}
                        ),
                    )

                # Calculate latency
                result.latency_ms = int((time.time() - start_time) * 1000)

                # Extract context updates if provided
                if hasattr(result, "context_updates") and result.context_updates:
                    context_updates = result.context_updates
                else:
                    # Try to infer context updates from output_data
                    context_updates = self._infer_context_updates(
                        agent_node.name, result.output_data
                    )

                result.context_updates = context_updates
                agent_node.result = result
                agent_node.status = (
                    AgentStatus.SUCCESS if result.success else AgentStatus.FAILED
                )

                if result.success:
                    self.logger.info(
                        f"Agent {agent_node.name} succeeded in {result.latency_ms}ms"
                    )
                    return context.merge_into_context(result)
                else:
                    last_error = result.error or "Unknown error"
                    if attempt < agent_node.max_retries:
                        self.logger.warning(
                            f"Agent {agent_node.name} failed (attempt {attempt+1}), retrying..."
                        )
                        time.sleep(agent_node.retry_delay)
                    else:
                        self.logger.error(
                            f"Agent {agent_node.name} failed after {agent_node.max_retries+1} attempts: {last_error}"
                        )

            except Exception as e:
                last_error = str(e)
                self.logger.error(
                    f"Agent {agent_node.name} crashed: {traceback.format_exc()}"
                )
                if attempt < agent_node.max_retries:
                    self.logger.warning(
                        f"Agent {agent_node.name} crashed (attempt {attempt+1}), retrying..."
                    )
                    time.sleep(agent_node.retry_delay)
                else:
                    self.logger.error(
                        f"Agent {agent_node.name} crashed after {agent_node.max_retries+1} attempts"
                    )

        # All retries exhausted
        agent_node.status = AgentStatus.FAILED
        agent_node.error = last_error
        agent_node.result = AgentResult(
            success=False,
            agent_name=agent_node.name,
            error=last_error,
            recoverable=False,
        )
        context.add_error(agent_node.name, last_error)
        return context

    def _infer_context_updates(self, agent_name: str, output_data: dict) -> dict:
        """
        Infer what parts of the PipelineContext should be updated based on agent name and output.
        This is a heuristic; agents should ideally provide explicit context_updates.
        """
        updates = {}

        # Mapping of agent names to context fields they typically update
        agent_mapping = {
            "TrendHunterAgent": ["trends_data"],
            "ViralAnalystAgent": ["viral_insights"],
            "OriginalityEngineAgent": ["originality_score"],
            "StoryArchitectAgent": ["episode_blueprint", "characters"],
            "CharacterDirectorAgent": ["characters"],
            "MasterWriterAgent": ["beats"],
            "HookEngineAgent": ["beats"],  # Assuming it modifies beats
            "CTAWriterAgent": ["beats"],
            "EpisodeScorerAgent": ["quality_results"],
            "VideoAnimator": ["visual_prompts"],
            "VideoAgent": ["video_results"],
            "VoiceDirectorAgent": ["audio_prompts"],
            "SoundDesignerAgent": ["audio_prompts"],
            "MusicSupervisorAgent": ["audio_prompts"],
            "KeyframeAgent": ["keyframes"],
            "StoryboardAgent": ["storyboards"],
            "VisualAgent": ["visual_direction"],
            "PublisherAgent": ["distribution_schedule"],
            "SEOOptimizerAgent": ["seo_metadata"],
            "AnalyticsEngineAgent": ["analytics_data"],
            "FeedbackLoopAgent": ["feedback_hypotheses"],
            "CreativeGenomeAgent": ["genome_mutations"],
            "QualityGateAgent": ["quality_results"],
        }

        if agent_name in agent_mapping:
            for field in agent_mapping[agent_name]:
                if field in output_data:
                    updates[field] = output_data[field]
                elif field.endswith("_list") or field.endswith("_s"):
                    # Handle plural forms
                    singular = (
                        field[:-1]
                        if field.endswith("s")
                        else field.removesuffix("_list")
                    )
                    if singular in output_data:
                        updates[field] = [output_data[singular]]
                else:
                    # Try direct match
                    if field in output_data:
                        updates[field] = output_data[field]

        return updates

    def get_execution_status(self) -> dict[str, Any]:
        """Get current status of all agents"""
        return {
            name: {
                "status": node.status.value,
                "success": node.result.success if node.result else None,
                "latency_ms": node.result.latency_ms if node.result else None,
                "error": node.error,
            }
            for name, node in self.agents.items()
        }


# Global orchestrator instance
orchestrator = OrchestrationEngine()
