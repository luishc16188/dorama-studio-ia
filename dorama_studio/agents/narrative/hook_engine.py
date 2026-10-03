# dorama_studio/agents/narrative/hook_engine.py
"""
Hook Lab Agent v4.0 - Generates 100-150 hook hypotheses with novelty checking.
Replaces the simple Hook Engine with a full-scale creativity lab.
"""

import logging
import random
from collections import deque
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.originality_engine_agent import OriginalityEngineAgent
from dorama_studio.creative_genome import CreativeGenomeV2 as CreativeGenome
from dorama_studio.core.knowledge_ledger import knowledge_ledger, KnowledgeState
from dorama_studio.core.story_graph import story_graph_manager, StoryNode, StoryEdge
from datetime import datetime

logger = logging.getLogger(__name__)


class HookEngineAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    def __init__(self, agent_name: str = "hook_engine", session_id: str = None):
        super().__init__(agent_name)
        self.agent_name = agent_name
        self.session_id = session_id or f"hook_{hash(str(__file__))}"

        # Initialize dependencies for novelty checking
        try:
            self.originality_engine = OriginalityEngineAgent()
            self.creative_genome = CreativeGenome(
                agent_name=self.agent_name, session_id=self.session_id
            )
            logger.info(
                "Hook Engine initialized with Originality Engine and Creative Genome"
            )
        except Exception as e:
            logger.warning(
                f"Could not initialize dependencies for novelty checking: {e}"
            )
            self.originality_engine = deque([], maxlen=10)  # placeholder for None
            self.creative_genome = None

        # Define extensive libraries for hook generation
        self._init_libraries()

    def _process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process method required by BaseAgent - delegates to execute method."""
        return self.execute(input_data)

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the hook engine agent."""
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

    def _init_libraries(self):
        """Initialize the libraries of mechanisms, emotions, visuals, audio, and script templates."""

        # Mechanism Library (core emotional/cognitive turns)
        self.mechanisms = [
            "power_reversal",
            "identity_flip",
            "loyalty_shift",
            "morality_inversion",
            "knowledge_reveal",
            "emotional_journey",
            "social_status_shift",
            "time_manipulation",
            "truth_revelation",
            "betrayal_exposure",
            "innocence_proven",
            "guilty_realization",
            "ally_becomes_enemy",
            "enemy_becomes_ally",
            "weak_to_strong",
            "strong_falls",
            "smart_fool",
            "fool_outsmarts",
            "love_to_hate",
            "hate_to_love",
            "trust_shattered",
            "trust_earned",
            "secret_kept",
            "secret_revealed",
            "promise_broken",
            "promise_kept",
            "sacrifice_made",
            "sacrifice_refused",
            "justice_served",
            "justice_denied",
            "freedom_gained",
            "freedom_lost",
            "knowledge_gained",
            "knowledge_lost",
            "hope_found",
            "hope_lost",
        ]

        # Emotion Library (target emotional impact)
        self.emotions = [
            "shock",
            "surprise",
            "betrayal",
            "anger",
            "fear",
            "sadness",
            "joy",
            "disgust",
            "trust",
            "anticipation",
            "suspense",
            "tension",
            "curiosity",
            "satisfaction",
            "relief",
            "guilt",
            "shame",
            "pride",
            "humiliation",
            "vindication",
            "validation",
            "devastation",
            "euphoria",
            "terror",
            "awe",
        ]

        # Visual Technique Library (camera, lighting, composition) - ENHANCED WITH OASIZ 0-2s VISUAL HOOKS
        self.visuals = [
            {
                "type": "ECU",
                "description": "Extreme close-up on eyes/hands/object - MACRO SHOT FOR 0-2s HOOK",
                "technique": "push_in",
                "use_case": "hook_0_2s",
            },
            {
                "type": "ECU_EYE",
                "description": "Extreme close-up on eye with reflection or detail",
                "technique": "push_in",
                "use_case": "hook_0_2s",
            },
            {
                "type": "ECU_HAND",
                "description": "Extreme close-up on hands manipulating object",
                "technique": "push_in",
                "use_case": "hook_0_2s",
            },
            {
                "type": "CU",
                "description": "Close-up on face/object",
                "technique": "rack_focus",
            },
            {"type": "MCU", "description": "Medium close-up", "technique": "tilt_down"},
            {
                "type": "WS",
                "description": "Wide shot establishing context",
                "technique": "crane_up",
            },
            {
                "type": "insert_shot",
                "description": "Insert shot of critical detail",
                "technique": "match_cut",
            },
            {
                "type": "point_of_view",
                "description": "POV shot showing what character sees",
                "technique": "handheld",
            },
            {
                "type": "silhouete",
                "description": "Character backlit as silhouette",
                "technique": "silhouette_lighting",
            },
            {
                "type": "dutch_angle",
                "description": "Dutch angle for disorientation",
                "technique": "dutch_angle",
            },
            {
                "type": "whip_pan",
                "description": "Fast whip pan to reveal",
                "technique": "whip_pan",
            },
            {
                "type": "speed_ramp",
                "description": "Speed ramp for emphasis",
                "technique": "speed_ramp",
            },
            {
                "type": "orbital",
                "description": "Orbital shot around subject",
                "technique": "orbital",
            },
            {
                "type": "dolly_zoom",
                "description": "Dolly zoom (Vertigo effect)",
                "technique": "dolly_zoom",
            },
            {
                "type": "match_cut",
                "description": "Match cut connecting two elements",
                "technique": "match_cut",
            },
            {
                "type": "smash_cut",
                "description": "Sudden smash cut to contrasting image",
                "technique": "smash_cut",
            },
            {
                "type": "jump_cut",
                "description": "Jump cut showing time passage",
                "technique": "jump_cut",
            },
            {
                "type": "split_screen",
                "description": "Split screen showing parallel action",
                "technique": "split_screen",
            },
            {
                "type": "reflection_shot",
                "description": "Shot through reflection (mirror, water)",
                "technique": "reflection",
            },
            {
                "type": "through_object",
                "description": "Shot through object (glass, foliage)",
                "technique": "foreground",
            },
            {
                "type": "silhouete",
                "description": "Silhouette against bright background",
                "technique": "silhouette",
            },
            {
                "type": "light_leak",
                "description": "Light leak or lens flare effect",
                "technique": "light_leak",
            },
        ]

        # Audio Library (sound design elements) - ENHANCED WITH OASIZ PATTERNS
        self.audio = [
            {
                "type": "sub_bass_40hz",
                "description": "Sub-bass 40Hz pulse for hook impact",
                "frequency": 40,
                "use_case": "hook_impact",
            },
            {
                "type": "sub_bass_40hz_stinger",
                "description": "Sub-bass 40Hz stinger for cliffhanger impact",
                "frequency": 40,
                "pattern": "stinger",
                "use_case": "cliffhanger_impact",
            },
            {
                "type": "heartbeat_pause",
                "description": "Heartbeat then sudden silence",
                "pattern": "pause",
            },
            {
                "type": "paper_tear",
                "description": "Sound of paper tearing or document rustle",
                "fx": "paper",
            },
            {
                "type": "glass_shatter",
                "description": "Glass shattering or breaking",
                "fx": "glass",
            },
            {
                "type": "footsteps_gravel",
                "description": "Footsteps on gravel or loose surface",
                "fx": "footsteps",
            },
            {
                "type": "door_creak",
                "description": "Door creaking open or closing slowly",
                "fx": "door",
            },
            {
                "type": "clock_ticking",
                "description": "Loud clock ticking in silent room",
                "fx": "clock",
            },
            {
                "type": "breath_inhale",
                "description": "Sharp intake of breath",
                "fx": "breath",
            },
            {
                "type": "whisper_voice",
                "description": "Character whispering a critical line",
                "fx": "whisper",
            },
            {
                "type": "shout_echo",
                "description": "Shout that echoes in empty space",
                "fx": "shout",
            },
            {
                "type": "radio_tune",
                "description": "Radio tuning between stations",
                "fx": "radio",
            },
            {
                "type": "heartbeat_slow",
                "description": "Slow, ominous heartbeat",
                "pattern": "slow_beat",
            },
            {
                "type": "reverse_audio",
                "description": "Audio played slightly in reverse",
                "effect": "reverse",
            },
            {
                "type": "vinyl_scratch",
                "description": "Vinyl record scratch or skip",
                "fx": "scratch",
            },
            {
                "type": "tape_stop",
                "description": "Tape stopping abruptly",
                "fx": "tape_stop",
            },
            {
                "type": "crowd_murmur",
                "description": "Low crowd murmur or indistinct chatter",
                "fx": "crowd",
            },
            {
                "type": "single_violin",
                "description": "Single sustained violin note",
                "music": "violin",
            },
            {
                "type": "piano_chord",
                "description": "Single somber piano chord",
                "music": "piano",
            },
            {
                "type": "digital_glitch",
                "description": "Digital glitch or data corruption sound",
                "fx": "glitch",
            },
            {
                "type": "silence_drop",
                "description": "Sudden drop to silence before impact (Music Drop)",
                "pattern": "silence_drop",
                "use_case": "pre_revelation",
            },
            {
                "type": "bass_drop",
                "description": "Electronic bass drop",
                "music": "bass",
            },
            {
                "type": "orchestra_hit",
                "description": "Sudden orchestra hit",
                "music": "orchestra",
            },
            {
                "type": "heartbeat_fast",
                "description": "Rapid heartbeat indicating panic",
                "pattern": "fast_beat",
            },
            {
                "type": "sub_bass_40hz_hook",
                "description": "Sub-bass 40Hz pulse for 0-2s visual hook impact",
                "frequency": 40,
                "use_case": "hook_impact_0_2s",
            },
        ]

        # Script Line Templates (hook-specific lines that create intrigue)
        self.script_templates = [
            "¿Estás segura de que quieres saber la verdad?",
            "Esto no es lo que parece...",
            "La verdad duele más que la mentira.",
            "Nunca debiste haberme confiado esto.",
            "Lo que hiciste tiene consecuencias.",
            "Esto cambia todo lo que creías saber.",
            "No era él quien...",
            "Yo nunca fui quien creías que era.",
            "La respuesta estaba frente a ti todo este tiempo.",
            "No puedes deshacer lo que ya se hizo.",
            "Hay cosas que no se perdonan.",
            "Este secreto te destruirá a ti también.",
            "No hay vuelta atrás después de esto.",
            "El precio de la verdad es demasiado alto.",
            "Estás jugando un juego que no entiendes.",
            "Cada mentira necesita una verdad más grande para sostenerla.",
            "No soy el enemigo que crees que soy.",
            "Tu peor miedo ya está aquí.",
            "No hay héroes en esta historia, solo sobrevivientes.",
            "La línea entre el bien y el mal se acaba de borrar.",
        ]

        # Shuffle the lists to add randomness (seed based on session for consistency if needed)
        # Use episode_num or other context for seeding if available, otherwise use system randomness
        random.shuffle(self.mechanisms)
        random.shuffle(self.emotions)
        random.shuffle(self.visuals)
        random.shuffle(self.audio)
        random.shuffle(self.script_templates)

    def generate_hooks(
        self,
        episode_num: int,
        episode_blueprint: dict[str, Any],
        characters: list[dict[str, Any]],
        genome_context: dict[str, Any],
        viral_ruleset: list[str],
    ) -> dict[str, Any]:
        """
        Generate hooks for an episode based on the blueprint and context.
        Returns dict with top_5_hooks and all_candidates_count.
        Implements Hook Lab: 100-150 hypotheses with novelty checking.
        """
        logger.info(
            f"Generating hooks for episode {episode_num}, category: {episode_blueprint.get('hook_category')}"
        )

        # Get target hook category from blueprint
        target_category = episode_blueprint.get("hook_category", "betrayal")

        # We'll generate 150 hypotheses by combining:
        # - 30 mechanisms (5 per mechanism gives 150)
        # - For each mechanism, vary emotion, visual, audio, and script

        # Select 30 mechanisms (cycle if we don't have enough)
        mechanisms_to_use = []
        if len(self.mechanisms) >= 30:
            mechanisms_to_use = self.mechanisms[:30]
        else:
            # Repeat the mechanisms list to get 30
            repeats = (30 // len(self.mechanisms)) + 1
            mechanisms_to_use = (self.mechanisms * repeats)[:30]

        hypotheses = []

        # For each mechanism, create 5 hypotheses by varying other dimensions
        for i, mechanism in enumerate(mechanisms_to_use):
            base_index = i * 5
            for j in range(5):
                idx = base_index + j

                # Cycle through emotion, visual, audio, script lists
                emotion = (
                    self.emotions[idx % len(self.emotions)]
                    if self.emotions
                    else "neutral"
                )
                visual = self.visuals[idx % len(self.visuals)] if self.visuals else {}
                audio = self.audio[idx % len(self.audio)] if self.audio else {}
                script_template = (
                    self.script_templates[idx % len(self.script_templates)]
                    if self.script_templates
                    else ""
                )

                # Create hook hypothesis
                hook = {
                    "mechanism": mechanism,
                    "emotion": emotion,
                    "visual": visual,
                    "audio": audio,
                    "script_template": script_template,
                    "category": target_category,  # All hooks in this batch target the same category
                }
                hypotheses.append(hook)

        # Now we have 150 hypotheses. Score each one.
        scored_hooks = []
        for hook in hypotheses:
            # Calculate novelty score (0-100) based on mechanism usage in Creative Genome
            novelty_score = self._calculate_novelty_score(hook["mechanism"])

            # Score the hook on other factors: emotional impact, visual clarity, audio distinctiveness, script strength
            other_score = self._score_hook_hypothesis(
                hook, episode_blueprint, characters, viral_ruleset
            )

            # Combined weighted score: 40% novelty, 60% other factors
            weighted_score = (novelty_score * 0.4) + (other_score * 0.6)

            hook["novelty_score"] = novelty_score
            hook["other_score"] = other_score
            hook["weighted_score"] = weighted_score
            scored_hooks.append(hook)

        # Sort by weighted score descending
        scored_hooks.sort(key=lambda x: x["weighted_score"], reverse=True)

        # Select top 5 hooks
        top_5 = scored_hooks[:5]

        # Format top 5 hooks for output
        formatted_top_5 = []
        for i, hook in enumerate(top_5):
            # Build the visual_hook and audio_hook strings from the visual/audio dicts
            visual_hook_str = self._visual_to_string(hook["visual"])
            audio_hook_str = self._audio_to_string(hook["audio"])

            # Generate subversion angle and rationale
            subversion_angle = self._generate_subversion_angle(hook)
            rationale = self._generate_rationale(hook, episode_blueprint)

            formatted_top_5.append(
                {
                    "rank": i + 1,
                    "category": hook["category"],
                    "mechanism": hook["mechanism"],
                    "visual_hook": visual_hook_str,
                    "audio_hook": audio_hook_str,
                    "script_line": hook["script_template"],
                    "weighted_score": round(hook["weighted_score"], 1),
                    "novelty_score": round(hook["novelty_score"], 1),
                    "subversion_angle": subversion_angle,
                    "rationale": rationale,
                }
            )

        # Calculate mechanism coverage across all 150 hypotheses
        mechanism_coverage = {}
        for hook in hypotheses:
            mech = hook["mechanism"]
            mechanism_coverage[mech] = mechanism_coverage.get(mech, 0) + 1

        logger.info(f"Generated {len(hypotheses)} hook hypotheses, selected top 5")

# Record hook generation event in Knowledge Ledger
        try:
            knowledge_ledger.acquire_knowledge(
                character_id="hook_engine",
                knowledge_type="hook_generation",
                knowledge_state=KnowledgeState.KNOWS,
                source=KnowledgeSource.DIRECT,
                source_reference="hook_engine_algorithm",
                confidence=1.0,
                context={"episode_num": episode_num}
            )
        except Exception as e:
            logger.warning(f"Knowledge ledger error: {e}")
        # Add nodes for top hooks in Story Graph
        for hook in formatted_top_5:
            try:
                node_id = f"hook_{hook['rank']}_{episode_num}"
                story_graph_manager.add_node(
                    node_id=node_id,
                    node_type="hook",
                    timestamp="now",
                    description=f"Hook {hook['rank']} for episode {episode_num}",
                    metadata={"mechanism": hook['mechanism']}
                )
                story_graph_manager.add_edge(
                    source_node_id=f"episode_{episode_num}",
                    target_node_id=node_id,
                    relationship_type="contains_hook",
                    strength=1.0,
                    metadata={}
                )
            except Exception as e:
                logger.warning(f"StoryGraph update error: {e}")
        return {
            "top_5_hooks": formatted_top_5,
            "all_candidates_count": len(hypotheses),
            "mechanism_coverage": mechanism_coverage,
        }

    def _calculate_novelty_score(self, mechanism: str) -> float:
        """
        Calculate novelty score (0-100) for a mechanism based on Creative Genome usage.
        Higher score = more novel (less recently used).
        """
        if not self.creative_genome:
            # Fallback: return a moderate novelty score
            return 50.0

        try:
            # Check how recently this mechanism was used in the genome
            # We'll check the budget usage as a proxy for recent usage
            budget = self.creative_genome.check_budget(self.agent_name, genre="general")
            # In a real implementation, we'd check specific mechanism usage
            # For now, we'll use the overall budget availability as a proxy
            # Higher available budget = less recently used = higher novelty
            total_budget = 100  # 70+20+10
            used_budget = (
                (100 - budget["proven_available"])
                + (100 - budget["exploration_available"])
                + (100 - budget["big_bet_available"])
            )
            usage_ratio = used_budget / (total_budget * 3)  # Normalize to 0-1

            # Novelty is inverse of usage: 1 - usage_ratio
            novelty = max(0.0, min(1.0, 1.0 - usage_ratio)) * 100
            return novelty
        except Exception as e:
            logger.warning(f"Error calculating novelty score: {e}")
            return 50.0

    def _score_hook_hypothesis(
        self,
        hook: dict[str, Any],
        episode_blueprint: dict[str, Any],
        characters: list[dict[str, Any]],
        viral_ruleset: list[str],
    ) -> float:
        """
        Score a hook hypothesis on factors other than novelty:
        - Emotional impact (0-30)
        - Visual clarity (0-25)
        - Audio distinctiveness (0-20)
        - Script strength (0-25)
        Total: 0-100
        """
        score = 0.0

        # Emotional impact: does the emotion match the intended impact?
        emotion = hook.get("emotion", "")
        # Simple scoring: some emotions are more impactful for hooks
        high_impact_emotions = ["shock", "surprise", "betrayal", "anger", "fear"]
        medium_impact_emotions = ["sadness", "joy", "disgust", "trust", "anticipation"]
        if emotion in high_impact_emotions:
            score += 30.0
        elif emotion in medium_impact_emotions:
            score += 20.0
        else:
            score += 10.0

        # Visual clarity: does the visual technique suggest a clear, impactful image?
        visual = hook.get("visual", {})
        visual_desc = visual.get("description", "").lower()
        # Check for strong visual indicators
        strong_visual_indicators = [
            "extreme close-up",
            "close-up",
            "wide shot",
            "insert shot",
            "point of view",
            "silhouette",
            "dutch angle",
            "whip pan",
            "speed ramp",
            "orbital",
            "dolly zoom",
            "match cut",
            "smash cut",
            "jump cut",
            "split screen",
            "reflection",
        ]
        if any(indicator in visual_desc for indicator in strong_visual_indicators):
            score += 25.0
        else:
            score += 15.0  # baseline for having a visual

        # Audio distinctiveness: does the audio element create a memorable sound moment?
        audio = hook.get("audio", {})
        audio_desc = audio.get("description", "").lower()
        # Check for distinctive audio elements
        distinctive_audio = [
            "sub-bass",
            "heartbeat",
            "paper tear",
            "glass shatter",
            "footsteps",
            "door creak",
            "clock ticking",
            "breath",
            "whisper",
            "shout",
            "radio tune",
            "heartbeat slow",
            "reverse audio",
            "vinyl scratch",
            "tape stop",
            "crowd murmur",
            "single violin",
            "piano chord",
            "digital glitch",
            "silence drop",
            "bass drop",
            "orchestra hit",
            "heartbeat fast",
        ]
        if any(indicator in audio_desc for indicator in distinctive_audio):
            score += 20.0
        else:
            score += 10.0  # baseline for having audio

        # Script strength: does the script line create intrigue and hook the viewer?
        script = hook.get("script_template", "")
        # Check for hook-worthy elements in the script
        hook_indicators = [
            "¿",
            "?",
            "verdad",
            "mentira",
            "secreto",
            "consecuencias",
            "cambia",
            "nunca",
            "siempre",
            "nadie",
            "todo",
            "nada",
            "pero",
            "sin embargo",
            "aunque",
            "porque",
            "puesto que",
        ]
        script_lower = script.lower()
        indicator_count = sum(
            1 for indicator in hook_indicators if indicator in script_lower
        )
        # Normalize: 5+ indicators = strong, 3-4 = medium, 1-2 = weak
        if indicator_count >= 5:
            score += 25.0
        elif indicator_count >= 3:
            score += 15.0
        elif indicator_count >= 1:
            score += 5.0
        # else: 0

        return min(100.0, score)  # Cap at 100

    def _visual_to_string(self, visual: dict[str, Any]) -> str:
        """Convert visual dict to a descriptive string."""
        if not visual:
            return "Visual estándar"

        parts = []
        if visual.get("type"):
            parts.append(visual["type"])
        if visual.get("description"):
            parts.append(f"({visual['description']})")
        if visual.get("technique"):
            parts.append(f"técnica: {visual['technique']}")

        return " ".join(parts) if parts else "Visual no especificado"

    def _audio_to_string(self, audio: dict[str, Any]) -> str:
        """Convert audio dict to a descriptive string."""
        if not audio:
            return "Audio estándar"

        parts = []
        if audio.get("type"):
            parts.append(audio["type"])
        if audio.get("description"):
            parts.append(f"({audio['description']})")
        if audio.get("frequency"):
            parts.append(f"{audio['frequency']}Hz")
        if audio.get("fx"):
            parts.append(f"fx: {audio['fx']}")
        if audio.get("music"):
            parts.append(f"música: {audio['music']}")
        if audio.get("pattern"):
            parts.append(f"patrón: {audio['pattern']}")
        if audio.get("effect"):
            parts.append(f"efecto: {audio['effect']}")

        return " ".join(parts) if parts else "Audio no especificado"

    def _generate_subversion_angle(self, hook: dict[str, Any]) -> str:
        """Generate a subversion angle description for the hook."""
        mechanism = hook.get("mechanism", "").replace("_", " ")
        emotion = hook.get("emotion", "")

        # Simple subversion angles based on mechanism
        subversion_map = {
            "power_reversal": "El personaje aparentemente débil revela ser quien tiene el control total",
            "identity_flip": "La identidad que todos creían verdadera resulta ser una cuidadosa ficción",
            "loyalty_shift": "La lealtad aparente resulta ser una cuidadosa estrategia de información",
            "morality_inversion": "Lo que parece ser un acto de maldad es en realidad el único camino hacia la redención",
            "knowledge_reveal": "El conocimiento que todos buscaban estaba oculto a plena vista todo este tiempo",
            "emotional_journey": "La jornada emocional que todos esperaban resulta ser exactamente lo opuesto a lo que parecía",
            "social_status_shift": "El ascenso o descenso social resulta ser una ilusión cuidadosamente construida",
            "time_manipulation": "El control sobre el tiempo que creían tener resulta ser una percepción subjetiva",
            "truth_revelation": "La verdad que todos temían resulta ser exactamente lo que necesitaban escuchar",
            "betrayal_exposure": "La traición que todos vieron venir resulta ser una doble traición mucho más profunda",
            "innocence_proven": "La inocencia que todos daban por perdida resulta ser la evidencia más contundente",
            "guilty_realization": "La culpa que todos creían evidente resulta ser una compleja red de circunstancias",
            "ally_becomes_enemy": "El aliado de confianza resulta ser el arquitecto de su propia caída",
            "enemy_becomes_ally": "El enemigo jurado resulta ser el único capaz de salvarles de una amenaza mayor",
            "weak_to_strong": "La debilidad que todos percibían resulta ser la fuente de su mayor fortaleza",
            "strong_falls": "La fortaleza que todos admiraban resulta ser frágil como una casa de naipes",
            "smart_fool": "El personaje que todos consideran tonto resulta ser el más perspicaz de todos",
            "fool_outsmarts": "El supuesto ingenioso resulta ser superado por quien todos subestimaron",
            "love_to_hate": "El amor que todos creían inquebrantable resulta ser una peligrosa obsesión",
            "hate_to_love": "El odio que todos creían eterno resulta ser un malentendido que disuelve barreras",
            "trust_shattered": "La confianza que todos daban por sólida resulta ser frágil como cristal",
            "trust_earned": "La desconfianza que todos mostraban resulta ser el primer paso hacia una alianza inesperada",
            "secret_kept": "El secreto que todos creían seguro resulta ser de conocimiento común para unos pocos seleccionados",
            "secret_revealed": "La revelación que todos temían resulta ser exactamente lo que necesitaban para avanzar",
            "promise_broken": "La promesa que todos creían sagrada resulta ser el catalizador de un cambio necesario",
            "promise_kept": "La promesa que todos daban por perdida resulta ser el vínculo que los mantiene unidos",
            "sacrifice_made": "El sacrifice que todos temían resulta ser exactamente lo que necesitaban para seguir adelante",
            "sacrifice_refused": "La negativa a sacrificar lo que todos creían esencial resulta ser el acto más valiente",
            "justice_served": "La justicia que todos creían imposible resulta ser exactamente lo que el orden necesario",
            "justice_denied": "La injusticia que todos aceptaban como inevitable resulta ser la chispa de la revolución",
            "freedom_gained": "La libertad que todos creían perdida resulta ser exactamente lo que necesitaban para ser quienes son",
            "freedom_lost": "La seguridad que todos creían garantizada resulta ser la jaula más dorada de todas",
            "knowledge_gained": "El conocimiento que todos temían adquirir resulta ser exactamente lo que necesitaban para sobrevivir",
            "knowledge_lost": "La pérdida de conocimiento que todos creían catastrófica resulta ser un alivio inesperado",
            "hope_found": "La esperanza que todos creían perdida resulta ser exactamente lo que necesitaban para seguir adelante",
            "hope_lost": "La certeza que todos creían inquebrantable resulta ser el terreno fértil para un nuevo comienzo",
        }

        # Return the subversion angle if we have it, otherwise generate a generic one
        return subversion_map.get(
            mechanism,
            f"Un giro inesperado revela que {mechanism} resulta ser exactamente lo opuesto a lo que parecía",
        )

    def _generate_rationale(
        self, hook: dict[str, Any], episode_blueprint: dict[str, Any]
    ) -> str:
        """Generate a rationale for why this hook works."""
        mechanism = hook.get("mechanism", "").replace("_", " ")
        emotion = hook.get("emotion", "")
        visual_desc = hook.get("visual", {}).get("description", "visual impactante")

        # Simple rationale
        return f"Combina el mecanismo de {mechanism} con una emoción de {emotion} y un {visual_desc} para crear un momento de alto impacto que captura la atención inmediatamente y establece el conflicto central del episodio."

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute method for flat agent interface.
        Delegates to the real hook generation logic with enhanced zero-dialogue visual-first requirements.
        """
        try:
            logger.info(
                f"Hook Engine agent processing episode {context.get('episode_num', 'unknown')}"
            )

            # Extract context
            episode_num = context.get("episode_num", 1)
            episode_blueprint = context.get("episode_blueprint", {})
            characters = context.get("characters", [])
            genome_context = context.get("genome_context", {})
            viral_ruleset = context.get("viral_ruleset", [])

            # Generate hooks using the real agent's logic
            result = self.generate_hooks(
                episode_num,
                episode_blueprint,
                characters,
                genome_context,
                viral_ruleset,
            )

            # Enhance the result with OASIZ-inspired zero-dialogue visual-first hook requirement
            # Ensure at least one of the top 5 hooks meets the 0-2s visual-first criteria
            enhanced_result = self._enforce_zero_dialogue_visual_first(result)

            return enhanced_result
        except Exception as e:
            error_id = self.error_memory.register_error(
                agent=self.agent_name,
                category="PROMPT",
                description=f"Hook Engine execution failed: {e!s}",
                fix="Review hook engine dependencies and input data",
                severity="MEDIUM",
                root_cause="Execution exception during hook generation",
            )
            logger.error(
                f"Hook Engine failed in {self.agent_name}: {e!s} | Error registered: {error_id}"
            )
            raise

    def _enforce_zero_dialogue_visual_first(
        self, result: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Enhance hook generation results to ensure compliance with OASIZ-inspired
        zero-dialogue visual-first hook requirements (0-2s ECU + 40Hz sub-bass).
        """
        top_5_hooks = result.get("top_5_hooks", [])
        if not top_5_hooks:
            return result

        # Check if any hook already meets the criteria
        has_visual_first_hook = False
        for hook in top_5_hooks:
            visual_hook = hook.get("visual_hook", "").lower()
            audio_hook = hook.get("audio_hook", "").lower()
            script_line = hook.get("script_line", "")

            # Check for zero dialogue (empty or minimal script line) and ECU visual
            is_visual_first = (
                "ecu" in visual_hook
                and (
                    "macro" in visual_hook
                    or "ojo" in visual_hook
                    or "extreme close-up" in visual_hook
                )
                and (len(script_line.strip()) == 0 or script_line.strip() == "")
            )

            # Check for 40Hz sub-bass in audio
            has_40hz_subbass = "40hz" in audio_hook or "sub-bass 40hz" in audio_hook

            if is_visual_first and has_40hz_subbass:
                has_visual_first_hook = True
                break

        # If no hook meets the criteria, enhance the top hook to meet them
        if not has_visual_first_hook and top_5_hooks:
            # Enhance the top hook (rank 1) to meet zero-dialogue visual-first requirements
            top_hook = top_5_hooks[0]

            # Ensure it has ECU visual for 0-2s hook
            if "ecu" not in top_hook.get("visual_hook", "").lower():
                top_hook["visual_hook"] = (
                    "ECU Extreme close-up on eyes/hands/object - MACRO SHOT FOR 0-2s HOOK (técnica: push_in)"
                )
                top_hook["mechanism"] = (
                    "knowledge_reveal"  # Good mechanism for visual hook
                )

            # Ensure it has 40Hz sub-bass audio
            if "40hz" not in top_hook.get("audio_hook", "").lower():
                top_hook["audio_hook"] = (
                    "Sub-bass 40Hz pulse for hook impact (frequency: 40Hz, use_case: hook_impact)"
                )

            # Ensure zero dialogue in script line
            top_hook["script_line"] = ""  # Zero dialogue for pure visual hook

            # Update the rationale to reflect the visual-first nature
            top_hook["rationale"] = (
                "Combina el mecanismo de knowledge_reveal con un impacto visual extremo (ECU) y audio de sub-bass 40Hz para crear un momento de alto impacto que captura la atención inmediatamente sin diálogo."
            )

            # Update mechanism coverage if needed
            # (We don't have easy access to mechanism_coverage here, but it's less critical)

        return result
