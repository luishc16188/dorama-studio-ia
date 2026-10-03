"""
Video Analyzer & Reference Intelligence Agent - Phase 5
Parses reference videos to extract hooks, beat structures, visual motifs, and audio signatures.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent

from .contracts import (
    AudioSignature,
    AudioSignatureType,
    BeatStructure,
    BeatType,
    HookCategory,
    HookRule,
    ProductionDNA,
    ReferenceAnalysis,
    VisualMotif,
    VisualMotifType,
)

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """
    Analyzes reference videos to extract production DNA.
    In production, this would use:
    - Video understanding models (Video-LLaVA, Gemini, etc.)
    - Audio analysis (librosa, Essentia)
    - Computer vision (OpenCV, MediaPipe)
    - Scene detection (PySceneDetect)
    """

    def __init__(self, cache_dir: str = "data/reference_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Built-in reference database (would be populated from analysis)
        self._reference_db: dict[str, ReferenceAnalysis] = {}
        self._production_dna_cache: dict[str, ProductionDNA] = {}

    def analyze_video(
        self,
        video_path: str,
        video_id: str | None = None,
        video_url: str | None = None,
    ) -> ReferenceAnalysis:
        """
        Analyze a reference video and extract production DNA.

        In production, this would:
        1. Download/load video
        2. Scene detection → beat boundaries
        3. Frame sampling → visual analysis
        4. Audio extraction → audio analysis
        5. Dialogue transcription → hook detection
        6. Scene classification → beat type classification

        For now, returns a structured mock based on known viral patterns.
        """
        if video_id is None:
            video_id = self._generate_video_id(video_path, video_url)

        # Check cache
        cache_file = self.cache_dir / f"{video_id}.json"
        if cache_file.exists():
            with open(cache_file, encoding='utf-8') as f:
                data = json.load(f)
                return ReferenceAnalysis(**data)

        logger.info(f"Analyzing reference video: {video_id}")

        # Mock analysis based on known viral patterns
        # In production, replace with actual video understanding pipeline
        analysis = self._mock_analyze_video(video_id, video_path, video_url)

        # Cache result
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(analysis.model_dump(mode='json'), f, ensure_ascii=False, indent=2)

        return analysis

    def _generate_video_id(self, video_path: str, video_url: str | None) -> str:
        """Generate unique ID for video."""
        source = video_url or video_path
        return hashlib.md5(source.encode()).hexdigest()[:12]

    def _mock_analyze_video(
        self,
        video_id: str,
        video_path: str,
        video_url: str | None,
    ) -> ReferenceAnalysis:
        """Mock analysis returning known viral patterns for K-drama/vertical dorama."""

        # Simulate beat detection (9 beats for 90s)
        beats = []
        beat_configs = [
            {"type": "hook", "start": 0, "end": 10, "hook_category": "visual_shock", "viral_score": 0.95},
            {"type": "context", "start": 10, "end": 20, "hook_category": "impossible_romance", "viral_score": 0.82},
            {"type": "problem", "start": 20, "end": 30, "hook_category": "threat", "viral_score": 0.88},
            {"type": "escalation", "start": 30, "end": 40, "hook_category": "betrayal", "viral_score": 0.91},
            {"type": "twist_1", "start": 40, "end": 50, "hook_category": "identity_shock", "viral_score": 0.97},
            {"type": "conflict_2", "start": 50, "end": 60, "hook_category": "power_reveal", "viral_score": 0.93},
            {"type": "revelation", "start": 60, "end": 70, "hook_category": "revelation", "viral_score": 0.89},
            {"type": "cliffhanger", "start": 70, "end": 80, "hook_category": "moral_dilemma", "viral_score": 0.96},
            {"type": "cta", "start": 80, "end": 90, "hook_category": "question", "viral_score": 0.85},
        ]

        hooks = [
            {
                "category": "visual_shock",
                "pattern": "ECU on impossible object + 40Hz sub-bass",
                "viral_score": 0.95,
                "timestamp": 0.5,
            },
            {
                "category": "identity_shock",
                "pattern": "Character realizes impossible truth via visual cue",
                "viral_score": 0.97,
                "timestamp": 42.0,
            },
            {
                "category": "moral_dilemma",
                "pattern": "Protagonist must choose between two impossible options",
                "viral_score": 0.96,
                "timestamp": 72.0,
            },
        ]

        visual_motifs = [
            {
                "type": "color_palette",
                "name": "Cold Cyan / Warm Gold Split",
                "spec": {"primary": "#00FFFF", "secondary": "#FFD700", "accent": "#FF0000"},
                "emotional_effect": "duality, conflict, premium feel",
                "beats": ["hook", "twist_1", "cliffhanger"],
            },
            {
                "type": "lighting_style",
                "name": "Chiaroscuro Rim Light",
                "spec": {"key_angle": 45, "fill_ratio": 0.1, "rim_intensity": 2.0},
                "emotional_effect": "mystery, isolation, premium",
                "beats": ["hook", "problem", "revelation"],
            },
            {
                "type": "camera_grammar",
                "name": "ECU → Wide Whip Pan",
                "spec": {"transition": "whip_pan", "duration_frames": 3, "direction": "horizontal"},
                "emotional_effect": "disorientation, energy, momentum",
                "beats": ["escalation", "twist_1"],
            },
        ]

        audio_signatures = [
            {
                "type": "silence_drop_pattern",
                "name": "Pre-Revelation Silence",
                "spec": {"duration_sec": 0.5, "fade_curve": "exponential"},
                "trigger": "before critical revelation dialogue",
                "beats": ["twist_1", "revelation", "cliffhanger"],
                "emotional_purpose": "tension building, anticipation",
            },
            {
                "type": "sub_bass_stinger",
                "name": "40Hz Sub-Bass on Cliffhanger",
                "spec": {"frequency_hz": 40, "duration_sec": 0.8, "envelope": "percussive"},
                "trigger": "cliffhanger reveal + visual punch",
                "beats": ["cliffhanger"],
                "emotional_purpose": "shock, suspense, physical impact",
            },
            {
                "type": "music_genre_progression",
                "name": "3-Stage Genre Shift",
                "spec": {
                    "stage_1": {"genre": "dark_ambient", "bpm": 70, "beats": ["hook", "context"]},
                    "stage_2": {"genre": "synthwave_tension", "bpm": 128, "beats": ["problem", "escalation", "twist_1"]},
                    "stage_3": {"genre": "orchestral_epic", "bpm": 90, "beats": ["conflict_2", "revelation", "cliffhanger", "cta"]},
                },
                "trigger": "beat progression",
                "beats": ["all"],
                "emotional_purpose": "emotional arc progression, tension to catharsis",
            },
            {
                "type": "foley_amplification",
                "name": "Premium Object Foley +6dB",
                "spec": {"objects": ["glass", "silk", "watch", "paper"], "gain_db": 6},
                "trigger": "emotional object interaction",
                "beats": ["problem", "twist_1", "revelation"],
                "emotional_purpose": "intimacy, premium feel, emotional grounding",
            },
        ]

        return ReferenceAnalysis(
            video_id=video_id,
            video_url=video_url,
            title="K-Drama Viral Reference",
            platform="TikTok/Reels/Shorts",
            duration_sec=90.0,
            hooks_detected=hooks,
            beats_detected=beats,
            visual_motifs=visual_motifs,
            audio_signatures=audio_signatures,
            viral_potential_score=0.92,
            production_quality_score=0.95,
            originality_score=0.78,
            confidence_score=0.88,
        )

    def extract_production_dna(self, analyses: list[ReferenceAnalysis]) -> ProductionDNA:
        """
        Synthesize multiple reference analyses into unified Production DNA.
        """
        if not analyses:
            return self._default_dna()

        # Aggregate hook rules
        hook_rules = []
        for a in analyses:
            for h in a.hooks_detected:
                hook_rules.append(HookRule(
                    category=HookCategory(h.get("category", "question")),
                    pattern=h.get("pattern", ""),
                    viral_score=h.get("viral_score", 0.5),
                    optimal_position_sec=h.get("timestamp", 0.5),
                ))

        # Deduplicate by category
        unique_hooks = {}
        for h in hook_rules:
            if h.category not in unique_hooks or h.viral_score > unique_hooks[h.category].viral_score:
                unique_hooks[h.category] = h

        # Aggregate visual motifs
        visual_motifs = []
        for a in analyses:
            for v in a.visual_motifs:
                visual_motifs.append(VisualMotif(
                    motif_type=VisualMotifType(v.get("type", "color_palette")),
                    name=v.get("name", ""),
                    description=v.get("emotional_effect", ""),
                    technical_spec=v.get("spec", {}),
                    emotional_effect=v.get("emotional_effect", ""),
                    beat_applicability=v.get("beats", []),
                ))

        # Aggregate audio signatures
        audio_signatures = []
        for a in analyses:
            for s in a.audio_signatures:
                audio_signatures.append(AudioSignature(
                    signature_type=AudioSignatureType(s.get("type", "music_genre_progression")),
                    name=s.get("name", ""),
                    description=s.get("trigger", ""),
                    technical_spec=s.get("spec", {}),
                    trigger_conditions=[s.get("trigger", "")],
                    beat_targets=s.get("beats", []),
                    emotional_purpose=s.get("emotional_purpose", "emotional impact"),
                ))

        # Build standard beat structures
        beat_structures = self._standard_beat_structures()

        return ProductionDNA(
            source_references=[a.video_id for a in analyses],
            genre="romance_traicion",
            subgenre="thriller_romantico",
            hook_rules=list(unique_hooks.values()),
            beat_structures=beat_structures,
            visual_motifs=visual_motifs,
            audio_signatures=audio_signatures,
        )

    def _standard_beat_structures(self) -> list[BeatStructure]:
        """Standard 9-beat structure for 90s vertical dorama."""
        return [
            BeatStructure(
                beat_type=BeatType.HOOK,
                duration_range_sec=(8.0, 12.0),
                required_components=["visual_punch", "audio_punch", "hook_dialogue", "sub_bass"],
                emotional_target="shock",
                information_delta="reveal",
                visual_change_required=True,
                audio_shift_required=True,
                subversion_mandatory=True,
                pattern_interrupts=["silence_drop", "sub_bass_stinger", "ecu_punch"],
            ),
            BeatStructure(
                beat_type=BeatType.CONTEXT,
                duration_range_sec=(8.0, 12.0),
                required_components=["establishing_shot", "character_intro", "world_rules"],
                emotional_target="curiosity",
                information_delta="partial",
                visual_change_required=True,
                audio_shift_required=False,
            ),
            BeatStructure(
                beat_type=BeatType.PROBLEM,
                duration_range_sec=(8.0, 12.0),
                required_components=["inciting_incident", "stakes_established", "character_reaction"],
                emotional_target="tension",
                information_delta="reveal",
                visual_change_required=True,
                audio_shift_required=True,
            ),
            BeatStructure(
                beat_type=BeatType.ESCALATION,
                duration_range_sec=(8.0, 12.0),
                required_components=["complication", "stakes_raise", "character_pressure"],
                emotional_target="urgency",
                information_delta="withhold",
                visual_change_required=True,
                audio_shift_required=True,
                pattern_interrupts=["whip_pan", "music_shift"],
            ),
            BeatStructure(
                beat_type=BeatType.TWIST_1,
                duration_range_sec=(8.0, 12.0),
                required_components=["revelation", "information_delta", "silence_drop", "sub_bass"],
                emotional_target="shock",
                information_delta="reveal",
                visual_change_required=True,
                audio_shift_required=True,
                subversion_mandatory=True,
                pattern_interrupts=["silence_drop", "sub_bass", "ecu_punch"],
            ),
            BeatStructure(
                beat_type=BeatType.CONFLICT_2,
                duration_range_sec=(8.0, 12.0),
                required_components=["new_conflict", "character_choice", "stakes_peak"],
                emotional_target="desperation",
                information_delta="partial",
                visual_change_required=True,
                audio_shift_required=True,
            ),
            BeatStructure(
                beat_type=BeatType.REVELATION,
                duration_range_sec=(8.0, 12.0),
                required_components=["truth_revealed", "character_realization", "emotional_payoff"],
                emotional_target="catharsis",
                information_delta="reveal",
                visual_change_required=True,
                audio_shift_required=True,
            ),
            BeatStructure(
                beat_type=BeatType.CLIFFHANGER,
                duration_range_sec=(8.0, 12.0),
                required_components=["impossible_choice", "visual_punch", "sub_bass", "open_loop"],
                emotional_target="suspense",
                information_delta="withhold",
                visual_change_required=True,
                audio_shift_required=True,
                subversion_mandatory=True,
                pattern_interrupts=["sub_bass", "freeze_frame", "open_question"],
            ),
            BeatStructure(
                beat_type=BeatType.CTA,
                duration_range_sec=(8.0, 12.0),
                required_components=["moral_question", "audience_address", "loop_close"],
                emotional_target="engagement",
                information_delta="question",
                visual_change_required=False,
                audio_shift_required=False,
            ),
        ]

    def _default_dna(self) -> ProductionDNA:
        """Fallback DNA when no references available."""
        return ProductionDNA(
            source_references=[],
            genre="romance_traicion",
            hook_rules=[
                HookRule(category=HookCategory.VISUAL_SHOCK, pattern="ECU impossible object + sub-bass", viral_score=0.95),
                HookRule(category=HookCategory.IDENTITY_SHOCK, pattern="Impossible truth via visual cue", viral_score=0.97),
            ],
            beat_structures=self._standard_beat_structures(),
            visual_motifs=[],
            audio_signatures=[],
        )


class ReferenceIntelligenceAgent(BaseAgent[dict[str, Any], ReferenceAnalysis]):
    """
    Agent that analyzes reference videos and extracts production DNA.
    Integrates with the orchestration pipeline.
    """

    def __init__(self, cache_dir: str = "data/reference_cache"):
        super().__init__("ReferenceIntelligenceAgent")
        self.analyzer = VideoAnalyzer(cache_dir)

    def run(self, input_data: dict[str, Any]) -> ReferenceAnalysis:
        """Run the agent with input data."""
        return self._process(input_data)

    def _process(self, validated_input: dict[str, Any]) -> ReferenceAnalysis:
        """Process reference video analysis request."""
        video_path = validated_input.get("video_path")
        video_url = validated_input.get("video_url")
        video_id = validated_input.get("video_id")

        if not video_path and not video_url:
            raise ValueError("Either video_path or video_url required")

        return self.analyzer.analyze_video(video_path, video_id, video_url)

    def extract_dna(self, video_ids: list[str]) -> ProductionDNA:
        """Extract unified Production DNA from multiple references."""
        analyses = []
        for vid in video_ids:
            cache_file = self.analyzer.cache_dir / f"{vid}.json"
            if cache_file.exists():
                with open(cache_file, encoding='utf-8') as f:
                    data = json.load(f)
                    analyses.append(ReferenceAnalysis(**data))

        return self.analyzer.extract_production_dna(analyses)


# Default instances
default_analyzer = VideoAnalyzer()
default_agent = ReferenceIntelligenceAgent()
