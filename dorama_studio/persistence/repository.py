"""
Repository layer for DORAMA STUDIO IA V2.
Provides high-level data access operations.
"""

import json
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from .models import (
    AgentExecution,
    Artifact,
    CreativeGenomeUsage,
    EpisodeRun,
    PipelineRun,
    QualityReport,
    Trace,
)


class BaseRepository:
    """Base repository with common CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()


class ArtifactRepository(BaseRepository):
    """Repository for Artifact operations."""

    def create(self, artifact_data: dict[str, Any]) -> Artifact:
        """Create a new artifact."""
        artifact = Artifact(**artifact_data)
        self.session.add(artifact)
        self.session.flush()
        return artifact

    def get_by_id(self, artifact_id: str) -> Artifact | None:
        """Get artifact by artifact_id."""
        return self.session.query(Artifact).filter(
            Artifact.artifact_id == artifact_id
        ).first()

    def get_by_project(self, project_id: str, limit: int = 100) -> list[Artifact]:
        """Get artifacts by project."""
        return self.session.query(Artifact).filter(
            Artifact.project_id == project_id
        ).order_by(desc(Artifact.created_at)).limit(limit).all()

    def get_by_season(self, project_id: str, season_id: str) -> list[Artifact]:
        """Get artifacts by project and season."""
        return self.session.query(Artifact).filter(
            and_(Artifact.project_id == project_id, Artifact.season_id == season_id)
        ).order_by(desc(Artifact.created_at)).all()

    def get_by_episode(self, project_id: str, episode_id: str) -> list[Artifact]:
        """Get artifacts by project and episode."""
        return self.session.query(Artifact).filter(
            and_(Artifact.project_id == project_id, Artifact.episode_id == episode_id)
        ).order_by(desc(Artifact.created_at)).all()

    def get_by_type(self, artifact_type: str, project_id: str = None) -> list[Artifact]:
        """Get artifacts by type, optionally filtered by project."""
        query = self.session.query(Artifact).filter(Artifact.artifact_type == artifact_type)
        if project_id:
            query = query.filter(Artifact.project_id == project_id)
        return query.order_by(desc(Artifact.created_at)).all()

    def update(self, artifact_id: str, updates: dict[str, Any]) -> Artifact | None:
        """Update an artifact."""
        artifact = self.get_by_id(artifact_id)
        if artifact:
            for key, value in updates.items():
                if hasattr(artifact, key):
                    # Serialize dict/list to JSON for content and metadata_json fields
                    if key in ('content', 'metadata_json') and isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)
                    setattr(artifact, key, value)
            artifact.updated_at = datetime.utcnow()
            self.session.flush()
        return artifact

    def delete(self, artifact_id: str) -> bool:
        """Delete an artifact."""
        artifact = self.get_by_id(artifact_id)
        if artifact:
            self.session.delete(artifact)
            self.session.flush()
            return True
        return False


class TraceRepository(BaseRepository):
    """Repository for Trace operations."""

    def create(self, trace_data: dict[str, Any]) -> Trace:
        """Create a new trace."""
        trace = Trace(**trace_data)
        self.session.add(trace)
        self.session.flush()
        return trace

    def get_by_id(self, trace_id: str) -> Trace | None:
        """Get trace by trace_id."""
        return self.session.query(Trace).filter(Trace.trace_id == trace_id).first()

    def get_by_agent(self, agent_name: str, limit: int = 100) -> list[Trace]:
        """Get traces by agent name."""
        return self.session.query(Trace).filter(
            Trace.agent_name == agent_name
        ).order_by(desc(Trace.created_at)).limit(limit).all()

    def get_by_run(self, run_id: str) -> list[Trace]:
        """Get traces by run_id."""
        return self.session.query(Trace).filter(
            Trace.run_id == run_id
        ).order_by(Trace.created_at).all()

    def get_failed(self, limit: int = 100) -> list[Trace]:
        """Get failed traces."""
        return self.session.query(Trace).filter(
            Trace.status == "failed"
        ).order_by(desc(Trace.created_at)).limit(limit).all()

    def get_recent(self, hours: int = 24, limit: int = 500) -> list[Trace]:
        """Get recent traces within hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.session.query(Trace).filter(
            Trace.created_at >= cutoff
        ).order_by(desc(Trace.created_at)).limit(limit).all()


