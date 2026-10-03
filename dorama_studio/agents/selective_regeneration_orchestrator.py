"""
Selective Regeneration Orchestrator - Fase 13
Orquesta la regeneración selectiva de módulos fallidos basándose en el reporte de QC multimodal.
Coordina qué agentes re-ejecutar y cómo integrar los resultados.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.multimodal_quality_agent import (
    MultimodalQualityAgent,
    MultimodalQualityReport,
)
from dorama_studio.contracts.v2_schemas import EpisodeSpecV2, QualityState

logger = logging.getLogger(__name__)


class RegenerationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class RegenerationTask:
    """Tarea de regeneración individual."""
    module_name: str
    agent_class: str
    dimension_triggered: list[str]
    status: RegenerationStatus = RegenerationStatus.PENDING
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] | None = None
    error: str | None = None
    attempts: int = 0
    max_attempts: int = 3
    latency_ms: int = 0


@dataclass
class RegenerationPlan:
    """Plan completo de regeneración selectiva."""
    episode_id: str
    quality_report: MultimodalQualityReport
    tasks: list[RegenerationTask] = field(default_factory=list)
    overall_status: RegenerationStatus = RegenerationStatus.PENDING
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None


# Mapeo de módulos a agentes canónicos
MODULE_TO_AGENT = {
    "HookEngineAgent": "dorama_studio.agents.hook_engine_agent.HookEngineAgent",
    "StoryArchitectAgent": "dorama_studio.agents.story_architect_agent.StoryArchitectAgent",
    "CharacterDirectorAgent": "dorama_studio.agents.character_director_agent.CharacterDirectorAgent",
    "CliffhangerEngineAgent": "dorama_studio.agents.narrative.episode_scorer.EpisodeScorer",
    "RetentionEngineAgent": "dorama_studio.agents.narrative.retention_engine.RetentionEngineAgent",
    "MasterWriterAgent": "dorama_studio.agents.narrative.master_writer.MasterWriterAgent",
    "OriginalityEngineAgent": "dorama_studio.agents.originality_engine_agent.OriginalityEngineAgent",
    "DialoguePolisherAgent": "dorama_studio.agents.narrative.dialogue_polisher.DialoguePolisherAgent",
    "VoiceDirectorAgent": "dorama_studio.agents.audio.voice_director_agent.VoiceDirectorAgent",
    "ActingMotionPlannerAgent": "dorama_studio.agents.acting_motion_planner_agent.ActingMotionPlannerAgent",
    "AudioEngineerAgent": "dorama_studio.agents.audio_engineer_agent.AudioEngineerAgent",
    "MusicSupervisorAgent": "dorama_studio.agents.audio.music_supervisor_agent.MusicSupervisorAgent",
    "LocationBibleAgent": "dorama_studio.agents.narrative.location_bible_agent.LocationBibleAgent",
    "ContinuityLockAgent": "dorama_studio.agents.narrative.continuity_lock_agent.ContinuityLockAgent",
    "VideoAgent": "dorama_studio.agents.production.video_agent.VideoAgent",
    "EditorAgent": "dorama_studio.agents.production.editor_agent.EditorAgent",
    "PromptCompiler": "dorama_studio.pipeline.prompt_compiler.PromptCompiler",
    "VisualDirectorAgent": "dorama_studio.agents.visual_director_agent.VisualDirectorAgent",
}


def import_agent_class(class_path: str):
    """Importa dinámicamente una clase de agente."""
    import importlib
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class SelectiveRegenerationOrchestrator(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Orquestador de Regeneración Selectiva.
    Recibe un reporte de QC multimodal y ejecuta regeneración selectiva
    solo en los módulos que fallaron, iterando hasta pasar o agotar intentos.
    """

    def __init__(self, max_iterations: int = 2):
        super().__init__("SelectiveRegenerationOrchestrator")
        self.max_iterations = max_iterations
        self.quality_agent = MultimodalQualityAgent()
        self._agent_cache: dict[str, Any] = {}

    def _get_agent(self, module_name: str):
        """Obtiene instancia de agente (con cache)."""
        if module_name not in self._agent_cache:
            class_path = MODULE_TO_AGENT.get(module_name)
            if not class_path:
                logger.warning(f"No agent mapping for module: {module_name}")
                return None
            try:
                agent_class = import_agent_class(class_path)
                self._agent_cache[module_name] = agent_class()
                logger.info(f"Loaded agent: {module_name} from {class_path}")
            except Exception as e:
                logger.error(f"Failed to load agent {module_name}: {e}")
                return None
        return self._agent_cache[module_name]

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Ejecuta regeneración selectiva basada en reporte de QC.

        Args:
            validated_input: Dict con:
                - episode: EpisodeSpecV2
                - quality_report: MultimodalQualityReport (opcional, se genera si no se provee)
                - max_iterations: int (opcional, default=2)

        Returns:
            Dict con plan de regeneración ejecutado y episodio actualizado
        """
        episode = validated_input.get("episode")
        quality_report = validated_input.get("quality_report")
        max_iterations = validated_input.get("max_iterations", self.max_iterations)

        if not episode:
            return {"status": "error", "message": "Episode required in input"}

        # Si no hay reporte de calidad, generarlo
        if not quality_report:
            logger.info("No quality report provided, generating multimodal QC...")
            quality_report = self.quality_agent.run(episode)

        # Crear plan de regeneración
        plan = self._create_regeneration_plan(episode, quality_report)

        # Ejecutar iteraciones de regeneración
        for iteration in range(max_iterations):
            logger.info(f"Regeneration iteration {iteration + 1}/{max_iterations}")
            plan = self._execute_regeneration_iteration(plan, episode)

            # Re-evaluar calidad después de cada iteración
            quality_report = self.quality_agent.run(episode)
            plan.quality_report = quality_report

            # Verificar si pasó
            if quality_report.overall_state == QualityState.PASS:
                logger.info(f"Quality PASS achieved after iteration {iteration + 1}")
                plan.overall_status = RegenerationStatus.COMPLETED
                plan.completed_at = time.time()
                break

            # Actualizar tareas basadas en nuevo reporte
            plan = self._update_regeneration_plan(plan, quality_report)

        else:
            # Se agotaron iteraciones sin pasar
            logger.warning(f"Max iterations ({max_iterations}) reached without PASS")
            plan.overall_status = RegenerationStatus.FAILED
            plan.completed_at = time.time()

        return {
            "status": plan.overall_status.value,
            "episode": episode,
            "final_quality_report": quality_report,
            "regeneration_plan": plan,
            "iterations_executed": iteration + 1,
            "modules_regenerated": [t.module_name for t in plan.tasks if t.status == RegenerationStatus.COMPLETED],
            "modules_failed": [t.module_name for t in plan.tasks if t.status == RegenerationStatus.FAILED]
        }

    def _create_regeneration_plan(
        self,
        episode: EpisodeSpecV2,
        quality_report: MultimodalQualityReport
    ) -> RegenerationPlan:
        """Crea plan de regeneración a partir de reporte de QC."""
        tasks = []

        for module_name in quality_report.regeneration_modules:
            class_path = MODULE_TO_AGENT.get(module_name)
            if not class_path:
                logger.warning(f"No agent mapping for regeneration module: {module_name}")
                continue

            # Encontrar dimensiones que dispararon este módulo
            triggered_dims = [
                r.dimension.value for r in quality_report.dimension_results
                if not r.passed and self._module_for_dimension(r.dimension.value) == module_name
            ]

            task = RegenerationTask(
                module_name=module_name,
                agent_class=class_path,
                dimension_triggered=triggered_dims,
                max_attempts=3
            )
            tasks.append(task)

        return RegenerationPlan(
            episode_id=f"ep_{episode.episode_number}",
            quality_report=quality_report,
            tasks=tasks
        )

    def _module_for_dimension(self, dimension: str) -> str | None:
        """Mapea dimensión a módulo de regeneración (inverso del quality agent)."""
        dimension_to_module = {
            "hook_0_3s": "HookEngineAgent",
            "conflicto_concreto": "StoryArchitectAgent",
            "protagonista_deseo_claro": "CharacterDirectorAgent",
            "pregunta_abierta": "CliffhangerEngineAgent",
            "situacion_empeora": "RetentionEngineAgent",
            "respuesta_parcial": "MasterWriterAgent",
            "elemento_sorpresa": "OriginalityEngineAgent",
            "cliffhanger_fuerte": "CliffhangerEngineAgent",
            "impacto_emocional": "RetentionEngineAgent",
            "show_dont_tell": "DialoguePolisherAgent",
            "dialogo_avanza_historia": "DialoguePolisherAgent",
            "dialogo_delivery_presente": "VoiceDirectorAgent",
            "micro_expresiones_presentes": "ActingMotionPlannerAgent",
            "silencio_antes_revelacion": "AudioEngineerAgent",
            "formula_fraccional_aplicada": "StoryArchitectAgent",
            "resolucion_correcta": "VideoAgent",
            "frame_rate_correcto": "VideoAgent",
            "duracion_shots_valida": "EditorAgent",
            "consistencia_visual": "VisualDirectorAgent",
            "prompt_ast_unico": "PromptCompiler",
            "mezcla_balanceada": "AudioEngineerAgent",
            "silencio_critico": "AudioEngineerAgent",
            "foley_amplificado": "AudioEngineerAgent",
            "sub_bass_stinger": "AudioEngineerAgent",
            "music_progression": "MusicSupervisorAgent",
            "continuidad_personajes": "CharacterDirectorAgent",
            "continuidad_localizaciones": "LocationBibleAgent",
            "continuidad_objetos": "ContinuityLockAgent",
            "continuidad_tiempo": "ContinuityLockAgent",
            "formato_plataforma": "VideoAgent",
            "aspect_ratio_correcto": "VideoAgent",
            "safe_zones_respetadas": "PromptCompiler",
        }
        return dimension_to_module.get(dimension)

    def _execute_regeneration_iteration(
        self,
        plan: RegenerationPlan,
        episode: EpisodeSpecV2
    ) -> RegenerationPlan:
        """Ejecuta una iteración completa de regeneración."""
        pending_tasks = [t for t in plan.tasks if t.status == RegenerationStatus.PENDING]

        for task in pending_tasks:
            if task.attempts >= task.max_attempts:
                task.status = RegenerationStatus.FAILED
                logger.warning(f"Module {task.module_name} exceeded max attempts")
                continue

            task.status = RegenerationStatus.IN_PROGRESS
            task.attempts += 1
            start_time = time.time()

            try:
                # Preparar input para el agente basado en el módulo
                agent_input = self._prepare_agent_input(task.module_name, episode, plan.quality_report)
                task.input_data = agent_input

                # Ejecutar agente
                agent = self._get_agent(task.module_name)
                if not agent:
                    task.status = RegenerationStatus.FAILED
                    task.error = "Agent not found or failed to load"
                    continue

                logger.info(f"Executing {task.module_name} (attempt {task.attempts})")
                output = agent.run(agent_input)
                task.output_data = output
                task.status = RegenerationStatus.COMPLETED

                # Integrar output en el episodio
                self._integrate_output(episode, task.module_name, output)

                logger.info(f"Completed {task.module_name} in {int((time.time() - start_time) * 1000)}ms")

            except Exception as e:
                task.status = RegenerationStatus.FAILED
                task.error = str(e)
                logger.error(f"Failed {task.module_name}: {e}")

            task.latency_ms = int((time.time() - start_time) * 1000)

        return plan

    def _prepare_agent_input(
        self,
        module_name: str,
        episode: EpisodeSpecV2,
        quality_report: MultimodalQualityReport
    ) -> dict[str, Any]:
        """Prepara input específico para cada agente basado en el módulo."""
        # Input base común
        base_input = {
            "episode": episode,
            "quality_report": quality_report,
            "failed_dimensions": [
                r.dimension.value for r in quality_report.dimension_results if not r.passed
            ]
        }

        # Inputs específicos por módulo
        specific_inputs = {
            "HookEngineAgent": {
                **base_input,
                "task": "regenerate_hook",
                "focus": "explosive_opening_3s"
            },
            "StoryArchitectAgent": {
                **base_input,
                "task": "regenerate_structure",
                "focus": "conflict_and_fractal"
            },
            "CharacterDirectorAgent": {
                **base_input,
                "task": "regenerate_character_state",
                "focus": "desire_wardrobe_continuity"
            },
            "CliffhangerEngineAgent": {
                **base_input,
                "task": "regenerate_cliffhanger",
                "focus": "strong_pull_next_episode"
            },
            "RetentionEngineAgent": {
                **base_input,
                "task": "regenerate_retention",
                "focus": "microbeat_pacing_questions"
            },
            "MasterWriterAgent": {
                **base_input,
                "task": "regenerate_dialogue",
                "focus": "show_dont_tell_advance_story"
            },
            "OriginalityEngineAgent": {
                **base_input,
                "task": "regenerate_twist",
                "focus": "surprise_element_novelty"
            },
            "DialoguePolisherAgent": {
                **base_input,
                "task": "polish_dialogue",
                "focus": "under_10_words_delivery"
            },
            "VoiceDirectorAgent": {
                **base_input,
                "task": "regenerate_voice_direction",
                "focus": "delivery_micro_expressions"
            },
            "ActingMotionPlannerAgent": {
                **base_input,
                "task": "regenerate_acting",
                "focus": "micro_expressions_gestures"
            },
            "AudioEngineerAgent": {
                **base_input,
                "task": "regenerate_audio",
                "focus": "silence_drop_foley_sub_bass"
            },
            "MusicSupervisorAgent": {
                **base_input,
                "task": "regenerate_music",
                "focus": "three_stage_progression"
            },
            "LocationBibleAgent": {
                **base_input,
                "task": "regenerate_location_continuity",
                "focus": "location_state_consistency"
            },
            "ContinuityLockAgent": {
                **base_input,
                "task": "fix_continuity",
                "focus": "prop_time_character_consistency"
            },
            "VideoAgent": {
                **base_input,
                "task": "regenerate_video",
                "focus": "resolution_framerate_format"
            },
            "EditorAgent": {
                **base_input,
                "task": "re_edit",
                "focus": "shot_duration_pacing"
            },
            "PromptCompiler": {
                **base_input,
                "task": "recompile_prompts",
                "focus": "unique_asts_safe_zones"
            },
            "VisualDirectorAgent": {
                **base_input,
                "task": "regenerate_visual_plan",
                "focus": "consistency_references"
            }
        }

        return specific_inputs.get(module_name, base_input)

    def _integrate_output(
        self,
        episode: EpisodeSpecV2,
        module_name: str,
        output: Any
    ) -> None:
        """Integra output del agente regenerado en el episodio."""
        # Esta es una integración simplificada - en producción sería más compleja
        # mapeando campos específicos del output a episode.beats, episode.shots, etc.

        logger.info(f"Integrating output from {module_name} into episode {episode.episode_number}")

        # Mapeo de módulos a qué parte del episodio actualizan
        integration_map = {
            "HookEngineAgent": "beats[0].narrative_goal",
            "StoryArchitectAgent": "beats (structure)",
            "CharacterDirectorAgent": "character_state_ref, shots[].continuity",
            "CliffhangerEngineAgent": "beats[-1].narrative_goal",
            "RetentionEngineAgent": "beats (pacing, questions)",
            "MasterWriterAgent": "dialogues, beats (dialogue_ids)",
            "OriginalityEngineAgent": "beats (twist, surprise)",
            "DialoguePolisherAgent": "dialogues (text, delivery)",
            "VoiceDirectorAgent": "dialogues (delivery), beats (acting)",
            "ActingMotionPlannerAgent": "beats (acting, motion)",
            "AudioEngineerAgent": "beats (audio), shots (audio)",
            "MusicSupervisorAgent": "beats (audio.music_state)",
            "LocationBibleAgent": "shots (location_id, continuity)",
            "ContinuityLockAgent": "shots (continuity)",
            "VideoAgent": "shots (visual_prompt_ast_id)",
            "EditorAgent": "shots (start, end)",
            "PromptCompiler": "shots (visual_prompt_ast_id, forbidden_elements)",
            "VisualDirectorAgent": "shots (camera, lighting, visual_prompt_ast_id)"
        }

        target = integration_map.get(module_name, "unknown")
        logger.debug(f"Module {module_name} updates: {target}")

        # En producción, aquí se haría merge real del output en episode
        # Por ahora solo logueamos

    def _update_regeneration_plan(
        self,
        plan: RegenerationPlan,
        quality_report: MultimodalQualityReport
    ) -> RegenerationPlan:
        """Actualiza plan de regeneración basado en nuevo reporte de QC."""
        # Marcar tareas completadas exitosamente como SKIPPED para siguiente iteración
        for task in plan.tasks:
            if task.status == RegenerationStatus.COMPLETED:
                task.status = RegenerationStatus.SKIPPED

        # Añadir nuevas tareas para dimensiones que siguen fallando
        for module_name in quality_report.regeneration_modules:
            if not any(t.module_name == module_name and t.status != RegenerationStatus.FAILED for t in plan.tasks):
                class_path = MODULE_TO_AGENT.get(module_name)
                if class_path:
                    triggered_dims = [
                        r.dimension.value for r in quality_report.dimension_results
                        if not r.passed and self._module_for_dimension(r.dimension.value) == module_name
                    ]
                    task = RegenerationTask(
                        module_name=module_name,
                        agent_class=class_path,
                        dimension_triggered=triggered_dims,
                        max_attempts=3
                    )
                    plan.tasks.append(task)

        return plan

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Ejecuta el orquestador de regeneración selectiva."""
        return self.process(input_data)


# Función de conveniencia
def run_selective_regeneration(
    episode: EpisodeSpecV2,
    quality_report: MultimodalQualityReport | None = None,
    max_iterations: int = 2
) -> dict[str, Any]:
    """Función de conveniencia para ejecutar regeneración selectiva."""
    orchestrator = SelectiveRegenerationOrchestrator(max_iterations=max_iterations)
    return orchestrator.run({
        "episode": episode,
        "quality_report": quality_report,
        "max_iterations": max_iterations
    })
