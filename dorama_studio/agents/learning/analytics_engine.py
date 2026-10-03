# dorama_studio/agents/learning/analytics_engine.py
"""
Analytics Engine Agent - Causal Attribution Scientist.
Atribución CAUSAL por EVENTO (shot/línea/personaje/audio/beat).
MAPA DE CALOR frame-by-frame: segundo exacto de caída + QUÉ variable técnica lo causó.
"""

import logging
from collections import defaultdict
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)


class AnalyticsEngineAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Analytics Engine Agent that performs causal attribution analysis.
    """

    InputSchema = dict[str, Any]
    OutputSchema = dict[str, Any]

    def __init__(self):
        super().__init__("AnalyticsEngineAgent")
        self.frame_rate = 24  # Default, will be overridden by metadata

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze performance of published episodes.

        Args:
            validated_input: Dict with published_episodes and project_id

        Returns:
            Dict with analytics results including causal attribution
        """
        published_episodes = validated_input.get("published_episodes", {})
        project_id = validated_input.get("project_id", "unknown")

        logger.info(f"Starting causal attribution analysis for project {project_id}")

        return self.analyze_performance(published_episodes, project_id)

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the analytics engine agent."""
        return self.process(input_data)

    def analyze_performance(self,
                           published_episodes: dict[str, Any],
                           project_id: str) -> dict[str, Any]:
        """
        Analiza rendimiento publicado para crear insights accionables de atribución causal.
        Returns dict con retention_curve, drop_off_points, hook_performance,
        character_engagement, cta_conversion, completion_rate, y benchmark_vs_genre.
        Ahora incluye análisis causal frame-by-frame y mapa de calor de causalidad.
        """
        logger.info(f"Starting causal attribution analysis for project {project_id}")

        # Extract core data
        video_metadata = published_episodes.get("video_metadata", {})
        platform_data = published_episodes.get("platform_analytics", {})
        episode_package = published_episodes.get("episode_package", {})

        # Set frame rate from metadata
        self.frame_rate = video_metadata.get("fps", 24)
        duration_seconds = video_metadata.get("duration_seconds", 0)
        total_frames = int(duration_seconds * self.frame_rate) if duration_seconds else 0

        # Build high-resolution retention timeline (frame-by-frame)
        retention_timeline = self._build_retention_timeline(platform_data, total_frames)

        # Extract all events at frame level
        frame_events = self._extract_frame_events(episode_package, total_frames)

        # Calculate frame-by-frame correlations and causal attributions
        causal_analysis = self._calculate_causal_attribution(
            retention_timeline, frame_events, total_frames
        )

        # Generate optimization recommendations
        optimization_recs = self._generate_causal_optimization_recommendations(
            causal_analysis, episode_package
        )

        # Perform standard analytics (enhanced with causal insights)
        retention_curve = self._build_retention_curve_from_timeline(retention_timeline)
        drop_off_points = self._enhanced_drop_off_points(platform_data, causal_analysis)
        hook_performance = self._analyze_hook_performance(episode_package, causal_analysis)
        character_engagement = self._analyze_character_engagement(episode_package)
        cta_conversion = self._analyze_cta_conversion(platform_data)
        completion_rate = self._calculate_completion_rate(retention_timeline)
        benchmark_vs_genre = self._get_benchmark_vs_genre(published_episodes)

        result = {
            "retention_curve": retention_curve,
            "drop_off_points": drop_off_points,
            "hook_performance": hook_performance,
            "character_engagement": character_engagement,
            "cta_conversion": cta_conversion,
            "completion_rate": completion_rate,
            "benchmark_vs_genre": benchmark_vs_genre,
            # NEW: Causal attribution analysis
            "causal_heatmap": causal_analysis["heatmap_data"],
            "causal_attributions": causal_analysis["attributions"],
            "optimization_recommendations": optimization_recs,
            "analysis_metadata": {
                "total_frames_analyzed": total_frames,
                "frame_rate": self.frame_rate,
                "analysis_confidence": causal_analysis.get("confidence", 0.85)
            }
        }

        logger.info(f"Analysis complete: {len(causal_analysis['attributions'])} causal attributions found")

        return result

    # Helper methods (stubs for now - in real implementation these would have full logic)
    def _build_retention_timeline(self, platform_data: dict, total_frames: int) -> list[float]:
        """Build frame-by-frame retention timeline from platform analytics."""
        # Mock implementation - return array of retention values per frame
        return [0.95 + 0.05 * (1 - i/total_frames) for i in range(total_frames)] if total_frames > 0 else []

    def _extract_frame_events(self, episode_package: dict, total_frames: int) -> dict[int, list[dict]]:
        """Extract all events (shots, dialogue, audio, beats) mapped to frame numbers."""
        events = defaultdict(list)
        beats = episode_package.get("beats", [])
        for i, beat in enumerate(beats):
            start_frame = int((i * 10) * self.frame_rate)
            end_frame = min(int(((i + 1) * 10) * self.frame_rate), total_frames)
            events[start_frame].append({
                "type": "beat_start",
                "beat_name": beat.get("beat_name", f"beat_{i}"),
                "dialogue": beat.get("dialogue", ""),
                "emotion": beat.get("emotion", ""),
                "camera": beat.get("camera", {}),
                "sound": beat.get("sound", {})
            })
            events[end_frame].append({
                "type": "beat_end",
                "beat_name": beat.get("beat_name", f"beat_{i}")
            })
        return events

    def _calculate_causal_attribution(self, retention_timeline: list[float], frame_events: dict[int, list[dict]], total_frames: int) -> dict[str, Any]:
        """Calculate frame-by-frame correlations and causal attributions."""
        # Mock implementation
        attributions = []
        for frame_idx in range(0, total_frames, self.frame_rate * 10):  # Every 10 seconds
            if frame_idx < len(retention_timeline):
                retention = retention_timeline[frame_idx]
                if retention < 0.7:
                    attributions.append({
                        "frame": frame_idx,
                        "second": frame_idx / self.frame_rate,
                        "retention": retention,
                        "cause": "pattern_interrupt_missing",
                        "confidence": 0.8
                    })
        return {
            "heatmap_data": [[retention_timeline[i] if i < len(retention_timeline) else 0 for i in range(total_frames)]],
            "attributions": attributions,
            "confidence": 0.85
        }

    def _generate_causal_optimization_recommendations(self, causal_analysis: dict, episode_package: dict) -> list[dict[str, Any]]:
        """Generate optimization recommendations from causal analysis."""
        recs = []
        for attr in causal_analysis.get("attributions", [])[:3]:
            recs.append({
                "recommendation": f"Add pattern interrupt at second {attr.get('second', 0)}",
                "expected_improvement": "+5-8% retention",
                "difficulty": "medium",
                "confidence": attr.get("confidence", 0.8)
            })
        return recs

    def _build_retention_curve_from_timeline(self, retention_timeline: list[float]) -> dict[str, float]:
        """Build standard retention curve from frame timeline."""
        return {"overall": sum(retention_timeline) / len(retention_timeline) if retention_timeline else 0.75}

    def _enhanced_drop_off_points(self, platform_data: dict, causal_analysis: dict) -> list[dict]:
        """Enhanced drop-off points with causal attribution."""
        return [{"second": a["second"], "retention_drop": 1 - a["retention"], "cause": a["cause"]} for a in causal_analysis.get("attributions", [])]

    def _analyze_hook_performance(self, episode_package: dict, causal_analysis: dict) -> dict[str, Any]:
        """Analyze hook performance with causal insights."""
        beats = episode_package.get("beats", [])
        hook_beat = beats[0] if beats else {}
        return {"hook_retention": 0.85, "has_visual_hook": True, "has_audio_hook": True}

    def _analyze_character_engagement(self, episode_package: dict) -> dict[str, Any]:
        """Analyze character engagement."""
        return {"protagonist": 0.92, "antagonist": 0.85}

    def _analyze_cta_conversion(self, platform_data: dict) -> dict[str, Any]:
        """Analyze CTA conversion."""
        return {"ctr": 0.084, "comment_rate": 0.032}

    def _calculate_completion_rate(self, retention_timeline: list[float]) -> float:
        """Calculate completion rate from retention timeline."""
        return retention_timeline[-1] if retention_timeline else 0.75

    def _get_benchmark_vs_genre(self, published_episodes: dict) -> dict[str, Any]:
        """Get benchmark comparison vs genre."""
        return {"genre_avg_completion": 0.72, "genre_avg_hook": 0.80, "vs_genre": "above_average"}
