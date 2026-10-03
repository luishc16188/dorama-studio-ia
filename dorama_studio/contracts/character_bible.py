"""
Character Bible contract - for visual consistency validation (GAP 3 fix)
"""

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class CharacterAttribute(str, Enum):
    FACE_CONSISTENCY = "face_consistency"
    HAIR_COLOR = "hair_color"
    HAIR_STYLE = "hair_style"
    EYE_COLOR = "eye_color"
    CLOTHING = "clothing"
    ACCESSORIES = "accessories"
    AGE_APPEARANCE = "age_appearance"
    HEIGHT_PROPORTIONS = "height_proportions"
    PERSONALITY_MANNERISMS = "personality_mannerisms"
    VOICE_CHARACTERISTICS = "voice_characteristics"


class ReferenceImage(BaseModel):
    """Single reference image with metadata"""

    path: str
    clip_embedding: list[float] | None = None
    seed: int | None = None
    quality_score: float = Field(default=1.0, ge=0, le=1)


class CharacterBible(BaseModel):
    """Complete character definition for consistency enforcement"""

    character_id: str = Field(pattern=r"^CH-\d{4}$")
    name: str = Field(min_length=1, max_length=50)

    # Visual attributes (locked at creation)
    face_description: str = Field(min_length=50)
    hair_color: str = Field(min_length=3)
    hair_style: str = Field(min_length=3)
    eye_color: str = Field(min_length=3)
    typical_clothing: list[str] = Field(min_length=1)
    accessories: list[str] = Field(default_factory=list)
    age_appearance: str = Field(min_length=5)
    height_proportions: str = Field(min_length=10)

    # Behavioral attributes
    personality_mannerisms: list[str] = Field(min_length=3)
    voice_characteristics: str = Field(min_length=20)

    # Reference images (for CLIP validation)
    reference_images: list[ReferenceImage] = Field(min_length=3, max_length=10)

    # Deterministic seed (locked on creation)
    locked_seed: int = Field(ge=0, le=2**32 - 1)

    # Validation thresholds (from quality.yaml continuity)
    similarity_threshold: float = Field(default=0.85, ge=0.7, le=0.99)
    max_drift_per_episode: float = Field(default=0.05, ge=0.01, le=0.2)

    @model_validator(mode="after")
    def validate_reference_count(self):
        """Ensure we have at least 3 reference images"""
        if len(self.reference_images) < 3:
            raise ValueError("Need at least 3 reference images")
        return self


class CharacterConsistencyReport(BaseModel):
    """Report from consistency validation"""

    character_id: str
    episode_num: int
    scene_num: int
    passed: bool
    clip_score: float
    threshold: float
    drift_from_previous: float | None = None
    failed_attributes: list[CharacterAttribute] = Field(default_factory=list)
    notes: str = ""
