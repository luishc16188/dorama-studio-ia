"""
Hit Predictor AI - Sistema de puntuación que evalúa elige historias con alto potencial de éxito.
Evalúa: potencial viral, fuerza emocional, originalidad, retención, potencial de comentarios, potencial internacional.
Implementa DORAMA SCORE con umbral mínimo para producción automática.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class HitScoreComponents:
    """Componentes del puntaje de éxito."""
    viral_potential: float = 0.0      # 0-100
    emotional_strength: float = 0.0   # 0-100
    originality: float = 0.0          # 0-100
    retention_potential: float = 0.0  # 0-100
    comment_potential: float = 0.0    # 0-100
    international_appeal: float = 0.0 # 0-100

    # Pesos para el cálculo final (configurable)
    weights: dict[str, float] = field(default_factory=lambda: {
        "viral_potential": 0.25,
        "emotional_strength": 0.20,
        "originality": 0.15,
        "retention_potential": 0.15,
        "comment_potential": 0.10,
        "international_appeal": 0.15
    })

@dataclass
class HitPredictorResult:
    """Resultado completo del predictor de éxito."""
    dorama_score: float = 0.0              # Puntaje final 0-100
    verdict: str = "REJECT"                # PASS, CONDITIONAL_PASS, REJECT, NEEDS_IMPROVEMENT
    components: HitScoreComponents = field(default_factory=HitScoreComponents)
    feedback: list[str] = field(default_factory=list)
    improvement_suggestions: list[str] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class HitPredictorAI:
    """
    Hit Predictor AI que evalúa historias antes de producción completa.
    Genera un DORAMA SCORE basado en 6 dimensiones clave.
    Si no supera el mínimo establecido, sugiere mejoras automáticas.
    """

    def __init__(self, minimum_score: float = 75.0):
        """
        Inicializa el predictor de éxito.

        Args:
            minimum_score: Puntaje mínimo requerido para aprobar producción (default 75/100)
        """
        self.minimum_score = minimum_score
        self.score_history = []  # Para seguimiento de calibración
        self.genre_modifiers = {
            "romance_traicion": {"viral_potential": 1.1, "emotional_strength": 1.2},
            "thriller_misterio": {"retention_potential": 1.3, "comment_potential": 1.1},
            "fantasia_epica": {"international_appeal": 1.4, "originality": 1.2},
            "drama_medico": {"emotional_strength": 1.1, "comment_potential": 1.2},
            "drama_legal": {"comment_potential": 1.3, "international_appeal": 1.1},
            "drama_familia": {"emotional_strength": 1.1, "retention_potential": 1.1},
            "comedia_romantica": {"viral_potential": 1.2, "comment_potential": 1.3},
            "accion": {"retention_potential": 1.2, "international_appeal": 1.3},
            "sobrenatural": {"originality": 1.3, "viral_potential": 1.1}
        }

        logger.info(f"HitPredictorAI initialized with minimum score: {minimum_score}")

    def predict_hit(
        self,
        story_data: dict[str, Any],
        genre: str = "romance_traicion",
        episode_count: int = 20,
        target_audience: str = "general"
    ) -> HitPredictorResult:
        """
        Evalúa si una historia tiene potencial de éxito.

        Args:
            story_data: Diccionario con elementos de la historia (characters, plot, etc.)
            genre: Género del dorama
            episode_count: Número de episodios planeados
            target_audience: Audiencia objetivo (general, teen, adult, international)

        Returns:
            HitPredictorResult con DORAMA SCORE y recomendaciones
        """
        logger.info(f"Evaluing hit potential for {genre} story with {episode_count} episodes")

        # Evaluar cada dimensión
        components = HitScoreComponents()

        # 1. Potencial viral (basado en tendencia, hook, shareability)
        components.viral_potential = self._evaluate_viral_potential(story_data, genre)

        # 2. Fuerza emocional (arco emocional, identificabilidad, catarsis)
        components.emotional_strength = self._evaluate_emotional_strength(story_data, genre)

        # 3. Originalidad (novela, combinación de elementos, giro único)
        components.originality = self._evaluate_originality(story_data, genre)

        # 4. Potencial de retención (curva de atención, hooks, cliffhangers)
        components.retention_potential = self._evaluate_retention_potential(story_data, genre)

        # 5. Potencial de comentarios (debatibilidad, teorías, polarización constructiva)
        components.comment_potential = self._evaluate_comment_potential(story_data, genre)

        # 6. Potencial internacional (trans-culturalidad, universalidad, adaptabilidad)
        components.international_appeal = self._evaluate_international_appeal(story_data, genre, target_audience)

        # Aplicar modificadores de género
        self._apply_genre_modifiers(components, genre)

        # Calcular puntaje final ponderado
        dorama_score = self._calculate_weighted_score(components)

        # Generar veredicto y feedback
        verdict, feedback, improvements = self._generate_verdict_and_feedback(
            dorama_score, components, story_data, genre
        )

        # Calcular confianza basada en consistencia de datos
        confidence = self._calculate_confidence(story_data, components)

        result = HitPredictorResult(
            dorama_score=round(dorama_score, 1),
            verdict=verdict,
            components=components,
            feedback=feedback,
            improvement_suggestions=improvements,
            confidence=round(confidence, 2)
        )

        # Guardar en historial para calibración
        self.score_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "score": dorama_score,
            "genre": genre,
            "verdict": verdict
        })

        # Mantener solo últimos 1000 registros
        if len(self.score_history) > 1000:
            self.score_history = self.score_history[-1000:]

        logger.info(f"Hit Prediction: {dorama_score}/100 - {verdict}")
        return result

    def _evaluate_viral_potential(self, story_data: dict[str, Any], genre: str) -> float:
        """Evalúa el potencial viral de la historia."""
        score = 50.0  # Base

        # Factores que aumentan potencial viral
        viral_boosters = []

        # Hook fuerte en los primeros 3 segundos
        if story_data.get("has_strong_hook", False):
            viral_boosters.append(15)

        # Elemento de sorpresa o giro inesperado
        if story_data.get("has_plot_twist", False):
            viral_boosters.append(12)

        # Controversia constructiva o tema candente
        if story_data.get("has_social_commentary", False):
            viral_boosters.append(10)

        # Visual impactante o estética distintiva
        if story_data.get("has_distinctive_visual", False):
            viral_boosters.append(10)

        # Elemento de identificación fuerte
        if story_data.get("has_strong_relatability", False):
            viral_boosters.append(12)

        # Factor de novedad/revolución
        if story_data.get("has_novelty_factor", False):
            viral_boosters.append(15)

        # Aplicar boosters
        score += sum(viral_boosters)

        # Factores que disminuyen potencial viral
        viral_reducers = []

        # Demasiado predecible o cliché
        if story_data.get("is_cliche_heavy", False):
            viral_reducers.append(15)

        # Falta de elemento compartible
        if story_data.get("lacks_shareable_moments", False):
            viral_reducers.append(10)

        # Demasiado nicho o específico
        if story_data.get("is_too_niche", False):
            viral_reducers.append(12)

        score -= sum(viral_reducers)

        # Normalizar a 0-100
        return max(0.0, min(100.0, score))

    def _evaluate_emotional_strength(self, story_data: dict[str, Any], genre: str) -> float:
        """Evalúa la fuerza emocional de la historia."""
        score = 40.0  # Base

        # Factores que aumentan fuerza emocional
        emotional_boosters = []

        # Arco emocional claro y profundo
        if story_data.get("has_clear_emotional_arc", False):
            emotional_boosters.append(20)

        # Identificación fuerte con protagonista
        if story_data.get("has_strong_protagonist_connection", False):
            emotional_boosters.append(15)

        # Momentos catárticos bien colocados
        if story_data.get("has_cathartic_moments", False):
            emotional_boosters.append(12)

        # Emociones complejas y matizadas
        if story_data.get("has_complex_emotions", False):
            emotional_boosters.append(10)

        # Viaje de transformación significativo
        if story_data.get("has_character_transformation", False):
            emotional_boosters.append(15)

        # Empatía generada hacia personajes incluso antagonistas
        if story_data.get("generates_antagonist_empathy", False):
            emotional_boosters.append(10)

        # Aplicar boosters
        score += sum(emotional_boosters)

        # Factores que disminuyen fuerza emocional
        emotional_reducers = []

        # Emociones superficiales o forzadas
        if story_data.get("emotions_feel_forced", False):
            emotional_reducers.append(15)

        # Falta de vulnerabilidad auténtica
        if story_data.get("lacks_authentic_vulnerability", False):
            emotional_reducers.append(12)

        # Demasiado enfoque en trama sobre emoción
        if story_data.get("plot_over_emotion", False):
            emotional_reducers.append(10)

        score -= sum(emotional_reducers)

        # Normalizar a 0-100
        return max(0.0, min(100.0, score))

    def _evaluate_originality(self, story_data: dict[str, Any], genre: str) -> float:
        """Evalúa la originalidad de la historia."""
        score = 35.0  # Base (es difícil ser completamente original)

        # Factores que aumentan originalidad
        originality_boosters = []

        # Combinación única de géneros o elementos
        if story_data.get("has_genre_mashup", False):
            originality_boosters.append(20)

        # Estructura narrativa innovadora
        if story_data.get("has_novel_structure", False):
            originality_boosters.append(18)

        # Perspectiva o punto de vista único
        if story_data.get("has_unique_pov", False):
            originality_boosters.append(15)

        # Elementos culturales o subculturales poco representados
        if story_data.get("has_underrepresented_elements", False):
            originality_boosters.append(15)

        # Rompe tropes de manera significativa
        if story_data.get("meaningfully_subverts_tropes", False):
            originality_boosters.append(20)

        # Ambientación o mundo único
        if story_data.get("has_unique_setting", False):
            originality_boosters.append(12)

        # Aplicar boosters
        score += sum(originality_boosters)

        # Factores que disminuyen originalidad
        originality_reducers = []

        # Demasiado dependiente de tropes conocidos
        if story_data.get("heavy_trope_reliance", False):
            originality_reducers.append(20)

        # Historia vista antes con pequeños cambios
        if story_data.get("feels_like_a_rerun", False):
            originality_reducers.append(18)

        # Falta de voz distintiva
        if story_data.get("lacks_distinctive_voice", False):
            originality_reducers.append(15)

        score -= sum(originality_reducers)

        # Normalizar a 0-100
        return max(0.0, min(100.0, score))

    def _evaluate_retention_potential(self, story_data: dict[str, Any], genre: str) -> float:
        """Evalúa el potencial de retención de la historia."""
        score = 45.0  # Base

        # Factores que aumentan potencial de retención
        retention_boosters = []

        # Curva de tensión bien diseñada (picos y valles estratégicos)
        if story_data.get("has_well_designed_tension_curve", False):
            retention_boosters.append(20)

        # Hooks efectivos cada 8-12 minutos (para formato episódico)
        if story_data.get("has_effective_hooks", False):
            retention_boosters.append(15)

        # Cliffhangers fuertes y variados
        if story_data.get("has_strong_varied_cliffhangers", False):
            retention_boosters.append(18)

        # Revelaciones de información bien espaciadas
        if story_data.get("has_well_spaced_revelations", False):
            retention_boosters.append(12)

        # Equilibrio entre acción y reflexión
        if story_data.get("has_action_reflection_balance", False):
            retention_boosters.append(10)

        # Momentos de "ah-ha" o descubrimiento
        if story_data.get("has_aha_moments", False):
            retention_boosters.append(10)

        # Aplicar boosters
        score += sum(retention_boosters)

        # Factores que disminuyen potencial de retención
        retention_reducers = []

        # Ritmo monótono o predecible
        if story_data.get("has_monotonous_pacing", False):
            retention_reducers.append(15)

        # Información dada sin propósito (exposición vacía)
        if story_data.get("has_empty_exposition", False):
            retention_reducers.append(12)

        # Falta de preguntas abiertas que mantengan curiosidad
        if story_data.get("lacks_open_questions", False):
            retention_reducers.append(10)

        # Demasiado enfoque en un solo tipo de emoción
        if story_data.get("emotional_one_dimensional", False):
            retention_reducers.append(10)

        score -= sum(retention_reducers)

        # Normalizar a 0-100
        return max(0.0, min(100.0, score))

    def _evaluate_comment_potential(self, story_data: dict[str, Any], genre: str) -> float:
        """Evalúa el potencial de generación de comentarios y discusión."""
        score = 30.0  # Base

        # Factores que aumentan potencial de comentarios
        comment_boosters = []

        # Temas éticos o morales complejos
        if story_data.get("has_complex_ethical_dilemmas", False):
            comment_boosters.append(20)

        # Ambigüedad intencional que permite múltiples interpretaciones
        if story_data.get("has_intentional_ambiguity", False):
            comment_boosters.append(15)

        # Personajes moralmente grises (ni totalmente buenos ni malos)
        if story_data.get("has_morally_grey_characters", False):
            comment_boosters.append(18)

        # Teorías de fan hechos fáciles (pistas visibles pero no obvias)
        if story_data.get("has_easter_eggs_and_clues", False):
            comment_boosters.append(12)

        # Elementos de "shippeo" o relaciones complejas
        if story_data.get("has_complex_relationships", False):
            comment_boosters.append(12)

        # Finales abiertos o semi-abiertos que generan debate
        if story_data.get("has_debatable_ending", False):
            comment_boosters.append(15)

        # Aplicar boosters
        score += sum(comment_boosters)

        # Factores que disminuyen potencial de comentarios
        comment_reducers = []

        # Respuestas demasiado fáciles o obvias
        if story_data.get("answers_are_too_obvious", False):
            comment_reducers.append(15)

        # Falta de elementos discutibles
        if story_data.get("lacks_discussable_elements", False):
            comment_reducers.append(12)

        # Demasiado lineal o predictivo
        if story_data.get("is_too_linear_predictive", False):
            comment_reducers.append(10)

        score -= sum(comment_reducers)

        # Normalizar a 0-100
        return max(0.0, min(100.0, score))

    def _evaluate_international_appeal(self, story_data: dict[str, Any], genre: str, target_audience: str) -> float:
        """Evalúa el potencial internacional de la historia."""
        score = 25.0  # Base (muchas historias son muy locales)

        # Factores que aumentan potencial internacional
        international_boosters = []

        # Temas universales (amor, pérdida, poder, identidad, justicia)
        if story_data.get("has_universal_themes", False):
            international_boosters.append(20)

        # Bajo dependencia de referencias culturales específicas
        if story_data.get("has_low_cultural_specificity", False):
            international_boosters.append(18)

        # Emociones y motivaciones comprensibles跨文化
        if story_data.get("has_cross_cultural_emotions", False):
            international_boosters.append(15)

        # Visual storytelling fuerte (menos dependiente del diálogo)
        if story_data.get("has_strong_visual_storytelling", False):
            international_boosters.append(15)

        # Arquetipos reconocibles internacionalmente
        if story_data.get("has_recognizable_archetypes", False):
            international_boosters.append(12)

        # Adaptabilidad fácil a diferentes mercados
        if story_data.get("is_easily_adaptable", False):
            international_boosters.append(10)

        # Aplicar boosters
        score += sum(international_boosters)

        # Factores que disminuyen potencial internacional
        international_reducers = []

        # Altamente dependiente de contexto histórico/local específico
        if story_data.get("is_highly_locally_specific", False):
            international_reducers.append(20)

        # Humor o riferencias que no se traducen bien
        if story_data.get("has_untranslatable_humor", False):
            international_reducers.append(15)

        # Ritmo o estructura que no funciona en otros mercados
        if story_data.get("has_market_specific_pacing", False):
            international_reducers.append(12)

        score -= sum(international_reducers)

        # Normalizar a 0-100
        return max(0.0, min(100.0, score))

    def _apply_genre_modifiers(self, components: HitScoreComponents, genre: str) -> None:
        """Aplica modificadores específicos de género a los componentes."""
        if genre in self.genre_modifiers:
            modifiers = self.genre_modifiers[genre]

            for component, modifier in modifiers.items():
                if hasattr(components, component):
                    current_value = getattr(components, component)
                    # Aplicar modificador pero limitar a 100 máximo
                    new_value = min(100.0, current_value * modifier)
                    setattr(components, component, new_value)

    def _calculate_weighted_score(self, components: HitScoreComponents) -> float:
        """Calcula el puntaje final ponderado."""
        score = (
            components.viral_potential * components.weights["viral_potential"] +
            components.emotional_strength * components.weights["emotional_strength"] +
            components.originality * components.weights["originality"] +
            components.retention_potential * components.weights["retention_potential"] +
            components.comment_potential * components.weights["comment_potential"] +
            components.international_appeal * components.weights["international_appeal"]
        )
        return score

    def _generate_verdict_and_feedback(
        self,
        score: float,
        components: HitScoreComponents,
        story_data: dict[str, Any],
        genre: str
    ) -> tuple[str, list[str], list[str]]:
        """Genera veredicto, feedback y sugerencias de mejora."""
        feedback = []
        improvements = []

        # Determinar veredicto basado en score
        if score >= self.minimum_score:
            if score >= 90:
                verdict = "PASS_EXCELLENT"
            elif score >= 80:
                verdict = "PASS_STRONG"
            else:
                verdict = "PASS"
        elif score >= self.minimum_score - 10:
            verdict = "CONDITIONAL_PASS"
            feedback.append(f"Score {score}/100 está cerca del umbral mínimo de {self.minimum_score}/100")
        elif score >= self.minimum_score - 20:
            verdict = "NEEDS_IMPROVEMENT"
            feedback.append(f"Score {score}/100 requiere mejoras significativas para alcanzar el umbral de {self.minimum_score}/100")
        else:
            verdict = "REJECT"
            feedback.append(f"Score {score}/100 está significativamente por debajo del umbral mínimo de {self.minimum_score}/100")

        # Generar feedback específico basado en componentes bajos
        component_scores = {
            "viral_potential": components.viral_potential,
            "emotional_strength": components.emotional_strength,
            "originality": components.originality,
            "retention_potential": components.retention_potential,
            "comment_potential": components.comment_potential,
            "international_appeal": components.international_appeal
        }

        # Identificar componentes por debajo del 60 (áreas de mejora crítica)
        weak_components = [
            (name, score) for name, score in component_scores.items() if score < 60
        ]

        if weak_components:
            feedback.append(f"Áreas de mejora crítica: {', '.join([name for name, _ in weak_components])}")

            # Generar sugerencias específicas para cada componente débil
            for name, comp_score in weak_components:
                if name == "viral_potential":
                    improvements.append("Agregar hook más fuerte en los primeros 3 segundos")
                    improvements.append("Incluir elemento de sorpresa o giro inesperado temprano")
                    improvements.append("Considerar tema candente o controversia constructiva")

                elif name == "emotional_strength":
                    improvements.append("Desarrollar arco emocional más claro y profundo")
                    improvements.append("Aumentar identificación con el protagonista")
                    improvements.append("Agregar momentos catárticos bien colocados")

                elif name == "originality":
                    improvements.append("Explorar combinación única de géneros o elementos")
                    improvements.append("Considerar estructura narrativa innovadora")
                    improvements.append("Buscar perspectiva o punto de vista único")

                elif name == "retention_potential":
                    improvements.append("Diseñar curva de tensión con picos y valles estratégicos")
                    improvements.append("Agregar hooks efectivos cada 8-12 minutos")
                    improvements.append("Mejorar variedad y fuerza de cliffhangers")

                elif name == "comment_potential":
                    improvements.append("Introducir dilemas éticos o morales complejos")
                    improvements.append("Crear personajes moralmente grises")
                    improvements.append("Agregar elementos de teorías de fan o easter eggs")

                elif name == "international_appeal":
                    improvements.append("Enfocarse en temas universales más que en lo local")
                    improvements.append("Reducir dependencia de referencias culturales específicas")
                    improvements.append("Mejorar storytelling visual para reducir dependencia del diálogo")

                elif name == "retention_potential":  # Duplicate key, fixing
                    improvements.append("Diseñar curva de tensión con picos y valles estratégicos")
                    improvements.append("Agregar hooks efectivos cada 8-12 minutos")
                    improvements.append("Mejorar variedad y fuerza de cliffhangers")

        # Si el score es alto, reconocer fortalezas
        strong_components = [
            (name, score) for name, score in component_scores.items() if score >= 80
        ]

        if strong_components:
            feedback.append(f"Fortalezas destacadas: {', '.join([name for name, _ in strong_components])}")

        return verdict, feedback, improvements

    def _calculate_confidence(self, story_data: dict[str, Any], components: HitScoreComponents) -> float:
        """Calcula la confianza en la predicción basada en completitud y consistencia de datos."""
        # Factores que aumentan confianza
        confidence_factors = []

        # Más datos disponibles = mayor confianza
        data_completeness = len([v for v in story_data.values() if v is not None and v != "" and v != []]) / max(len(story_data), 1)
        if data_completeness > 0.8:
            confidence_factors.append(0.2)
        elif data_completeness > 0.6:
            confidence_factors.append(0.1)

        # Consistencia entre componentes (no varianza extrema)
        scores = [
            components.viral_potential,
            components.emotional_strength,
            components.originality,
            components.retention_potential,
            components.comment_potential,
            components.international_appeal
        ]
        score_variance = np.var(scores) if len(scores) > 0 else 0
        if score_variance < 400:  # Varianza baja = componentes similares = más predecible
            confidence_factors.append(0.15)

        # Falta de contradicciones obvias en los datos
        contradiction_penalty = 0
        if story_data.get("has_obvious_contradictions", False):
            contradiction_penalty = 0.2

        base_confidence = 0.6  # Confianza base
        final_confidence = base_confidence + sum(confidence_factors) - contradiction_penalty

        return max(0.3, min(0.95, final_confidence))  # Entre 30% y 95%

# Instancia singleton
hit_predictor = HitPredictorAI()
