"""
Feedback Loop Agent – Registra comentarios de usuarios y los convierte en tareas de mejora.
Conecta a los artefactos `Idea` y `UserFeedback` y produce `FeedbackInstructions`.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import FeedbackInstructions

logger = logging.getLogger(__name__)


class FeedbackLoopAgent(BaseAgent[dict, FeedbackInstructions]):
    """Transforma comentarios de usuarios en instrucciones de mejora."""

    def __init__(self):
        super().__init__("FeedbackLoopAgent")

    def run(self, input_data: dict) -> FeedbackInstructions:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, payload: dict) -> FeedbackInstructions:
        # payload debe contener lista de comentarios y meta-información de producción
        comments = payload.get("comments", [])
        instructions: list[str] = []
        for c in comments:
            # Unión simple: "Presentar ejecución de X y observar A"
            if "probar" in c.lower():
                instructions.append("Ejecutar la función X y reportar resultados.")
            if "micro" in c.lower():
                instructions.append("Resaltar la micro-animación entre Y y Z.")
        return FeedbackInstructions(instructions=instructions)

# Alias
Feedback = FeedbackLoopAgent
