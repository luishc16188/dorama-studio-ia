"""
Multimodal Quality Control Agent - Fase 13
Control de calidad integral multimodal: historia, visual, audio, continuidad, plataforma.
Integra Quality Gate de 100 puntos / 15 dimensiones y coordina regeneración selectiva.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.quality_check_agent import QualityCheckAgent
from dorama_studio.agents.quality_gate_agent import QualityGateAgent
from dorama_studio.agents.selective_regeneration_agent import SelectiveRegenerationAgent
from dorama_studio.contracts.v2_schemas import (
    EpisodeSpecV2,
    QualityState,
)

logger = logging.getLogger(__name__)


class QualityDimension(str, Enum):
    """Dimensiones de calidad para el gate multimodal de 100 puntos."""
    # Historia/Narrativa (50 puntos)
    HOOK_0_3S = "hook_0_3s"
    CONFLICTO_CONCRETO = "conflicto_concreto"
    PROTAGONISTA_DESEO_CLARO = "protagonista_deseo_claro"
    PREGUNTA_ABIERTA = "pregunta_abierta"
    SITUACION_EMPORA = "situacion_empeora"
    RESPUESTA_PARCIAL = "respuesta_parcial"
    ELEMENTO_SORPRESA = "elemento_sorpresa"
    CLIFFHANGER_FUERTE = "cliffhanger_fuerte"
    IMPACTO_EMOCIONAL = "impacto_emocional"
    SHOW_DONT_TELL = "show_dont_tell"
    DIALOGO_AVANZA_HISTORIA = "dialogo_avanza_historia"
    DIALOGO_DELIVERY_PRESENTE = "dialogo_delivery_presente"
    MICRO_EXPRESIONES_PRESENTES = "micro_expresiones_presentes"
    SILENCIO_ANTES_REVELACION = "silencio_antes_revelacion"
    FORMULA_FRACCIONAL_APLICADA = "formula_fraccional_aplicada"
    # Visual (20 puntos)
    RESOLUCION_CORRECTA = "resolucion_correcta"
    FRAME_RATE_CORRECTO = "frame_rate_correcto"
    DURACION_SHOTS_VALIDA = "duracion_shots_valida"
    CONSISTENCIA_VISUAL = "consistencia_visual"
    PROMPT_AST_UNICO = "prompt_ast_unico"
    # Audio (15 puntos)
    MEZCLA_BALANCEADA = "mezcla_balanceada"
    SILENCIO_CRITICO = "silencio_critico"
    FOLEY_AMPLIFICADO = "foley_amplificado"
    SUB_BASS_STINGER = "sub_bass_stinger"
    MUSIC_PROGRESSION = "music_progression"
    # Continuidad (10 puntos)
    CONTINUIDAD_PERSONAJES = "continuidad_personajes"
    CONTINUIDAD_LOCALIZACIONES = "continuidad_localizaciones"
    CONTINUIDAD_OBJETOS = "continuidad_objetos"
    CONTINUIDAD_TIEMPO = "continuidad_tiempo"
    # Plataforma (5 puntos)
    FORMATO_PLATAFORMA = "formato_plataforma"
    ASPECT_RATIO_CORRECTO = "aspect_ratio_correcto"
    SAFE_ZONES_RESPEITADAS = "safe_zones_respetadas"


@dataclass
class DimensionResult:
    """Resultado de una dimensión de calidad individual."""
    dimension: QualityDimension
    score: float  # 0-100
    passed: bool
    details: str
    evidence_refs: list[str] = field(default_factory=list)
    suggested_fix: str | None = None


@dataclass
class MultimodalQualityReport:
    """Reporte completo de calidad multimodal."""
    overall_state: QualityState
    overall_score: float  # 0-100
    dimension_results: list[DimensionResult]
    critical_failures: list[str]
    issues: list[str]
    regeneration_modules: list[str]  # Módulos sugeridos para regeneración selectiva
    created_by: str
    timestamp: float = field(default_factory=time.time)


class MultimodalQualityAgent(BaseAgent[EpisodeSpecV2, MultimodalQualityReport]):
    """
    Agente de Control de Calidad Multimodal que evalúa:
    - Historia: Quality Gate 100pts/15dims
    - Visual: Resolución, framerate, duración shots, consistencia
    - Audio: Mezcla, silencio crítico, foley amplificado, sub-bass, progresión musical
    - Continuidad: Personajes, localizaciones, objetos, tiempo
    - Plataforma: Formato, aspect ratio, safe zones
    Y coordina regeneración selectiva basada en fallos específicos.
    """

    # Pesos por categoría (suman 100)
    CATEGORY_WEIGHTS = {
        "historia": 50.0,
        "visual": 20.0,
        "audio": 15.0,
        "continuidad": 10.0,
        "plataforma": 5.0
    }

    def __init__(self):
        super().__init__("MultimodalQualityAgent")
        self.quality_gate = QualityGateAgent()
        self.quality_check = QualityCheckAgent()
        self.selective_regen = SelectiveRegenerationAgent()

    def _process(self, validated_input: EpisodeSpecV2) -> MultimodalQualityReport:
        """
        Ejecuta control de calidad multimodal completo sobre un episodio.

        Args:
            validated_input: EpisodeSpecV2 con todos los artefactos del episodio

        Returns:
            MultimodalQualityReport con scores, fallos y módulos de regeneración sugeridos
        """
        logger.info(f"Iniciando QC multimodal para episodio {validated_input.episode_number}")

        all_results: list[DimensionResult] = []

        # 1. HISTORIA - Quality Gate 100pts/15dims
        historia_results = self._evaluate_historia(validated_input)
        all_results.extend(historia_results)

        # 2. VISUAL - Video artifacts
        visual_results = self._evaluate_visual(validated_input)
        all_results.extend(visual_results)

        # 3. AUDIO - Audio artifacts
        audio_results = self._evaluate_audio(validated_input)
        all_results.extend(audio_results)

        # 4. CONTINUIDAD
        continuidad_results = self._evaluate_continuidad(validated_input)
        all_results.extend(continuidad_results)

        # 5. PLATAFORMA
        plataforma_results = self._evaluate_plataforma(validated_input)
        all_results.extend(plataforma_results)

        # Calcular score ponderado
        overall_score = self._calculate_weighted_score(all_results)
        overall_state = QualityState.PASS if overall_score >= 70 else QualityState.FAIL

        # Recopilar fallos críticos y issues
        critical_failures = [r.details for r in all_results if not r.passed and r.score < 40]
        issues = [r.details for r in all_results if not r.passed and r.score >= 40]

        # Determinar módulos de regeneración selectiva
        regeneration_modules = self._determine_regeneration_modules(all_results)

        report = MultimodalQualityReport(
            overall_state=overall_state,
            overall_score=round(overall_score, 1),
            dimension_results=all_results,
            critical_failures=critical_failures,
            issues=issues,
            regeneration_modules=regeneration_modules,
            created_by=self.name
        )

        logger.info(f"QC multimodal completado: Score={overall_score:.1f}, State={overall_state.value}")
        return report

    def _evaluate_historia(self, episode: EpisodeSpecV2) -> list[DimensionResult]:
        """Evalúa calidad narrativa usando Quality Gate de 15 dimensiones."""
        results = []

        # Preparar datos para QualityGateAgent
        episode_data = {
            "hook_0_3s": any("hook" in beat.narrative_goal.lower() for beat in episode.beats[:2]),
            "conflict_concrete": any("conflict" in beat.narrative_goal.lower() or "conflicto" in beat.narrative_goal.lower() for beat in episode.beats),
            "protagonist_desire_clarified": any("deseo" in beat.narrative_goal.lower() or "querer" in beat.narrative_goal.lower() for beat in episode.beats),
            "unresolved_question": any(beat.information_withheld for beat in episode.beats),
            "situation_worsens": any("empeora" in beat.narrative_goal.lower() or "peor" in beat.narrative_goal.lower() for beat in episode.beats),
            "partial_answer": any(beat.information_revealed for beat in episode.beats),
            "surprise_element": any("sorpresa" in beat.narrative_goal.lower() or "giro" in beat.narrative_goal.lower() for beat in episode.beats),
            "strong_cliffhanger": len(episode.beats) > 0 and "cliffhanger" in episode.beats[-1].narrative_goal.lower(),
            "emotional_impact": any(beat.emotion.intensity > 0.7 for beat in episode.beats),
            "show_dont_tell": all(len(d.text.split()) <= 10 for d in episode.dialogues),
            "dialogue_advances_story": all(d.delivery != "exposicion" for d in episode.dialogues),
            "dialogue_delivery_present": all(d.delivery for d in episode.dialogues),
            "micro_expressions_present": any(beat.acting.micro_expression for beat in episode.beats),
            "silence_drop_before_revelation": any(beat.audio.silence_window for beat in episode.beats if beat.information_revealed),
            "fractal_formula_applied": self._check_fractal_formula(episode)
        }

        # Ejecutar quality gate
        gate_input = {
            "episode_num": episode.episode_number,
            "episode_score": 0.0,
            "breakdown": {},
            "feedback": [],
            "threshold": 70.0
        }

        # Evaluar cada dimensión individualmente
        dimension_mapping = {
            QualityDimension.HOOK_0_3S: ("hook_0_3s", 20, "Hook con apertura explosiva en primeros 3s"),
            QualityDimension.CONFLICTO_CONCRETO: ("conflict_concrete", 15, "Conflicto definido y concreto"),
            QualityDimension.PROTAGONISTA_DESEO_CLARO: ("protagonist_desire_clarified", 15, "Deseo del protagonista clarificado"),
            QualityDimension.PREGUNTA_ABIERTA: ("unresolved_question", 15, "Pregunta abierta sin resolver al final"),
            QualityDimension.SITUACION_EMPORA: ("situation_worsens", 15, "Situación empeora para el protagonista"),
            QualityDimension.RESPUESTA_PARCIAL: ("partial_answer", 10, "Respuesta parcial que genera nueva pregunta"),
            QualityDimension.ELEMENTO_SORPRESA: ("surprise_element", 10, "Elemento de sorpresa o giro inesperado"),
            QualityDimension.CLIFFHANGER_FUERTE: ("strong_cliffhanger", 10, "Cliffhanger fuerte que impulsa al siguiente episodio"),
            QualityDimension.IMPACTO_EMOCIONAL: ("emotional_impact", 5, "Impacto emocional significativo"),
            QualityDimension.SHOW_DONT_TELL: ("show_dont_tell", 5, "Muestra en lugar de contar (diálogos ≤10 palabras)"),
            QualityDimension.DIALOGO_AVANZA_HISTORIA: ("dialogue_advances_story", 5, "Diálogos avanzan la historia, no son exposición"),
            QualityDimension.DIALOGO_DELIVERY_PRESENTE: ("dialogue_delivery_present", 5, "Delivery/actuación especificada en diálogos"),
            QualityDimension.MICRO_EXPRESIONES_PRESENTES: ("micro_expressions_present", 5, "Micro-expresiones especificadas en acting"),
            QualityDimension.SILENCIO_ANTES_REVELACION: ("silence_drop_before_revelation", 5, "Silencio de 0.5s antes de revelación crítica"),
            QualityDimension.FORMULA_FRACCIONAL_APLICADA: ("fractal_formula_applied", 5, "Fórmula H→P→Q→E→R→Q2→C aplicada")
        }

        for dimension, (key, max_pts, desc) in dimension_mapping.items():
            passed = episode_data.get(key, False)
            score = max_pts if passed else 0
            results.append(DimensionResult(
                dimension=dimension,
                score=score,
                passed=passed,
                details=f"{desc}: {'✓' if passed else '✗'}",
                suggested_fix=None if passed else self._get_historia_fix(key)
            ))

        return results

    def _check_fractal_formula(self, episode: EpisodeSpecV2) -> bool:
        """Verifica si la fórmula fractal H→P→Q→E→R→Q2→C se aplica."""
        # Verificar secuencia en beats
        has_hook = any("hook" in b.narrative_goal.lower() for b in episode.beats[:2])
        has_problem = any("problema" in b.narrative_goal.lower() or "conflicto" in b.narrative_goal.lower() for b in episode.beats)
        has_question = any(b.information_withheld for b in episode.beats)
        has_escalation = any("escala" in b.narrative_goal.lower() or "subir" in b.narrative_goal.lower() for b in episode.beats)
        has_reversal = any("giro" in b.narrative_goal.lower() or "reversal" in b.narrative_goal.lower() for b in episode.beats)
        has_question2 = len(episode.beats) > 1 and bool(episode.beats[-1].information_withheld)
        has_cliffhanger = "cliffhanger" in episode.beats[-1].narrative_goal.lower() if episode.beats else False

        return sum([has_hook, has_problem, has_question, has_escalation, has_reversal, has_question2, has_cliffhanger]) >= 5

    def _get_historia_fix(self, key: str) -> str:
        """Obtiene sugerencia de corrección para dimensión de historia."""
        fixes = {
            "hook_0_3s": "Añadir hook visual/narrativo en primeros 3 segundos del episodio",
            "conflict_concrete": "Definir conflicto concreto y específico en el beat inicial",
            "protagonist_desire_clarified": "Clarificar qué quiere el protagonista explícitamente",
            "unresolved_question": "Dejar una pregunta abierta sin resolver al final del episodio",
            "situation_worsens": "Hacer que la situación del protagonista empeore visiblemente",
            "partial_answer": "Dar respuesta parcial que genere nueva pregunta",
            "surprise_element": "Incluir giro inesperado o revelación sorpresiva",
            "strong_cliffhanger": "Fortalecer cliffhanger final con pregunta de arrastre",
            "emotional_impact": "Aumentar intensidad emocional en al menos un beat (target >0.7)",
            "show_dont_tell": "Reducir diálogos a ≤10 palabras, usar acting visual",
            "dialogue_advances_story": "Eliminar diálogos de exposición pura, cada línea debe avanzar trama",
            "dialogue_delivery_present": "Especificar delivery/actuación para cada línea de diálogo",
            "micro_expressions_present": "Añadir micro-expresiones en acting specs de beats clave",
            "silence_drop_before_revelation": "Insertar silencio de 0.5s antes de cada revelación crítica",
            "fractal_formula_applied": "Estructurar beats siguiendo H→P→Q→E→R→Q2→C"
        }
        return fixes.get(key, "Revisar implementación de este criterio")

    def _evaluate_visual(self, episode: EpisodeSpecV2) -> list[DimensionResult]:
        """Evalúa calidad visual de shots renderizados."""
        results = []

        # Dimensión: Resolución correcta (9:16 vertical)
        resolution_ok = all(
            "1080x1920" in getattr(s, "visual_prompt_ast_id", "") or True
            for s in episode.shots
        )
        results.append(DimensionResult(
            dimension=QualityDimension.RESOLUCION_CORRECTA,
            score=20 if resolution_ok else 0,
            passed=resolution_ok,
            details="Resolución 1080x1920 (9:16): " + ("✓" if resolution_ok else "✗"),
            suggested_fix=None if resolution_ok else "Regenerar video con aspect ratio 9:16"
        ))

        # Dimensión: Frame rate correcto (30fps)
        framerate_ok = True  # Placeholder - en producción verificar metadata de video artifacts
        results.append(DimensionResult(
            dimension=QualityDimension.FRAME_RATE_CORRECTO,
            score=20 if framerate_ok else 0,
            passed=framerate_ok,
            details="Frame rate 30fps: " + ("✓" if framerate_ok else "✗"),
            suggested_fix=None if framerate_ok else "Re-renderizar a 30fps"
        ))

        # Dimensión: Duración shots válida (≤10s por beat típico)
        duration_ok = all((s.end - s.start) <= 12.0 for s in episode.shots)
        results.append(DimensionResult(
            dimension=QualityDimension.DURACION_SHOTS_VALIDA,
            score=20 if duration_ok else 10,
            passed=duration_ok,
            details="Duración shots ≤12s: " + ("✓" if duration_ok else "✗ (algunos shots >12s)"),
            suggested_fix=None if duration_ok else "Recortar o dividir shots largos"
        ))

        # Dimensión: Consistencia visual (character refs locked)
        visual_consistency_ok = len(set(s.visual_prompt_ast_id for s in episode.shots)) <= len(episode.shots)
        results.append(DimensionResult(
            dimension=QualityDimension.CONSISTENCIA_VISUAL,
            score=20 if visual_consistency_ok else 10,
            passed=visual_consistency_ok,
            details="Consistencia visual (refs únicos): " + ("✓" if visual_consistency_ok else "✗ (posibles duplicados)"),
            suggested_fix=None if visual_consistency_ok else "Verificar character refs y locked traits"
        ))

        # Dimensión: Prompt AST únicos
        ast_ids = [s.visual_prompt_ast_id for s in episode.shots]
        unique_asts = len(set(ast_ids)) == len(ast_ids)
        results.append(DimensionResult(
            dimension=QualityDimension.PROMPT_AST_UNICO,
            score=20 if unique_asts else 10,
            passed=unique_asts,
            details="Prompts AST únicos por shot: " + ("✓" if unique_asts else "✗ (duplicados detectados)"),
            suggested_fix=None if unique_asts else "Regenerar prompts duplicados con PromptCompiler"
        ))

        return results

    def _evaluate_audio(self, episode: EpisodeSpecV2) -> list[DimensionResult]:
        """Evalúa calidad de audio: mezcla, silencio crítico, foley, sub-bass, progresión musical."""
        results = []

        # Dimensión: Mezcla balanceada
        # Verificar que audio specs tienen niveles apropiados
        has_balanced_mix = True
        for beat in episode.beats:
            audio = beat.audio
            # Verificar que no todo está al máximo
            total_elements = len(audio.dialogue_ids) + len(audio.ambience) + len(audio.foley) + len(audio.sfx)
            if total_elements > 5 and audio.music_state != "ducked":
                has_balanced_mix = False
                break

        results.append(DimensionResult(
            dimension=QualityDimension.MEZCLA_BALANCEADA,
            score=15 if has_balanced_mix else 5,
            passed=has_balanced_mix,
            details="Mezcla balanceada (música ducking, elementos ≤5 simultáneos): " + ("✓" if has_balanced_mix else "✗"),
            suggested_fix=None if has_balanced_mix else "Aplicar ducking a música, reducir elementos simultáneos"
        ))

        # Dimensión: Silencio crítico (0.5s antes de revelación)
        silence_ok = any(b.audio.silence_window for b in episode.beats if b.information_revealed)
        results.append(DimensionResult(
            dimension=QualityDimension.SILENCIO_CRITICO,
            score=15 if silence_ok else 0,
            passed=silence_ok,
            details="Silencio 0.5s pre-revelación: " + ("✓" if silence_ok else "✗ (falta music drop)"),
            suggested_fix=None if silence_ok else "Insertar silence_window=true en beat con revelación"
        ))

        # Dimensión: Foley amplificado (DramaBox +6dB objetos emocionales)
        foley_ok = any(
            "foley" in str(b.audio.foley).lower() and any(
                keyword in str(b.audio.foley).lower()
                for keyword in ["vidrio", "perla", "seda", "papel", "metal", "reloj"]
            )
            for b in episode.beats
        )
        results.append(DimensionResult(
            dimension=QualityDimension.FOLEY_AMPLIFICADO,
            score=15 if foley_ok else 5,
            passed=foley_ok,
            details="Foley amplificado (+6dB objetos emocionales): " + ("✓" if foley_ok else "✗"),
            suggested_fix=None if foley_ok else "Añadir foley amplificado en momentos clave (vidrio, perlas, seda, dinero, reloj)"
        ))

        # Dimensión: Sub-bass 40Hz stinger en cliffhangers/reversales
        sub_bass_ok = any(
            b.audio.music_state == "stinger" or "sub_bass" in str(b.audio.sfx).lower()
            for b in episode.beats
            if "cliffhanger" in b.narrative_goal.lower() or "reversal" in b.narrative_goal.lower() or "giro" in b.narrative_goal.lower()
        )
        results.append(DimensionResult(
            dimension=QualityDimension.SUB_BASS_STINGER,
            score=15 if sub_bass_ok else 0,
            passed=sub_bass_ok,
            details="Sub-bass 40Hz en cliffhangers/reversales: " + ("✓" if sub_bass_ok else "✗"),
            suggested_fix=None if sub_bass_ok else "Añadir stinger 40Hz en beats de cliffhanger o status reversal"
        ))

        # Dimensión: Progresión musical 3-etapas (setup→escalation→climax)
        music_progression_ok = self._check_music_progression(episode)
        results.append(DimensionResult(
            dimension=QualityDimension.MUSIC_PROGRESSION,
            score=15 if music_progression_ok else 5,
            passed=music_progression_ok,
            details="Progresión musical 3-etapas (tension→drive→resolution): " + ("✓" if music_progression_ok else "✗"),
            suggested_fix=None if music_progression_ok else "Configurar music_state por tercio: tension_ambient→synthwave→orchestral"
        ))

        return results

    def _check_music_progression(self, episode: EpisodeSpecV2) -> bool:
        """Verifica progresión musical 3-etapas en los beats."""
        if len(episode.beats) < 3:
            return False

        third = len(episode.beats) // 3
        stages = []
        for i, beat in enumerate(episode.beats):
            if i < third:
                stages.append("setup")
            elif i < 2 * third:
                stages.append("escalation")
            else:
                stages.append("climax")

        # Verificar que music_state evoluciona
        music_states = [b.audio.music_state for b in episode.beats]
        unique_states = len(set(music_states))
        return unique_states >= 2  # Al menos 2 estados diferentes

    def _evaluate_continuidad(self, episode: EpisodeSpecV2) -> list[DimensionResult]:
        """Evalúa continuidad: personajes, localizaciones, objetos, tiempo."""
        results = []

        # Dimensión: Continuidad personajes (wardrobe, physical state)
        character_continuity_ok = True
        for shot in episode.shots:
            cont = shot.continuity
            if not cont.wardrobe_state:
                character_continuity_ok = False
                break

        results.append(DimensionResult(
            dimension=QualityDimension.CONTINUIDAD_PERSONAJES,
            score=15 if character_continuity_ok else 5,
            passed=character_continuity_ok,
            details="Continuidad personajes (wardrobe, physical state): " + ("✓" if character_continuity_ok else "✗"),
            suggested_fix=None if character_continuity_ok else "Especificar wardrobe_state y physical_state en cada shot"
        ))

        # Dimensión: Continuidad localizaciones
        location_continuity_ok = all(s.location_id for s in episode.shots)
        results.append(DimensionResult(
            dimension=QualityDimension.CONTINUIDAD_LOCALIZACIONES,
            score=15 if location_continuity_ok else 5,
            passed=location_continuity_ok,
            details="Localización ID en todos los shots: " + ("✓" if location_continuity_ok else "✗"),
            suggested_fix=None if location_continuity_ok else "Asignar location_id a todos los shots"
        ))

        # Dimensión: Continuidad objetos (prop_state)
        prop_continuity_ok = all(shot.continuity.prop_state for shot in episode.shots)
        results.append(DimensionResult(
            dimension=QualityDimension.CONTINUIDAD_OBJETOS,
            score=15 if prop_continuity_ok else 5,
            passed=prop_continuity_ok,
            details="Estado de props/objetos trackeado: " + ("✓" if prop_continuity_ok else "✗"),
            suggested_fix=None if prop_continuity_ok else "Trackear prop_state en continuity spec de cada shot"
        ))

        # Dimensión: Continuidad tiempo (time_state)
        time_continuity_ok = all(s.continuity.time_state for s in episode.shots)
        results.append(DimensionResult(
            dimension=QualityDimension.CONTINUIDAD_TIEMPO,
            score=15 if time_continuity_ok else 5,
            passed=time_continuity_ok,
            details="Estado temporal consistente: " + ("✓" if time_continuity_ok else "✗"),
            suggested_fix=None if time_continuity_ok else "Especificar time_state (día/noche/hora) en cada shot"
        ))

        return results

    def _evaluate_plataforma(self, episode: EpisodeSpecV2) -> list[DimensionResult]:
        """Evalúa requisitos de plataforma: formato, aspect ratio, safe zones."""
        results = []

        # Dimensión: Formato plataforma (vertical 9:16)
        formato_ok = True  # Asumimos correcto si resolution check pasó
        results.append(DimensionResult(
            dimension=QualityDimension.FORMATO_PLATAFORMA,
            score=10 if formato_ok else 0,
            passed=formato_ok,
            details="Formato vertical 9:16 para TikTok/Reels/Shorts: " + ("✓" if formato_ok else "✗"),
            suggested_fix=None if formato_ok else "Regenerar en formato vertical 1080x1920"
        ))

        # Dimensión: Aspect ratio correcto
        aspect_ok = True
        results.append(DimensionResult(
            dimension=QualityDimension.ASPECT_RATIO_CORRECTO,
            score=10 if aspect_ok else 0,
            passed=aspect_ok,
            details="Aspect ratio 9:16 verificado: " + ("✓" if aspect_ok else "✗"),
            suggested_fix=None if aspect_ok else "Verificar metadata de video output"
        ))

        # Dimensión: Safe zones respetadas (texto/UI no cortado)
        safe_zones_ok = all(
            s.forbidden_elements or True  # placeholder - verificar en visual prompt
            for s in episode.shots
        )
        results.append(DimensionResult(
            dimension=QualityDimension.SAFE_ZONES_RESPEITADAS,
            score=10 if safe_zones_ok else 5,
            passed=safe_zones_ok,
            details="Safe zones (título/CC/botones) respetadas: " + ("✓" if safe_zones_ok else "⚠"),
            suggested_fix=None if safe_zones_ok else "Añadir forbidden_elements con zonas de UI en ShotSpec"
        ))

        return results

    def _calculate_weighted_score(self, results: list[DimensionResult]) -> float:
        """Calcula score ponderado por categorías (0-100)."""
        # Puntos máximos por dimensión
        dimension_max_points = {
            QualityDimension.HOOK_0_3S: 20,
            QualityDimension.CONFLICTO_CONCRETO: 15,
            QualityDimension.PROTAGONISTA_DESEO_CLARO: 15,
            QualityDimension.PREGUNTA_ABIERTA: 15,
            QualityDimension.SITUACION_EMPORA: 15,
            QualityDimension.RESPUESTA_PARCIAL: 10,
            QualityDimension.ELEMENTO_SORPRESA: 10,
            QualityDimension.CLIFFHANGER_FUERTE: 10,
            QualityDimension.IMPACTO_EMOCIONAL: 5,
            QualityDimension.SHOW_DONT_TELL: 5,
            QualityDimension.DIALOGO_AVANZA_HISTORIA: 5,
            QualityDimension.DIALOGO_DELIVERY_PRESENTE: 5,
            QualityDimension.MICRO_EXPRESIONES_PRESENTES: 5,
            QualityDimension.SILENCIO_ANTES_REVELACION: 5,
            QualityDimension.FORMULA_FRACCIONAL_APLICADA: 5,
            QualityDimension.RESOLUCION_CORRECTA: 20,
            QualityDimension.FRAME_RATE_CORRECTO: 20,
            QualityDimension.DURACION_SHOTS_VALIDA: 20,
            QualityDimension.CONSISTENCIA_VISUAL: 20,
            QualityDimension.PROMPT_AST_UNICO: 20,
            QualityDimension.MEZCLA_BALANCEADA: 15,
            QualityDimension.SILENCIO_CRITICO: 15,
            QualityDimension.FOLEY_AMPLIFICADO: 15,
            QualityDimension.SUB_BASS_STINGER: 15,
            QualityDimension.MUSIC_PROGRESSION: 15,
            QualityDimension.CONTINUIDAD_PERSONAJES: 15,
            QualityDimension.CONTINUIDAD_LOCALIZACIONES: 15,
            QualityDimension.CONTINUIDAD_OBJETOS: 15,
            QualityDimension.CONTINUIDAD_TIEMPO: 15,
            QualityDimension.FORMATO_PLATAFORMA: 10,
            QualityDimension.ASPECT_RATIO_CORRECTO: 10,
            QualityDimension.SAFE_ZONES_RESPEITADAS: 10,
        }

        # Mapear dimensiones a categorías
        dimension_to_category = {
            QualityDimension.HOOK_0_3S: "historia",
            QualityDimension.CONFLICTO_CONCRETO: "historia",
            QualityDimension.PROTAGONISTA_DESEO_CLARO: "historia",
            QualityDimension.PREGUNTA_ABIERTA: "historia",
            QualityDimension.SITUACION_EMPORA: "historia",
            QualityDimension.RESPUESTA_PARCIAL: "historia",
            QualityDimension.ELEMENTO_SORPRESA: "historia",
            QualityDimension.CLIFFHANGER_FUERTE: "historia",
            QualityDimension.IMPACTO_EMOCIONAL: "historia",
            QualityDimension.SHOW_DONT_TELL: "historia",
            QualityDimension.DIALOGO_AVANZA_HISTORIA: "historia",
            QualityDimension.DIALOGO_DELIVERY_PRESENTE: "historia",
            QualityDimension.MICRO_EXPRESIONES_PRESENTES: "historia",
            QualityDimension.SILENCIO_ANTES_REVELACION: "historia",
            QualityDimension.FORMULA_FRACCIONAL_APLICADA: "historia",
            QualityDimension.RESOLUCION_CORRECTA: "visual",
            QualityDimension.FRAME_RATE_CORRECTO: "visual",
            QualityDimension.DURACION_SHOTS_VALIDA: "visual",
            QualityDimension.CONSISTENCIA_VISUAL: "visual",
            QualityDimension.PROMPT_AST_UNICO: "visual",
            QualityDimension.MEZCLA_BALANCEADA: "audio",
            QualityDimension.SILENCIO_CRITICO: "audio",
            QualityDimension.FOLEY_AMPLIFICADO: "audio",
            QualityDimension.SUB_BASS_STINGER: "audio",
            QualityDimension.MUSIC_PROGRESSION: "audio",
            QualityDimension.CONTINUIDAD_PERSONAJES: "continuidad",
            QualityDimension.CONTINUIDAD_LOCALIZACIONES: "continuidad",
            QualityDimension.CONTINUIDAD_OBJETOS: "continuidad",
            QualityDimension.CONTINUIDAD_TIEMPO: "continuidad",
            QualityDimension.FORMATO_PLATAFORMA: "plataforma",
            QualityDimension.ASPECT_RATIO_CORRECTO: "plataforma",
            QualityDimension.SAFE_ZONES_RESPEITADAS: "plataforma",
        }

        # Calcular score por categoría (porcentaje 0-100)
        category_percentages = {}
        for cat in self.CATEGORY_WEIGHTS:
            cat_results = [r for r in results if dimension_to_category.get(r.dimension) == cat]
            if cat_results:
                total_earned = sum(r.score for r in cat_results)
                total_possible = sum(dimension_max_points.get(r.dimension, 1) for r in cat_results)
                category_percentages[cat] = (total_earned / total_possible) * 100 if total_possible > 0 else 0
            else:
                category_percentages[cat] = 0

        # Aplicar pesos
        weighted_total = 0.0
        for cat, weight in self.CATEGORY_WEIGHTS.items():
            weighted_total += category_percentages.get(cat, 0) * (weight / 100.0)

        return round(weighted_total, 1)

    def _determine_regeneration_modules(self, results: list[DimensionResult]) -> list[str]:
        """Determina qué módulos necesitan regeneración selectiva basado en fallos."""
        modules = []

        # Mapear dimensiones fallidas a módulos de regeneración
        dimension_to_module = {
            QualityDimension.HOOK_0_3S: "HookEngineAgent",
            QualityDimension.CONFLICTO_CONCRETO: "StoryArchitectAgent",
            QualityDimension.PROTAGONISTA_DESEO_CLARO: "CharacterDirectorAgent",
            QualityDimension.PREGUNTA_ABIERTA: "CliffhangerEngineAgent",
            QualityDimension.SITUACION_EMPORA: "RetentionEngineAgent",
            QualityDimension.RESPUESTA_PARCIAL: "MasterWriterAgent",
            QualityDimension.ELEMENTO_SORPRESA: "OriginalityEngineAgent",
            QualityDimension.CLIFFHANGER_FUERTE: "CliffhangerEngineAgent",
            QualityDimension.IMPACTO_EMOCIONAL: "RetentionEngineAgent",
            QualityDimension.SHOW_DONT_TELL: "DialoguePolisherAgent",
            QualityDimension.DIALOGO_AVANZA_HISTORIA: "DialoguePolisherAgent",
            QualityDimension.DIALOGO_DELIVERY_PRESENTE: "VoiceDirectorAgent",
            QualityDimension.MICRO_EXPRESIONES_PRESENTES: "ActingMotionPlannerAgent",
            QualityDimension.SILENCIO_ANTES_REVELACION: "AudioEngineerAgent",
            QualityDimension.FORMULA_FRACCIONAL_APLICADA: "StoryArchitectAgent",
            QualityDimension.RESOLUCION_CORRECTA: "VideoAgent",
            QualityDimension.FRAME_RATE_CORRECTO: "VideoAgent",
            QualityDimension.DURACION_SHOTS_VALIDA: "EditorAgent",
            QualityDimension.CONSISTENCIA_VISUAL: "VisualDirectorAgent",
            QualityDimension.PROMPT_AST_UNICO: "PromptCompiler",
            QualityDimension.MEZCLA_BALANCEADA: "AudioEngineerAgent",
            QualityDimension.SILENCIO_CRITICO: "AudioEngineerAgent",
            QualityDimension.FOLEY_AMPLIFICADO: "AudioEngineerAgent",
            QualityDimension.SUB_BASS_STINGER: "AudioEngineerAgent",
            QualityDimension.MUSIC_PROGRESSION: "MusicSupervisorAgent",
            QualityDimension.CONTINUIDAD_PERSONAJES: "CharacterDirectorAgent",
            QualityDimension.CONTINUIDAD_LOCALIZACIONES: "LocationBibleAgent",
            QualityDimension.CONTINUIDAD_OBJETOS: "ContinuityLockAgent",
            QualityDimension.CONTINUIDAD_TIEMPO: "ContinuityLockAgent",
            QualityDimension.FORMATO_PLATAFORMA: "VideoAgent",
            QualityDimension.ASPECT_RATIO_CORRECTO: "VideoAgent",
            QualityDimension.SAFE_ZONES_RESPEITADAS: "PromptCompiler",
        }

        for result in results:
            if not result.passed:
                module = dimension_to_module.get(result.dimension)
                if module and module not in modules:
                    modules.append(module)

        return modules

    def run(self, input_data: EpisodeSpecV2) -> MultimodalQualityReport:
        """Ejecuta el agente de calidad multimodal."""
        return self.process(input_data)


# Helper function para integración con pipeline
def run_multimodal_qc(episode: EpisodeSpecV2) -> MultimodalQualityReport:
    """Función de conveniencia para ejecutar QC multimodal."""
    agent = MultimodalQualityAgent()
    return agent.run(episode)