class PipelineRepository(BaseRepository):
    """Repository for PipelineRun operations."""

    def create(self, pipeline_data: dict[str, Any]) -> PipelineRun:
        """Create a new pipeline run."""
        pipeline = PipelineRun(**pipeline_data)
        self.session.add(pipeline)
        self.session.flush()
        return pipeline

    def get_by_id(self, run_id: str) -> PipelineRun | None:
        """Get pipeline run by run_id."""
        return self.session.query(PipelineRun).filter(
            PipelineRun.run_id == run_id
        ).first()

    def get_by_project(self, project_id: str, status: str = None) -> list[PipelineRun]:
        """Get pipeline runs by project."""
        query = self.session.query(PipelineRun).filter(
            PipelineRun.project_id == project_id
        )
        if status:
            query = query.filter(PipelineRun.status == status)
        return query.order_by(desc(PipelineRun.started_at)).all()

    def get_by_season(self, season_id: str) -> list[PipelineRun]:
        """Get pipeline runs by season."""
        return self.session.query(PipelineRun).filter(
            PipelineRun.season_id == season_id
        ).order_by(desc(PipelineRun.started_at)).all()

    def update_status(self, run_id: str, status: str) -> PipelineRun | None:
        """Update pipeline run status."""
        pipeline = self.get_by_id(run_id)
        if pipeline:
            pipeline.status = status
            if status in ("completed", "failed"):
                pipeline.completed_at = datetime.utcnow()
            self.session.flush()
        return pipeline


class EpisodeRepository(BaseRepository):
    """Repository for EpisodeRun operations."""

    def create(self, episode_data: dict[str, Any]) -> EpisodeRun:
        """Create a new episode run."""
        episode = EpisodeRun(**episode_data)
        self.session.add(episode)
        self.session.flush()
        return episode

    def get_by_id(self, episode_id: str) -> EpisodeRun | None:
        """Get episode run by episode_id."""
        return self.session.query(EpisodeRun).filter(
            EpisodeRun.episode_id == episode_id
        ).first()

    def get_by_pipeline(self, pipeline_run_id: int) -> list[EpisodeRun]:
        """Get episodes by pipeline run."""
        return self.session.query(EpisodeRun).filter(
            EpisodeRun.pipeline_run_id == pipeline_run_id
        ).order_by(EpisodeRun.episode_number).all()

    def get_by_run_and_number(self, run_id: str, episode_number: int) -> EpisodeRun | None:
        """Get episode by run_id and episode_number."""
        return self.session.query(EpisodeRun).filter(
            and_(EpisodeRun.run_id == run_id, EpisodeRun.episode_number == episode_number)
        ).first()

    def update_status(self, episode_id: str, status: str,
                      quality_score: float = None, quality_state: str = None) -> EpisodeRun | None:
        """Update episode run status."""
        episode = self.get_by_id(episode_id)
        if episode:
            episode.status = status
            if quality_score is not None:
                episode.quality_score = quality_score
            if quality_state is not None:
                episode.quality_state = quality_state
            if status in ("completed", "failed"):
                episode.completed_at = datetime.utcnow()
            self.session.flush()
        return episode

    def increment_retry(self, episode_id: str) -> EpisodeRun | None:
        """Increment retry count."""
        episode = self.get_by_id(episode_id)
        if episode:
            episode.retry_count += 1
            self.session.flush()
        return episode

    def get_failed_episodes(self, run_id: str) -> list[EpisodeRun]:
        """Get failed episodes in a pipeline run."""
        return self.session.query(EpisodeRun).filter(
            and_(EpisodeRun.run_id == run_id, EpisodeRun.status == "failed")
        ).all()


class QualityRepository(BaseRepository):
    """Repository for QualityReport operations."""

    def create(self, quality_data: dict[str, Any]) -> QualityReport:
        """Create a new quality report."""
        report = QualityReport(**quality_data)
        self.session.add(report)
        self.session.flush()
        return report

    def get_by_id(self, report_id: str) -> QualityReport | None:
        """Get quality report by report_id."""
        return self.session.query(QualityReport).filter(
            QualityReport.report_id == report_id
        ).first()

    def get_by_episode(self, episode_run_id: int) -> list[QualityReport]:
        """Get quality reports by episode run."""
        return self.session.query(QualityReport).filter(
            QualityReport.episode_run_id == episode_run_id
        ).order_by(desc(QualityReport.created_at)).all()

    def get_latest_by_episode(self, episode_run_id: int) -> QualityReport | None:
        """Get latest quality report for an episode."""
        return self.session.query(QualityReport).filter(
            QualityReport.episode_run_id == episode_run_id
        ).order_by(desc(QualityReport.created_at)).first()

    def get_pass_rate(self, project_id: str = None, season_id: str = None) -> dict[str, Any]:
        """Get pass/fail statistics."""
        query = self.session.query(QualityReport)

        if project_id or season_id:
            # Need to join with EpisodeRun and PipelineRun
            from .models import EpisodeRun, PipelineRun
            query = query.join(EpisodeRun).join(PipelineRun)
            if project_id:
                query = query.filter(PipelineRun.project_id == project_id)
            if season_id:
                query = query.filter(PipelineRun.season_id == season_id)

        total = query.count()
        passed = query.filter(QualityReport.state == "pass").count()
        failed = query.filter(QualityReport.state == "fail").count()

        avg_score = query.with_entities(func.avg(QualityReport.score)).scalar() or 0.0

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "avg_score": float(avg_score)
        }


