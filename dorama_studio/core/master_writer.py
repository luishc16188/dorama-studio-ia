"""
Master Writer Agent - Generates viral vertical drama scripts using the 9-beat structure
and the H->P->Q->E->R->Q2->C fractal formula.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from dorama_studio.contracts.character_bible import CharacterBible
from dorama_studio.contracts.trend_signal import TrendSignal


@dataclass
class Beat:
    """Represents a single beat in the 9-beat structure."""

    beat_name: str
    time_range: str  # e.g., "0-10s"
    duration: float  # in seconds
    action: str  # Physical action + subtext
    dialogue: str  # Dialogue (max 8 words per intervention)
    subtitle_en: str  # English subtitle
    camera: dict[str, Any] = field(default_factory=dict)
    sound: dict[str, Any] = field(default_factory=dict)
    emotion: str = "neutral"
    characters_present: list[str] = field(default_factory=list)
    pacing: str = "medium"  # hyper, fast, medium, slow
    tension: int = 5  # 0-10
    is_info_beat: bool = False
    pattern_interrupt: str | None = None


@dataclass
class Cliffhanger:
    """Represents the cliffhanger at the end of an episode."""

    type: str  # revelacion, amenaza, decision, identidad, traicion, accion_interrumpida, respuesta_congelada, reversal
    question: str  # The unresolved question that drives curiosity
    visual: str  # Visual description of the cliffhanger moment
    urgency: int = 5  # 0-10
    curiosity: int = 5  # 0-10
    specificity: int = 5  # 0-10


@dataclass
class CTA:
    """Call to Action that is narrative and tied to the cliffhanger."""

    text: str
    type: str  # e.g., "continuation", "reaction", "theory"
    platform_specific: dict[str, str] = field(default_factory=dict)


@dataclass
class SecretMatrix:
    """Metadata tracking secrets and revelations for the episode."""

    main_conflict: str
    revealed_secret: str
    unresolved_question: str


@dataclass
class MasterScript:
    """Complete script for a single episode."""

    episode_num: int
    title: str
    beats: list[Beat]
    cliffhanger: Cliffhanger
    cta: CTA
    secret_matrix: SecretMatrix
    emotional_arc: list[str]  # List of emotions across the 9 beats
    # Additional metadata
    trend_signal: TrendSignal | None = None
    character_bible: CharacterBible | None = None
    target_audience: str = "Gen Z, 18-24"
    genre: str = "Romance/Thriller"
    tone: str = "Emotional, Suspenseful"


class MasterWriter:
    """
    Generates episode scripts following the viral drama framework.
    """

    def __init__(self):
        # Predefined templates for different genres and emotions
        self.genre_templates = {
            "romance": self._get_romance_template(),
            "thriller": self._get_thriller_template(),
            "fantasy": self._get_fantasy_template(),
            "comedy": self._get_comedy_template(),
        }

        # Emotional arc templates (9 beats)
        self.emotional_arcs = {
            "romance": [
                "sorpresa",
                "tension",
                "miedo",
                "indignacion",
                "esperanza",
                "sorpresa",
                "dolor",
                "recompensa",
                "nueva_amenaza",
            ],
            "thriller": [
                "tension",
                "miedo",
                "sorpresa",
                "indignacion",
                "esperanza",
                "tension",
                "dolor",
                "recompensa",
                "nueva_amenaza",
            ],
            "fantasy": [
                "asombro",
                "curiosidad",
                "tension",
                "miedo",
                "esperanza",
                "sorpresa",
                "dolor",
                "recompensa",
                "nueva_amenaza",
            ],
            "comedy": [
                "humor",
                "sorpresa",
                "alegría",
                "tension",
                "esperanza",
                "sorpresa",
                "dolor",
                "recompensa",
                "nueva_amenaza",
            ],
        }

        # Camera shot mappings by emotion and tension
        self.camera_presets = {
            "high_tension": {
                "shot_type": "ECU",
                "angle": "eye_level",
                "movement": "push_in",
                "lens": "85mm f/1.4",
                "focus_pull": "pupila → papel",
            },
            "emotional_intimacy": {
                "shot_type": "CU",
                "angle": "slightly_above",
                "movement": "static",
                "lens": "50mm f/1.8",
                "focus_pull": "ojos",
            },
            "action": {
                "shot_type": "WS",
                "angle": "low_angle",
                "movement": "handheld",
                "lens": "24-70mm f/2.8",
                "focus_pull": "acción",
            },
            "revelation": {
                "shot_type": "ECU",
                "angle": "eye_level",
                "movement": "slow_zoom",
                "lens": "100mm f/2.8",
                "focus_pull": "texto o objeto",
            },
            "establishing": {
                "shot_type": "WS",
                "angle": "high_angle",
                "movement": "static",
                "lens": "16-35mm f/4",
                "focus_pull": "escenario",
            },
        }

        # Sound design presets
        self.sound_presets = {
            "tension_pulse_low": {
                "sfx": ["heartbeat_subtle"],
                "ambience": "HVAC hum",
                "music_cue": "low_drone",
            },
            "revelation_sting": {
                "sfx": ["paper_whisper", "glass_tap"],
                "ambience": "silence",
                "music_cue": "high_string_sting",
            },
            "emotional_swell": {
                "sfx": [],
                "ambience": "room_tone",
                "music_cue": "piano_arpeggio",
            },
            "action_impact": {
                "sfx": ["punch_impact", "glass_break"],
                "ambience": "outdoor_wind",
                "music_cue": "percussive_hit",
            },
        }

    def generate_script(
        self,
        episode_num: int,
        title: str,
        genre: str = "romance",
        trend_signal: TrendSignal | None = None,
        character_bible: CharacterBible | None = None,
    ) -> MasterScript:
        """
        Generate a complete episode script following the 9-beat structure.
        """
        # Select emotional arc based on genre
        emotional_arc = self.emotional_arcs.get(genre, self.emotional_arcs["romance"])

        # Generate the 9 beats
        beats = self._generate_nine_beats(episode_num, title, genre, emotional_arc)

        # Generate cliffhanger (type rotates to avoid repetition)
        cliffhanger = self._generate_cliffhanger(episode_num, genre)

        # Generate CTA tied to cliffhanger
        cta = self._generate_cta(cliffhanger)

        # Generate secret matrix
        secret_matrix = self._generate_secret_matrix(beats, cliffhanger, genre)

        script = MasterScript(
            episode_num=episode_num,
            title=title,
            beats=beats,
            cliffhanger=cliffhanger,
            cta=cta,
            secret_matrix=secret_matrix,
            emotional_arc=emotional_arc,
            trend_signal=trend_signal,
            character_bible=character_bible,
            target_audience="Gen Z, 18-24",
            genre=genre,
            tone="Emotional, Suspenseful",
        )

        return script

    def _generate_nine_beats(
        self,
        episode_num: int,
        title: str,
        genre: str,
        emotional_arc: list[str],
    ) -> list[Beat]:
        """Generate the 9 beats following the H->P->Q->E->R->Q2->C formula."""
        beats = []

        # Beat 1: HOOK EXPLOSIVO (0-10s)
        beats.append(
            Beat(
                beat_name="HOOK EXPLOSIVO",
                time_range="0-10s",
                duration=10.0,
                action=self._generate_hook_action(episode_num, genre),
                dialogue=self._generate_dialogue(max_words=8, emotion="sorpresa"),
                subtitle_en="English subtitle for hook",
                camera=self.camera_presets["high_tension"],
                sound=self.sound_presets["tension_pulse_low"],
                emotion=emotional_arc[0],
                characters_present=["@Protagonista", "@Antagonista"],
                pacing="hyper",
                tension=8,
                is_info_beat=False,
                pattern_interrupt="whip_pan",
            )
        )

        # Beat 2: CONTEXTO MÍNIMO (10-20s)
        beats.append(
            Beat(
                beat_name="CONTEXTO MÍNIMO",
                time_range="10-20s",
                duration=10.0,
                action=self._generate_context_action(episode_num, genre),
                dialogue=self._generate_dialogue(max_words=8, emotion="curiosidad"),
                subtitle_en="English subtitle for context",
                camera=self.camera_presets["emotional_intimacy"],
                sound=self.sound_presets["emotional_swell"],
                emotion=emotional_arc[1],
                characters_present=["@Protagonista", "@Aliado"],
                pacing="fast",
                tension=5,
                is_info_beat=True,
                pattern_interrupt=None,
            )
        )

        # Beat 3: PROBLEMA INMEDIATO (20-30s)
        beats.append(
            Beat(
                beat_name="PROBLEMA INMEDIATO",
                time_range="20-30s",
                duration=10.0,
                action=self._generate_problem_action(episode_num, genre),
                dialogue=self._generate_dialogue(max_words=8, emotion="tension"),
                subtitle_en="English subtitle for problem",
                camera=self.camera_presets["action"],
                sound=self.sound_presets["tension_pulse_low"],
                emotion=emotional_arc[2],
                characters_present=["@Protagonista", "@Antagonista"],
                pacing="fast",
                tension=6,
                is_info_beat=False,
                pattern_interrupt=None,
            )
        )

        # Beat 4: ESCALADA (30-40s)
        beats.append(
            Beat(
                beat_name="ESCALADA",
                time_range="30-40s",
                duration=10.0,
                action=self._generate_escalation_action(episode_num, genre),
                dialogue=self._generate_dialogue(max_words=8, emotion="miedo"),
                subtitle_en="English subtitle for escalation",
                camera=self.camera_presets["high_tension"],
                sound=self.sound_presets["tension_pulse_low"],
                emotion=emotional_arc[3],
                characters_present=["@Protagonista", "@Antagonista", "@Aliado"],
                pacing="medium",
                tension=7,
                is_info_beat=False,
                pattern_interrupt=None,
            )
        )

        # Beat 5: GIRO / REVELACIÓN (40-50s)
        beats.append(
            Beat(
                beat_name="GIRO / REVELACIÓN",
                time_range="40-50s",
                duration=10.0,
                action=self._generate_revelation_action(episode_num, genre),
                dialogue=self._generate_dialogue(max_words=8, emotion="sorpresa"),
                subtitle_en="English subtitle for revelation",
                camera=self.camera_presets["revelation"],
                sound=self.sound_presets["revelation_sting"],
                emotion=emotional_arc[4],
                characters_present=["@Protagonista", "@Antagonista"],
                pacing="medium",
                tension=8,
                is_info_beat=False,
                pattern_interrupt=None,
            )
        )

        # Beat 6: COMPLICACIÓN (50-60s)
        beats.append(
            Beat(
                beat_name="COMPLICACIÓN",
                time_range="50-60s",
                duration=10.0,
                action=self._generate_complication_action(episode_num, genre),
                dialogue=self._generate_dialogue(max_words=8, emotion="indignacion"),
                subtitle_en="English subtitle for complication",
                camera=self.camera_presets["action"],
                sound=self.sound_presets["tension_pulse_low"],
                emotion=emotional_arc[5],
                characters_present=["@Protagonista", "@Antagonista", "@Aliado"],
                pacing="fast",
                tension=8,
                is_info_beat=False,
                pattern_interrupt=None,
            )
        )

        # Beat 7: REVERSAL MAYOR (60-70s)
        beats.append(
            Beat(
                beat_name="REVERSAL MAYOR",
                time_range="60-70s",
                duration=10.0,
                action=self._generate_reversal_action(episode_num, genre),
                dialogue=self._generate_dialogue(max_words=8, emotion="esperanza"),
                subtitle_en="English subtitle for reversal",
                camera=self.camera_presets["high_tension"],
                sound=self.sound_presets["revelation_sting"],
                emotion=emotional_arc[6],
                characters_present=["@Protagonista", "@Antagonista"],
                pacing="hyper",
                tension=9,
                is_info_beat=False,
                pattern_interrupt=None,
            )
        )

        # Beat 8: NUEVA INFORMACIÓN (70-80s)
        beats.append(
            Beat(
                beat_name="NUEVA INFORMACIÓN",
                time_range="70-80s",
                duration=10.0,
                action=self._generate_new_info_action(episode_num, genre),
                dialogue=self._generate_dialogue(max_words=8, emotion="tension"),
                subtitle_en="English subtitle for new info",
                camera=self.camera_presets["emotional_intimacy"],
                sound=self.sound_presets["emotional_swell"],
                emotion=emotional_arc[7],
                characters_present=["@Protagonista", "@Aliado"],
                pacing="medium",
                tension=7,
                is_info_beat=True,
                pattern_interrupt=None,
            )
        )

        # Beat 9: CLIFFHANGER (80-90s)
        beats.append(
            Beat(
                beat_name="CLIFFHANGER",
                time_range="80-90s",
                duration=10.0,
                action=self._generate_cliffhanger_action(episode_num, genre),
                dialogue=self._generate_dialogue(max_words=8, emotion="determinacion"),
                subtitle_en="English subtitle for cliffhanger",
                camera=self.camera_presets["revelation"],
                sound=self.sound_presets["revelation_sting"],
                emotion=emotional_arc[8],
                characters_present=["@Protagonista", "@Antagonista"],
                pacing="hyper",
                tension=10,
                is_info_beat=False,
                pattern_interrupt=None,
            )
        )

        return beats

    def _generate_hook_action(self, episode_num: int, genre: str) -> str:
        """Generate a hook action that stops the scroll in first 3 seconds."""
        hooks = {
            "romance": "Ella encuentra una carta sin remitente en su bolsillo",
            "thriller": "Una llamada anónima advierte: 'No confíes en nadie'",
            "fantasy": "El espejo muestra su reflejo... pero no es ella",
            "comedy": "Él accidentalmente envía un mensaje de amor a su jefe",
        }
        return hooks.get(genre, "Algo inesperado rompe la rutina cotidiana")

    def _generate_context_action(self, episode_num: int, genre: str) -> str:
        """Generate minimal context action."""
        contexts = {
            "romance": "Recuerda la promesa que se hicieron bajo la lluvia",
            "thriller": "Revisa las cámaras de seguridad buscando al desconocido",
            "fantasy": "Consulta el antiguo grimorio para entender el reflejo",
            "comedy": "Intenta borrar el mensaje antes de que su jefe lo lea",
        }
        return contexts.get(genre, "El personaje procesa lo que acaba de suceder")

    def _generate_problem_action(self, episode_num: int, genre: str) -> str:
        """Generate immediate problem action."""
        problems = {
            "romance": "La carta contiene una amenaza: 'Deja de verlo o pagarás las consecuencias'",
            "thriller": "Las cámaras muestran a alguien siguiendo a su mejor amigo",
            "fantasy": "El grimorio adviene que el reflejo está intentando reemplazarla",
            "comedy": "Su jefe menciona que vio el mensaje y quiere hablar en privado",
        }
        return problems.get(genre, "Un nuevo conflicto surge que complica la situación")

    def _generate_escalation_action(self, episode_num: int, genre: str) -> str:
        """Generate escalation action."""
        escalations = {
            "romance": "Decide confrontar al remitente apesar de la amenaza",
            "thriller": "Instala una cámara escondida para seguir al seguidor",
            "fantasy": "Intenta comunicarse con el reflejo a través del espejo",
            "comedy": "Se prepara para la conversación con su jefe practicando qué decir",
        }
        return escalations.get(
            genre, "El personaje toma una decisión que aumenta el riesgo"
        )

    def _generate_revelation_action(self, episode_num: int, genre: str) -> str:
        """Generate revelation/action beat."""
        revelations = {
            "romance": "La carta es de su ex, quien revela un secreto peligroso sobre su actual pareja",
            "thriller": "El seguidor es su hermano desaparecido, buscando ayuda",
            "fantasy": "El reflejo intenta advertirle sobre un peligro inminente en el espejo",
            "comedy": "Su jefe en realidad quería felicitarlo por un proyecto exitoso",
        }
        return revelations.get(
            genre, "Se revela información clave que cambia la percepción del conflicto"
        )

    def _generate_complication_action(self, episode_num: int, genre: str) -> str:
        """Generate complication action."""
        complications = {
            "romance": "Al confrontar al ex, descubre que él también está siendo amenazado",
            "thriller": "Al seguir a su hermano, lo ven entrando a un edificio sospechoso",
            "fantasy": "El reflejo muestra una visión de un accidente que aún no ha ocurrido",
            "comedy": "Durante la conversación, su jefe menciona un ascenso que implica mudarse a otra ciudad",
        }
        return complications.get(
            genre, "Nuevos factores complican la situación inicial"
        )

    def _generate_reversal_action(self, episode_num: int, genre: str) -> str:
        """Generate major reversal action."""
        reversals = {
            "romance": "El ex revela que él también está siendo chantajeado por la misma persona",
            "thriller": "El edificio sospechoso es en realidad un centro de rescate de víctimas",
            "fantasy": "La visión del reflejo muestra cómo evitar el accidente, no causarlo",
            "comedy": "El ascenso incluye liderar el proyecto que él siempre quiso dirigir",
        }
        return reversals.get(
            genre, "La situación da un giro inesperado que beneficia al protagonista"
        )

    def _generate_new_info_action(self, episode_num: int, genre: str) -> str:
        """Generate new information action."""
        new_info = {
            "romance": "El chantajeador es alguien cercano que conoce ambos secretos",
            "thriller": "Descubren que el centro de rescate está investigando a una red criminal",
            "fantasy": "La visión muestra que deben actuar en el próximo horario de eclipse",
            "comedy": "El ascenso requiere que deje su equipo actual y lidie con personal desconocido",
        }
        return new_info.get(
            genre, "Se revela información que abre nuevas posibilidades y preguntas"
        )

    def _generate_cliffhanger_action(self, episode_num: int, genre: str) -> str:
        """Generate cliffhanger action."""
        cliffhangers = {
            "romance": "Recibe un mensaje del chantajeador: 'Ya sé que él te ayudó'",
            "thriller": "Al salir del centro, ven a su hermano siendo forzado a entrar a un auto negro",
            "fantasy": "En el eclipse, el reflejo sale del espejo y se pone detrás de ella",
            "comedy": "Al aceptar el ascenso, descubre que debe mudarse a otro país inmediatamente",
        }
        return cliffhangers.get(
            genre,
            "Termina con una pregunta sin respuesta que obliga a ver el siguiente episodio",
        )

    def _generate_dialogue(self, max_words: int = 8, emotion: str = "neutral") -> str:
        """Generate brief dialogue (max words per intervention)."""
        # Simple dialogue bank by emotion
        dialogue_bank = {
            "sorpresa": [
                "¿En serio?",
                "Esto no puede estar pasando",
                "No lo creía posible",
            ],
            "tension": [
                "Tenemos que actuar ahora",
                "No hay tiempo para explicar",
                "Cada segundo cuenta",
            ],
            "miedo": [
                "¿Y si...?",
                "No quiero estar solo/a",
                "Siento que algo malo viene",
            ],
            "indignacion": [
                "Esto es injustificable",
                "No puedo permitir que siga así",
                "Hay que hacer algo ya",
            ],
            "esperanza": [
                "Tal vez todavía haya una manera",
                "No todo está perdido",
                "Aún podemos intentarlo",
            ],
            "dolor": [
                "No sabía que me importaba tanto",
                "Esto duele más de lo que pensé",
                "Echo de menos lo que teníamos",
            ],
            "recompensa": [
                "Lo logramos juntos",
                "Valió la pena esperar",
                "Esto es exactamente lo que necesitábamos",
            ],
            "nueva_amenaza": [
                "Pero ahora...",
                "Acaba de comenzar lo peor",
                "No creí que pudiera empeorar",
            ],
            "determinacion": [
                "No me rendiré",
                "Haré lo que sea necesario",
                "Este asunto no termina aquí",
            ],
            "curiosidad": [
                "¿Qué significa esto?",
                "Necesito saber más",
                "Hay algo que no me cuadra",
            ],
            "neutral": ["Entiendo", "Vale", "Así será"],
        }
        options = dialogue_bank.get(emotion, dialogue_bank["neutral"])
        dialogue = random.choice(options)
        # Ensure max words constraint (approximate)
        words = dialogue.split()
        if len(words) > max_words:
            dialogue = " ".join(words[:max_words])
        return dialogue

    def _generate_cliffhanger(self, episode_num: int, genre: str) -> Cliffhanger:
        """Generate cliffhanger with rotating types to avoid repetition."""
        cliffhanger_types = [
            "revelacion",
            "amenaza",
            "decision",
            "identidad",
            "traicion",
            "accion_interrumpida",
            "respuesta_congelada",
            "reversal",
        ]
        # Simple rotation based on episode number to avoid immediate repeats
        selected_type = cliffhanger_types[episode_num % len(cliffhanger_types)]

        questions = {
            "revelacion": "¿Quién está realmente detrás de las amenazas?",
            "amenaza": "¿Cómo escaparán de esta situación sin ser vistos?",
            "decision": "¿Aceptará el trato aunque signifique perderlo todo?",
            "identidad": "¿Por qué el reflejo conoce tantos detalles de su vida?",
            "traicion": "¿Por qué su aliado más confiable los ha delatado?",
            "accion_interrumpida": "¿Lograrán llegar a tiempo antes de que ocurra lo inevitable?",
            "respuesta_congelada": "¿Qué decidirá hacer después de esa revelación devastadora?",
            "reversal": "¿Cómo revertirán las consecuencias de su última decisión?",
        }

        visuals = {
            "revelacion": "Primer plano de un documento sellado con el símbolo de la organización",
            "amenaza": "Dos figuras acercándose en la oscuridad, solo se ven sus siluetas",
            "decision": "Mano temblorosa sobre un contrato, bolígrafo listo para firmar",
            "identidad": "Reflejo en el espejo que hace un gesto que ella no hizo",
            "traicion": "Mensaje de texto enviado desde el teléfono del desaparecido",
            "accion_interrumpida": "Reloj marcando 00:00 mientras el personaje corre por el pasillo",
            "respuesta_congelada": "Lágrima congelada en la mejilla mientras procesa la información",
            "reversal": "Manos que antes luchaban ahora se unen en un mismo propósito",
        }

        return Cliffhanger(
            type=selected_type,
            question=questions[selected_type],
            visual=visuals[selected_type],
            urgency=random.randint(8, 10),
            curiosity=random.randint(8, 10),
            specificity=random.randint(7, 10),
        )

    def _generate_cta(self, cliffhanger: Cliffhanger) -> CTA:
        """Generate narrative call to action tied to the cliffhanger."""
        cta_map = {
            "revelacion": {
                "text": "¿Qué harías tú con este secreto?",
                "type": "reaction",
                "platform_specific": {
                    "tiktok": "Dueto con tu teoría",
                    "youtube": "Comenta tu predicción abajo",
                },
            },
            "amenaza": {
                "text": "¿Cómo escaparías de esta situación?",
                "type": "continuation",
                "platform_specific": {
                    "tiktok": "Stitch con tu plan de escape",
                    "youtube": "Suscríbete para ver el próximo episodio",
                },
            },
            "decision": {
                "text": "¿Aceptarías el trato o lucharías por tus principios?",
                "type": "theory",
                "platform_specific": {
                    "tiktok": "Stitch mostrando tu elección",
                    "youtube": "Comenta qué harías en su lugar",
                },
            },
            "identidad": {
                "text": "¿Quién crees que es realmente ese reflejo?",
                "type": "reaction",
                "platform_specific": {
                    "tiktok": "Dueto mostrando tu sospecha",
                    "youtube": "Teoría en los comentarios",
                },
            },
            "traicion": {
                "text": "¿Perdonarías una traición así o buscarías justicia?",
                "type": "continuation",
                "platform_specific": {
                    "tiktok": "Stitch con tu decisión",
                    "youtube": "Suscríbete para ver la consecuencia",
                },
            },
            "accion_interrumpida": {
                "text": "¿Lograrán llegar a tiempo?",
                "type": "continuation",
                "platform_specific": {
                    "tiktok": "Cuenta regresiva en dueto",
                    "youtube": "Mantente al tanto del desenlace",
                },
            },
            "respuesta_congelada": {
                "text": "¿Cómo reaccionarías ante esa noticia?",
                "type": "reaction",
                "platform_specific": {
                    "tiktok": "Dueto expresando tu emoción",
                    "youtube": "Comparte tu reacción en los comentarios",
                },
            },
            "reversal": {
                "text": "¿Cómo crees que arreglarán esta situación?",
                "type": "theory",
                "platform_specific": {
                    "tiktok": "Stitch mostrando tu solución",
                    "youtube": "Predice cómo resolverán el conflicto",
                },
            },
        }
        data = cta_map.get(cliffhanger.type, cta_map["revelacion"])
        return CTA(
            text=data["text"],
            type=data["type"],
            platform_specific=data["platform_specific"],
        )

    def _generate_secret_matrix(
        self,
        beats: list[Beat],
        cliffhanger: Cliffhanger,
        genre: str,
    ) -> SecretMatrix:
        """Generate secret matrix tracking what was revealed and what remains hidden."""
        # Simplified extraction from beats and cliffhanger
        main_conflict = (
            f"Protagonista enfrenta amenaza que pone en riesgo su {genre} y seguridad"
        )
        revealed_secret = (
            "El antagonista tiene una conexión personal con el pasado del protagonista"
        )
        unresolved_question = cliffhanger.question
        return SecretMatrix(
            main_conflict=main_conflict,
            revealed_secret=revealed_secret,
            unresolved_question=unresolved_question,
        )


# Convenience function
def generate_episode_script(
    episode_num: int,
    title: str,
    genre: str = "romance",
    trend_signal: TrendSignal | None = None,
    character_bible: CharacterBible | None = None,
) -> MasterScript:
    """Convenience function to generate an episode script."""
    writer = MasterWriter()
    return writer.generate_script(
        episode_num=episode_num,
        title=title,
        genre=genre,
        trend_signal=trend_signal,
        character_bible=character_bible,
    )


if __name__ == "__main__":
    # Quick test
    script = generate_episode_script(
        episode_num=1,
        title="El Secreto del Espejo",
        genre="fantasy",
    )
    print(f"Generated Episode {script.episode_num}: {script.title}")
    print(f"Beats: {len(script.beats)}")
    for i, beat in enumerate(script.beats, 1):
        print(
            f"  Beat {i}: {beat.beat_name} - {beat.emotion} (Tension: {beat.tension})"
        )
    print(f"Cliffhanger: {script.cliffhanger.type} - {script.cliffhanger.question}")
    print(f"Secret Matrix: {script.secret_matrix.main_conflict}")
