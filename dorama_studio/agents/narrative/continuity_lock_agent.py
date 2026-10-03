"""
Continuity Lock Agent – Mantiene la consistencia entre cada `ShotSpec`.
Recibe una lista de `ShotSpec`s (del episodio) y revisa que los
atributos de continuidad (vestuario, props, iluminación, etc.) sean
coherentes con su antecedente.  Cuando detecta una violación, crea
una `ContinuitySpec` de error y la guarda como artefacto.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import ContinuitySpec, ShotSpec

logger = logging.getLogger(__name__)


class ContinuityLockAgent(BaseAgent[list[ShotSpec], list[ContinuitySpec]]):
    """Comprueba la continuidad entre tomas y genera reportes de error."""

    def __init__(self):
        super().__init__("ContinuityLockAgent")

    def run(self, input_data: list[ShotSpec]) -> list[ContinuitySpec]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, shots: list[Any]) -> list[ContinuitySpec]:
        errors: list[ContinuitySpec] = []
        last: ContinuitySpec | None = None
        for shot in shots:
            try:
                # Handle both dict and ShotSpec objects
                if isinstance(shot, dict):
                    shot_id = shot.get("shot_id", "unknown")
                    project_id = shot.get("project_id", "unknown")
                    location_id = shot.get("location_id", "unknown")
                    wardrobe_state = shot.get("wardrobe_state", {})
                    prop_state = shot.get("prop_state", {})
                    location_state = shot.get("location_state", {})
                    cur = type("obj", (object,), {
                        "wardrobe_state": wardrobe_state,
                        "prop_state": prop_state,
                        "location_state": location_state
                    })()
                else:
                    shot_id = getattr(shot, "shot_id", "unknown")
                    project_id = getattr(shot, "project_id", "unknown")
                    location_id = getattr(shot, "location_id", "unknown")
                    cur = shot.continuity

                if last:
                    # Verifica vestuario
                    if last.wardrobe_state != cur.wardrobe_state:
                        errors.append(
                            ContinuitySpec(
                                artifact_id=f"art_cont_{shot_id[:8]}",
                                artifact_type="continuity",
                                project_id=project_id,
                                location_id=location_id,
                                wardrobe_state=cur.wardrobe_state,
                                lighting_state=cur.location_state,
                                prop_state=cur.prop_state,
                                broken_items=[
                                    "vestuario distinto",
                                ],
                            )
                        )
                    # verificar props (simplificado)
                    if set(last.prop_state.keys()) != set(cur.prop_state.keys()):
                        errors.append(
                            ContinuitySpec(
                                artifact_id=f"art_cont_{shot_id[:8]}",
                                artifact_type="continuity",
                                project_id=project_id,
                                location_id=location_id,
                                wardrobe_state=cur.wardrobe_state,
                                lighting_state=cur.location_state,
                                prop_state=cur.prop_state,
                                broken_items=["props cambiados"],
                            )
                        )
                last = cur
            except Exception as e:
                logger.warning("Erro al revisar continuidad en %s: %s", shot_id, e)
        return errors

# Alias
ContinuityChecker = ContinuityLockAgent
