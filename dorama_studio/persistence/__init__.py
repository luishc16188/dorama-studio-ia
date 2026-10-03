"""
Persistence layer for DORAMA STUDIO IA V2.
SQLite-based storage for artifacts, traces, and pipeline state.
"""

from .artifact_store import ArtifactStore
from .init_db import close_db, get_db_info, get_session, init_db, session_scope
from .models import (
    AgentExecution,
    Artifact,
    Base,
    CreativeGenomeUsage,
    EpisodeRun,
    PipelineRun,
    QualityReport,
    Trace,
)
from .repository import (
    AgentExecutionRepository,
    ArtifactRepository,
    CreativeGenomeRepository,
    EpisodeRepository,
    PipelineRepository,
    QualityRepository,
    TraceRepository,
)
from .trace_service import TraceService

__all__ = [
    "Base",
    "Artifact",
    "Trace",
    "PipelineRun",
    "EpisodeRun",
    "QualityReport",
    "AgentExecution",
    "CreativeGenomeUsage",
    "ArtifactRepository",
    "TraceRepository",
    "PipelineRepository",
    "EpisodeRepository",
    "QualityRepository",
    "AgentExecutionRepository",
    "CreativeGenomeRepository",
    "ArtifactStore",
    "TraceService",
    "init_db",
    "get_session",
    "close_db",
    "get_db_info",
    "session_scope",
]
