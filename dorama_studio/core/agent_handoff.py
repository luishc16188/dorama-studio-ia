"""
Agent Handoff Optimization - Schemas estructurados para pasar solo campos necesarios entre agentes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Type, get_type_hints
from enum import Enum
import json


class HandoffFieldType(str, Enum):
    """Tipos de campos en handoff."""
    REQUIRED = "required"       # Campo obligatorio para el agente receptor
    OPTIONAL = "optional"       # Campo opcional
    DERIVED = "derived"         # Campo derivado (no viene del agente anterior)
    CONTEXT = "context"         # Campo de contexto (no output del agente anterior)


@dataclass
class HandoffField:
    """Definición de un campo en el handoff."""
    name: str
    field_type: HandoffFieldType = HandoffFieldType.REQUIRED
    description: str = ""
    source_agent: str = ""      # Agente que produce este campo
    target_agents: List[str] = field(default_factory=list)  # Agentes que lo consumen
    schema_type: str = "Any"    # Tipo de dato (para documentación)
    max_size_chars: int = 0     # Límite de tamaño (0 = sin límite)
    compression_hint: str = ""  # Pista de compresión (ej: "summary", "ids_only", "hash")


@dataclass
class AgentHandoffSchema:
    """
    Schema de handoff para un agente.
    Define qué inputs requiere y qué outputs produce.
    """
    agent_name: str
    inputs: List[HandoffField] = field(default_factory=list)
    outputs: List[HandoffField] = field(default_factory=list)

    def get_required_input_names(self) -> List[str]:
        return [f.name for f in self.inputs if f.field_type == HandoffFieldType.REQUIRED]

    def get_optional_input_names(self) -> List[str]:
        return [f.name for f in self.inputs if f.field_type == HandoffFieldType.OPTIONAL]

    def get_output_names(self) -> List[str]:
        return [f.name for f in self.outputs]

    def get_fields_for_target(self, target_agent: str) -> List[HandoffField]:
        """Obtiene campos que este agente produce para un agente target específico."""
        return [f for f in self.outputs if target_agent in f.target_agents]

    def validate_input(self, data: Dict[str, Any]) -> List[str]:
        """Valida que los inputs requeridos estén presentes. Retorna lista de faltantes."""
        missing = []
        for field in self.inputs:
            if field.field_type == HandoffFieldType.REQUIRED and field.name not in data:
                missing.append(field.name)
        return missing

    def filter_output_for_target(self, output_data: Dict[str, Any], target_agent: str) -> Dict[str, Any]:
        """Filtra outputs para pasar solo lo que el target_agent necesita."""
        relevant_fields = self.get_fields_for_target(target_agent)
        filtered = {}
        for field in relevant_fields:
            if field.name in output_data:
                value = output_data[field.name]
                # Aplicar compresión si hay hint
                if field.compression_hint:
                    value = self._compress_value(value, field.compression_hint, field.max_size_chars)
                filtered[field.name] = value
        return filtered

    def _compress_value(self, value: Any, hint: str, max_chars: int) -> Any:
        """Aplica compresión según hint."""
        if hint == "ids_only" and isinstance(value, list):
            # Extraer solo IDs de objetos
            return [v.get("id") if isinstance(v, dict) else getattr(v, "id", str(v)) for v in value]
        elif hint == "summary" and isinstance(value, str) and len(value) > max_chars > 0:
            return value[:max_chars] + "... [truncated]"
        elif hint == "hash" and isinstance(value, (str, dict)):
            import hashlib
            content = json.dumps(value, sort_keys=True) if isinstance(value, dict) else value
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        elif hint == "keys_only" and isinstance(value, dict):
            return list(value.keys())
        elif hint == "count_only" and isinstance(value, (list, dict)):
            return len(value)
        return value


class HandoffRegistry:
    """
    Registro central de schemas de handoff para todos los agentes.
    Permite resolver automáticamente qué datos pasar entre agentes.
    """

    def __init__(self):
        self._schemas: Dict[str, AgentHandoffSchema] = {}
        self._build_default_schemas()

    def _build_default_schemas(self):
        """Construye schemas por defecto para agentes conocidos."""

        # TrendHunterAgent
        self.register(AgentHandoffSchema(
            agent_name="TrendHunterAgent",
            inputs=[
                HandoffField("project_id", HandoffFieldType.REQUIRED, "Project identifier", "", ["TrendHunterAgent"]),
                HandoffField("season_id", HandoffFieldType.REQUIRED, "Season identifier", "", ["TrendHunterAgent"]),
            ],
            outputs=[
                HandoffField("trend_evidence", HandoffFieldType.REQUIRED, "Trend evidence artifact", "TrendHunterAgent",
                            ["StoryArchitectAgent", "MasterWriterAgent"], "dict", compression_hint="keys_only"),
                HandoffField("viral_ruleset", HandoffFieldType.REQUIRED, "Viral rules for hooks", "TrendHunterAgent",
                            ["HookEngineAgent", "MasterWriterAgent"], "list[str]", compression_hint="count_only"),
            ]
        ))

        # StoryArchitectAgent
        self.register(AgentHandoffSchema(
            agent_name="StoryArchitectAgent",
            inputs=[
                HandoffField("project_id", HandoffFieldType.REQUIRED, "", "", ["StoryArchitectAgent"]),
                HandoffField("season_id", HandoffFieldType.REQUIRED, "", "", ["StoryArchitectAgent"]),
                HandoffField("total_episodes", HandoffFieldType.REQUIRED, "", "", ["StoryArchitectAgent"]),
                HandoffField("trend_evidence_ref", HandoffFieldType.OPTIONAL, "", "TrendHunterAgent", ["StoryArchitectAgent"]),
            ],
            outputs=[
                HandoffField("season_bible", HandoffFieldType.REQUIRED, "Season bible artifact", "StoryArchitectAgent",
                            ["CharacterDirectorAgent", "LocationBibleAgent", "SeasonArcAgent"], "dict", compression_hint="keys_only"),
                HandoffField("episode_blueprints", HandoffFieldType.REQUIRED, "All episode blueprints", "StoryArchitectAgent",
                            ["MasterWriterAgent", "EpisodeRouterAgent"], "list[dict]", compression_hint="ids_only"),
                HandoffField("season_arc", HandoffFieldType.REQUIRED, "Season narrative arc", "StoryArchitectAgent",
                            ["SeasonArcAgent", "MasterWriterAgent"], "dict", compression_hint="summary"),
            ]
        ))

        # MasterWriterAgent
        self.register(AgentHandoffSchema(
            agent_name="MasterWriterAgent",
            inputs=[
                HandoffField("blueprint", HandoffFieldType.REQUIRED, "Episode blueprint", "StoryArchitectAgent", ["MasterWriterAgent"]),
                HandoffField("hook", HandoffFieldType.REQUIRED, "Hook pack", "HookEngineAgent", ["MasterWriterAgent"]),
                HandoffField("characters", HandoffFieldType.REQUIRED, "Character bibles", "CharacterDirectorAgent", ["MasterWriterAgent"], "list[dict]", compression_hint="ids_only"),
                HandoffField("viral_ruleset", HandoffFieldType.OPTIONAL, "Viral rules", "TrendHunterAgent", ["MasterWriterAgent"], "list[str]"),
                HandoffField("genome_context", HandoffFieldType.OPTIONAL, "Creative genome context", "FeedbackLoopAgent", ["MasterWriterAgent"]),
            ],
            outputs=[
                HandoffField("script", HandoffFieldType.REQUIRED, "Full script artifact", "MasterWriterAgent",
                            ["DialoguePolisherAgent", "RetentionEngineAgent", "CliffhangerEngineAgent", "DirectorEngineAgent"], "dict", compression_hint="keys_only"),
                HandoffField("beats", HandoffFieldType.REQUIRED, "9 beats with full detail", "MasterWriterAgent",
                            ["DialoguePolisherAgent", "RetentionEngineAgent", "CliffhangerEngineAgent", "DirectorEngineAgent", "ShotPlannerAgent"], "list[dict]", compression_hint="ids_only"),
            ]
        ))

        # HookEngineAgent
        self.register(AgentHandoffSchema(
            agent_name="HookEngineAgent",
            inputs=[
                HandoffField("episode_blueprint", HandoffFieldType.REQUIRED, "", "StoryArchitectAgent", ["HookEngineAgent"]),
                HandoffField("episode_number", HandoffFieldType.REQUIRED, "", "", ["HookEngineAgent"]),
                HandoffField("viral_ruleset", HandoffFieldType.OPTIONAL, "", "TrendHunterAgent", ["HookEngineAgent"]),
            ],
            outputs=[
                HandoffField("hook_pack", HandoffFieldType.REQUIRED, "Top 5 hooks", "HookEngineAgent",
                            ["MasterWriterAgent"], "dict", compression_hint="keys_only"),
            ]
        ))

        # DirectorEngineAgent
        self.register(AgentHandoffSchema(
            agent_name="DirectorEngineAgent",
            inputs=[
                HandoffField("episode_spec", HandoffFieldType.REQUIRED, "Full episode spec", "MasterWriterAgent", ["DirectorEngineAgent"], "dict", compression_hint="keys_only"),
                HandoffField("beats", HandoffFieldType.REQUIRED, "Beats from script", "MasterWriterAgent", ["DirectorEngineAgent"], "list[dict]", compression_hint="ids_only"),
            ],
            outputs=[
                HandoffField("director_plan", HandoffFieldType.REQUIRED, "Cinematic plan", "DirectorEngineAgent",
                            ["ShotPlannerAgent", "ActingMotionPlannerAgent"], "dict", compression_hint="keys_only"),
            ]
        ))

        # ShotPlannerAgent
        self.register(AgentHandoffSchema(
            agent_name="ShotPlannerAgent",
            inputs=[
                HandoffField("director_plan", HandoffFieldType.REQUIRED, "Director plan", "DirectorEngineAgent", ["ShotPlannerAgent"]),
                HandoffField("beats", HandoffFieldType.REQUIRED, "Beats", "MasterWriterAgent", ["ShotPlannerAgent"], "list[dict]", compression_hint="ids_only"),
            ],
            outputs=[
                HandoffField("shots", HandoffFieldType.REQUIRED, "Shot specifications", "ShotPlannerAgent",
                            ["ContinuityLockAgent", "PromptCompilerAgent", "VisualEngineAgent"], "list[dict]", compression_hint="ids_only"),
            ]
        ))

        # CharacterStateAgent
        self.register(AgentHandoffSchema(
            agent_name="CharacterStateAgent",
            inputs=[
                HandoffField("project_id", HandoffFieldType.REQUIRED, "", "", ["CharacterStateAgent"]),
                HandoffField("season_id", HandoffFieldType.REQUIRED, "", "", ["CharacterStateAgent"]),
                HandoffField("episode_number", HandoffFieldType.REQUIRED, "", "", ["CharacterStateAgent"]),
                HandoffField("beats", HandoffFieldType.REQUIRED, "Beats for state tracking", "MasterWriterAgent", ["CharacterStateAgent"], "list[dict]", compression_hint="ids_only"),
            ],
            outputs=[
                HandoffField("character_states", HandoffFieldType.REQUIRED, "Character states per beat", "CharacterStateAgent",
                            ["ContinuityLockAgent", "VisualEngineAgent", "ActingMotionPlannerAgent"], "list[dict]", compression_hint="keys_only"),
            ]
        ))

        # ContinuityLockAgent
        self.register(AgentHandoffSchema(
            agent_name="ContinuityLockAgent",
            inputs=[
                HandoffField("shots", HandoffFieldType.REQUIRED, "Shots to check", "ShotPlannerAgent", ["ContinuityLockAgent"], "list[dict]"),
                HandoffField("character_states", HandoffFieldType.OPTIONAL, "Character states", "CharacterStateAgent", ["ContinuityLockAgent"]),
            ],
            outputs=[
                HandoffField("continuity_report", HandoffFieldType.REQUIRED, "Continuity errors", "ContinuityLockAgent",
                            ["QualityCheckAgent", "SelectiveRegenerationAgent"], "list[dict]", compression_hint="count_only"),
            ]
        ))

        # PromptCompilerAgent
        self.register(AgentHandoffSchema(
            agent_name="PromptCompilerAgent",
            inputs=[
                HandoffField("shots", HandoffFieldType.REQUIRED, "Shots to compile", "ShotPlannerAgent", ["PromptCompilerAgent"], "list[dict]"),
                HandoffField("character_refs", HandoffFieldType.OPTIONAL, "Character visual refs", "CharacterDirectorAgent", ["PromptCompilerAgent"]),
            ],
            outputs=[
                HandoffField("prompt_asts", HandoffFieldType.REQUIRED, "Compiled prompts", "PromptCompilerAgent",
                            ["VisualEngineAgent", "VideoAgent"], "list[dict]", compression_hint="ids_only"),
            ]
        ))

        # VisualEngineAgent / VideoAgent
        self.register(AgentHandoffSchema(
            agent_name="VisualEngineAgent",
            inputs=[
                HandoffField("prompt_ast", HandoffFieldType.REQUIRED, "Compiled prompt", "PromptCompilerAgent", ["VisualEngineAgent"]),
                HandoffField("shot_id", HandoffFieldType.REQUIRED, "Shot identifier", "", ["VisualEngineAgent"]),
            ],
            outputs=[
                HandoffField("visual_artifact", HandoffFieldType.REQUIRED, "Video artifact", "VisualEngineAgent",
                            ["AudioMixerAgent", "EditorAgent", "QualityCheckAgent"], "dict", compression_hint="keys_only"),
            ]
        ))

        # AudioEngineerAgent
        self.register(AgentHandoffSchema(
            agent_name="AudioEngineerAgent",
            inputs=[
                HandoffField("shots", HandoffFieldType.REQUIRED, "Shots for SFX", "ShotPlannerAgent", ["AudioEngineerAgent"]),
                HandoffField("beats", HandoffFieldType.REQUIRED, "Beats for music", "MasterWriterAgent", ["AudioEngineerAgent"], "list[dict]", compression_hint="ids_only"),
                HandoffField("master_audio", HandoffFieldType.OPTIONAL, "Voice track for mixing", "VoiceDirectorAgent", ["AudioEngineerAgent"]),
            ],
            outputs=[
                HandoffField("sfx_artifacts", HandoffFieldType.REQUIRED, "SFX artifacts", "AudioEngineerAgent",
                            ["AudioMixerAgent"], "list[dict]", compression_hint="ids_only"),
                HandoffField("music_artifacts", HandoffFieldType.REQUIRED, "Music artifacts", "AudioEngineerAgent",
                            ["AudioMixerAgent"], "list[dict]", compression_hint="ids_only"),
            ]
        ))

        # EditorAgent
        self.register(AgentHandoffSchema(
            agent_name="EditorAgent",
            inputs=[
                HandoffField("visual_artifacts", HandoffFieldType.REQUIRED, "Video clips", "VisualEngineAgent", ["EditorAgent"], "list[dict]", compression_hint="ids_only"),
                HandoffField("master_audio", HandoffFieldType.REQUIRED, "Mixed audio", "AudioMixerAgent", ["EditorAgent"]),
                HandoffField("edit_plan", HandoffFieldType.OPTIONAL, "Edit plan", "DirectorEngineAgent", ["EditorAgent"]),
            ],
            outputs=[
                HandoffField("edit_timeline", HandoffFieldType.REQUIRED, "Edited timeline", "EditorAgent",
                            ["SubtitleAgent", "QualityCheckAgent", "DistributionPublisherAgent"], "dict", compression_hint="keys_only"),
            ]
        ))

        # QualityCheckAgent
        self.register(AgentHandoffSchema(
            agent_name="QualityCheckAgent",
            inputs=[
                HandoffField("edit_timeline", HandoffFieldType.REQUIRED, "Final edit", "EditorAgent", ["QualityCheckAgent"]),
                HandoffField("continuity_report", HandoffFieldType.OPTIONAL, "Continuity issues", "ContinuityLockAgent", ["QualityCheckAgent"]),
                HandoffField("episode_spec", HandoffFieldType.REQUIRED, "Original spec", "MasterWriterAgent", ["QualityCheckAgent"], "dict", compression_hint="keys_only"),
            ],
            outputs=[
                HandoffField("quality_report", HandoffFieldType.REQUIRED, "QC report with pass/fail", "QualityCheckAgent",
                            ["SelectiveRegenerationAgent", "FeedbackLoopAgent", "DistributionPublisherAgent"], "dict", compression_hint="keys_only"),
            ]
        ))

        # SelectiveRegenerationAgent
        self.register(AgentHandoffSchema(
            agent_name="SelectiveRegenerationAgent",
            inputs=[
                HandoffField("quality_report", HandoffFieldType.REQUIRED, "Failed QC report", "QualityCheckAgent", ["SelectiveRegenerationAgent"]),
                HandoffField("episode_spec", HandoffFieldType.REQUIRED, "Episode spec", "MasterWriterAgent", ["SelectiveRegenerationAgent"], "dict", compression_hint="keys_only"),
            ],
            outputs=[
                HandoffField("regeneration_plan", HandoffFieldType.REQUIRED, "What to regenerate", "SelectiveRegenerationAgent",
                            ["MasterWriterAgent", "DirectorEngineAgent", "ShotPlannerAgent", "VisualEngineAgent", "AudioEngineerAgent"], "dict", compression_hint="keys_only"),
            ]
        ))

        # AnalyticsEngineAgent
        self.register(AgentHandoffSchema(
            agent_name="AnalyticsEngineAgent",
            inputs=[
                HandoffField("episode_id", HandoffFieldType.REQUIRED, "", "", ["AnalyticsEngineAgent"]),
                HandoffField("final_episode", HandoffFieldType.REQUIRED, "Published episode", "DistributionPublisherAgent", ["AnalyticsEngineAgent"]),
            ],
            outputs=[
                HandoffField("analytics_report", HandoffFieldType.REQUIRED, "Analytics data", "AnalyticsEngineAgent",
                            ["FeedbackLoopAgent"], "dict", compression_hint="keys_only"),
            ]
        ))

        # FeedbackLoopAgent
        self.register(AgentHandoffSchema(
            agent_name="FeedbackLoopAgent",
            inputs=[
                HandoffField("analytics_report", HandoffFieldType.REQUIRED, "Analytics", "AnalyticsEngineAgent", ["FeedbackLoopAgent"]),
                HandoffField("quality_report", HandoffFieldType.OPTIONAL, "QC report", "QualityCheckAgent", ["FeedbackLoopAgent"]),
            ],
            outputs=[
                HandoffField("genome_updates", HandoffFieldType.REQUIRED, "Creative genome updates", "FeedbackLoopAgent",
                            ["HookEngineAgent", "MasterWriterAgent", "StoryArchitectAgent", "CharacterDirectorAgent"], "dict", compression_hint="keys_only"),
                HandoffField("direct_instructions", HandoffFieldType.REQUIRED, "Direct instructions per agent", "FeedbackLoopAgent",
                            ["HookEngineAgent", "MasterWriterAgent", "StoryboardAgent", "EditorAgent"], "dict", compression_hint="keys_only"),
            ]
        ))

        # DistributionPublisherAgent
        self.register(AgentHandoffSchema(
            agent_name="DistributionPublisherAgent",
            inputs=[
                HandoffField("final_episode", HandoffFieldType.REQUIRED, "Episode to publish", "EditorAgent", ["DistributionPublisherAgent"]),
                HandoffField("quality_report", HandoffFieldType.REQUIRED, "QC pass", "QualityCheckAgent", ["DistributionPublisherAgent"]),
            ],
            outputs=[
                HandoffField("published_episode", HandoffFieldType.REQUIRED, "Published artifact", "DistributionPublisherAgent",
                            ["AnalyticsEngineAgent"], "dict", compression_hint="keys_only"),
            ]
        ))

    def register(self, schema: AgentHandoffSchema):
        """Registra un schema de handoff."""
        self._schemas[schema.agent_name] = schema

    def get_schema(self, agent_name: str) -> Optional[AgentHandoffSchema]:
        """Obtiene schema por nombre de agente."""
        return self._schemas.get(agent_name)

    def get_required_inputs(self, agent_name: str) -> List[str]:
        """Obtiene inputs requeridos para un agente."""
        schema = self.get_schema(agent_name)
        return schema.get_required_input_names() if schema else []

    def filter_output_for_next_agent(
        self,
        source_agent: str,
        target_agent: str,
        output_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filtra output de source_agent para pasar solo lo que target_agent necesita."""
        schema = self.get_schema(source_agent)
        if not schema:
            return output_data  # Sin schema, pasar todo
        return schema.filter_output_for_target(output_data, target_agent)

    def get_handoff_path(self, from_agent: str, to_agent: str) -> List[str]:
        """Obtiene campos que fluyen de from_agent a to_agent."""
        schema = self.get_schema(from_agent)
        if not schema:
            return []
        fields = schema.get_fields_for_target(to_agent)
        return [f.name for f in fields]

    def validate_agent_input(self, agent_name: str, input_data: Dict[str, Any]) -> List[str]:
        """Valida que un agente reciba todos sus inputs requeridos."""
        schema = self.get_schema(agent_name)
        if not schema:
            return []
        return schema.validate_input(input_data)

    def get_all_schemas(self) -> Dict[str, AgentHandoffSchema]:
        """Obtiene todos los schemas registrados."""
        return self._schemas.copy()


# Instancia global
handoff_registry = HandoffRegistry()


def create_handoff(
    source_agent: str,
    target_agent: str,
    output_data: Dict[str, Any],
    registry: HandoffRegistry = None
) -> Dict[str, Any]:
    """
    Crea handoff optimizado entre dos agentes.

    Usage:
        # En orchestrator, después de que MasterWriter termina:
        handoff_data = create_handoff("MasterWriterAgent", "DirectorEngineAgent", master_writer_output)
        # handoff_data contiene solo blueprint, hook, characters, viral_ruleset
    """
    reg = registry or handoff_registry
    return reg.filter_output_for_next_agent(source_agent, target_agent, output_data)


def validate_handoff(
    agent_name: str,
    input_data: Dict[str, Any],
    registry: HandoffRegistry = None
) -> List[str]:
    """Valida que un agente tenga todos sus inputs requeridos."""
    reg = registry or handoff_registry
    return reg.validate_agent_input(agent_name, input_data)