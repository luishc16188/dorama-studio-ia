"""
Episode Architect Agent – Arquitecto de episodio individual.
Extrae del Season Bible el objetivo causal del episodio y crea EpisodeBlueprint.
"""

from __future__ import annotations

from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext
from dorama_studio.data.schemas import CTAType, EpisodeBlueprint, HookCategory


class EpisodeArchitectAgent(BaseAgent):
    """Episode Architect Agent - Creates individual episode blueprints."""

    def __init__(self):
        super().__init__("EpisodeArchitectAgent")

    def _process(self, ctx: PipelineContext) -> AgentResult:
        """Create episode blueprint from season bible."""

        # Extract inputs
        season_bible = getattr(ctx, 'season_bible', {})
        episode_num = getattr(ctx, 'episode_num', 1)
        total_episodes = getattr(ctx, 'total_episodes', 40)

        if not season_bible:
            # Fallback if no season bible
            return AgentResult(
                success=False,
                agent_name=self.name,
                error="No season bible available",
                recoverable=True
            )

        # Get episode envelope from season bible
        episodes = season_bible.get("episodes", [])
        if episode_num - 1 < len(episodes):
            episode_envelope = episodes[episode_num - 1]
        else:
            episode_envelope = self._create_default_envelope(episode_num, total_episodes)

        # Build episode blueprint
        blueprint = EpisodeBlueprint(
            ep=episode_num,
            hook_category=HookCategory(episode_envelope.get("hook_category", "mystery")),
            core_conflict=episode_envelope.get("core_conflict", "Conflicto del episodio"),
            twist=episode_envelope.get("twist", "Giro inesperado"),
            cliffhanger=episode_envelope.get("cliffhanger", "Cliffhanger abierto"),
            cta_type=CTAType(episode_envelope.get("cta_type", "moral_dilemma"))
        )

        # Add additional metadata from season bible
        blueprint_data = {
            "blueprint": blueprint,
            "episode_envelope": episode_envelope,
            "pressure_level": episode_envelope.get("pressure_level", 50),
            "resolves": episode_envelope.get("resolves", []),
            "creates": episode_envelope.get("creates", []),
            "escalates": episode_envelope.get("escalates", []),
            "rewards": episode_envelope.get("rewards", []),
            "opens": episode_envelope.get("opens", []),
            "reference_patterns": episode_envelope.get("reference_patterns", []),
            "season_arc_context": {
                "season_number": season_bible.get("season_number", 1),
                "macro_hook": season_bible.get("macro_hook", ""),
                "premise": season_bible.get("premise", ""),
                "character_arcs": season_bible.get("character_arcs", []),
                "relationship_arcs": season_bible.get("relationship_arcs", []),
                "mystery_architecture": season_bible.get("mystery_architecture", {}),
                "subplots": season_bible.get("subplots", [])
            }
        }

        # Update state
        if hasattr(ctx, 'state') and ctx.state:
            state_dict = ctx.state.dict() if hasattr(ctx.state, 'dict') else dict(ctx.state) if hasattr(ctx.state, '__dict__') else {}
            state_dict['episode_blueprint'] = blueprint_data
            state_dict['blueprint_id'] = f"blueprint_s01e{episode_num:03d}"

            if hasattr(ctx.state, '__dict__'):
                for key, value in state_dict.items():
                    setattr(ctx.state, key, value)
            elif hasattr(ctx.state, '__setitem__'):
                for key, value in state_dict.items():
                    ctx.state[key] = value

        return AgentResult(
            success=True,
            agent_name=self.name,
            output_data=blueprint_data,
            context_updates={
                "episode_blueprint": blueprint_data,
                "blueprint_id": f"blueprint_s01e{episode_num:03d}"
            },
            logs=[{
                "step": "EpisodeArchitect",
                "episode": episode_num,
                "hook_category": blueprint.hook_category.value,
                "pressure_level": episode_envelope.get("pressure_level", 50)
            }],
        )

    def _create_default_envelope(self, episode_num: int, total_episodes: int) -> dict[str, Any]:
        """Create default envelope if not available."""
        hook_categories = [
            "visual_status", "mystery", "emotion", "contradiction",
            "threat", "relationship", "object", "question",
            "shock", "impossible_situation", "status_reversal", "identity_reveal"
        ]
        cliffhanger_types = [
            "revelation", "betrayal", "threat", "interruption",
            "discovery", "emotional_reversal", "identity_reveal",
            "secret_revealed", "new_antagonist", "impossible_choice",
            "unanswered_question", "unexpected_arrival", "status_reversal",
            "relationship_reversal"
        ]
        cta_types = [
            "moral_dilemma", "theory_question", "choose_side",
            "predict_outcome", "emotional_choice", "identity_question"
        ]

        return {
            "hook_category": hook_categories[(episode_num - 1) % len(hook_categories)],
            "core_conflict": f"Conflicto del episodio {episode_num}",
            "twist": f"Giro en el episodio {episode_num}",
            "cliffhanger": cliffhanger_types[(episode_num - 1) % len(cliffhanger_types)],
            "cta_type": cta_types[(episode_num - 1) % len(cta_types)],
            "pressure_level": min(20 + int(75 * episode_num / total_episodes), 95),
            "resolves": [f"Tensión del episodio {episode_num - 1}"],
            "creates": [f"Nueva pregunta del episodio {episode_num}"],
            "escalates": [f"Escala hacia el episodio {episode_num + 1}"],
            "rewards": [f"Revelación parcial en {episode_num}"],
            "opens": [f"Misterio para {episode_num + 1}"],
            "reference_patterns": []
        }
