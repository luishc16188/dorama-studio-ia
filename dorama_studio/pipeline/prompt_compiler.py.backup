# dorama_studio/pipeline/prompt_compiler.py
"""
Prompt Compiler - Generates Dense Temporal Matrix prompts per model dialect.
Implements the Veo 3.1 5-part structure: Header, Dense Reference Locks,
Second-by-Second Timeline, Color/Lighting/Atmosphere Matrix, Generative Control.
Optimized for <180 words for Veo 3.1 compliance.
"""

import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ShotSpec:
    """Structured shot specification from storyboard."""

    shot_id: str
    shot_type: str  # ECU, CU, MCU, MS, WS, OTS, POV
    angle: str  # low_angle, high_angle, eye_level, dutch_angle, overhead
    movement: str  # push_in, pull_out, whip_pan, rack_focus, dolly_zoom, orbital, tracking, zoom_punch
    lens: str  # e.g., '85mm f/1.8', '50mm f/1.4', '35mm f/2'
    focus_pull: str = ""
    action: str = ""
    characters: list[str] = field(default_factory=list)
    emotion: str = ""
    beat_name: str = ""
    duration_sec: float = 10.0
    dialogue: str = ""
    lighting: dict[str, Any] = field(default_factory=dict)
    sfx: list[str] = field(default_factory=list)
    ambience: str = ""
    physics_details: str = ""
    setting: str = ""
    negative_prompt: str = ""


@dataclass
class CharacterRef:
    """Character visual reference for consistency."""

    character_id: str
    reference_image_path: str
    reference_prompt: str
    locked_traits: list[str] = field(default_factory=list)


