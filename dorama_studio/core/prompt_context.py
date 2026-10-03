"""
Prompt Context Builder - Construye contexto mínimo necesario para cada operación LLM.
Separa STABLE / DYNAMIC / TASK context para optimizar tokens.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from pathlib import Path
import json

from dorama_studio.core.token_usage import estimate_tokens, TokenEstimationMethod


class ContextLevel(str, Enum):
    """Niveles de contexto jerárquicos."""
    GLOBAL = "global"           # Reglas del sistema, arquitectura, estilo global
    SEASON = "season"           # Arco temporada, personajes principales, world rules
    EPISODE = "episode"         # Objetivo episodio, beats, personajes presentes
    SCENE = "scene"             # Personajes de la escena, location, action, dialogue
    TASK = "task"               # Qué debe hacer el agente ahora, constraints, output schema


@dataclass
class ContextBudget:
    """Presupuesto de tokens por nivel de contexto."""
    max_global_tokens: int = 2000
    max_season_tokens: int = 1500
    max_episode_tokens: int = 2000
    max_scene_tokens: int = 1500
    max_task_tokens: int = 1000
    max_total_tokens: int = 7000

    def get_budget_for_level(self, level: ContextLevel) -> int:
        budgets = {
            ContextLevel.GLOBAL: self.max_global_tokens,
            ContextLevel.SEASON: self.max_season_tokens,
            ContextLevel.EPISODE: self.max_episode_tokens,
            ContextLevel.SCENE: self.max_scene_tokens,
            ContextLevel.TASK: self.max_task_tokens,
        }
        return budgets.get(level, 1000)

    def validate_total(self, level_tokens: Dict[ContextLevel, int]) -> bool:
        total = sum(level_tokens.values())
        return total <= self.max_total_tokens


@dataclass
class StableContext:
    """Contexto estable que rara vez cambia - cacheable."""
    system_rules: str = ""
    architecture_docs: str = ""
    global_style: str = ""
    contracts: str = ""
    permanent_instructions: str = ""
    prompt_version: str = "1.0"

    # Cache keys
    _hash: Optional[str] = None

    def compute_hash(self) -> str:
        import hashlib
        content = f"{self.system_rules}{self.architecture_docs}{self.global_style}{self.contracts}{self.permanent_instructions}{self.prompt_version}"
        self._hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self._hash

    def get_cache_key(self) -> str:
        if not self._hash:
            self.compute_hash()
        return f"stable_ctx_{self._hash}"

    def to_prompt_block(self) -> str:
        """Convierte a bloque de prompt estable."""
        parts = []
        if self.system_rules:
            parts.append(f"=== SYSTEM RULES ===\n{self.system_rules}")
        if self.architecture_docs:
            parts.append(f"=== ARCHITECTURE ===\n{self.architecture_docs}")
        if self.global_style:
            parts.append(f"=== GLOBAL STYLE ===\n{self.global_style}")
        if self.contracts:
            parts.append(f"=== CONTRACTS ===\n{self.contracts}")
        if self.permanent_instructions:
            parts.append(f"=== PERMANENT INSTRUCTIONS ===\n{self.permanent_instructions}")
        return "\n\n".join(parts)


@dataclass
class DynamicContext:
    """Contexto dinámico que cambia por temporada/episodio."""
    # Season level
    season_arc: str = ""
    main_characters: List[Dict[str, Any]] = field(default_factory=list)
    character_relationships: Dict[str, str] = field(default_factory=dict)
    world_rules: str = ""
    visual_identity: str = ""
    season_continuity: Dict[str, Any] = field(default_factory=dict)

    # Episode level
    episode_objective: str = ""
    episode_beats: List[Dict[str, Any]] = field(default_factory=list)
    episode_characters: List[str] = field(default_factory=list)
    episode_locations: List[str] = field(default_factory=list)
    episode_conflict: str = ""
    episode_cliffhanger: str = ""
    immediate_continuity: Dict[str, Any] = field(default_factory=dict)

    def to_prompt_block(self, include_season: bool = True, include_episode: bool = True) -> str:
        parts = []
        if include_season:
            if self.season_arc:
                parts.append(f"=== SEASON ARC ===\n{self.season_arc}")
            if self.main_characters:
                char_summary = "\n".join(
                    f"- {c.get('id', '?')}: {c.get('name', '?')} ({c.get('role', '?')}) - {c.get('archetype', '')}"
                    for c in self.main_characters[:10]  # límite
                )
                parts.append(f"=== MAIN CHARACTERS ===\n{char_summary}")
            if self.character_relationships:
                rel_summary = "\n".join(f"- {k}: {v}" for k, v in list(self.character_relationships.items())[:10])
                parts.append(f"=== RELATIONSHIPS ===\n{rel_summary}")
            if self.world_rules:
                parts.append(f"=== WORLD RULES ===\n{self.world_rules}")
            if self.visual_identity:
                parts.append(f"=== VISUAL IDENTITY ===\n{self.visual_identity}")
            if self.season_continuity:
                parts.append(f"=== SEASON CONTINUITY ===\n{json.dumps(self.season_continuity, ensure_ascii=False)[:1000]}")

        if include_episode:
            if self.episode_objective:
                parts.append(f"=== EPISODE OBJECTIVE ===\n{self.episode_objective}")
            if self.episode_beats:
                beats_summary = "\n".join(
                    f"  {b.get('beat_name', '?')}: {b.get('action', '')[:50]}"
                    for b in self.episode_beats[:9]
                )
                parts.append(f"=== EPISODE BEATS ===\n{beats_summary}")
            if self.episode_characters:
                parts.append(f"=== EPISODE CHARACTERS ===\n{', '.join(self.episode_characters)}")
            if self.episode_locations:
                parts.append(f"=== EPISODE LOCATIONS ===\n{', '.join(self.episode_locations)}")
            if self.episode_conflict:
                parts.append(f"=== CONFLICT ===\n{self.episode_conflict}")
            if self.episode_cliffhanger:
                parts.append(f"=== CLIFFHANGER ===\n{self.episode_cliffhanger}")
            if self.immediate_continuity:
                parts.append(f"=== IMMEDIATE CONTINUITY ===\n{json.dumps(self.immediate_continuity, ensure_ascii=False)[:1000]}")

        return "\n\n".join(parts)


@dataclass
class TaskContext:
    """Contexto específico de la tarea actual - solo lo necesario."""
    agent_name: str = ""
    task_description: str = ""
    constraints: List[str] = field(default_factory=list)
    output_schema: str = ""
    required_fields: List[str] = field(default_factory=list)
    forbidden_fields: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    specific_data: Dict[str, Any] = field(default_factory=dict)

    def to_prompt_block(self) -> str:
        parts = []
        if self.task_description:
            parts.append(f"=== TASK ===\n{self.task_description}")
        if self.constraints:
            parts.append(f"=== CONSTRAINTS ===\n" + "\n".join(f"- {c}" for c in self.constraints))
        if self.output_schema:
            parts.append(f"=== OUTPUT SCHEMA ===\n{self.output_schema}")
        if self.required_fields:
            parts.append(f"=== REQUIRED FIELDS ===\n{', '.join(self.required_fields)}")
        if self.forbidden_fields:
            parts.append(f"=== FORBIDDEN ===\n{', '.join(self.forbidden_fields)}")
        if self.examples:
            for i, ex in enumerate(self.examples[:2]):  # máx 2 ejemplos
                parts.append(f"=== EXAMPLE {i+1} ===\n{json.dumps(ex, ensure_ascii=False)[:500]}")
        if self.specific_data:
            parts.append(f"=== SPECIFIC DATA ===\n{json.dumps(self.specific_data, ensure_ascii=False)[:1000]}")
        return "\n\n".join(parts)


@dataclass
class CompressedContinuity:
    """Estado de continuidad comprimido - hechos importantes sin historial completo."""
    facts: List[str] = field(default_factory=list)
    unresolved_threads: List[str] = field(default_factory=list)
    recent_events: List[str] = field(default_factory=list)  # últimos 3-5 eventos
    character_changes: Dict[str, str] = field(default_factory=dict)
    location_changes: Dict[str, str] = field(default_factory=dict)
    visual_changes: Dict[str, str] = field(default_factory=dict)
    relationship_changes: Dict[str, str] = field(default_factory=dict)
    active_constraints: List[str] = field(default_factory=list)

    def to_prompt_block(self) -> str:
        parts = []
        if self.facts:
            parts.append(f"=== KEY FACTS ===\n" + "\n".join(f"- {f}" for f in self.facts[:10]))
        if self.unresolved_threads:
            parts.append(f"=== UNRESOLVED THREADS ===\n" + "\n".join(f"- {t}" for t in self.unresolved_threads[:5]))
        if self.recent_events:
            parts.append(f"=== RECENT EVENTS ===\n" + "\n".join(f"- {e}" for e in self.recent_events[:5]))
        if self.character_changes:
            parts.append(f"=== CHARACTER CHANGES ===\n" + "\n".join(f"- {k}: {v}" for k, v in list(self.character_changes.items())[:5]))
        if self.location_changes:
            parts.append(f"=== LOCATION CHANGES ===\n" + "\n".join(f"- {k}: {v}" for k, v in list(self.location_changes.items())[:3]))
        if self.visual_changes:
            parts.append(f"=== VISUAL CHANGES ===\n" + "\n".join(f"- {k}: {v}" for k, v in list(self.visual_changes.items())[:3]))
        if self.relationship_changes:
            parts.append(f"=== RELATIONSHIP CHANGES ===\n" + "\n".join(f"- {k}: {v}" for k, v in list(self.relationship_changes.items())[:5]))
        if self.active_constraints:
            parts.append(f"=== ACTIVE CONSTRAINTS ===\n" + "\n".join(f"- {c}" for c in self.active_constraints[:5]))
        return "\n\n".join(parts)

    @classmethod
    def from_episode_state(cls, episode_data: Dict[str, Any], previous_episodes: List[Dict[str, Any]] = None) -> 'CompressedContinuity':
        """Construye continuidad comprimida desde estado del episodio."""
        cc = cls()

        # Extraer hechos clave del episodio actual
        if episode_data.get("beats"):
            for beat in episode_data["beats"][-3:]:  # últimos 3 beats
                if beat.get("action"):
                    cc.recent_events.append(f"{beat.get('beat_name', 'Beat')}: {beat['action'][:100]}")

        # Si hay episodios previos, extraer threads sin resolver
        if previous_episodes:
            for ep in previous_episodes[-3:]:  # últimos 3 episodios
                if ep.get("cliffhanger"):
                    cc.unresolved_threads.append(f"Ep {ep.get('episode_number', '?')}: {ep['cliffhanger'][:100]}")

        return cc


class PromptContextBuilder:
    """
    Construye contexto mínimo necesario para cada operación LLM.
    Implementa selección contextual y presupuestos de tokens.
    """

    def __init__(self, budget: Optional[ContextBudget] = None):
        self.budget = budget or ContextBudget()
        self._stable_context: Optional[StableContext] = None
        self._stable_context_cache: Dict[str, StableContext] = {}

    def set_stable_context(self, stable: StableContext):
        """Establece el contexto estable (cacheable)."""
        self._stable_context = stable
        self._stable_context_cache[stable.get_cache_key()] = stable

    def load_stable_context_from_files(self, base_path: str = ".") -> StableContext:
        """Carga contexto estable desde archivos de configuración."""
        base = Path(base_path)
        stable = StableContext()

        # Cargar reglas del sistema
        rules_file = base / "config" / "system_rules.md"
        if rules_file.exists():
            stable.system_rules = rules_file.read_text(encoding="utf-8")[:5000]

        # Cargar arquitectura
        arch_file = base / "docs" / "architecture.md"
        if arch_file.exists():
            stable.architecture_docs = arch_file.read_text(encoding="utf-8")[:5000]

        # Cargar estilo global
        style_file = base / "config" / "global_style.md"
        if style_file.exists():
            stable.global_style = style_file.read_text(encoding="utf-8")[:3000]

        # Cargar contratos
        contracts_file = base / "config" / "contracts.md"
        if contracts_file.exists():
            stable.contracts = contracts_file.read_text(encoding="utf-8")[:5000]

        # Instrucciones permanentes
        instructions_file = base / "config" / "permanent_instructions.md"
        if instructions_file.exists():
            stable.permanent_instructions = instructions_file.read_text(encoding="utf-8")[:3000]

        stable.compute_hash()
        self.set_stable_context(stable)
        return stable

    def build(
        self,
        task: str,
        agent: str,
        episode: Optional[Dict[str, Any]] = None,
        scene: Optional[Dict[str, Any]] = None,
        required_context: Optional[Set[ContextLevel]] = None,
        dynamic_context: Optional[DynamicContext] = None,
        compressed_continuity: Optional[CompressedContinuity] = None,
        task_context: Optional[TaskContext] = None,
        max_total_tokens: Optional[int] = None,
    ) -> str:
        """
        Construye el prompt completo con contexto optimizado.

        Args:
            task: Descripción de la tarea
            agent: Nombre del agente
            episode: Datos del episodio (opcional)
            scene: Datos de la escena (opcional)
            required_context: Niveles de contexto requeridos (None = todos)
            dynamic_context: Contexto dinámico pre-construido
            compressed_continuity: Continuidad comprimida
            task_context: Contexto específico de la tarea
            max_total_tokens: Override del presupuesto total

        Returns:
            Prompt completo optimizado
        """
        if required_context is None:
            required_context = {
                ContextLevel.GLOBAL, ContextLevel.SEASON,
                ContextLevel.EPISODE, ContextLevel.SCENE, ContextLevel.TASK
            }

        budget = self.budget
        if max_total_tokens:
            # Ajustar presupuesto proporcionalmente
            ratio = max_total_tokens / budget.max_total_tokens
            budget = ContextBudget(
                max_global_tokens=int(budget.max_global_tokens * ratio),
                max_season_tokens=int(budget.max_season_tokens * ratio),
                max_episode_tokens=int(budget.max_episode_tokens * ratio),
                max_scene_tokens=int(budget.max_scene_tokens * ratio),
                max_task_tokens=int(budget.max_task_tokens * ratio),
                max_total_tokens=max_total_tokens,
            )

        # Construir o usar contexto dinámico
        if dynamic_context is None:
            dynamic_context = self._build_dynamic_context(episode, scene)

        # Construir o usar continuidad comprimida
        if compressed_continuity is None:
            previous_eps = episode.get("previous_episodes", []) if episode else []
            compressed_continuity = CompressedContinuity.from_episode_state(episode or {}, previous_eps)

        # Construir o usar contexto de tarea
        if task_context is None:
            task_context = TaskContext(
                agent_name=agent,
                task_description=task,
            )

        # Construir bloques por nivel
        blocks: Dict[ContextLevel, str] = {}
        level_tokens: Dict[ContextLevel, int] = {}

        # GLOBAL - siempre incluir si está en required_context
        if ContextLevel.GLOBAL in required_context and self._stable_context:
            stable_block = self._stable_context.to_prompt_block()
            stable_tokens = estimate_tokens(stable_block)
            if stable_tokens <= budget.max_global_tokens:
                blocks[ContextLevel.GLOBAL] = stable_block
                level_tokens[ContextLevel.GLOBAL] = stable_tokens
            else:
                # Truncar
                blocks[ContextLevel.GLOBAL] = self._truncate_to_tokens(stable_block, budget.max_global_tokens)
                level_tokens[ContextLevel.GLOBAL] = budget.max_global_tokens

        # SEASON
        if ContextLevel.SEASON in required_context:
            season_block = dynamic_context.to_prompt_block(include_season=True, include_episode=False)
            season_tokens = estimate_tokens(season_block)
            if season_tokens <= budget.max_season_tokens:
                blocks[ContextLevel.SEASON] = season_block
                level_tokens[ContextLevel.SEASON] = season_tokens
            else:
                blocks[ContextLevel.SEASON] = self._truncate_to_tokens(season_block, budget.max_season_tokens)
                level_tokens[ContextLevel.SEASON] = budget.max_season_tokens

        # EPISODE
        if ContextLevel.EPISODE in required_context:
            episode_block = dynamic_context.to_prompt_block(include_season=False, include_episode=True)
            episode_tokens = estimate_tokens(episode_block)
            if episode_tokens <= budget.max_episode_tokens:
                blocks[ContextLevel.EPISODE] = episode_block
                level_tokens[ContextLevel.EPISODE] = episode_tokens
            else:
                blocks[ContextLevel.EPISODE] = self._truncate_to_tokens(episode_block, budget.max_episode_tokens)
                level_tokens[ContextLevel.EPISODE] = budget.max_episode_tokens

        # SCENE + CONTINUITY (combinados)
        if ContextLevel.SCENE in required_context:
            scene_parts = []
            if scene:
                scene_data = {
                    "characters": scene.get("characters", []),
                    "location": scene.get("location", ""),
                    "action": scene.get("action", ""),
                    "dialogue": scene.get("dialogue", ""),
                    "shot_requirements": scene.get("shot_requirements", ""),
                }
                scene_parts.append(f"=== CURRENT SCENE ===\n{json.dumps(scene_data, ensure_ascii=False)[:1500]}")

            if compressed_continuity:
                cont_block = compressed_continuity.to_prompt_block()
                scene_parts.append(f"=== CONTINUITY ===\n{cont_block}")

            scene_block = "\n\n".join(scene_parts)
            scene_tokens = estimate_tokens(scene_block)
            if scene_tokens <= budget.max_scene_tokens:
                blocks[ContextLevel.SCENE] = scene_block
                level_tokens[ContextLevel.SCENE] = scene_tokens
            else:
                blocks[ContextLevel.SCENE] = self._truncate_to_tokens(scene_block, budget.max_scene_tokens)
                level_tokens[ContextLevel.SCENE] = budget.max_scene_tokens

        # TASK - siempre incluir
        if ContextLevel.TASK in required_context:
            task_block = task_context.to_prompt_block()
            task_tokens = estimate_tokens(task_block)
            if task_tokens <= budget.max_task_tokens:
                blocks[ContextLevel.TASK] = task_block
                level_tokens[ContextLevel.TASK] = task_tokens
            else:
                blocks[ContextLevel.TASK] = self._truncate_to_tokens(task_block, budget.max_task_tokens)
                level_tokens[ContextLevel.TASK] = budget.max_task_tokens

        # Validar presupuesto total
        total_estimated = sum(level_tokens.values())
        if total_estimated > budget.max_total_tokens:
            # Reducir proporcionalmente empezando por los niveles menos críticos
            excess = total_estimated - budget.max_total_tokens
            for level in [ContextLevel.GLOBAL, ContextLevel.SEASON, ContextLevel.EPISODE, ContextLevel.SCENE]:
                if level in blocks and excess > 0:
                    current = level_tokens[level]
                    reduction = min(excess, current // 2)
                    if reduction > 0:
                        blocks[level] = self._truncate_to_tokens(blocks[level], current - reduction)
                        level_tokens[level] = current - reduction
                        excess -= reduction

        # Ordenar bloques: GLOBAL -> SEASON -> EPISODE -> SCENE -> TASK
        ordered_levels = [
            ContextLevel.GLOBAL, ContextLevel.SEASON,
            ContextLevel.EPISODE, ContextLevel.SCENE, ContextLevel.TASK
        ]

        final_blocks = [blocks[level] for level in ordered_levels if level in blocks]

        return "\n\n".join(final_blocks)

    def _build_dynamic_context(
        self,
        episode: Optional[Dict[str, Any]],
        scene: Optional[Dict[str, Any]]
    ) -> DynamicContext:
        """Construye contexto dinámico desde datos de episodio/escena."""
        dyn = DynamicContext()

        if episode:
            dyn.episode_objective = episode.get("objective", "")
            dyn.episode_beats = episode.get("beats", [])
            dyn.episode_characters = episode.get("characters_present", [])
            dyn.episode_locations = episode.get("locations", [])
            dyn.episode_conflict = episode.get("conflict", "")
            dyn.episode_cliffhanger = episode.get("cliffhanger", "")
            dyn.immediate_continuity = episode.get("continuity", {})

            # Season data from episode if available
            dyn.season_arc = episode.get("season_arc", "")
            dyn.main_characters = episode.get("season_characters", [])
            dyn.character_relationships = episode.get("relationships", {})
            dyn.world_rules = episode.get("world_rules", "")
            dyn.visual_identity = episode.get("visual_identity", "")
            dyn.season_continuity = episode.get("season_continuity", {})

        return dyn

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Trunca texto para caber en presupuesto de tokens."""
        estimated = estimate_tokens(text)
        if estimated <= max_tokens:
            return text

        # Truncar por caracteres (aproximado)
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text

        return text[:max_chars] + "\n... [TRUNCATED]"

    def get_context_stats(self, prompt: str) -> Dict[str, Any]:
        """Obtiene estadísticas del prompt construido."""
        return {
            "total_chars": len(prompt),
            "estimated_tokens": estimate_tokens(prompt),
            "within_budget": estimate_tokens(prompt) <= self.budget.max_total_tokens,
        }


# Instancia global por defecto
prompt_context_builder = PromptContextBuilder()


def build_minimal_prompt(
    agent: str,
    task: str,
    episode_data: Optional[Dict] = None,
    scene_data: Optional[Dict] = None,
    schema: Optional[str] = None,
    budget_override: Optional[int] = None,
) -> str:
    """
    Función de conveniencia para construir prompt mínimo.

    Usage:
        prompt = build_minimal_prompt(
            agent="MasterWriter",
            task="Generate 9 beats for episode 5",
            episode_data={"objective": "...", "beats": [...]},
            schema="JSON schema here"
        )
    """
    tc = TaskContext(
        agent_name=agent,
        task_description=task,
        output_schema=schema or "",
    )

    return prompt_context_builder.build(
        task=task,
        agent=agent,
        episode=episode_data,
        scene=scene_data,
        task_context=tc,
        max_total_tokens=budget_override,
    )