class AgentExecutionRepository(BaseRepository):
    """Repository for AgentExecution operations."""

    def create(self, execution_data: dict[str, Any]) -> AgentExecution:
        """Create a new agent execution record."""
        execution = AgentExecution(**execution_data)
        self.session.add(execution)
        self.session.flush()
        return execution

    def get_by_episode(self, episode_run_id: int) -> list[AgentExecution]:
        """Get all agent executions for an episode."""
        return self.session.query(AgentExecution).filter(
            AgentExecution.episode_run_id == episode_run_id
        ).order_by(AgentExecution.created_at).all()

    def get_by_agent(self, agent_name: str, limit: int = 100) -> list[AgentExecution]:
        """Get executions by agent name."""
        return self.session.query(AgentExecution).filter(
            AgentExecution.agent_name == agent_name
        ).order_by(desc(AgentExecution.created_at)).limit(limit).all()

    def get_failed_executions(self, episode_run_id: int) -> list[AgentExecution]:
        """Get failed executions for an episode."""
        return self.session.query(AgentExecution).filter(
            and_(
                AgentExecution.episode_run_id == episode_run_id,
                AgentExecution.status == "failed"
            )
        ).all()

    def get_avg_latency(self, agent_name: str, hours: int = 24) -> float | None:
        """Get average latency for an agent."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        result = self.session.query(func.avg(AgentExecution.latency_ms)).filter(
            and_(
                AgentExecution.agent_name == agent_name,
                AgentExecution.created_at >= cutoff,
                AgentExecution.status == "success",
                AgentExecution.latency_ms.isnot(None)
            )
        ).scalar()
        return float(result) if result else None


class CreativeGenomeRepository(BaseRepository):
    """Repository for CreativeGenomeUsage operations."""

    def create(self, usage_data: dict[str, Any]) -> CreativeGenomeUsage:
        """Create a new genome usage record."""
        usage = CreativeGenomeUsage(**usage_data)
        self.session.add(usage)
        self.session.flush()
        return usage

    def get_by_agent(self, agent_name: str) -> list[CreativeGenomeUsage]:
        """Get usage by agent."""
        return self.session.query(CreativeGenomeUsage).filter(
            CreativeGenomeUsage.agent_name == agent_name
        ).order_by(desc(CreativeGenomeUsage.used_at)).all()

    def get_by_session(self, session_id: str) -> list[CreativeGenomeUsage]:
        """Get usage by session."""
        return self.session.query(CreativeGenomeUsage).filter(
            CreativeGenomeUsage.session_id == session_id
        ).order_by(CreativeGenomeUsage.used_at).all()

    def get_by_genre(self, genre: str) -> list[CreativeGenomeUsage]:
        """Get usage by genre."""
        return self.session.query(CreativeGenomeUsage).filter(
            CreativeGenomeUsage.genre == genre
        ).order_by(desc(CreativeGenomeUsage.used_at)).all()

    def get_budget_status(self, agent_name: str, genre: str = None) -> dict[str, int]:
        """Get remaining budget for agent/genre combination."""
        query = self.session.query(CreativeGenomeUsage).filter(
            CreativeGenomeUsage.agent_name == agent_name
        )
        if genre:
            query = query.filter(CreativeGenomeUsage.genre == genre)

        usage = query.all()

        counts = {"proven": 0, "exploration": 0, "big_bet": 0}
        for u in usage:
            if u.mutation_type in counts:
                counts[u.mutation_type] += 1

        # Limits per agent per genre (70/20/10)
        limits = {"proven": 70, "exploration": 20, "big_bet": 10}

        return {
            "used": counts,
            "limits": limits,
            "remaining": {
                k: limits[k] - counts.get(k, 0)
                for k in limits
            }
        }

    def get_total_usage(self, genre: str = None) -> dict[str, int]:
        """Get total usage across all agents."""
        query = self.session.query(CreativeGenomeUsage)
        if genre:
            query = query.filter(CreativeGenomeUsage.genre == genre)

        usage = query.all()

        totals = {"proven": 0, "exploration": 0, "big_bet": 0}
        for u in usage:
            if u.mutation_type in totals:
                totals[u.mutation_type] += 1

        return totals
