"""
Episode Scorer - Rates episode quality based on the 100-point system from quality.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass

from dorama_studio.core.master_writer import MasterScript


@dataclass
class EpisodeScoreDetails:
    """Detailed breakdown of episode scores."""

    hook: int = 0  # 0-20
    historia: int = 0  # 0-15
    emocion: int = 0  # 0-15
    retencion: int = 0  # 0-15
    personajes: int = 0  # 0-10
    visual: int = 0  # 0-10
    audio: int = 0  # 0-5
    cliffhanger: int = 0  # 0-5
    cta: int = 0  # 0-5
    total: int = 0  # 0-100

    def __post_init__(self):
        self.total = (
            self.hook
            + self.historia
            + self.emocion
            + self.retencion
            + self.personajes
            + self.visual
            + self.audio
            + self.cliffhanger
            + self.cta
        )


class EpisodeScorer:
    """
    Scores episodes based on the 100-point quality system.
    Thresholds:
    - 85+: Publishable
    - 75-84: Needs rewrite
    - <75: Needs human review/rework
    """

    def __init__(self):
        # Weights from quality.yaml
        self.weights = {
            "hook": 20,
            "historia": 15,
            "emocion": 15,
            "retencion": 15,
            "personajes": 10,
            "visual": 10,
            "audio": 5,
            "cliffhanger": 5,
            "cta": 5,
        }

        # Thresholds
        self.publish_minimum = 85
        self.rewrite_trigger = 75
        self.human_review_threshold = 70

    def score_episode(self, script: MasterScript) -> EpisodeScoreDetails:
        """
        Score a complete episode script.
        """
        details = EpisodeScoreDetails()

        # Hook score (0-20)
        details.hook = self._score_hook(script)

        # Historia score (0-15) - plot, structure, pacing
        details.historia = self._score_historia(script)

        # Emocion score (0-15) - emotional impact, authenticity
        details.emocion = self._score_emocion(script)

        # Retencion score (0-15) - ability to keep viewer engaged
        details.retencion = self._score_retencion(script)

        # Personajes score (0-10) - character depth, consistency, chemistry
        details.personajes = self._score_personajes(script)

        # Visual score (0-10) - composition, lighting, consistency
        details.visual = self._score_visual(script)

        # Audio score (0-5) - dialogue clarity, music fit, SFX quality
        details.audio = self._score_audio(script)

        # Cliffhanger score (0-5) - urgency, curiosity, specificity
        details.cliffhanger = self._score_cliffhanger(script)

        # CTA score (0-5) - narrative integration, clarity, urgency
        details.cta = self._score_cta(script)

        return details

    def _score_hook(self, script: MasterScript) -> int:
        """Score the hook (first 0-10s or first beat)."""
        if not script.beats:
            return 0

        first_beat = script.beats[0]
        score = 0

        # Check if hook is explosive (high tension, hyper pacing)
        if first_beat.tension >= 8 and first_beat.pacing == "hyper":
            score += 8
        elif first_beat.tension >= 6:
            score += 5
        else:
            score += 2

        # Check for strong visual hook in action
        action_lower = first_beat.action.lower()
        hook_indicators = [
            "encuentra",
            "descubre",
            "recibe",
            "ve",
            "oye",
            "siente",
            "llega",
            "ve",
            "salta",
            "corre",
            "disparo",
            "cae",
            "explota",
        ]
        if any(indicator in action_lower for indicator in hook_indicators):
            score += 4
        else:
            score += 1

        # Check dialogue for question or shock
        dialogue_lower = script.beats[0].dialogue.lower()
        question_indicators = [
            "¿",
            "?",
            "qué",
            " quién",
            "cómo",
            "cuándo",
            "dónde",
            "por qué",
        ]
        shock_indicators = ["¡", "!", "no", "nunca", "jamás", "imposible"]
        if any(ind in dialogue_lower for ind in question_indicators + shock_indicators):
            score += 4
        else:
            score += 2

        # Camera contribution
        camera = first_beat.camera
        if camera.get("shot_type") == "ECU" or camera.get("movement") == "push_in":
            score += 2
        else:
            score += 1

        return min(20, max(0, score))

    def _score_historia(self, script: MasterScript) -> int:
        """Score plot, structure, pacing, coherence."""
        score = 0
        beats = script.beats

        # Check that we have 9 beats
        if len(beats) == 9:
            score += 4
        else:
            score += max(
                0, 4 - abs(len(beats) - 9)
            )  # Penalty for missing/additional beats

        # Check pacing distribution (should vary)
        paces = [beat.pacing for beat in beats]
        unique_paces = len(set(paces))
        if unique_paces >= 3:
            score += 3
        elif unique_paces == 2:
            score += 2
        else:
            score += 1

        # Check tension progression (should generally increase)
        tensions = [beat.tension for beat in beats]
        increasing_count = sum(
            1 for i in range(1, len(tensions)) if tensions[i] >= tensions[i - 1]
        )
        if increasing_count >= 6:  # Mostly increasing
            score += 3
        elif increasing_count >= 4:
            score += 2
        else:
            score += 1

        # Check for clear beat names and purposes
        expected_beat_names = [
            "HOOK EXPLOSIVO",
            "CONTEXTO MÍNIMO",
            "PROBLEMA INMEDIATO",
            "ESCALADA",
            "GIRO / REVELACIÓN",
            "COMPLICACIÓN",
            "REVERSAL MAYOR",
            "NUEVA INFORMACIÓN",
            "CLIFFHANGER",
        ]
        name_matches = sum(
            1
            for beat, expected in zip(beats, expected_beat_names)
            if expected.lower() in beat.beat_name.lower()
        )
        score += min(3, name_matches // 3)  # Up to 3 points for good naming

        # Check for emotional arc variation
        emotions = [beat.emotion for beat in beats]
        unique_emotions = len(set(emotions))
        if unique_emotions >= 5:
            score += 2
        elif unique_emotions >= 3:
            score += 1

        return min(15, max(0, score))

    def _score_emocion(self, script: MasterScript) -> int:
        """Score emotional impact, authenticity, variety."""
        score = 0
        beats = script.beats

        # Check emotional arc follows expected pattern for genre
        emotions = [beat.emotion for beat in beats]
        # Should have good variation (not all same emotion)
        if len(set(emotions)) >= 4:
            score += 4
        elif len(set(emotions)) >= 2:
            score += 2
        else:
            score += 0

        # Check for emotional beats that match the 9-beat emotional arc expectation
        expected_emotions = [
            "sorpresa",
            "tension",
            "miedo",
            "indignacion",
            "esperanza",
            "sorpresa",
            "dolor",
            "recompensa",
            "nueva_amenaza",
        ]
        matches = sum(
            1
            for i, (actual, expected) in enumerate(zip(emotions, expected_emotions))
            if actual == expected or self._emotions_related(actual, expected)
        )
        score += min(4, matches // 2)  # Up to 4 points for good emotional progression

        # Check dialogue emotional authenticity (brief but impactful)
        dialogue_emotion_matches = 0
        for beat in beats:
            dialogue_lower = beat.dialogue.lower()
            emotion_words = {
                "sorpresa": ["qué", "cómo", "imposible", "en serio", "en serio"],
                "tension": ["ahora", "rápido", "corre", "rápido", "no hay tiempo"],
                "miedo": ["miedo", "temor", "asustado", "qué pasará", "no quiero"],
                "indignacion": [
                    "injusto",
                    "no puedo",
                    "basta",
                    "ya basta",
                    "parar esto",
                ],
                "esperanza": [
                    "esperanza",
                    "tal vez",
                    "quizás",
                    "todavía",
                    "aún podemos",
                ],
                "dolor": [
                    "duele",
                    "extraño",
                    "echo de menos",
                    "no puedo creer",
                    "lo lamento",
                ],
                "recompensa": ["lo logramos", "valió la pena", "lo sabía", "justo así"],
                "nueva_amenaza": [
                    "pero",
                    "ahora",
                    "esto",
                    "acaba de comenzar",
                    "no creí",
                ],
                "determinacion": [
                    "haré",
                    "no importa",
                    "lo haré",
                    "aunque cueste",
                    "no importa el costo",
                ],
                "curiosidad": [
                    "qué significa",
                    "necesito saber",
                    "cómo es posible",
                    "no entiendo",
                    "qué pasó",
                ],
            }
            for emotion, words in emotion_words.items():
                if beat.emotion == emotion and any(
                    word in dialogue_lower for word in words
                ):
                    dialogue_emotion_matches += 1
                    break

        score += min(
            3, dialogue_emotion_matches // 2
        )  # Up to 3 points for emotional dialogue

        # Check for physical actions showing emotion (show don't tell)
        physical_indicators = [
            "rompe",
            "tira",
            "golpea",
            "abraza",
            "besa",
            "llora",
            "grita",
            "huir",
            "correr",
            "esconder",
            "temblar",
            "sudor",
            "lágrima",
        ]
        physical_beats = sum(
            1
            for beat in beats
            if any(ind in beat.action.lower() for ind in physical_indicators)
        )
        score += min(
            3, physical_beats // 2
        )  # Up to 3 points for physical emotion expression

        return min(15, max(0, score))

    def _emotions_related(self, emo1: str, emo2: str) -> bool:
        """Check if two emotions are related (for scoring flexibility)."""
        related_groups = [
            ["sorpresa", "asombro", "impacto"],
            ["tension", "ansiedad", "miedo", "temor"],
            ["miedo", "terror", "pavor"],
            ["indignacion", "rabia", "frustración", "enojo"],
            ["esperanza", "optimismo", "fe", "confianza"],
            ["dolor", "tristeza", "melancolía", "llanto"],
            ["recompensa", "satisfacción", "alegría", "felicidad", "contento"],
            ["nueva_amenaza", "peligro", "amenaza", "riesgo"],
            ["determinacion", "resolución", "valor", "coraje"],
            ["curiosidad", "intriga", "interés", "duda"],
        ]
        for group in related_groups:
            if emo1 in group and emo2 in group:
                return True
        return False

    def _score_retencion(self, script: MasterScript) -> int:
        """Score ability to retain viewer attention."""
        score = 0
        beats = script.beats

        # Check for hook strength in first beat (already partially scored in hook)
        # Additional retention factors: question creation, pacing variations, emotional spikes

        # Count how many beats create or maintain questions
        question_indicators = [
            "¿",
            "?",
            "qué",
            " quién",
            "cómo",
            "cuándo",
            "dónde",
            "por qué",
            "mystery",
            "secreto",
        ]
        question_beats = 0
        for beat in beats:
            combined_text = (
                beat.action + " " + beat.dialogue + " " + beat.subtitle_en
            ).lower()
            if any(ind in combined_text for ind in question_indicators):
                question_beats += 1
        score += min(4, question_beats)  # Up to 4 points for question creation

        # Check for pacing variations (avoid monotony)
        paces = [beat.pacing for beat in beats]
        pace_changes = sum(1 for i in range(1, len(paces)) if paces[i] != paces[i - 1])
        if pace_changes >= 5:
            score += 3
        elif pace_changes >= 3:
            score += 2
        else:
            score += 1

        # Check for emotional highs and lows (variety)
        emotions = [beat.emotion for beat in beats]
        # Look for at least one high tension and one low/tender moment
        high_tension = any(beat.tension >= 8 for beat in beats)
        low_tension_or_tender = any(
            beat.emotion in ["esperanza", "dolor", "recompensa"] for beat in beats
        )
        if high_tension and low_tension_or_tender:
            score += 3
        elif high_tension or low_tension_or_tender:
            score += 2
        else:
            score += 1

        # Check for information delivery timing (not too much too early)
        info_beats = sum(1 for beat in beats if beat.is_info_beat)
        if 2 <= info_beats <= 4:  # Ideal amount of exposition beats
            score += 2
        elif info_beats == 1 or info_beats == 5:
            score += 1
        # 0 or >5 info beats gets 0

        # Check for climax placement (should be around beat 7-9)
        # The highest tension should be in later beats
        tensions = [beat.tension for beat in beats]
        max_tension_index = tensions.index(max(tensions)) if tensions else -1
        if max_tension_index >= 5:  # Beat 6 or later (0-indexed)
            score += 2
        elif max_tension_index >= 3:
            score += 1

        return min(15, max(0, score))

    def _score_personajes(self, script: MasterScript) -> int:
        """Score character depth, consistency, chemistry."""
        score = 0
        beats = script.beats

        # Check for character variety and development
        all_characters = []
        for beat in beats:
            all_characters.extend(beat.characters_present)
        unique_characters = list(set(all_characters))
        if len(unique_characters) >= 3:
            score += 3
        elif len(unique_characters) >= 2:
            score += 2
        else:
            score += 1

        # Check for character-revealing actions and dialogue
        character_revealing_beats = 0
        for beat in beats:
            combined = (beat.action + " " + beat.dialogue).lower()
            revealing_indicators = [
                "secreto",
                "miedo",
                "deseo",
                "recuerdo",
                "promesa",
                "juramento",
                "confesión",
                "admitir",
                "revelar",
                "confesar",
            ]
            if any(ind in combined for ind in revealing_indicators):
                character_revealing_beats += 1
        score += min(3, character_revealing_beats // 2)  # Up to 3 points

        # Check for character consistency (same characters maintain traits)
        # This would require character bible data, simplified here:
        # Assume good if we have recurring characters across beats
        recurring_characters = [
            char for char in unique_characters if all_characters.count(char) > 1
        ]
        if len(recurring_characters) >= 2:
            score += 2
        elif len(recurring_characters) == 1:
            score += 1

        # Check for interpersonal dynamics (chemistry, conflict, bonding)
        interaction_beats = sum(
            1 for beat in beats if len(beat.characters_present) >= 2
        )
        if interaction_beats >= 5:
            score += 2
        elif interaction_beats >= 3:
            score += 1

        return min(10, max(0, score))

    def _score_visual(self, script: MasterScript) -> int:
        """Score visual composition, lighting, consistency."""
        score = 0
        beats = script.beats

        # Check for visual variety in camera shots
        shot_types = [beat.camera.get("shot_type", "") for beat in beats if beat.camera]
        unique_shots = len(set(shot_types))
        if unique_shots >= 4:
            score += 3
        elif unique_shots >= 2:
            score += 2
        else:
            score += 1

        # Check for lighting and lens variety (simplified)
        lenses = [beat.camera.get("lens", "") for beat in beats if beat.camera]
        unique_lenses = len(set(lenses))
        if unique_lenses >= 3:
            score += 2
        elif unique_lenses >= 1:
            score += 1

        # Check for movement variety
        movements = [beat.camera.get("movement", "") for beat in beats if beat.camera]
        unique_movements = len(set(movements))
        if unique_movements >= 3:
            score += 2
        elif unique_movements >= 1:
            score += 1

        # Check for visual elements that are known to be viral/vengadores
        viral_visual_elements = [
            "paraguas",
            "back hug",
            "face reveal",
            "confrontación",
            "momento break",
            "lágrima",
            "espejo",
            "reflejo",
        ]
        visual_element_mentions = 0
        for beat in beats:
            combined = (beat.action + " " + beat.subtitle_en).lower()
            if any(element in combined for element in viral_visual_elements):
                visual_element_mentions += 1
        score += min(
            3, visual_element_mentions
        )  # Up to 3 points for viral visual elements

        # Check for color and lighting indications in descriptions
        lighting_indicators = [
            "luz",
            "sombra",
            "oscuridad",
            "brillo",
            "reflejo",
            "silhouette",
            "contrajuego",
        ]
        lighting_mentions = sum(
            1
            for beat in beats
            if any(
                ind in (beat.action + " " + beat.subtitle_en).lower()
                for ind in lighting_indicators
            )
        )
        score += min(2, lighting_mentions // 2)  # Up to 2 points for lighting awareness

        return min(10, max(0, score))

    def _score_audio(self, script: MasterScript) -> int:
        """Score audio elements: dialogue clarity, music fit, SFX quality."""
        score = 0
        beats = script.beats

        # Check for SFX presence and variety
        sfx_counts = []
        for beat in beats:
            sfx_list = beat.sound.get("sfx", []) if beat.sound else []
            sfx_counts.append(len(sfx_list))
        total_sfx = sum(sfx_counts)
        if total_sfx >= 6:
            score += 2
        elif total_sfx >= 3:
            score += 1
        # 0-2 SFX gets 0 for this component

        # Check for music cues presence and variety
        music_cues = [beat.sound.get("music_cue", "") for beat in beats if beat.sound]
        non_empty_music = [cue for cue in music_cues if cue]
        if len(non_empty_music) >= 4:
            score += 2
        elif len(non_empty_music) >= 2:
            score += 1

        # Check for ambience/atmosphere
        ambience_presences = [
            beat.sound.get("ambience", "") for beat in beats if beat.sound
        ]
        non_empty_ambience = [amb for amb in ambience_presences if amb]
        if len(non_empty_ambience) >= 5:
            score += 1

        # Check for dialogue clarity indicators (implied by brief dialogue)
        brief_dialogue_count = sum(
            1 for beat in beats if len(beat.dialogue.split()) <= 8
        )
        if brief_dialogue_count >= 7:
            score += 2
        elif brief_dialogue_count >= 5:
            score += 1

        return min(5, max(0, score))

    def _score_cliffhanger(self, script: MasterScript) -> int:
        """Score cliffhanger: urgency, curiosity, specificity."""
        if not hasattr(script, "cliffhanger") or not script.cliffhanger:
            return 0

        ch = script.cliffhanger
        score = 0

        # Urgency (0-4 points)
        if ch.urgency >= 9:
            score += 4
        elif ch.urgency >= 7:
            score += 3
        elif ch.urgency >= 5:
            score += 2
        elif ch.urgency >= 3:
            score += 1

        # Curiosity (0-3 points)
        if ch.curiosity >= 9:
            score += 3
        elif ch.curiosity >= 7:
            score += 2
        elif ch.curiosity >= 5:
            score += 1

        # Specificity (0-3 points)
        if ch.specificity >= 9:
            score += 3
        elif ch.specificity >= 7:
            score += 2
        elif ch.specificity >= 5:
            score += 1

        return min(10, max(0, score))

    def _score_cta(self, script: MasterScript) -> int:
        """Score call to action: narrative integration, clarity, urgency."""
        if not hasattr(script, "cta") or not script.cta:
            return 0

        cta = script.cta
        score = 0

        # Narrative integration (0-3 points) - tied to cliffhanger
        # Simple check: if text mentions something from the episode
        cliffhanger_keywords = set(script.cliffhanger.question.lower().split())
        cta_words = set(cta.text.lower().split())
        overlap = len(cliffhanger_keywords.intersection(cta_words))
        if overlap >= 3:
            score += 3
        elif overlap >= 2:
            score += 2
        elif overlap >= 1:
            score += 1

        # Clarity (0-2 points) - clear, direct language
        if len(cta.text.split()) <= 12:  # Reasonably short and clear
            score += 2
        elif len(cta.text.split()) <= 18:
            score += 1

        # Urgency/action orientation (0-1 point)
        action_words = [
            "haz",
            "ve",
            "corre",
            "escucha",
            "mira",
            "actúa",
            "participa",
            "comenta",
            "suscríbete",
            "dueto",
            "stitch",
        ]
        if any(word in cta.text.lower() for word in action_words):
            score += 1

        return min(5, max(0, score))

    def is_publishable(self, details: EpisodeScoreDetails) -> bool:
        """Check if episode meets minimum quality threshold for publishing."""
        return details.total >= self.publish_minimum

    def needs_rewrite(self, details: EpisodeScoreDetails) -> bool:
        """Check if episode triggers rewrite threshold."""
        return details.total < self.rewrite_trigger

    def needs_human_review(self, details: EpisodeScoreDetails) -> bool:
        """Check if episode requires human review."""
        return details.total < self.human_review_threshold

    def get_rewrite_instructions(self, details: EpisodeScoreDetails) -> dict[str, str]:
        """Generate specific rewrite instructions based on low scores."""
        instructions = {}

        if details.hook < 12:  # 60% of 20
            instructions["hook"] = (
                "Fortalece el hook inicial: debe detener el scroll en los primeros 3 segundos con una pregunta visual o acción impactante."
            )

        if details.historia < 9:  # 60% of 15
            instructions["historia"] = (
                "Mejorar la estructura narrativa: asegúrate de tener un claro comienzo, medio y final con progresión lógica de eventos."
            )

        if details.emocion < 9:  # 60% of 15
            instructions["emocion"] = (
                "Aumentar el impacto emocional: muestra más emociones a través de acciones físicas y diálogos breves pero significativos."
            )

        if details.retencion < 9:  # 60% of 15
            instructions["retencion"] = (
                "Incluir más preguntas abiertas y variar el pacing para mantener la atención del espectador a lo largo del episodio."
            )

        if details.personajes < 6:  # 60% of 10
            instructions["personajes"] = (
                "Desarrollar mejor los personajes: darles motivaciones claras, acciones reveladoras y relaciones interpersonales interesantes."
            )

        if details.visual < 6:  # 60% of 10
            instructions["visual"] = (
                "Mejorar la composición visual: variar tipos de tomas, usar iluminación intencionalmente y incluir elementos visuales virales."
            )

        if details.audio < 3:  # 60% of 5
            instructions["audio"] = (
                "Mejorar el diseño de audio: agregar efectos de sonido significativos, usar la música como herramienta narrativa y asegurar claridad de diálogo."
            )

        if details.cliffhanger < 3:  # 60% of 5
            instructions["cliffhanger"] = (
                "Hacer el cliffhanger más fuerte: aumentar la urgencia, curiosidad y especificidad de la pregunta sin respuesta."
            )

        if details.cta < 3:  # 60% of 5
            instructions["cta"] = (
                "Mejorar el llamado a acción: hacerlo narrativo, claro y directamente relacionado con el cliffhanger del episodio."
            )

        return instructions


# Convenience function
def score_episode(script: MasterScript) -> EpisodeScoreDetails:
    """Convenience function to score an episode."""
    scorer = EpisodeScorer()
    return scorer.score_episode(script)


if __name__ == "__main__":
    # Quick test (would need a MasterScript instance)
    print("EpisodeScorer module loaded successfully")
    print("Thresholds: Publishable >=85, Rewrite <75, Human Review <70")
