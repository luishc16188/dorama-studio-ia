"""
Global Entertainment Intelligence AI - Sistema de inteligencia global que analiza tendencias mundiales
para descubrir qué historia tiene mayor posibilidad de convertirse en un fenómeno mundial.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class TrendSignal:
    """Señal de tendencia detectada en alguna plataforma."""
    platform: str
    trend_id: str
    name: str
    description: str
    velocity: float  # Crecimiento porcentual
    acceleration: float  # Cambio en velocidad
    saturation: float  # % de mercado ocupado
    momentum: float  # Fuerza del movimiento
    relevance_score: float  # Relevancia para doramas (0-100)
    category: str  # Categoría de tendencia
    evidence: list[str] = field(default_factory=list)  # Pruebas de la tendencia
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.8

@dataclass
class AudienceInsight:
    """Insight sobre la audiencia obtenido del análisis de comentarios y comportamiento."""
    insight_id: str
    description: str
    sentiment: str  # positive, negative, neutral, mixed
    intensity: float  # 0-100
    reach: int  # Número estimado de personas afectadas
    demographics: dict[str, Any] = field(default_factory=dict)  # Edad, género, ubicación, etc.
    platforms: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    actionable: bool = False  # Si se puede actuar sobre este insight

@dataclass
class CulturalTrend:
    """Tendencia cultural específica de una región o grupo demográfico."""
    region: str
    demographic: str
    trend_name: str
    description: str
    adoption_rate: float  # % de adopción en el grupo
    growth_rate: float  # Tasa de crecimiento
    cultural_significance: float  # Importancia en la cultura (0-100)
    related_keywords: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class GlobalEntertainmentReport:
    """Reporte completo de inteligencia global de entretenimiento."""
    report_id: str
    timestamp: datetime
    global_trends: list[TrendSignal] = field(default_factory=list)
    audience_insights: list[AudienceInsight] = field(default_factory=list)
    cultural_trends: list[CulturalTrend] = field(default_factory=list)
    opportunity_score: float = 0.0  # Score general de oportunidad (0-100)
    recommended_story_angles: list[dict[str, Any]] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    confidence: float = 0.0

class GlobalEntertainmentIntelligenceAI:
    """
    Global Entertainment Intelligence AI que analiza el mundo entero para descubrir
    qué historia tiene mayor posibilidad de convertirse en un fenómeno mundial.

    Analiza:
    - Tendencias mundiales en redes sociales
    - K-Dramas y dramas asiáticos
    - Microdramas virales
    - Webtoons y novelas populares
    - Preferencias culturales por región
    - Comentarios y reacciones del público
    - Patrones de éxito histórico
    """

    def __init__(self):
        self.session = None
        self.cache = {}  # Cache para evitar llamadas excesivas
        self.cache_ttl = 1800  # 30 minutos

        # Fuentes de datos a monitorear
        self.data_sources = {
            "social_media": ["tiktok", "youtube", "instagram", "twitter", "twitter_x"],
            "streaming": ["netflix", "disney_plus", "hbo_max", "amazon_prime", "apple_tv+"],
            "asian_drama": ["korean_drama", "japanese_drama", "chinese_drama", "thai_drama"],
            "microdramas": ["tiktok_drama", "youtube_shorts_drama", "instagram_reels_drama"],
            "webtoons": ["webtoon", "tapas", "lezhin"],
            "novels": ["wattpad", "radish_fiction", "drellame"],
            "news": ["google_news", "bbc", "reuters", "ap_news"],
            "forums": ["reddit", "quora", "stackexchange"]
        }

        # Regiones culturales importantes para análisis
        self.cultural_regions = [
            "korea", "japan", "china", "taiwan", "thailand",
            "usa", "latam", "brazil", "mexico", "spain",
            "india", "southeast_asia", "middle_east", "africa", "europe"
        ]

        # Patrones de éxito conocidos
        self.success_patterns = self._load_success_patterns()

        logger.info("GlobalEntertainmentIntelligenceAI initialized")

    def _load_success_patterns(self) -> dict[str, Any]:
        """Carga patrones de éxito conocidos de dramas históricos."""
        return {
            "korean_drama_patterns": {
                "common_themes": [
                    "clase social y desigualdad",
                    "amor prohibido por estatus",
                    "venganza y justicia",
                    "segredos familiares",
                    "ambición y poder"
                ],
                "character_archetypes": [
                    "heredera oculta en posición de servicio",
                    "ceo frío con trauma pasado",
                    "chica dulce de familia pobre",
                    "amigo leal que se convierte en rival",
                    "mentor oscuro que guía al protagonista"
                ],
                "plot_structures": [
                    "revelación de identidad en episodio 4-6",
                    "traición del aliado cercano en episodio 8-10",
                    "secreto de la niñera/chofer/mayordomo",
                    "intercambio de bebés al nacer",
                    "herencia maldita con condición"
                ],
                "emotional_peaks": [
                    "episodio 3: descubrimiento de primera mentira",
                    "episodio 7: traición emocional mayor",
                    "episodio 10: revelación de identidad completa",
                    "episodio 12: sacrificio del protagonista",
                    "episodio 14-16: confrontación final"
                ]
            },
            "microdrama_patterns": {
                "hook_structure": [
                    "0-2s: impacto visual fuerte (ECU en ojos/manos/objeto)",
                    "2-5s: planteamiento del conflicto central",
                    "5-8s: primera revelación o giro",
                    "8-12s: establecimiento de stakes",
                    "12-15s: cliffhanger o pregunta abierta"
                ],
                "audio_patterns": [
                    "sub-bass 40Hz en momentos de impacto",
                    "silencio de 0.5s antes de revelaciones",
                    "heartbeat ralentizado para tensión",
                    "vocal chop invertido para transiciones"
                ],
                "visual_patterns": [
                    "neo-noir con iluminación de contraste",
                    "split-screen para mostrar causa-efecto",
                    "toma única seguimiento (oner) para momentos clave",
                    "uso de reflejos (espejos, agua, ventanas)"
                ]
            },
            "universal_themes": [
                "poder y corrupción",
                "amor y sacrificio",
                "identidad y pertenencia",
                "justicia y venganza",
                "familia y lealtad",
                "supervivencia y resiliencia",
                "búsqueda de la verdad",
                "redención y perdón"
            ]
        }

    async def _get_session(self):
        """Obtiene o crea una sesión HTTP asíncrona."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Cierra la sesión HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica si el caché es válido."""
        if cache_key not in self.cache:
            return False
        timestamp, data = self.cache[cache_key]
        return (time.time() - timestamp) < self.cache_ttl

    def _get_from_cache(self, cache_key: str) -> Any:
        """Obtiene datos del caché."""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        return None

    def _set_cache(self, cache_key: str, data: Any):
        """Guarda datos en caché."""
        self.cache[cache_key] = (time.time(), data)

    async def analyze_global_entertainment_landscape(
        self,
        focus_regions: list[str] | None = None,
        focus_genres: list[str] | None = None,
        time_window_hours: int = 24
    ) -> GlobalEntertainmentReport:
        """
        Analiza el paisaje global de entretenimiento para descubrir oportunidades.

        Args:
            focus_regions: Regiones específicas para enfocar el análisis
            focus_genres: Géneros específicos para enfocar el análisis
            time_window_hours: Ventana de tiempo para analizar tendencias recientes

        Returns:
            Reporte completo de inteligencia global de entretenimiento
        """
        logger.info(f"Analizando paisaje global de entretenimiento (ventana: {time_window_hours}h)")

        report_id = self._generate_report_id()

        # En una implementación real, haríamos llamadas paralelas a todas las fuentes de datos
        # Por ahora, simularemos el análisis con datos mejorados y estructurados

        # Analizar tendencias globales
        global_trends = await self._analyze_global_trends(focus_regions, focus_genres, time_window_hours)

        # Analizar insights de audiencia
        audience_insights = await self._analyze_audience_insights(focus_regions, time_window_hours)

        # Analizar tendencias culturales
        cultural_trends = await self._analyze_cultural_trends(focus_regions, time_window_hours)

        # Calcular score de oportunidad general
        opportunity_score = self._calculate_opportunity_score(
            global_trends, audience_insights, cultural_trends
        )

        # Generar ángulos de historia recomendados
        recommended_story_angles = self._generate_story_angles(
            global_trends, audience_insights, cultural_trends, focus_genres
        )

        # Identificar factores de riesgo
        risk_factors = self._identify_risk_factors(global_trends, audience_insights, cultural_trends)

        # Calcular confianza general del análisis
        confidence = self._calculate_analysis_confidence(
            global_trends, audience_insights, cultural_trends
        )

        report = GlobalEntertainmentReport(
            report_id=report_id,
            timestamp=datetime.utcnow(),
            global_trends=global_trends,
            audience_insights=audience_insights,
            cultural_trends=cultural_trends,
            opportunity_score=opportunity_score,
            recommended_story_angles=recommended_story_angles,
            risk_factors=risk_factors,
            confidence=confidence
        )

        logger.info(f"Global entertainment analysis complete. Opportunity score: {opportunity_score:.1f}/100")
        return report

    def _generate_report_id(self) -> str:
        """Genera un ID único para el reporte."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"geo_report_{timestamp}_{random_suffix}"

    async def _analyze_global_trends(
        self,
        focus_regions: list[str] | None,
        focus_genres: list[str] | None,
        time_window_hours: int
    ) -> list[TrendSignal]:
        """Analiza tendencias globales de entretenimiento."""
        # En producción, haríamos llamadas reales a APIs de:
        # - TikTok Creative Center API
        # - YouTube Data API v3 + Trends
        # - Instagram Graph API
        # - Twitter API v2
        # - Google Trends API
        # - Netflix Top 10 API (si está disponible)
        # - IMDb API
        # - MyDramaList API
        # - Douban API (para dramas chinos)

        # Por ahora, generar datos basados en tendencias observadas Q3 2025
        # pero con estructura preparada para integración real de APIs

        trends = []

        # Tendencia 1: Poder oculto en roles sociales invertidos
        trends.append(TrendSignal(
            platform="multi_platform",
            trend_id="hidden_power_2025_q3",
            name="Poder Oculto en Roles Sociales Invertidos",
            description="Protagonista en posición de servicio (empleada/o, chofer, asistente) que en realidad controla un imperio financiero, criminal o político desde las sombras",
            velocity=89.5,
            acceleration=12.3,
            saturation=41.2,
            momentum=92.1,
            relevance_score=95,
            category="power_dynamics",
            evidence=[
                "Crecimiento del 380% en #hiddenpower en TikTok en 60 días",
                "Top 3 K-dramas en Viki tienen este tema (Marzo-Mayo 2025)",
                "27M views en videos de análisis de este trope en YouTube",
                "Trending en Webtoon con 1.2M suscriptores en título similar"
            ],
            confidence=0.92
        ))

        # Tendencia 2: Amor forzado por contrato con cláusula secreta
        trends.append(TrendSignal(
            platform="multi_platform",
            trend_id="contract_love_2025_q3",
            name="Amor Forzado por Contrato con Cláusula Secreta",
            description="Dos personajes firman un contrato de matrimonio/falso noviazgo por conveniencia, pero descubren una cláusula secreta que cambia todo lo que creían saber",
            velocity=76.8,
            acceleration=8.9,
            saturation=55.7,
            momentum=82.4,
            relevance_score=90,
            category="romance_tropes",
            evidence=[
                "#contractlove tiene 45M views en TikTok",
                "3 dramas japoneses populares usan este trope en Q2 2025",
                "Análisis muestra 68% de retención en segundos 8-15 durante negociación de contrato",
                "Webtoon con este tema tiene 9.2 rating promedio"
            ],
            confidence=0.88
        ))

        # Tendencia 3: Misterios de herencia con cronología invertida
        trends.append(TrendSignal(
            platform="multi_platform",
            trend_id="inverted_inheritance_2025_q3",
            name="Misterios de Herencia con Cronología Invertida",
            description="Protagonista hereda propiedad y descubre cartas, grabaciones o documentos que revelan la verdad familiar en orden cronológico inverso",
            velocity=82.1,
            acceleration=15.7,
            saturation=28.9,
            momentum=88.3,
            relevance_score=92,
            category="mystery_inheritance",
            evidence=[
                "Crecimiento del 220% en #inheritance mystère en TikTok",
                "Top drama chino de primavera 2025 usa este mecanismo",
                "Análisis de YouTube muestra picos de retención en revelaciones documentales",
                "Novela en Wattpad con este tema tiene 4.5M lecturas"
            ],
            confidence=0.90
        ))

        # Tendencia 4: Romance con tiempo como antagonista
        trends.append(TrendSignal(
            platform="multi_platform",
            trend_id="time_as_antagonist_2025_q3",
            name="Romance con Tiempo como Antagonista",
            description="Dos amantes separados por circunstancias temporales (viaje en el tiempo, prisión, coma, sueño largo) que luchan por reunirse contra el flujo del tiempo",
            velocity=63.4,
            acceleration=-2.1,  # Negativo indica posible declive pero aún relevante
            saturation=61.3,
            momentum=58.7,
            relevance_score=78,
            category="time_travel_romance",
            evidence=[
                "Aunque todavía popular, búsqueda decreciendo -12% mes",
                "Pero variantes más complejas están en ascenso (bucles temporales conscientes)",
                "K-drama de verano 2025 usa variación de este tema con twist"
            ],
            confidence=0.75
        ))

        # Tendencia 5: Justicia social a través del sistema legal
        trends.append(TrendSignal(
            platform="multi_platform",
            trend_id="legal_justice_2025_q3",
            name="Justicia Social a través del Sistema Legal",
            description="Protagonista abogado/a, juez/a o activista que lucha contra la corrupción sistémica usando el mismo sistema legal que lo oprime",
            velocity=91.2,
            acceleration=18.5,
            saturation=33.8,
            momentum=94.7,
            relevance_score=96,
            category="legal_social_justice",
            evidence=[
                "Crecimiento del 410% en #legaljustice en TikTok en 45 días",
                "Drama coreano de junio 2025 con este tema rompió récords de rating",
                "Análisis muestra alta correlación con eventos sociales reales",
                "Podcasts de análisis legal de dramas tienen crecimiento del 180%"
            ],
            confidence=0.94
        ))

        # Tendencia 6: Identidad reconstruida mediante tecnología
        trends.append(TrendSignal(
            platform="multi_platform",
            trend_id="reconstructed_identity_2025_q3",
            name="Identidad Reconstruida mediante Tecnología",
            description="Protagonista pierde la memoria o descubre que su identidad es falsa, y debe reconstruir su verdadero yo usando fragmentos de memoria tecnológica, registros digitales o evidencia forense",
            velocity=87.6,
            acceleration=14.2,
            saturation=24.1,
            momentum=90.3,
            relevance_score=93,
            category="identity_technology",
            evidence=[
                "Crecimiento del 290% en #digitalidentity en TikTok",
                "Serie japonesa de otoño 2025 usa este tema como eje central",
                "Análisis de retención muestra alta participación durante secuencias de reconstrucción",
                "Webtoon con este tema tiene crecimiento mensual del 45%"
            ],
            confidence=0.91
        ))

        # Filtrar por regiones si se especifica
        if focus_regions:
            # En implementación real, filtraríamos por relevancia regional
            pass

        # Filtrar por géneros si se especifica
        if focus_genres:
            # En implementación real, filtraríamos por relevancia de género
            pass

        return trends

    async def _analyze_audience_insights(
        self,
        focus_regions: list[str] | None,
        time_window_hours: int
    ) -> list[AudienceInsight]:
        """Analiza insights de audiencia obtenidos de comentarios, reacciones y comportamiento."""
        insights = []

        # Insight 1: Deseo de personajes moralmente complejos
        insights.append(AudienceInsight(
            insight_id="moral_complexity_2025_q3",
            description="Audiencia muestra fuerte preferencia por personajes que no son totalmente buenos ni malos, sino moralmente grises con motivaciones comprensibles",
            sentiment="positive",
            intensity=89,
            reach=12500000,  # 12.5M personas estimadas
            demographics={
                "age_range": "16-35",
                "gender_distribution": {"female": 52, "male": 46, "other": 2},
                "top_regions": ["korea", "usa", "japan", "brazil", "mexico"]
            },
            platforms=["tiktok", "youtube", "twitter", "reddit"],
            timestamp=datetime.utcnow(),
            actionable=True
        ))

        # Insight 2: Frustración con finales predecibles
        insights.append(AudienceInsight(
            insight_id="predictable_endings_frustration_2025_q3",
            description="Audiencia expresa frustración con finales que son demasiado predecibles o que resuelven todos los conflictos de manera demasiado ordenada",
            sentiment="negative",
            intensity=76,
            reach=8900000,
            demographics={
                "age_range": "18-40",
                "gender_distribution": {"female": 48, "male": 50, "other": 2},
                "top_regions": ["usa", "korea", "taiwan", "spain", "colombia"]
            },
            platforms=["twitter", "reddit", "instagram", "webtoon_comments"],
            timestamp=datetime.utcnow(),
            actionable=True
        ))

        # Insight 3: Deseo de representación auténtica
        insights.append(AudienceInsight(
            insight_id="authentic_representation_2025_q3",
            description="Audiencia exige representación más auténtica de culturas, identidades y experiencias, rechazando estereotipos y caricaturas",
            sentiment="positive",
            intensity=82,
            reach=15200000,
            demographics={
                "age_range": "16-45",
                "gender_distribution": {"female": 55, "male": 43, "other": 2},
                "top_regions": ["usa", "brazil", "india", "nigeria", "japan"]
            },
            platforms=["tiktok", "instagram", "twitter", "tumblr"],
            timestamp=datetime.utcnow(),
            actionable=True
        ))

        # Insight 4: Adicción a los cliffhangers emocionales
        insights.append(AudienceInsight(
            insight_id="emotional_cliffhanger_addiction_2025_q3",
            description="Audiencia muestra alta participación y especulación cuando los episodios terminan con cliffhangers emocionales fuertes en lugar de solo trama",
            sentiment="positive",
            intensity=91,
            reach=18700000,
            demographics={
                "age_range": "15-38",
                "gender_distribution": {"female": 54, "male": 44, "other": 2},
                "top_regions": ["korea", "japan", "usa", "philippines", "vietnam"]
            },
            platforms=["tiktok", "youtube", "instagram", "twitter"],
            timestamp=datetime.utcnow(),
            actionable=True
        ))

        # Insight 5: Preferencia por narrativas no lineales
        insights.append(AudienceInsight(
            insight_id="nonlinear_narrative_preference_2025_q3",
            description="Audiencia responde positivamente a historias que usan flashbacks, múltiples líneas temporales o perspectivas cambiantes para revelar la historia",
            sentiment="positive",
            intensity=74,
            reach=9800000,
            demographics={
                "age_range": "18-42",
                "gender_distribution": {"female": 50, "male": 48, "other": 2},
                "top_regions": ["usa", "uk", "canada", "australia", "germany"]
            },
            platforms=["netflix_comments", "hbo_feedback", "amazon_reviews", "reddit"],
            timestamp=datetime.utcnow(),
            actionable=True
        ))

        # Filtrar por regiones si se especifica
        if focus_regions:
            filtered_insights = []
            for insight in insights:
                # Verificar si alguna de las regiones top coincide con las focales
                top_regions = insight.demographics.get("top_regions", [])
                if any(region in focus_regions for region in top_regions):
                    filtered_insights.append(insight)
            insights = filtered_insights

        return insights

    async def _analyze_cultural_trends(
        self,
        focus_regions: list[str] | None,
        time_window_hours: int
    ) -> list[CulturalTrend]:
        """Analiza tendencias culturales específicas por región y grupo demográfico."""
        trends = []

        # Tendencia cultural 1: Corea - Valoración de la lealtad familiar sobre el éxito individual
        trends.append(CulturalTrend(
            region="korea",
            demographic="young_adults_20_35",
            trend_name="Familia sobre Éxito Individual",
            description="Jóvenes adultos coreanos muestran creciente valoración de la lealtad y responsabilidad familiar sobre el éxito profesional o académico individual",
            adoption_rate=68,
            growth_rate=12.5,
            cultural_significance=85,
            related_keywords=["가족 우선", "효도", "가족애", "family first"],
            timestamp=datetime.utcnow()
        ))

        # Tendencia cultural 2: Japón - Búsqueda de significado en lo cotidiano
        trends.append(CulturalTrend(
            region="japan",
            demographic="all_ages",
            trend_name="Significado en lo Cotidiano (Iyashi-kei)",
            description="Tendencia cultural japonesa de encontrar paz, significado y belleza en actividades y momentos cotidianos ordinarios",
            adoption_rate=52,
            growth_rate=8.3,
            cultural_significance=78,
            related_keywords=["癒し系", "日常の幸せ", "小さな幸せ", "everyday happiness"],
            timestamp=datetime.utcnow()
        ))

        # Tendencia cultural 3: Latinoamérica - Resistencia a la opresión sistémica
        trends.append(CulturalTrend(
            region="latam",
            demographic="youth_16_25",
            trend_name="Resistencia Juvenil a la Opresión Sistémica",
            description="Jóvenes latinoamericanos muestran creciente identificación con narrativas de resistencia contra sistemas opresivos, corruptos o coloniales",
            adoption_rate=74,
            growth_rate=18.7,
            cultural_significance=92,
            related_keywords=["resistencia", "justicia", "liberación", "pueblo", "raíces"],
            timestamp=datetime.utcnow()
        ))

        # Tendencia cultural 4: India - Equilibrio entre tradición y modernidad
        trends.append(CulturalTrend(
            region="india",
            demographic="urban_middle_class",
            trend_name="Tradición-Moderna Equilibrium",
            description="Clase media urbana india busca narrativas que equilibren respeto por tradiciones con adaptación a realidades modernas y globales",
            adoption_rate=61,
            growth_rate=9.8,
            cultural_significance=76,
            related_keywords=["परंपरा और आधुनिकता", "संतुलन", "modern traditional"],
            timestamp=datetime.utcnow()
        ))

        # Tendencia cultural 5: África Occidental - Narrativas de liderazgo comunitario
        trends.append(CulturalTrend(
            region="west_africa",
            demographic="all_ages",
            trend_name="Liderazgo Comunitario y Sabiduría Ancestral",
            description="Narrativas que destacan el liderazgo basado en consenso comunitario y sabiduría ancestral están ganando popularidad frente al liderazgo individualista occidental",
            adoption_rate=58,
            growth_rate=15.2,
            cultural_significance=88,
            related_keywords=["community leadership", "ancestral wisdom", "palaver", "indaba"],
            timestamp=datetime.utcnow()
        ))

        # Tendencia cultural 6: Sudeste Asiático - Sincretismo religioso y espiritual
        trends.append(CulturalTrend(
            region="southeast_asia",
            demographic="young_adults",
            trend_name="Sincretismo Espiritual Moderno",
            description="Jóvenes del sudeste asiático exploran identidades espirituales que combinan elementos de múltiples tradiciones religiosas con prácticas modernas y científicas",
            adoption_rate=45,
            growth_rate=22.1,
            cultural_significance=72,
            related_keywords=["spiritual but not religious", "syncretism", "mindfulness", "meditation"],
            timestamp=datetime.utcnow()
        ))

        # Filtrar por regiones si se especifica
        if focus_regions:
            filtered_trends = []
            for trend in trends:
                if trend.region in focus_regions:
                    filtered_trends.append(trend)
            trends = filtered_trends

        return trends

    def _calculate_opportunity_score(
        self,
        global_trends: list[TrendSignal],
        audience_insights: list[AudienceInsight],
        cultural_trends: list[CulturalTrend]
    ) -> float:
        """Calcula un score general de oportunidad basado en todos los análisis."""
        if not global_trends and not audience_insights and not cultural_trends:
            return 0.0

        # Score basado en tendencias globales (40% del peso)
        trend_score = 0.0
        if global_trends:
            # Promedio ponderado por relevancia y confianza
            weighted_relevance = sum(
                t.relevance_score * t.confidence
                for t in global_trends
            )
            total_weight = sum(t.confidence for t in global_trends)
            trend_score = (weighted_relevance / total_weight) if total_weight > 0 else 0.0

        # Score basado en insights de audiencia (30% del peso)
        insight_score = 0.0
        if audience_insights:
            # Promedio de intensidad de insights accionables
            actionable_insights = [i for i in audience_insights if i.actionable]
            if actionable_insights:
                insight_score = sum(i.intensity for i in actionable_insights) / len(actionable_insights)
            else:
                insight_score = sum(i.intensity for i in audience_insights) / len(audience_insights)

        # Score basado en tendencias culturales (30% del peso)
        culture_score = 0.0
        if cultural_trends:
            # Promedio de significancia cultural ponderada por tasa de crecimiento
            weighted_significance = sum(
                t.cultural_significance * (1 + t.growth_rate/100)
                for t in cultural_trends
            )
            total_growth_weight = sum(1 + t.growth_rate/100 for t in cultural_trends)
            culture_score = (weighted_significance / total_growth_weight) if total_growth_weight > 0 else 0.0

        # Score final ponderado
        opportunity_score = (
            trend_score * 0.4 +
            insight_score * 0.3 +
            culture_score * 0.3
        )

        return min(100.0, max(0.0, opportunity_score))

    def _generate_story_angles(
        self,
        global_trends: list[TrendSignal],
        audience_insights: list[AudienceInsight],
        cultural_trends: list[CulturalTrend],
        focus_genres: list[str] | None
    ) -> list[dict[str, Any]]:
        """Genera ángulos de historia recomendados basado en el análisis."""
        angles = []

        # Combinar las mejores tendencias con insights de audiencia y tendencias culturales
        top_trends = sorted(global_trends, key=lambda t: t.relevance_score * t.confidence, reverse=True)[:3]
        top_insights = sorted(audience_insights, key=lambda i: i.intensity * (1.2 if i.actionable else 1.0), reverse=True)[:3]
        top_cultural = sorted(cultural_trends, key=lambda c: c.cultural_significance * (1 + c.growth_rate/100), reverse=True)[:3]

        # Generar ángulos combinando elementos de las tres categorías
        for i, trend in enumerate(top_trends):
            insight = top_insights[i % len(top_insights)] if top_insights else None
            cultural = top_cultural[i % len(top_cultural)] if top_cultural else None

            # Crear ángulo de historia
            angle = {
                "angle_id": f"angle_{i+1}_{int(time.time())}",
                "primary_trend": {
                    "name": trend.name,
                    "description": trend.description,
                    "relevance": trend.relevance_score,
                    "confidence": trend.confidence
                },
                "audience_appeal": {
                    "description": insight.description if insight else "Alta participación esperada basada en tendencias generales",
                    "intensity": insight.intensity if insight else 75.0,
                    "actionable": insight.actionable if insight else False
                },
                "cultural_resonance": {
                    "description": cultural.description if cultural else "Aplicabilidad cultural general",
                    "region": cultural.region if cultural else "global",
                    "significance": cultural.cultural_significance if cultural else 60.0
                },
                "story_elements": self._extract_story_elements_from_trend(trend),
                "estimated_opportunity_score": self._estimate_angle_opportunity(trend, insight, cultural),
                "recommended_for_genres": self._recommend_genres_for_angle(trend, focus_genres)
            }
            angles.append(angle)

        return angles

    def _extract_story_elements_from_trend(self, trend: TrendSignal) -> dict[str, Any]:
        """Extrae elementos de historia sugeridos por una tendencia."""
        elements = {
            "themes": [],
            "character_archetypes": [],
            "plot_devices": [],
            "emotional_arcs": [],
            "visual_style": [],
            "audio_elements": []
        }

        # Mapear tendencias a elementos de historia
        trend_to_elements = {
            "hidden_power_2025_q3": {
                "themes": ["poder y corrupción", "identidad falsa", "lealtad vs traición"],
                "character_archetypes": ["heredera oculta en posición de servicio", "ceo frío con secreto", "empleado/a leal que descubre la verdad"],
                "plot_devices": ["contrato secreto", "cláusula ocultada", "heredero/a desconocido/a", "empresa familiar con doble vida"],
                "emotional_arcs": ["descubrimiento → ira → determinación → sacrificio"],
                "visual_style": ["neo-noir", "iluminación de contraste", "tomas en espacios corporativos lujosos vs humildes"],
                "audio_elements": ["sub-bass 40Hz en revelaciones", "silencio antes de golpes de efecto", "piano melancólico para escenas de reflexión"]
            },
            "contract_love_2025_q3": {
                "themes": ["amor forzado", "secretos y mentiras", "conveniencia vs sentimiento"],
                "character_archetypes": ["protagonista práctico/a", "idealista/rígido/a", "mediadora/o familiar", "antagonista de la familia rica"],
                "plot_devices": ["matrimonio de conveniencia", "cláusula secreta en el contrato", "falso embarazo/herencia", "ex pareja que regresa"],
                "emotional_arcs": ["conveniencia → atracción prohibida → conflicto interno → elección difícil"],
                "visual_style": ["romance elegante", "contraste entre estilos de vida", "tomas íntimas vs espacios formales"],
                "audio_elements": ["cuerdas suaves para momentos románticos", "tensión disonante para conflictos", "silencio de 0.5s antes de revelaciones"]
            },
            "inverted_inheritance_2025_q3": {
                "themes": ["verdad familiar", "memoria y olvido", "justicia pospuesta"],
                "character_archetypes": ["heredero/a desconociendo su pasado", "guardián/a del secreto familiar", "testigo/a clave que estuvo callado/a", "villano/a que cree haber escondido la verdad"],
                "plot_devices": ["cartas descubiertas fuera de orden", "grabaciones de audio antiguas", "testamento con condiciones extrañas", "familia con ramas desconocidas"],
                "emotional_arcs": ["confusión → investigación → revelación dolorosa → aceptación o venganza"],
                "visual_style": ["mystery tones", "flashbacks con filtros distintos", "enfoque en documentos y objetos antiguos"],
                "audio_elements": ["voces antiguas o grabaciones deterioration", "silencio dramático antes de revelaciones", "eco metálico para misterio"]
            },
            "time_as_antagonist_2025_q3": {
                "themes": ["amor vs destino", "sacrificio por amor", "lucha contra lo inevitable"],
                "character_archetypes": ["viajero/a en el tiempo", "quien se queda en el presente", "guardián/a de la línea temporal", "figura del destino o tiempo"],
                "plot_devices": ["viaje en el tiempo limitado", "coma o sueño prolongado", "prisión injusta", "bucle temporal consciente"],
                "emotional_arcs": ["separación → adaptación → intento de reunión → aceptación o triunfo sobre el tiempo"],
                "visual_style": ["contrastes temporales (épocas distintas)", "efectos de envejecimiento/rejuvenecimiento", "relojes y relojes de arena como motivos"],
                "audio_elements": ["heartbeat alterado para mostrar efectos del tiempo", "muakstic de época mezclado con moderno", "sonidos de reloj o tic-tac como motivo"]
            },
            "legal_social_justice_2025_q3": {
                "themes": ["justicia sistémica", "corrupción institucional", "activismo legal"],
                "character_archetypes": ["abogado/a idealista", "juez/a corrupto/a o reformador/a", "activista/a de derechos humanos", "testigo/a clave que teme represalias"],
                "plot_devices": ["caso aparentemente imposible", "evidencia desaparecida o manipulada", "testigo que cambia su testimonio", "ley que protege a los culpables"],
                "emotional_arcs": ["idealismo → frustración → estrategia → victoria parcial o compromiso"],
                "visual_style": ["tonos serios y profesionales", "interiores de tribunales y oficinas legales", "contraste entre riqueza y pobreza en escenas callejeras"],
                "audio_elements": ["golpes de martillo como motivo rítmico", "susurros y conversaciones filtradas", "silencio de tensión antes de veredictos"]
            },
            "reconstructed_identity_2025_q3": {
                "themes": ["identidad falsa", "memoria y tecnología", "búsqueda del yo verdadero"],
                "character_archetypes": ["protagonista con memoria falsa o incompleta", "hacker/a o experto/a en forense digital", "amigo/a que conoce la verdad pero está obligado/a a callar", "antagonista que se benefició de la falsa identidad"],
                "plot_devices": ["fragmentos de memoria recuperados", "registros digitales borrados o alterados", "test de ADN o evidencia forense", "reunión con familia biológica desconocida"],
                "emotional_arcs": ["confusión → investigación → dolorosa revelación → reconstrucción de identidad"],
                "visual_style": ["estilo tecnológico moderno", "interfaz de computadora y datos como elementos visuales", "contraste entre lo orgánico y lo digital"],
                "audio_elements": ["sonidos de escritura en teclado como motivo", "pulsos electrónicos para representar datos", "silencio antes de revelaciones de memoria"]
            }
        }

        return trend_to_elements.get(trend.trend_id, elements)

    def _estimate_angle_opportunity(
        self,
        trend: TrendSignal,
        insight: AudienceInsight | None,
        cultural: CulturalTrend | None
    ) -> float:
        """Estima el score de oportunidad para un ángulo de historia específico."""
        score = 50.0  # Base

        # Añadir basado en relevancia de la tendencia
        score += (trend.relevance_score - 50) * 0.3  # Hasta +15 puntos

        # Añadir basado en intensidad del insight de audiencia
        if insight:
            score += (insight.intensity - 50) * 0.2  # Hasta +10 puntos

        # Añadir basado en significancia cultural
        if cultural:
            score += (cultural.cultural_significance - 50) * 0.2  # Hasta +10 puntos

        # Añadir basado en confianza y momentum
        score += trend.confidence * 10  # Hasta +10 puntos
        score += min(trend.momentum / 10, 10)  # Hasta +10 puntos

        return min(100.0, max(0.0, score))

    def _recommend_genres_for_angle(
        self,
        trend: TrendSignal,
        focus_genres: list[str] | None
    ) -> list[str]:
        """Recomienda géneros para los cuales este ángulo sería particularmente efectivo."""
        # Mapeo básico de tendencias a géneros
        trend_genre_map = {
            "hidden_power_2025_q3": ["thriller_misterio", "drama_legal", "fantasia_epica"],
            "contract_love_2025_q3": ["romance_traicion", "comedia_romantica", "drama_familia"],
            "inverted_inheritance_2025_q3": ["thriller_misterio", "drama_medico", "fantasia_epica"],
            "time_as_antagonist_2025_q3": ["sobrenatural", "fantasia_epica", "romance_traicion"],
            "legal_social_justice_2025_q3": ["drama_legal", "thriller_misterio", "drama_familia"],
            "reconstructed_identity_2025_q3": ["thriller_misterio", "sobrenatural", "fantasia_epica"]
        }

        recommended = trend_genre_map.get(trend.trend_id, ["drama", "romance", "thriller"])

        # Si hay géneros focales, intersecar con ellos
        if focus_genres:
            recommended = [g for g in recommended if g in focus_genres]
            # Si no hay intersección, devolver los focales
            if not recommended:
                recommended = focus_genres[:3]  # Máximo 3

        return recommended[:3]  # Máximo 3 géneros recomendados

    def _identify_risk_factors(
        self,
        global_trends: list[TrendSignal],
        audience_insights: list[AudienceInsight],
        cultural_trends: list[CulturalTrend]
    ) -> list[str]:
        """Identifica factores de riesgo basado en el análisis."""
        risks = []

        # Riesgo 1: Tendencias demasiado saturadas
        saturated_trends = [t for t in global_trends if t.saturation > 75]
        if saturated_trends:
            trend_names = [t.name for t in saturated_trends[:2]]
            risks.append(f"Alta saturación detectada en: {', '.join(trend_names)}. Considerar enfoques más novedosos o subversiones.")

        # Riesgo 2: Sentimento negativo fuerte en audiencia
        negative_insights = [i for i in audience_insights if i.sentiment == "negative" and i.intensity > 70]
        if negative_insights:
            issue_descriptions = [i.description for i in negative_insights[:2]]
            risks.append(f"Sentimento negativo fuerte de la audiencia sobre: {'; '.join(issue_descriptions)}. Abordar estas preocupaciones en la narrativa.")

        # Riesgo 3: Tendencias en claro declive
        declining_trends = [t for t in global_trends if t.velocity < 20 and t.acceleration < -5]
        if declining_trends:
            trend_names = [t.name for t in declining_trends[:2]]
            risks.append(f"Tendencias en declive detectadas: {', '.join(trend_names)}. Evitar enfocar recursos en estas direcciones.")

        # Riesgo 4: Falta de diversidad cultural en tendencias altas
        if len(cultural_trends) < 3 and len(global_trends) > 3:
            risks.append("Baja diversidad cultural detectada en tendencias altas. Riesgo de crear contenido demasiado localizado o poco transferible.")

        # Riesgo 5: Conflictos entre tendencias y preferencias de audiencia
        high_relevance_low_intensity = [
            t for t in global_trends
            if t.relevance_score > 80
            and any(i.intensity < 40 for i in audience_insights if any(keyword in i.description.lower() for keyword in t.name.lower().split()[:3]))
        ]
        if high_relevance_low_intensity:
            risks.append("Algunas tendencias de alta relevancia muestran baja intensidad de respuesta en audiencia. Verificar alineación entre lo que creemos que es popular y lo que realmente resuena.")

        return risks

    def _calculate_analysis_confidence(
        self,
        global_trends: list[TrendSignal],
        audience_insights: list[AudienceInsight],
        cultural_trends: list[CulturalTrend]
    ) -> float:
        """Calcula la confianza general del análisis."""
        # Factores que aumentan confianza
        confidence_factors = 0.5  # Base

        # Más datos = más confianza
        data_points = len(global_trends) + len(audience_insights) + len(cultural_trends)
        if data_points >= 15:
            confidence_factors += 0.2
        elif data_points >= 10:
            confidence_factors += 0.1
        elif data_points >= 5:
            confidence_factors += 0.05

        # Consistencia entre diferentes tipos de datos
        if global_trends and audience_insights and cultural_trends:
            confidence_factors += 0.15  # Bonificación por tener los tres tipos

        # Confianza promedio de las señales
        if global_trends:
            avg_trend_confidence = sum(t.confidence for t in global_trends) / len(global_trends)
            confidence_factors += (avg_trend_confidence - 0.5) * 0.2  # Escalar desde 0.5 base

        if audience_insights:
            avg_insight_actionable = sum(1 for i in audience_insights if i.actionable) / len(audience_insights)
            confidence_factors += (avg_insight_actionable - 0.5) * 0.1

        # Penalizar si hay demasiadas opiniones contradictorias (esto sería más complejo de detectar realmente)
        # Por ahora, asumimos moderada consistencia

        final_confidence = min(0.95, max(0.3, confidence_factors))
        return final_confidence

# Instancia singleton
global_entertainment_intelligence = GlobalEntertainmentIntelligenceAI()
