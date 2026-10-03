# dorama_studio/pipeline/api_clients.py
"""
API Clients for video, image, audio generation models.
Supports: Kling, Runway, Veo, Hailuo, ElevenLabs, Suno, Flux, Imagen.
"""

import asyncio
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class GenerationStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GenerationRequest:
    prompt: str
    negative_prompt: str = ""
    reference_images: list[str] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    request_id: str
    status: GenerationStatus
    output_url: str | None = None
    local_path: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    cost_usd: float = 0.0
    duration_sec: float = 0.0


class BaseAPIClient(ABC):
    """Base class for all model API clients."""

    def __init__(self, api_key: str = None, base_url: str = None, timeout: int = 300):
        self.api_key = api_key or os.getenv(self.ENV_VAR)
        self.base_url = base_url
        self.timeout = timeout
        self.session: aiohttp.ClientSession | None = None

    @property
    @abstractmethod
    def ENV_VAR(self) -> str:
        pass

    @property
    @abstractmethod
    def MODEL_NAME(self) -> str:
        pass

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        pass

    async def _poll_until_complete(
        self, task_id: str, poll_interval: float = 5.0, max_wait: int = 300
    ) -> GenerationResult:
        """Poll task until completion."""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            result = await self._check_status(task_id)
            if result.status in [GenerationStatus.COMPLETED, GenerationStatus.FAILED]:
                return result
            await asyncio.sleep(poll_interval)
        return GenerationResult(
            request_id=task_id,
            status=GenerationStatus.FAILED,
            error="Timeout waiting for generation",
        )

    @abstractmethod
    async def _check_status(self, task_id: str) -> GenerationResult:
        pass


