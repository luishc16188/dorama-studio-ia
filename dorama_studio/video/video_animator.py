"""
Video Animator Agent - Generates video prompts and handles visual production based on script metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dorama_studio.core.master_writer import Beat, MasterScript
from dorama_studio.video.model_router import ModelRouter, ShotType, VideoModel
from dorama_studio.visual.consistency_validator import CharacterConsistencyValidator


@dataclass
class VideoPrompt:
    """Represents a prompt for video generation."""

    prompt_text: str
    negative_prompt: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    seed: int | None = None
    duration_seconds: float = 5.0
    model_preference: VideoModel | None = None


class VideoAnimator:
    """
    Generates video prompts for Kling/Runway/Veo/Hailuo based on script metadata.
    Also handles visual consistency validation and model routing.
    """

    def __init__(self):
        self.model_router = ModelRouter()
        self.consistency_validator = CharacterConsistencyValidator()

        # Video style presets by genre and emotion
        self.style_presets = {
            "romance": {
                "lighting": "soft, warm, golden hour",
                "color_palette": "pastel, warm tones, soft contrasts",
                "camera_movement": "slow, smooth, graceful",
                "focus": "shallow depth of field, intimate",
            },
            "thriller": {
                "lighting": "high contrast, chiaroscuro, dramatic shadows",
                "color_palette": "cool tones, desaturated, monochromatic accents",
                "camera_movement": "dynamic, handheld, tense",
                "focus": "deep focus for tension, selective focus for reveals",
            },
            "fantasy": {
                "lighting": "ethereal, volumetric, magical glows",
                "color_palette": "vibrant, saturated, contrasting",
                "camera_movement": "sweeping, graceful, flowing",
                "focus": "selective focus on magical elements",
            },
            "comedy": {
                "lighting": "bright, even, flat lighting",
                "color_palette": "bright, saturated, cheerful",
                "camera_movement": "quick, bouncy, playful",
                "focus": "medium depth, clear facial expressions",
            },
        }

        # Aspect ratios and resolutions by platform (from platforms.yaml)
        self.platform_specs = {
            "tiktok": {
                "width": 1080,
                "height": 1920,
                "aspect_ratio": "9:16",
                "fps": 30,
            },
            "youtube_shorts": {
                "width": 1080,
                "height": 1920,
                "aspect_ratio": "9:16",
                "fps": 30,
            },
            "instagram_reels": {
                "width": 1080,
                "height": 1920,
                "aspect_ratio": "9:16",
                "fps": 30,
            },
        }

    def generate_video_prompts(
        self,
        script: MasterScript,
        platform: str = "tiktok",
        character_bible: Any | None = None,
    ) -> list[VideoPrompt]:
        """
        Generate video prompts for each beat or significant visual moment.
        """
        prompts = []
        platform_specs = self.platform_specs.get(
            platform, self.platform_specs["tiktok"]
        )

        # Generate prompt for each beat
        for i, beat in enumerate(script.beats):
            prompt = self._create_beat_video_prompt(beat, script, i, platform_specs)
            prompts.append(prompt)

        # Generate prompt for cliffhanger moment (might be separate or part of last beat)
        cliffhanger_prompt = self._create_cliffhanger_video_prompt(
            script, platform_specs
        )
        prompts.append(cliffhanger_prompt)

        return prompts

    def _create_beat_video_prompt(
        self,
        beat: Beat,
        script: MasterScript,
        beat_index: int,
        platform_specs: dict[str, Any],
    ) -> VideoPrompt:
        """Create a video prompt for a specific beat."""

        # Base description from beat action
        base_description = beat.action

        # Add emotional and visual context
        emotional_context = f"Emoción: {beat.emotion}. "
        pacing_context = f"Ritmo: {beat.pacing}. "
        tension_context = f"Tensión: {beat.tension}/10. "

        # Add camera details
        camera_details = ""
        if beat.camera:
            camera_details = f"Cámara: {beat.camera.get('shot_type', 'WS')} {beat.camera.get('angle', 'eye_level')} {beat.camera.get('movement', 'static')} {beat.camera.get('lens', '35mm')}. "

        # Add sound details for audio-visual sync
        sound_details = ""
        if beat.sound and beat.sound.get("sfx"):
            sfx_list = ", ".join(beat.sound["sfx"])
            sound_details = f"Efectos de sonido: {sfx_list}. "

        # Add subtitle if available
        subtitle_details = ""
        if beat.subtitle_en:
            subtitle_details = f"Subtítulo: '{beat.subtitle_en}'. "

        # Build full prompt
        prompt_text = (
            f"{base_description}. "
            f"{emotional_context}"
            f"{pacing_context}"
            f"{tension_context}"
            f"{camera_details}"
            f"{sound_details}"
            f"{subtitle_details}"
            f"Estilo: {self._get_style_description(script.genre, beat.emotion)}. "
            f"Formato vertical para {platform_specs['width']}x{platform_specs['height']} {platform_specs['aspect_ratio']} {platform_specs['fps']}fps."
        )

        # Negative prompt (what to avoid)
        negative_prompt = "text, watermark, logo, low quality, blurry, distorted, deformed, disfigured"

        # Parameters for video generator
        parameters = {
            "duration": beat.duration,
            "width": platform_specs["width"],
            "height": platform_specs["height"],
            "fps": platform_specs["fps"],
            "seed": beat_index * 1000
            + hash(script.title) % 10000,  # Deterministic but varied
            "guidance_scale": 7.5,
            "num_inference_steps": 25,
        }

        # Determine preferred model based on shot type and emotion
        model_preference = self._select_model_for_beat(beat, script)

        return VideoPrompt(
            prompt_text=prompt_text.strip(),
            negative_prompt=negative_prompt,
            parameters=parameters,
            seed=parameters["seed"],
            duration_seconds=beat.duration,
            model_preference=model_preference,
        )

    def _create_cliffhanger_video_prompt(
        self, script: MasterScript, platform_specs: dict[str, Any]
    ) -> VideoPrompt:
        """Create a video prompt for the cliffhanger moment."""
        # Use the last beat's action but emphasize the cliffhanger
        last_beat = script.beats[-1] if script.beats else None

        base_description = (
            script.cliffhanger.visual
            if hasattr(script, "cliffhanger") and script.cliffhanger.visual
            else "Momento de cliffhanger sin resolución"
        )
        if last_beat:
            base_description = f"{last_beat.action} leading to: {base_description}"

        emotional_context = f"Emoción: {script.cliffhanger.__dict__.get('emotion', 'determinacion')} (urgency: {script.cliffhanger.urgency}/10). "
        pacing_context = "Ritmo: hyper (cliffhanger moment). "
        tension_context = f"Tensión: {script.cliffhanger.urgency}/10. "

        camera_details = "Cámara: ECU eye_level push_in 85mm f/1.4 (focusing on the revelation/object). "

        sound_details = ""
        if script.cliffhanger.__dict__.get("urgency", 5) >= 8:
            sound_details = "Efectos de sonido: tension_pulse_low, heartbeat_rise. "

        subtitle_details = ""
        if hasattr(script.cliffhanger, "question") and script.cliffhanger.question:
            subtitle_details = f"Subtítulo: '{script.cliffhanger.question[:50]}...'. "

        prompt_text = (
            f"{base_description}. "
            f"{emotional_context}"
            f"{pacing_context}"
            f"{tension_context}"
            f"{camera_details}"
            f"{sound_details}"
            f"{subtitle_details}"
            f"Estilo: {self._get_style_description(script.genre, 'tension')}. "
            f"Formato vertical para {platform_specs['width']}x{platform_specs['height']} {platform_specs['aspect_ratio']} {platform_specs['fps']}fps. "
            f"Enfocar en el elemento que genera la pregunta sin respuesta."
        )

        negative_prompt = "text, watermark, logo, resolution low, blurry, distorted, cut off, incomplete"

        parameters = {
            "duration": 5.0,  # Cliffhanger moment is usually shorter but impactful
            "width": platform_specs["width"],
            "height": platform_specs["height"],
            "fps": platform_specs["fps"],
            "seed": 9999 + hash(script.title) % 10000,
            "guidance_scale": 8.0,
            "num_inference_steps": 30,
        }

        model_preference = self._select_model_for_cliffhanger(script)

        return VideoPrompt(
            prompt_text=prompt_text.strip(),
            negative_prompt=negative_prompt,
            parameters=parameters,
            seed=parameters["seed"],
            duration_seconds=5.0,
            model_preference=model_preference,
        )

    def _get_style_description(self, genre: str, emotion: str) -> str:
        """Get style description based on genre and emotion."""
        base_style = self.style_presets.get(genre, self.style_presets["romance"])

        # Adjust based on emotion
        emotion_modifiers = {
            "tension": {
                "lighting": "high contrast, dramatic shadows",
                "color_palette": "cool tones, desaturated",
            },
            "sorpresa": {
                "lighting": "sudden flashes, stark contrasts",
                "color_palette": "vibrant, saturated",
            },
            "miedo": {
                "lighting": "low key, shadows, darkness",
                "color_palette": "monochromatic, cold tones",
            },
            "indignacion": {
                "lighting": "harsh, directional, unflattering",
                "color_palette": "warm vs cold contrast",
            },
            "esperanza": {
                "lighting": "golden hour, warm rays, lens flares",
                "color_palette": "warm, hopeful tones",
            },
            "dolor": {
                "lighting": "soft, diffused, muted",
                "color_palette": "desaturated, cool tones",
            },
            "recompensa": {
                "lighting": "bright, uplifting, lens flares",
                "color_palette": "vibrant, saturated, warm",
            },
            "nueva_amenaza": {
                "lighting": "ominous, looming shadows, gradual darkening",
                "color_palette": "darkening palette",
            },
            "determinacion": {
                "lighting": "strong directional, purposeful lighting",
                "color_palette": "strong contrasts, bold colors",
            },
            "curiosidad": {
                "lighting": "directional, investigative, spotlight",
                "color_palette": "selective color highlighting",
            },
        }

        style = base_style.copy()
        if emotion in emotion_modifiers:
            for key, value in emotion_modifiers[emotion].items():
                style[key] = value

        return f"Iluminación: {style['lighting']}. Paleta de colores: {style['color_palette']}. Movimiento de cámara: {style['camera_movement']}. Enfoque: {style['focus']}."

    def _select_model_for_beat(
        self, beat: Beat, script: MasterScript
    ) -> VideoModel | None:
        """Select the optimal video model for a beat based on shot type and content."""
        # Determine shot type from action and emotion
        shot_type = self._classify_shot_type(beat, script)
        return self.model_router.route_by_type(shot_type, beat.duration)

    def _select_model_for_cliffhanger(self, script: MasterScript) -> VideoModel | None:
        """Select model for cliffhanger moment."""
        # Cliffhangers often benefit from models good at emotional reveals and tension
        shot_type = (
            ShotType.ROMANCE_INTIMATE
            if script.genre == "romance"
            else ShotType.TEMPORAL_CONTINUITY
        )
        return self.model_router.route_by_type(shot_type, 5.0)  # 5 second cliffhanger

    def _classify_shot_type(self, beat: Beat, script: MasterScript) -> ShotType:
        """Classify the shot type based on beat content."""
        action_lower = beat.action.lower()
        emotion = beat.emotion

        # Audio-numeric beats (lip-sync critical, dialogue heavy)
        if (
            beat.sound
            and beat.sound.get("music_cue")
            and "lip" in beat.sound.get("music_cue", "").lower()
        ):
            return ShotType.AUDIO_NATIVE

        # Multiple characters interaction
        if len(beat.characters_present) >= 2:
            return ShotType.MULTI_CHARACTER

        # Action/movement based
        action_keywords = [
            "corre",
            "salta",
            "lucha",
            "pelea",
            "persigue",
            "escapa",
            "lanza",
            "dispara",
            "cae",
            "explota",
        ]
        if any(keyword in action_lower for keyword in action_keywords):
            return ShotType.ACTION_MOVEMENT

        # Romance/intimate moments
        romance_keywords = [
            "abraza",
            "besa",
            "mano",
            "cariño",
            "amor",
            "mirada",
            "susurro",
            "cercanía",
        ]
        if any(keyword in action_lower for keyword in romance_keywords) or emotion in [
            "amor",
            "ternura",
            "intimidad",
        ]:
            return ShotType.ROMANCE_INTIMATE

        # Dialogue heavy
        if len(beat.dialogue.split()) > 3:  # More than just a few words
            return ShotType.DIALOGUE_STATIC

        # Environmental/scenery
        if any(
            keyword in action_lower
            for keyword in [
                "paisaje",
                "ciudad",
                "naturaleza",
                "cielo",
                "montaña",
                "mar",
            ]
        ):
            return ShotType.ENVIRONMENTAL

        # Visual effects / magical
        if any(
            keyword in action_lower
            for keyword in [
                "magia",
                "brillo",
                "resplandor",
                "efecto",
                "sobrenatural",
                "poder",
            ]
        ):
            return ShotType.VISUAL_EFFECTS

        # Default to environmental if unsure
        return ShotType.ENVIRONMENTAL

    def validate_visual_consistency(
        self,
        character_bible: CharacterBible,
        video_frames: list[Any],  # Would be actual frames in real implementation
        episode_num: int,
        scene_num: int,
    ) -> bool:
        """
        Validate visual consistency of generated video.
        In real implementation, this would check actual frames against character bible.
        For now, return True as placeholder.
        """
        # Placeholder - in reality would use CLIP similarity etc.
        return True


# Convenience function
def generate_video_prompts_from_script(
    script: MasterScript, platform: str = "tiktok", character_bible: Any | None = None
) -> list[VideoPrompt]:
    """Convenience function to generate video prompts from a script."""
    animator = VideoAnimator()
    return animator.generate_video_prompts(script, platform, character_bible)


if __name__ == "__main__":
    # Quick test
    print("VideoAnimator module loaded successfully")
