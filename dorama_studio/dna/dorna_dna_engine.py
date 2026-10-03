"""
DORAMA DNA ENGINE - Inteligencia capaz de analizar miles de historias exitosas para descubrir patrones de éxito.
Crea la base de datos: DORAMA SUCCESS DNA DATABASE.
"""

import hashlib
import json
import logging
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class DNAPattern:
    """Patrón de éxito descubierto en el análisis de historias."""
    pattern_id: str
    pattern_type: str  # character_archetype, plot_structure, theme, emotional_arc, etc.
    name: str
    description: str
    frequency: int  # Cuántas veces aparece en la base de datos
    success_correlation: float  # Correlación con éxito (0-1.0)
    examples: list[str] = field(default_factory=list)  # Títulos de dramas donde aparece
    variations: list[str] = field(default_factory=list)  # Variaciones del patrón
    confidence: float = 0.8
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DramaDNA:
    """Representación completa del ADN de un drama exitoso."""
    drama_id: str
    title: str
    year: int
    country: str
    genre: str
    platform: str
    # Componentes del ADN
    character_archetypes: list[str] = field(default_factory=list)
    plot_structures: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    emotional_arc: list[str] = field(default_factory=list)
    tropes_used: list[str] = field(default_factory=list)
    tropes_subverted: list[str] = field(default_factory=list)
    # Métricas de éxito
    rating_score: float = 0.0  # Puntaje de rating (0-10)
    popularity_score: float = 0.0  # Puntaje de popularidad (0-100)
    critical_acclaim: float = 0.0  # Puntaje de aclamación crítica (0-10)
    audience_score: float = 0.0  # Puntaje de audiencia (0-100)
    viral_score: float = 0.0  # Puntaje de viralidad (0-100)
    longevity_score: float = 0.0  # Puntaje de longevidad (0-100)
    # Metadatos
    dna_hash: str = ""  # Hash único del ADN
    analysis_date: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.8

