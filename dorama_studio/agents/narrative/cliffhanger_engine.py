"""
Cliffhanger Engine Agent - Implements anti-repetition and causal cliffhanger logic.
Generates cliffhangers that are causally connected to the episode narrative and avoid repetition.
"""
from __future__ import annotations

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)


class CliffhangerEngineAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Cliffhanger Engine Agent that creates causally-connected cliffhangers
    with anti-repetition mechanisms and question pressure optimization.
    """

    def __init__(self):
        super().__init__("CliffhangerEngineAgent")
        # Cliffhanger types from forensic analysis
        self.cliffhanger_types = [
            "revelation",
            "betrayal",
            "threat",
            "interruption",
            "discovery",
            "emotional_reversal",
            "identity_reveal",
            "secret_revealed",
            "new_antagonist",
            "impossible_choice",
            "unanswered_question",
            "unexpected_arrival",
            "status_reversal",
            "relationship_reversal"
        ]

        # Anti-repetition tracking (in production would be persistent)
        self.last_3_types: list[str] = []
        self.last_10_structural_signatures: list[str] = []
        self.question_history: list[str] = []
        self.payoff_history: list[str] = []

        # Scoring weights from forensic analysis
        self.scoring_weights = {
            "causalidad": 0.25,
            "novedad": 0.20,
            "emotional_shift": 0.15,
            "question_pressure": 0.20,
            "continuity": 0.10,
            "next_episode_pull": 0.10
        }

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, ctx: dict[str, Any]) -> dict[str, Any]:
        """
        Process the context to generate an optimal cliffhanger for the episode.

        Expects ctx to contain:
        - episode_blueprint: EpisodeBlueprint from EpisodeArchitectAgent
        - episode_events: list of events that happened in the episode
        - character_arcs: current state of character arcs
        - season_memory: ongoing season mysteries and questions
        - previous_cliffhangers: list of previous cliffhangers for anti-repetition

        Returns:
        - cliffhanger_spec: detailed cliffhanger specification
        - cliffhanger_text: the actual cliffhanger line
        - score: quality score (0-100)
        - reasoning: explanation of why this cliffhanger works
        """
        episode_blueprint = ctx.get("episode_blueprint", {})
        episode_events = ctx.get("episode_events", [])
        character_arcs = ctx.get("character_arcs", {})
        season_memory = ctx.get("season_memory", {})
        previous_cliffhangers = ctx.get("previous_cliffhangers", [])
        episode_num = ctx.get("episode_num", 1)

        # Update anti-repetition history from previous cliffhangers
        self._update_anti_repetition_history(previous_cliffhangers)

        # Generate cliffhanger candidates based on episode events and blueprint
        candidates = self._generate_cliffhanger_candidates(
            episode_blueprint, episode_events, character_arcs, season_memory
        )

        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            score, breakdown = self._score_cliffhanger_candidate(
                candidate, episode_blueprint, episode_events, character_arcs, season_memory
            )
            scored_candidates.append({
                "candidate": candidate,
                "score": score,
                "breakdown": breakdown
            })

        # Select best candidate
        if not scored_candidates:
            # Fallback to default cliffhanger
            best = self._generate_default_cliffhanger(episode_num)
            score = 50.0
            breakdown = {"fallback": True}
        else:
            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            best = scored_candidates[0]
            score = best["score"]
            breakdown = best["breakdown"]

        # Format output
        cliffhanger_spec = best["candidate"]
        cliffhanger_text = cliffhanger_spec.get("text", "")

        # Update history with selected cliffhanger
        self._update_anti_repetition_history([cliffhanger_spec])

        return {
            "cliffhanger_spec": cliffhanger_spec,
            "cliffhanger_text": cliffhanger_text,
            "score": round(score, 1),
            "breakdown": breakdown,
            "episode_num": episode_num,
            "reasoning": self._generate_reasoning(best["candidate"], breakdown),
            "anti_repetition_state": {
                "last_3_types": self.last_3_types.copy(),
                "question_history_len": len(self.question_history)
            }
        }

    def _generate_cliffhanger_candidates(
        self,
        blueprint: dict[str, Any],
        events: list[dict],
        character_arcs: dict,
        season_memory: dict
    ) -> list[dict[str, Any]]:
        """Generate cliffhanger candidates based on episode content."""
        candidates = []

        # Extract key elements from episode
        core_conflict = blueprint.get("core_conflict", "")
        twist = blueprint.get("twist", "")
        unresolved_questions = season_memory.get("unanswered_questions", [])
        character_stakes = self._extract_character_stakes(character_arcs, events)

        # Candidate 1: Revelation based on twist
        if twist and "revelation" not in self.last_3_types:
            candidates.append({
                "type": "revelation",
                "text": f"La verdad sobre {twist.split('(')[0] if '(' in twist else twist} cambia todo lo que creíamos saber",
                "visual_hook": "ECU on character realizing the truth",
                "leads_to_next": f"How will the characters react to this revelation about {core_conflict}?",
                "causal_elements": [twist, core_conflict],
                "emotional_shift": "shock to determination"
            })

        # Candidate 2: Betrayal from character arcs
        betrayal_potential = self._find_betrayal_potential(character_arcs, events)
        if betrayal_potential and "betrayal" not in self.last_3_types:
            candidates.append({
                "type": "betrayal",
                "text": f"El último aliado de {betrayal_potential} revela que estuvo trabajando para el enemigo todo este tiempo",
                "visual_hook": "Split screen: ally meeting with enemy",
                "leads_to_next": f"How will {betrayal_potential} survive this betrayal?",
                "causal_elements": [betrayal_potential, "trust"],
                "emotional_shift": "trust to devastation"
            })

        # Candidate 3: Threat escalation
        threat_elements = self._extract_threat_elements(events, core_conflict)
        if threat_elements and "threat" not in self.last_3_types:
            candidates.append({
                "type": "threat",
                "text": f"El verdadero peligro no era lo que pensábamos, sino {threat_elements}",
                "visual_hook": "ECU on ticking clock or approaching danger",
                "leads_to_next": "How will they stop this new threat before it's too late?",
                "causal_elements": threat_elements,
                "emotional_shift": "relief to renewed fear"
            })

        # Candidate 4: Unanswered question (from season memory)
        if unresolved_questions and "unanswered_question" not in self.last_3_types:
            question = unresolved_questions[0] if isinstance(unresolved_questions, list) else str(unresolved_questions)
            candidates.append({
                "type": "unanswered_question",
                "text": f"Pero la pregunta más importante sigue sin respuesta: {question}",
                "visual_hook": "Text on screen: the question, character looking troubled",
                "leads_to_next": question,
                "causal_elements": [question],
                "emotional_shift": "frustration to determination"
            })

        # Candidate 5: Identity reveal
        identity_reveal = self._find_identity_reveal_opportunity(character_arcs, events)
        if identity_reveal and "identity_reveal" not in self.last_3_types:
            candidates.append({
                "type": "identity_reveal",
                "text": f"La persona que todos creían que era {identity_reveal['false_identity']} en realidad es {identity_reveal['true_identity']}",
                "visual_hook": "ECU on revealing document or photo",
                "leads_to_next": f"How will this change affect {identity_reveal['true_identity']}'s relationships?",
                "causal_elements": [identity_reveal['false_identity'], identity_reveal['true_identity']],
                "emotional_shift": "confusion to shock"
            })

        # Candidate 6: Impossible choice
        choice_options = self._extract_impossible_choice(events, character_arcs)
        if choice_options and "impossible_choice" not in self.last_3_types:
            candidates.append({
                "type": "impossible_choice",
                "text": f"¿Salvar a {choice_options['person_a']} o detener el plan que destruiría a {choice_options['person_b']}?",
                "visual_hook": "Split screen: two simultaneous crises",
                "leads_to_next": "Which choice will they make, and what will be the consequences?",
                "causal_elements": [choice_options['person_a'], choice_options['person_b']],
                "emotional_shift": "hope to agonizing decision"
            })

        # If no specific candidates, create general ones based on episode type
        if not candidates:
            candidates = self._generate_generic_cliffhangers(blueprint, events)

        return candidates

    def _find_betrayal_potential(self, character_arcs: dict, events: list[dict]) -> str:
        """Find potential betrayal based on character relationships."""
        # Look for close alliances that could be broken
        alliances = []
        for event in events:
            if event.get("type") == "alliance_formed" or event.get("type") == "trust_built":
                chars = event.get("characters", [])
                if len(chars) >= 2:
                    alliances.extend(chars)

        # Return a character that has built trust (could betray)
        if alliances:
            # Simple heuristic: return most frequent character in alliances
            from collections import Counter
            most_common = Counter(alliances).most_common(1)
            if most_common:
                return most_common[0][0]
        return ""

    def _extract_threat_elements(self, events: list[dict], core_conflict: str) -> str:
        """Extract threat elements from events and core conflict."""
        threats = []
        for event in events:
            if event.get("type") in ["threat_revealed", "danger_approaching", "villain_plan"]:
                threat_desc = event.get("description", "")
                if threat_desc:
                    threats.append(threat_desc)

        # Also look for threats in core conflict
        if "amenaza" in core_conflict.lower() or "peligro" in core_conflict.lower():
            threats.append(core_conflict)

        return "; ".join(threats) if threats else "una consecuencia inesperada de sus acciones"

    def _find_identity_reveal_opportunity(self, character_arcs: dict, events: list[dict]) -> dict[str, str]:
        """Find opportunity for identity reveal."""
        # Look for characters with hidden identities or secrets
        secrets_revealed = []
        false_identities = []

        for event in events:
            if event.get("type") == "secret_kept" or event.get("type") == "hidden_identity":
                char = event.get("character", "")
                if char:
                    false_identities.append(char)
            elif event.get("type") == "secret_revealed" or event.get("type") == "identity_exposed":
                char = event.get("character", "")
                if char:
                    secrets_revealed.append(char)

        # If we have a secret kept but not revealed, that's our opportunity
        for char in false_identities:
            if char not in secrets_revealed:
                # Find what the true identity might be (simplified)
                return {
                    "false_identity": char,
                    "true_identity": f"el verdadero {char.split()[-1] if ' ' in char else 'agente encubierto'}"
                }
        return {}

    def _extract_impossible_choice(self, events: list[dict], character_arcs: dict) -> dict[str, str]:
        """Extract impossible choice scenario from events."""
        # Look for conflicting goals or saved vs greater good scenarios
        saved_characters = []
        threatened_groups = []

        for event in events:
            if event.get("type") == "character_saved":
                saved_characters.extend(event.get("characters", []))
            elif event.get("type") == "group_threatened" or event.get("type") == "civilian_danger":
                threatened_groups.append(event.get("description", "innocentes"))

        if saved_characters and threatened_groups:
            return {
                "person_a": saved_characters[0] if saved_characters else "un ser querido",
                "person_b": threatened_groups[0] if threatened_groups else "muchos inocentes"
            }
        return {}

    def _extract_character_stakes(self, character_arcs: dict, events: list[dict]) -> list[str]:
        """Extract what characters have at stake."""
        stakes = []
        for char_id, arc in character_arcs.items():
            if arc.get("goal"):
                stakes.append(f"{arc.get('name', char_id)} quiere {arc['goal']}")
            if arc.get("fear"):
                stakes.append(f"{arc.get('name', char_id)} teme perder {arc['fear']}")
        return stakes

    def _generate_generic_cliffhangers(self, blueprint: dict[str, Any], events: list[dict]) -> list[dict[str, Any]]:
        """Generate generic cliffhangers when specific opportunities aren't found."""
        hook_category = blueprint.get("hook_category", "mystery")
        core_conflict = blueprint.get("core_conflict", "el conflicto central")

        # Map hook category to likely cliffhanger types
        hook_to_cliff = {
            "betrayal": ["revelation", "betrayal", "identity_reveal"],
            "mystery": ["unanswered_question", "revelation", "secret_revealed"],
            "threat": ["threat", "new_antagonist", "impossible_choice"],
            "revelation": ["betrayal", "threat", "emotional_reversal"],
            "identity_shock": ["identity_reveal", "secret_revealed", "new_antagonist"],
            "visual_shock": ["discovery", "unexpected_arrival", "status_reversal"],
            "moral_dilemma": ["impossible_choice", "relationship_reversal", "emotional_reversal"],
            "power_reveal": ["status_reversal", "new_antagonist", "betrayal"]
        }

        likely_types = hook_to_cliff.get(hook_category, ["revelation", "betrayal", "threat"])
        candidates = []

        for cliff_type in likely_types:
            if cliff_type not in self.last_3_types:  # Avoid immediate repetition
                candidates.append({
                    "type": cliff_type,
                    "text": f"El final del episodio revela una nueva capa de {core_conflict.lower()} que nadie esperaba",
                    "visual_hook": "ECU on shocked face + text hinting at revelation",
                    "leads_to_next": f"How will this new information change the approach to {core_conflict}?",
                    "causal_elements": [core_conflict],
                    "emotional_shift": "surprise to renewed purpose"
                })

        return candidates[:3]  # Limit candidates

    def _score_cliffhanger_candidate(
        self,
        candidate: dict[str, Any],
        blueprint: dict[str, Any],
        events: list[dict],
        character_arcs: dict,
        season_memory: dict
    ) -> tuple[float, dict[str, float]]:
        """Score a cliffhanger candidate based on forensic analysis criteria."""
        breakdown = {}

        # 1. Causalidad (25%) - How causally connected to episode events
        causal_score = self._score_causality(candidate, events, blueprint)
        breakdown["causalidad"] = causal_score * 100

        # 2. Novedad (20%) - Avoids repetition using anti-repetition history
        novelty_score = self._score_novelty(candidate)
        breakdown["novedad"] = novelty_score * 100

        # 3. Emotional Shift (15%) - Creates strong emotional shift
        emotional_score = self._score_emotional_shift(candidate, character_arcs)
        breakdown["emotional_shift"] = emotional_score * 100

        # 4. Question Pressure (20%) - Maintains or increases question pressure
        question_score = self._score_question_pressure(candidate, season_memory)
        breakdown["question_pressure"] = question_score * 100

        # 5. Continuity (10%) - Doesn't violate established continuity
        continuity_score = self._score_continuity(candidate, character_arcs, season_memory)
        breakdown["continuity"] = continuity_score * 100

        # 6. Next Episode Pull (10%) - Creates strong pull to next episode
        pull_score = self._score_next_episode_pull(candidate, blueprint)
        breakdown["next_episode_pull"] = pull_score * 100

        # Calculate weighted score
        total_score = (
            breakdown["causalidad"] * self.scoring_weights["causalidad"] +
            breakdown["novedad"] * self.scoring_weights["novedad"] +
            breakdown["emotional_shift"] * self.scoring_weights["emotional_shift"] +
            breakdown["question_pressure"] * self.scoring_weights["question_pressure"] +
            breakdown["continuity"] * self.scoring_weights["continuity"] +
            breakdown["next_episode_pull"] * self.scoring_weights["next_episode_pull"]
        )

        return total_score, breakdown

    def _score_causality(self, candidate: dict[str, Any], events: list[dict], blueprint: dict[str, Any]) -> float:
        """Score how causally connected the cliffhanger is to episode events."""
        causal_elements = candidate.get("causal_elements", [])
        if not causal_elements:
            return 0.3  # Low score for non-causal

        # Check if elements appear in episode events or blueprint
        episode_text = " ".join([
            str(event.get("description", "")) for event in events
        ] + [
            blueprint.get("core_conflict", ""),
            blueprint.get("twist", ""),
            blueprint.get("cliffhanger", "")
        ]).lower()

        matches = 0
        for element in causal_elements:
            if str(element).lower() in episode_text:
                matches += 1

        # Score based on proportion of causal elements found
        if len(causal_elements) == 0:
            return 0.5
        return min(1.0, matches / len(causal_elements))

    def _score_novelty(self, candidate: dict[str, Any]) -> float:
        """Score novelty based on anti-repetition history."""
        cliff_type = candidate.get("type", "")

        # Check against last 3 types
        if cliff_type in self.last_3_types:
            return 0.2  # Very low score for immediate repetition

        # Check against last 10 structural signatures (simplified)
        # In production, this would be more sophisticated signature matching
        signature = f"{cliff_type}_{hash(str(candidate.get('text', '')))}"
        if signature in self.last_10_structural_signatures:
            return 0.4  # Low score for recent similar structure

        # Good novelty
        return 0.9

    def _score_emotional_shift(self, candidate: dict[str, Any], character_arcs: dict) -> float:
        """Score the emotional shift created by the cliffhanger."""
        emotional_shift = candidate.get("emotional_shift", "")
        if not emotional_shift:
            return 0.4

        # Look for strong emotional transitions
        strong_shifts = [
            "trust to devastation",
            "joy to fear",
            "hope to despair",
            "relief to renewed fear",
            "confusion to shock",
            "satisfaction to betrayal"
        ]

        shift_lower = emotional_shift.lower()
        for strong_shift in strong_shifts:
            if strong_shift in shift_lower:
                return 0.9

        # Moderate shifts
        moderate_shifts = [
            "surprise to determination",
            "frustration to determination",
            "doubt to resolve",
            "curiosity to urgency"
        ]

        for moderate_shift in moderate_shifts:
            if moderate_shift in shift_lower:
                return 0.7

        # Weak shift or unknown
        return 0.5

    def _score_question_pressure(self, candidate: dict[str, Any], season_memory: dict) -> float:
        """Score how well the cliffhanger maintains or increases question pressure."""
        leads_to_next = candidate.get("leads_to_next", "")
        if not leads_to_next:
            return 0.3

        # Check if it creates a question or implies one
        question_indicators = ["?", "cómo", "qué", "quién", "cuándo", "dónde", "por qué", "cuál"]
        leads_lower = leads_to_next.lower()

        question_score = 0.0
        for indicator in question_indicators:
            if indicator in leads_lower:
                question_score += 0.2

        # Bonus if it references existing season mysteries
        season_questions = season_memory.get("unanswered_questions", [])
        if isinstance(season_questions, list):
            for sq in season_questions:
                if str(sq).lower() in leads_lower:
                    question_score += 0.3
                    break
        elif isinstance(season_questions, str) and season_questions.lower() in leads_lower:
            question_score += 0.3

        return min(1.0, question_score)

    def _score_continuity(self, candidate: dict[str, Any], character_arcs: dict, season_memory: dict) -> float:
        """Score whether the cliffhanger violates continuity."""
        # In production, this would check against established facts, character abilities, etc.
        # For now, basic check: doesn't contradict known character traits

        text = candidate.get("text", "").lower()

        # Check for impossible actions based on character arcs (simplified)
        continuity_violations = [
            "suddenly gains powers",  # unless established
            "forgets everything",      # unless amnesia plot
            "completely changes personality without reason"
        ]

        violations = 0
        for violation in continuity_violations:
            if violation in text:
                violations += 1

        # Also check if it resolves season mysteries too early (should be saved for later)
        # This is simplified - in production would be more sophisticated
        if len(season_memory.get("major_reveals_planned", [])) > 0:
            # If cliffhanger seems to resolve a major mystery too early
            reveal_words = ["revelation", "secret revealed", "truth about"]
            if any(word in text for word in reveal_words):
                # Penalize if it's too early in season (would need episode num check)
                pass  # Simplified for now

        if violations == 0:
            return 0.9
        elif violations == 1:
            return 0.6
        else:
            return 0.3

    def _score_next_episode_pull(self, candidate: dict[str, Any], blueprint: dict[str, Any]) -> float:
        """Score how strongly the cliffhanger pulls viewers to the next episode."""
        leads_to_next = candidate.get("leads_to_next", "")
        if not leads_to_next:
            return 0.3

        # Strong pull elements
        strong_pull_indicators = [
            "¿cómo",
            "qué pasará",
            "quién",
            "cuándo",
            "antes de que sea demasiado tarde",
            "última oportunidad",
            "decisión imposible",
            "consecuencias graves"
        ]

        leads_lower = leads_to_next.lower()
        pull_score = 0.0
        for indicator in strong_pull_indicators:
            if indicator in leads_lower:
                pull_score += 0.2

        # Bonus if it directly relates to next episode's blueprint (if available)
        # This would be enhanced in production with actual next episode data

        return min(1.0, pull_score)

    def _generate_default_cliffhanger(self, episode_num: int) -> dict[str, Any]:
        """Generate a default cliffhanger when no better candidates are found."""
        cliff_types_available = [ct for ct in self.cliffhanger_types if ct not in self.last_3_types]
        if not cliff_types_available:
            cliff_types_available = self.cliffhanger_types  # Reset if all used recently

        import random
        selected_type = random.choice(cliff_types_available)

        default_texts = {
            "revelation": "Una revelación inesperada cambia todo lo que creíamos saber sobre el caso",
            "betrayal": "El aliado más confiable revela su verdadera lealtad",
            "threat": "Un nuevo peligro emerge, más grande que cualquier cosa que hayan enfrentado",
            "interruption": "Justo cuando creían tener la situación bajo control, todo se interrumpe",
            "discovery": "Encuentran algo que no debería existir, y cambia todo",
            "emotional_reversal": "Lo que parecía victoria sabe a derrota, y viceversa",
            "identity_reveal": "La verdadera identidad de un personaje clave se revela finalmente",
            "secret_revealed": "Un secreto que creían enterrado sale a la luz",
            "new_antagonist": "Aparece un nuevo antagonista cuyos motivos son aún más oscuros",
            "impossible_choice": "Deben elegir entre dos opciones, ambas inaceptables",
            "unanswered_question": "Pero la pregunta más importante sigue sin respuesta",
            "unexpected_arrival": "Alguien que creían muerto o perdido regresa inesperadamente",
            "status_reversal": "El poderoso se vuelve débil, y el débil encuentra inesperada fuerza",
            "relationship_reversal": "Los aliados se vuelven enemigos, y los enemigos encuentran común ground"
        }

        text = default_texts.get(selected_type, "Un giro inesperado deja el futuro incierto")

        return {
            "type": selected_type,
            "text": text,
            "visual_hook": "ECU on shocked character + mysterious text on screen",
            "leads_to_next": "¿Cómo afectará esto a todo lo que han construido hasta ahora?",
            "causal_elements": ["episodio actual"],
            "emotional_shift": "confusion to determination"
        }

    def _update_anti_repetition_history(self, cliffhangers: list[dict[str, Any]]) -> None:
        """Update anti-repetition history with new cliffhangers."""
        for cliff in cliffhangers:
            cliff_type = cliff.get("type", "")
            if cliff_type and cliff_type not in self.last_3_types:
                self.last_3_types.append(cliff_type)
                # Keep only last 3
                if len(self.last_3_types) > 3:
                    self.last_3_types.pop(0)

            # Add structural signature (simplified)
            signature = f"{cliff_type}_{hash(str(cliff.get('text', '')))}"
            if signature not in self.last_10_structural_signatures:
                self.last_10_structural_signatures.append(signature)
                # Keep only last 10
                if len(self.last_10_structural_signatures) > 10:
                    self.last_10_structural_signatures.pop(0)

    def _generate_reasoning(self, candidate: dict[str, Any], breakdown: dict[str, float]) -> str:
        """Generate human-readable reasoning for the cliffhanger selection."""
        cliff_type = candidate.get("type", "unknown")
        text = candidate.get("text", "")

        reasoning_parts = [
            f"Selected {cliff_type} cliffhanger: '{text}'",
            "",
            "Scoring breakdown:"
        ]

        for criterion, score in breakdown.items():
            weight = self.scoring_weights.get(criterion, 0)
            weighted_contribution = score * weight
            reasoning_parts.append(
                f"  {criterion}: {score:.1f} (weight: {weight:.0%}) → contributes {weighted_contribution:.1f}"
            )

        reasoning_parts.extend([
            "",
            f"Total score: {sum(breakdown[c] * self.scoring_weights[c] for c in breakdown):.1f}/100",
            "",
            "This cliffhanger was chosen because it:"
        ])

        # Add explanations based on high scores
        if breakdown.get("causalidad", 0) > 0.7:
            reasoning_parts.append("  - Tiene fuertes conexiones causales con los eventos del episodio")
        if breakdown.get("novedad", 0) > 0.7:
            reasoning_parts.append("  - Evita la repetición reciente y mantiene la frescura narrativa")
        if breakdown.get("emotional_shift", 0) > 0.7:
            reasoning_parts.append("  - Crea un cambio emocional significativo que impactará al Zuschauer")
        if breakdown.get("question_pressure", 0) > 0.7:
            reasoning_parts.append("  - Mantiene o aumenta la presión de preguntas para el próximo episodio")
        if breakdown.get("continuity", 0) > 0.7:
            reasoning_parts.append("  - Respeta la continuidad establecida y los arcos de personaje")
        if breakdown.get("next_episode_pull", 0) > 0.7:
            reasoning_parts.append("  - Genera un fuerte gancho que impulsa a ver el próximo episodio")

        return "\n".join(reasoning_parts)


# Alias for backward compatibility
CliffhangerEngine = CliffhangerEngineAgent
