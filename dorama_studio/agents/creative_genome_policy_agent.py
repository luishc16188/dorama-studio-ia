"""
Creative Genome Policy Agent – Administrar la estrategia 70/20/10 de aparición
de nuevos tropo, exploración y "big bets".  Responde a consultas sobre el
estado del presupuesto y si hay margen para nuevos experimentos.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.creative_genome import CreativeGenomeV2 as CreativeGenome

logger = logging.getLogger(__name__)


class CreativeGenomePolicyAgent(BaseAgent[dict, dict]):
    """Consulta y actualiza la política del Creative Genome."""

    def __init__(self):
        super().__init__("CreativeGenomePolicyAgent")
        self.genome = CreativeGenome(agent_name="policy", session_id="policy_session")

    def run(self, input_data: dict) -> dict:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, payload: dict) -> dict:
        # payload: {"action": "check" | "grants", "genre": "drama", ...}
        action = payload.get("action")
        genre = payload.get("genre", "generic")
        if action == "check":
            return self.genome.check_budget(agent_name="policy", genre=genre)
        if action == "grants":
            return {
                "proven": 10,
                "exploration": 5,
                "big_bet": 2,
            }
        return {"error": "unknown action"}

# Alias
GenomePolicy = CreativeGenomePolicyAgent
