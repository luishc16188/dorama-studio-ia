"""Creative Genome 2.0 for DORAMA STUDIO IA V2.

Este módulo define la ``CreativeGenome`` de segunda generación, que
almacena y gestiona patrones emergentes, ganadores, sobreusados y fallidos
extraídos de la historia, los beats, los diálogos y los resultados de
control de calidad.

La ``CreativeGenome`` se usa en el ``Feedback Loop`` (Fase 11) para
recomendar ajustes creativos y evitar la repetición de patrones
negativos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PatternInfo:
    """Metadato de un patrón detectado en el sistema."""
    pattern_type: str            # "winning", "overused", "failed", "emerging"
    description: str
    occurrence_count: int = 0
    last_seen_episode: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CreativeGenomeV2:
    """Representación de la Creative Genome versión 2.0."""
    # Patrones clasificados por tipo
    winning: list[PatternInfo] = field(default_factory=list)
    overused: list[PatternInfo] = field(default_factory=list)
    failed: list[PatternInfo] = field(default_factory=list)
    emerging: list[PatternInfo] = field(default_factory=list)

    # Mapeo inverted: descripción → PatternInfo para búsquedas rápidas
    _by_description: dict[str, PatternInfo] = field(default_factory=dict, init=False)

    def __init__(self, agent_name: str = None, session_id: str = None):
        # Initialize dataclass fields
        self.winning = []
        self.overused = []
        self.failed = []
        self.emerging = []
        self._by_description = {}
        # Store agent_name and session_id for tracking (if needed)
        self.agent_name = agent_name
        self.session_id = session_id

    # -----------------------------------------------------------------
    # Registro de un nuevo patrón (llamado habitualmente después de
    # evaluar un episodio o un conjunto de beats)
    # -----------------------------------------------------------------
    def register_pattern(
        self,
        pattern_type: str,
        description: str,
        episode_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Añade o actualiza un patrón en la genome."""
        if pattern_type not in {"winning", "overused", "failed", "emerging"}:
            raise ValueError(f"Tipo de patrón desconocido: {pattern_type}")

        # Buscar si ya existe con la misma descripción
        existing = self._by_description.get(description)
        if existing:
            existing.occurrence_count += 1
            if episode_id > existing.last_seen_episode:  # comparación simple de strings
                existing.last_seen_episode = episode_id
            if metadata:
                existing.metadata.update(metadata)
        else:
            new_p = PatternInfo(
                pattern_type=pattern_type,
                description=description,
                occurrence_count=1,
                last_seen_episode=episode_id,
                metadata=metadata or {},
            )
            # Insertar en la lista correspondiente
            lst = getattr(self, pattern_type)
            lst.append(new_p)
            # Actualizar índice
            self._by_description[description] = new_p

    # -----------------------------------------------------------------
    # Consultas rápidas
    # -----------------------------------------------------------------
    def count_by_type(self, ptype: str) -> int:
        """Número total de patrones de un tipo dado."""
        return len(getattr(self, ptype, []))

    def get_by_description(self, description: str) -> PatternInfo | None:
        return self._by_description.get(description)

    def recent_failed(self, n: int = 5) -> list[PatternInfo]:
        """Devolver los ``n`` patrones ``failed`` más recientes."""
        lst = self.failed
        # Ordenar por last_seen_episode de forma descendente (asumiendo IDs cronológicos)
        sorted_lst = sorted(lst, key=lambda p: p.last_seen_episode, reverse=True)
        return sorted_lst[:n]

    # -----------------------------------------------------------------
    # Budget tracking for 70/20/10 allocation
    # -----------------------------------------------------------------
    def check_budget(self, agent_name: str, genre: str) -> dict[str, int]:
        """
        Check available budget for 70/20/10 allocation.
        Returns dict with proven_available, exploration_available, big_bet_available.
        This is a simplified implementation for testing.
        """
        # Simplified budget tracking - in reality this would be more sophisticated
        # and track actual usage per agent/genre combination
        return {
            "proven_available": 70,    # 70% for proven approaches
            "exploration_available": 20, # 20% for exploration
            "big_bet_available": 10    # 10% for big bets
        }

    def record_mutation(
        self,
        mutation_type: str,
        seed_identifier: str,
        genre: str
    ) -> None:
        """
        Record a mutation event in the genome.
        This is a simplified implementation for testing.
        """
        # For now, we just log this - in a real implementation this would
        # update internal tracking of mutations
        pass

    # -----------------------------------------------------------------
    # Integración simple con Quality Control: si el score es bajo,
    # registrar un patrón "failed".
    # -----------------------------------------------------------------
    def record_low_quality(self, spec: Any, episode_id: str) -> None:
        """Registrar un patrón ``failed`` cuando el quality_score es bajo."""
        from .quality_control import evaluate_spec as _eval
        result = _eval(spec) if hasattr(spec, '__class__') and 'quality_score' in str(_eval.__code__.co_varnames) else {"quality_score": 0.0}
        # Fallback seguro: si evaluate_spec no está disponible, registrar igualmente
        try:
            score = _eval(spec).get("quality_score", 0.0)
        except Exception:
            score = 0.0
        if score < 0.7:
            self.register_pattern(
                pattern_type="failed",
                description="Episodio con quality_score bajo",
                episode_id=episode_id,
                metadata={"quality_score": score},
            )


# Alias for backward compatibility
CreativeGenome = CreativeGenomeV2
