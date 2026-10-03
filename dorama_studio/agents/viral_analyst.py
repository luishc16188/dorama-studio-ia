"""
Viral Analyst Agent (Agent 2) - Analyzes viral content patterns.
"""
import logging
import random
from collections import deque
from datetime import datetime
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.viral_analyst_schemas import (
    ViralAnalystInput,
    ViralAnalystOutput,
)

logger = logging.getLogger(__name__)


class ViralAnalystAgent(BaseAgent[ViralAnalystInput, ViralAnalystOutput]):
    """
    Agent 2: Viral Analyst
    Analyzes TrendSignal and predicts viral potential with hook categories.
    """

    def __init__(self):
        super().__init__("ViralAnalystAgent")

        # Hook categories from quality.yaml
        self.hook_categories = deque([
            "revelation", "threat", "betrayal", "humiliation",
            "power", "identity", "prohibition", "mystery",
            "impossible_romance", "revenge", "visual_shock", "question"
        ], maxlen=20)

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the viral analyst agent."""
        result = self.process(input_data)
        # Return dict-like object with payload attribute for test compatibility
        class ResultWrapper:
            def __init__(self, payload):
                self.payload = payload
            def get(self, key, default=None):
                if isinstance(self.payload, dict):
                    return self.payload.get(key, default)
                return default
            def __getitem__(self, key):
                if isinstance(self.payload, dict):
                    return self.payload[key]
                raise KeyError(key)
            def __contains__(self, key):
                if isinstance(self.payload, dict):
                    return key in self.payload
                return False
        return ResultWrapper(result)

    def _process(self, validated_input: ViralAnalystInput) -> ViralAnalystOutput:
        """
        Analyze viral potential from trend signal.

        Args:
            validated_input: Contains 'trend_signal' and optional 'historical_data'.

        Returns:
            ViralAnalystOutput with viral potential analysis.
        """
        try:
            trend_signal = validated_input.trend_signal
            if not trend_signal:
                raise ValueError("trend_signal required")

            # Analyze viral potential
            viral_potential = self._analyze_viral_potential(trend_signal)

            return ViralAnalystOutput(
                trend_id=viral_potential.trend_id,
                viral_score=viral_potential.viral_score,
                hook_categories=viral_potential.hook_categories,
                target_demographic=viral_potential.target_demographic,
                estimated_reach=viral_potential.estimated_reach,
                confidence=viral_potential.confidence,
                key_angles=viral_potential.key_angles,
                risk_factors=viral_potential.risk_factors,
                recommended_format=viral_potential.recommended_format,
                status="completed"
            )

        except Exception as e:
            logger.error(f"Viral analysis failed: {e!s}")
            return ViralAnalystOutput(
                trend_id="",
                viral_score=0,
                hook_categories=[],
                target_demographic="",
                estimated_reach=0,
                confidence=0.0,
                key_angles=[],
                risk_factors=[],
                recommended_format="",
                status="error"
            )

    def _analyze_viral_potential(self, trend_signal: dict[str, Any]):
        """Analyze trend signal and predict viral potential."""

        # Create a simple object to hold the analysis
        class ViralPotentialResult:
            pass

        result = ViralPotentialResult()
        result.trend_id = trend_signal.get("trend_id", f"TR-{datetime.now().strftime('%Y')}-{random.randint(100000, 999999):06d}")

        # Score based on growth rate and saturation
        base_score = min(100, int(trend_signal.get("growth_rate_pct", 50) * 1.2))

        # Saturation adjustment
        saturation_bonus = {
            "emerging": 15,
            "growing": 10,
            "mature": 0,
            "declining": -20
        }
        adjusted_score = base_score + saturation_bonus.get(trend_signal.get("saturation_level", "emerging"), 0)
        adjusted_score = max(0, min(100, adjusted_score))

        # Select hook categories based on trend sentiment and topic
        hook_categories = self._select_hook_categories(trend_signal)

        # Estimate reach
        estimated_reach = int(adjusted_score * 10000)

        # Confidence based on saturation and sentiment
        confidence = 0.8 if trend_signal.get("saturation_level") in ["emerging", "growing"] else 0.6

        # Key angles for the story
        key_angles = self._generate_key_angles(trend_signal)

        # Risk factors
        risk_factors = self._identify_risks(trend_signal)

        # Recommended format
        recommended_format = self._recommend_format(adjusted_score)

        # Add all attributes to result object
        result.viral_score = adjusted_score
        result.hook_categories = hook_categories
        result.target_demographic = trend_signal.get("demographic_hint", "Young adults 18-34")
        result.estimated_reach = estimated_reach
        result.confidence = confidence
        result.key_angles = key_angles
        result.risk_factors = risk_factors
        result.recommended_format = recommended_format

        return result

    def _select_hook_categories(self, trend_signal: dict[str, Any]) -> list[str]:
        """Select top 3 hook categories based on trend."""
        # Map sentiment and topic to hook categories
        sentiment_map = {
            "positive": ["revelation", "impossible_romance", "power", "identity"],
            "negative": ["threat", "betrayal", "humiliation", "revenge", "mystery"],
            "neutral": ["question", "prohibition", "visual_shock", "power"]
        }

        base_categories = sentiment_map.get(trend_signal.get("sentiment", "neutral"), ["question", "mystery"])

        # Add trending categories based on growth
        if trend_signal.get("growth_rate_pct", 0) > 50:
            base_categories.extend(["visual_shock", "revelation"])

        # Select top 3 unique
        unique = []
        for cat in base_categories:
            if cat not in unique and len(unique) < 3:
                unique.append(cat)

        # Ensure we have 3
        while len(unique) < 3:
            for cat in self.hook_categories:
                if cat not in unique:
                    unique.append(cat)
                    break

        return unique[:3]

    def _generate_key_angles(self, trend_signal: dict[str, Any]) -> list[str]:
        """Generate key narrative angles for the story."""
        angles = deque()

        # Angle based on topic
        trend_text = trend_signal.get("trend", "").upper()
        if "IA" in trend_text or "AI" in trend_text:
            angles.append("Tecnología vs Humanidad")
            angles.append("Identidad digital")

        if "romance" in trend_text.lower():
            angles.append("Amor imposible")
            angles.append("Segunda oportunidad")

        if "misterio" in trend_text.lower() or "secreto" in trend_text.lower():
            angles.append("Revelación impactante")
            angles.append("Investigación personal")

        # Default angles if none matched
        if not angles:
            angles = deque([
                "Desafío personal transformador",
                "Relación prohibida",
                "Venganza justificada"
            ], maxlen=20)

        return angles[:5]  # Max 5

    def _identify_risks(self, trend_signal: dict[str, Any]) -> list[str]:
        """Identify risk factors for the viral potential."""
        risks = []

        if trend_signal.get("saturation_level") == "declining":
            risks.append("Tendencia en declive - puede no sostener interés")

        if trend_signal.get("growth_rate_pct", 0) > 100:
            risks.append("Crecimiento explosivo - riesgo de saturación rápida")

        if trend_signal.get("sentiment") == "negative" and trend_signal.get("growth_rate_pct", 0) < 20:
            risks.append("Sentimiento negativo con bajo crecimiento - riesgo de rechazo")

        return risks[:3]  # Max 3

    def _recommend_format(self, score: int) -> str:
        """Recommend episode format based on viral score."""
        if score >= 80:
            return "vertical_60s"  # High potential - longer format
        elif score >= 60:
            return "vertical_30s"
        else:
            return "vertical_15s"  # Lower potential - short and punchy


if __name__ == "__main__":
    print("ViralAnalystAgent module loaded successfully")