class DoramaDNAEngine:
    """
    DORAMA DNA Engine que analiza miles de historias exitosas para descubrir patrones.
    Crea y mantiene la base de datos DORAMA SUCCESS DNA DATABASE.
    """

    def __init__(self, db_path: str = "dorama_studio_data/dna_database.db"):
        self.db_path = db_path
        self.pattern_cache = {}  # Cache de patrones descubiertos
        self._init_database()
        logger.info(f"DORAMA DNA Engine initialized with database: {db_path}")

    def _init_database(self):
        """Inicializa la base de datos SQLite para el ADN de dramas."""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                PRAGMA journal_mode=WAL;
                PRAGMA foreign_keys=ON;

                CREATE TABLE IF NOT EXISTS dramas (
                    drama_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    year INTEGER,
                    country TEXT,
                    genre TEXT,
                    platform TEXT,
                    rating_score REAL DEFAULT 0.0,
                    popularity_score REAL DEFAULT 0.0,
                    critical_acclaim REAL DEFAULT 0.0,
                    audience_score REAL DEFAULT 0.0,
                    viral_score REAL DEFAULT 0.0,
                    longevity_score REAL DEFAULT 0.0,
                    dna_hash TEXT UNIQUE,
                    analysis_date TEXT,
                    confidence REAL DEFAULT 0.8
                );

                CREATE TABLE IF NOT EXISTS dna_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    frequency INTEGER DEFAULT 0,
                    success_correlation REAL DEFAULT 0.0,
                    confidence REAL DEFAULT 0.8,
                    last_updated TEXT
                );

                CREATE TABLE IF NOT EXISTS drama_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    drama_id TEXT,
                    pattern_id TEXT,
                    strength REAL DEFAULT 1.0,  # Qué tan fuerte está el patrón en este drama
                    FOREIGN KEY (drama_id) REFERENCES dramas (drama_id),
                    FOREIGN KEY (pattern_id) REFERENCES dna_patterns (pattern_id),
                    UNIQUE(drama_id, pattern_id)
                );

                CREATE TABLE IF NOT EXISTS pattern_examples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT,
                    example_title TEXT,
                    FOREIGN KEY (pattern_id) REFERENCES dna_patterns (pattern_id)
                );

                CREATE INDEX IF NOT EXISTS idx_dramas_genre ON dramas(genre);
                CREATE INDEX IF NOT EXISTS idx_dramas_country ON dramas(country);
                CREATE INDEX IF NOT EXISTS idx_dramas_year ON dramas(year);
                CREATE INDEX IF NOT EXISTS idx_dna_patterns_type ON dna_patterns(pattern_type);
                CREATE INDEX IF NOT EXISTS idx_drama_patterns_drama ON drama_patterns(drama_id);
                CREATE INDEX IF NOT EXISTS idx_drama_patterns_pattern ON drama_patterns(pattern_id);
            """)
            conn.commit()

    def _generate_drama_id(self, title: str, year: int) -> str:
        """Genera un ID único para un drama."""
        base_string = f"{title}_{year}"
        return hashlib.md5(base_string.encode()).hexdigest()[:12]

    def _generate_dna_hash(self, drama_data: dict[str, Any]) -> str:
        """Genera un hash único que representa el ADN del drama."""
        # Crear una representación canonica de los componentes clave del ADN
        dna_components = {
            "character_archetypes": sorted(drama_data.get("character_archetypes", [])),
            "plot_structures": sorted(drama_data.get("plot_structures", [])),
            "themes": sorted(drama_data.get("themes", [])),
            "emotional_arc": sorted(drama_data.get("emotional_arc", [])),
            "tropes_used": sorted(drama_data.get("tropes_used", [])),
            "tropes_subverted": sorted(drama_data.get("tropes_subverted", []))
        }

        # Convertir a JSON estable y generar hash
        dna_json = json.dumps(dna_components, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(dna_json.encode()).hexdigest()[:16]

    def analyze_drama(
        self,
        title: str,
        year: int,
        country: str,
        genre: str,
        platform: str,
        character_archetypes: list[str] = None,
        plot_structures: list[str] = None,
        themes: list[str] = None,
        emotional_arc: list[str] = None,
        tropes_used: list[str] = None,
        tropes_subverted: list[str] = None,
        rating_score: float = 0.0,
        popularity_score: float = 0.0,
        critical_acclaim: float = 0.0,
        audience_score: float = 0.0,
        viral_score: float = 0.0,
        longevity_score: float = 0.0
    ) -> DramaDNA:
        """
        Analiza un drama y extrae su ADN para almacenarlo en la base de datos.

        Args:
            title: Título del drama
            year: Año de estreno
            country: País de origen
            genre: Género del drama
            platform: Plataforma de emisión
            character_archetypes: Arquétipos de personajes presentes
            plot_structures: Estructuras de trama utilizadas
            themes: Temas explorados
            emotional_arc: Arco emocional del drama
            tropes_used: Tropes utilizados
            tropes_subverted: Tropes subvertidos o invertidos
            rating_score: Puntaje de rating (0-10)
            popularity_score: Puntaje de popularidad (0-100)
            critical_acclaim: Puntaje de aclamación crítica (0-10)
            audience_score: Puntaje de audiencia (0-100)
            viral_score: Puntaje de viralidad (0-100)
            longevity_score: Puntaje de longevidad (0-100)

        Returns:
            DramaDNA con el ADN analizado
        """
        logger.info(f"Analyzing drama DNA: {title} ({year})")

        # Establecer valores por defecto
        character_archetypes = character_archetypes or []
        plot_structures = plot_structures or []
        themes = themes or []
        emotional_arc = emotional_arc or []
        tropes_used = tropes_used or []
        tropes_subverted = tropes_subverted or []

        # Generar IDs y hash
        drama_id = self._generate_drama_id(title, year)
        dna_data = {
            "character_archetypes": character_archetypes,
            "plot_structures": plot_structures,
            "themes": themes,
            "emotional_arc": emotional_arc,
            "tropes_used": tropes_used,
            "tropes_subverted": tropes_subverted
        }
        dna_hash = self._generate_dna_hash(dna_data)

        # Crear objeto DramaDNA
        drama_dna = DramaDNA(
            drama_id=drama_id,
            title=title,
            year=year,
            country=country,
            genre=genre,
            platform=platform,
            character_archetypes=character_archetypes,
            plot_structures=plot_structures,
            themes=themes,
            emotional_arc=emotional_arc,
            tropes_used=tropes_used,
            tropes_subverted=tropes_subverted,
            rating_score=rating_score,
            popularity_score=popularity_score,
            critical_acclaim=critical_acclaim,
            audience_score=audience_score,
            viral_score=viral_score,
            longevity_score=longevity_score,
            dna_hash=dna_hash,
            confidence=0.9  # Alta confianza cuando tenemos todos los datos
        )

        # Guardar en base de datos
        self._save_drama_to_db(drama_dna)

        # Actualizar patrones descubiertos
        self._update_patterns_from_drama(drama_dna)

        logger.info(f"DNA analysis complete for {title}. DNA hash: {dna_hash}")
        return drama_dna

    def _save_drama_to_db(self, drama: DramaDNA) -> None:
        """Guarda un drama en la base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dramas
                (drama_id, title, year, country, genre, platform,
                 rating_score, popularity_score, critical_acclaim, audience_score,
                 viral_score, longevity_score, dna_hash, analysis_date, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                drama.drama_id, drama.title, drama.year, drama.country, drama.genre,
                drama.platform, drama.rating_score, drama.popularity_score,
                drama.critical_acclaim, drama.audience_score, drama.viral_score,
                drama.longevity_score, drama.dna_hash,
                drama.analysis_date.isoformat(), drama.confidence
            ))
            conn.commit()

    def _update_patterns_from_drama(self, drama: DramaDNA) -> None:
        """Actualiza la frecuencia y correlación de patrones basado en un nuevo drama analizado."""
        # Procesar cada tipo de patrón
        pattern_categories = [
            ("character_archetypes", drama.character_archetypes),
            ("plot_structures", drama.plot_structures),
            ("themes", drama.themes),
            ("emotional_arc", drama.emotional_arc),
            ("tropes_used", drama.tropes_used),
            ("tropes_subverted", drama.tropes_subverted)
        ]

        success_score = self._calculate_overall_success_score(drama)

        for pattern_type, patterns in pattern_categories:
            for pattern_name in patterns:
                if not pattern_name.strip():
                    continue

                # Normalizar el nombre del patrón
                normalized_name = self._normalize_pattern_name(pattern_name)

                # Verificar si el patrón ya existe
                existing_pattern = self._get_pattern(pattern_type, normalized_name)

                if existing_pattern:
                    # Actualizar patrón existente
                    self._update_pattern_frequency_and_correlation(
                        existing_pattern.pattern_id,
                        success_score
                    )

                    # Añadir ejemplo si no está ya presente
                    if drama.title not in existing_pattern.examples:
                        self._add_pattern_example(existing_pattern.pattern_id, drama.title)
                else:
                    # Crear nuevo patrón
                    pattern_id = self._create_new_pattern(
                        pattern_type, normalized_name, drama.title, success_score
                    )

                    # Añadir el drama como ejemplo
                    self._add_pattern_example(pattern_id, drama.title)

    def _calculate_overall_success_score(self, drama: DramaDNA) -> float:
        """Calcula un score general de éxito para el drama."""
        # Ponderación de los diferentes componentes de éxito
        weights = {
            "rating_score": 0.20,      # Puntaje de rating (0-10)
            "popularity_score": 0.25,  # Puntaje de popularidad (0-100)
            "critical_acclaim": 0.15,  # Puntaje de aclamación crítica (0-10)
            "audience_score": 0.20,    # Puntaje de audiencia (0-100)
            "viral_score": 0.10,       # Puntaje de viralidad (0-100)
            "longevity_score": 0.10    # Puntaje de longevidad (0-100)
        }

        # Normalizar todos los scores a 0-1 escala
        normalized_scores = {
            "rating_score": drama.rating_score / 10.0,
            "popularity_score": drama.popularity_score / 100.0,
            "critical_acclaim": drama.critical_acclaim / 10.0,
            "audience_score": drama.audience_score / 100.0,
            "viral_score": drama.viral_score / 100.0,
            "longevity_score": drama.longevity_score / 100.0
        }

        # Calcular promedio ponderado
        weighted_sum = sum(
            normalized_scores[key] * weight
            for key, weight in weights.items()
        )

        return weighted_sum  # Ya está en escala 0-1

    def _normalize_pattern_name(self, name: str) -> str:
        """Normaliza el nombre de un patrón para consistencia."""
        # Convertir a minúsculas y eliminar espacios extra
        normalized = name.lower().strip()
        # Reemplazar múltiples espacios con un solo espacio
        normalized = re.sub(r'\s+', ' ', normalized)
        # Eliminar caracteres especiales no deseados pero mantener guiones y subrayados
        normalized = re.sub(r'[^\w\s\-_]', '', normalized)
        return normalized

    def _get_pattern(self, pattern_type: str, pattern_name: str) -> DNAPattern | None:
        """Obtiene un patrón existente de la base de datos o caché."""
        cache_key = f"{pattern_type}:{pattern_name}"
        if cache_key in self.pattern_cache:
            return self.pattern_cache[cache_key]

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT p.* FROM dna_patterns p
                WHERE p.pattern_type = ? AND p.name = ?
            """, (pattern_type, pattern_name))
            row = cursor.fetchone()

            if row:
                pattern = DNAPattern(
                    pattern_id=row["pattern_id"],
                    pattern_type=row["pattern_type"],
                    name=row["name"],
                    description=row["description"] or "",
                    frequency=row["frequency"],
                    success_correlation=row["success_correlation"],
                    confidence=row["confidence"],
                    last_updated=datetime.fromisoformat(row["last_updated"]) if row["last_updated"] else datetime.utcnow()
                )
                self.pattern_cache[cache_key] = pattern
                return pattern

        return None

    def _create_new_pattern(
        self,
        pattern_type: str,
        pattern_name: str,
        example_title: str,
        initial_success_score: float
    ) -> str:
        """Crea un nuevo patrón en la base de datos."""
        pattern_id = self._generate_pattern_id(pattern_type, pattern_name)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO dna_patterns
                (pattern_id, pattern_type, name, description, frequency, success_correlation, confidence, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_id,
                pattern_type,
                pattern_name,
                f"Patrón de {pattern_type} descubierto mediante análisis de dramas exitosos",
                1,  # Frecuencia inicial
                initial_success_score,  # Correlación inicial basada en el éxito del drama ejemplo
                0.8,  # Confianza inicial
                datetime.utcnow().isoformat()
            ))
            conn.commit()

        # Actualizar caché
        cache_key = f"{pattern_type}:{pattern_name}"
        self.pattern_cache[cache_key] = DNAPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            name=pattern_name,
            description=f"Patrón de {pattern_type} descubierto mediante análisis de dramas exitosos",
            frequency=1,
            success_correlation=initial_success_score,
            confidence=0.8,
            last_updated=datetime.utcnow()
        )

        return pattern_id

    def _generate_pattern_id(self, pattern_type: str, pattern_name: str) -> str:
        """Genera un ID único para un patrón."""
        base_string = f"{pattern_type}_{pattern_name}"
        return hashlib.md5(base_string.encode()).hexdigest()[:12]

    def _add_pattern_example(self, pattern_id: str, example_title: str) -> None:
        """Añade un ejemplo a un patrón existente."""
        with sqlite3.connect(self.db_path) as conn:
            # Verificar si el ejemplo ya existe para evitar duplicados
            cursor = conn.execute("""
                SELECT 1 FROM pattern_examples
                WHERE pattern_id = ? AND example_title = ?
            """, (pattern_id, example_title))

            if not cursor.fetchone():
                conn.execute("""
                    INSERT INTO pattern_examples (pattern_id, example_title)
                    VALUES (?, ?)
                """, (pattern_id, example_title))
                conn.commit()

    def _update_pattern_frequency_and_correlation(
        self,
        pattern_id: str,
        new_drama_success_score: float
    ) -> None:
        """Actualiza la frecuencia y correlación de éxito de un patrón."""
        with sqlite3.connect(self.db_path) as conn:
            # Obtener valores actuales
            cursor = conn.execute("""
                SELECT frequency, success_correlation FROM dna_patterns WHERE pattern_id = ?
            """, (pattern_id,))
            row = cursor.fetchone()

            if row:
                current_frequency, current_correlation = row
                new_frequency = current_frequency + 1

                # Actualizar correlación usando promedio ponderado
                # Nueva correlación = (correlación_actual * frecuencia_actual + nuevo_score) / (frecuencia_actual + 1)
                new_correlation = (
                    (current_correlation * current_frequency) + new_drama_success_score
                ) / new_frequency

                # Actualizar en base de datos
                conn.execute("""
                    UPDATE dna_patterns
                    SET frequency = ?, success_correlation = ?, last_updated = ?
                    WHERE pattern_id = ?
                """, (
                    new_frequency,
                    new_correlation,
                    datetime.utcnow().isoformat(),
                    pattern_id
                ))
                conn.commit()

                # Actualizar caché
                # Necesitamos obtener el nombre y tipo del patrón para actualizar la caché correctamente
                cursor = conn.execute("""
                    SELECT pattern_type, name FROM dna_patterns WHERE pattern_id = ?
                """, (pattern_id,))
                row = cursor.fetchone()
                if row:
                    pattern_type, pattern_name = row
                    cache_key = f"{pattern_type}:{pattern_name}"
                    self.pattern_cache[cache_key] = DNAPattern(
                        pattern_id=pattern_id,
                        pattern_type=pattern_type,
                        name=pattern_name,
                        description="",  # Se llenará desde la BD si es necesario
                        frequency=new_frequency,
                        success_correlation=new_correlation,
                        confidence=0.8,  # Mantener confianza base
                        last_updated=datetime.utcnow()
                    )

    def get_top_patterns(
        self,
        pattern_type: str | None = None,
        limit: int = 20,
        min_frequency: int = 3
    ) -> list[DNAPattern]:
        """
        Obtiene los patrones más exitosos y frecuentes.

        Args:
            pattern_type: Tipo de patrón a filtrar (None para todos)
            limit: Número máximo de patrones a retornar
            min_frequency: Frecuencia mínima para considerar un patrón

        Returns:
            Lista de patrones ordenados por éxito y frecuencia
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if pattern_type:
                cursor = conn.execute("""
                    SELECT p.* FROM dna_patterns p
                    WHERE p.pattern_type = ? AND p.frequency >= ?
                    ORDER BY p.success_correlation DESC, p.frequency DESC
                    LIMIT ?
                """, (pattern_type, min_frequency, limit))
            else:
                cursor = conn.execute("""
                    SELECT p.* FROM dna_patterns p
                    WHERE p.frequency >= ?
                    ORDER BY p.success_correlation DESC, p.frequency DESC
                    LIMIT ?
                """, (min_frequency, limit))

            patterns = []
            for row in cursor.fetchall():
                pattern = DNAPattern(
                    pattern_id=row["pattern_id"],
                    pattern_type=row["pattern_type"],
                    name=row["name"],
                    description=row["description"] or "",
                    frequency=row["frequency"],
                    success_correlation=row["success_correlation"],
                    confidence=row["confidence"],
                    last_updated=datetime.fromisoformat(row["last_updated"]) if row["last_updated"] else datetime.utcnow()
                )
                patterns.append(pattern)

            return patterns

    def get_pattern_examples(self, pattern_id: str, limit: int = 10) -> list[str]:
        """Obtiene los ejemplos de un patrón específico."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT example_title FROM pattern_examples
                WHERE pattern_id = ?
                LIMIT ?
            """, (pattern_id, limit))

            return [row[0] for row in cursor.fetchall()]

    def search_dramas_by_criteria(
        self,
        genre: str | None = None,
        country: str | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        min_success_score: float | None = None
    ) -> list[DramaDNA]:
        """Busca dramas en la base de datos según criterios específicos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            query = "SELECT * FROM dramas WHERE 1=1"
            params = []

            if genre:
                query += " AND genre = ?"
                params.append(genre)

            if country:
                query += " AND country = ?"
                params.append(country)

            if year_min is not None:
                query += " AND year >= ?"
                params.append(year_min)

            if year_max is not None:
                query += " AND year <= ?"
                params.append(year_max)

            if min_success_score is not None:
                # Calcular score de éxito compuesto para filtrado
                query += """ AND ((rating_score/10.0 * 0.20 + popularity_score/100.0 * 0.25 +
                               critical_acclaim/10.0 * 0.15 + audience_score/100.0 * 0.20 +
                               viral_score/100.0 * 0.10 + longevity_score/100.0 * 0.10) >= ?)"""
                params.append(min_success_score)

            cursor = conn.execute(query, params)

            dramas = []
            for row in cursor.fetchall():
                # Reconstruir el objeto DramaDNA (simplificado - en implementación real
                # necesitaríamos obtener los componentes de ADN desde otras tablas)
                drama = DramaDNA(
                    drama_id=row["drama_id"],
                    title=row["title"],
                    year=row["year"],
                    country=row["country"],
                    genre=row["genre"],
                    platform=row["platform"],
                    rating_score=row["rating_score"] or 0.0,
                    popularity_score=row["popularity_score"] or 0.0,
                    critical_acclaim=row["critical_acclaim"] or 0.0,
                    audience_score=row["audience_score"] or 0.0,
                    viral_score=row["viral_score"] or 0.0,
                    longevity_score=row["longevity_score"] or 0.0,
                    dna_hash=row["dna_hash"] or "",
                    analysis_date=datetime.fromisoformat(row["analysis_date"]) if row["analysis_date"] else datetime.utcnow(),
                    confidence=row["confidence"] or 0.8
                )
                dramas.append(drama)

            return dramas

    def get_dna_statistics(self) -> dict[str, Any]:
        """Obtiene estadísticas generales de la base de datos de ADN."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}

            # Número total de dramas analizados
            cursor = conn.execute("SELECT COUNT(*) FROM dramas")
            stats["total_dramas_analyzed"] = cursor.fetchone()[0]

            # Número total de patrones únicos descubiertos
            cursor = conn.execute("SELECT COUNT(*) FROM dna_patterns")
            stats["total_unique_patterns"] = cursor.fetchone()[0]

            # Número total de ejemplos de patrones
            cursor = conn.execute("SELECT COUNT(*) FROM pattern_examples")
            stats["total_pattern_examples"] = cursor.fetchone()[0]

            # Distribución por géneros
            cursor = conn.execute("""
                SELECT genre, COUNT(*) as count
                FROM dramas
                GROUP BY genre
                ORDER BY count DESC
            """)
            stats["genre_distribution"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Distribución por países
            cursor = conn.execute("""
                SELECT country, COUNT(*) as count
                FROM dramas
                GROUP BY country
                ORDER BY count DESC
            """)
            stats["country_distribution"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Rangos de años
            cursor = conn.execute("""
                SELECT MIN(year) as min_year, MAX(year) as max_year
                FROM dramas
            """)
            min_year, max_year = cursor.fetchone()
            stats["year_range"] = {"min": min_year, "max": max_year}

            # Promedio de scores de éxito
            cursor = conn.execute("""
                SELECT
                    AVG(rating_score/10.0 * 0.20 + popularity_score/100.0 * 0.25 +
                          critical_acclaim/10.0 * 0.15 + audience_score/100.0 * 0.20 +
                          viral_score/100.0 * 0.10 + longevity_score/100.0 * 0.10) as avg_success
                FROM dramas
            """)
            stats["average_success_score"] = cursor.fetchone()[0] or 0.0

            return stats

# Instancia singleton
dorna_dna_engine = DoramaDNAEngine()
