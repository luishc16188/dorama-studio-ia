"""
Season Architect Agent – Showrunner estructural para 40 episodios.
Convierte una idea en una temporada causal de 40 episodios.
"""

from __future__ import annotations

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.reference_intelligence_agent import ReferenceIntelligenceAgent
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext
from dorama_studio.creative_genome import CreativeGenomeV2 as CreativeGenome

logger = logging.getLogger(__name__)


class SeasonArchitectAgent(BaseAgent):
    """Season Architect Agent - Creates 40-episode season architecture."""

    def __init__(self):
        super().__init__("SeasonArchitectAgent")
        self.creative_genome = CreativeGenome(
            agent_name="season_architect",
            session_id=f"season_arch_{hash(str(__file__))}"
        )
        self.reference_intelligence = ReferenceIntelligenceAgent()
        logger.info("SeasonArchitectAgent initialized with 40-episode capacity")

    def _process(self, ctx: PipelineContext) -> AgentResult:
        """Create complete season architecture for 40 episodes."""

        # Extract inputs
        concept_seed = ctx.concept_seed
        genre = ctx.genre
        total_episodes = ctx.total_episodes if hasattr(ctx, 'total_episodes') else 40

        # Load reference DNA
        ref_result = self.reference_intelligence.process(ctx)
        reference_dna = ref_result.context_updates.get("reference_dna", {})

        # Get creative genome budget
        budget = self.creative_genome.check_budget("season_architect", genre)

        # Build season structure based on reference DNA
        season_arc = self._build_season_arc(
            concept_seed, genre, total_episodes, reference_dna, budget
        )

        # Create episode envelopes
        episodes = self._create_episode_envelopes(
            season_arc, total_episodes, genre, reference_dna
        )

        # Create character arcs
        character_arcs = self._create_character_arcs(
            episodes, genre, reference_dna
        )

        # Create relationship arcs
        relationship_arcs = self._create_relationship_arcs(
            episodes, character_arcs
        )

        # Create mystery architecture
        mystery_architecture = self._create_mystery_architecture(
            episodes, total_episodes
        )

        # Create subplots
        subplots = self._create_subplots(episodes, total_episodes)

        # Build season bible
        season_bible = {
            "season_number": 1,
            "concept_seed": concept_seed,
            "genre": genre,
            "total_episodes": total_episodes,
            "season_arc": season_arc,
            "episodes": episodes,
            "character_arcs": character_arcs,
            "relationship_arcs": relationship_arcs,
            "mystery_architecture": mystery_architecture,
            "subplots": subplots,
            "macro_hook": self._create_macro_hook(season_arc, reference_dna),
            "premise": self._create_premise(concept_seed, genre),
            "pressure_ladder": self._calculate_pressure_ladder(total_episodes),
            "reference_dna_applied": True,
            "creative_genome_budget": budget
        }

        # Update state
        if hasattr(ctx, 'state') and ctx.state:
            state_dict = ctx.state.dict() if hasattr(ctx.state, 'dict') else dict(ctx.state) if hasattr(ctx.state, '__dict__') else {}
            state_dict['season_bible'] = season_bible
            state_dict['season_bible_ref'] = "season_bible_s01"

            if hasattr(ctx.state, '__dict__'):
                for key, value in state_dict.items():
                    setattr(ctx.state, key, value)
            elif hasattr(ctx.state, '__setitem__'):
                for key, value in state_dict.items():
                    ctx.state[key] = value

        return AgentResult(
            success=True,
            agent_name=self.name,
            output_data=season_bible,
            context_updates={
                "season_bible": season_bible,
                "season_bible_ref": "season_bible_s01"
            },
            logs=[{
                "step": "SeasonArchitect",
                "episodes_created": total_episodes,
                "macro_hook": season_bible["macro_hook"][:100]
            }],
        )

    def _build_season_arc(
        self,
        concept_seed: str,
        genre: str,
        total_episodes: int,
        reference_dna: dict,
        budget: dict
    ) -> dict[str, Any]:
        """Build the macro season arc using reference DNA patterns."""

        # Use reference DNA to inform season structure
        narrative_dna = reference_dna.get("narrative_dna", {})
        attention_psych = reference_dna.get("attention_psychology", {})

        # Define season blocks based on 40-episode envelope
        blocks = [
            {"name": "Setup & Promise", "episodes": "1-4", "function": "promise + mundo + conflicto"},
            {"name": "Escalation & Alliances", "episodes": "5-8", "function": "escalada + primeras alianzas/amenazas"},
            {"name": "First Major Reveal", "episodes": "9-12", "function": "primer gran reveal"},
            {"name": "Midpoint Reversal", "episodes": "13-16", "function": "midpoint/reversal"},
            {"name": "Consequences & Convergence", "episodes": "17-21", "function": "consecuencias + subtramas convergentes"},
            {"name": "Compression & Loss", "episodes": "22-25", "function": "compresión y pérdida de opciones"},
            {"name": "Crisis & Truth", "episodes": "26-28", "function": "crisis + verdad principal"},
            {"name": "Penultimate Payoff", "episodes": "29", "function": "penúltimo payoff + última pregunta"},
            {"name": "Final Resolution", "episodes": "30", "function": "resolución + payoff final"}
        ]

        # Adjust for 40 episodes
        if total_episodes == 40:
            blocks = [
                {"name": "Setup & Promise", "episodes": "1-5", "function": "promise + mundo + conflicto"},
                {"name": "Escalation & Alliances", "episodes": "6-10", "function": "escalada + primeras alianzas/amenazas"},
                {"name": "First Major Reveal", "episodes": "11-14", "function": "primer gran reveal"},
                {"name": "Midpoint Reversal", "episodes": "15-20", "function": "midpoint/reversal"},
                {"name": "Consequences & Convergence", "episodes": "21-26", "function": "consecuencias + subtramas convergentes"},
                {"name": "Compression & Loss", "episodes": "27-32", "function": "compresión y pérdida de opciones"},
                {"name": "Crisis & Truth", "episodes": "33-36", "function": "crisis + verdad principal"},
                {"name": "Penultimate Payoff", "episodes": "37-38", "function": "penúltimo payoff + última pregunta"},
                {"name": "Final Resolution", "episodes": "39-40", "function": "resolución + payoff final"}
            ]

        return {
            "concept": concept_seed,
            "genre": genre,
            "blocks": blocks,
            "central_questions": self._define_central_questions(concept_seed, genre),
            "sub_mysteries": self._define_sub_mysteries(genre),
            "major_reversals": 5,
            "major_reveals": 4,
            "major_payoffs": 3,
            "final_payoff": 1,
            "narrative_dna_applied": list(narrative_dna.keys()),
            "attention_patterns_applied": list(attention_psych.keys())
        }

    def _create_episode_envelopes(
        self,
        season_arc: dict,
        total_episodes: int,
        genre: str,
        reference_dna: dict
    ) -> list[dict[str, Any]]:
        """Create episode envelopes with resolve/create/escalate/reward/open pattern."""

        episodes = []
        blocks = season_arc.get("blocks", [])
        central_questions = season_arc.get("central_questions", [])
        sub_mysteries = season_arc.get("sub_mysteries", [])

        # Hook categories from reference DNA - cycle through them
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

        for ep_num in range(1, total_episodes + 1):
            # Determine which block this episode belongs to
            block = self._find_block_for_episode(ep_num, blocks)

            # Select hook category (no consecutive duplicates)
            hook_cat = hook_categories[(ep_num - 1) % len(hook_categories)]

            # Select cliffhanger type
            cliff_type = cliffhanger_types[(ep_num - 1) % len(cliffhanger_types)]

            # Build episode envelope
            episode = {
                "episode_number": ep_num,
                "block": block["name"],
                "block_function": block["function"],
                "hook_category": hook_cat,
                "core_conflict": self._generate_core_conflict(ep_num, block, genre),
                "twist": self._generate_twist(ep_num, sub_mysteries),
                "cliffhanger": self._generate_cliffhanger(ep_num, cliff_type, central_questions),
                "cta_type": self._select_cta_type(ep_num, genre),
                "pressure_level": self._calculate_pressure(ep_num, total_episodes),
                "resolves": self._define_resolves(ep_num, block, central_questions, sub_mysteries),
                "creates": self._define_creates(ep_num, block, central_questions, sub_mysteries),
                "escalates": self._define_escalates(ep_num, block),
                "rewards": self._define_rewards(ep_num, block),
                "opens": self._define_opens(ep_num, block, central_questions, sub_mysteries),
                "reference_patterns": self._select_reference_patterns(ep_num, reference_dna)
            }
            episodes.append(episode)

        return episodes

    def _find_block_for_episode(self, ep_num: int, blocks: list[dict]) -> dict:
        """Find which block an episode belongs to."""
        for block in blocks:
            ep_range = block["episodes"]
            if "-" in ep_range:
                start, end = map(int, ep_range.split("-"))
                if start <= ep_num <= end:
                    return block
            else:
                if int(ep_range) == ep_num:
                    return block
        return blocks[-1] if blocks else {"name": "Unknown", "function": "unknown"}

    def _define_central_questions(self, concept_seed: str, genre: str) -> list[str]:
        """Define 2-4 central questions for the season."""
        return [
            "¿Quién es realmente el protagonista y cuál es su verdadero origen?",
            "¿Qué secreto oculta la familia antagonista?",
            "¿Logrará el protagonista venganza sin perder su humanidad?",
            "¿Cuál es el verdadero precio del poder en este mundo?"
        ]

    def _define_sub_mysteries(self, genre: str) -> list[str]:
        """Define 3-6 sub-mysteries."""
        return [
            "El origen del objeto de deseo",
            "La identidad del informante",
            "El pasado oculto del mentor",
            "La verdad sobre el accidente",
            "La lealtad del aliado más cercano",
            "El destino del personaje perdido"
        ]

    def _generate_core_conflict(self, ep_num: int, block: dict, genre: str) -> str:
        """Generate core conflict for episode."""
        conflicts = {
            "Setup & Promise": "Establecer el mundo y el deseo del protagonista",
            "Escalation & Alliances": "Conflicto de lealtades y primeras traiciones",
            "First Major Reveal": "Revelación que cambia la comprensión del conflicto",
            "Midpoint Reversal": "Inversión total de las expectativas",
            "Consequences & Convergence": "Consecuencias de decisiones previas convergen",
            "Compression & Loss": "Pérdida de opciones y aliados",
            "Crisis & Truth": "Confrontación con la verdad principal",
            "Penultimate Payoff": "Resolución de misterio principal, nueva pregunta final",
            "Final Resolution": "Resolución final y payoff emocional"
        }
        return conflicts.get(block["name"], f"Conflicto del episodio {ep_num}")

    def _generate_twist(self, ep_num: int, sub_mysteries: list[str]) -> str:
        """Generate twist for episode."""
        if sub_mysteries:
            return f"Pista hacia: {sub_mysteries[(ep_num - 1) % len(sub_mysteries)]}"
        return f"Giro en el episodio {ep_num}"

    def _generate_cliffhanger(self, ep_num: int, cliff_type: str, central_questions: list[str]) -> str:
        """Generate cliffhanger for episode."""
        return f"{cliff_type.capitalize()} que abre: {central_questions[(ep_num - 1) % len(central_questions)]}"

    def _select_cta_type(self, ep_num: int, genre: str) -> str:
        """Select CTA type for episode."""
        cta_types = [
            "moral_dilemma", "theory_question", "choose_side",
            "predict_outcome", "emotional_choice", "identity_question"
        ]
        return cta_types[(ep_num - 1) % len(cta_types)]

    def _calculate_pressure(self, ep_num: int, total_episodes: int) -> int:
        """Calculate pressure level (20% to 90%+)."""
        # Pressure ladder: starts ~20%, reaches ~90%+
        base = 20
        max_pressure = 95
        progress = ep_num / total_episodes
        # Non-linear escalation - faster in middle
        if progress < 0.5:
            pressure = base + int((max_pressure - base) * progress * 1.5)
        else:
            pressure = base + int((max_pressure - base) * (1 + (progress - 0.5)))
        return min(pressure, max_pressure)

    def _define_resolves(self, ep_num: int, block: dict, central_questions: list, sub_mysteries: list) -> list[str]:
        """Define what this episode resolves."""
        # Every episode must resolve something
        return [f"Resuelve tensión de: {block['function']}"]

    def _define_creates(self, ep_num: int, block: dict, central_questions: list, sub_mysteries: list) -> list[str]:
        """Define what this episode creates."""
        # Every episode must create something new
        return [f"Crea nueva pregunta: {central_questions[(ep_num - 1) % len(central_questions)]}"]

    def _define_escalates(self, ep_num: int, block: dict) -> list[str]:
        """Define what this episode escalates."""
        return [f"Escala: {block['function']}"]

    def _define_rewards(self, ep_num: int, block: dict) -> list[str]:
        """Define what this episode rewards."""
        return [f"Entrega recompensa: avance en {block['function']}"]

    def _define_opens(self, ep_num: int, block: dict, central_questions: list, sub_mysteries: list) -> list[str]:
        """Define what this episode opens."""
        return [f"Abre: {sub_mysteries[(ep_num - 1) % len(sub_mysteries)]}"]

    def _select_reference_patterns(self, ep_num: int, reference_dna: dict) -> list[str]:
        """Select reference DNA patterns to apply to this episode."""
        patterns = []
        narrative_dna = reference_dna.get("narrative_dna", {})
        editing_dna = reference_dna.get("editing_dna", {})
        attention = reference_dna.get("attention_psychology", {})

        # Apply relevant patterns based on episode position
        if ep_num <= 5:
            patterns.append(narrative_dna.get("world_promise", ""))
            patterns.append(narrative_dna.get("character_identification", ""))
        if ep_num % 3 == 0:
            patterns.append(attention.get("reaction_chain", ""))
        if ep_num % 4 == 0:
            patterns.append(narrative_dna.get("status_contrast", ""))
        if ep_num >= 10 and ep_num % 5 == 0:
            patterns.append(narrative_dna.get("threat", ""))
            patterns.append(attention.get("reward_then_threat", ""))
        if ep_num >= 20:
            patterns.append(narrative_dna.get("consequence", ""))
            patterns.append(attention.get("threat_escalation", ""))

        return [p for p in patterns if p]

    def _create_macro_hook(self, season_arc: dict, reference_dna: dict) -> str:
        """Create macro hook for the season."""
        narrative_dna = reference_dna.get("narrative_dna", {})
        world_promise = narrative_dna.get("world_promise", "Un mundo de secretos y poder")
        return f"{world_promise}: {season_arc['concept']} — Una promesa de {season_arc['genre']} que abarca 40 episodios de revelaciones escalonadas."

    def _create_premise(self, concept_seed: str, genre: str) -> str:
        """Create season premise."""
        return f"En un mundo de {genre}, {concept_seed.lower()}. Cada episodio revela una capa más de la verdad, escalando desde deseo personal hasta consecuencias globales."

    def _calculate_pressure_ladder(self, total_episodes: int) -> list[dict]:
        """Calculate pressure ladder for all episodes."""
        return [
            {"episode": i, "pressure": self._calculate_pressure(i, total_episodes)}
            for i in range(1, total_episodes + 1)
        ]

    def _create_character_arcs(self, episodes: list, genre: str, reference_dna: dict) -> list[dict]:
        """Create character arcs for main characters."""
        archetypes = ["protagonist", "antagonist", "mentor", "ally", "love_interest", "traitor"]
        arcs = []
        for i, archetype in enumerate(archetypes):
            arcs.append({
                "character_id": f"char_{i+1:03d}",
                "archetype": archetype,
                "arc_type": self._select_arc_type(archetype, genre),
                "want": f"Deseo del {archetype}",
                "need": f"Necesidad del {archetype}",
                "lie": f"Mentira del {archetype}",
                "ghost": f"Fantasma del {archetype}",
                "secret": f"Secreto del {archetype}",
                "episodes_involved": list(range(1, len(episodes) + 1))
            })
        return arcs

    def _select_arc_type(self, archetype: str, genre: str) -> str:
        """Select arc type for archetype."""
        arc_types = {
            "protagonist": "redemption_vs_revenge",
            "antagonist": "power_corruption",
            "mentor": "sacrificial_guidance",
            "ally": "loyalty_tested",
            "love_interest": "agency_awakening",
            "traitor": "double_agent_reveal"
        }
        return arc_types.get(archetype, "transformation")

    def _create_relationship_arcs(self, episodes: list, character_arcs: list) -> list[dict]:
        """Create relationship arcs between characters."""
        relationships = [
            {"between": ["char_001", "char_002"], "type": "antagonist_protagonist", "arc": "hatred_to_understanding"},
            {"between": ["char_001", "char_004"], "type": "allies", "arc": "trust_to_betrayal_to_redemption"},
            {"between": ["char_001", "char_005"], "type": "romantic", "arc": "attraction_to_partnership"},
            {"between": ["char_002", "char_003"], "type": "mentor_student", "arc": "manipulation_to_genuine_care"},
            {"between": ["char_004", "char_006"], "type": "friendship", "arc": "loyalty_to_sacrifice"}
        ]
        return relationships

    def _create_mystery_architecture(self, episodes: list, total_episodes: int) -> dict:
        """Create mystery architecture with setup/payoff mapping."""
        mysteries = []
        for i in range(4):  # 4 major mysteries
            setup_ep = (i + 1) * 8
            reveal_ep = setup_ep + 6
            payoff_ep = reveal_ep + 4
            mysteries.append({
                "mystery_id": f"mystery_{i+1}",
                "setup_episode": min(setup_ep, total_episodes),
                "reveal_episode": min(reveal_ep, total_episodes),
                "payoff_episode": min(payoff_ep, total_episodes),
                "type": ["identity", "origin", "conspiracy", "betrayal"][i]
            })

        return {
            "major_mysteries": mysteries,
            "mini_mysteries": [
                {"setup": i, "reveal": i+3, "payoff": i+6}
                for i in range(1, total_episodes, 5)
                if i + 6 <= total_episodes
            ]
        }

    def _create_subplots(self, episodes: list, total_episodes: int) -> list[dict]:
        """Create subplot structure."""
        subplots = []
        subplot_types = [
            "family_secret", "political_intrigue", "past_trauma",
            "secondary_romance", "rivalry", "redemption_quest"
        ]

        for i, stype in enumerate(subplot_types):
            start = (i + 1) * 3
            end = min(start + 10, total_episodes)
            subplots.append({
                "subplot_id": f"subplot_{i+1}",
                "type": stype,
                "start_episode": start,
                "end_episode": end,
                "converges_at": total_episodes - 2
            })

        return subplots
