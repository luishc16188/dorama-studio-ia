"""
Music Supervisor Agent - Fase 12
Selecciona, compone y supervisa la música para episodios.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *


@dataclass
class MusicCue:
    """Una cue musical específica para un momento en la escena."""
    cue_id: str
    name: str
    description: str
    music_type: str  # score, source, song, theme, sting
    genre: str  # orchestral, electronic, pop, rock, jazz, etc.
    mood: str  # tense, romantic, sad, heroic, mysterious, etc.
    instrumentation: list[str]  # instrumentos utilizados
    tempo_bpm: int | None  # pulsos por minuto
    time_signature: str  # 4/4, 3/4, 6/8, etc.
    duration: float  # en segundos
    intensity: float  # 0.0 a 1.0
    spatial_position: dict[str, float]  # left, right, center, height
    entry_point: str  # cómo entra la música (fade_in, hit, swell, etc.)
    exit_point: str  # cómo sale la música (fade_out, cut, sustain, etc.)
    lyrical_content: str | None = None  # si es una canción con letra
    copyright_status: str = "original"  # original, licensed, public_domain
    triggers: list[str] = field(default_factory=list)  # eventos que desencadenan la cue
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MusicalTheme:
    """Tema musical recurrente asociado con personajes, lugares o conceptos."""
    theme_id: str
    name: str
    description: str
    associated_with: str  # character_id, location_id, concept_id
    musical_idea: str  # descripción de la idea melódica/rítmica
    instrumentation_core: list[str]  # instrumentos principales
    variations: list[str] = field(default_factory=list)  # variaciones del tema
    usage_notes: str = ""  # notas sobre cómo y cuándo usar el tema


class MusicSupervisorAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Music Supervisor Agent que selecciona, compone y supervisa la música
    para episodios basado en análisis emocional, narrativo y de personajes.
    """

    def __init__(self):
        super().__init__("MusicSupervisorAgent")

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Supervisa la música basada en análisis de contenido y requerimientos.

        Args:
            validated_input: Diccionario con:
                - emotion_analysis: Análisis emocional por beat
                - character_arcs: Arcos de personajes
                - plot_points: Puntos importantes de la trama
                - genre: Género del contenido
                - scene_transitions: Transiciones entre escenas
                - vocal_performance: Información sobre actuación vocal
                - sound_design: Información del diseño de sonido
                - music_requirements: Requerimientos específicos de música
                - episode_structure: Estructura del episodio

        Returns:
            Diccionario con plan musical, temas, cues y recomendaciones
        """
        emotion_analysis = validated_input.get("emotion_analysis", {})
        character_arcs = validated_input.get("character_arcs", [])
        plot_points = validated_input.get("plot_points", [])
        genre = validated_input.get("genre", "romance_traicion")
        scene_transitions = validated_input.get("scene_transitions", [])
        vocal_performance = validated_input.get("vocal_performance", {})
        sound_design = validated_input.get("sound_design", {})
        music_requirements = validated_input.get("music_requirements", {})
        episode_structure = validated_input.get("episode_structure", {})

        # Identificar temas musicales necesarios
        themes = self._identify_musical_themes(character_arcs, plot_points, genre)

        # Diseñar cues musicales basadas en análisis emocional
        music_cues = self._design_music_cues(
            emotion_analysis, themes, genre, scene_transitions
        )

        # Seleccionar música fuente y canciones
        source_music = self._select_source_music(genre, emotion_analysis, plot_points)

        # Crear plan de desarrollo musical
        music_plan = self._create_music_plan(themes, music_cues, source_music, episode_structure)

        # Generar especificaciones técnicas
        technical_specs = self._get_technical_specifications(genre, music_cues)

        # Estimar presupuesto y recursos
        budget_estimate = self._estimate_music_budget(themes, music_cues, source_music)

        result = {
            "musical_themes": [self._theme_to_dict(t) for t in themes],
            "music_cues": [self._cue_to_dict(c) for c in music_cues],
            "source_music": source_music,
            "music_plan": music_plan,
            "technical_specs": technical_specs,
            "budget_estimate": budget_estimate,
            "recommendations": self._get_music_recommendations(themes, music_cues, genre)
        }

        return result

    def _identify_musical_themes(
        self,
        character_arcs: list[dict[str, Any]],
        plot_points: list[dict[str, Any]],
        genre: str
    ) -> list[MusicalTheme]:
        """Identifica temas musicales necesarios basado en arcos de personajes y puntos de trama."""
        themes = []

        # Temas para personajes principales
        for i, char_arc in enumerate(character_arcs[:3]):  # Máximo 3 temas de personajes
            char_id = char_arc.get("character_id", f"CHAR_{i:02d}")
            char_name = char_arc.get("name", f"Personaje {i+1}")

            # Determinar estilo musical basado en arco del personaje
            want = char_arc.get("psychological", {}).get("want", "")
            need = char_arc.get("psychological", {}).get("need", "")
            lie = char_arc.get("psychological", {}).get("lie", "")

            theme_style = self._determine_character_theme_style(want, need, lie, genre)

            theme = MusicalTheme(
                theme_id=f"theme_char_{char_id}",
                name=f"Tema de {char_name}",
                description=f"Tema musical que representa el arco interno de {char_name}",
                associated_with=char_id,
                musical_idea=theme_style["idea"],
                instrumentation_core=theme_style["instrumentation"],
                variations=theme_style["variations"],
                usage_notes=theme_style["usage"]
            )
            themes.append(theme)

        # Tema para la trama principal/conflicto central
        if plot_points:
            central_conflict = self._identify_central_conflict(plot_points)
            theme = MusicalTheme(
                theme_id="theme_plot",
                name="Tema de la Trama Principal",
                description="Tema que representa el conflicto central y evolución de la trama",
                associated_with="plot_central",
                musical_idea="Motivo oscilante que representa tensión y liberación",
                instrumentation_core=["cuerdas", "piano", "percusión sutil"],
                variations=["desarrollo", "clímax", "resolución"],
                usage_notes="Usar en escenas de revelación, confrontación y resolución"
            )
            themes.append(theme)

        # Tema de ubicación/ambiente si es relevante
        location_theme = self._identify_location_theme(plot_points, genre)
        if location_theme:
            themes.append(location_theme)

        return themes

    def _determine_character_theme_style(
        self,
        want: str,
        need: str,
        lie: str,
        genre: str
    ) -> dict[str, Any]:
        """Determina el estilo musical del tema de un personaje."""
        combined = (want + need + lie).lower()

        # Mapeo de rasgos psicológicos a estilos musicales
        style_mapping = {
            # Temas inocentes/vulnerables
            "innocente": {
                "idea": "Melodía simple de nota única con armonías abiertas",
                "instrumentation": ["piano", "glockenspiel", "cuerdas suaves"],
                "variations": ["juguetón", "melancólico", "esperanzado"],
                "usage": "Escenas de descubrimiento, inocencia, vulnerabilidad"
            },
            # Temas de poder/autoridad
            "poder": {
                "idea": "Motivo rítmico fuerte con intervalos de cuarta y quinta",
                "instrumentation": ["metales", "percusión", "cuerdas graves"],
                "variations": ["militar", "elegante", "ominoso"],
                "usage": "Escenas de control, autoridad, confrontación"
            },
            # Temas de amor/romance
            "amor": {
                "idea": "Melodía lírica de terceras y sextas con movimiento ondulatorio",
                "instrumentation": ["cuerdas", "piano", "arpa", "woodwinds"],
                "variations": ["pasional", "tímido", "maduro"],
                "usage": "Escenas románticas, íntimas, de conexión emocional"
            },
            # Temas de misterio/sospecha
            "misterio": {
                "idea": "Motivo cromático con armonías ambiguas y ritmos irregulares",
                "instrumentation": ["piano preparado", "cuerdas pizzicato", "instrumentos étnicos"],
                "variations": ["sospechoso", "revelador", "oscuro"],
                "usage": "Escenas de investigación, duda, revelaciones"
            },
            # Temas de conflicto interno
            "conflicto": {
                "idea": "Intervalos disonantes que se resuelven lentamente",
                "instrumentation": ["cuerdas", "piano", "metales sordos"],
                "variations": ["tenso", "liberado", "turbulento"],
                "usage": "Escenas de decisión, angustia, transformación interna"
            }
        }

        # Determinar estilo basado en rasgos predominantes
        style_key = "neutral"  # default
        if any(word in combined for word in ["inocente", "vulnerable", "puro", "sencillo"]):
            style_key = "innocente"
        elif any(word in combined for word in ["poder", "autoridad", "control", "dominio"]):
            style_key = "poder"
        elif any(word in combined for word in ["amor", "pasión", "romance", "íntimo"]):
            style_key = "amor"
        elif any(word in combined for word in ["misterio", "sospecha", "duda", "investigación"]):
            style_key = "misterio"
        elif any(word in combined for word in ["conflicto", "lucha", "angustia", "decisión"]):
            style_key = "conflicto"

        # Ajustar por género
        base_style = style_mapping.get(style_key, style_mapping["innocente"])
        genre_adjustments = {
            "thriller_domestico": {
                "instrumentation": base_style["instrumentation"] + ["sintetizador analógico"],
                "usage": base_style["usage"] + " con tensión subyacente"
            },
            "romance_traicion": {
                "instrumentation": base_style["instrumentation"] + ["cuerdas solistas"],
                "usage": base_style["usage"] + " con doblez emocional"
            },
            "horror": {
                "instrumentation": ["cuerdas graves", "metales extremos", "instrumentos no convencionales"],
                "usage": "Versión distorsionada y/o lenta del tema original"
            },
            "comedia": {
                "instrumentation": base_style["instrumentation"] + ["instrumentos juguetones"],
                "usage": base_style["usage"] + " con elementos sorpresa o exageración"
            }
        }

        adjusted_style = base_style.copy()
        if genre in genre_adjustments:
            adjustments = genre_adjustments[genre]
            for key, value in adjustments.items():
                if key in adjusted_style:
                    if isinstance(adjusted_style[key], list):
                        adjusted_style[key] = value
                    else:
                        adjusted_style[key] = f"{adjusted_style[key]} {value}"

        return adjusted_style

    def _identify_central_conflict(self, plot_points: list[dict[str, Any]]) -> str:
        """Identifica el conflicto central basado en puntos de trama."""
        if not plot_points:
            return "conflicto_general"

        # Buscar palabras clave de conflicto en los plot points
        conflict_indicators = ["traición", "revelación", "confrontación", "secreto", "mentira", "venganza"]

        conflict_score = 0
        for point in plot_points:
            point_text = str(point.get("description", "") + point.get("type", "")).lower()
            for indicator in conflict_indicators:
                if indicator in point_text:
                    conflict_score += 1

        return "conflicto_central" if conflict_score > len(plot_points) // 2 else "tema_general"

    def _identify_location_theme(
        self,
        plot_points: list[dict[str, Any]],
        genre: str
    ) -> MusicalTheme | None:
        """Identifica si necesita un tema de ubicación específica."""
        # Por simplicidad, solo crear tema de ubicación para ciertos géneros
        location_genres = ["historico", "fantasia", "ciencia_ficcion"]
        if genre in location_genres:
            return MusicalTheme(
                theme_id="theme_location",
                name="Tema de la Ubicación Principal",
                description="Tema que representa el mundo y ambiente donde ocurre la historia",
                associated_with="location_central",
                musical_idea="Textura atmosférica con instrumentos característicos del mundo",
                instrumentation_core=self._get_location_instruments(genre),
                variations=["exterior", "interior", "nocturno", "diurno"],
                usage_notes="Usar como base atmosférica en escenas de establecimiento"
            )
        return None

    def _get_location_instruments(self, genre: str) -> list[str]:
        """Obtiene instrumentos característicos para un género de ubicación."""
        instruments = {
            "historico": ["laud", "viola da gamba", "flauta traverso", "percusión histórica"],
            "fantasia": ["cítara", "duduk", "cuencos tibetanos", "arpa celta"],
            "ciencia_ficcion": ["sintetizador modular", "theremin", "instrumentos procesados", "cuerdas eléctricas"]
        }
        return instruments.get(genre, ["piano", "cuerdas"])

    def _design_music_cues(
        self,
        emotion_analysis: dict[str, Any],
        themes: list[MusicalTheme],
        genre: str,
        scene_transitions: list[dict[str, Any]]
    ) -> list[MusicCue]:
        """Diseña cues musicales basado en análisis emocional y transiciones."""
        cues = []

        # Cues basadas en análisis emocional por beat
        beats = emotion_analysis.get("beats", [])
        for i, beat in enumerate(beats):
            emotion = beat.get("dominant_emotion", "neutral")
            intensity = beat.get("intensity", 0.5)
            beat_description = beat.get("description", f"Beat {i+1}")

            # Determinar tipo y características de la cue
            cue_specs = self._get_cue_specs_for_emotion(emotion, intensity, genre)

            cue = MusicCue(
                cue_id=f"cue_beat_{i:03d}",
                name=f"Cue emocional {emotion.title()} {i+1}",
                description=f"Música para apoyar la emoción de {emotion} en: {beat_description}",
                music_type=cue_specs["type"],
                genre=cue_specs["musical_genre"],
                mood=emotion,
                instrumentation=cue_specs["instrumentation"],
                tempo_bpm=cue_specs["tempo"],
                time_signature=cue_specs["time_signature"],
                duration=10.0,  # Asumiendo beats de 10s como estándar
                intensity=intensity,
                spatial_position={"left": 0.0, "right": 0.0, "center": 1.0, "height": 0.0},
                entry_point=cue_specs["entry"],
                exit_point=cue_specs["exit"],
                triggers=[f"beat_{i}"]
            )
            cues.append(cue)

        # Cues para transiciones de escena
        for i, transition in enumerate(scene_transitions):
            transition_type = transition.get("type", "cut")
            from_emotion = transition.get("from_emotion", "neutral")
            to_emotion = transition.get("to_emotion", "neutral")

            cue = MusicCue(
                cue_id=f"cue_transition_{i:03d}",
                name=f"Transición musical {from_emotion}→{to_emotion}",
                description=f"Música para transición de escena de {from_emotion} a {to_emotion}",
                music_type="sting",
                genre="electronic_ambient",
                mood="transitional",
                instrumentation=["sintetizador", "pad atmosférico"],
                tempo_bpm=None,
                time_signature="4/4",
                duration=3.0,
                intensity=0.4,
                spatial_position={"left": -0.2, "right": 0.2, "center": 0.0, "height": 0.0},
                entry_point="swell_in",
                exit_point="fade_out",
                triggers=[f"transition_{i}"]
            )
            cues.append(cue)

        return cues

    def _get_cue_specs_for_emotion(
        self,
        emotion: str,
        intensity: float,
        genre: str
    ) -> dict[str, Any]:
        """Obtiene especificaciones musicales para una emoción dada."""
        # Base specs por emoción
        emotion_specs = {
            "miedo": {
                "type": "score",
                "musical_genre": "dark_ambient",
                "instrumentation": ["cuerdas graves", "sintetizador oscuro", "percusión metálica"],
                "tempo": 60,
                "time_signature": "5/4",
                "entry": "fade_in_slow",
                "exit": "fade_out_slow"
            },
            "ira": {
                "type": "score",
                "musical_genre": "aggressive_orchestral",
                "instrumentation": ["metales", "percusión fuerte", "cuerdas agresivas"],
                "tempo": 120,
                "time_signature": "4/4",
                "entry": "hit_strong",
                "exit": "cut_abrupt"
            },
            "tristeza": {
                "type": "score",
                "musical_genre": "melancholic_piano",
                "instrumentation": ["piano solo", "cuerdas sostenidas", "corno inglés"],
                "tempo": 50,
                "time_signature": "3/4",
                "entry": "fade_in_gentle",
                "exit": "fade_out_gentle"
            },
            "felicidad": {
                "type": "score",
                "musical_genre": "light_orchestral",
                "instrumentation": ["piano brillante", "cuerdas pizzicato", "flauta"],
                "tempo": 100,
                "time_signature": "4/4",
                "entry": "swell_bright",
                "exit": "fade_out_playful"
            },
            "sorpresa": {
                "type": "sting",
                "musical_genre": "orchestral_hit",
                "instrumentation": ["orquesta completa", "platillos", "bombo"],
                "tempo": None,
                "time_signature": "4/4",
                "entry": "sudden_hit",
                "exit": "quick_decay"
            },
            "romance": {
                "type": "score",
                "musical_genre": "romantic_strings",
                "instrumentation": ["violín solo", "viola", "chelo", "arpa"],
                "tempo": 70,
                "time_signature": "3/4",
                "entry": "fade_in_lush",
                "exit": "fade_out_warm"
            },
            "neutral": {
                "type": "score",
                "musical_genre": "minimal_ambient",
                "instrumentation": ["pad sintetizador sutil", "tonos sostenidos"],
                "tempo": 60,
                "time_signature": "4/4",
                "entry": "fade_in_barely",
                "exit": "fade_out_barely"
            }
        }

        specs = emotion_specs.get(emotion, emotion_specs["neutral"]).copy()

        # Ajustar intensidad
        if intensity > 0.7:
            # Intensidad alta: hacer más prominente
            if specs["tempo"]:
                specs["tempo"] = int(specs["tempo"] * 1.1)
            specs["instrumentation"] = [inst + " prominente" for inst in specs["instrumentation"]]
        elif intensity < 0.3:
            # Intensidad baja: hacer más sutil
            if specs["tempo"]:
                specs["tempo"] = int(specs["tempo"] * 0.9)
            specs["instrumentation"] = [inst + " muy sutil" for inst in specs["instrumentation"]]

        # Ajustar por género
        genre_adjustments = {
            "thriller_domestico": {
                "instrumentation": lambda x: [inst.replace("óscuro", "óscuro con texturas digitales") for inst in x],
                "musical_genre": lambda x: f"{x}_con_elementos_electronicos"
            },
            "romance_traicion": {
                "instrumentation": lambda x: x + ["voz etérea (sin letra)"] if "romantic" in str(x) else x,
                "musical_genre": lambda x: f"{x}_con_toque_de_desesperanza"
            },
            "horror": {
                "instrumentation": lambda x: [inst.replace("normal", "extremo o procesado") for inst in x],
                "musical_genre": lambda x: f"{x}_extremo"
            },
            "comedia": {
                "instrumentation": lambda x: [inst.replace("serio", "juguetón") for inst in x],
                "musical_genre": lambda x: f"{x}_con_ironia"
            }
        }

        if genre in genre_adjustments:
            adjustments = genre_adjustments[genre]
            for key, adjustment in adjustments.items():
                if key in specs:
                    specs[key] = adjustment(specs[key])

        return specs

    def _select_source_music(
        self,
        genre: str,
        emotion_analysis: dict[str, Any],
        plot_points: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Selecciona música fuente (canciones existentes) apropiada."""
        source_music = []

        # Determinar necesidades de música fuente basado en plot points y emociones
        needs_source = self._determine_source_music_needs(plot_points, emotion_analysis)

        if needs_source:
            # Géneros y estilos apropiados para música fuente
            genre_source_map = {
                "romance_traicion": [
                    {"style": "balada_pop_latina", "mood": "romantic", "usage": "escenas_intimas"},
                    {"style": "reggaeton_suave", "mood": "pasional", "usage": "montaje"},
                    {"style": "bolero_moderno", "mood": "melancolico", "usage": "revelacion"}
                ],
                "thriller_domestico": [
                    {"style": "electronic_dark", "mood": "tense", "usage": "investigacion"},
                    {"style": "minimal_piano", "mood": "suspense", "usage": "revelacion"},
                    {"style": "ambient_dark", "mood": "ominoso", "usage": "montaje"}
                ],
                "comedia": [
                    {"style": "pop_upbeat", "mood": "alegre", "usage": "montaje"},
                    {"style": "funk_ligero", "mood": "divertido", "usage": "transiciones"},
                    {"style": "ska_suave", "mood": "energetico", "usage": "creditos"}
                ]
            }

            source_styles = genre_source_map.get(genre, [
                {"style": "ambient_moderno", "mood": "neutral", "usage": "fondo"}
            ])

            for i, style_info in enumerate(source_styles[:2]):  # Máximo 2 selecciones
                source_music.append({
                    "source_id": f"source_{i:02d}",
                    "style": style_info["style"],
                    "mood": style_info["mood"],
                    "suggested_usage": style_info["usage"],
                    "lyrics_language": "español",
                    "vocal_style": "male" if "romantic" in style_info["mood"] else "mixed",
                    "instrumentation_typical": self._get_typical_instruments(style_info["style"]),
                    "licensing_note": "Requiere licencia de sincronización - considerar versiones cover o producción original",
                    "duration_range": "90-180 segundos",
                    "priority": "alta" if i == 0 else "media"
                })

        return source_music

    def _determine_source_music_needs(
        self,
        plot_points: list[dict[str, Any]],
        emotion_analysis: dict[str, Any]
    ) -> bool:
        """Determina si se necesita música fuente basada en contenido."""
        # Indicadores de necesidad de música fuente
        indicators = [
            "montaje", "baile", "fiesta", "creditos", "tema_principal",
            "cancion_diegetica", "bailando", "manejando", "trabajando"
        ]

        # Chequear plot points
        plot_needs_source = False
        for point in plot_points:
            point_text = str(point.get("description", "") + point.get("type", "")).lower()
            if any(indicator in point_text for indicator in indicators):
                plot_needs_source = True
                break

        # Chequear análisis emocional para momentos que se benefician de canciones
        beats = emotion_analysis.get("beats", [])
        emotion_needs_source = False
        romantic_or_energetic_beats = 0
        for beat in beats:
            emotion = beat.get("dominant_emotion", "")
            if emotion in ["felicidad", "romance", "pasión", "excitacion", "alegría"]:
                romantic_or_energetic_beats += 1

        if romantic_or_energetic_beats >= len(beats) * 0.3:  # 30% o más de beats emocionalmente cargados
            emotion_needs_source = True

        return plot_needs_source or emotion_needs_source

    def _get_typical_instruments(self, style: str) -> list[str]:
        """Obtiene instrumentos típicos para un estilo de música fuente."""
        instruments_map = {
            "balada_pop_latina": ["piano", "cuerdas", "percusión ligera", "bajo eléctrico"],
            "reggaeton_suave": ["sintetizador", "caja de ritmos", "bajo", "vocales"],
            "bolero_moderno": ["guitarra clásica", "cuerdas", "piano", "percusión ligera"],
            "electronic_dark": ["sintetizador analógico", "caja de ritmos", "bajo sintético"],
            "minimal_piano": ["piano solo", "cuerdas muy sostenidas"],
            "ambient_dark": ["texturas sintetizador", "field recordings", "procesamiento extremo"],
            "pop_upbeat": ["guitarra eléctrica", "bajo", "batería", "teclados", "cuerdas"],
            "funk_ligero": ["guitarra funk", "bajo slap", "batería sincopada", "metales"],
            "ska_suave": ["guitarra ska", "bajo walking", "batería", "metales", "órgano"]
        }
        return instruments_map.get(style, ["guitarra", "bajo", "batería", "teclados"])

    def _create_music_plan(
        self,
        themes: list[MusicalTheme],
        music_cues: list[MusicCue],
        source_music: list[dict[str, Any]],
        episode_structure: dict[str, Any]
    ) -> dict[str, Any]:
        """Crea un plan de desarrollo musical para el episodio."""
        total_runtime = episode_structure.get("total_runtime_seconds", 90)  # Default 90s para vertical video

        # Calcular distribución de música
        score_duration = sum(cue.duration for cue in music_cues if cue.music_type == "score")
        sting_duration = sum(cue.duration for cue in music_cues if cue.music_type == "sting")
        source_duration = sum(float(item.get("duration_range", "120").split("-")[0]) for item in source_music if isinstance(item.get("duration_range"), str))

        # Asegurar que no exceda el runtime
        music_duration = min(score_duration + sting_duration + source_duration, total_runtime * 0.7)  # Máximo 70% de música

        plan = {
            "episode_runtime": total_runtime,
            "music_distribution": {
                "original_score": {
                    "duration_estimate": round(score_duration, 1),
                    "percentage": round((score_duration / max(music_duration, 1)) * 100, 1),
                    "cues_count": len([c for c in music_cues if c.music_type == "score"]),
                    "description": "Música compuesta originalmente para apoyar emociones y narrativa"
                },
                "stings_and_hits": {
                    "duration_estimate": round(sting_duration, 1),
                    "percentage": round((sting_duration / max(music_duration, 1)) * 100, 1),
                    "cues_count": len([c for c in music_cues if c.music_type == "sting"]),
                    "description": "Impactos musicales breves para enfatizar momentos clave"
                },
                "source_music": {
                    "duration_estimate": round(source_duration, 1),
                    "percentage": round((source_duration / max(music_duration, 1)) * 100, 1),
                    "tracks_count": len(source_music),
                    "description": "Canciones existentes o música fuente para escenas específicas"
                }
            },
            "development_timeline": {
                "theme_composition": "Días 1-2: Composición y desarrollo de temas musicales principales",
                "cue_spotting": "Día 3: Spotting session para determinar lugares exactos de cada cue",
                "score_writing": "Días 4-7: Composición y orquestación de cues musicales",
                "mockup_review": "Día 8: Revisión de maquets con equipo creativo",
                "final_production": "Días 9-10: Producción final, mezcla y masterización",
                "source_music_clearance": "Días 1-5: Búsqueda y clearance de música fuente (paralelo)"
            },
            "delivery_format": {
                "stems": ["cuerdas", "metales", "ritmo", "armonia", "vocales_sinteticas"],
                "mix_format": "Stereo 24-bit/48kHz WAV",
                "delivery_timing": "Entrega final 24 horas antes del audio mix final"
            }
        }

        return plan

    def _get_technical_specifications(
        self,
        genre: str,
        music_cues: list[MusicCue]
    ) -> dict[str, Any]:
        """Obtiene especificaciones técnicas para la producción musical."""
        # Determinar complejidad orquestal basada en cues y género
        orchestral_layers = self._estimate_orchestral_layers(music_cues, genre)

        specs = {
            "recording": {
                "sample_rate": "48000 Hz",
                "bit_depth": "24-bit",
                "format": "WAV (Broadcast Wave Format)",
                "bit_rate": "2304 kbps",
                "channels": "Stereo (L,R) o 5.1 Surround si aplica"
            },
            "orchestration": {
                "estimated_layers": orchestral_layers,
                "recording_approach": self._get_recording_approach(genre, orchestral_layers),
                "session_length_estimate": f"{max(2, orchestral_layers // 4)} horas por sesión",
                "musicians_needed": self._estimate_musicians_needed(orchestral_layers, genre)
            },
            "production": {
                "daw_recommended": ["Pro Tools", "Logic Pro", "Cubase"],
                "virtual_instruments": self._get_recommended_virtual_instruments(genre),
                "processing_chain": [
                    "1. Gain staging y limpieza",
                    "2. Ecualización quirúrgica por sección",
                    "3. Compresión de grupo por familia instrumental",
                    "4. Reverb y espacialización según ambiente",
                    "5. Saturación armónica selectiva para calor",
                    "6. Limiter de pico para loudness estándar"
                ]
            },
            "delivery": {
                "file_naming": "MS_SceneID_CueType_Description_v01.wav",
                "metadata_required": ["Composer", "Cue Description", "Timing", "Genre", "Mood"],
                "version_control": "Semantic versioning (v01, v02, etc.) con cambios significativos"
            }
        }

        return specs

    def _estimate_orchestral_layers(
        self,
        music_cues: list[MusicCue],
        genre: str
    ) -> int:
        """Estima el número de capas orquestales necesarias."""
        base_layers = 4  # Cuerdas, metales, madera, ritmo

        # Incrementar por complejidad de cues
        unique_instruments = set()
        for cue in music_cues:
            unique_instruments.update(cue.instrumentation)

        instrument_bonus = min(len(unique_instruments) // 3, 4)  # Máximo +4 por instrumentos únicos

        # Ajustar por género
        genre_multiplier = {
            "thriller_domestico": 1.2,
            "romance_traicion": 1.0,
            "accion": 1.5,
            "fantasia": 1.3,
            "comedia": 0.9
        }.get(genre, 1.0)

        total_layers = int((base_layers + instrument_bonus) * genre_multiplier)
        return min(max(total_layers, 2), 16)  # Entre 2 y 16 capas

    def _get_recording_approach(
        self,
        genre: str,
        layers: int
    ) -> str:
        """Obtiene el enfoque de grabación basado en género y capas."""
        if layers <= 4:
            approach = "Grabación de sección completa o overdubbing mínimo"
        elif layers <= 8:
            approach = "Grabación por familias instrumentales (cuerdas, metales, ritmo)"
        else:
            approach = "Grabación individual o por secciones pequeñas con overdubbing extensivo"

        genre_modifiers = {
            "thriller_domestico": "con énfasis en texturas oscuras y procesamiento",
            "romance_traicion": "con enfoque en calidez y intimidad",
            "horror": "con técnicas de grabación no convencionales",
            "comedia": "con sensación en vivo y espontánea"
        }

        modifier = genre_modifiers.get(genre, "")
        return f"{approach} {modifier}".strip()

    def _estimate_musicians_needed(
        self,
        layers: int,
        genre: str
    ) -> dict[str, int]:
        """Estima el número de músicos necesarios."""
        # Estimación básica por familia instrumental
        base_orchestra = {
            "cuerdas": min(8, layers // 2),  # Violines, violas, chelos, contrabajos
            "metales": min(4, layers // 4),  # Trompetas, trombones, cornos
            "maderas": min(4, layers // 4),  # Flautas, oboes, clarinetes, fagotes
            "ritmo": min(2, layers // 8),    # Percusión, bajo, piano/guitarra
            "vocales": min(2, layers // 8)   # Vocales sintéticas o étnicas si aplica
        }

        # Ajustar por género
        if genre == "thriller_domestico":
            base_orchestra["cuerdas"] = max(4, base_orchestra["cuerdas"] - 2)
            base_orchestra["metales"] = max(2, base_orchestra["metales"])
            base_orchestra["ritmo"] = max(2, base_orchestra["ritmo"])  # Más énfasis en ritmo electrónico
        elif genre == "romance_traicion":
            base_orchestra["cuerdas"] = max(6, base_orchestra["cuerdas"])  # Más cuerdas para calidez
            base_orchestra["metales"] = max(2, base_orchestra["metales"] - 2)  # Metales más sutiles
        elif genre == "comedia":
            base_orchestra["ritmo"] = max(2, base_orchestra["ritmo"] + 2)  # Más énfasis en ritmo

        return {k: v for k, v in base_orchestra.items() if v > 0}

    def _get_recommended_virtual_instruments(self, genre: str) -> list[str]:
        """Obtiene instrumentos virtuales recomendados."""
        base_vsti = [
            "Spitfire Audio - BBC Symphony Orchestra (cuerdas)",
            "Native Instruments - Kontakt (bibliotecas diversas)",
            "EastWest - Quantum Leap Pianos",
            "Spectrasonics - Omnisphere (texturas y sintetizador)",
            "Toontrack - EZdrummer 3 (batería)"
        ]

        genre_specific = {
            "thriller_domestico": [
                "Output - Analog Strings",
                "Heavyocity - Damage",
                "Soundtoys - Little AlterBoy (vocales procesados)"
            ],
            "romance_traicion": [
                "Spitfire Audio - Luminous Strings",
                "8dio - Lacrimosa Choir",
                "Spectrasonics - Trilian (bajo)"
            ],
            "horror": [
                "Cinesamples - Horror Bouquet",
                "Soundiron - Venom",
                "Audiobro - LA Scoring Strings (para efectos extremos)"
            ],
            "comedia": [
                "EastWest - Hollywood Orchestra",
                "Best Service - Chris Hein Winds",
                "Native Instruments - Scarbee Bass"
            ]
        }

        result = base_vsti.copy()
        if genre in genre_specific:
            result.extend(genre_specific[genre])

        return result

    def _estimate_music_budget(
        self,
        themes: list[MusicalTheme],
        music_cues: list[MusicCue],
        source_music: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Estima el presupuesto de producción musical."""
        # Costos base
        composer_fee_per_minute = 150  # USD por minuto de música compuesta
        orchestrator_fee_per_minute = 50
        recording_session_hourly = 200  # USD/hora para sesión de grabación
        mixing_hourly = 150
        music_editor_hourly = 75

        # Calcular minutos de música
        score_minutes = sum(cue.duration for cue in music_cues if cue.music_type == "score") / 60
        sting_minutes = sum(cue.duration for cue in music_cues if cue.music_type == "sting") / 60
        total_composed_minutes = score_minutes + sting_minutes

        # Tiempo de producción
        composing_hours = total_composed_minutes * 2  # 2 horas por minuto compuesto
        orchestrating_hours = total_composed_minutes * 0.5
        recording_hours = max(2, total_composed_minutes * 0.3)  # Sesiones de grabación
        mixing_hours = 3  # Tiempo base de mezcla
        editing_hours = total_composed_minutes * 0.2

        # Costos de música fuente (licencias)
        source_music_cost = len(source_music) * 1500  # Estimado promedio por licencia

        # Gastos varios
        miscellaneous = (composing_hours * composer_fee_per_minute +
                        orchestrating_hours * orchestrator_fee_per_minute +
                        recording_hours * recording_session_hourly +
                        mixing_hours * mixing_hourly +
                        editing_hours * music_editor_hourly) * 0.1  # 10% para gastos varios

        total_cost = (
            composing_hours * composer_fee_per_minute +
            orchestrating_hours * orchestrator_fee_per_minute +
            recording_hours * recording_session_hourly +
            mixing_hours * mixing_hourly +
            editing_hours * music_editor_hourly +
            source_music_cost +
            miscellaneous
        )

        return {
            "composing": {
                "hours": round(composing_hours, 1),
                "cost": round(composing_hours * composer_fee_per_minute, 2)
            },
            "orchestrating": {
                "hours": round(orchestrating_hours, 1),
                "cost": round(orchestrating_hours * orchestrator_fee_per_minute, 2)
            },
            "recording": {
                "hours": round(recording_hours, 1),
                "cost": round(recording_hours * recording_session_hourly, 2)
            },
            "mixing": {
                "hours": round(mixing_hours, 1),
                "cost": round(mixing_hours * mixing_hourly, 2)
            },
            "editing": {
                "hours": round(editing_hours, 1),
                "cost": round(editing_hours * music_editor_hourly, 2)
            },
            "source_music_licensing": {
                "tracks": len(source_music),
                "cost": round(source_music_cost, 2)
            },
            "miscellaneous": {
                "cost": round(miscellaneous, 2)
            },
            "total_hours": round(composing_hours + orchestrating_hours + recording_hours +
                              mixing_hours + editing_hours, 1),
            "total_cost_usd": round(total_cost, 2),
            "cost_per_minute": round(total_cost / max(total_composed_minutes, 0.1), 2)
        }

    def _get_music_recommendations(
        self,
        themes: list[MusicalTheme],
        music_cues: list[MusicCue],
        genre: str
    ) -> list[str]:
        """Obtiene recomendaciones generales de música."""
        recommendations = [
            "Desarrollar un motivo musical central que pueda transformarse a lo largo de la historia",
            "Crear paleta sonora consistente que evolucione con los arcos de los personajes",
            "Usar el silencio como elemento musical activo en momentos de tensión",
            "Considerar versiones alternativas de temas importantes para diferentes contextos emocionales",
            "Documentar claramente el uso y variaciones de cada tema para consistencia"
        ]

        # Recomendaciones específicas por número de temas
        if len(themes) > 3:
            recommendations.append("Considerar combinar temas relacionados para evitar sobrecarga temática")
        elif len(themes) < 2:
            recommendations.append("Explorar oportunidades para desarrollar temas secundarios para profundidad")

        # Recomendaciones específicas por género
        if genre == "thriller_domestico":
            recommendations.extend([
                "Explorar contrastes entre lo doméstico familiar y lo amenazante mediante procesamiento de sonido",
                "Considerar uso de instrumentos preparados o no convencionales para texturas únicas",
                "Crear paleta de sonidos que puedan ser tanto diegéticos como no diegéticos"
            ])
        elif genre == "romance_traicion":
            recommendations.extend([
                "Desarrollar temas que reflejen la dualidad entre amor aparente y sentimientos ocultos",
                "Usar armonías ambiguas que sugieran tanto felicidad como peligro inminente",
                "Considerar versiones instrumentales de canciones populares con letra modificada"
            ])
        elif genre == "horror":
            recommendations.extend([
                "Experimentar con rangos extremos de frecuencia (infrasonido y ultrasonido)",
                "Crear biblioteca de sonidos orgánicos distorsionados para uso musical",
                "Considerar música que juegue con expectativas y las subvierta"
            ])
        elif genre == "comedia":
            recommendations.extend([
                "Usar contraste entre expectativa musical y realidad cómica",
                "Considerar estilos musicales exagerados o pastiche para efecto cómico",
                "Jugar con timing musical para crear momentos de anticipación y sorpresa"
            ])

        return recommendations

    def _theme_to_dict(self, theme: MusicalTheme) -> dict[str, Any]:
        """Convierte un MusicalTheme a diccionario para serialización."""
        return {
            "theme_id": theme.theme_id,
            "name": theme.name,
            "description": theme.description,
            "associated_with": theme.associated_with,
            "musical_idea": theme.musical_idea,
            "instrumentation_core": theme.instrumentation_core,
            "variations": theme.variations,
            "usage_notes": theme.usage_notes
        }

    def _cue_to_dict(self, cue: MusicCue) -> dict[str, Any]:
        """Convierte un MusicCue a diccionario para serialización."""
        return {
            "cue_id": cue.cue_id,
            "name": cue.name,
            "description": cue.description,
            "music_type": cue.music_type,
            "genre": cue.genre,
            "mood": cue.mood,
            "instrumentation": cue.instrumentation,
            "tempo_bpm": cue.tempo_bpm,
            "time_signature": cue.time_signature,
            "duration": cue.duration,
            "intensity": cue.intensity,
            "spatial_position": cue.spatial_position,
            "entry_point": cue.entry_point,
            "exit_point": cue.exit_point,
            "lyrical_content": cue.lyrical_content,
            "copyright_status": cue.copyright_status,
            "triggers": cue.triggers,
            "metadata": cue.metadata
        }

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the music supervisor agent."""
        return self.process(input_data)
