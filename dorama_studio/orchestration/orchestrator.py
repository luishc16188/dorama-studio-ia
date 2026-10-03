#!/usr/bin/env python

import asyncio
import json
from typing import Any


class TripleOrchestrator:
    """
    Orquestador simplificado que intenta cargar los sub-agentes
    (Claude y Codex) de manera tolerante y devuelve un resumen de los
    resultados simulados.
    """

    def __init__(self):
        # Intento de cargar agentes, ignorando errores de import
        try:
            from dorama_studio.subagents.claude_code.agent import ClaudeCodeAgent

            self.claude = ClaudeCodeAgent()
        except Exception:
            self.claude = None

        try:
            from dorama_studio.subagents.codex.agent import CodexAgent

            self.codex = CodexAgent()
        except Exception:
            self.codex = None

    async def run(self, task: str) -> dict[str, Any]:
        """
        Ejecuta la cadena de agentes y devuelve un dict con los resultados
        simulados. Si un agente no está disponible se devuelve un mensaje de error.
        """
        outputs = {}

        if self.claude:
            outputs["claude"] = self.claude.process(
                {"type": "design", "objective": task}
            )
        else:
            outputs["claude"] = {"error": "Claude no disponible"}

        if self.codex:
            outputs["codex"] = self.codex.process(
                {"type": "implementation", "objective": task}
            )
        else:
            outputs["codex"] = {"error": "Codex no disponible"}

        outputs["harness"] = {"status": "completed", "output": "análisis completado"}
        return outputs

    # Vista por consola
    async def main(self):
        import sys

        if len(sys.argv) <= 1:
            print("Uso: python orchestrator.py <tarea>")
            return
        task = " ".join(sys.argv[1:])
        result = await self.run(task)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    orchestrator = TripleOrchestrator()
    asyncio.run(orchestrator.main())
