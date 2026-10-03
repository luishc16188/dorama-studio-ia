"""
Video Animator Agent - Generates video prompts for animation.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.persistence import persistence
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext

logger = logging.getLogger(__name__)


class VideoAnimatorAgent(BaseAgent[PipelineContext, PipelineContext]):
    """
    Agent 11: Video Animator
    Generates video prompts for Kling/Runway/Veo/Hailuo based on script metadata.
    """

    InputSchema = PipelineContext
    OutputSchema = PipelineContext  # We'll update context with visual_prompts

    def __init__(self):
        super().__init__("VideoAnimatorAgent")
        self.agent_name = "VideoAnimatorAgent"

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the video animator agent."""
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

    def _process(self, context: Any) -> Any:
        """
        Process the context to generate video prompts.
        Handles both PipelineContext and VideoAnimatorInput.
        """
        start = time.time()
        try:
            if hasattr(context, 'project_id') and hasattr(context, 'episode_id'):
                # It's a PipelineContext
                return self._process_pipeline_context(context, start)
            else:
                # It's a VideoAnimatorInput or dict
                return self._process_video_animator_input(context, start)
        except Exception as e:
            if hasattr(context, 'project_id') and hasattr(context, 'episode_id'):
                return AgentResult(
                    success=False,
                    agent_name=self.agent_name,
                    error=str(e),
                    recoverable=True,
                    latency_ms=int((time.time() - start) * 1000),
                )
            else:
                from dorama_studio.agents.schemas.video_animator_schemas import VideoAnimatorOutput
                return VideoAnimatorOutput(
                    video_prompts=[],
                    status="error",
                    total_prompts=0
                )

    def _process_pipeline_context(self, context: PipelineContext, start: float) -> AgentResult:
        """Process PipelineContext and return AgentResult."""
        logger.info(
            f"Video Animator agent processing episode {context.episode_num}"
        )

        # Extract master script from context
        master_script = context.master_script or {}
        episode_num = context.episode_num

        # Generate visual direction from master script
        visual_direction = self._generate_visual_direction(master_script, context)

        # Simple video prompt generation logic based on master script
        video_prompts = []

        # Generate video prompts based on master script elements
        script_parts = [
            master_script.get("script_beginning", ""),
            master_script.get("script_development", ""),
            master_script.get("script_resolution", ""),
        ]

        # Extract themes/elements from script
        all_text = " ".join(script_parts).lower()

        # Generate prompts based on detected themes
        if any(
            word in all_text
            for word in [
                "traición",
                "traicion",
                "conflicto",
                "acción",
                "pelea",
                "persecución",
                "acción",
            ]
        ):
            video_prompts.append(
                {
                    "prompt_id": f"vid_{context.episode_num}_001",
                    "description": "Secuencia de tensión y conflicto",
                    "duration": 10.0,
                    "style": "noir",
                    "elements": ["tensión", "conflicto", "miradas intensas"],
                }
            )

        if any(
            word in all_text
            for word in ["diálogo", "conversación", "susurro", "diálogo", "charla"]
        ):
            video_prompts.append(
                {
                    "prompt_id": f"vid_{context.episode_num}_002",
                    "description": "Diálogo íntimo",
                    "duration": 15.0,
                    "style": "intimate",
                    "elements": [
                        "primer_plano",
                        "iluminación_suave",
                        "enfoque_selectivo",
                    ],
                }
            )

        if any(
            word in all_text
            for word in [
                "emocional",
                "triste",
                "llanto",
                "dolor",
                "revelación",
                "emoción",
            ]
        ):
            video_prompts.append(
                {
                    "prompt_id": f"vid_{context.episode_num}_003",
                    "description": "Escena emocional",
                    "duration": 20.0,
                    "style": "emotional",
                    "elements": [
                        "luz_directa",
                        "expresiones_faciales",
                        "música_sutil",
                    ],
                }
            )

        # If no specific prompts generated, add a default
        if not video_prompts:
            video_prompts.append(
                {
                    "prompt_id": f"vid_{context.episode_num}_default",
                    "description": "Escena general del episodio",
                    "duration": 10.0,
                    "style": "cinematic",
                    "elements": [
                        "composición_equilibrada",
                        "iluminación_dramática",
                    ],
                }
            )

        # Persist log
        log_id = persistence.log_generation(
            project_id=context.project_id,
            agent_name=self.agent_name,
            input_data={
                "episode_num": context.episode_num,
                "master_script_keys": list(master_script.keys()),
            },
            output_data={
                "video_prompts": video_prompts,
                "visual_direction": visual_direction,
            },
            model_used="deterministic",
            latency_ms=int((time.time() - start) * 1000),
            episode_id=context.episode_id or "",
        )

        return AgentResult(
            success=True,
            agent_name=self.agent_name,
            output_data={
                "video_prompts": video_prompts,
                "visual_direction": visual_direction,
            },
            context_updates={
                "visual_prompts": video_prompts,
                "visual_direction": visual_direction,
            },
            logs=[{"id": log_id}],
            latency_ms=int((time.time() - start) * 1000),
            tokens_used=0,
            model_used="deterministic",
        )

    def _process_video_animator_input(self, context: Any, start: float):
        """Process VideoAnimatorInput and return VideoAnimatorOutput."""
        from dorama_studio.agents.schemas.video_animator_schemas import VideoAnimatorOutput

        episode_num = getattr(context, 'episode_num', 1)
        master_script = getattr(context, 'master_script', {}) or {}
        visual_direction = getattr(context, 'visual_direction', {}) or {}
        animation_style = getattr(context, 'animation_style', 'cinematic')

        # Generate video prompts based on input
        video_prompts = []

        # Extract themes/elements from master script
        script_parts = [
            master_script.get("script_beginning", ""),
            master_script.get("script_development", ""),
            master_script.get("script_resolution", ""),
        ]
        all_text = " ".join(script_parts).lower()

        # Generate prompts based on detected themes
        if any(
            word in all_text
            for word in [
                "traición",
                "traicion",
                "conflicto",
                "acción",
                "pelea",
                "persecución",
                "acción",
            ]
        ) or master_script.get("has_action", False):
            video_prompts.append(
                {
                    "prompt_id": f"vid_{episode_num}_001",
                    "description": "Secuencia de tensión y conflicto",
                    "duration": 10.0,
                    "style": animation_style,
                    "elements": ["tensión", "conflicto", "miradas intensas"],
                }
            )

        if any(
            word in all_text
            for word in ["diálogo", "conversación", "susurro", "diálogo", "charla"]
        ) or master_script.get("has_dialogue", False):
            video_prompts.append(
                {
                    "prompt_id": f"vid_{episode_num}_002",
                    "description": "Diálogo íntimo",
                    "duration": 15.0,
                    "style": "intimate",
                    "elements": [
                        "primer_plano",
                        "iluminación_suave",
                        "enfoque_selectivo",
                    ],
                }
            )

        if any(
            word in all_text
            for word in [
                "emocional",
                "triste",
                "llanto",
                "dolor",
                "revelación",
                "emoción",
            ]
        ) or master_script.get("has_emotional_scene", False):
            video_prompts.append(
                {
                    "prompt_id": f"vid_{episode_num}_003",
                    "description": "Escena emocional",
                    "duration": 20.0,
                    "style": "emotional",
                    "elements": [
                        "luz_directa",
                        "expresiones_faciales",
                        "música_sutil",
                    ],
                }
            )

        # If no specific prompts generated, add a default
        if not video_prompts:
            video_prompts.append(
                {
                    "prompt_id": f"vid_{episode_num}_default",
                    "description": "Escena general del episodio",
                    "duration": 10.0,
                    "style": "cinematic",
                    "elements": [
                        "composición_equilibrada",
                        "iluminación_dramática",
                    ],
                }
            )

        return VideoAnimatorOutput(
            video_prompts=video_prompts,
            status="completed",
            total_prompts=len(video_prompts)
        )

    def _generate_visual_direction(self, master_script: dict, context: Any) -> dict:
        """Generate visual direction from master script."""
        direction = {
            "style": "noir",
            "color_palette": ["#1a1a2e", "#16213e", "#0f3460", "#e94560"],
            "lighting": "high_contrast",
            "camera_style": "handheld_intimate",
            "key_frames": [],
        }

        # Extract key moments from script
        script_parts = [
            master_script.get("script_beginning", ""),
            master_script.get("script_development", ""),
            master_script.get("script_resolution", ""),
        ]

        for i, part in enumerate(script_parts):
            if part:
                direction["key_frames"].append(
                    {
                        "beat": i + 1,
                        "description": part[:100] + "..." if len(part) > 100 else part,
                        "mood": self._detect_mood(part),
                    }
                )

        return direction

    def _detect_mood(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["traicion", "conflicto", "pelea", "tensión"]):
            return "tension"
        elif any(w in text_lower for w in ["amor", "beso", "abrazo", "ternura"]):
            return "romantic"
        elif any(w in text_lower for w in ["misterio", "secreto", "oculto", "enigma"]):
            return "mystery"
        elif any(w in text_lower for w in ["triste", "llanto", "dolor", "pérdida"]):
            return "sadness"
        elif any(w in text_lower for w in ["alegria", "feliz", "victoria", "triunfo"]):
            return "joy"
        return "neutral"
