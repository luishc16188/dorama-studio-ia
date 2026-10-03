"""
Trace Service - Centralized tracing and monitoring for the pipeline.
Provides structured logging, debugging, and performance analysis capabilities.
"""

import logging
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from .models import AgentExecution, Trace
from .repository import AgentExecutionRepository, TraceRepository

logger = logging.getLogger(__name__)


class TraceService:
    """
    Centralized tracing service for the DORAMA STUDIO pipeline.
    Handles agent execution tracing, performance monitoring, and debugging.
    """

    def __init__(self, session: Session):
        self.session = session
        self.trace_repo = TraceRepository(session)
        self.execution_repo = AgentExecutionRepository(session)

    @contextmanager
    def trace_agent(
        self,
        agent_name: str,
        run_id: str = None,
        episode_run_id: int = None,
        input_data: dict = None
    ):
        """
        Context manager for tracing an agent execution.

        Usage:
            with trace_service.trace_agent("MyAgent", run_id="run_123") as trace:
                trace.input_data = {"key": "value"}
                result = my_agent.run(input_data)
                trace.output_data = result
                trace.status = "success"

        Args:
            agent_name: Name of the agent being traced
            run_id: Optional pipeline run ID
            episode_run_id: Optional episode run ID
            input_data: Optional input data for the trace

        Yields:
            Trace object for recording execution details
        """
        trace_id = f"tr_{uuid.uuid4().hex[:12]}"
        start_time = time.time()

        trace_data = {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "run_id": run_id,
            "input_data": input_data or {},
            "status": "running",
            "created_at": datetime.utcnow()
        }

        trace = self.trace_repo.create(trace_data)

        # Also create agent execution record if episode_run_id provided
        execution = None
        if episode_run_id:
            execution_data = {
                "execution_id": f"ex_{uuid.uuid4().hex[:12]}",
                "agent_name": agent_name,
                "episode_run_id": episode_run_id,
                "input_data": input_data or {},
                "status": "running"
            }
            execution = self.execution_repo.create(execution_data)

        self.session.commit()

        try:
            yield trace
        except Exception as e:
            # Record error
            trace.status = "failed"
            trace.error_message = str(e)
            trace.latency_ms = int((time.time() - start_time) * 1000)

            if execution:
                execution.status = "failed"
                execution.error = str(e)
                execution.latency_ms = int((time.time() - start_time) * 1000)

            self.session.commit()
            raise
        else:
            # Success
            trace.status = "success"
            trace.latency_ms = int((time.time() - start_time) * 1000)

            if execution:
                execution.status = "success"
                execution.latency_ms = int((time.time() - start_time) * 1000)

            self.session.commit()

    def record_execution(
        self,
        agent_name: str,
        episode_run_id: int,
        input_data: dict,
        output_data: dict = None,
        status: str = "success",
        error: str = None,
        latency_ms: int = None,
        tokens_used: int = None,
        model_used: str = None
    ) -> AgentExecution:
        """
        Record an agent execution (alternative to context manager).

        Args:
            agent_name: Name of the agent
            episode_run_id: Episode run ID
            input_data: Input data
            output_data: Optional output data
            status: Execution status (success/failed)
            error: Optional error message
            latency_ms: Optional latency in milliseconds
            tokens_used: Optional token count
            model_used: Optional model identifier

        Returns:
            Created AgentExecution object
        """
        execution_data = {
            "execution_id": f"ex_{uuid.uuid4().hex[:12]}",
            "agent_name": agent_name,
            "episode_run_id": episode_run_id,
            "input_data": input_data,
            "output_data": output_data,
            "status": status,
            "error": error,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "model_used": model_used
        }

        execution = self.execution_repo.create(execution_data)
        self.session.commit()
        return execution

    def record_trace(
        self,
        agent_name: str,
        run_id: str,
        input_data: dict,
        output_data: dict = None,
        status: str = "success",
        error_message: str = None,
        latency_ms: int = None,
        tokens_used: int = None,
        model_used: str = None
    ) -> Trace:
        """
        Record a trace (alternative to context manager).

        Args:
            agent_name: Name of the agent
            run_id: Pipeline run ID
            input_data: Input data
            output_data: Optional output data
            status: Trace status (success/failed/running)
            error_message: Optional error message
            latency_ms: Optional latency in milliseconds
            tokens_used: Optional token count
            model_used: Optional model identifier

        Returns:
            Created Trace object
        """
        trace_data = {
            "trace_id": f"tr_{uuid.uuid4().hex[:12]}",
            "agent_name": agent_name,
            "run_id": run_id,
            "input_data": input_data,
            "output_data": output_data,
            "status": status,
            "error_message": error_message,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "model_used": model_used
        }

        trace = self.trace_repo.create(trace_data)
        self.session.commit()
        return trace

    def get_agent_traces(
        self, agent_name: str, limit: int = 100
    ) -> list[Trace]:
        """Get traces for a specific agent."""
        return self.trace_repo.get_by_agent(agent_name, limit)

    def get_run_traces(self, run_id: str) -> list[Trace]:
        """Get all traces for a pipeline run."""
        return self.trace_repo.get_by_run(run_id)

    def get_failed_traces(self, limit: int = 100) -> list[Trace]:
        """Get recently failed traces."""
        return self.trace_repo.get_failed(limit)

    def get_recent_traces(self, hours: int = 24, limit: int = 500) -> list[Trace]:
        """Get recent traces."""
        return self.trace_repo.get_recent(hours, limit)

    def get_episode_executions(self, episode_run_id: int) -> list[AgentExecution]:
        """Get all agent executions for an episode."""
        return self.execution_repo.get_by_episode(episode_run_id)

    def get_agent_avg_latency(self, agent_name: str, hours: int = 24) -> float | None:
        """Get average latency for an agent."""
        return self.execution_repo.get_avg_latency(agent_name, hours)

    def get_failed_executions(self, episode_run_id: int) -> list[AgentExecution]:
        """Get failed executions for an episode."""
        return self.execution_repo.get_failed_executions(episode_run_id)

    def get_performance_summary(self, hours: int = 24) -> dict[str, Any]:
        """
        Get performance summary for all agents.

        Returns:
            Dictionary with agent performance metrics
        """
        from .models import AgentExecution

        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Query all executions in time range
        executions = self.session.query(AgentExecution).filter(
            AgentExecution.created_at >= cutoff
        ).all()

        if not executions:
            return {"agents": {}, "total_executions": 0}

        # Group by agent
        agent_stats = {}
        for ex in executions:
            if ex.agent_name not in agent_stats:
                agent_stats[ex.agent_name] = {
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "total_latency": 0,
                    "latency_count": 0
                }

            stats = agent_stats[ex.agent_name]
            stats["total"] += 1
            if ex.status == "success":
                stats["success"] += 1
            else:
                stats["failed"] += 1
            if ex.latency_ms:
                stats["total_latency"] += ex.latency_ms
                stats["latency_count"] += 1

        # Calculate derived metrics
        summary = {
            "total_executions": len(executions),
            "agents": {}
        }

        for agent, stats in agent_stats.items():
            summary["agents"][agent] = {
                "total_executions": stats["total"],
                "success_rate": stats["success"] / stats["total"] if stats["total"] > 0 else 0,
                "avg_latency_ms": stats["total_latency"] / stats["latency_count"] if stats["latency_count"] > 0 else None
            }

        return summary

    def export_traces_for_analysis(
        self, run_id: str = None, agent_name: str = None,
        hours: int = 24
    ) -> list[dict[str, Any]]:
        """
        Export traces for external analysis.

        Args:
            run_id: Optional pipeline run filter
            agent_name: Optional agent filter
            hours: Time range

        Returns:
            List of trace dictionaries
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        query = self.session.query(Trace).filter(Trace.created_at >= cutoff)

        if run_id:
            query = query.filter(Trace.run_id == run_id)
        if agent_name:
            query = query.filter(Trace.agent_name == agent_name)

        traces = query.order_by(Trace.created_at).all()

        return [
            {
                "trace_id": t.trace_id,
                "agent_name": t.agent_name,
                "run_id": t.run_id,
                "status": t.status,
                "latency_ms": t.latency_ms,
                "tokens_used": t.tokens_used,
                "model_used": t.model_used,
                "created_at": t.created_at.isoformat(),
                "error_message": t.error_message
            }
            for t in traces
        ]
