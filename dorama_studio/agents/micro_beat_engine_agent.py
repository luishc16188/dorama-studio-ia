"""
MicroBeat Engine – Arquitectura de microbeats de duración variable.
Implementa el motor de microbeats para episodios de ~90s con 8-14 beats variables.
"""

from __future__ import annotations

import random
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext


class MicroBeatSpec:
    """Especificación de un microbeat individual."""

    def __init__(
        self,
        beat_id: str,
        start: float,
        end: float,
        duration: float,
        narrative_goal: str,
        emotion_start: str,
        emotion_end: str,
        information_revealed: list[str],
        information_withheld: list[str],
        question_delta: str,
        character_action: str,
        acting: dict[str, Any],
        camera: dict[str, Any],
        motion: dict[str, Any],
        visual_focus: str,
        sound_state: dict[str, Any],
        music_state: dict[str, Any],
        sfx_events: list[str],
        transition: str,
        retention_reason: str
    ):
        self.beat_id = beat_id
        self.start = start
        self.end = end
        self.duration = duration
        self.narrative_goal = narrative_goal
        self.emotion_start = emotion_start
        self.emotion_end = emotion_end
        self.information_revealed = information_revealed
        self.information_withheld = information_withheld
        self.question_delta = question_delta
        self.character_action = character_action
        self.acting = acting
        self.camera = camera
        self.motion = motion
        self.visual_focus = visual_focus
        self.sound_state = sound_state
        self.music_state = music_state
        self.sfx_events = sfx_events
        self.transition = transition
        self.retention_reason = retention_reason


