"""Publisher Agent - Handles multi-platform publishing of generated episodes.
Manages platform-specific formatting, scheduling, and API integration.
"""

import logging
import time
from collections import deque
from datetime import datetime
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import PublisherAgentOutputSchema

logger = logging.getLogger(__name__)


class PublisherAgent(BaseAgent[dict[str, Any], PublisherAgentOutputSchema]):
    """
    Publisher Agent that takes rendered episodes and publishes them
    to multiple platforms (TikTok, YouTube Shorts, Instagram Reels).
    """

    InputSchema = dict[str, Any]
    OutputSchema = PublisherAgentOutputSchema

    def __init__(self):
        super().__init__("PublisherAgent")

        # Platform configurations from config/platforms.yaml
        self._platform_cache = deque(maxlen=10)
        self._cache_ttl = 3600  # 1 hour
        self.platform_configs = {
            "tiktok": {
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "max_duration": 180,
                "optimal_duration": 90,
                "fps": 30,
                "video_codec": "libx264",
                "audio_codec": "aac",
                "bitrate": "8000k",
                "hashtags_max": 5,
                "required_hashtags": ["#dorama", "#kdrama", "#cdrama", "#microdrama"],
                "api_endpoint": "https://open.tiktokapis.com/v2/post/publish/video/init/",
                "scopes": ["video.publish", "video.upload"],
            },
            "youtube_shorts": {
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "max_duration": 60,
                "optimal_duration": 55,
                "fps": 30,
                "video_codec": "libx264",
                "audio_codec": "aac",
                "bitrate": "8000k",
                "hashtags_max": 3,
                "required_hashtags": ["#Shorts", "#Dorama", "#KDrama"],
                "api_endpoint": "https://www.googleapis.com/upload/youtube/v3/videos",
                "scopes": ["https://www.googleapis.com/auth/youtube.upload"],
            },
            "instagram_reels": {
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "max_duration": 90,
                "optimal_duration": 60,
                "fps": 30,
                "video_codec": "libx264",
                "audio_codec": "aac",
                "bitrate": "8000k",
                "hashtags_max": 30,
                "required_hashtags": [
                    "#Reels",
                    "#Dorama",
                    "#KDrama",
                    "#CDrama",
                    "#Microdrama",
                ],
                "api_endpoint": "https://graph.facebook.com/v19.0/me/media",
                "scopes": ["instagram_content_publish", "instagram_manage_insights"],
            },
        }

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the publisher agent."""
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

    def _process(self, validated_input: dict[str, Any]) -> PublisherAgentOutputSchema:
        """
        Process episode for multi-platform publishing.

        Args:
            validated_input: Dict containing episode_id, video_path, metadata, platforms, schedule

        Returns:
            PublisherAgentOutputSchema with publishing results per platform
        """
        episode_id = validated_input.get("episode_id", "unknown")
        video_path = validated_input.get("video_path", "")
        metadata = validated_input.get("metadata", {})
        platforms = validated_input.get(
            "platforms", ["tiktok", "youtube_shorts", "instagram_reels"]
        )
        schedule = validated_input.get("schedule", "immediate")
        cross_post_config = validated_input.get("cross_post", {})

        self._cleanup_cache()
        logger.info(f"Publishing episode {episode_id} to platforms: {platforms}")

        published_episodes = {}

        for platform in platforms:
            if platform not in self.platform_configs:
                logger.warning(f"Unknown platform: {platform}, skipping")
                continue

            try:
                result = self._publish_to_platform(
                    platform,
                    episode_id,
                    video_path,
                    metadata,
                    schedule,
                    cross_post_config,
                )
                published_episodes[platform] = result
            except Exception as e:
                logger.error(f"Failed to publish to {platform}: {e}")
                published_episodes[platform] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        return PublisherAgentOutputSchema(published_episodes=published_episodes)

    def _publish_to_platform(
        self,
        platform: str,
        episode_id: str,
        video_path: str,
        metadata: dict,
        schedule: str,
        cross_post_config: dict,
    ) -> dict[str, Any]:
        """Publish episode to a specific platform."""
        config = self.platform_configs[platform]

        # Validate video meets platform specs
        validation = self._validate_video(video_path, config)
        if not validation["valid"]:
            return {
                "status": "validation_failed",
                "errors": validation["errors"],
                "timestamp": datetime.now().isoformat(),
            }

        # Prepare platform-specific metadata
        platform_metadata = self._prepare_metadata(platform, metadata, config)

        # Generate hashtags
        hashtags = self._generate_hashtags(platform, metadata, config)

        # Prepare description/Caption
        description = self._prepare_description(platform, metadata, config)

        # In production: call platform API
        # For now, simulate successful publish
        publish_result = self._simulate_publish(
            platform,
            episode_id,
            video_path,
            platform_metadata,
            hashtags,
            description,
            schedule,
        )

        return publish_result

    def _validate_video(self, video_path: str, config: dict) -> dict[str, Any]:
        """Validate video meets platform specifications."""
        errors = []

        # In production, use ffprobe to check actual video properties
        # For now, assume valid if path provided
        if not video_path:
            errors.append("No video path provided")

        return {"valid": len(errors) == 0, "errors": errors}

    def _prepare_metadata(
        self, platform: str, metadata: dict, config: dict
    ) -> dict[str, Any]:
        """Prepare platform-specific metadata."""
        return {
            "title": metadata.get("title", "Dorama Episode"),
            "description": metadata.get("description", ""),
            "tags": metadata.get("tags", []),
            "category": "Entertainment",
            "privacy": "public",
            "made_for_kids": False,
        }

    def _generate_hashtags(
        self, platform: str, metadata: dict, config: dict
    ) -> list[str]:
        """Generate platform-appropriate hashtags."""
        hashtags = list(config["required_hashtags"])

        # Add genre/topic hashtags
        genre = metadata.get("genre", "").lower()
        if genre:
            hashtags.append(f"#{genre}")

        # Add custom hashtags from metadata
        custom_tags = metadata.get("hashtags", [])
        for tag in custom_tags:
            if not tag.startswith("#"):
                tag = f"#{tag}"
            if tag not in hashtags:
                hashtags.append(tag)

        # Limit to platform max
        return hashtags[: config["hashtags_max"]]

    def _prepare_description(self, platform: str, metadata: dict, config: dict) -> str:
        """Prepare platform-specific description/caption."""
        base_desc = metadata.get("description", "")
        cta = metadata.get("cta", "¿Qué pasa después? Sígueme para el desenlace 👆")

        # Platform-specific CTA templates
        cta_templates = {
            "tiktok": [
                "¿Qué pasa después? Parte 2 en mi perfil 👆",
                "Sígueme para el desenlace 🔥",
                "Comenta tu teoría 👇",
            ],
            "youtube_shorts": [
                "Suscríbete para ver el próximo episodio",
                "Comenta tu predicción abajo 👇",
            ],
            "instagram_reels": [
                "Sígueme para más microdramas 👆",
                "Tu teoría en los comentarios 👇",
            ],
        }

        platform_cta = metadata.get("platform_cta", {}).get(
            platform, cta_templates.get(platform, [cta])[0]
        )

        full_description = f"{base_desc}\n\n{platform_cta}"

        # Truncate to platform limit if needed
        max_chars = 2200 if platform in ["tiktok", "instagram_reels"] else 5000
        if len(full_description) > max_chars:
            full_description = full_description[: max_chars - 3] + "..."

        return full_description

    def _simulate_publish(
        self,
        platform: str,
        episode_id: str,
        video_path: str,
        metadata: dict,
        hashtags: list[str],
        description: str,
        schedule: str,
    ) -> dict[str, Any]:
        """Simulate platform publishing (replace with actual API calls in production)."""
        import uuid

        publish_id = str(uuid.uuid4())[:8]

        # Determine scheduled time
        if schedule == "immediate":
            scheduled_time = datetime.now().isoformat()
            status = "published"
        else:
            scheduled_time = schedule
            status = "scheduled"

        return {
            "status": status,
            "publish_id": publish_id,
            "platform": platform,
            "episode_id": episode_id,
            "video_path": video_path,
            "metadata": metadata,
            "hashtags": hashtags,
            "description": description,
            "scheduled_time": scheduled_time,
            "published_time": (
                datetime.now().isoformat() if schedule == "immediate" else None
            ),
            "url": f"https://{platform}.com/@doramastudio/{publish_id}",
            "timestamp": datetime.now().isoformat(),
        }

    def _cleanup_cache(self):
        """Remove expired cache entries."""
        now = time.time()
        while (
            self._platform_cache
            and (now - self._platform_cache[0][1]) > self._cache_ttl
        ):
            self._platform_cache.popleft()

    def get_platform_specs(self, platform: str) -> dict[str, Any]:
        """Get platform specifications for video rendering."""
        return self.platform_configs.get(platform, {})

    def validate_cross_post_schedule(self, cross_post_config: dict) -> bool:
        """Validate cross-posting schedule configuration."""
        strategy = cross_post_config.get("strategy", "staggered")
        stagger_minutes = cross_post_config.get("stagger_minutes", 30)
        platform_order = cross_post_config.get(
            "platform_order", ["tiktok", "youtube_shorts", "instagram_reels"]
        )

        return all(p in self.platform_configs for p in platform_order)
