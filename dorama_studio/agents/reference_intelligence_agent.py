"""
Referencia de Inteligencia –
Se encarga de cargar el *Reference Bible* y los datos de contexto a nivel de temporada.
Extrae patrones de producción del video de referencia para crear DNA de producción.
"""

from __future__ import annotations

import json
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext


class ReferenceIntelligenceAgent(BaseAgent):
    """Agent that loads the Reference Bible and attaches its ID to the state.
    Extracts production DNA patterns from reference video analysis.
    """

    def __init__(self):
        super().__init__("ReferenceIntelligenceAgent")
        self.reference_dna = self._load_reference_dna()

    def _load_reference_dna(self) -> dict[str, Any]:
        """Load reference DNA patterns from forensic analysis documents."""
        # In a real implementation, this would parse the actual forensic documents
        # For now, we'll extract key patterns from DORAMA_REFERENCE_FORENSIC_V2_EXTENDED.md
        reference_dna = {
            "video_properties": {
                "duration": 4247.208345,  # ~70:47.21
                "resolution": "202x360",
                "aspect_ratio": "9:16",
                "fps": 24,
                "video_codec": "H.264 Main",
                "audio_codec": "AAC-LC",
                "audio_sample_rate": 44100,
                "audio_channels": 2,
                "total_bitrate": 357  # kb/s
            },
            "temporal_grammar": {
                "segmentation_stats": {
                    "mean_interval": 6.425,
                    "median_interval": 3.75,
                    "p10": 1.0,
                    "p25": 1.5,
                    "p75": 8.0,
                    "p90": 15.0,
                    "p95": 21.75,
                    "p99": 37.5,
                    "min": 0.5,
                    "max": 94.5
                },
                "distribution": {
                    "0-1s": 41,
                    "1-2s": 142,
                    "2-3s": 97,
                    "3-5s": 114,
                    "5-8s": 95,
                    "8-12s": 74,
                    "12-20s": 60,
                    "20-30s": 25,
                    "30-60s": 12,
                    "60+s": 1
                },
                "first_90s_intervals": [
                    6.25, 2.50, 6.25, 1.25, 1.00, 1.00, 1.00, 1.50, 12.00, 2.00,
                    13.50, 0.75, 7.75, 4.75, 1.00, 1.00, 7.25, 8.00, 11.25
                ]
            },
            "narrative_dna": {
                "world_promise": "ESTATUS / MUNDO DE LUJO",
                "character_identification": "PRESENTACIÓN DE PERSONAJES",
                "desire_object": "OBJETO DE DESEO / REGALO",
                "micro_reward": "REACCIÓN EMOCIONAL",
                "status_contrast": "PREPARACIÓN / DESPLAZAMIENTO",
                "spatial_transition": "CAMBIO DE INTERIOR DE LUJO A CIUDAD",
                "threat": "VEHÍCULO EN MOVIMIENTO",
                "reaction": "LA MADRE VE EL PELIGRO Y REACCIONA",
                "consequence": "SHOCK + LLAMADA DE EMERGENCIA",
                "unresolved_social_conflict": "CONFLICTO INTERPERSONAL + REVERSIÓN"
            },
            "editing_dna": {
                "visual_change_density": "62 candidatos de cambio en primeros 90s (~1.41s media)",
                "pattern": "Edición de alta frecuencia que aumenta alrededor de momentos de conflicto",
                "audio_pattern": "Silencio utilizado para abrir espacio a reacción y cambio de emoción"
            },
            "camera_dna": {
                "techniques": [
                    "Gran plano/establishing para posicionar el mundo",
                    "Plano medio para interacción",
                    "Primer plano para emoción",
                    "Insertos para objetos de valor narrativo",
                    "Vista superior para transición de espacio y cambio de energía",
                    "Cambios rápidos de escala cuando sube la tensión",
                    "Eyelines relativamente claros en confrontación",
                    "Composición frontal limpia para tarjetas de identidad"
                ]
            },
            "sound_dna": {
                "structure": "DIALOGUE + ROOM TONE + AMBIENCE + FOLEY + SFX EVENTS + MUSIC STATE + SILENCE",
                "music_states": ["ENTER", "BUILD", "HOLD", "DROP", "HIT", "RELEASE", "EXIT"],
                "silence_as_tool": "El silencio se utiliza para crear impacto y recuperación"
            },
            "acting_dna": {
                "patterns": [
                    "mirada → objeto",
                    "objeto → rostro",
                    "rostro → amenaza",
                    "giro de cabeza → entrada del siguiente plano",
                    "reacción facial → transición de información",
                    "manos/objetos como señales narrativas"
                ],
                "secondary_motion": "Cabello, ropa, entorno funcionan como soporte, no deben competir con evento principal"
            },
            "attention_psychology": {
                "curiosity_gap": "Espectador recibe información suficiente para entender escenario pero no suficiente para conocer destino del personaje",
                "open_loops": "Objeto, relación o frase prepara consecuencia posterior",
                "status_contrast": "Conflicto se entiende rápidamente porque cada personaje carga código social/visual diferente",
                "threat_escalation": "Peligro pasa de 'vida lujosa' a 'riesgo para un niño' sin cambiar género",
                "information_compression": "Tarjetas de personaje y insertos reducen exposición verbal",
                "reaction_chain": "objeto/amenaza → percepción → rostro → reacción verbal → consecuencia",
                "reward_then_threat": "Entrega micro-recompensa antes de introducir peligro para aumentar peso de pérdida potencial"
            }
        }
        return reference_dna

    def _process(self, ctx: PipelineContext) -> AgentResult:
        """Process the context to load reference DNA and attach to state."""
        # Generate a reference ID based on the loaded DNA
        ref_id = f"ref_dna_{hash(json.dumps(self.reference_dna, sort_keys=True)) % 10000:04d}"

        # Update state with reference DNA
        if hasattr(ctx, 'state') and ctx.state:
            # Handle different state types
            state_dict = ctx.state.dict() if hasattr(ctx.state, 'dict') else dict(ctx.state) if hasattr(ctx.state, '__dict__') else {}
            state_dict['reference_dna'] = self.reference_dna
            state_dict['reference_bible_ref'] = ref_id

            # Try to update the state object if it supports it
            if hasattr(ctx.state, '__dict__'):
                for key, value in state_dict.items():
                    setattr(ctx.state, key, value)
            elif hasattr(ctx.state, '__setitem__'):
                for key, value in state_dict.items():
                    ctx.state[key] = value

        return AgentResult(
            success=True,
            agent_name=self.name,
            output_data={
                "reference_dna_loaded": True,
                "reference_id": ref_id,
                "dna_sections": list(self.reference_dna.keys())
            },
            context_updates={
                "reference_dna": self.reference_dna,
                "reference_bible_ref": ref_id
            },
            logs=[{
                "step": "ReferenceIntelligence",
                "ref_id": ref_id,
                "dna_sections_loaded": list(self.reference_dna.keys())
            }],
        )
