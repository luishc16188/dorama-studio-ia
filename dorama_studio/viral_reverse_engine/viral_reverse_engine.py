"""
Viral Reverse Engineer AI - Agente que analiza cualquier video exitoso para extraer:
HOOK: Primer segundo, primera imagen, primera frase, primer conflicto.
NARRATIVA: Problema, deseo, dolor, misterio, recompensa.
PRODUCCIÓN: Cámara, edición, música, texto, ritmo.
FINAL: Cliffhanger, pregunta abierta, deseo de continuar.
Guarda aprendizajes para mejorar futuras generaciones.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class HookAnalysis:
    """Análisis del hook de un video exitoso."""
    first_second_visual: str = ""  # Qué se ve en el primer segundo
    first_second_text: str = ""    # Qué texto aparece (si hay)
    first_second_audio: str = ""   # Qué se oye en el primer segundo
    first_frame_image: str = ""    # Descripción de la primera imagen
    first_phrase: str = ""         # Primera frase hablada o mostrada
    first_conflict: str = ""       # Primer indicio de conflicto o tensión
    hook_score: float = 0.0        # Score de efectividad del hook (0-100)
    retention_impact: float = 0.0  # Impacto estimado en retención inicial (0-100)

@dataclass
class NarrativeAnalysis:
    """Análisis de la narrativa de un video exitoso."""
    problem: str = ""              # Problema presentado o planteado
    desire: str = ""               # Deseo del protagonista o del espectador
    pain: str = ""                 # Dolor o sufrimiento mostrado
    mystery: str = ""              # Elemento de misterio o pregunta planteada
    reward: str = ""               # Recompensa o resolución ofrecida
    narrative_coherence: float = 0.0  # Coherencia de la narrativa (0-100)
    emotional_journey: list[str] = field(default_factory=list)  # Viaje emocional observado

@dataclass
class ProductionAnalysis:
    """Análisis de los elementos de producción de un video exitoso."""
    camera_work: list[str] = field(default_factory=list)  # Tipos de planos, movimientos
    editing_style: list[str] = field(default_factory=list)  # Estilo de edición, cortes, ritmo
    music_sound: list[str] = field(default_factory=list)  # Uso de música, efectos de sonido
    text_overlay: list[str] = field(default_factory=list)  # Uso de texto en pantalla
    pacing_rhythm: list[str] = field(default_factory=list)  # Ritmo y cadence
    production_score: float = 0.0  # Score general de producción (0-100)

@dataclass
class CliffhangerAnalysis:
    """Análisis del final/cliffhanger de un video exitoso."""
    cliffhanger_type: str = ""     # Tipo de cliffhanger (revelación, pregunta, etc.)
    cliffhanger_text: str = ""     # Texto exacto del cliffhanger (si aplica)
    open_question: str = ""        # Pregunta abierta que deja el video
    continuation_desire: float = 0.0  # Fuerza del deseo de continuar (0-100)
    satisfaction_level: float = 0.0  # Nivel de satisfacción proporcionada (0-100)
    frustration_level: float = 0.0  # Nivel de frustración saludable generada (0-100)

@dataclass
class ViralAnalysisResult:
    """Resultado completo del análisis viral de un video."""
    video_id: str
    platform: str
    title: str
    duration_seconds: float
    hook_analysis: HookAnalysis = field(default_factory=HookAnalysis)
    narrative_analysis: NarrativeAnalysis = field(default_factory=NarrativeAnalysis)
    production_analysis: ProductionAnalysis = field(default_factory=ProductionAnalysis)
    cliffhanger_analysis: CliffhangerAnalysis = field(default_factory=CliffhangerAnalysis)
    viral_score: float = 0.0       # Score general de viralidad (0-100)
    learnings: list[str] = field(default_factory=list)  # Lecciones extraídas para mejorar
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.8

class ViralReverseEngineerAI:
    """
    Viral Reverse Engineer AI que analiza cualquier video exitoso para extraer sus componentes
    clave y guardar aprendizajes para mejorar futuras generaciones de contenido.
    """

    def __init__(self):
        self.analysis_cache = {}  # Cache de análisis realizados
        self.learnings_database = []  # Base de conocimientos aprendidos
        self.hook_patterns = defaultdict(int)  # Patrones de hook exitosos
        self.narrative_patterns = defaultdict(int)  # Patrones narrativos exitosos
        self.production_patterns = defaultdict(int)  # Patrones de producción exitosos
        self.cliffhanger_patterns = defaultdict(int)  # Patrones de cliffhanger exitosos

        logger.info("ViralReverseEngineerAI initialized")

    def analyze_viral_video(
        self,
        video_data: dict[str, Any],
        platform: str = "unknown"
    ) -> ViralAnalysisResult:
        """
        Analiza un video exitoso para extraer sus componentes virales.

        Args:
            video_data: Diccionario con información del video (puede incluir transcript,
                       descripciones de escenas, métricas de engagement, etc.)
            platform: Plataforma donde se encontró el video (tiktok, youtube, instagram, etc.)

        Returns:
            ViralAnalysisResult con el análisis completo
        """
        logger.info(f"Analyzing viral video from {platform}: {video_data.get('title', 'Unknown')}")

        # Generar ID único para el video
        video_id = self._generate_video_id(video_data, platform)

        # Verificar si ya lo analizamos recientemente
        cache_key = f"{video_id}_{platform}"
        if cache_key in self.analysis_cache:
            cached_result, timestamp = self.analysis_cache[cache_key]
            if (datetime.utcnow() - timestamp).seconds < 3600:  # 1 hora de cache
                logger.info(f"Returning cached analysis for {video_id}")
                return cached_result

        # Extraer componentes del análisis
        hook_analysis = self._analyze_hook(video_data)
        narrative_analysis = self._analyze_narrative(video_data)
        production_analysis = self._analyze_production(video_data)
        cliffhanger_analysis = self._analyze_cliffhanger(video_data)

        # Calcular score general de viralidad
        viral_score = self._calculate_viral_score(
            hook_analysis, narrative_analysis, production_analysis, cliffhanger_analysis
        )

        # Extraer aprendizajes
        learnings = self._extract_learnings(
            hook_analysis, narrative_analysis, production_analysis, cliffhanger_analysis, video_data
        )

        # Actualizar bases de conocimiento
        self._update_knowledge_base(
            hook_analysis, narrative_analysis, production_analysis, cliffhanger_analysis
        )

        # Crear resultado
        result = ViralAnalysisResult(
            video_id=video_id,
            platform=platform,
            title=video_data.get("title", "Unknown Title"),
            duration_seconds=video_data.get("duration_seconds", 0.0),
            hook_analysis=hook_analysis,
            narrative_analysis=narrative_analysis,
            production_analysis=production_analysis,
            cliffhanger_analysis=cliffhanger_analysis,
            viral_score=viral_score,
            learnings=learnings,
            confidence=0.85  # Confianza basada en calidad de los datos de entrada
        )

        # Guardar en cache
        self.analysis_cache[cache_key] = (result, datetime.utcnow())

        # Limpiar cache si es muy grande (más de 1000 entradas)
        if len(self.analysis_cache) > 1000:
            # Eliminar las entradas más antiguas
            sorted_cache = sorted(
                self.analysis_cache.items(),
                key=lambda x: x[1][1]  # Ordenar por timestamp
            )
            self.analysis_cache = dict(sorted_cache[-500:])  # Mantener las 500 más recientes

        logger.info(f"Viral analysis complete for {video_id}. Viral score: {viral_score:.1f}/100")
        return result

    def _generate_video_id(self, video_data: dict[str, Any], platform: str) -> str:
        """Genera un ID único para un video basado en sus características."""
        # Usar título, plataforma y duración si están disponibles
        base_string = f"{platform}_{video_data.get('title', '')}_{video_data.get('duration_seconds', 0)}"
        # Si hay ID específico de la plataforma, usarlo
        if 'video_id' in video_data:
            base_string = f"{video_data['video_id']}_{platform}"
        elif 'url' in video_data:
            base_string = f"{video_data['url']}_{platform}"

        return hashlib.md5(base_string.encode()).hexdigest()[:12]

    def _analyze_hook(self, video_data: dict[str, Any]) -> HookAnalysis:
        """Analiza el hook de los primeros segundos del video."""
        hook = HookAnalysis()

        # Extraer información disponible sobre los primeros momentos
        # En una implementación real, esto vendría de análisis de frames, transcripción de audio, etc.

        # Primer segundo visual
        hook.first_second_visual = video_data.get(
            "first_second_visual",
            video_data.get("opening_shot", "ECU on eyes or hands - macro shot for impact")
        )

        # Primer segundo textual
        hook.first_second_text = video_data.get(
            "first_second_text",
            ""
        )

        # Primer segundo de audio
        hook.first_second_audio = video_data.get(
            "first_second_audio",
            video_data.get("opening_audio", "sub-bass 40Hz pulse or silence")
        )

        # Primera imagen significativa
        hook.first_frame_image = video_data.get(
            "first_frame_image",
            video_data.get("key_visual_element", "object of significance or character introduction")
        )

        # Primera frase
        hook.first_phrase = video_data.get(
            "first_phrase",
            video_data.get("opening_line", "")
        )

        # Primer conflicto o tensión
        hook.first_conflict = video_data.get(
            "first_conflict",
            video_data.get("initial_tension", "hint of mystery or problem")
        )

        # Calcular score del hook basado en elementos conocidos de efectividad
        hook.hook_score = self._calculate_hook_score(hook)
        hook.retention_impact = self._calculate_retention_impact(hook)

        return hook

    def _calculate_hook_score(self, hook: HookAnalysis) -> float:
        """Calcula el score de efectividad del hook basado en mejores prácticas."""
        score = 30.0  # Base score

        # Elementos que hacen un hook efectivo

        # Visual impactante en los primeros 2 segundos
        if any(word in hook.first_second_visual.lower() for word in
               ["ecu", "macro", "close-up", "eyes", "hands", "object", "ring", "letter", "photo"]):
            score += 20

        # Text on screen in first seconds
        if hook.first_second_text and len(hook.first_second_text.strip()) > 0:
            score += 15

        # Distinctive audio signature
        if any(word in hook.first_second_audio.lower() for word in
               ["sub-bass", "40hz", "heartbeat", "silence", "pulse"]):
            score += 15

        # Clear visual proposition
        if any(word in hook.first_frame_image.lower() for word in
               ["ring", "letter", "photo", "document", "weapon", "symbol"]):
            score += 15

        # Intriguing first phrase
        if hook.first_phrase:
            # Preguntas, declaraciones misteriosas, promesas
            if any(word in hook.first_phrase.lower() for word in
                   ["¿", "?", " secreto", "verdad", "mentira", "promesa", "jamás", "nunca"]):
                score += 20
            # Declaraciones fuertes o contradictorias
            elif any(word in hook.first_phrase.lower() for word in
                     ["nunca", "siempre", "jamás", "imposible", "no puede ser"]):
                score += 15

        # Early conflict or tension
        if hook.first_conflict and len(hook.first_conflict.strip()) > 0:
            score += 15

        # Penalizar elementos que debilitan el hook
        if any(word in hook.first_second_visual.lower() for word in
               ["talking head", "estatic", "boring", "text only"]):
            score -= 15

        if hook.first_second_text and len(hook.first_second_text.split()) > 15:
            score -= 10  # Demasiado texto al inicio

        return max(0.0, min(100.0, score))

    def _calculate_retention_impact(self, hook: HookAnalysis) -> float:
        """Calcula el impacto estimado del hook en la retención inicial."""
        # Basado en investigaciones de plataformas: los primeros 3 segundos son críticos
        base_impact = 40.0

        # Bonus por elementos que se sabe que aumentan retención inicial
        if hook.hook_score > 80:
            base_impact += 30
        elif hook.hook_score > 60:
            base_impact += 20
        elif hook.hook_score > 40:
            base_impact += 10

        # Penalty por hooks débiles
        if hook.hook_score < 30:
            base_impact -= 20

        return max(0.0, min(100.0, base_impact))

    def _analyze_narrative(self, video_data: dict[str, Any]) -> NarrativeAnalysis:
        """Analiza la narrativa central del video."""
        narrative = NarrativeAnalysis()

        # Extraer o inferir los elementos narrativos
        narrative.problem = video_data.get(
            "problem",
            self._infer_problem_from_data(video_data)
        )

        narrative.desire = video_data.get(
            "desire",
            self._infer_desire_from_data(video_data)
        )

        narrative.pain = video_data.get(
            "pain",
            self._infer_pain_from_data(video_data)
        )

        narrative.mystery = video_data.get(
            "mystery",
            self._infer_mystery_from_data(video_data)
        )

        narrative.reward = video_data.get(
            "reward",
            self._infer_reward_from_data(video_data)
        )

        # Calcular coherencia narrativa
        narrative.narrative_coherence = self._calculate_narrative_coherence(narrative)

        # Extraer viaje emocional
        narrative.emotional_journey = video_data.get(
            "emotional_journey",
            self._infer_emotional_journey(video_data)
        )

        return narrative

    def _infer_problem_from_data(self, video_data: dict[str, Any]) -> str:
        """Inferir el problema presentado a partir de los datos disponibles."""
        # Buscar en campos comunes donde se podría mencionar el problema
        problem_sources = [
            video_data.get("description", ""),
            video_data.get("synopsis", ""),
            video_data.get("conflict", ""),
            video_data.get("problem_statement", ""),
            " ".join(video_data.get("tags", [])) if isinstance(video_data.get("tags"), list) else ""
        ]

        # Palabras clave que indican un problema
        problem_indicators = [
            "problema", "problema", "conflicto", "amenaza", "peligro", "crisis",
            "problema", "trouble", "issue", "challenge", "obstacle", "dilema"
        ]

        # Buscar en las fuentes
        combined_text = " ".join(problem_sources).lower()
        for indicator in problem_indicators:
            if indicator in combined_text:
                # Extraer una frase alrededor de la palabra clave
                # En implementación real sería más sofisticado
                return f"Problema relacionado con {indicator}"

        # Si no se encuentra explícitamente, inferir de otros elementos
        if video_data.get("genre") == "thriller_misterio":
            return "Misterio o crimen que necesita ser resuelto"
        elif video_data.get("genre") == "romance_traicion":
            return "Traición o engaño que amenaza una relación"
        elif video_data.get("genre") == "fantasia_epica":
            return "Amenaza al reino o mundo que requiere acción heroica"
        else:
            return "Conflicto central que impulsa la narrativa"

    def _infer_desire_from_data(self, video_data: dict[str, Any]) -> str:
        """Inferir el deseo del protagonista o del video."""
        desire_sources = [
            video_data.get("desire", ""),
            video_data.get("goal", ""),
            video_data.get("motivation", ""),
            video_data.get("want", "")
        ]

        combined_text = " ".join(desire_sources).lower()

        # Buscar deseos comunes
        if any(word in combined_text for word in ["verdad", "justicia", "libertad"]):
            return "Descubrir la verdad o lograr justicia"
        elif any(word in combined_text for word in ["amor", "conexión", "relación"]):
            return "Encontrar o mantener una relación significativa"
        elif any(word in combined_text for word in ["poder", "control", "seguridad"]):
            return "Obtener poder, control o seguridad"
        elif any(word in combined_text for word in ["sobrevivir", "escape", "liberación"]):
            return "Sobrevivir o alcanzar la libertad"
        else:
            return "Lograr un objetivo significativo o superar un obstáculo"

    def _infer_pain_from_data(self, video_data: dict[str, Any]) -> str:
        """Inferir el dolor o sufrimiento presentado."""
        pain_sources = [
            video_data.get("pain", ""),
            video_data.get("suffering", ""),
            video_data.get("struggle", ""),
            video_data.get("conflict", "")
        ]

        combined_text = " ".join(pain_sources).lower()

        if any(word in combined_text for word in ["pérdida", "pérdida", "muerte", "separación"]):
            return "Dolor por pérdida o separación"
        elif any(word in combined_text for word in ["engañ", "traición", "mentira"]):
            return "Dolor por traición o engaño"
        elif any(word in combined_text for word in ["injusticia", "opresión", "abuso"]):
            return "Dolor por injusticia o opresión"
        elif any(word in combined_text for word in ["miedo", "temor", "ansiedad"]):
            return "Dolor por miedo o ansiedad"
        else:
            return "Dolor emocional o sufrimiento interno"

    def _infer_mystery_from_data(self, video_data: dict[str, Any]) -> str:
        """Inferir el elemento de misterio o pregunta planteada."""
        mystery_sources = [
            video_data.get("mystery", ""),
            video_data.get("question", ""),
            video_data.get("enigma", ""),
            video_data.get("secret", "")
        ]

        combined_text = " ".join(mystery_sources).lower()

        if any(word in combined_text for word in ["quién", "qué", "cómo", "cuándo", "dónde", "por qué"]):
            return "Pregunta sin respuesta que impulsa la investigación"
        elif any(word in combined_text for word in ["secreto", "oculto", "misterio", "desconocido"]):
            return "Secreto o información oculta que necesita ser descubierta"
        elif any(word in combined_text for word in ["identidad", "verdadero yo", "pasado"]):
            return "Misterio alrededor de la identidad o el pasado"
        else:
            return "Pregunta o misterio central que mantiene el interés"

    def _infer_reward_from_data(self, video_data: dict[str, Any]) -> str:
        """Inferir la recompensa o resolución ofrecida."""
        reward_sources = [
            video_data.get("reward", ""),
            video_data.get("resolution", ""),
            video_data.get("solution", ""),
            video_data.get("payoff", "")
        ]

        combined_text = " ".join(reward_sources).lower()

        if any(word in combined_text for word in ["verdad", "justicia", "libertad"]):
            return "Descubrimiento de la verdad o logro de justicia"
        elif any(word in combined_text for word in ["amor", "unión", "reconciliación"]):
            return "Encontrar amor o reconciliación"
        elif any(word in combined_text for word in ["paz", "seguridad", "tranquilidad"]):
            return "Lograr paz interior o seguridad externa"
        elif any(word in combined_text for word in ["poder", "control", "victoria"]):
            return "Obtener poder, control o victoria"
        else:
            return "Resolución satisfactoria del conflicto central"

    def _calculate_narrative_coherence(self, narrative: NarrativeAnalysis) -> float:
        """Calcula la coherencia de la narrativa basada en cómo se relacionan los elementos."""
        score = 50.0  # Base

        # Verificar que los elementos estén presentes y relacionados
        elements = [narrative.problem, narrative.desire, narrative.pain, narrative.mystery, narrative.reward]
        non_empty_elements = [e for e in elements if e and len(e.strip()) > 0]

        # Más elementos definidos = mejor coherencia (hasta cierto punto)
        if len(non_empty_elements) >= 4:
            score += 25
        elif len(non_empty_elements) >= 3:
            score += 15
        elif len(non_empty_elements) >= 2:
            score += 10

        # Verificar conexiones lógicas entre elementos
        # Problema debería relacionarse con deseo y dolor
        if narrative.problem and narrative.desire:
            if any(word in narrative.problem.lower() for word in narrative.desire.lower().split()):
                score += 10

        if narrative.problem and narrative.pain:
            if any(word in narrative.problem.lower() for word in narrative.pain.lower().split()):
                score += 10

        # Misterio debería llevar a recompensa o resolución
        if narrative.mystery and narrative.reward:
            if any(word in narrative.mystery.lower() for word in narrative.reward.lower().split()):
                score += 10

        # Dolor debería relacionarse con el deseo (lo que se quiere evitar o conseguir)
        if narrative.pain and narrative.desire:
            # El deseo suele ser lo contrario al dolor o lo que resuelve el dolor
            score += 5  # Conexión básica asumida

        return max(0.0, min(100.0, score))

    def _infer_emotional_journey(self, video_data: dict[str, Any]) -> list[str]:
        """Inferir el viaje emocional observado en el video."""
        # En una implementación real, esto vendría de análisis de expresiones faciales, tono de voz, etc.
        # Por ahora, inferir basado en géneros y elementos conocidos

        genre = video_data.get("genre", "romance_traicion").lower()

        journey_templates = {
            "romance_traicion": ["sorpresa", "ira", "tristeza", "determinación", "esperanza"],
            "thriller_misterio": ["sorpresa", "sospecha", "tensión", "miedo", "alivio"],
            "fantasia_epica": ["esperanza", "miedo", "coraje", "ira", "alegría"],
            "drama_medico": ["miedo", "tristeza", "esperanza", "ira", "paz"],
            "drama_legal": ["ira", "frustración", "determinación", "esperanza", "satisfacción"],
            "comedia_romantica": ["diversión", "confusión", "irritación", "ternura", "felicidad"]
        }

        # Buscar coincidencia parcial
        for key, journey in journey_templates.items():
            if key in genre:
                return journey

        # Viaje emocional genérico
        return ["intriga", "conflicto", "tensión", "resolución", "satisfacción"]

    def _analyze_production(self, video_data: dict[str, Any]) -> ProductionAnalysis:
        """Analiza los elementos de producción del video."""
        production = ProductionAnalysis()

        # Extraer o inferir elementos de producción
        production.camera_work = video_data.get(
            "camera_work",
            self._infer_camera_work(video_data)
        )

        production.editing_style = video_data.get(
            "editing_style",
            self._infer_editing_style(video_data)
        )

        production.music_sound = video_data.get(
            "music_sound",
            self._infer_music_sound(video_data)
        )

        production.text_overlay = video_data.get(
            "text_overlay",
            self._infer_text_overlay(video_data)
        )

        production.pacing_rhythm = video_data.get(
            "pacing_rhythm",
            self._infer_pacing_rhythm(video_data)
        )

        # Calcular score general de producción
        production.production_score = self._calculate_production_score(production)

        return production

    def _infer_camera_work(self, video_data: dict[str, Any]) -> list[str]:
        """Inferir el trabajo de cámara utilizado."""
        camera_sources = [
            video_data.get("camera_work", []),
            video_data.get("shots", []),
            video_data.get("visual_style", [])
        ]

        # Flatten si vienen como listas
        camera_list = []
        for source in camera_sources:
            if isinstance(source, list):
                camera_list.extend(source)
            elif isinstance(source, str):
                camera_list.append(source)

        # Si no hay datos específicos, inferir de otros elementos
        if not camera_list:
            genre = video_data.get("genre", "").lower()
            if "thriller" in genre or "misterio" in genre:
                camera_list = ["ECU on eyes", "rack focus", "push in", "whip pan", "handheld"]
            elif "romance" in genre:
                camera_list = ["medium close-up", "push in", "tracking shot", "establishing shot"]
            elif "acción" in genre or "fantasia" in genre:
                camera_list = ["wide shot", "tracking", "crane up", "fast cut", "ECU"]
            else:
                camera_list = ["medium shot", "close-up", "establishing shot"]

        return camera_list[:5]  # Limitar a 5 elementos

    def _infer_editing_style(self, video_data: dict[str, Any]) -> list[str]:
        """Inferir el estilo de edición."""
        editing_sources = [
            video_data.get("editing_style", []),
            video_data.get("cuts", []),
            video_data.get("rhythm", [])
        ]

        editing_list = []
        for source in editing_sources:
            if isinstance(source, list):
                editing_list.extend(source)
            elif isinstance(source, str):
                editing_list.append(source)

        if not editing_list:
            duration = video_data.get("duration_seconds", 0)
            if duration <= 60:  # Video corto (TikTok, Reels, etc.)
                editing_list = ["quick cuts", "jump cuts", "beat cutting", "text on beat"]
            else:  # Video más largo
                editing_list = ["standard cuts", "cross-cutting", "match cuts", "L-cut/J-cut"]

        return editing_list[:5]

    def _infer_music_sound(self, video_data: dict[str, Any]) -> list[str]:
        """Inferir el uso de música y sonido."""
        music_sources = [
            video_data.get("music_sound", []),
            video_data.get("audio", []),
            video_data.get("soundtrack", [])
        ]

        music_list = []
        for source in music_sources:
            if isinstance(source, list):
                music_list.extend(source)
            elif isinstance(source, str):
                music_list.append(source)

        if not music_list:
            genre = video_data.get("genre", "").lower()
            if "thriller" in genre or "misterio" in genre:
                music_list = ["sub-bass 40Hz", "heartbeat slowed", "tense strings", "silence drops"]
            elif "romance" in genre:
                music_list = ["soft piano", "light guitar", "emotional swells", "vocal pads"]
            elif "acción" in genre or "fantasia" in genre:
                music_list = ["hybrid orchestral", "electronic pulses", "percussive elements", "thematic motifs"]
            else:
                music_list = ["ambient atmosphere", "light percussion", "melodic elements"]

        return music_list[:5]

    def _infer_text_overlay(self, video_data: dict[str, Any]) -> list[str]:
        """Inferir el uso de texto en pantalla."""
        text_sources = [
            video_data.get("text_overlay", []),
            video_data.get("subtitles", []),
            video_data.get("on_screen_text", [])
        ]

        text_list = []
        for source in text_sources:
            if isinstance(source, list):
                text_list.extend(source)
            elif isinstance(source, str):
                text_list.append(source)

        if not text_list:
            # Inferir basado en plataforma y duración
            platform = video_data.get("platform", "").lower()
            if any(p in platform for p in ["tiktok", "instagram", "youtube"]):
                text_list = ["opening hook text", "key information", "call to action", "subtitle translation"]
            else:
                text_list = ["dialogue subtitles", "title cards", "location/time stamps"]

        return text_list[:5]

    def _infer_pacing_rhythm(self, video_data: dict[str, Any]) -> list[str]:
        """Inferir el ritmo y ritmo del video."""
        pacing_sources = [
            video_data.get("pacing_rhythm", []),
            video_data.get("rhythm", []),
            video_data.get("tempo", [])
        ]

        pacing_list = []
        for source in pacing_sources:
            if isinstance(source, list):
                pacing_list.extend(source)
            elif isinstance(source, str):
                pacing_list.append(source)

        if not pacing_list:
            duration = video_data.get("duration_seconds", 0)
            if duration <= 30:  # Videos muy cortos
                pacing_list = ["fast", "high energy", "every second counts", "punctuated by impacts"]
            elif duration <= 90:  # Videos cortos/medianos
                pacing_list = ["moderate-fast", "building tension", "impact points", "slightly varied"]
            else:  # Videos más largos
                pacing_list = ["varied tempo", "scene-dependent pacing", "dialogue-driven", "action peaks"]

        return pacing_list[:5]

    def _calculate_production_score(self, production: ProductionAnalysis) -> float:
        """Calcula un score general de producción basado en los elementos analizados."""
        score = 40.0  # Base

        # Bonos por elementos de producción de calidad
        if len(production.camera_work) >= 3:
            score += 10
        if len(production.editing_style) >= 3:
            score += 10
        if len(production.music_sound) >= 3:
            score += 10
        if len(production.text_overlay) >= 2:
            score += 5
        if len(production.pacing_rhythm) >= 3:
            score += 5

        # Bonos por elementos específicos de alta calidad
        quality_indicators = [
            ("ECU", production.camera_work),
            ("macro shot", production.camera_work),
            ("rack focus", production.camera_work),
            ("whip pan", production.camera_work),
            ("push in", production.camera_work),
            ("sub-bass", production.music_sound),
            ("40hz", production.music_sound),
            ("heartbeat", production.music_sound),
            ("silence drop", production.music_sound),
            ("quick cuts", production.editing_style),
            ("beat cutting", production.editing_style),
            ("jump cuts", production.editing_style),
            ("text on beat", production.editing_style),
            ("opening hook", production.text_overlay),
            ("key information", production.text_overlay)
        ]

        for indicator, container in quality_indicators:
            if any(indicator.lower() in item.lower() for item in container):
                score += 3

        return max(0.0, min(100.0, score))

    def _analyze_cliffhanger(self, video_data: dict[str, Any]) -> CliffhangerAnalysis:
        """Analiza el final o cliffhanger del video."""
        cliffhanger = CliffhangerAnalysis()

        # Extraer o inferir elementos del cliffhanger
        cliffhanger.cliffhanger_type = video_data.get(
            "cliffhanger_type",
            self._infer_cliffhanger_type(video_data)
        )

        cliffhanger.cliffhanger_text = video_data.get(
            "cliffhanger_text",
            self._infer_cliffhanger_text(video_data)
        )

        cliffhanger.open_question = video_data.get(
            "open_question",
            self._infer_open_question(video_data)
        )

        cliffhanger.continuation_desire = self._calculate_continuation_desire(
            cliffhanger.cliffhanger_type,
            cliffhanger.cliffhanger_text,
            cliffhanger.open_question,
            video_data
        )

        cliffhanger.satisfaction_level = self._calculate_satisfaction_level(
            cliffhanger.cliffhanger_type,
            cliffhanger.cliffhanger_text,
            cliffhanger.open_question,
            video_data
        )

        cliffhanger.frustration_level = self._calculate_frustration_level(
            cliffhanger.satisfaction_level,
            cliffhanger.continuation_desire
        )

        return cliffhanger

    def _infer_cliffhanger_type(self, video_data: dict[str, Any]) -> str:
        """Inferir el tipo de cliffhanger."""
        cliffhanger_sources = [
            video_data.get("cliffhanger_type", ""),
            video_data.get("ending_type", ""),
            video_data.get("final_twist", ""),
            video_data.get("revelation", "")
        ]

        combined_text = " ".join(cliffhanger_sources).lower()

        if any(word in combined_text for word in ["revelación", "revelation", "se descubre", "se revela"]):
            return "revelation"
        elif any(word in combined_text for word in ["pregunta", "question", "¿", "?"]):
            return "question"
        elif any(word in combined_text for word in ["traición", "betrayal", "engañ"]):
            return "betrayal"
        elif any(word in combo_text for word in ["amenaza", "threat", "peligro"]):
            return "threat"
        elif any(word in combined_text for word in ["sorpresa", "surprise", "giro"]):
            return "surprise"
        elif any(word in combined_text for word in ["identidad", "identity", "secreto"]):
            return "identity_reveal"
        else:
            return "unspecified"

    def _infer_cliffhanger_text(self, video_data: dict[str, Any]) -> str:
        """Inferir el texto exacto del cliffhanger."""
        return video_data.get(
            "cliffhanger_text",
            video_data.get("final_line", "")
        )

    def _infer_open_question(self, video_data: dict[str, Any]) -> str:
        """Inferir la pregunta abierta que deja el video."""
        return video_data.get(
            "open_question",
            video_data.get("final_question", "")
        )

    def _calculate_continuation_desire(
        self,
        cliffhanger_type: str,
        cliffhanger_text: str,
        open_question: str,
        video_data: dict[str, Any]
    ) -> float:
        """Calcular el deseo de continuar basado en el cliffhanger."""
        base_desire = 30.0

        # Bonos por tipos de cliffhanger efectivos
        if cliffhanger_type in ["revelation", "identity_reveal"]:
            base_desire += 30
        elif cliffhanger_type in ["question", "betrayal", "threat"]:
            base_desire += 25
        elif cliffhanger_type == "surprise":
            base_desire += 20

        # Bonos por presencia de texto o pregunta
        if cliffhanger_text and len(cliffhanger_text.strip()) > 0:
            base_desire += 15
        if open_question and len(open_question.strip()) > 0:
            base_desire += 20

        # Bonos por elementos específicos que aumentan el deseo de continuar
        text_to_check = f"{cliffhanger_text} {open_question}".lower()
        if any(word in text_to_check for word in
               ["¿", "?", " secreto", "verdad", "por qué", "cómo", "quién"]):
            base_desire += 15
        if any(word in text_to_check for word in
               ["traición", "engañ", "mentira", "falso"]):
            base_desire += 10
        if any(word in text_to_check for word in
               ["amenaza", "peligro", "viene", "próximo"]):
            base_desire += 15

        return max(0.0, min(100.0, base_desire))

    def _calculate_satisfaction_level(
        self,
        cliffhanger_type: str,
        cliffhanger_text: str,
        open_question: str,
        video_data: dict[str, Any]
    ) -> float:
        """Calcular el nivel de satisfacción proporcionada."""
        # Los cliffhangers efectivos suelen tener baja satisfacción (dejan preguntas)
        # Pero algún nivel de satisfacción es necesario para no frustrar demasiado

        base_satisfaction = 40.0  # Satisfacción moderada base

        # Si hay una revelación parcial, aumenta la satisfacción
        if cliffhanger_type == "revelation":
            base_satisfaction += 20

        # Si hay resolución de un problema menor, aumenta la satisfacción
        if any(word in cliffhanger_text.lower() for word in
               ["resuelto", "solucionado", "completado", "terminado"]):
            base_satisfaction += 15

        # Si la pregunta es muy abierta o existencial, disminuye ligeramente la satisfacción
        if open_question and len(open_question.strip()) > 0:
            if any(word in open_question.lower() for word in
                   ["por qué", "para qué", "qué pasará", "el futuro"]):
                base_satisfaction -= 10  # Preguntas existenciales reducen satisfacción inmediata

        return max(0.0, min(100.0, base_satisfaction))

    def _calculate_frustration_level(
        self,
        satisfaction_level: float,
        continuation_desire: float
    ) -> float:
        """Calcular el nivel de frustración saludable generada."""
        # La frustración saludable es el deseo de continuar no satisfecho
        # Pero no tanta frustración que haga abandonar

        frustration = continuation_desire - (satisfaction_level * 0.5)  # La satisfacción reduce la frustración

        # Asegurar que esté en rango saludable (20-80)
        # Demasiado poca frustración = bajo deseo de continuar
        # Demasiada frustración = abandono

        return max(20.0, min(80.0, frustration))

    def _calculate_viral_score(
        self,
        hook: HookAnalysis,
        narrative: NarrativeAnalysis,
        production: ProductionAnalysis,
        cliffhanger: CliffhangerAnalysis
    ) -> float:
        """Calcular el score general de viralidad."""
        # Ponderación de los diferentes componentes
        weights = {
            "hook": 0.25,      # Los primeros segundos son críticos para detener el scroll
            "narrative": 0.20,  # La historia mantiene el interés
            "production": 0.20,  # La calidad de producción afecta la compartibilidad
            "cliffhanger": 0.20,  # El final determina si se vuelve a ver o se comparte
            "emotional_journey": 0.15  # El viaje emocional genera conexión y reacción
        }

        # Normalizar componentes a escala 0-100
        hook_score = hook.hook_score
        narrative_score = narrative.narrative_coherence
        production_score = production.production_score
        cliffhanger_score = cliffhanger.continuation_desire  # Usamos deseo de continuar como métrica clave
        emotional_score = min(100.0, len(narrative.emotional_journey) * 15)  # Hasta 7 elementos = ~100

        # Calcular promedio ponderado
        viral_score = (
            hook_score * weights["hook"] +
            narrative_score * weights["narrative"] +
            production_score * weights["production"] +
            cliffhanger_score * weights["cliffhanger"] +
            emotional_score * weights["emotional_journey"]
        )

        return max(0.0, min(100.0, viral_score))

    def _extract_learnings(
        self,
        hook: HookAnalysis,
        narrative: NarrativeAnalysis,
        production: ProductionAnalysis,
        cliffhanger: CliffhangerAnalysis,
        video_data: dict[str, Any]
    ) -> list[str]:
        """Extraer aprendizajes específicos para mejorar futuras generaciones."""
        learnings = []

        # Aprendizajes del hook
        if hook.hook_score >= 80:
            learnings.append(f"Hook efectivo: {hook.first_second_visual} + {hook.first_second_audio} + '{hook.first_phrase}'")
        elif hook.hook_score < 50:
            learnings.append("Mejorar hook: considerar ECU en ojos/manos + sub-bass 40Hz + frase intrigante")

        # Aprendizajes narrativos
        if narrative.narrative_coherence >= 70:
            learnings.append("Narrativa coherente: problema→dolor→deseo→misterio→recompensa bien conectados")
        elif narrative.narrative_coherence < 40:
            learnings.append("Mejorar coherencia narrativa: asegurar que problema, deseo, dolor, misterio y recompensa estén lógicamente conectados")

        # Aprendizajes de producción
        if production.production_score >= 80:
            learnings.append(f"Producción de alta calidad: {', '.join(production.camera_work[:2])} + {', '.join(production.editing_style[:2])}")
        elif production.production_score < 50:
            learnings.append("Mejorar producción: considerar trabajo de cámara más dinámico y edición rítmica")

        # Aprendizajes del cliffhanger
        if cliffhanger.continuation_desire >= 70:
            learnings.append(f"Cliffhanger efectivo: {cliffhanger.cliffhanger_type} con fuerte deseo de continuar ({cliffhanger.continuation_desire:.0f}/100)")
        elif cliffhanger.continuation_desire < 40:
            learnings.append("Mejorar cliffhanger: considerar revelación, pregunta abierta o amenaza clara")

        # Aprendizajes basados en métricas de video (si están disponibles)
        if video_data.get("completion_rate", 0) < 0.5:
            learnings.append("Baja tasa de completión: considerar acortar o aumentar tensión a lo largo")
        if video_data.get("engagement_rate", 0) < 0.03:
            learnings.append("Baja tasa de engagement: considerar aumentar elementos interactivos o preguntas")
        if video_data.get("share_rate", 0) < 0.01:
            learnings.append("Baja tasa de compartición: considerar agregar elementos altamente emocionales o controversial de forma constructiva")

        # Aprendizajes de viaje emocional
        if len(narrative.emotional_journey) >= 4:
            learnings.append(f"Viaje emocional rico: {' → '.join(narrative.emotional_journey)}")
        elif len(narrative.emotional_journey) < 2:
            learnings.append("Mejorar viaje emocional: incluir más variaciones emocionales a lo largo del video")

        return learnings[:10]  # Limitar a 10 aprendizajes más importantes

    def _update_knowledge_base(
        self,
        hook: HookAnalysis,
        narrative: NarrativeAnalysis,
        production: ProductionAnalysis,
        cliffhanger: CliffhangerAnalysis
    ) -> None:
        """Actualizar la base de conocimientos con los nuevos aprendizajes."""
        # Actualizar patrones de hook exitosos
        if hook.hook_score >= 70:
            hook_pattern_key = f"{hook.first_second_visual}_{hook.first_second_audio}_{hook.first_phrase[:20]}"
            self.hook_patterns[hook_pattern_key] += 1

        # Actualizar patrones narrativos exitosos
        if narrative.narrative_coherence >= 70:
            narrative_pattern_key = f"{narrative.problem}_{narrative.desire}_{narrative.reward}"
            self.narrative_patterns[narrative_pattern_key] += 1

        # Actualizar patrones de producción exitosos
        if production.production_score >= 70:
            # Tomar algunos elementos representativos
            prod_pattern_key = f"{production.camera_work[0] if production.camera_work else 'none'}_{production.editing_style[0] if production.editing_style else 'none'}"
            self.production_patterns[prod_pattern_key] += 1

        # Actualizar patrones de cliffhanger exitosos
        if cliffhanger.continuation_desire >= 70:
            cliffhanger_pattern_key = f"{cliffhanger.cliffhanger_type}_{cliffhanger.open_question[:20] if cliffhanger.open_question else 'none'}"
            self.cliffhanger_patterns[cliffhanger_pattern_key] += 1

        # Actualizar la base de conocimientos aprendidos (mantener solo los más recientes y relevantes)
        # En una implementación real, esto sería más sofisticado y persistente
        # Por ahora, limitamos el tamaño para no crecer indefinidamente
        if len(self.learnings_database) > 1000:
            # Mantener los 500 más recientes (en una implementación real, ordenaríamos por relevancia)
            self.learnings_database = self.learnings_database[-500:]

    def get_top_hook_patterns(self, limit: int = 10) -> list[tuple[str, int]]:
        """Obtener los patrones de hook más exitosos."""
        return sorted(self.hook_patterns.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_top_narrative_patterns(self, limit: int = 10) -> list[tuple[str, int]]:
        """Obtener los patrones narrativos más exitosos."""
        return sorted(self.narrative_patterns.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_top_production_patterns(self, limit: int = 10) -> list[tuple[str, int]]:
        """Obtener los patrones de producción más exitosos."""
        return sorted(self.production_patterns.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_top_cliffhanger_patterns(self, limit: int = 10) -> list[tuple[str, int]]:
        """Obtener los patrones de cliffhanger más exitosos."""
        return sorted(self.cliffhanger_patterns.items(), key=lambda x: x[1], reverse=True)[:limit]

# Instancia singleton
viral_reverse_engineer = ViralReverseEngineerAI()
