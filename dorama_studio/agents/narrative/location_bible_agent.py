"""
Location Bible Agent - Fase 9
Genera la Biblia de Ubicaciones con atributos inmutables y rastrea su evolución.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *


class GeographyTraits(BaseModel):
    """Rasgos geográficos inmutables (P0)."""
    location_type: str = Field(..., description="Tipo: urbano, rural, submarino, espacial, etc.")
    climate: str = Field(..., description="Clima: tropical, árido, templado, frío, polar")
    topography: str = Field(..., description="Topografía: plana, montañosa, accidentada, costera")
    timezone: str = Field(..., description="Zona horaria aproximada")
    natural_landmarks: list[str] = Field(default_factory=list, description="Monumentos naturales: montaña, río, lago")
    size_scale: str = Field(..., description="Escala: íntima, barrio, ciudad, metrópoli, región, país")


class ArchitectureTraits(BaseModel):
    """Rasgos arquitectónicos semi-inmutables (P1)."""
    architectural_style: str = Field(..., description="Estilo: moderno, colonial, gótico, futurista, rústico")
    building_materials: list[str] = Field(default_factory=list, description="Materiales: concreto, madera, acero, vidrio")
    density_level: str = Field(..., description="Densidad de poblamiento: disperso, bajo, medio, alto, saturado")
    iconic_structures: list[str] = Field(default_factory=list, description="Estructuras icónicas: torre, puente, catedral")
    infrastructure_quality: str = Field(..., description="Calidad de infraestructura: pobre, básica, adecuada, excelente")


class CulturalTraits(BaseModel):
    """Rasgo cultural inmutable (P2)."""
    primary_language: str = Field(..., description="Idioma principal hablado")
    cultural_values: list[str] = Field(default_factory=list, description="Valores: colectivismo, individualismo, honor, progreso")
    taboos: list[str] = Field(default_factory=list, description="Tabúes culturales principales")
    traditional_foods: list[str] = Field(default_factory=list, description="Comidas tradicionales características")
    celebration_calendar: dict[str, str] = Field(default_factory=dict, description="Celebraciones importantes por mes")
    social_hierarchy: str = Field(..., description="Jerarquía social: igualitaria, estratificada, castas, meritocrática")


class LocationBibleEntry(BaseModel):
    """Entrada completa en la Biblia de Ubicaciones."""
    location_id: str = Field(..., description="ID único de la ubicación")
    name: str = Field(..., description="Nombre de la ubicación")
    description: str = Field(..., description="Descripción general de la ubicación")

    # Los 3 anclajes inmutables
    geography: GeographyTraits
    architecture: ArchitectureTraits
    cultural: CulturalTraits

    # Evolución a lo largo de la temporada (puede cambiar por eventos)
    current_geography_evolution: dict[int, GeographyTraits] = Field(default_factory=dict)  # episodio -> geography
    current_architecture_evolution: dict[int, ArchitectureTraits] = Field(default_factory=dict)  # episodio -> architecture
    current_cultural_evolution: dict[int, CulturalTraits] = Field(default_factory=dict)  # episodio -> cultural

    # Estado actual (puede cambiar drásticamente por eventos de la trama)
    current_condition: str = Field(default="intact", description="Estado: intacto, dañado, en ruinas, en construcción, abandonado")
    temporary_modifications: list[str] = Field(default_factory=list, description="Modificaciones temporales por eventos")
    access_restrictions: list[str] = Field(default_factory=list, description="Restricciones de acceso actuales")
    notable_events: list[dict[str, Any]] = Field(default_factory=list, description="Eventos importantes ocurridos aquí")

    # Conexiones con otros locations
    travel_times: dict[str, int] = Field(default_factory=dict)  # location_id -> minutos de viaje
    route_types: dict[str, str] = Field(default_factory=dict)  # location_id -> tipo de ruta (carretera, sendero, aéreo, etc.)

    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1


class LocationBibleAgent(BaseAgent[dict[str, Any], LocationBibleEntry]):
    """
    Location Bible Agent que genera y mantiene la bíblia de ubicaciones
    con los 3 anclajes inmutables (P0: geografía, P1: arquitectura, P2: cultural).
    """

    def __init__(self):
        super().__init__("LocationBibleAgent")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the location bible agent."""
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

    def _process(self, validated_input: dict[str, Any]) -> LocationBibleEntry:
        """
        Genera una entrada de Biblia de Ubicaciones basada en la entrada.

        Args:
            validated_input: Diccionario con:
                - location_id: ID único
                - name: Nombre
                - description: Descripción
                - geography: Dict con rasgos geográficos
                - architecture: Dict con rasgos arquitectónicos
                - cultural: Dict con rasgos culturales
                - evolution_data: Opcional, datos de evolución por episodio

        Returns:
            LocationBibleEntry completo
        """
        # Extraer datos básicos
        location_id = validated_input.get("location_id", f"LOC_{hash(str(validated_input)):03d}")
        name = validated_input.get("name", "Ubicación Sin Nombre")
        description = validated_input.get("description", "Ubicación genérica para escenas")

        # Construir los 3 anclajes inmutables
        geography_data = validated_input.get("geography", {})
        geography = GeographyTraits(
            location_type=geography_data.get("location_type", "urbano"),
            climate=geography_data.get("climate", "templado"),
            topography=geography_data.get("topography", "plana"),
            timezone=geography_data.get("timezone", "UTC-5"),
            natural_landmarks=geography_data.get("natural_landmarks", []),
            size_scale=geography_data.get("size_scale", "ciudad")
        )

        architecture_data = validated_input.get("architecture", {})
        architecture = ArchitectureTraits(
            architectural_style=architecture_data.get("architectural_style", "moderno"),
            building_materials=architecture_data.get("building_materials", ["concreto", "acero"]),
            density_level=architecture_data.get("density_level", "medio"),
            iconic_structures=architecture_data.get("iconic_structures", []),
            infrastructure_quality=architecture_data.get("infrastructure_quality", "adecuada")
        )

        cultural_data = validated_input.get("cultural", {})
        cultural = CulturalTraits(
            primary_language=cultural_data.get("primary_language", "español"),
            cultural_values=cultural_data.get("cultural_values", ["familia", "trabajo"]),
            taboos=cultural_data.get("taboos", ["deslealtad", "mentira en asuntos graves"]),
            traditional_foods=cultural_data.get("traditional_foods", ["arroz con pollo", "empanadas"]),
            celebration_calendar=cultural_data.get("celebration_calendar", {"12": "Navidad", "01": "Año Nuevo"}),
            social_hierarchy=cultural_data.get("social_hierarchy", "estratificada")
        )

        # Crear la entrada
        entry = LocationBibleEntry(
            location_id=location_id,
            name=name,
            description=description,
            geography=geography,
            architecture=architecture,
            cultural=cultural,
            # Inicializar evolución con los valores base en episodio 1
            current_geography_evolution={1: geography},
            current_architecture_evolution={1: architecture},
            current_cultural_evolution={1: cultural}
        )

        # Procesar datos de evolución si se proporcionan
        evolution_data = validated_input.get("evolution_data", {})
        if evolution_data:
            # Actualizar evolución de geografía
            geo_evolution = evolution_data.get("geography_evolution", {})
            for ep_str, geo_dict in geo_evolution.items():
                try:
                    ep = int(ep_str)
                    if ep >= 1:
                        entry.current_geography_evolution[ep] = GeographyTraits(**geo_dict)
                except (ValueError, TypeError):
                    pass

            # Actualizar evolución de arquitectura
            arch_evolution = evolution_data.get("architecture_evolution", {})
            for ep_str, arch_dict in arch_evolution.items():
                try:
                    ep = int(ep_str)
                    if ep >= 1:
                        entry.current_architecture_evolution[ep] = ArchitectureTraits(**arch_dict)
                except (ValueError, TypeError):
                    pass

            # Actualizar evolución cultural
            cult_evolution = evolution_data.get("cultural_evolution", {})
            for ep_str, cult_dict in cult_evolution.items():
                try:
                    ep = int(ep_str)
                    if ep >= 1:
                        entry.current_cultural_evolution[ep] = CulturalTraits(**cult_dict)
                except (ValueError, TypeError):
                    pass

            # Actualizar estado
            condition = evolution_data.get("condition")
            if condition:
                entry.current_condition = condition

            # Actualizar modificaciones temporales
            temp_mods = evolution_data.get("temporary_modifications", [])
            if isinstance(temp_mods, list):
                entry.temporary_modifications = temp_mods

            # Actualizar restricciones de acceso
            access_rest = evolution_data.get("access_restrictions", [])
            if isinstance(access_rest, list):
                entry.access_restrictions = access_rest

            # Actualizar eventos notables
            notable_events = evolution_data.get("notable_events", [])
            if isinstance(notable_events, list):
                entry.notable_events = notable_events

            # Actualizar conexiones de viaje
            travel_times = evolution_data.get("travel_times", {})
            if isinstance(travel_times, dict):
                entry.travel_times.update({k: int(v) for k, v in travel_times.items() if str(v).isdigit()})

            route_types = evolution_data.get("route_types", {})
            if isinstance(route_types, dict):
                entry.route_types.update(route_types)

        entry.updated_at = datetime.utcnow()
        return entry

    def get_location_at_episode(self, bible_entry: LocationBibleEntry, episode_num: int) -> LocationBibleEntry:
        """
        Obtiene la versión de la ubicación en un episodio específico,
        aplicando las evoluciones acumuladas hasta ese episodio.

        Args:
            bible_entry: Entrada base de la bíblia
            episode_num: Número de episodio (1-40)

        Returns:
            Nueva LocationBibleEntry con el estado en ese episodio
        """
        # Copiar la entrada base
        evolved_entry = bible_entry.model_copy(deep=True)

        # Aplicar evolución de geografía si existe para este episodio
        if episode_num in bible_entry.current_geography_evolution:
            evolved_entry.geography = bible_entry.current_geography_evolution[episode_num]
        else:
            # Encontrar la evolución más cercana anterior
            prior_eps = [ep for ep in bible_entry.current_geography_evolution.keys() if ep <= episode_num]
            if prior_eps:
                latest_prior = max(prior_eps)
                evolved_entry.geography = bible_entry.current_geography_evolution[latest_prior]

        # Aplicar evolución de arquitectura si existe para este episodio
        if episode_num in bible_entry.current_architecture_evolution:
            evolved_entry.architecture = bible_entry.current_architecture_evolution[episode_num]
        else:
            # Encontrar la evolución más cercana anterior
            prior_eps = [ep for ep in bible_entry.current_architecture_evolution.keys() if ep <= episode_num]
            if prior_eps:
                latest_prior = max(prior_eps)
                evolved_entry.architecture = bible_entry.current_architecture_evolution[latest_prior]

        # Aplicar evolución cultural si existe para este episodio
        if episode_num in bible_entry.current_cultural_evolution:
            evolved_entry.cultural = bible_entry.current_cultural_evolution[episode_num]
        else:
            # Encontrar la evolución más cercana anterior
            prior_eps = [ep for ep in bible_entry.current_cultural_evolution.keys() if ep <= episode_num]
            if prior_eps:
                latest_prior = max(prior_eps)
                evolved_entry.cultural = bible_entry.current_cultural_evolution[latest_prior]

        evolved_entry.updated_at = datetime.utcnow()
        return evolved_entry

    def update_evolution(
        self,
        bible_entry: LocationBibleEntry,
        episode_num: int,
        geography_changes: dict[str, Any] | None = None,
        architecture_changes: dict[str, Any] | None = None,
        cultural_changes: dict[str, Any] | None = None,
        condition: str | None = None,
        temporary_modifications: list[str] | None = None,
        access_restrictions: list[str] | None = None,
        notable_events: list[dict[str, Any]] | None = None,
        travel_times: dict[str, int] | None = None,
        route_types: dict[str, str] | None = None
    ) -> LocationBibleEntry:
        """
        Actualiza la evolución de la ubicación para un episodio específico.

        Args:
            bible_entry: Entrada base de la bíblia
            episode_num: Número de episodio
            geography_changes: Cambios en geografía (se fusiona con el actual)
            architecture_changes: Cambios en arquitectura (se fusiona con el actual)
            cultural_changes: Cambios en cultural (se fusiona con el actual)
            condition: Nuevo estado de la ubicación
            temporary_modifications: Nuevas modificaciones temporales (reemplaza la lista)
            access_restrictions: Nuevas restricciones de acceso (reemplaza la lista)
            notable_events: Nuevos eventos notables (se fusiona con la lista)
            travel_times: Nuevos tiempos de viaje (se fusiona con el mapa)
            route_types: Nuevos tipos de ruta (se fusiona con el mapa)

        Returns:
            Nueva LocationBibleEntry con la evolución actualizada
        """
        # Copiar la entrada
        updated_entry = bible_entry.model_copy(deep=True)

        # Actualizar evolución de geografía
        if geography_changes is not None:
            current = updated_entry.current_geography_evolution.get(episode_num, updated_entry.geography)
            new_geo_dict = current.model_dump()
            new_geo_dict.update(geography_changes)
            updated_entry.current_geography_evolution[episode_num] = GeographyTraits(**new_geo_dict)

        # Actualizar evolución de arquitectura
        if architecture_changes is not None:
            current = updated_entry.current_architecture_evolution.get(episode_num, updated_entry.architecture)
            new_arch_dict = current.model_dump()
            new_arch_dict.update(architecture_changes)
            updated_entry.current_architecture_evolution[episode_num] = ArchitectureTraits(**new_arch_dict)

        # Actualizar evolución cultural
        if cultural_changes is not None:
            current = updated_entry.current_cultural_evolution.get(episode_num, updated_entry.cultural)
            new_cult_dict = current.model_dump()
            new_cult_dict.update(cultural_changes)
            updated_entry.current_cultural_evolution[episode_num] = CulturalTraits(**new_cult_dict)

        # Actualizar estado
        if condition is not None:
            updated_entry.current_condition = condition

        # Actualizar modificaciones temporales
        if temporary_modifications is not None:
            updated_entry.temporary_modifications = temporary_modifications

        # Actualizar restricciones de acceso
        if access_restrictions is not None:
            updated_entry.access_restrictions = access_restrictions

        # Actualizar eventos notables
        if notable_events is not None:
            updated_entry.notable_events.extend(notable_events)

        # Actualizar tiempos de viaje
        if travel_times is not None:
            updated_entry.travel_times.update({k: int(v) for k, v in travel_times.items() if str(v).isdigit()})

        # Actualizar tipos de ruta
        if route_types is not None:
            updated_entry.route_types.update(route_types)

        updated_entry.updated_at = datetime.utcnow()
        return updated_entry


# Instancia por defecto para uso conveniente
default_location_bible = LocationBibleAgent()
