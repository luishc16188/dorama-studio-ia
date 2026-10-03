#!/usr/bin/env python3
"""
Test de integración: Quality Check + Selective Regeneration.
Verifica que QualityCheckAgent detecta fallos y SelectiveRegenerationAgent genera workaround.
"""

from unittest.mock import patch

import pytest

from dorama_studio.agents.quality_check_agent import QualityCheckAgent
from dorama_studio.agents.selective_regeneration_agent import SelectiveRegenerationAgent
from dorama_studio.contracts.v2_schemas import (
    ActingSpec,
    AudioSpec,
    BeatSpec,
    CameraSpec,
    ContinuitySpec,
    EmotionState,
    EpisodeSpecV2,
    MotionSpec,
    QualityReport,
    QualityState,
    ShotSpec,
)


def _minimal_emotion() -> EmotionState:
    return EmotionState(primary="neutral", intensity=0.5, valence=0.0)


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


class TestQCJudgment:
    """Tests para QC y regeneración selectiva."""

    @pytest.fixture
    def failing_episode(self) -> EpisodeSpecV2:
        """Episodio con problemas de QC (diálogos >10 palabras, shots duplicados)."""
        # Beat con diálogo largo
        beat = BeatSpec(
            beat_id="beat_001",
            start=0.0,
            end=10.0,
            narrative_goal="hook",
            emotion=_minimal_emotion(),
            action="character speaks",
            dialogue_ids=["This dialogue has way more than ten words and should fail QC"],
            acting=_minimal_acting(),
            camera=_minimal_camera(),
            motion=_minimal_motion(),
            audio=_minimal_audio(),
            information_revealed=[],
            information_withheld=[],
            retention_reason="hook"
        )

        # Shots con prompt visual duplicado
        shot1 = ShotSpec(
            shot_id="shot_001",
            beat_id="beat_001",
            start=0.0,
            end=5.0,
            characters=["CHAR_001"],
            location_id="loc_01",
            visual_prompt_ast_id="prompt_duplicate",
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
        shot2 = ShotSpec(
            shot_id="shot_002",
            beat_id="beat_001",
            start=5.0,
            end=10.0,
            characters=["CHAR_001"],
            location_id="loc_01",
            visual_prompt_ast_id="prompt_duplicate",  # DUPLICADO
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

        return EpisodeSpecV2(
            artifact_id="ep_test",
            artifact_type="episode_spec",
            project_id="proj_test",
            season_id="s01",
            episode_id="e01",
            episode_number=1,
            title="Test Episode",
            genre="drama",
            target_duration_sec=90.0,
            hook_id="hook_001",
            blueprint_id="bp_001",
            character_state_ref="cs_001",
            dialogues=[],
            beats=[beat],
            shots=[shot1, shot2],
            continuity=_minimal_continuity(),
            quality=QualityReport(
                state=QualityState.DRAFT,
                score=0.0,
                critical_failures=[],
                issues=[],
                evidence_refs=[]
            ),
            artifact_refs={},
            created_by="test_agent",
        )

    @pytest.fixture
    def passing_episode(self) -> EpisodeSpecV2:
        """Episodio que pasa QC."""
        beat = BeatSpec(
            beat_id="beat_001",
            start=0.0,
            end=10.0,
            narrative_goal="hook",
            emotion=_minimal_emotion(),
            action="character speaks",
            dialogue_ids=["Short dialogue ok"],
            acting=_minimal_acting(),
            camera=_minimal_camera(),
            motion=_minimal_motion(),
            audio=_minimal_audio(),
            information_revealed=[],
            information_withheld=[],
            retention_reason="hook"
        )

        shot = ShotSpec(
            shot_id="shot_001",
            beat_id="beat_001",
            start=0.0,
            end=10.0,
            characters=["CHAR_001"],
            location_id="loc_01",
            visual_prompt_ast_id="prompt_unique",
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

        return EpisodeSpecV2(
            artifact_id="ep_test_pass",
            artifact_type="episode_spec",
            project_id="proj_test",
            season_id="s01",
            episode_id="e01",
            episode_number=1,
            title="Test Episode Pass",
            genre="drama",
            target_duration_sec=90.0,
            hook_id="hook_001",
            blueprint_id="bp_001",
            character_state_ref="cs_001",
            dialogues=[],
            beats=[beat],
            shots=[shot],
            continuity=_minimal_continuity(),
            quality=QualityReport(
                state=QualityState.DRAFT,
                score=0.0,
                critical_failures=[],
                issues=[],
                evidence_refs=[]
            ),
            artifact_refs={},
            created_by="test_agent",
        )

    def test_quality_check_detects_long_dialogue(self, failing_episode: EpisodeSpecV2):
        """QC detecta diálogos >10 palabras."""
        qc = QualityCheckAgent()
        report = qc.process(failing_episode)

        assert report.state == "fail"
        assert any("Dialogue >10 words" in f for f in report.critical_failures)

    def test_quality_check_detects_duplicate_visual_prompt(self, failing_episode: EpisodeSpecV2):
        """QC detecta visual_prompt_ast_id duplicado."""
        qc = QualityCheckAgent()
        report = qc.process(failing_episode)

        assert report.state == "fail"
        assert any("Duplicate visual prompt" in f for f in report.critical_failures)

    def test_quality_check_passes_clean_episode(self, passing_episode: EpisodeSpecV2):
        """Episodio limpio pasa QC."""
        qc = QualityCheckAgent()
        report = qc.process(passing_episode)

        assert report.state == "pass"
        assert len(report.critical_failures) == 0

    def test_selective_regeneration_on_failure(self, failing_episode: EpisodeSpecV2):
        """SelectiveRegenerationAgent actúa cuando QC falla."""
        qc = QualityCheckAgent()
        report = qc.process(failing_episode)

        assert report.state == "fail"

        regen = SelectiveRegenerationAgent()
        # Mock de los engines internos para evitar dependencias externas
        with patch.object(regen.retention_engine, 'process') as mock_ret, \
             patch.object(regen.cliffhanger_engine, 'process') as mock_cliff:

            mock_ret.return_value = {"retention_actions": []}
            mock_cliff.return_value = {"cliffhanger_text": "Regenerated cliffhanger"}

            result = regen.process({
                "quality_report": report,
                "episode": failing_episode
            })

        assert result["status"] == "regenerated"
        assert "retention" in result
        assert "cliffhanger" in result

    def test_selective_regeneration_no_action_on_pass(self, passing_episode: EpisodeSpecV2):
        """No hay regeneración si QC pasa."""
        qc = QualityCheckAgent()
        report = qc.process(passing_episode)

        assert report.state == "pass"

        regen = SelectiveRegenerationAgent()
        result = regen.process({
            "quality_report": report,
            "episode": passing_episode
        })

        assert result["status"] == "no_action_needed"

    def test_multiple_failures_all_reported(self, failing_episode: EpisodeSpecV2):
        """Todos los fallos se reportan, no solo el primero."""
        qc = QualityCheckAgent()
        report = qc.process(failing_episode)

        assert report.state == "fail"
        assert len(report.critical_failures) >= 2  # diálogo largo + prompt duplicado


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
