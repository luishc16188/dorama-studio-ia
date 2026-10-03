"""
Tests for the Beat Contract implementation.
"""

from dorama_studio.contracts.beat import (
    BeatSchema,
    BeatCamera,
    BeatSound,
    FractalStage,
    PatternInterruptType,
    InformationAsymmetryType,
    ShotType,
    CameraAngleType,
    CameraMovementType,
    DialogueDeliveryType,
    MicroExpressionType,
    DialogueEmotionType,
    EpisodeBeats,
    create_beat_template,
    DEFAULT_BEAT_SEQUENCE
)


def test_beat_creation():
    """Test creating a beat with all required fields."""
    camera = BeatCamera(
        shot_type=ShotType.ECU,
        angle=CameraAngleType.LOW_ANGLE,
        movement=CameraMovementType.SLOW_DOLLY_IN,
        lens="85mm f/1.4",
        focus_pull="eyes to ring",
        composition="rule_of_thirds"
    )

    sound = BeatSound(
        ambience="silence",
        sfx=["heartbeat"],
        music_cue={"genre": "tension", "bpm": 60},
        silence_drop=False,
        voice="[Voice: whispered threatening tempo 0.8s pitch -2st: '¿Qué guardas ahí?']"
    )

    beat = BeatSchema(
        beat_id="beat_001",
        beat_name="Hook",
        timestamp="0-10",
        duration_sec=10.0,
        dialogue="¿Qué guardas ahí?",
        dialogue_delivery=DialogueDeliveryType.SUSURRADO_AMENAZANTE,
        micro_expression=MicroExpressionType.CEJA_ARQUEADA,
        dialogue_emotion=DialogueEmotionType.SUSPENSE,
        action="She slowly turns to face the camera",
        camera=camera,
        sound=sound,
        character_emotion={"char_001": "tension"},
        pattern_interrupt=PatternInterruptType.ZOOM_PUNCH,
        curiosity_loop_planted="What is she hiding?",
        information_asymmetry=InformationAsymmetryType.AUDIENCE_KNOWS_LESS,
        subversion_applied="",
        fractal_stage=FractalStage.HOOK,
        continuity_block="genesis",
        character_ids=["char_001", "char_002"],
        negative_prompt="lowres, bad anatomy, worst quality, low quality",
        state_delta={"emotional_state": "tension"},
        validation_rules=["Validate emotional arc consistency"]
    )

    assert beat.beat_id == "beat_001"
    assert beat.beat_name == "Hook"
    assert beat.timestamp == "0-10"
    assert beat.dialogue == "¿Qué guardas ahí?"
    assert beat.fractal_stage == FractalStage.HOOK
    assert beat.character_ids == ["char_001", "char_002"]
    print("✓ Beat creation test passed")


def test_beat_sequence_validation():
    """Test validating a complete episode beat sequence."""
    # Create 9 beats following the default sequence
    beats = []
    character_ids = ["protagonist", "antagonist"]

    for i, beat_info in enumerate(DEFAULT_BEAT_SEQUENCE):
        beat = create_beat_template(
            beat_id=f"beat_{i+1:03d}",
            beat_name=beat_info["beat_name"],
            timestamp=beat_info["timestamp"],
            fractal_stage=beat_info["fractal_stage"],
            character_ids=character_ids
        )
        # Fill in some required fields for testing
        beat.dialogue = f"Dialogue for beat {i+1}"
        beat.action = f"Action for beat {i+1}"
        beat.camera = BeatCamera(
            shot_type=ShotType.MCU,
            angle=CameraAngleType.EYE_LEVEL,
            movement=CameraMovementType.SLOW_DOLLY_IN,
            lens="85mm prime lens f/1.4",
            focus_pull="",
            composition="rule_of_thirds"
        )
        beat.sound = BeatSound(
            ambience="silence",
            sfx=[],
            music_cue={},
            silence_drop=False,
            voice=""
        )
        beat.character_emotion = {}
        beat.pattern_interrupt = PatternInterruptType.RACK_FOCUS
        beat.curiosity_loop_planted = f"Curiosity loop for beat {i+1}"
        beat.information_asymmetry = InformationAsymmetryType.AUDIENCE_KNOWS_MORE
        beat.subversion_applied = "test subversion" if i == 4 else ""  # Twist1 (index 4)
        beat.continuity_block = f"continuity_{i+1}"
        beat.character_ids = ["protagonist", "antagonist"]
        beat.negative_prompt = ""
        beat.state_delta = {}
        beat.validation_rules = []
        beats.append(beat)

    episode_beats = EpisodeBeats(
        episode_id="episode_001",
        episode_number=1,
        beats=beats,
        character_sheets={},
        scene_state_log=[]
    )

    is_valid, errors = episode_beats.validate_beat_sequence()
    assert is_valid, f"Validation failed: {errors}"
    print("✓ Beat sequence validation test passed")


def test_fractal_stage_enum():
    """Test FractalStage enum values."""
    assert FractalStage.HOOK.value == "H"
    assert FractalStage.PROMISE.value == "P"
    assert FractalStage.QUESTION.value == "Q"
    assert FractalStage.ESCALATION.value == "E"
    assert FractalStage.REWARD.value == "R"
    assert FractalStage.NEW_QUESTION.value == "Q2"
    assert FractalStage.CLIFFHANGER.value == "C"
    print("✓ FractalStage enum test passed")


def test_shot_type_enum():
    """Test ShotType enum values."""
    assert ShotType.ECU.value == "ECU"
    assert ShotType.CU.value == "CU"
    assert ShotType.MCU.value == "MCU"
    assert ShotType.MS.value == "MS"
    assert ShotType.MLS.value == "MLS"
    assert ShotType.LS.value == "LS"
    assert ShotType.VLS.value == "VLS"
    assert ShotType.EST.value == "EST"
    print("✓ ShotType enum test passed")


def test_create_beat_template():
    """Test the beat template helper function."""
    beat = create_beat_template(
        beat_id="test_beat",
        beat_name="Test Beat",
        timestamp="00-10",
        fractal_stage=FractalStage.HOOK,
        character_ids=["char_001"]
    )

    assert beat.beat_id == "test_beat"
    assert beat.beat_name == "Test Beat"
    assert beat.timestamp == "00-10"
    assert beat.fractal_stage == FractalStage.HOOK
    assert beat.character_ids == ["char_001"]
    assert beat.dialogue == ""
    assert beat.action == ""
    print("✓ Beat template creation test passed")


if __name__ == "__main__":
    test_beat_creation()
    test_beat_sequence_validation()
    test_fractal_stage_enum()
    test_shot_type_enum()
    test_create_beat_template()
    print("\n🎉 All beat contract tests passed!")