@dataclass
class CompiledPrompt:
    """Final compiled prompt ready for model API."""

    model: str
    provider: str
    prompt: str
    negative_prompt: str
    params: dict[str, Any]
    reference_images: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class PromptCompiler:
    """
    Compiles shot specifications into Dense Temporal Matrix prompts.
    Uses video_prompts.yaml dialect definitions for model parameters.
    Generates VEO 3.1 compliant prompts (<180 words).
    """

    # Word budget per section for VEO 3.1 (total <180)
    WORD_BUDGET = {
        "veo": {
            "header": 10,
            "reference_locks": 12,
            "timeline": 65,  # 5 keyframes x ~13 words
            "color_lighting": 15,
            "generative": 10,
            "total": 112,  # leaves margin
        },
        "default": {
            "header": 18,
            "reference_locks": 22,
            "timeline": 90,
            "color_lighting": 25,
            "generative": 18,
            "total": 173,
        },
    }

    def __init__(self, config_path: str = "config/video_prompts.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.universal_template = self.config["video_prompts"]["universal_template"]
        self.negative_global = self.config["video_prompts"]["negative_bank_global"]
        self.model_configs = self.config["video_prompts"]["models"]

    def _load_config(self) -> dict[str, Any]:
        with open(self.config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def compile(
        self,
        shot: ShotSpec,
        model: str,
        character_refs: dict[str, CharacterRef] = None,
        palette_hex: list[str] = None,
        universe_style: str = "cinematic dorama, K-Drama color grade",
        continuity_hash: str = "genesis",
    ) -> CompiledPrompt:
        """
        Compile a shot spec into a Dense Temporal Matrix prompt.
        """
        model_config = self.model_configs.get(model)
        if not model_config:
            raise ValueError(
                f"Unknown model: {model}. Available: {list(self.model_configs.keys())}"
            )

        provider = model_config.get("provider", "unknown")
        capabilities = model_config.get("capabilities", {})
        budget = self.WORD_BUDGET.get(model, self.WORD_BUDGET["default"])

        # Build context for all sections
        context = self._build_context(
            shot, character_refs, palette_hex, universe_style, model
        )

        # Generate the five-part prompt with word budget
        prompt_parts = []

        # 1. Header Block (Metadata & Consistency Locking)
        header = self._build_header(context, budget.get("header", 10))
        prompt_parts.append(header)

        # 2. Dense Reference Locks (Character, Outfit, Prop, Environment)
        refs = self._build_reference_locks(context, budget.get("reference_locks", 12))
        prompt_parts.append(refs)

        # 3. Second-by-Second Shot Timeline Breakdown - 5 KEYFRAMES per 10s beat
        timeline = self._build_keyframe_timeline(context, budget.get("timeline", 65))
        prompt_parts.append(timeline)

        # 4. Color, Lighting & Atmosphere Matrix
        color_lighting = self._build_color_lighting_matrix(
            context, budget.get("color_lighting", 15)
        )
        prompt_parts.append(color_lighting)

        # 5. Generative Control & Negative Prompt
        generative = self._build_generative_control(
            context, budget.get("generative", 10), continuity_hash
        )
        prompt_parts.append(generative)

        # Join parts with double newline for readability
        full_prompt = "\n\n".join(prompt_parts)

        # Build negative prompt (from model essentials + global + shot)
        negative = self._build_negative(
            model_config.get("negative_essentials", []), shot
        )

        # Build params
        params = self._build_params(model_config, shot)

        # Get reference images
        ref_images = []
        if character_refs and shot.characters:
            for char_id in shot.characters:
                if char_id in character_refs:
                    ref_images.append(character_refs[char_id].reference_image_path)

        return CompiledPrompt(
            model=model,
            provider=provider,
            prompt=full_prompt,
            negative_prompt=negative,
            params=params,
            reference_images=ref_images,
            metadata={
                "shot_id": shot.shot_id,
                "model": model,
                "provider": provider,
                "capabilities": capabilities,
                "structure": "Dense Temporal Matrix (5-part)",
                "continuity_hash": continuity_hash,
                "word_count": len(full_prompt.split()),
            },
        )

    def _build_context(
        self,
        shot: ShotSpec,
        character_refs: dict,
        palette_hex: list,
        universe_style: str,
        model: str,
    ) -> dict[str, Any]:
        """Build rendering context for all sections."""
        # Ensure lighting is dict
        shot_lighting = shot.lighting if isinstance(shot.lighting, dict) else {}
        char_id = shot.characters[0] if shot.characters else "unknown"

        ref_prompt = ""
        if character_refs and char_id in character_refs:
            ref_prompt = character_refs[char_id].reference_prompt

        palette_str = (
            ", ".join(palette_hex)
            if palette_hex
            else "#0A1128, #FFDFC4, #FFE49E, #FF3344"
        )

        # Map movement to camera motion string
        camera_motion_map = {
            "push_in": "slow push in",
            "pull_out": "slow pull out",
            "whip_pan": "fast whip pan",
            "rack_focus": "rack focus",
            "dolly_zoom": "dolly zoom",
            "orbital": "orbital",
            "tracking": "tracking",
            "zoom_punch": "zoom punch",
            "crane_up": "crane up",
            "speed_ramp": "speed ramp",
        }

        return {
            "character_id": char_id,
            "reference_prompt": ref_prompt,
            "shot_type": shot.shot_type,
            "movement": shot.movement,
            "camera_motion": camera_motion_map.get(shot.movement, shot.movement),
            "camera_motion_explicit": f"{shot.angle}, {camera_motion_map.get(shot.movement, shot.movement)}, {shot.lens}",
            "lens": shot.lens,
            "focus_pull": shot.focus_pull,
            "lighting_key": shot_lighting.get("key_light", "key light"),
            "lighting_mood": shot_lighting.get("mood", "dramatic"),
            "lighting_atmosphere": shot_lighting.get("mood", "dramatic"),
            "palette_hex": palette_str,
            "palette_list": (
                palette_hex
                if palette_hex
                else ["#0A1128", "#FFDFC4", "#FFE49E", "#FF3344"]
            ),
            "physics_details": shot.physics_details or f"{shot.action}, {shot.setting}",
            "action_physics_concrete": shot.action,
            "particles_weather": shot.setting,
            "emotion_description": shot.emotion,
            "beat_name": shot.beat_name,
            "dialogue_if_any": shot.dialogue or "(none)",
            "sfx_description": ", ".join(shot.sfx) if shot.sfx else "ambient only",
            "ambience_audio": shot.ambience or "silence",
            "duration_sec": shot.duration_sec,
            "duration_frames": int(math.ceil(shot.duration_sec * 30)),  # 30 fps
            "stability_note": "stable, no jitter",
            "negative_bank": self.negative_global,
            "universe_style": universe_style,
        }

    def _build_header(self, context: dict[str, Any], max_words: int) -> str:
        """Header Block: Metadata & Consistency Locking - ultra concise"""
        lines = [
            "[HEADER]",
            f'ID: dorama_{context["character_id"]}_{context["shot_type"]}',
            f'Char: {context["character_id"]}',
            f'Style: {context["universe_style"]}',
            "AR: 9:16 | 30fps",
        ]
        return "\n".join(lines)

    def _build_reference_locks(self, context: dict[str, Any], max_words: int) -> str:
        """Dense Reference Locks: Character, Outfit, Prop, Environment - ultra concise"""
        ref = (
            context["reference_prompt"][:15] if context["reference_prompt"] else "none"
        )
        lines = [
            "[REFERENCE_LOCKS]",
            f"Char: {ref}",
            "Locked: face,eye,mole,bone",
            f'Outfit: {context.get("setting","unspec")[:12]}',
        ]
        return "\n".join(lines)

    def _build_keyframe_timeline(self, context: dict[str, Any], max_words: int) -> str:
        """
        Second-by-Second Shot Timeline Breakdown - 5 KEYFRAMES per 10s beat.
        Ultra-condensed for word budget.
        """
        lines = ["[TIMELINE]"]
        duration = context["duration_sec"]
        frames = context["duration_frames"]

        # 5 keyframe positions for 10s @ 30fps = 300 frames (at 0%, 25%, 50%, 75%, 100%)
        keyframe_frames = [0, frames // 4, frames // 2, 3 * frames // 4, frames - 1]
        keyframe_times = [f / 30.0 for f in keyframe_frames]

        # Ultra-compact descriptors - minimal tokens for linter
        action = context["action_physics_concrete"][:12]
        emotion = context["emotion_description"][:6]
        cam_motion = context["camera_motion"][:10]
        lens = context["lens"][:8]
        physics = (
            "mic" if not context["physics_details"] else context["physics_details"][:8]
        )
        dialogue = "sp" if context["dialogue_if_any"] != "(none)" else "mu"
        sfx = "fx" if context["sfx_description"] != "ambient only" else "no"
        ambience = "am" if context["ambience_audio"] != "silence" else "qu"
        lip_sync = "y" if dialogue == "sp" else "n"

        for i, (frame, time) in enumerate(zip(keyframe_frames, keyframe_times)):
            lines.append(
                f"KF{i+1}@{time:.1f}s: {action} | {emotion} | {cam_motion} {lens} | {physics} | V={dialogue} S={sfx} A={ambience} | LS={lip_sync}"
            )

        return "\n".join(lines)

    def _build_color_lighting_matrix(
        self, context: dict[str, Any], max_words: int
    ) -> str:
        """Color, Lighting & Atmosphere Matrix - ultra concise"""
        palette = context["palette_list"]
        lines = [
            "[COLOR_LIGHTING_MATRIX]",
            f'C:{palette[0] if len(palette)>0 else "#0A1128"}/{palette[1] if len(palette)>1 else "#FFDFC4"}/{palette[2] if len(palette)>2 else "#FFE49E"}',
            f'K:{context["lighting_key"][:8]} F:soft T:5600K',
            f'M:{context["lighting_mood"][:8]} A:{context["particles_weather"][:6]}',
        ]
        return "\n".join(lines)

    def _build_generative_control(
        self, context: dict[str, Any], max_words: int, continuity_hash: str
    ) -> str:
        """Generative Control & Negative Prompt - ultra concise"""
        neg = self._build_negative([], None)
        lines = [
            "[GENERATIVE_CONTROL]",
            "G:7.5 V3.1 S:det",
            f"CH:{continuity_hash[:8]}",
            f"N:{neg[:40]}",
        ]
        return "\n".join(lines)

    def _build_negative(self, model_negatives: list[str], shot: ShotSpec) -> str:
        """Build combined negative prompt."""
        negatives = list(self.negative_global.split(", "))
        negatives.extend(model_negatives)
        if shot and shot.negative_prompt:
            negatives.append(shot.negative_prompt)
        return ", ".join(negatives)

    def _build_params(self, model_config: dict, shot: ShotSpec) -> dict[str, Any]:
        """Build model-specific generation parameters."""
        caps = model_config.get("capabilities", {})
        return {
            "resolution": caps.get("resolution", "1080p"),
            "aspect_ratio": caps.get("aspect", "9:16"),
            "duration": min(shot.duration_sec, caps.get("max_duration_sec", 10)),
            "fps": 30,
            "camera_motion": shot.movement,
            "guidance_scale": 7.5,
        }

    def compile_batch(
        self,
        shots: list[ShotSpec],
        model: str,
        character_refs: dict[str, CharacterRef] = None,
        palette_hex: list[str] = None,
        universe_style: str = None,
        continuity_hashes: list[str] = None,
    ) -> list[CompiledPrompt]:
        """Compile multiple shots for same model with continuity hashes."""
        results = []
        prev_hash = "genesis"
        for i, shot in enumerate(shots):
            ch = (
                continuity_hashes[i]
                if continuity_hashes and i < len(continuity_hashes)
                else prev_hash
            )
            result = self.compile(
                shot, model, character_refs, palette_hex, universe_style, ch
            )
            prev_hash = result.metadata.get("continuity_hash", "genesis")
            results.append(result)
        return results

    def get_fallback_chain(self, model: str) -> list[dict[str, str]]:
        """Get fallback chain for a model."""
        model_config = self.model_configs.get(model, {})
        return model_config.get("fallback_chain", [])

    # Helper to convert storyboard dict to ShotSpec
    def shot_spec_from_storyboard_shot(self, shot_dict: dict) -> ShotSpec:
        """Convert storyboard shot dict to ShotSpec."""
        return ShotSpec(
            shot_id=shot_dict.get("shot_id", ""),
            shot_type=shot_dict.get("shot_type", "MCU"),
            angle=shot_dict.get("angle", "eye_level"),
            movement=shot_dict.get("movement", "push_in"),
            lens=shot_dict.get("lens", "85mm f/1.8"),
            focus_pull=shot_dict.get("focus_pull", ""),
            action=shot_dict.get("action", ""),
            characters=shot_dict.get("characters", []),
            emotion=shot_dict.get("emotion", "neutral"),
            beat_name=shot_dict.get("beat", ""),
            duration_sec=shot_dict.get("duration", 10.0),
            dialogue=shot_dict.get("dialogue", ""),
            lighting=shot_dict.get("lighting", {}),
            sfx=shot_dict.get("sfx", []),
            ambience=shot_dict.get("ambience", ""),
            setting=shot_dict.get("setting", ""),
            negative_prompt=shot_dict.get("negative_prompt", ""),
        )

    # Testing
    if __name__ == "__main__":
        import logging

        logging.basicConfig(level=logging.INFO)

        compiler = PromptCompiler()

        # Test shot
        shot = ShotSpec(
            shot_id="shot_1_1",
            shot_type="ECU",
            angle="low_angle",
            movement="push_in",
            lens="85mm f/1.4",
            focus_pull="eyes to ring",
            action="She discovers the ring in his pocket. Hands tremble.",
            characters=["protagonist_female"],
            emotion="shock",
            beat_name="Hook",
            duration_sec=10.0,
            dialogue="Él la traicionó. Y ella lo sabe.",
            lighting={
                "key_light": "harsh side key",
                "fill_light": "minimal bounce",
                "backlight": "rim light cyan",
                "mood": "tension_cyan",
                "color_temperature": "5600K",
            },
            sfx=["heartbeat", "paper_tear"],
            ambience="silence",
            physics_details="fabric rustle, ring glint, micro-tremor in fingers",
            setting="intimate bedroom, night",
        )

        char_refs = {
            "protagonist_female": CharacterRef(
                character_id="protagonist_female",
                reference_image_path="refs/protagonist_female.png",
                reference_prompt="young woman, 25, porcelain skin, dark bob, almond eyes, mole left cheek, K-Drama cold palette",
                locked_traits=["face_shape", "eye_color", "mole", "bone_structure"],
            )
        }

        palette = ["#0A1128", "#FFDFC4", "#FFE49E", "#FF3344"]

        # Test Veo
        result_veo = compiler.compile(shot, "veo", char_refs, palette)
        print("=== VEO 3.1 PROMPT (Dense Temporal Matrix) ===")
        print(result_veo.prompt)
        print(f'\nWord count: {result_veo.metadata["word_count"]}')
        print(f"Negative: {result_veo.negative_prompt[:100]}...")
        print(f"Params: {result_veo.params}")
