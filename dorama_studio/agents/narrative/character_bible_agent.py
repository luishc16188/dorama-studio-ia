"""
Character Bible Agent - Fase 9
Genera la Biblia de Personajes con los 3 anclajes inmutables (P0, P1, P2)
y rastrea su evolución a lo largo de la temporada.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *


class PhysicalTraits(BaseModel):
    """Rasgos físicos inmutables (P0)."""
    height_cm: int = Field(..., description="Altura en centímetros")
    build: str = Field(..., description="Complexión: ectomorfo, mesomorfo, endomorfo")
    hair_color: str = Field(..., description="Color de cabello natural")
    hair_style: str = Field(..., description="Estilo de cabello natural")
    eye_color: str = Field(..., description="Color de ojos (codificado hex)")
    skin_tone: str = Field(..., description="Tono de piel")
    distinguishing_marks: list[str] = Field(default_factory=list, description="Marcas distintivas: cicatrices, tatuajes, pecas")
    age_apparent: int = Field(..., description="Edad aparente")
    face_shape: str = Field(..., description="Forma del rostro: oval, redondo, cuadrado, corazón")
    bone_structure: str = Field(..., description="Estructura ósea: gracil, robusto")


class WardrobeTraits(BaseModel):
    """Rasgos de vestuario semi-inmutables (P1)."""
    signature_style: str = Field(..., description="Estilo signature: ejecutivo, bohemio, deportivo, etc.")
    color_palette: list[str] = Field(default_factory=list, description="Paleta de colores preferidos")
    key_items: list[str] = Field(default_factory=list, description="Prendas clave: traje negro, reloj de plata, etc.")
    accessories: list[str] = Field(default_factory=list, description="Accesorios característicos")


class PsychologicalCore(BaseModel):
    """Rasgo psicológico inmutable (P2)."""
    want: str = Field(..., description="Deseo consciente del personaje")
    need: str = Field(..., description="Necesidad inconsciente del personaje")
    lie: str = Field(..., description="Mentira que el personaje cree sobre sí mismo")
    ghost: str = Field(..., description="Trauma o evento del pasado que lo marca")
    secret: str = Field(..., description="Secreto que el personaje oculta al mundo")
    fear: str = Field(..., description="Miedo más profundo")
    wound: str = Field(..., description="Herida emocional que lo define")


class CharacterBibleEntry(BaseModel):
    """Entrada completa en la Biblia de Personajes."""
    character_id: str = Field(..., description="ID único del personaje")
    name: str = Field(..., description="Nombre del personaje")
    role: str = Field(..., description="Rol en la historia: protagonista, antagonista, etc.")
    archetype: str = Field(..., description="Arquetipo junguiano: ruler, caregiver, rebel, etc.")

    # Los 3 anclajes inmutables
    physical: PhysicalTraits
    wardrobe: WardrobeTraits
    psychological: PsychologicalCore

    # Evolución a lo largo de la temporada (puede cambiar)
    current_wardrobe_evolution: dict[int, WardrobeTraits] = Field(default_factory=dict)  # episodio -> wardrobe
    current_psychological_evolution: dict[int, PsychologicalCore] = Field(default_factory=dict)  # episodio -> psychological (para crecimiento)
    current_aliases: list[str] = Field(default_factory=list)  # aliases o seudónimos usados

    # Relaciones y redes
    relationship_map: dict[str, str] = Field(default_factory=dict)  # otro_character_id -> tipo de relación
    alliance_map: dict[str, bool] = Field(default_factory=dict)  # character_id -> es aliado (True) o enemigo (False)

    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1


class CharacterBibleAgent(BaseAgent[dict[str, Any], CharacterBibleEntry]):
    """
    Character Bible Agent que genera y mantiene la bíblia de personajes
    con los 3 anclajes inmutables (P0: físico, P1: vestuario, P2: psicológico).
    """

    def __init__(self):
        super().__init__("CharacterBibleAgent")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the character bible agent."""
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

    def _process(self, validated_input: dict[str, Any]) -> CharacterBibleEntry:
        """
        Genera una entrada de Biblia de Personajes basada en la entrada.

        Args:
            validated_input: Diccionario con:
                - character_id: ID único
                - name: Nombre
                - role: Rol
                - archetype: Arquetipo
                - physical: Dict con rasgos físicos
                - wardrobe: Dict con rasgos de vestuario
                - psychological: Dict con rasgos psicológicos
                - evolution_data: Opcional, datos de evolución por episodio

        Returns:
            CharacterBibleEntry completo
        """
        # Extraer datos básicos
        character_id = validated_input.get("character_id", f"CHAR_{hash(str(validated_input)):03d}")
        name = validated_input.get("name", "Personaje Sin Nombre")
        role = validated_input.get("role", "protagonist")
        archetype = validated_input.get("archetype", "caregiver")

        # Construir los 3 anclajes inmutables
        physical_data = validated_input.get("physical", {})
        physical = PhysicalTraits(
            height_cm=physical_data.get("height_cm", 170),
            build=physical_data.get("build", "mesomorfo"),
            hair_color=physical_data.get("hair_color", "#000000"),
            hair_style=physical_data.get("hair_style", "natural"),
            eye_color=physical_data.get("eye_color", "#000000"),
            skin_tone=physical_data.get("skin_tone", "medium"),
            distinguishing_marks=physical_data.get("distinguishing_marks", []),
            age_apparent=physical_data.get("age_apparent", 25),
            face_shape=physical_data.get("face_shape", "oval"),
            bone_structure=physical_data.get("bone_structure", "mediano")
        )

        wardrobe_data = validated_input.get("wardrobe", {})
        wardrobe = WardrobeTraits(
            signature_style=wardrobe_data.get("signature_style", "casual"),
            color_palette=wardrobe_data.get("color_palette", ["#FFFFFF", "#000000"]),
            key_items=wardrobe_data.get("key_items", ["jeans", "tshirt"]),
            accessories=wardrobe_data.get("accessories", ["reloj"])
        )

        psychological_data = validated_input.get("psychological", {})
        psychological = PsychologicalCore(
            want=psychological_data.get("want", "ser feliz"),
            need=psychological_data.get("need", "ser amado"),
            lie=psychological_data.get("lie", "debo ser perfecto para ser amado"),
            ghost=psychological_data.get("ghost", "perdí a alguien importante"),
            secret=psychological_data.get("secret", "tengo un talento oculto"),
            fear=psychological_data.get("fear", "estar solo"),
            wound=psychological_data.get("wound", "traición en la infancia")
        )

        # Crear la entrada
        entry = CharacterBibleEntry(
            character_id=character_id,
            name=name,
            role=role,
            archetype=archetype,
            physical=physical,
            wardrobe=wardrobe,
            psychological=psychological,
            # Inicializar evolución con los valores base en episodio 1
            current_wardrobe_evolution={1: wardrobe},
            current_psychological_evolution={1: psychological}
        )

        # Procesar datos de evolución si se proporcionan
        evolution_data = validated_input.get("evolution_data", {})
        if evolution_data:
            # Actualizar evolución de vestuario
            wardrobe_evolution = evolution_data.get("wardrobe_evolution", {})
            for ep_str, wardrobe_dict in wardrobe_evolution.items():
                try:
                    ep = int(ep_str)
                    if ep >= 1:  # asumimos que se actualizará según temporada
                        entry.current_wardrobe_evolution[ep] = WardrobeTraits(**wardrobe_dict)
                except (ValueError, TypeError):
                    pass

            # Actualizar evolución psicológica
            psych_evolution = evolution_data.get("psychological_evolution", {})
            for ep_str, psych_dict in psych_evolution.items():
                try:
                    ep = int(ep_str)
                    if ep >= 1:
                        entry.current_psychological_evolution[ep] = PsychologicalCore(**psych_dict)
                except (ValueError, TypeError):
                    pass

            # Actualizar aliases
            aliases = evolution_data.get("aliases", [])
            if isinstance(aliases, list):
                entry.current_aliases = aliases

            # Actualizar relaciones
            relationships = evolution_data.get("relationships", {})
            if isinstance(relationships, dict):
                entry.relationship_map.update(relationships)

            alliances = evolution_data.get("alliances", {})
            if isinstance(alliances, dict):
                entry.alliance_map.update({k: bool(v) for k, v in alliances.items()})

        entry.updated_at = datetime.utcnow()
        return entry

    def get_character_at_episode(self, bible_entry: CharacterBibleEntry, episode_num: int) -> CharacterBibleEntry:
        """
        Obtiene la versión del personaje en un episodio específico,
        aplicando las evoluciones acumuladas hasta ese episodio.

        Args:
            bible_entry: Entrada base de la bíblia
            episode_num: Número de episodio (1-40)

        Returns:
            Nueva CharacterBibleEntry con el estado en ese episodio
        """
        # Copiar la entrada base
        evolved_entry = bible_entry.model_copy(deep=True)

        # Aplicar evolución de vestuario si existe para este episodio
        if episode_num in bible_entry.current_wardrobe_evolution:
            evolved_entry.wardrobe = bible_entry.current_wardrobe_evolution[episode_num]
        else:
            # Encontrar la evolución más cercana anterior
            prior_eps = [ep for ep in bible_entry.current_wardrobe_evolution.keys() if ep <= episode_num]
            if prior_eps:
                latest_prior = max(prior_eps)
                evolved_entry.wardrobe = bible_entry.current_wardrobe_evolution[latest_prior]

        # Aplicar evolución psicológica si existe para este episodio
        if episode_num in bible_entry.current_psychological_evolution:
            evolved_entry.psychological = bible_entry.current_psychological_evolution[episode_num]
        else:
            # Encontrar la evolución más cercana anterior
            prior_eps = [ep for ep in bible_entry.current_psychological_evolution.keys() if ep <= episode_num]
            if prior_eps:
                latest_prior = max(prior_eps)
                evolved_entry.psychological = bible_entry.current_psychological_evolution[latest_prior]

        evolved_entry.updated_at = datetime.utcnow()
        return evolved_entry

    def update_evolution(
        self,
        bible_entry: CharacterBibleEntry,
        episode_num: int,
        wardrobe_changes: dict[str, Any] | None = None,
        psychological_changes: dict[str, Any] | None = None,
        aliases: list[str] | None = None,
        relationships: dict[str, str] | None = None,
        alliances: dict[str, bool] | None = None
    ) -> CharacterBibleEntry:
        """
        Actualiza la evolución del personaje para un episodio específico.

        Args:
            bible_entry: Entrada base de la bíblia
            episode_num: Número de episodio
            wardrobe_changes: Cambios en vestuario (se fusiona con el actual)
            psychological_changes: Cambios en psicológico (se fusiona con el actual)
            aliases: Nuevos aliases (reemplaza la lista)
            relationships: Nuevas relaciones (se fusiona con el mapa)
            alliances: Nuevas alianzas (se fusiona con el mapa)

        Returns:
            Nueva CharacterBibleEntry con la evolución actualizada
        """
        # Copiar la entrada
        updated_entry = bible_entry.model_copy(deep=True)

        # Actualizar evolución de vestuario
        if wardrobe_changes is not None:
            current = updated_entry.current_wardrobe_evolution.get(episode_num, updated_entry.wardrobe)
            # Crear nuevo objeto con los cambios fusionados
            new_wardrobe_dict = current.model_dump()
            new_wardrobe_dict.update(wardrobe_changes)
            updated_entry.current_wardrobe_evolution[episode_num] = WardrobeTraits(**new_wardrobe_dict)

        # Actualizar evolución psicológica
        if psychological_changes is not None:
            current = updated_entry.current_psychological_evolution.get(episode_num, updated_entry.psychological)
            new_psych_dict = current.model_dump()
            new_psych_dict.update(psychological_changes)
            updated_entry.current_psychological_evolution[episode_num] = PsychologicalCore(**new_psych_dict)

        # Actualizar aliases
        if aliases is not None:
            updated_entry.current_aliases = aliases

        # Actualizar relaciones
        if relationships is not None:
            updated_entry.relationship_map.update(relationships)

        # Actualizar alianzas
        if alliances is not None:
            updated_entry.alliance_map.update({k: bool(v) for k, v in alliances.items()})

        updated_entry.updated_at = datetime.utcnow()
        return updated_entry


# Instancia por defecto para uso conveniente
default_character_bible = CharacterBibleAgent()
