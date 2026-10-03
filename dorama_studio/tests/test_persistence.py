"""
Tests for DORAMA STUDIO IA V2 persistence layer.
"""

import os
import tempfile

import pytest

from dorama_studio.persistence import (
    AgentExecution,
    AgentExecutionRepository,
    Artifact,
    ArtifactRepository,
    ArtifactStore,
    CreativeGenomeRepository,
    CreativeGenomeUsage,
    EpisodeRepository,
    EpisodeRun,
    PipelineRepository,
    PipelineRun,
    QualityReport,
    QualityRepository,
    Trace,
    TraceRepository,
    TraceService,
    close_db,
    get_db_info,
    get_session,
    init_db,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Initialize database
    init_db(db_path)

    yield db_path

    # Cleanup
    close_db()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def session(temp_db):
    """Get a database session for testing."""
    session = get_session(temp_db)
    yield session
    session.close()


class TestModels:
    """Test model creation and relationships."""

    def test_create_artifact(self, session):
        """Test creating an artifact."""
        artifact = Artifact(
            artifact_id="art_test_001",
            artifact_type="script",
            project_id="proj_001",
            content='{"title": "Test Episode"}',
            metadata_json={"author": "test"}
        )
        session.add(artifact)
        session.commit()

        retrieved = session.query(Artifact).filter_by(artifact_id="art_test_001").first()
        assert retrieved is not None
        assert retrieved.artifact_type == "script"
        assert retrieved.project_id == "proj_001"

    def test_create_trace(self, session):
        """Test creating a trace."""
        trace = Trace(
            trace_id="tr_test_001",
            agent_name="TestAgent",
            run_id="run_001",
            input_data={"param": "value"},
            output_data={"result": "ok"},
            status="success",
            latency_ms=100,
            tokens_used=50
        )
        session.add(trace)
        session.commit()

        retrieved = session.query(Trace).filter_by(trace_id="tr_test_001").first()
        assert retrieved is not None
        assert retrieved.agent_name == "TestAgent"
        assert retrieved.status == "success"

    def test_create_pipeline_run(self, session):
        """Test creating a pipeline run."""
        pipeline = PipelineRun(
            run_id="run_test_001",
            project_id="proj_001",
            season_id="s01",
            status="running",
            total_episodes=30,
            configuration={"genre": "romance"}
        )
        session.add(pipeline)
        session.commit()

        retrieved = session.query(PipelineRun).filter_by(run_id="run_test_001").first()
        assert retrieved is not None
        assert retrieved.project_id == "proj_001"
        assert retrieved.status == "running"

    def test_create_episode_run(self, session):
        """Test creating an episode run."""
        # First create pipeline
        pipeline = PipelineRun(
            run_id="run_test_002",
            project_id="proj_001",
            season_id="s01",
            status="running"
        )
        session.add(pipeline)
        session.flush()

        episode = EpisodeRun(
            run_id="run_test_002",
            pipeline_run_id=pipeline.id,
            episode_number=1,
            episode_id="e01",
            status="running"
        )
        session.add(episode)
        session.commit()

        retrieved = session.query(EpisodeRun).filter_by(episode_id="e01").first()
        assert retrieved is not None
        assert retrieved.episode_number == 1
        assert retrieved.pipeline_run_id == pipeline.id

    def test_create_quality_report(self, session):
        """Test creating a quality report."""
        pipeline = PipelineRun(run_id="run_test_003", project_id="proj_001", status="running")
        session.add(pipeline)
        session.flush()

        episode = EpisodeRun(
            run_id="run_test_003",
            pipeline_run_id=pipeline.id,
            episode_number=1,
            episode_id="e01",
            status="completed"
        )
        session.add(episode)
        session.flush()

        report = QualityReport(
            report_id="qc_test_001",
            episode_run_id=episode.id,
            state="pass",
            score=95.0,
            critical_failures=[],
            issues=["minor timing issue"],
            created_by="QualityCheckAgent"
        )
        session.add(report)
        session.commit()

        retrieved = session.query(QualityReport).filter_by(report_id="qc_test_001").first()
        assert retrieved is not None
        assert retrieved.state == "pass"
        assert retrieved.score == 95.0

    def test_create_agent_execution(self, session):
        """Test creating an agent execution."""
        pipeline = PipelineRun(run_id="run_test_004", project_id="proj_001", status="running")
        session.add(pipeline)
        session.flush()

        episode = EpisodeRun(
            run_id="run_test_004",
            pipeline_run_id=pipeline.id,
            episode_number=1,
            episode_id="e01",
            status="completed"
        )
        session.add(episode)
        session.flush()

        execution = AgentExecution(
            execution_id="ex_test_001",
            agent_name="StoryArchitectAgent",
            episode_run_id=episode.id,
            input_data={"concept": "test"},
            output_data={"blueprint": "created"},
            status="success",
            latency_ms=500,
            tokens_used=1000
        )
        session.add(execution)
        session.commit()

        retrieved = session.query(AgentExecution).filter_by(execution_id="ex_test_001").first()
        assert retrieved is not None
        assert retrieved.agent_name == "StoryArchitectAgent"
        assert retrieved.status == "success"

    def test_create_genome_usage(self, session):
        """Test creating a creative genome usage record."""
        usage = CreativeGenomeUsage(
            usage_id="gen_test_001",
            agent_name="StoryArchitectAgent",
            session_id="sess_001",
            mutation_type="proven",
            seed_identifier="seed_001",
            genre="romance"
        )
        session.add(usage)
        session.commit()

        retrieved = session.query(CreativeGenomeUsage).filter_by(usage_id="gen_test_001").first()
        assert retrieved is not None
        assert retrieved.mutation_type == "proven"
        assert retrieved.genre == "romance"


class TestRepositories:
    """Test repository operations."""

    def test_artifact_repository(self, session):
        """Test ArtifactRepository CRUD operations."""
        repo = ArtifactRepository(session)

        # Create
        artifact = repo.create({
            "artifact_id": "art_repo_001",
            "artifact_type": "video",
            "project_id": "proj_001",
            "content": '{"duration": 90}',
            "season_id": "s01",
            "episode_id": "e01"
        })
        assert artifact.artifact_id == "art_repo_001"

        # Get by ID
        retrieved = repo.get_by_id("art_repo_001")
        assert retrieved is not None
        assert retrieved.artifact_type == "video"

        # Get by project
        artifacts = repo.get_by_project("proj_001")
        assert len(artifacts) == 1

        # Get by season
        artifacts = repo.get_by_season("proj_001", "s01")
        assert len(artifacts) == 1

        # Get by episode
        artifacts = repo.get_by_episode("proj_001", "e01")
        assert len(artifacts) == 1

        # Get by type
        artifacts = repo.get_by_type("video", "proj_001")
        assert len(artifacts) == 1

        # Update
        updated = repo.update("art_repo_001", {"content": '{"duration": 120}'})
        assert updated is not None
        assert updated.content == '{"duration": 120}'

        # Delete
        deleted = repo.delete("art_repo_001")
        assert deleted is True
        assert repo.get_by_id("art_repo_001") is None

    def test_trace_repository(self, session):
        """Test TraceRepository operations."""
        repo = TraceRepository(session)

        # Create
        trace = repo.create({
            "trace_id": "tr_repo_001",
            "agent_name": "TestAgent",
            "run_id": "run_001",
            "input_data": {"test": "input"},
            "output_data": {"test": "output"},
            "status": "success",
            "latency_ms": 200
        })

        # Get by agent
        traces = repo.get_by_agent("TestAgent")
        assert len(traces) == 1

        # Get by run
        traces = repo.get_by_run("run_001")
        assert len(traces) == 1

        # Get failed
        repo.create({
            "trace_id": "tr_repo_002",
            "agent_name": "FailedAgent",
            "run_id": "run_001",
            "input_data": {},
            "status": "failed",
            "error_message": "test error"
        })
        failed = repo.get_failed()
        assert len(failed) == 1
        assert failed[0].agent_name == "FailedAgent"

    def test_pipeline_repository(self, session):
        """Test PipelineRepository operations."""
        repo = PipelineRepository(session)

        # Create
        pipeline = repo.create({
            "run_id": "run_repo_001",
            "project_id": "proj_001",
            "season_id": "s01",
            "status": "running",
            "total_episodes": 10
        })

        # Get by ID
        retrieved = repo.get_by_id("run_repo_001")
        assert retrieved is not None
        assert retrieved.total_episodes == 10

        # Get by project
        pipelines = repo.get_by_project("proj_001")
        assert len(pipelines) == 1

        # Update status
        updated = repo.update_status("run_repo_001", "completed")
        assert updated is not None
        assert updated.status == "completed"
        assert updated.completed_at is not None

    def test_episode_repository(self, session):
        """Test EpisodeRepository operations."""
        repo = EpisodeRepository(session)

        # Create pipeline
        pipeline = PipelineRun(run_id="run_ep_001", project_id="proj_001", status="running")
        session.add(pipeline)
        session.flush()

        # Create episodes
        for i in range(3):
            repo.create({
                "run_id": "run_ep_001",
                "pipeline_run_id": pipeline.id,
                "episode_number": i + 1,
                "episode_id": f"e{i+1:02d}",
                "status": "running"
            })

        # Get by pipeline
        episodes = repo.get_by_pipeline(pipeline.id)
        assert len(episodes) == 3

        # Get by run and number
        ep = repo.get_by_run_and_number("run_ep_001", 2)
        assert ep is not None
        assert ep.episode_number == 2

        # Update status
        updated = repo.update_status("e01", "completed", quality_score=90.0, quality_state="pass")
        assert updated is not None
        assert updated.status == "completed"
        assert updated.quality_score == 90.0

        # Increment retry
        updated = repo.increment_retry("e01")
        assert updated.retry_count == 1

        # Get failed
        repo.update_status("e02", "failed")
        failed = repo.get_failed_episodes("run_ep_001")
        assert len(failed) == 1

    def test_quality_repository(self, session):
        """Test QualityRepository operations."""
        repo = QualityRepository(session)

        # Setup pipeline and episode
        pipeline = PipelineRun(run_id="run_qc_001", project_id="proj_001", status="running")
        session.add(pipeline)
        session.flush()

        episode = EpisodeRun(
            run_id="run_qc_001",
            pipeline_run_id=pipeline.id,
            episode_number=1,
            episode_id="e01",
            status="completed"
        )
        session.add(episode)
        session.flush()

        # Create quality reports
        for i in range(5):
            repo.create({
                "report_id": f"qc_repo_{i:03d}",
                "episode_run_id": episode.id,
                "state": "pass" if i < 4 else "fail",
                "score": 90.0 if i < 4 else 60.0,
                "critical_failures": [] if i < 4 else ["critical failure"],
                "created_by": "QualityCheckAgent"
            })

        # Get pass rate
        stats = repo.get_pass_rate(project_id="proj_001")
        assert stats["total"] == 5
        assert stats["passed"] == 4
        assert stats["failed"] == 1
        assert stats["pass_rate"] == 0.8

    def test_agent_execution_repository(self, session):
        """Test AgentExecutionRepository operations."""
        repo = AgentExecutionRepository(session)

        # Setup
        pipeline = PipelineRun(run_id="run_ae_001", project_id="proj_001", status="running")
        session.add(pipeline)
        session.flush()

        episode = EpisodeRun(
            run_id="run_ae_001",
            pipeline_run_id=pipeline.id,
            episode_number=1,
            episode_id="e01",
            status="completed"
        )
        session.add(episode)
        session.flush()

        # Create executions
        for i in range(3):
            repo.create({
                "execution_id": f"ex_ae_{i:03d}",
                "agent_name": f"Agent{i}",
                "episode_run_id": episode.id,
                "input_data": {"ep": i},
                "output_data": {"result": "ok"},
                "status": "success" if i < 2 else "failed",
                "latency_ms": 100 * (i + 1)
            })

        # Get by episode
        executions = repo.get_by_episode(episode.id)
        assert len(executions) == 3

        # Get by agent
        executions = repo.get_by_agent("Agent0")
        assert len(executions) == 1

        # Get failed
        failed = repo.get_failed_executions(episode.id)
        assert len(failed) == 1

        # Get avg latency
        avg = repo.get_avg_latency("Agent0")
        assert avg == 100.0  # 100ms for Agent0

    def test_creative_genome_repository(self, session):
        """Test CreativeGenomeRepository operations."""
        repo = CreativeGenomeRepository(session)

        # Create usage records
        for i in range(10):
            repo.create({
                "usage_id": f"gen_repo_{i:03d}",
                "agent_name": "StoryArchitectAgent",
                "session_id": "sess_001",
                "mutation_type": "proven" if i < 7 else ("exploration" if i < 9 else "big_bet"),
                "genre": "romance"
            })

        # Get budget status
        status = repo.get_budget_status("StoryArchitectAgent", "romance")
        assert status["used"]["proven"] == 7
        assert status["used"]["exploration"] == 2
        assert status["used"]["big_bet"] == 1
        assert status["remaining"]["proven"] == 63  # 70 - 7
        assert status["remaining"]["exploration"] == 18  # 20 - 2
        assert status["remaining"]["big_bet"] == 9  # 10 - 1

        # Get total usage
        totals = repo.get_total_usage("romance")
        assert totals["proven"] == 7
        assert totals["exploration"] == 2
        assert totals["big_bet"] == 1


class TestArtifactStore:
    """Test ArtifactStore high-level operations."""

    def test_save_and_load_artifact(self, temp_db):
        """Test saving and loading artifacts."""
        session = get_session(temp_db)
        store = ArtifactStore(session)

        # Save artifact
        artifact = store.save_artifact(
            artifact_id="art_store_001",
            artifact_type="script",
            project_id="proj_001",
            content={"title": "Test Episode", "beats": 9},
            season_id="s01",
            episode_id="e01",
            metadata={"author": "test"}
        )
        assert artifact.artifact_id == "art_store_001"

        # Load artifact
        loaded = store.load_artifact("art_store_001")
        assert loaded is not None
        assert loaded.artifact_type == "script"

        # Load content
        content = store.load_artifact_content("art_store_001")
        assert content == {"title": "Test Episode", "beats": 9}

        # Get by project
        artifacts = store.get_artifacts_by_project("proj_001")
        assert len(artifacts) == 1

        session.close()

    def test_update_artifact(self, temp_db):
        """Test updating artifact metadata."""
        session = get_session(temp_db)
        store = ArtifactStore(session)

        store.save_artifact(
            artifact_id="art_store_002",
            artifact_type="video",
            project_id="proj_001",
            content={"url": "http://example.com/video.mp4"}
        )

        updated = store.update_artifact("art_store_002", {"content": {"url": "new_url.mp4"}})
        assert updated is not None

        content = store.load_artifact_content("art_store_002")
        assert content == {"url": "new_url.mp4"}

        session.close()


class TestTraceService:
    """Test TraceService operations."""

    def test_trace_context_manager(self, temp_db):
        """Test trace_agent context manager."""
        session = get_session(temp_db)
        service = TraceService(session)

        # Test successful trace
        with service.trace_agent("TestAgent", run_id="run_test", input_data={"param": "value"}) as trace:
            trace.output_data = {"result": "success"}
            trace.status = "success"
            trace.latency_ms = 100

        traces = service.get_agent_traces("TestAgent")
        assert len(traces) == 1
        assert traces[0].status == "success"
        assert traces[0].output_data == {"result": "success"}

        session.close()

    def test_trace_context_manager_error(self, temp_db):
        """Test trace context manager with error."""
        session = get_session(temp_db)
        service = TraceService(session)

        # Test failed trace
        try:
            with service.trace_agent("FailingAgent", run_id="run_test", input_data={"param": "value"}) as trace:
                raise ValueError("Test error")
        except ValueError:
            pass

        traces = service.get_agent_traces("FailingAgent")
        assert len(traces) == 1
        assert traces[0].status == "failed"
        assert "Test error" in traces[0].error_message

        session.close()

    def test_record_execution(self, temp_db):
        """Test recording agent execution."""
        session = get_session(temp_db)
        service = TraceService(session)

        # Setup episode
        pipeline = PipelineRun(run_id="run_ts_001", project_id="proj_001", status="running")
        session.add(pipeline)
        session.flush()

        episode = EpisodeRun(
            run_id="run_ts_001",
            pipeline_run_id=pipeline.id,
            episode_number=1,
            episode_id="e01",
            status="completed"
        )
        session.add(episode)
        session.flush()

        # Record execution
        execution = service.record_execution(
            agent_name="TestAgent",
            episode_run_id=episode.id,
            input_data={"test": "input"},
            output_data={"result": "ok"},
            status="success",
            latency_ms=150,
            tokens_used=500
        )

        assert execution is not None
        assert execution.status == "success"
        assert execution.latency_ms == 150

        executions = service.get_episode_executions(episode.id)
        assert len(executions) == 1

        session.close()

    def test_performance_summary(self, temp_db):
        """Test performance summary generation."""
        session = get_session(temp_db)
        service = TraceService(session)

        # Setup
        pipeline = PipelineRun(run_id="run_perf_001", project_id="proj_001", status="running")
        session.add(pipeline)
        session.flush()

        episode = EpisodeRun(
            run_id="run_perf_001",
            pipeline_run_id=pipeline.id,
            episode_number=1,
            episode_id="e01",
            status="completed"
        )
        session.add(episode)
        session.flush()

        # Record multiple executions
        for i in range(5):
            service.record_execution(
                agent_name="FastAgent" if i < 3 else "SlowAgent",
                episode_run_id=episode.id,
                input_data={},
                output_data={},
                status="success",
                latency_ms=50 if i < 3 else 200
            )

        summary = service.get_performance_summary()
        assert summary["total_executions"] == 5
        assert "FastAgent" in summary["agents"]
        assert "SlowAgent" in summary["agents"]
        assert summary["agents"]["FastAgent"]["avg_latency_ms"] == 50
        assert summary["agents"]["SlowAgent"]["avg_latency_ms"] == 200

        session.close()


class TestDatabaseFunctions:
    """Test database utility functions."""

    def test_init_db(self, temp_db):
        """Test database initialization."""
        info = get_db_info(temp_db)
        assert info["exists"] is True
        assert info["tables"] is not None
        assert len(info["tables"]) > 0

    def test_get_db_info(self, temp_db):
        """Test getting database info."""
        info = get_db_info(temp_db)
        assert info["exists"] is True
        assert info["size_bytes"] > 0
        assert "artifacts" in info["tables"]
        assert "traces" in info["tables"]
        assert "pipeline_runs" in info["tables"]
        assert "episode_runs" in info["tables"]

    def test_session_scope(self, temp_db):
        """Test session_scope context manager."""
        from dorama_studio.persistence import session_scope

        with session_scope(temp_db) as session:
            artifact = Artifact(
                artifact_id="art_scope_001",
                artifact_type="test",
                project_id="proj_001",
                content="test"
            )
            session.add(artifact)

        # Verify committed
        session2 = get_session(temp_db)
        retrieved = session2.query(Artifact).filter_by(artifact_id="art_scope_001").first()
        assert retrieved is not None
        session2.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