class MicroBeatEngineAgent(BaseAgent):
    """MicroBeat Engine - Crea microbeats de duración variable para episodios de ~90s."""

    def __init__(self):
        super().__init__("MicroBeatEngineAgent")

        # Envelope sugerido para 90 segundos basado en análisis forense
        self.suggested_envelope = [
            # (start_time, end_time, primary_function, typical_duration_range)
            (0.0, 3.0, "Hook", (2.0, 4.0)),           # 0-3s: Hook explosivo
            (3.0, 7.0, "Promise", (3.0, 5.0)),        # 3-7s: Promesa clara
            (7.0, 18.0, "Setup/Question", (8.0, 12.0)), # 7-18s: Setup y pregunta inicial
            (18.0, 35.0, "Escalation A", (12.0, 20.0)), # 18-35s: Escalada inicial
            (35.0, 50.0, "Reveal/Reward", (10.0, 20.0)), # 35-50s: Reveal y recompensa
            (50.0, 68.0, "Complication B", (12.0, 20.0)), # 50-68s: Complicación secundaria
            (68.0, 82.0, "Reversal/Peak", (8.0, 18.0)),   # 68-82s: Reversión emocional
            (82.0, 90.0, "Cliffhanger", (5.0, 10.0))      # 82-90s: Cliffhanger final
        ]

        # Patrones de microbeats basados en análisis forense
        self.microbeat_patterns = {
            "hook": [
                {"narrative_goal": "Establecer mundo y conflicto inmediato",
                 "emotion": "tension", "retention": "visual_impact"},
                {"narrative_goal": "Presentar deseo del protagonista",
                 "emotion": "curiosity", "retention": "object_focus"},
                {"narrative_goal": "Mostrar objeto de deseo",
                 "emotion": "anticipation", "retention": "curiosity_gap"}
            ],
            "promise": [
                {"narrative_goal": "Definir stakes claros",
                 "emotion": "determination", "retention": "stakes_clarity"},
                {"narrative_goal": "Mostrar capacidad de acción",
                 "emotion": "empowerment", "retention": "agency"},
                {"narrative_goal": "Crear conexión emocional",
                 "emotion": "connection", "retention": "relational_bond"}
            ],
            "setup": [
                {"narrative_goal": "Plantada primera pista",
                 "emotion": "intrigue", "retention": "information_asymmetry"},
                {"narrative_goal": "Mostrar obstáculo inicial",
                 "emotion": "frustration", "retention": "problem_awareness"},
                {"narrative_goal": "Establecer reglas del mundo",
                 "emotion": "understanding", "retention": "world_building"}
            ],
            "escalation": [
                {"narrative_goal": "Aumentar presión externa",
                 "emotion": "anxiety", "retention": "external_pressure"},
                {"narrative_goal": "Mostrar conflicto interno",
                 "emotion": "torture", "retention": "internal_conflict"},
                {"narrative_goal": "Revelar información crítica",
                 "emotion": "shock", "retention": "information_reward"}
            ],
            "reveal": [
                {"narrative_goal": "Revelar información clave",
                 "emotion": "revelation", "retention": "satisfaction"},
                {"narrative_goal": "Mostrar consecuencia inmediata",
                 "emotion": "fear", "retention": "consequence_awareness"},
                {"narrative_goal": "Establecer nueva pregunta",
                 "emotion": "curiosity", "retention": "open_loop"}
            ],
            "complication": [
                {"narrative_goal": "Introducir nuevo obstáculo",
                 "emotion": "anger", "retention": "frustration"},
                {"narrative_goal": "Mostrar traición o engaño",
                 "emotion": "betrayal", "retention": "trust_break"},
                {"narrative_goal": "Escalar amenaza",
                 "emotion": "panic", "retention": "survival_instinct"}
            ],
            "reversal": [
                {"narrative_goal": "Voltear la situación",
                 "emotion": "triumph", "retention": "empowerment"},
                {"narrative_goal": "Revelar información oculta",
                 "emotion": "awe", "retention": "wonder"},
                {"narrative_goal": "Establecer nueva dinámica",
                 "emotion": "hope", "retention": "possibility"}
            ],
            "cliffhanger": [
                {"narrative_goal": "Dejar pregunta crítica abierta",
                 "emotion": "urgency", "retention": "need_to_know"},
                {"narrative_goal": "Mostrar elección imposible",
                 "emotion": "anxiety", "retention": "moral_dilemma"},
                {"narrative_goal": "Amenazar lo que más importa",
                 "emotion": "fear", "retention": "protective_instinct"}
            ]
        }

        # Elementos de retención basados en análisis forense
        self.retention_triggers = {
            "visual_change": "Cambio en iluminación, color, composición",
            "information_delta": "Nueva información revelada o retenida",
            "emotion_delta": "Cambio en estado emocional detectable",
            "motion_delta": "Cambio en movimiento de cámara o acción",
            "social_tension": "Tensión en relaciones o poder",
            "question_pressure": "Presión de preguntas sin respuesta",
            "visual_novelty": "Elemento visual nunca visto antes",
            "sound_change": "Cambio en ambiente, música o efectos",
            "reward_signal": "Señal de recompensa o satisfacción",
            "pattern_interrupt": "Interrupción de patrón establecido"
        }

    def _process(self, ctx: PipelineContext) -> AgentResult:
        """Create variable duration microbeats for episode."""

        # Extract inputs
        episode_num = getattr(ctx, 'episode_num', 1)
        total_episodes = getattr(ctx, 'total_episodes', 40)
        blueprint = getattr(ctx, 'episode_blueprint', {})

        if not blueprint:
            # Fallback blueprint
            blueprint = {
                "hook_category": "mystery",
                "core_conflict": "Conflicto del episodio",
                "twist": "Giro inesperado",
                "cliffhanger": "Cliffhanger abierto",
                "cta_type": "moral_dilemma"
            }

        # Generate microbeats based on envelope
        microbeats = self._generate_microbeats(episode_num, blueprint)

        # Calculate total duration
        total_duration = sum(beat.duration for beat in microbeats)

        # Adjust to target ~90 seconds if needed
        microbeats = self._adjust_duration(microbeats, target_duration=90.0)

        # Create microbeat specification list
        microbeat_specs = []
        for i, beat_data in enumerate(microbeats):
            spec = MicroBeatSpec(
                beat_id=f"beat_{episode_num:03d}_{i+1:02d}",
                start=beat_data["start"],
                end=beat_data["end"],
                duration=beat_data["duration"],
                narrative_goal=beat_data["narrative_goal"],
                emotion_start=beat_data["emotion_start"],
                emotion_end=beat_data["emotion_end"],
                information_revealed=beat_data["information_revealed"],
                information_withheld=beat_data["information_withheld"],
                question_delta=beat_data["question_delta"],
                character_action=beat_data["character_action"],
                acting=beat_data["acting"],
                camera=beat_data["camera"],
                motion=beat_data["motion"],
                visual_focus=beat_data["visual_focus"],
                sound_state=beat_data["sound_state"],
                music_state=beat_data["music_state"],
                sfx_events=beat_data["sfx_events"],
                transition=beat_data["transition"],
                retention_reason=beat_data["retention_reason"]
            )
            microbeat_specs.append(spec)

        # Update state
        if hasattr(ctx, 'state') and ctx.state:
            state_dict = ctx.state.dict() if hasattr(ctx.state, 'dict') else dict(ctx.state) if hasattr(ctx.state, '__dict__') else {}
            state_dict['microbeats'] = [
                {
                    "beat_id": spec.beat_id,
                    "start": spec.start,
                    "end": spec.end,
                    "duration": spec.duration,
                    "narrative_goal": spec.narrative_goal,
                    "emotion_start": spec.emotion_start,
                    "emotion_end": spec.emotion_end,
                    "information_revealed": spec.information_revealed,
                    "information_withheld": spec.information_withheld,
                    "question_delta": spec.question_delta,
                    "character_action": spec.character_action,
                    "retention_reason": spec.retention_reason
                }
                for spec in microbeat_specs
            ]
            state_dict['microbeat_count'] = len(microbeat_specs)
            state_dict['total_duration'] = sum(spec.duration for spec in microbeat_specs)

            if hasattr(ctx.state, '__dict__'):
                for key, value in state_dict.items():
                    setattr(ctx.state, key, value)
            elif hasattr(ctx.state, '__setitem__'):
                for key, value in state_dict.items():
                    ctx.state[key] = value

        return AgentResult(
            success=True,
            agent_name=self.name,
            output_data={
                "microbeats": [
                    {
                        "beat_id": spec.beat_id,
                        "start": spec.start,
                        "end": spec.end,
                        "duration": spec.duration,
                        "narrative_goal": spec.narrative_goal,
                        "emotion_start": spec.emotion_start,
                        "emotion_end": spec.emotion_end,
                        "information_revealed": spec.information_revealed,
                        "information_withheld": spec.information_withheld,
                        "question_delta": spec.question_delta,
                        "character_action": spec.character_action,
                        "retention_reason": spec.retention_reason
                    }
                    for spec in microbeat_specs
                ],
                "microbeat_count": len(microbeat_specs),
                "total_duration": sum(spec.duration for spec in microbeat_specs),
                "envelope_used": self.suggested_envelope
            },
            context_updates={
                "microbeats": state_dict.get('microbeats', []),
                "microbeat_count": state_dict.get('microbeat_count', 0),
                "total_duration": state_dict.get('total_duration', 0.0)
            },
            logs=[{
                "step": "MicroBeatEngine",
                "episode": episode_num,
                "microbeat_count": len(microbeat_specs),
                "total_duration": round(sum(spec.duration for spec in microbeat_specs), 2),
                "beat_range": f"{len(microbeats)} beats"
            }],
        )

    def _generate_microbeats(self, episode_num: int, blueprint: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate microbeats based on envelope and blueprint."""

        microbeats = []
        current_time = 0.0
        hook_category = blueprint.get("hook_category", "mystery")

        # Generate beats for each envelope segment
        for segment_start, segment_end, function, duration_range in self.suggested_envelope:
            segment_duration = segment_end - segment_start

            # Determine number of microbeats in this segment (2-9 seconds each)
            min_beats = max(1, int(segment_duration / 9.0))  # Max 9s per beat
            max_beats = max(min_beats, int(segment_duration / 2.0))  # Min 2s per beat

            # Add some randomness but keep within bounds
            num_beats = random.randint(min_beats, max_beats)

            # Distribute duration among beats
            beat_durations = self._distribute_duration(segment_duration, num_beats, 2.0, 9.0)

            # Generate each microbeat in segment
            for i, duration in enumerate(beat_durations):
                beat_start = current_time
                beat_end = current_time + duration

                # Select appropriate pattern based on function and position
                pattern_category = self._map_function_to_pattern(function)
                pattern_index = (episode_num + i) % len(self.microbeat_patterns.get(pattern_category, [{}]))
                pattern = self.microbeat_patterns.get(pattern_category, [{}])[pattern_index]

                # Generate beat data
                beat_data = {
                    "start": beat_start,
                    "end": beat_end,
                    "duration": duration,
                    "narrative_goal": self._generate_narrative_goal(function, episode_num, i),
                    "emotion_start": pattern.get("emotion", "neutral"),
                    "emotion_end": self._get_emotion_arc(function, i, num_beats),
                    "information_revealed": self._generate_information_revealed(function, episode_num, i),
                    "information_withheld": self._generate_information_withheld(function, episode_num, i),
                    "question_delta": self._generate_question_delta(function, episode_num, i, blueprint),
                    "character_action": self._generate_character_action(function, episode_num, i),
                    "acting": self._generate_acting_spec(function, episode_num, i),
                    "camera": self._generate_camera_spec(function, episode_num, i, hook_category),
                    "motion": self._generate_motion_spec(function, episode_num, i),
                    "visual_focus": self._generate_visual_focus(function, episode_num, i),
                    "sound_state": self._generate_sound_state(function, episode_num, i),
                    "music_state": self._generate_music_state(function, episode_num, i),
                    "sfx_events": self._generate_sfx_events(function, episode_num, i),
                    "transition": self._generate_transition(function, episode_num, i, num_beats, i == num_beats - 1),
                    "retention_reason": self._select_retention_reason(function, episode_num, i)
                }

                microbeats.append(beat_data)
                current_time = beat_end

        return microbeats

    def _distribute_duration(self, total_duration: float, num_parts: int, min_part: float, max_part: float) -> list[float]:
        """Distribute total duration among parts with min/max constraints."""
        if num_parts == 1:
            return [total_duration]

        # Start with equal distribution
        base_duration = total_duration / num_parts
        durations = [base_duration] * num_parts

        # Apply min/max constraints
        for i in range(num_parts):
            if durations[i] < min_part:
                durations[i] = min_part
            elif durations[i] > max_part:
                durations[i] = max_part

        # Adjust to maintain total
        current_sum = sum(durations)
        if abs(current_sum - total_duration) > 0.01:
            # Distribute the difference
            diff = total_duration - current_sum
            for i in range(num_parts):
                if diff > 0 and durations[i] < max_part:
                    add = min(diff, max_part - durations[i])
                    durations[i] += add
                    diff -= add
                elif diff < 0 and durations[i] > min_part:
                    subtract = min(-diff, durations[i] - min_part)
                    durations[i] -= subtract
                    diff += subtract
                if abs(diff) < 0.01:
                    break

        return durations

    def _map_function_to_pattern(self, function: str) -> str:
        """Map envelope function to pattern category."""
        mapping = {
            "Hook": "hook",
            "Promise": "promise",
            "Setup/Question": "setup",
            "Escalation A": "escalation",
            "Reveal/Reward": "reveal",
            "Complication B": "complication",
            "Reversal/Peak": "reversal",
            "Cliffhanger": "cliffhanger"
        }
        return mapping.get(function, "setup")

    def _generate_narrative_goal(self, function: str, episode_num: int, beat_index: int) -> str:
        """Generate narrative goal for beat."""
        goals = {
            "Hook": [
                "Establecer mundo de lujo y exclusividad",
                "Presentar objeto de deseo como nodo narrativo",
                "Mostrar contraste de estatus inmediato"
            ],
            "Promise": [
                "Definir stakes claros del conflicto",
                "Mostrar capacidad de protagonistas para actuar",
                "Crear conexión emocional inicial"
            ],
            "Setup/Question": [
                "Plantada primera pista visual",
                "Mostrar obstáculo inicial que genera pregunta",
                "Establecer reglas del mundo que limitan acciones"
            ],
            "Escalation A": [
                "Aumentar presión externa mediante antagonismo",
                "Mostrar conflicto interno del protagonista",
                "Revelar información que cambia percepción"
            ],
            "Reveal/Reward": [
                "Revelar información clave que recompensa atención",
                "Mostrar consecuencia inmediata de descubrimiento",
                "Establecer nueva pregunta que mantiene engagement"
            ],
            "Complication B": [
                "Introducir nuevo obstáculo que complica situación",
                "Mostrar traición o engaño que rompe confianza",
                "Escalar amenaza a nivel personal o familiar"
            ],
            "Reversal/Peak": [
                "Voltear la situación con información crítica",
                "Revelar verdad oculta que cambia todo",
                "Establecer nueva dinámica de poder o relación"
            ],
            "Cliffhanger": [
                "Dejar pregunta crítica que exige resolución inmediata",
                "Mostrar elección imposible entre dos opciones válidas",
                "Amenazar lo que más vale para el protagonista"
            ]
        }

        goals_list = goals.get(function, ["Desarrollar narrativa del episodio"])
        return goals_list[beat_index % len(goals_list)]

    def _get_emotion_arc(self, function: str, beat_index: int, total_beats: int) -> str:
        """Get emotion progression for beat."""
        # Simple emotion arc based on position in segment
        position_ratio = beat_index / max(total_beats - 1, 1)

        emotion_arcs = {
            "Hook": ["tension", "curiosity", "anticipation"],
            "Promise": ["determination", "empowerment", "connection"],
            "Setup/Question": ["intrigue", "frustration", "understanding"],
            "Escalation A": ["anxiety", "torture", "shock"],
            "Reveal/Reward": ["revelation", "fear", "curiosity"],
            "Complication B": ["anger", "betrayal", "panic"],
            "Reversal/Peak": ["triumph", "awe", "hope"],
            "Cliffhanger": ["urgency", "anxiety", "fear"]
        }

        arcs = emotion_arcs.get(function, ["neutral"])
        index = min(int(position_ratio * len(arcs)), len(arcs) - 1)
        return arcs[index]

    def _generate_information_revealed(self, function: str, episode_num: int, beat_index: int) -> list[str]:
        """Generate information revealed in beat."""
        info_map = {
            "Hook": ["El mundo es de lujo y exclusividad", "Hay un objeto de deseo visible"],
            "Promise": ["Los stakes son claros y personales", "El protagonista tiene capacidad de acción"],
            "Setup/Question": ["Hay una pista que sugiere misterio", "Existe un obstáculo que no se esperaba"],
            "Escalation A": ["La presión está aumentando", "Hay conflicto interno que se muestra"],
            "Reveal/Reward": ["Se revela información clave", "Hay consecuencia inmediata visible"],
            "Complication B": ["Aparece un nuevo obstáculo", "Hay evidencia de traición o engaño"],
            "Reversal/Peak": ["Se revela información que cambia todo", "La verdad oculta sale a luz"],
            "Cliffhanger": ["Queda una pregunta crítica sin respuesta", "Se presenta una elección imposible"]
        }

        info_list = info_map.get(function, [f"Información del episodio {episode_num} beat {beat_index}"])
        # Return 1-3 items
        count = random.randint(1, min(3, len(info_list)))
        return random.sample(info_list, count)

    def _generate_information_withheld(self, function: str, episode_num: int, beat_index: int) -> list[str]:
        """Generate information withheld in beat."""
        withheld_map = {
            "Hook": ["El verdadero propósito del objeto", "Quién está detrás de la situación"],
            "Promise": ["Cuál será el costo de la acción", "Qué secretos ocultas los antagonistas"],
            "Setup/Question": ["Qué significa realmente la pista", "Quién plantó el obstáculo"],
            "Escalation A": ["Hasta dónde llegará la presión", "Qué secretos está ocultando el protagonista"],
            "Reveal/Reward": ["Qué sigue después de esta revelación", "Quién se benefició de la situación anterior"],
            "Complication B": ["Quién está detrás de esta complicación", "Qué recursos tiene el nuevo antagonista"],
            "Reversal/Peak": ["Por qué se ocultó esta información antes", "Qué consecuencias tendrá esta revelación"],
            "Cliffhanger": ["Cómo se resolverá esta situación", "Qué decidirá el protagonista"]
        }

        withheld_list = withheld_map.get(function, [f"Información futura del episodio {episode_num}"])
        count = random.randint(1, min(2, len(withheld_list)))
        return random.sample(withheld_list, count)

    def _generate_question_delta(self, function: str, episode_num: int, beat_index: int, blueprint: dict) -> str:
        """Generate question delta (change in question state)."""
        question_types = [
            "Nueva pregunta sobre el objeto de deseo",
            "Pregunta sobre lealtades y alianzas",
            "Pregunta sobre el pasado de los personajes",
            "Pregunta sobre recursos y poder disponibles",
            "Pregunta sobre consecuencias de acciones",
            "Pregunta sobre identidad verdadera",
            "Pregunta sobre lealtad y traición",
            "Pregunta sobre escape o consecuencias"
        ]

        return question_types[(episode_num + beat_index) % len(question_types)]

    def _generate_character_action(self, function: str, episode_num: int, beat_index: int) -> str:
        """Generate character action verb."""
        actions = {
            "Hook": ["observar", "descubrir", "reaccionar", "señalar", "enfrentar"],
            "Promise": ["prometer", "jurar", "demostrar", "ofrecer", "comprometerse"],
            "Setup/Question": ["investigar", "examinar", "preguntar", "seguir", "observar"],
            "Escalation A": ["confrontar", "resistir", "luchar", "defender", "atacar"],
            "Reveal/Reward": ["mostrar", "explicar", "demostrar", "entregar", "revelar"],
            "Complication B": ["sorprenderse", "enfadarse", "reaccionar", "defenderse", "atacar"],
            "Reversal/Peak": ["superar", "vencer", "revelar", "transformar", "conquistar"],
            "Cliffhanger": ["decidir", "elegir", "actuar", "reaccionar", "enfrentar"]
        }

        action_list = actions.get(function, ["actuar"])
        return action_list[beat_index % len(action_list)]

    def _generate_acting_spec(self, function: str, episode_num: int, beat_index: int) -> dict[str, Any]:
        """Generate acting specification."""
        # Microexpressions based on emotion
        microexpression_map = {
            "tension": ["pupilas_dilatadas", "mandíbula_apretada"],
            "curiosity": ["ceja_arqueada", "pupilas_dilatadas"],
            "anticipation": ["respiración_contenida", "ceja_arqueada"],
            "determination": ["mandíbula_apretada", "ceja_fruncida"],
            "empowerment": ["sonrisa_tensa", "postura_erecta"],
            "connection": ["ojos_suaves", "inclinacion_cuerpo"],
            "intrigue": ["ceja_arqueada", "inclinacion_cabeza"],
            "frustration": ["mandíbula_apretada", "respiración_irregular"],
            "understanding": ["ojos_suaves", "sonrisa_sutil"],
            "anxiety": ["pupilas_dilatadas", "respiración_acelerada"],
            "torture": ["ojos_cerrados", "expresion_dolor"],
            "shock": ["pupilas_dilatadas", "mandíbula_apretada"],
            "revelation": ["ojos_abiertos", "respiración_detenida"],
            "fear": ["pupilas_dilatadas", "sudoración_visible"],
            "curiosity": ["ceja_arqueada", "inclinacion_cabeza"],
            "anger": ["mandíbula_apretada", "ceja_fruncida", "ojos_llenos"],
            "betrayal": ["ojos_lagrimeantes", "labio_tembloroso"],
            "panic": ["respiración_acelerada", "movimientos_bruscos"],
            "triumph": ["postura_erecta", "sonrisa_amplia"],
            "awe": ["ojos_abiertos", "respiración_lenta"],
            "hope": ["sonrisa_sutil", "ojos_iluminados"],
            "urgency": ["movimientos_rapidos", "expresion_intensa"],
            "anxiety": ["paseo_inquieto", "gestos_repetitivos"]
        }

        # Determine primary emotion for this beat
        emotions = ["tension", "curiosity", "anticipation", "determination", "empowerment",
                   "connection", "intrigue", "frustration", "understanding", "anxiety",
                   "torture", "shock", "revelation", "fear", "anger", "betrayal", "panic",
                   "triumph", "awe", "hope", "urgency"]
        emotion = emotions[(episode_num + beat_index) % len(emotions)]

        microexpressions = microexpression_map.get(emotion, ["ceja_arqueada"])

        return {
            "micro_expressions": random.sample(microexpressions, min(2, len(microexpressions))),
            "eye_target": random.choice(["objeto", "personaje_especifico", "distancia", "mano"]),
            "facial_beat": random.choice(["ascendente", "descendente", "estable", "oscilante"]),
            "body_beat": random.choice(["tenso", "relajado", "preparado", "listo_para_accion"]),
            "gesture": random.choice(["señalar", "tocar", "cruzar_brazos", "amanecer_mano"]),
            "reaction": random.choice(["inmediata", "retrasada", "exagerada", "contida"]),
            "reaction_delay": random.choice(["0s", "0.5s", "1s", "1.5s"]),
            "breathing": random.choice(["normal", "acelerada", "detenida", "irregular"]),
            "emotion_base": emotion
        }

    def _generate_camera_spec(self, function: str, episode_num: int, beat_index: int, hook_category: str) -> dict[str, Any]:
        """Generate camera specification."""
        camera_specs = {
            "Hook": {
                "shot_type": "ECU",  # Extreme Close Up
                "angle": "eye_level",
                "movement": "slow_dolly_in",
                "lens": "85mm prime lens f/1.4",
                "focus_pull": "ojos → mano u objeto",
                "composition": "rule_of_thirds",
                "depth_layers": ["foreground_subject", "middle_ground", "background_context"]
            },
            "Promise": {
                "shot_type": "CU",   # Close Up
                "angle": "eye_level",
                "movement": "static_locked_off",
                "lens": "50mm prime lens f/2.8",
                "focus_pull": "rostro → objeto",
                "composition": "look_space",
                "depth_layers": ["subject", "immediate_background"]
            },
            "Setup/Question": {
                "shot_type": "MCU",  # Medium Close Up
                "angle": "low_angle",
                "movement": "rapid_truck_left",
                "lens": "35mm anamorphic lens T/4",
                "focus_pull": "fondo → primer plano",
                "composition": "leading_lines",
                "depth_layers": ["foreground", "subject", "background"]
            },
            "Escalation A": {
                "shot_type": "MS",   # Medium Shot
                "angle": "dutch_angle",
                "movement": "whip_pan",
                "lens": "24mm wide angle f/8",
                "focus_pull": "8s",
                "composition": "asymmetry",
                "depth_layers": ["foreground_elements", "subjects", "background_context"]
            },
            "Reveal/Reward": {
                "shot_type": "ECU",
                "angle": "low_angle",
                "movement": "static_locked_off",
                "lens": "85mm prime lens f/1.4",
                "focus_pull": "detalle → detalle",
                "composition": "rule_of_thirds",
                "depth_layers": ["extreme_close_subject", "immediate_context"]
            },
            "Complication B": {
                "shot_type": "CU",
                "angle": "eye_level",
                "movement": "steadicam",
                "lens": "50mm prime lens f/2.8",
                "focus_pull": "persona → persona",
                "composition": "symmetry",
                "depth_layers": ["subject1", "interaction_space", "subject2"]
            },
            "Reversal/Peak": {
                "shot_type": "ECU",
                "angle": "high_angle",
                "movement": "violent_crash_zoom_push_in",
                "lens": "85mm prime lens f/1.4",
                "focus_pull": "ojos → sien",
                "composition": "frame_within_frame",
                "depth_layers": ["extreme_subject", "narrative_context"]
            },
            "Cliffhanger": {
                "shot_type": "MS",
                "angle": "dutch_angle",
                "movement": "slow_pull_back",
                "lens": "35mm anamorphic lens T/4",
                "focus_pull": "10s",
                "composition": "leading_lines",
                "depth_layers": ["subject", "threat_direction", "environment"]
            }
        }

        specs = camera_specs.get(function, camera_specs["Setup/Question"])
        # Add some variation
        specs = specs.copy()
        if random.random() < 0.3:  # 30% chance to vary lens
            lens_variants = ["85mm prime lens f/1.4", "50mm prime lens f/2.8", "35mm anamorphic lens T/4", "24mm wide angle f/8"]
            specs["lens"] = random.choice(lens_variants)

        return specs

    def _generate_motion_spec(self, function: str, episode_num: int, beat_index: int) -> dict[str, Any]:
        """Generate motion specification."""
        motion_types = {
            "Hook": {"primary": "push_in", "secondary": ["tilt_up"], "micro": ["eyebrow_raise"], "environmental": []},
            "Promise": {"primary": "static", "secondary": [], "micro": ["lip_compression"], "environmental": []},
            "Setup/Question": {"primary": "truck_left", "secondary": ["pan_right"], "micro": ["head_tilt"], "environmental": []},
            "Escalation A": {"primary": "whip_pan", "secondary": ["zoom_out"], "micro": ["head_jerk"], "environmental": []},
            "Reveal/Reward": {"primary": "static", "secondary": [], "micro": ["blink"], "environmental": []},
            "Complication B": {"primary": "static", "secondary": [], "micro": ["jaw_clench"], "environmental": []},
            "Reversal/Peak": {"primary": "push_in", "secondary": ["tilt_down"], "micro": ["smile_expand"], "environmental": []},
            "Cliffhanger": {"primary": "pull_back", "secondary": [], "micro": ["eyebrow_furrow"], "environmental": []}
        }

        base_motion = motion_types.get(function, motion_types["Setup/Question"])
        return base_motion.copy()

    def _generate_visual_focus(self, function: str, episode_num: int, beat_index: int) -> str:
        """Generate visual focus."""
        focus_map = {
            "Hook": ["objeto_de_deseo", "rostro_protagonista", "simbolo_status"],
            "Promise": ["mano_haciendo_promesa", "ojos_decididos", "recurso_valioso"],
            "Setup/Question": ["pista_visual", "elemento_sospechoso", "entorno_revelador"],
            "Escalation A": ["rostro_antagonista", "mano_en_accion", "elemento_amenazador"],
            "Reveal/Reward": ["informacion_critica", "objeto_revelado", "expresion_facial"],
            "Complication B": ["nuevo_objetos_amenazante", "rostro_traidor", "simbolo_peligro"],
            "Reversal/Peak": ["verdad_oculta_mostrada", "expresion_de_cambio", "elemento_transformador"],
            "Cliffhanger": ["pregunta_visiblemente_abierta", "eleccion_en_mano", "momento_de_decision"]
        }

        focus_list = focus_map.get(function, ["elemento_narrativo"])
        return focus_list[beat_index % len(focus_list)]

    def _generate_sound_state(self, function: str, episode_num: int, beat_index: int) -> dict[str, Any]:
        """Generate sound state."""
        sound_states = {
            "Hook": {
                "ambience": "heavy rain on metal roof, distant thunder 40Hz",
                "room_tone": "low_hum_60hz",
                "reverb": "large_space",
                "dynamic_range": "wide"
            },
            "Promise": {
                "ambience": "light keyboard typing, distant AC hum",
                "room_tone": "neutral_room_tone",
                "reverb": "medium_space",
                "dynamic_range": "medium"
            },
            "Setup/Question": {
                "ambience": "paper rustle, pen click, distant traffic",
                "room_tone": "work_environment",
                "reverb": "small_room",
                "dynamic_range": "medium"
            },
            "Escalation A": {
                "ambience": "gold dust motes in light beam, distant sirens",
                "room_tone": "tense_environment",
                "reverb": "large_hall",
                "dynamic_range": "wide"
            },
            "Reveal/Reward": {
                "ambience": "absolute silence, then single violin note",
                "room_tone": "contemplative",
                "reverb": "dry",
                "dynamic_range": "narrow"
            },
            "Complication B": {
                "ambience": "sudden silence then low drone 30Hz, heartbeats",
                "room_tone": "threatening",
                "reverb": "reverb_heavy",
                "dynamic_range": "wide"
            },
            "Reversal/Peak": {
                "ambience": "heartbeat 60bpm, watch tick",
                "room_tone": "hopeful",
                "reverb": "medium_space",
                "dynamic_range": "medium"
            },
            "Cliffhanger": {
                "ambience": "dead silence",
                "room_tone": "tense_silence",
                "reverb": "very_dry",
                "dynamic_range": "minimal"
            }
        }

        state = sound_states.get(function, sound_states["Setup/Question"])
        return state.copy()

    def _generate_music_state(self, function: str, episode_num: int, beat_index: int) -> dict[str, Any]:
        """Generate music state."""
        music_states = {
            "Hook": {"state": "ENTER", "genre": "tension", "bpm": 60, "function": "tension_building"},
            "Promise": {"state": "BUILD", "genre": "curiosity", "bpm": 90, "function": "curiosity_building"},
            "Setup/Question": {"state": "BUILD", "genre": "suspense", "bpm": 100, "function": "suspense_building"},
            "Escalation A": {"state": "HOLD", "genre": "tension", "bpm": 120, "function": "tension_sustain"},
            "Reveal/Reward": {"state": "DROP", "genre": "revelation", "bpm": 30, "function": "revelation_sustain"},
            "Complication B": {"state": "HIT", "genre": "dread", "bpm": 40, "function": "dread_build"},
            "Reversal/Peak": {"state": "RELEASE", "genre": "triumph", "bpm": 100, "function": "triumphant_release"},
            "Cliffhanger": {"state": "EXIT", "genre": "stinger", "bpm": 0, "function": "cliffhanger_impact"}
        }

        state = music_states.get(function, music_states["Setup/Question"])
        return state.copy()

    def _generate_sfx_events(self, function: str, episode_num: int, beat_index: int) -> list[str]:
        """Generate SFX events."""
        sfx_map = {
            "Hook": ["[Foley: crisp fabric rustle sleeve silk]", "[Foley: subtle wood creak box lid]"],
            "Promise": ["[Foley: paper rustle documents]", "[Foley: pen click]"],
            "Setup/Question": ["[Foley: box vibration low hum]", "[Foley: fabric snap sudden movement]"],
            "Escalation A": ["[Foley: paper rustle bills]", "[Foley: gold clink jewelry]", "[Foley: box hinge creak]"],
            "Reveal/Reward": ["[Foley: box faint click]", "[Foley: swallowing motion audible throat]"],
            "Complication B": ["[Foley: knuckles crack]", "[Foley: fabric stretch]", "[Foley: sharp exhale]"],
            "Reversal/Peak": ["[Foley: finger snap near mic]", "[Foley: sharp inhalation]", "[Foley: fabric tear]"],
            "Cliffhanger": ["[Foley: finger snap near mic]", "[Foley: sharp inhalation Kira]", "[Foley: fabric tear]"]
        }

        sfx_list = sfx_map.get(function, ["[Foley: ambient_room_tone]"])
        count = random.randint(1, min(3, len(sfx_list)))
        return random.sample(sfx_list, count)

    def _generate_transition(self, function: str, episode_num: int, beat_index: int, total_beats: int, is_last: bool) -> str:
        """Generate transition to next beat."""
        if is_last and function == "Cliffhanger":
            return "cut_to_black"  # Special for cliffhanger ending

        transitions = {
            "Hook": ["cut", "fade", "dissolve"],
            "Promise": ["cut", "wipe", "fade"],
            "Setup/Question": ["cut", "jump_cut", "fade"],
            "Escalation A": ["cut", "whip_pan", "flash"],
            "Reveal/Reward": ["cut", "fade", "dissolve"],
            "Complication B": ["cut", "jump_cut", "wipe"],
            "Reversal/Peak": ["cut", "fade", "dissolve"],
            "Cliffhanger": ["cut_to_black", "fade_to_black", "sudden_silence"]
        }

        trans_list = transitions.get(function, ["cut"])
        return trans_list[beat_index % len(trans_list)]

    def _select_retention_reason(self, function: str, episode_num: int, beat_index: int) -> str:
        """Select retention reason based on forensics."""
        retention_reasons = {
            "Hook": ["visual_impact", "object_focus", "curiosity_gap"],
            "Promise": ["stakes_clarity", "agency", "relational_bond"],
            "Setup/Question": ["information_asymmetry", "problem_awareness", "world_building"],
            "Escalation A": ["external_pressure", "internal_conflict", "information_reward"],
            "Reveal/Reward": ["satisfaction", "consequence_awareness", "open_loop"],
            "Complication B": ["frustration", "trust_break", "survival_instinct"],
            "Reversal/Peak": ["empowerment", "wonder", "possibility"],
            "Cliffhanger": ["need_to_know", "moral_dilemma", "protective_instinct"]
        }

        reasons = retention_reasons.get(function, ["engagement_maintenance"])
        return reasons[beat_index % len(reasons)]

    def _adjust_duration(self, microbeats: list[dict], target_duration: float) -> list[dict]:
        """Adjust microbeats to hit target duration."""
        current_duration = sum(beat["duration"] for beat in microbeats)
        if current_duration == 0:
            return microbeats

        ratio = target_duration / current_duration
        if abs(ratio - 1.0) < 0.1:  # Within 10%, no adjustment needed
            return microbeats

        # Adjust each beat proportionally
        adjusted_beats = []
        for beat in microbeats:
            adjusted_beat = beat.copy()
            adjusted_beat["duration"] = beat["duration"] * ratio
            # Keep within reasonable bounds (1.5s to 15s)
            adjusted_beat["duration"] = max(1.5, min(15.0, adjusted_beat["duration"]))
            adjusted_beat["end"] = adjusted_beat["start"] + adjusted_beat["duration"]
            adjusted_beats.append(adjusted_beat)

        # Fine-tune to hit exact target
        final_duration = sum(beat["duration"] for beat in adjusted_beats)
        diff = target_duration - final_duration
        if abs(diff) > 0.1 and adjusted_beats:
            # Distribute difference across beats
            per_beat = diff / len(adjusted_beats)
            for beat in adjusted_beats:
                new_duration = beat["duration"] + per_beat
                if 1.5 <= new_duration <= 15.0:
                    beat["duration"] = new_duration
                    beat["end"] = beat["start"] + beat["duration"]

        return adjusted_beats
