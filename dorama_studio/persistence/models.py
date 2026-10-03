"""
SQLAlchemy models for DORAMA STUDIO IA V2 persistence layer.
Defines all database tables and relationships.
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Artifact(Base):
    """Stored artifacts (scripts, videos, audio, etc.)"""
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    artifact_id = Column(String(100), unique=True, nullable=False, index=True)
    artifact_type = Column(String(50), nullable=False, index=True)
    project_id = Column(String(50), nullable=False, index=True)
    season_id = Column(String(50), nullable=True, index=True)
    episode_id = Column(String(50), nullable=True, index=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_artifact_project_season', 'project_id', 'season_id'),
        Index('idx_artifact_project_episode', 'project_id', 'episode_id'),
    )

class Trace(Base):
    """Execution traces for debugging and monitoring"""
    __tablename__ = "traces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(50), unique=True, nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    run_id = Column(String(100), nullable=True, index=True)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, index=True)  # success, failed, running
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_trace_agent_status', 'agent_name', 'status'),
        Index('idx_trace_run_id', 'run_id'),
    )

class PipelineRun(Base):
    """Pipeline execution records"""
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    project_id = Column(String(50), nullable=False, index=True)
    season_id = Column(String(50), nullable=True, index=True)
    status = Column(String(20), nullable=False, index=True)  # running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    total_episodes = Column(Integer, default=0)
    completed_episodes = Column(Integer, default=0)
    configuration = Column(JSON, nullable=True)

    __table_args__ = (
        Index('idx_pipeline_project_status', 'project_id', 'status'),
        Index('idx_pipeline_season_status', 'season_id', 'status'),
    )

class EpisodeRun(Base):
    """Individual episode execution records"""
    __tablename__ = "episode_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), nullable=False, index=True)
    pipeline_run_id = Column(Integer, ForeignKey('pipeline_runs.id'), nullable=False)
    episode_number = Column(Integer, nullable=False)
    episode_id = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)  # running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    quality_score = Column(Float, nullable=True)
    quality_state = Column(String(20), nullable=True)  # pass, fail
    retry_count = Column(Integer, default=0)
    artifacts_generated = Column(JSON, nullable=True)  # List of artifact IDs

    # Relationships
    pipeline_run = relationship("PipelineRun", backref="episode_runs")

    __table_args__ = (
        Index('idx_episode_pipeline_run', 'pipeline_run_id'),
        Index('idx_episode_run_status', 'run_id', 'status'),
        Index('idx_episode_number', 'episode_number'),
        UniqueConstraint('pipeline_run_id', 'episode_number', name='uq_episode_pipeline_number'),
    )

class QualityReport(Base):
    """Quality check results"""
    __tablename__ = "quality_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    episode_run_id = Column(Integer, ForeignKey('episode_runs.id'), nullable=False)
    state = Column(String(20), nullable=False, index=True)  # pass, fail
    score = Column(Float, nullable=False)
    critical_failures = Column(JSON, nullable=True)  # List of failure descriptions
    issues = Column(JSON, nullable=True)  # List of warnings/issues
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    episode_run = relationship("EpisodeRun", backref="quality_reports")

    __table_args__ = (
        Index('idx_quality_episode_run', 'episode_run_id'),
        Index('idx_quality_state_score', 'state', 'score'),
    )

class AgentExecution(Base):
    """Individual agent execution records"""
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(100), unique=True, nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    episode_run_id = Column(Integer, ForeignKey('episode_runs.id'), nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, index=True)  # success, failed
    error = Column(Text, nullable=True)
    recoverable = Column(Boolean, default=True)
    latency_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    episode_run = relationship("EpisodeRun", backref="agent_executions")

    __table_args__ = (
        Index('idx_agent_exec_episode', 'episode_run_id'),
        Index('idx_agent_exec_name_status', 'agent_name', 'status'),
        Index('idx_agent_exec_created', 'created_at'),
    )

class CreativeGenomeUsage(Base):
    """Creative Genome budget tracking"""
    __tablename__ = "creative_genome_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usage_id = Column(String(100), unique=True, nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    mutation_type = Column(String(20), nullable=False, index=True)  # proven, exploration, big_bet
    seed_identifier = Column(String(100), nullable=True)
    genre = Column(String(50), nullable=True, index=True)
    used_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_genome_agent_type', 'agent_name', 'mutation_type'),
        Index('idx_genome_session', 'session_id'),
        Index('idx_genome_genre', 'genre'),
    )
