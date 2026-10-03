"""Contratos (schemas) compartidos usados por los agentes."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentContract(BaseModel):
    """Contrato genérico que toda entrada/salida de agente debe cumplir."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )
    request_id: str = Field(..., description="Identificador único de la petición")
    timestamp: float = Field(..., description="Momento en que se procesó la petición")

    @field_validator("request_id")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("request_id no puede estar vacío")
        return v

class EpisodeSpecV2(BaseModel):
    """Especificación de episodio de ~90 segundos."""
    episode_id: str
    title: str
    beats: list = Field(default_factory=list, description="Micro-beats (MicroBeat Engine)")
    duration_seconds: float = Field(
        default=90.0, ge=30, le=120, description="Duracion objetivo en segundos"
    )
    season: int = Field(default=1, ge=1, description="Numero de temporada")
    episode_number: int = Field(ge=1, description="Numero de episodio dentro de la temporada")

    @field_validator("duration_seconds")
    @classmethod
    def _within_range(cls, v: float) -> float:
        if not (30 <= v <= 120):
            raise ValueError("duration_seconds debe estar entre 30 y 120 segundos")
        return v
