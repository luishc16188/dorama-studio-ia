# dorama_studio/agents/narrative/story_architect.py
"""
Story Architect Agent - Showrunner de élite para doramas verticales de 90s × 20 eps.
Crea originalidad mediante subversión de tropo, arquitectura de revelaciones y escalada de stakes.
Integrado con Quality Gate 100pts, Creative Genome 70/20/10, Knowledge Ledger y Story Graph.
"""

import logging
from typing import Any, Dict, List

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.creative_genome import CreativeGenomeV2 as CreativeGenome
from dorama_studio.core.knowledge_ledger import knowledge_ledger, KnowledgeState
from dorama_studio.core.story_graph import story_graph_manager, StoryNode, StoryEdge
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)

class StoryArchitectAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Story Architect Agent que crea arquitectura de historia completa.
    Valida con Quality Gate, respeta presupuesto Creative Genome,
    y mantiene conocimiento y grafo de historia.
    """

    InputSchema = dict[str, Any]
    OutputSchema = dict[str, Any]

    def __init__(self):
        super().__init__("StoryArchitectAgent")
        self.agent_name = "StoryArchitectAgent"
        # Inicializar Creative Genome para tracking de presupuesto
        self.creative_genome = CreativeGenome(
            agent_name="story_architect",
            session_id=f"story_arch_{hash(str(__file__))}"
        )
        logger.info("StoryArchitectAgent inicializado con Quality Gate, Creative Genome, Knowledge Ledger y Story Graph")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the story architect agent."""
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

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Crea arquitectura de historia completa desde concept seed.
        Aplica Quality Gate 100pts y verifica presupuesto 70/20/10.
        Integra Knowledge Ledger y Story Graph.

        Args:
            validated_input: Dict con concept_seed, genre, num_episodes, episode_duration, seed_identifier

        Returns:
            Dict con universe, character_bible, season_arc, central_secret, antagonist, episodes, quality_gate
        """
        concept_seed = validated_input.get("concept_seed", "")
        genre = validated_input.get("genre", "romance_traicion")
        num_episodes = validated_input.get("num_episodes", 20)
        episode_duration = validated_input.get("episode_duration", 90)
        seed_identifier = validated_input.get("seed_identifier", concept_seed[:50] if concept_seed else "default")

        logger.info(f"Architecting story: {concept_seed} ({genre}, {num_episodes} eps)")

        # Verificar presupuesto Creative Genome antes de generar
        budget_check = self.creative_genome.check_budget(agent_name=self.agent_name, genre=genre)
        logger.info(f"Presupuesto Creative Genome: {budget_check}")

        # Determinar tipo de mutación basado en presupuesto disponible
        mutation_type = self._determine_mutation_type(budget_check)

        # Generar arquitectura
        story_architecture = self.architect_story(
            concept_seed, genre, num_episodes, episode_duration, seed_identifier, mutation_type
        )

        # Registrar uso de mutación en Creative Genome
        self.creative_genome.record_mutation(
            mutation_type=mutation_type,
            seed_identifier=seed_identifier,
            genre=genre
        )

        # Actualizar Knowledge Ledger con información adquirida durante la arquitectura
        self._update_knowledge_ledger(story_architecture, concept_seed, genre)

        # Actualizar Story Graph con la arquitectura generada
        self._update_story_graph(story_architecture, concept_seed, genre, num_episodes)

        # Aplicar Quality Gate a la arquitectura generada
        quality_result = self._apply_quality_gate(story_architecture, genre, num_episodes)

        # Agregar metadatos de calidad y presupuesto al resultado
        story_architecture["quality_gate"] = quality_result
        story_architecture["creative_genome"] = {
            "mutation_type_used": mutation_type,
            "budget_before": budget_check,
            "budget_after": self.creative_genome.check_budget(agent_name=self.agent_name, genre=genre)
        }
        story_architecture["knowledge_ledger"] = {
            "events_recorded": len(self._get_recent_knowledge_events())
        }
        story_architecture["story_graph"] = {
            "nodes": len(story_graph_manager.graph.nodes),
            "edges": len(story_graph_manager.graph.edges)
        }

        return story_architecture

    def _determine_mutation_type(self, budget_check: dict[str, int]) -> str:
        """
        Determina qué tipo de mutación usar basado en presupuesto disponible.
        Prioriza proven > exploration > big_bet según Creative Genome 70/20/10.
        """
        if budget_check.get("proven_available", 0) >= 10:
            return "proven"
        elif budget_check.get("exploration_available", 0) >= 5:
            return "exploration"
        elif budget_check.get("big_bet_available", 0) >= 2:
            return "big_bet"
        else:
            # Presupuesto agotado - usar proven como fallback
            logger.warning("Presupuesto Creative Genome agotado, usando proven como fallback")
            return "proven"

    def _apply_quality_gate(self, story_architecture: dict[str, Any], genre: str, num_episodes: int) -> dict[str, Any]:
        """
        Aplica Quality Gate 100pts (15 dimensiones) a la arquitectura de historia.
        Evalúa estructura, personajes, arcos, cliffhangers, etc.
        """
        # Extraer datos para evaluación
        episodes = story_architecture.get("episodes", [])
        character_bible = story_architecture.get("character_bible", [])
        season_arc = story_architecture.get("season_arc", {})
        universe = story_architecture.get("universe", {})
        central_secret = story_architecture.get("central_secret", "")
        antagonist = story_architecture.get("antagonist", {})

        # Preparar episode_data para quality_gate del base_agent
        episode_data = self._extract_architecture_quality_data(
            episodes, character_bible, season_arc, universe, central_secret, antagonist, genre, num_episodes
        )

        # Usar quality_gate heredado de BaseAgent
        approved, deficiencies = self.quality_gate(None, episode_data)  # type: ignore

        # Calcular score
        quality_score = self._calculate_architecture_quality_score(episode_data)

        return {
            "approved": approved,
            "score": quality_score,
            "deficiencies": deficiencies,
            "threshold": 85,
            "details": episode_data
        }

    def _extract_architecture_quality_data(self, episodes: list[dict], character_bible: list[dict],
                                           season_arc: dict, universe: dict, central_secret: str,
                                           antagonist: dict, genre: str, num_episodes: int) -> dict[str, Any]:
        """
        Extrae datos de la arquitectura para evaluar 15 dimensiones del Quality Gate.
        """
        data = {}

        # 1. Hook 0-3s: Verificar que el episodio 1 tiene hook explosivo
        ep1 = next((e for e in episodes if e.get("ep") == 1), {})
        data["hook_0_3s"] = bool(ep1.get("hook_category") and ep1.get("core_conflict"))

        # 2. Conflict concrete: Conflicto central definido
        data["conflict_concrete"] = all(
            e.get("core_conflict") and len(e.get("core_conflict", "")) > 20
            for e in episodes
        )

        # 3. Protagonist desire clarified: Protagonista tiene want/need claros
        protagonist = next((c for c in character_bible if c.get("role") == "protagonist"), {})
        data["protagonist_desire_clarified"] = bool(
            protagonist.get("want") and protagonist.get("need")
        )

        # 4. Unresolved question: Preguntas abiertas en mystery_map
        mystery_map = season_arc.get("mystery_map", {})
        data["unresolved_question"] = bool(
            mystery_map.get("central_question") and mystery_map.get("clues_per_episode", 0) > 0
        )

        # 5. Situation worsens: Escalamiento en intensity ladder
        beats = season_arc.get("beats", [])
        pressures = [b.get("pressure", 0) for b in beats if "pressure" in b]
        data["situation_worsens"] = all(
            pressures[i] <= pressures[i+1] for i in range(len(pressures)-1)
        ) if len(pressures) > 1 else True

        # 6. Partial answer: Reveal map tiene revelaciones programadas
        reveal_map = season_arc.get("reveal_map", {})
        data["partial_answer"] = len(reveal_map) >= 3

        # 7. Surprise element: Subversiones en episodios
        data["surprise_element"] = all(
            e.get("subversion_applied") and e.get("subversion_applied") != "none"
            for e in episodes
        )

        # 8. Strong cliffhanger: Cada episodio tiene cliffhanger definido y rotado
        cliffhanger_types = [e.get("cliffhanger", "") for e in episodes]
        unique_types = len(set(cliffhanger_types))
        data["strong_cliffhanger"] = (
            all(c for c in cliffhanger_types) and
            unique_types >= min(5, num_episodes)  # Al menos 5 tipos únicos
        )

        # 9. Emotional impact: Arco emocional en season_arc
        data["emotional_impact"] = bool(
            season_arc.get("theme") and season_arc.get("beats")
        )

        # 10. Show don't tell: Universe tiene reglas visuales y world_rules
        data["show_dont_tell"] = bool(
            universe.get("world_rules") and universe.get("visual_tone")
        )

        # 11. Dialogue advances story: Personajes tienen contradiction y moral_line
        data["dialogue_advances_story"] = all(
            c.get("contradiction") and c.get("moral_line")
            for c in character_bible if c.get("role") in ["protagonist", "antagonist"]
        )

        # Dimensiones adicionales para arquitectura
        # 12. Central secret exists and is compelling
        data["central_secret_compelling"] = bool(central_secret and len(central_secret) > 50)

        # 13. Antagonist has understandable motivation
        data["antagonist_understandable"] = bool(
            antagonist.get("goal") and antagonist.get("method") and antagonist.get("weakness")
        )

        # 14. Genre consistency: hook categories match genre expectations
        genre_hook_map = {
            "romance_traicion": ["betrayal", "revelation", "identity_shock", "impossible_romance"],
            "venganza_sofisticada": ["revenge", "power_reveal", "humiliation", "threat"],
            "thriller_domestico": ["threat", "betrayal", "humiliation", "moral_dilemma"],
        }
        expected_categories = genre_hook_map.get(genre, [])
        used_categories = set(e.get("hook_category") for e in episodes)
        data["genre_consistency"] = len(used_categories.intersection(set(expected_categories))) >= 3

        # 15. Episode structure completeness: 9 beats implícitos por episodio
        data["episode_structure_complete"] = all(
            e.get("core_conflict") and e.get("twist") and e.get("cliffhanger") and e.get("cta_type")
            for e in episodes
        )

        return data

    def _calculate_architecture_quality_score(self, episode_data: dict[str, Any]) -> float:
        """
        Calcula puntaje de calidad para arquitectura (15 dimensiones + 3 bonus).
        Máximo: 115pts (100 base + 15 bonus). Umbral PASS: ≥85.
        """
        base_checks = [
            ("hook_0_3s", 20),
            ("conflict_concrete", 15),
            ("protagonist_desire_clarified", 15),
            ("unresolved_question", 15),
            ("situation_worsens", 15),
            ("partial_answer", 10),
            ("surprise_element", 10),
            ("strong_cliffhanger", 10),
            ("emotional_impact", 5),
            ("show_dont_tell", 5),
            ("dialogue_advances_story", 5),
        ]

        bonus_checks = [
            ("central_secret_compelling", 5),
            ("antagonist_understandable", 5),
            ("genre_consistency", 5),
            ("episode_structure_complete", 5),
        ]

        score = 0.0
        for field, pts in base_checks:
            if episode_data.get(field):
                score += pts

        for field, pts in bonus_checks:
            if episode_data.get(field):
                score += pts

        return min(115.0, score)

    def _update_knowledge_ledger(self, story_architecture: dict[str, Any], concept_seed: str, genre: str) -> None:
        """
        Update the Knowledge Ledger with information acquired during story architecture.
        """
        try:
            # Record the concept seed as known information
            knowledge_ledger.acquire_knowledge(
                character_id="narrative_knowledge",
                knowledge_type="concept_seed",
                knowledge_state=KnowledgeState.KNOWS,
                source=KnowledgeSource.DIRECT_OBSERVATION,
                source_reference=concept_seed,
                confidence=1.0,
                context={"genre": genre, "timestamp": datetime.utcnow().isoformat()}
            )

            # Record genre knowledge
            knowledge_ledger.acquire_knowledge(
                character_id="narrative_knowledge",
                knowledge_type="genre_expectations",
                knowledge_state=KnowledgeState.KNOWS,
                source=KnowledgeSource.DIRECT_OBSERVATION,
                source_reference=genre,
                confidence=1.0,
                context={"concept_seed": concept_seed, "timestamp": datetime.utcnow().isoformat()}
            )

            # Record key architectural elements as knowledge
            universe = story_architecture.get("universe", {})
            if universe:
                knowledge_ledger.acquire_knowledge(
                    character_id="narrative_knowledge",
                    knowledge_type="universe_core_conflict",
                    knowledge_state=KnowledgeState.KNOWS,
                    source=KnowledgeSource.DIRECT_OBSERVATION,
                    source_reference=universe.get("core_conflict", ""),
                    confidence=0.9,
                    context={"universe_name": universe.get("name", ""), "timestamp": datetime.utcnow().isoformat()}
                )

            character_bible = story_architecture.get("character_bible", [])
            if character_bible:
                protagonist = next((c for c in character_bible if c.get("role") == "protagonist"), None)
                if protagonist:
                    knowledge_ledger.acquire_knowledge(
                        character_id="narrative_knowledge",
                        knowledge_type="protagonist_want",
                        knowledge_state=KnowledgeState.KNOWS,
                        source=KnowledgeSource.DIRECT_OBSERVATION,
                        source_reference=protagonist.get("want", ""),
                        confidence=0.9,
                        context={"character_name": protagonist.get("name", ""), "timestamp": datetime.utcnow().isoformat()}
                    )

                    knowledge_ledger.acquire_knowledge(
                        character_id="narrative_knowledge",
                        knowledge_type="protagonist_need",
                        knowledge_state=KnowledgeState.KNOWS,
                        source=KnowledgeSource.DIRECT_OBSERVATION,
                        source_reference=protagonist.get("need", ""),
                        confidence=0.9,
                        context={"character_name": protagonist.get("name", ""), "timestamp": datetime.utcnow().isoformat()}
                    )

            logger.info("Knowledge Ledger updated with story architecture information")
        except Exception as e:
            logger.warning(f"Failed to update Knowledge Ledger: {e}")

    def _update_story_graph(self, story_architecture: dict[str, Any], concept_seed: str, genre: str, num_episodes: int) -> None:
        """
        Update the Story Graph with the generated story architecture.
        """
        try:
            # Add universe node
            universe = story_architecture.get("universe", {})
            if universe:
                universe_node_id = story_graph_manager.add_node(
                    node_id=f"universe_{hash(universe.get('name', ''))}",
                    node_type="universe",
                    timestamp=datetime.utcnow().isoformat(),
                    description=f"Universe: {universe.get('name', 'Unknown')}",
                    metadata={
                        "setting": universe.get("setting", ""),
                        "core_conflict": universe.get("core_conflict", ""),
                        "world_rules": universe.get("world_rules", []),
                        "visual_tone": universe.get("visual_tone", "")
                    }
                )

                # Add concept seed as setup node
                setup_node_id = story_graph_manager.add_node(
                    node_id=f"setup_{hash(concept_seed)}",
                    node_type="setup",
                    timestamp=datetime.utcnow().isoformat(),
                    description=f"Concept seed: {concept_seed[:50]}...",
                    metadata={
                        "genre": genre,
                        "seed_identifier": concept_seed[:50] if concept_seed else "default"
                    }
                )

                # Connect setup to universe (setup informs universe understanding)
                story_graph_manager.add_edge(
                    source_node_id=setup_node_id,
                    target_node_id=universe_node_id,
                    relationship_type="informs",
                    strength=0.8,
                    metadata={"connection_type": "concept_to_universe"}
                )

            # Add season arc node
            season_arc = story_architecture.get("season_arc", {})
            if season_arc:
                season_node_id = story_graph_manager.add_node(
                    node_id=f"season_arc_{hash(str(season_arc.get('theme', '')))}",
                    node_type="season_arc",
                    timestamp=datetime.utcnow().isoformat(),
                    description=f"Season Arc: {season_arc.get('theme', 'Unknown Theme')}",
                    metadata={
                        "beats": season_arc.get("beats", []),
                        "mystery_map": season_arc.get("mystery_map", {}),
                        "reveal_map": season_arc.get("reveal_map", {}),
                        "payoff_map": season_arc.get("payoff_map", {})
                    }
                )

                # Connect universe to season arc (universe enables season arc)
                if 'universe_node_id' in locals():
                    story_graph_manager.add_edge(
                        source_node_id=universe_node_id,
                        target_node_id=season_node_id,
                        relationship_type="enables",
                        strength=0.9,
                        metadata={"connection_type": "universe_to_season"}
                    )

            # Add character bible nodes
            character_bible = story_architecture.get("character_bible", [])
            for character in character_bible:
                char_id = character.get("id", f"char_{hash(character.get('name', ''))}")
                char_node_id = story_graph_manager.add_node(
                    node_id=f"character_{char_id}",
                    node_type="character",
                    timestamp=datetime.utcnow().isoformat(),
                    description=f"Character: {character.get('name', 'Unknown')} ({character.get('role', 'Unknown')})",
                    metadata={
                        "archetype": character.get("archetype", ""),
                        "want": character.get("want", ""),
                        "need": character.get("need", ""),
                        "lie": character.get("lie", ""),
                        "ghost": character.get("ghost", ""),
                        "secret": character.get("secret", ""),
                        "moral_line": character.get("moral_line", ""),
                        "contradiction": character.get("contradiction", ""),
                        "archetype_subversion": character.get("archetype_subversion", ""),
                        "physical": character.get("physical", {}),
                        "micro_expressions": character.get("micro_expressions", {}),
                        "voice_profile": character.get("voice_profile", {}),
                        "wardrobe": character.get("wardrobe", {}),
                        "continuity_rules": character.get("continuity_rules", {})
                    }
                )

                # Connect character to universe (character exists in universe)
                if 'universe_node_id' in locals():
                    story_graph_manager.add_edge(
                        source_node_id=universe_node_id,
                        target_node_id=char_node_id,
                        relationship_type="contains",
                        strength=1.0,
                        metadata={"connection_type": "universe_contains_character"}
                    )

            # Add episode nodes
            episodes = story_architecture.get("episodes", [])
            for episode in episodes:
                ep_num = episode.get("ep", 0)
                ep_node_id = story_graph_manager.add_node(
                    node_id=f"episode_{ep_num}",
                    node_type="episode",
                    timestamp=datetime.utcnow().isoformat(),
                    description=f"Episode {ep_num}: {episode.get('hook_category', 'Unknown')} hook",
                    metadata={
                        "hook_category": episode.get("hook_category", ""),
                        "core_conflict": episode.get("core_conflict", ""),
                        "twist": episode.get("twist", ""),
                        "cliffhanger": episode.get("cliffhanger", ""),
                        "cta_type": episode.get("cta_type", ""),
                        "pressure_level": episode.get("pressure_level", 0),
                        "fractal_formula_applied": episode.get("fractal_formula_applied", ""),
                        "subversion_applied": episode.get("subversion_applied", "")
                    }
                )

                # Connect season arc to episode (season arc contains episodes)
                if 'season_node_id' in locals():
                    story_graph_manager.add_edge(
                        source_node_id=season_node_id,
                        target_node_id=ep_node_id,
                        relationship_type="contains",
                        strength=1.0,
                        metadata={"connection_type": "season_contains_episode"}
                    )

                # Connect character to episode (characters participate in episodes)
                for character in character_bible:
                    char_id = character.get("id", f"char_{hash(character.get('name', ''))}")
                    char_node_id = f"character_{char_id}"
                    if char_node_id in [n.node_id for n in story_graph_manager.graph.values()]:
                        story_graph_manager.add_edge(
                            source_node_id=char_node_id,
                            target_node_id=ep_node_id,
                            relationship_type="participates_in",
                            strength=0.8,
                            metadata={"connection_type": "character_episode_participation"}
                        )

            logger.info("Story Graph updated with story architecture information")
        except Exception as e:
            logger.warning(f"Failed to update Story Graph: {e}")

    def _get_recent_knowledge_events(self, limit: int = 10) -> list:
        """Get recent knowledge events for reporting."""
        try:
            return knowledge_ledger.get_knowledge_events(limit=limit)
        except Exception:
            return []

    def architect_story(self,
                       concept_seed: str,
                       genre: str,
                       num_episodes: int,
                       episode_duration: int = 90,
                       seed_identifier: str = "default",
                       mutation_type: str = "proven") -> dict[str, Any]:
        """
        Crea arquitectura de historia completa con universo, personajes, arco de temporada y blueprints.
        El mutation_type influye en el nivel de subversión/innovación aplicado.
        """
        # Subversión más agresiva para exploration/big_bet
        subversion_intensity = {
            "proven": "subversión sutil de tropos conocidos",
            "exploration": "subversión moderada con giros inesperados",
            "big_bet": "subversión radical, estructura experimental"
        }.get(mutation_type, "subversión estándar")

        # Universo base (determinista para testing, en producción usaría LLM)
        universe = {
            "name": "Imperio Ferroviario Li",
            "setting": "Metrópolis industrial con líneas férreas que controlan la economía",
            "visual_tone": "neo-noir industriel",
            "core_conflict": "poder hereditario vs mérito ganado",
            "world_rules": [
                "El apellido Li controla todas las líneas férreas desde 1920",
                "Solo los herederos de sangre pueden operar el Motor Central",
                "El secreto de la combustión eterna está enterrado bajo la estación principal"
            ],
            "aesthetic_identity": {
                "color_palette": ["#0A1128", "#FFDFC4", "#FFE49E", "#FF3344"],
                "lighting_style": "contrast_chiaroscuro",
                "lens_preference": "anamorfico_85mm",
                "texture_quality": "granulado_35mm"
            }
        }

        # Character Bible con heridas arquetípicas (Capa 7 RESEARCH_CONSOLIDATED)
        character_bible = [
            {
                "id": "char_001",
                "name": "Li Wei",
                "role": "protagonist",
                "archetype": "ruler",
                "want": "venganza por la muerte sospechosa de su padre",
                "need": "aprender a confiar y perdonar",
                "lie": "no necesita a nadie para tener éxito",
                "ghost": "creció en orfanato después de que lo expulsaran de la mansión familiar",
                "secret": "sabía desde el día 1 que era el heredero legítimo",
                "moral_line": "no matar a inocentes, incluso si son enemigos",
                "contradiction": "busca justicia pero usa métodos de villano",
                "archetype_subversion": f"el ruler que se niega a sentarse en el trono hasta probar su valía ({subversion_intensity})",
                "physical": {
                    "height_cm": 182,
                    "build": "athletic",
                    "hair_color": "dark_brown_ash",
                    "hair_style": "slicked_back",
                    "eye_color": "#1a2332",
                    "skin_tone": "fair_porcelain",
                    "distinguishing_marks": ["beauty_mark_left_cheek"],
                    "age_apparent": 32,
                    "face_shape": "heart",
                    "bone_structure": "sharp_jaw_high_cheekbones"
                },
                "micro_expressions": {
                    "tell": "contiene la respiración al mentir",
                    "eye_dart": "down_left",
                    "micro_smile": True,
                    "jaw_clench": True,
                    "breath_hitch": True
                },
                "voice_profile": {
                    "voice_id": "pNInz6obpgDQGcFmaJgB",
                    "accent": "es-419",
                    "pitch_range": "low",
                    "speaking_rate": "slow",
                    "breathiness": 0.1,
                    "roughness": 0.2,
                    "emotional_range": {
                        "cold": 0.9,
                        "contained_betrayal": 0.8
                    }
                },
                "wardrobe": {
                    "signature_style": "minimalist executive",
                    "color_palette": ["charcoal", "black", "white", "silver"],
                    "key_items": ["charcoal_brioni_suit", "white_italian_shirt", "black_silk_tie"],
                    "accessories": ["patek_philippe_nautilus", "silver_tie_clip"]
                },
                "continuity_rules": {
                    "locked_traits": ["face_shape", "eye_color", "bone_structure", "distinguishing_marks"],
                    "allowed_variations": {
                        "hair_style": ["slicked_back", "loose", "wet"]
                    },
                    "drift_tolerance": 0.05,
                    "deform_prohibited": ["face_shape", "eye_color", "hair_color"],
                    "master_reference_prompt": "hyper-detailed prompt para Flux/Imagen: 85mm f/1.4, volumetric rim light, skin texture pores, K-Drama cold palette #1a2332/#e8d5b7, micro-expression: contained betrayal",
                    "psychological_arc_by_episode": [
                        {"ep": 1, "state": "want_dominant", "subtext": "cree que el poder es la única forma de proteger lo que ama"},
                        {"ep": 10, "state": "transition", "subtext": "empieza a cuestionar si la venganza lo está consumiendo"},
                        {"ep": 20, "state": "need_dominant", "subtext": "entendió que el verdadero poder está en proteger, no destruir"}
                    ]
                }
            }
        ]

        # Season Arc con Intensity Ladder (Capa 6 RESEARCH_CONSOLIDATED)
        season_arc = {
            "theme": "la verdadera herencia no es el poder, sino quiénes elegimos proteger",
            "beats": [
                {"ep": 1, "beat_type": "inciting", "description": "Li Wei descubre que su 'accidente' fue un asesinato", "pressure": 20},
                {"ep": 5, "beat_type": "setup_next", "description": "Primer aliado inesperado dentro de la empresa enemiga", "pressure": 42},
                {"ep": 10, "beat_type": "midpoint", "description": "Revela que el Motor Central funciona con energía limpia robada", "pressure": 52},
                {"ep": 15, "beat_type": "setup_next", "description": "Descubre que su aliado es el hijo de su mayor enemigo", "pressure": 72},
                {"ep": 20, "beat_type": "resolution", "description": "Decide compartir la tecnología en lugar de monopolizarla", "pressure": 100}
            ],
            "mystery_map": {
                "central_question": "¿Quién realmente controla el Motor Central y por qué ocultaron su función limpia?",
                "clues_per_episode": 2,
                "red_herrings": ["el contador corrupto", "la aparentemente leal secretaria"]
            },
            "reveal_map": {
                "secret_reveal_ep": 12,
                "power_source_reveal_ep": 16,
                "true_antagonist_reveal_ep": 19
            },
            "payoff_map": {
                "vengence_payoff": "ep 18",
                "redemption_payoff": "ep 20",
                "legacy_payoff": "ep 20"
            }
        }

        central_secret = "El Motor Central no requiere combustibles fósiles, sino una cristalización de energía limpia que la familia Li ha estado ocultando para mantener su monopolio energético"

        # Antagonista Viral (Capa 8 RESEARCH_CONSOLIDATED)
        antagonist = {
            "name": "Chen Xiao (Secretaria Aparente)",
            "goal": "proteger el secreto de la energía limpia a cualquier costo",
            "method": "manipular información y crear conflictos internos",
            "weakness": "su lealtad a la verdadera misión de su familia",
            "connection_to_protag": "ella es la verdadera heredera, Li Wei es el hijo ilegítimo que cree que es legítimo",
            "humanity_moment": "ep 14 - revela que protege la tecnología para evitar una guerra energética global"
        }

        # Episodes con 9 beats implícitos, hook categories rotados, cliffhangers variados
        hook_categories = [
            HookCategory.betrayal,
            HookCategory.revelation,
            HookCategory.visual_shock,
            HookCategory.threat,
            HookCategory.moral_dilemma,
            HookCategory.power_reveal,
            HookCategory.humiliation,
            HookCategory.prohibition,
            HookCategory.impossible_romance,
            HookCategory.revenge,
            HookCategory.question
        ]

        # Cliffhanger types para rotación obligatoria (Capa 7 RESEARCH_CONSOLIDATED)
        cliffhanger_types = [
            "revelación",
            "amenaza",
            "decisión",
            "identidad",
            "traición",
            "acción_interrumpida",
            "respuesta_congelada",
            "reversal"
        ]

        episodes = []
        for ep in range(1, num_episodes + 1):
            # Rotar hook category
            hook_category = hook_categories[(ep - 1) % len(hook_categories)].value

            # Rotar cliffhanger type (no repetir consecutivos)
            cliffhanger_type = cliffhanger_types[(ep - 1) % len(cliffhanger_types)]

            # CTA type rotado
            cta_types = [CTAType.MORAL_DILEMMA, CTAType.REVENGE_CHOICE, CTAType.IDENTITY_TEASE, CTAType.TEAM_WAR]
            cta_type = cta_types[(ep - 1) % len(cta_types)].value

            # Intensity ladder pressure
            pressure = min(20 + (ep - 1) * 4, 100)  # 20, 24, 28... up to 100

            episode = {
                "ep": ep,
                "hook_category": hook_category,
                "core_conflict": f"Conflicto central del episodio {ep} relacionado con el control del Motor Central (presión: {pressure}%)",
                "twist": f"Giro que redefine la alianza en el episodio {ep} - {subversion_intensity}",
                "cliffhanger": f"[{cliffhanger_type.upper()}] Decisión imposible que deja al público en vilo para el episodio {ep + 1 if ep < num_episodes else 1}",
                "cta_type": cta_type,
                "subversion_applied": f"Subversión del tropo {hook_category} mediante revelación de motivaciones opuestas a las aparentes - {subversion_intensity}",
                "pressure_level": pressure,
                "fractal_formula_applied": "H→P→Q→E→R→Q2→C"  # Documentado para validación
            }
            episodes.append(episode)

        return {
            "universe": universe,
            "character_bible": character_bible,
            "season_arc": season_arc,
            "central_secret": central_secret,
            "antagonist": antagonist,
            "episodes": episodes,
            "mutation_type": mutation_type,
            "subversion_intensity": subversion_intensity
        }