"""
Feedback Loop - Generates actionable feedback from analytics to improve future episodes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class AnalyticsOutput:
    """Output from Analytics Engine (Agent 20)"""

    episode_id: str
    retention_curve: list[float]  # Retention at each second (0.0 to 1.0)
    drop_off_points: list[int]  # Seconds where viewers drop significantly
    winning_hook_category: str  # Which hook type performed best
    losing_hook_category: str  # Which hook type performed worst
    avg_watch_time: float  # Average watch time in seconds
    completion_rate: float  # Percentage who watched entire episode
    emotional_peaks: list[tuple[int, str]]  # (second, emotion) peaks
    timestamp: datetime = field(default_factory=datetime.now)
    social_shares: int = 0  # Number of shares/duets/stitches
    comments_count: int = 0  # Number of comments
    likes_ratio: float = 0.0  # Likes/views ratio


class FeedbackLoop:
    """
    Generates actionable feedback injection - closes the loop between Analytics
    and Writer/Hook/Video/Audio agents (GAP 2 from autodiagnostico)
    """

    def __init__(self, memory_path: Path | None = None):
        self.memory_path = memory_path or Path("memory/feedback_history.json")
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._history: list[dict] = []
        self._load_history()

    def _load_history(self):
        if self.memory_path.exists():
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
            except Exception:
                self._history = []

    def _save_history(self):
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self._history[-1000:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def analyze_episode_performance(self, analytics: AnalyticsOutput) -> dict[str, Any]:
        """
        Analyze analytics output and generate insights for different agents.
        Returns a dictionary with feedback for each agent type.
        """
        feedback = {
            "timestamp": analytics.timestamp.isoformat(),
            "episode_id": analytics.episode_id,
            "overall_performance": self._assess_overall_performance(analytics),
            "writer_feedback": self._generate_writer_feedback(analytics),
            "hook_feedback": self._generate_hook_feedback(analytics),
            "video_feedback": self._generate_video_feedback(analytics),
            "audio_feedback": self._generate_audio_feedback(analytics),
            "general_recommendations": self._generate_general_recommendations(
                analytics
            ),
        }

        # Record this feedback
        self._history.append(feedback)
        self._save_history()

        return feedback

    def _assess_overall_performance(self, analytics: AnalyticsOutput) -> dict[str, Any]:
        """Assess overall episode performance."""
        retention_at_3s = (
            analytics.retention_curve[3] if len(analytics.retention_curve) > 3 else 0
        )
        retention_at_10s = (
            analytics.retention_curve[10] if len(analytics.retention_curve) > 10 else 0
        )

        return {
            "retention_3s": retention_at_3s,
            "retention_10s": retention_at_10s,
            "avg_watch_time": analytics.avg_watch_time,
            "completion_rate": analytics.completion_rate,
            "social_engagement": analytics.social_shares + analytics.comments_count,
            "performance_level": (
                "excellent"
                if analytics.completion_rate > 0.7
                else (
                    "good"
                    if analytics.completion_rate > 0.5
                    else "fair" if analytics.completion_rate > 0.3 else "poor"
                )
            ),
        }

    def _generate_writer_feedback(self, analytics: AnalyticsOutput) -> dict[str, Any]:
        """Generate feedback for the Script Writer agent."""
        feedback = {
            "hook_effectiveness": "",
            "pacing_advice": "",
            "emotional_timing": "",
            "specific_actions": [],
        }

        # Analyze hook performance
        if analytics.winning_hook_category and analytics.losing_hook_category:
            feedback["hook_effectiveness"] = (
                f"El tipo de hook '{analytics.winning_hook_category}' funcionó mejor que '{analytics.losing_hook_category}'. Considera usar más de lo primero y menos de lo segundo."
            )

        # Analyze retention curve for pacing issues
        retention_curve = analytics.retention_curve
        if len(retention_curve) >= 10:
            # Check for steep drops that might indicate pacing problems
            drops = []
            for i in range(1, len(retention_curve)):
                drop = retention_curve[i - 1] - retention_curve[i]
                if drop > 0.15:  # More than 15% drop in one second
                    drops.append((i, drop))

            if len(drops) > 3:
                feedback["pacing_advice"] = (
                    "Se detectaron múltiples caídas bruscas de retención. Considerar suavizar transiciones entre beats o reducir la densidad de información en esos puntos."
                )
                feedback["specific_actions"].append(
                    "Revisar los beats donde caen más de 15% puntos de retención en un segundo."
                )
            elif len(drops) == 0:
                feedback["pacing_advice"] = (
                    "La retención es relativamente estable a lo largo del episodio, lo que indica buen pacing."
                )
            else:
                feedback["pacing_advice"] = (
                    "Algunas caídas menores de retención detectadas; revisar si corresponden a momentos de exposición excesiva."
                )

        # Analyze emotional peaks for timing
        if analytics.emotional_peaks:
            peak_times = [peak[0] for peak in analytics.emotional_peaks]
            peak_emotions = [peak[1] for peak in analytics.emotional_peaks]

            # Check if emotional peaks are well-distributed
            if len(peak_times) >= 3:
                feedback["emotional_timing"] = (
                    f"Se detectaron {len(peak_times)} picos emocionales en segundos {peak_times}. Buena distribución emocional a lo largo del episodio."
                )
            else:
                feedback["emotional_timing"] = (
                    "Pocos picos emocionales detectados; considerar aumentar la variación emocional a lo largo del episodio."
                )
        else:
            feedback["emotional_timing"] = (
                "No se detectaron picos emocionales claros; considerar diseñar momentos emocionales más pronunciados."
            )

        # Specific actions based on drop-off points
        if analytics.drop_off_points:
            feedback["specific_actions"].append(
                f"Revisar los segundos {analytics.drop_off_points[:3]} donde se produjeron abandonos significativos. "
                "Estos puntos pueden indicar necesidad de ganchos internos o cambios de ritmo."
            )

        return feedback

    def _generate_hook_feedback(self, analytics: AnalyticsOutput) -> dict[str, Any]:
        """Generate feedback for the Hook Engine agent."""
        feedback = {
            "winning_hook_type": analytics.winning_hook_category,
            "losing_hook_type": analytics.losing_hook_category,
            "recommendation": "",
            "experiment_suggestion": "",
        }

        if analytics.winning_hook_category and analytics.losing_hook_category:
            feedback["recommendation"] = (
                f"Prioriza hooks del tipo '{analytics.winning_hook_category}' que tuvieron mejor rendimiento. "
                f"Reduce o experimenta con variaciones de '{analytics.losing_hook_category}' que tuvieron peor desempeño."
            )

            feedback["experiment_suggestion"] = (
                f"Para el siguiente episodio, prueba combinar elementos de '{analytics.winning_hook_category}' con un enfoque novedoso, "
                f"manteniendo lo que funcionó pero añadiendo un giro inesperado."
            )

        return feedback

    def _generate_video_feedback(self, analytics: AnalyticsOutput) -> dict[str, Any]:
        """Generate feedback for the Video Animator agent."""
        feedback = {"visual_effectiveness": "", "specific_actions": []}

        # Analyze retention drops for visual issues
        if len(analytics.retention_curve) >= 15:
            # Early drop might indicate weak visual hook
            early_drop = (
                analytics.retention_curve[5]
                if len(analytics.retention_curve) > 5
                else 0
            )
            if early_drop < 0.7:  # Less than 70% retention at 5 seconds
                feedback["visual_effectiveness"] = (
                    "La retención temprana es baja, sugiriendo que el hook visual inicial no es lo suficientemente impactante."
                )
                feedback["specific_actions"].append(
                    "Revisar los primeros 3-5 segundos: asegurar que haya un elemento visual fuerte que detenga el scroll."
                )
            else:
                feedback["visual_effectiveness"] = (
                    "Buena retención visual temprana, indicando un hook visual efectivo."
                )

            # Mid-episode drops might indicate visual fatigue
            mid_point = len(analytics.retention_curve) // 2
            mid_retention = (
                analytics.retention_curve[mid_point]
                if mid_point < len(analytics.retention_curve)
                else 0
            )
            end_retention = (
                analytics.retention_curve[-1] if analytics.retention_curve else 0
            )

            if mid_retention - end_retention > 0.2:  # Significant drop in second half
                feedback["specific_actions"].append(
                    "Se observa fatiga visual en la segunda mitad. Considerar aumentar la variedad de tomas, cambios de iluminación o elementos visuales dinámicos."
                )

        # Social shares indicate shareable visual moments
        if analytics.social_shares > 100:  # Arbitrary threshold
            feedback["specific_actions"].append(
                "El alto número de compartidos sugiere que hubo momentos visualmente memorables que resonaron con la audiencia. "
                "Identificar esos momentos y replicar su fórmula en futuros episodios."
            )

        return feedback

    def _generate_audio_feedback(self, analytics: AnalyticsOutput) -> dict[str, Any]:
        """Generate feedback for the Audio Engineer agent."""
        feedback = {"audio_effectiveness": "", "specific_actions": []}

        # Analyze emotional peaks for audio timing
        if analytics.emotional_peaks:
            # Check if emotional peaks coincide with expected audio moments
            peak_times = [peak[0] for peak in analytics.emotional_peaks]

            # Ideal: audio peaks around emotional high points
            feedback["audio_effectiveness"] = (
                f"Se detectaron {len(analytics.emotional_peaks)} picos emocionales que pueden estar relacionados con momentos de audio impactante."
            )

            # Check if we have peaks at expected narrative moments (beats 3, 5, 7, 9 approx)
            expected_peak_seconds = [
                25,
                45,
                65,
                85,
            ]  # Approximate middle of beats 3,5,7,9
            aligned_peaks = 0
            for peak_time in peak_times:
                for expected in expected_peak_seconds:
                    if abs(peak_time - expected) <= 10:  # Within 10 seconds
                        aligned_peaks += 1
                        break

            if aligned_peaks >= 2:
                feedback["specific_actions"].append(
                    "Buena sincronización entre picos emocionales y momentos de audio. Mantener esta estrategia."
                )
            else:
                feedback["specific_actions"].append(
                    "Considerar mejorar la sincronización entre momentos de audio (crescendos, silencios, impacts) y los picos emocionales de la narrativa."
                )
        else:
            feedback["audio_effectiveness"] = (
                "No se detectaron picos emocionales claros en el audio; considerar diseñar momentos de audio más pronunciados que marquen la narrativa."
            )

        # Check completion rate for audio fatigue
        if analytics.completion_rate < 0.4:
            feedback["specific_actions"].append(
                "Baja tasa de completación puede indicar fatiga auditiva. Revisar si la música es demasiado repetitiva o si los efectos de sonido resultan agresivos a largo plazo."
            )

        return feedback

    def _generate_general_recommendations(
        self, analytics: AnalyticsOutput
    ) -> list[str]:
        """Generate general recommendations based on overall performance."""
        recommendations = []

        # Based on completion rate
        if analytics.completion_rate >= 0.8:
            recommendations.append(
                "Excelente retención general. Mantener la fórmula actual pero continuar innovando para evitar estancamiento."
            )
        elif analytics.completion_rate >= 0.6:
            recommendations.append(
                "Buen desempeño general. Enfocarse en mejorar los puntos débiles específicos identificados en el análisis."
            )
        elif analytics.completion_rate >= 0.4:
            recommendations.append(
                "Desempeño moderado. Requerirá trabajo significativo en múltiples áreas: gancho, pacing, y valor emocional."
            )
        else:
            recommendations.append(
                "Bajo desempeño. Revisar fundamentalmente el concepto, gancho inicial y propuesta de valor para la audiencia objetivo."
            )

        # Based on social engagement
        engagement_rate = (analytics.social_shares + analytics.comments_count) / max(
            analytics.avg_watch_time, 1
        )
        if engagement_rate > 0.5:
            recommendations.append(
                "Alto engagement social indica que el contenido resonó emocionalmente. Identificar qué aspectos específicos generaron esta respuesta y amplificarlos."
            )
        elif engagement_rate < 0.1:
            recommendations.append(
                "Bajo engagement social sugiere que el contenido no generó suficiente conexión emocional para motivar interacción. Trabajar en crear momentos más compartibles."
            )

        # Based on drop-off points specificity
        if len(analytics.drop_off_points) > 5:
            recommendations.append(
                "Múltiples puntos de abandono sugieren problemas de pacing o densidad de información. Considerar simplificar y enfocarse en menos elementos por episodio."
            )
        elif len(analytics.drop_off_points) == 0:
            recommendations.append(
                "Pocos o ningún punto de abandono significativo detectado, lo que es excelente para la retención a lo largo del episodio."
            )

        return recommendations

    def get_latest_feedback(self, episode_id: str | None = None) -> dict | None:
        """Get the most recent feedback feedback."""
        if not self._history:
            return None

        if episode_id:
            # Find feedback for specific episode
            for feedback in reversed(self._history):
                if feedback.get("episode_id") == episode_id:
                    return feedback
            return None
        else:
            # Return most recent feedback
            return self._history[-1] if self._history else None


# Convenience function
def generate_feedback_from_analytics(analytics: AnalyticsOutput) -> dict[str, Any]:
    """Convenience function to generate feedback from analytics."""
    loop = FeedbackLoop()
    return loop.analyze_episode_performance(analytics)


if __name__ == "__main__":
    # Quick test
    print("FeedbackLoop module loaded successfully")
