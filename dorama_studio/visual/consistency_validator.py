"""
Visual Consistency Validator - Pre-render validation (GAP 3 fix)
Moves validation to Phase 0 (Character Bible) before spending render credits
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Import from contracts
from ..contracts.character_bible import CharacterBible


class ValidationStage(str, Enum):
    PHASE_0_REFERENCE = "phase_0_reference"  # Character Bible validation
    PHASE_1_KEYFRAME = "phase_1_keyframe"  # Keyframe test validation
    PHASE_2_FULL_RENDER = "phase_2_full_render"  # Full render validation


@dataclass
class ValidationResult:
    passed: bool
    stage: ValidationStage
    clip_score: float
    threshold: float
    details: str
    seed_used: int


class CharacterConsistencyValidator:
    """
    Validates character consistency BEFORE expensive render operations.

    Pipeline:
    1. Phase 0: Validate Character Bible reference images meet threshold
    2. Phase 1: Generate test keyframe at low res, validate
    3. Phase 2: Full render with deterministic seed

    Only proceeds to next phase if previous passes.
    """

    def __init__(self, clip_model_path: str | None = None, device: str = "cpu"):
        self.clip_model_path = clip_model_path
        self.device = device
        self._clip_model = None
        self._clip_processor = None

    def _get_clip(self):
        """Lazy load CLIP model"""
        if self._clip_model is None:
            try:
                import torch
                from transformers import CLIPModel, CLIPProcessor

                model_name = self.clip_model_path or "openai/clip-vit-base-patch32"
                self._clip_model = CLIPModel.from_pretrained(model_name).to(self.device)
                self._clip_processor = CLIPProcessor.from_pretrained(model_name)
            except ImportError:
                raise RuntimeError(
                    "CLIP validation requires transformers and torch. "
                    "Install: pip install transformers torch"
                )
        return self._clip_model, self._clip_processor

    def compute_embedding(self, image_path: Path) -> list[float]:
        """Compute CLIP embedding for image"""
        import torch
        from PIL import Image

        model, processor = self._get_clip()
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            embedding = model.get_image_features(**inputs)

        # Normalize
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        return embedding.cpu().numpy().flatten().tolist()

    def validate_character_bible(
        self, character_bible: CharacterBible, reference_dir: Path
    ) -> ValidationResult:
        """
        Phase 0: Validate all reference images in Character Bible
        meet minimum similarity threshold.
        """
        # Ensure all references have embeddings
        for i, ref in enumerate(character_bible.reference_images):
            if ref.clip_embedding is None:
                img_path = reference_dir / ref.path
                if not img_path.exists():
                    return ValidationResult(
                        passed=False,
                        stage=ValidationStage.PHASE_0_REFERENCE,
                        clip_score=0.0,
                        threshold=character_bible.similarity_threshold,
                        details=f"Reference image not found: {ref.path}",
                        seed_used=character_bible.locked_seed,
                    )

                # Compute embedding
                embedding = self.compute_embedding(img_path)
                character_bible.reference_images[i].clip_embedding = embedding

        # Compute pairwise similarities
        import numpy as np

        embeddings = [
            np.array(r.clip_embedding) for r in character_bible.reference_images
        ]
        min_sim = 1.0

        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = float(
                    np.dot(embeddings[i], embeddings[j])
                    / (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]))
                )
                min_sim = min(min_sim, sim)

        passed = min_sim >= character_bible.similarity_threshold

        return ValidationResult(
            passed=passed,
            stage=ValidationStage.PHASE_0_REFERENCE,
            clip_score=min_sim,
            threshold=character_bible.similarity_threshold,
            details=(
                f"Min pairwise CLIP similarity: {min_sim:.4f} "
                f"(threshold: {character_bible.similarity_threshold:.2f})"
            ),
            seed_used=character_bible.locked_seed,
        )

    def validate_keyframe(
        self,
        character_bible: CharacterBible,
        keyframe_path: Path,
        episode_num: int,
        scene_num: int,
    ) -> ValidationResult:
        """
        Phase 1: Validate a single test keyframe against Character Bible.
        """
        # Compute keyframe embedding
        keyframe_emb = self.compute_embedding(keyframe_path)

        # Compare against all references
        import numpy as np

        ref_embeddings = [
            np.array(r.clip_embedding) for r in character_bible.reference_images
        ]
        keyframe_vec = np.array(keyframe_emb)

        similarities = []
        for ref_vec in ref_embeddings:
            sim = float(
                np.dot(keyframe_vec, ref_vec)
                / (np.linalg.norm(keyframe_vec) * np.linalg.norm(ref_vec))
            )
            similarities.append(sim)

        avg_sim = sum(similarities) / len(similarities)
        seed_used = character_bible.get_deterministic_seed(episode_num, scene_num)

        passed = avg_sim >= character_bible.similarity_threshold

        return ValidationResult(
            passed=passed,
            stage=ValidationStage.PHASE_1_KEYFRAME,
            clip_score=avg_sim,
            threshold=character_bible.similarity_threshold,
            details=(
                f"Keyframe CLIP avg: {avg_sim:.4f} "
                f"(range: {min(similarities):.4f}-{max(similarities):.4f})"
            ),
            seed_used=seed_used,
        )

    def validate_full_render(
        self,
        character_bible: CharacterBible,
        video_path: Path,
        episode_num: int,
        scene_num: int,
        sample_frames: int = 5,
    ) -> list[ValidationResult]:
        """
        Phase 2: Validate rendered video by sampling frames.
        Returns list of results per sampled frame.
        """
        import cv2

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return [
                ValidationResult(
                    passed=False,
                    stage=ValidationStage.PHASE_2_FULL_RENDER,
                    clip_score=0.0,
                    threshold=character_bible.similarity_threshold,
                    details="Could not open video file",
                    seed_used=0,
                )
            ]

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_indices = [
            int(total_frames * i / (sample_frames + 1))
            for i in range(1, sample_frames + 1)
        ]

        results = []
        for idx, frame_idx in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                continue

            # Save frame temporarily
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                cv2.imwrite(tmp.name, frame)
                frame_path = Path(tmp.name)

            result = self.validate_keyframe(
                character_bible, frame_path, episode_num, scene_num
            )
            result.details = f"Frame {frame_idx}/{total_frames}: {result.details}"
            results.append(result)

            # Cleanup
            frame_path.unlink(missing_ok=True)

        cap.release()
        return results

    def full_validation_pipeline(
        self,
        character_bible: CharacterBible,
        reference_dir: Path,
        test_keyframe: Path | None = None,
        episode_num: int = 1,
        scene_num: int = 1,
    ) -> tuple[bool, list[ValidationResult]]:
        """
        Run complete validation pipeline.
        Returns (all_passed, list_of_results)
        """
        results = []

        # Phase 0: Reference validation
        phase0 = self.validate_character_bible(character_bible, reference_dir)
        results.append(phase0)
        if not phase0.passed:
            return False, results

        # Phase 1: Keyframe test (if provided)
        if test_keyframe and test_keyframe.exists():
            phase1 = self.validate_keyframe(
                character_bible, test_keyframe, episode_num, scene_num
            )
            results.append(phase1)
            if not phase1.passed:
                return False, results

        return True, results