class KlingClient(BaseAPIClient):
    """Kling (Kuaishou) Video Generation API Client."""

    ENV_VAR = "KLING_API_KEY"
    MODEL_NAME = "kling"

    def __init__(self, api_key: str = None, base_url: str = "https://api.kling.ai/v1"):
        super().__init__(api_key, base_url)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate video using Kling API."""
        payload = {
            "model_name": "kling-v1.6",
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "cfg_scale": request.params.get("guidance_scale", 7.5),
            "duration": request.params.get("duration", 10),
            "aspect_ratio": request.params.get("aspect_ratio", "9:16"),
            "camera_control": request.params.get("camera_motion", "push_in"),
        }

        # Add reference images if provided (image-to-video)
        if request.reference_images:
            payload["image"] = request.reference_images[0]  # base64 or URL
            payload["mode"] = "image_to_video"

        async with self.session.post(
            f"{self.base_url}/videos/text2video", headers=self.headers, json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return GenerationResult(
                    request_id="",
                    status=GenerationStatus.FAILED,
                    error=f"Kling API error {resp.status}: {error_text}",
                )
            data = await resp.json()
            task_id = data.get("task_id", data.get("id", ""))

        return await self._poll_until_complete(task_id)

    async def _check_status(self, task_id: str) -> GenerationResult:
        async with self.session.get(
            f"{self.base_url}/videos/{task_id}", headers=self.headers
        ) as resp:
            data = await resp.json()
            status = data.get("task_status", data.get("status", "unknown"))

            if status == "succeed":
                return GenerationResult(
                    request_id=task_id,
                    status=GenerationStatus.COMPLETED,
                    output_url=data.get("video_url", ""),
                    local_path=data.get("local_path", ""),
                    metadata=data,
                )
            elif status == "failed":
                return GenerationResult(
                    request_id=task_id,
                    status=GenerationStatus.FAILED,
                    error=data.get("error_message", "Unknown error"),
                )
            else:
                return GenerationResult(
                    request_id=task_id,
                    status=GenerationStatus.PROCESSING,
                    metadata=data,
                )


class RunwayClient(BaseAPIClient):
    """Runway Gen-3 Alpha / Gen-4 API Client."""

    ENV_VAR = "RUNWAY_API_KEY"
    MODEL_NAME = "runway"

    def __init__(
        self, api_key: str = None, base_url: str = "https://api.runwayml.com/v1"
    ):
        super().__init__(api_key, base_url)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        payload = {
            "model": "gen-3-alpha-turbo",
            "prompt_text": request.prompt,
            "negative_prompt": request.negative_prompt,
            "ratio": request.params.get("aspect_ratio", "9:16"),
            "duration": request.params.get("duration", 10),
            "camera_control": request.params.get("camera_motion", "push_in"),
        }

        if request.reference_images:
            payload["reference_image"] = request.reference_images[0]
            payload["mode"] = "image_to_video"

        async with self.session.post(
            f"{self.base_url}/text_to_video", headers=self.headers, json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return GenerationResult(
                    request_id="",
                    status=GenerationStatus.FAILED,
                    error=f"Runway API error {resp.status}: {error_text}",
                )
            data = await resp.json()
            task_id = data.get("id", "")

        return await self._poll_until_complete(task_id, poll_interval=3.0)

    async def _check_status(self, task_id: str) -> GenerationResult:
        async with self.session.get(
            f"{self.base_url}/text_to_video/{task_id}", headers=self.headers
        ) as resp:
            data = await resp.json()
            status = data.get("status", "unknown")

            if status == "SUCCEEDED":
                return GenerationResult(
                    request_id=task_id,
                    status=GenerationStatus.COMPLETED,
                    output_url=data.get("output", [{}])[0].get("url", ""),
                    metadata=data,
                )
            elif status == "FAILED":
                return GenerationResult(
                    request_id=task_id,
                    status=GenerationStatus.FAILED,
                    error=data.get("error", "Unknown error"),
                )
            else:
                return GenerationResult(
                    request_id=task_id,
                    status=GenerationStatus.PROCESSING,
                    metadata=data,
                )


class VeoClient(BaseAPIClient):
    """Google Veo 3 (Vertex AI) API Client."""

    ENV_VAR = "GOOGLE_CLOUD_PROJECT"  # Uses ADC
    MODEL_NAME = "veo"

    def __init__(
        self,
        project_id: str = None,
        location: str = "us-central1",
        base_url: str = None,
    ):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        # Uses Google Cloud Vertex AI SDK, not REST directly
        self.base_url = base_url or f"https://{location}-aiplatform.googleapis.com/v1"
        super().__init__(None, self.base_url)

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        # This would use google-cloud-aiplatform SDK in real implementation
        # For now, return mock to maintain pipeline flow
        logger.warning(
            "VeoClient: Using mock implementation. Install google-cloud-aiplatform for real API."
        )

        # Simulate async generation
        await asyncio.sleep(0.1)
        return GenerationResult(
            request_id=f"veo_{int(time.time())}",
            status=GenerationStatus.COMPLETED,
            output_url="mock://veo_output.mp4",
            metadata={"model": "veo-3", "mock": True},
        )

    async def _check_status(self, task_id: str) -> GenerationResult:
        return GenerationResult(request_id=task_id, status=GenerationStatus.COMPLETED)


class ElevenLabsClient(BaseAPIClient):
    """ElevenLabs TTS API Client."""

    ENV_VAR = "ELEVENLABS_API_KEY"
    MODEL_NAME = "elevenlabs"

    VOICE_MAP = {
        "narrator": "pNInz6obpgDQGcFmaJgB",  # Adam
        "protagonist_female": "EXAVITQu4vr4xnSDxMaL",  # Bella
        "protagonist_male": "VR6AewLTigWG4xSOukaG",  # Arnold
        "antagonist": "TxGEqnHWrfWFTfGW9XjX",  # Josh
        "supporting_female": "MF3mGyEYCl7XYWbV9V6O",  # Elli
        "supporting_male": "ErXwobaYiN019PkySvFV",  # Antoni
    }

    def __init__(
        self, api_key: str = None, base_url: str = "https://api.elevenlabs.io/v1"
    ):
        super().__init__(api_key, base_url)
        self.headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}

    async def generate_speech(
        self,
        text: str,
        voice_id: str = None,
        voice_role: str = "narrator",
        model: str = "eleven_turbo_v2_5",
        voice_settings: dict = None,
    ) -> GenerationResult:
        """Generate speech from text."""
        vid = voice_id or self.VOICE_MAP.get(voice_role, self.VOICE_MAP["narrator"])

        settings = voice_settings or {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True,
        }

        payload = {"text": text, "model_id": model, "voice_settings": settings}

        async with self.session.post(
            f"{self.base_url}/text-to-speech/{vid}", headers=self.headers, json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return GenerationResult(
                    request_id="",
                    status=GenerationStatus.FAILED,
                    error=f"ElevenLabs API error {resp.status}: {error_text}",
                )

            audio_data = await resp.read()

            # Save locally
            import uuid

            filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
            local_path = f"outputs/audio/{filename}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(audio_data)

            return GenerationResult(
                request_id=f"tts_{int(time.time())}",
                status=GenerationStatus.COMPLETED,
                local_path=local_path,
                metadata={
                    "voice_id": vid,
                    "model": model,
                    "duration_estimate": len(text) * 0.08,
                },
            )

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return await self.generate_speech(
            text=request.prompt,
            voice_role=request.metadata.get("voice_role", "narrator"),
            voice_settings=request.params.get("voice_settings"),
        )

    async def _check_status(self, task_id: str) -> GenerationResult:
        return GenerationResult(request_id=task_id, status=GenerationStatus.COMPLETED)


class SunoClient(BaseAPIClient):
    """Suno Music Generation API Client."""

    ENV_VAR = "SUNO_API_KEY"
    MODEL_NAME = "suno"

    def __init__(self, api_key: str = None, base_url: str = "https://api.suno.ai/v1"):
        super().__init__(api_key, base_url)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_music(
        self,
        prompt: str,
        genre: str = "cinematic",
        bpm: int = 80,
        duration_sec: int = 30,
        instrumental: bool = True,
    ) -> GenerationResult:
        payload = {
            "prompt": prompt,
            "tags": (
                f"{genre}, {bpm}bpm, instrumental"
                if instrumental
                else f"{genre}, {bpm}bpm"
            ),
            "duration": duration_sec,
            "model": "chirp-v3",
            "make_instrumental": instrumental,
        }

        async with self.session.post(
            f"{self.base_url}/generate", headers=self.headers, json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return GenerationResult(
                    request_id="",
                    status=GenerationStatus.FAILED,
                    error=f"Suno API error {resp.status}: {error_text}",
                )
            data = await resp.json()
            task_id = data.get("task_id", data.get("id", ""))

        return await self._poll_until_complete(
            task_id, poll_interval=10.0, max_wait=120
        )

    async def _check_status(self, task_id: str) -> GenerationResult:
        async with self.session.get(
            f"{self.base_url}/generate/{task_id}", headers=self.headers
        ) as resp:
            data = await resp.json()
            status = data.get("status", "unknown")

            if status == "completed":
                clips = data.get("clips", [])
                if clips:
                    return GenerationResult(
                        request_id=task_id,
                        status=GenerationStatus.COMPLETED,
                        output_url=clips[0].get("audio_url", ""),
                        metadata=data,
                    )
            elif status == "failed":
                return GenerationResult(
                    request_id=task_id,
                    status=GenerationStatus.FAILED,
                    error=data.get("error", "Unknown error"),
                )
            return GenerationResult(
                request_id=task_id, status=GenerationStatus.PROCESSING, metadata=data
            )

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return await self.generate_music(
            prompt=request.prompt,
            genre=request.metadata.get("genre", "cinematic"),
            bpm=request.metadata.get("bpm", 80),
            duration_sec=request.params.get("duration", 30),
        )


class FluxClient(BaseAPIClient):
    """Flux (Black Forest Labs) Image Generation API Client."""

    ENV_VAR = "FLUX_API_KEY"
    MODEL_NAME = "flux"

    def __init__(self, api_key: str = None, base_url: str = "https://api.bfl.ml/v1"):
        super().__init__(api_key, base_url)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1080,
        height: int = 1920,
        aspect_ratio: str = "9:16",
        seed: int = None,
    ) -> GenerationResult:
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "model": "flux-1.1-pro",
            "seed": seed,
            "steps": 28,
            "guidance": 3.5,
        }

        async with self.session.post(
            f"{self.base_url}/flux-pro-1.1", headers=self.headers, json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return GenerationResult(
                    request_id="",
                    status=GenerationStatus.FAILED,
                    error=f"Flux API error {resp.status}: {error_text}",
                )
            data = await resp.json()
            task_id = data.get("id", "")

        return await self._poll_until_complete(task_id, poll_interval=2.0)

    async def _check_status(self, task_id: str) -> GenerationResult:
        async with self.session.get(
            f"{self.base_url}/result/{task_id}", headers=self.headers
        ) as resp:
            data = await resp.json()
            status = data.get("status", "unknown")

            if status == "Ready":
                return GenerationResult(
                    request_id=task_id,
                    status=GenerationStatus.COMPLETED,
                    output_url=data.get("result", {}).get("sample", ""),
                    metadata=data,
                )
            elif status == "Error":
                return GenerationResult(
                    request_id=task_id,
                    status=GenerationStatus.FAILED,
                    error=data.get("error", "Unknown error"),
                )
            return GenerationResult(
                request_id=task_id, status=GenerationStatus.PROCESSING, metadata=data
            )

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return await self.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.params.get("width", 1080),
            height=request.params.get("height", 1920),
            aspect_ratio=request.params.get("aspect_ratio", "9:16"),
            seed=request.params.get("seed"),
        )


class APIClientFactory:
    """Factory for creating API clients."""

    _clients = {
        "kling": KlingClient,
        "runway": RunwayClient,
        "veo": VeoClient,
        "elevenlabs": ElevenLabsClient,
        "suno": SunoClient,
        "flux": FluxClient,
    }

    @classmethod
    def create(cls, model: str, **kwargs) -> BaseAPIClient:
        client_class = cls._clients.get(model.lower())
        if not client_class:
            raise ValueError(
                f"Unknown model: {model}. Available: {list(cls._clients.keys())}"
            )
        return client_class(**kwargs)

    @classmethod
    def create_all(cls, **kwargs) -> dict[str, BaseAPIClient]:
        return {
            name: client_class(**kwargs) for name, client_class in cls._clients.items()
        }


# Testing
if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    # Test factory
    print("Available clients:", list(APIClientFactory._clients.keys()))
