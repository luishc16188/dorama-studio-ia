from typing import Any

from pydantic import BaseModel


class CreativeGenomeInput(BaseModel):
    episode_num: int
    genome_data: dict[str, Any]
    mutation_context: dict[str, Any] | None = None


class CreativeGenomeOutput(BaseModel):
    genome_updated: bool
    status: str
    insights: dict[str, Any] = {}
