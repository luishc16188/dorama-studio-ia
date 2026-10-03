#!/usr/bin/env python3
"""
Test de integración: Video Render Pipeline.
Verifica que VideoAgent + VisualEngine producen un VideoArtifact válido.
"""


import pytest

from dorama_studio.agents.visual_engine import VisualEngineAgent
from dorama_studio.contracts.v2_schemas import (
    ActingSpec,
    AudioSpec,
    CameraSpec,
    ContinuitySpec,
    MotionSpec,
    ShotSpec,
    VideoArtifact,
)


def _minimal_acting() -> ActingSpec:
    return ActingSpec(
        facial_intent="neutral",
        gaze_target=None,
        blink_pattern=None,
        breathing=None,
        posture=None,
        gesture=None,
        micro_expression=None,
    )


def _minimal_camera() -> CameraSpec:
    return CameraSpec(
        shot_type="MS",
        framing="center",
        angle="eye_level",
        lens_language=None,
        movement=None,
        eyeline=None,
        depth_layers=[],
    )


def _minimal_motion() -> MotionSpec:
    return MotionSpec(
        primary="static",
        secondary=[],
        micro=[],
        environmental=[],
    )


def _minimal_continuity() -> ContinuitySpec:
    return ContinuitySpec(
        wardrobe_state=None,
        prop_state={},
        physical_state={},
        location_state=None,
        time_state=None,
        blocked_reveals=[],
    )


def _minimal_audio() -> AudioSpec:
    return AudioSpec(
        dialogue_ids=[],
        ambience=[],
        foley=[],
        sfx=[],
        music_state="none",
        silence_window=False,
    )


class TestVideoRender:
    """Tests para el pipeline de render de video."""

    @pytest.fixture
    def sample_shot(self) -> ShotSpec:
        """Crea un ShotSpec de prueba."""
        return ShotSpec(
            shot_id="test_shot_001",
            beat_id="beat_001",
            start=0.0,
            end=5.0,
            characters=["CHAR_001"],
            location_id="loc_01",
            visual_prompt_ast_id="prompt_001",
            acting=_minimal_acting(),
            camera=_minimal_camera(),
            motion=_minimal_motion(),
            continuity=_minimal_continuity(),
            audio=_minimal_audio(),
            required_reference_ids=[],
            forbidden_elements=[],
            project_id="proj_test",
            season_id="s01",
            episode_id="e01",
        )

    def test_visual_engine_creates_artifact(self, sample_shot: ShotSpec):
        """Verifica que VisualEngineAgent genera VideoArtifact."""
        engine = VisualEngineAgent(provider="test")
        artifact = engine.process(sample_shot)

        assert isinstance(artifact, VideoArtifact)
        assert artifact.shot_id == sample_shot.shot_id
        assert artifact.project_id == "proj_test"  # ShotSpec doesn't have project_id
        assert artifact.duration_sec == 5.0
        assert artifact.uri.startswith("file://")
        assert artifact.codec == "h264"

    def test_artifact_has_required_fields(self, sample_shot: ShotSpec):
        """Verifica que el artifact tiene todos los campos requeridos V2."""
        engine = VisualEngineAgent()
        artifact = engine.process(sample_shot)

        # Campos base artifact
        assert artifact.artifact_id.startswith("art_vid_")
        assert artifact.artifact_type == "video_artifact"
        assert artifact.quality_state.value in ["draft", "review", "pass", "fail"]
        assert artifact.data_origin.value in ["observed", "inferred", "synthetic", "generated"]

    def test_multiple_shots_produce_unique_artifacts(self, sample_shot: ShotSpec):
        """Cada shot produce artifact único."""
        engine = VisualEngineAgent()
        artifacts = []

        for i in range(3):
            shot = ShotSpec(
                shot_id=f"shot_{i}",
                beat_id=f"beat_{i}",
                start=float(i * 5),
                end=float((i + 1) * 5),
                characters=["CHAR_001"],
                location_id="loc_01",
                visual_prompt_ast_id=f"prompt_{i}",
                acting=_minimal_acting(),
                camera=_minimal_camera(),
                motion=_minimal_motion(),
                continuity=_minimal_continuity(),
                audio=_minimal_audio(),
                project_id="proj_test",
                season_id="s01",
                episode_id="e01",
            )
            artifacts.append(engine.process(shot))

        # Todos únicos
        ids = [a.artifact_id for a in artifacts]
        assert len(set(ids)) == 3

        # Duraciones correctas
        for a in artifacts:
            assert a.duration_sec == 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
