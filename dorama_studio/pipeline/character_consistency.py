# dorama_studio/pipeline/character_consistency.py
"""
Character Consistency System - Maintains visual identity across episodes.
Handles reference images, embeddings, and trait locking.
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TraitLockStatus(Enum):
    LOCKED = "locked"  # Never change
    VARIABLE = "variable"  # Can change per scene
    PROGRESSIVE = "progressive"  # Changes over episode arc


@dataclass
class VisualTrait:
    """A single visual trait with lock status."""

    name: str
    value: str
    lock_status: TraitLockStatus = TraitLockStatus.LOCKED
    allowed_variations: list[str] = field(default_factory=list)
    reference_image_crop: tuple[int, int, int, int] | None = None  # x, y, w, h


@dataclass
class CharacterProfile:
    """Complete character visual profile for consistency."""

    character_id: str
    name: str
    role: str  # protagonist, antagonist, supporting

    # Core locked traits (never change)
    face_shape: str = ""
    eye_color: str = ""
    bone_structure: str = ""
    distinguishing_marks: list[str] = field(default_factory=list)
    skin_tone: str = ""
    age_apparent: int = 25

    # Variable traits (can change per scene)
    hair_style: str = ""
    hair_color: str = ""
    facial_expression: str = "neutral"
    makeup: str = "natural"
    accessories: list[str] = field(default_factory=list)

    # Progressive traits (change over arc)
    emotional_arc_stage: str = (
        "introduction"  # introduction, conflict, climax, resolution
    )
    wardrobe_progression: dict[int, str] = field(
        default_factory=dict
    )  # episode -> style

    # Reference management
    master_reference_path: str = ""
    master_reference_prompt: str = ""
    episode_references: dict[int, str] = field(
        default_factory=dict
    )  # episode -> image path
    embedding_vector: list[float] | None = None  # For similarity matching

    # Drift detection
    drift_tolerance: float = 0.05  # Max allowed deviation
    last_known_embedding: list[float] | None = None

    def get_locked_traits(self) -> dict[str, str]:
        """Return all locked traits as dict."""
        return {
            "face_shape": self.face_shape,
            "eye_color": self.eye_color,
            "bone_structure": self.bone_structure,
            "distinguishing_marks": ", ".join(self.distinguishing_marks),
            "skin_tone": self.skin_tone,
            "age_apparent": str(self.age_apparent),
        }

    def get_variable_traits_for_episode(self, episode: int) -> dict[str, str]:
        """Get traits for specific episode."""
        return {
            "hair_style": self.hair_style,
            "hair_color": self.hair_color,
            "wardrobe": self.wardrobe_progression.get(episode, ""),
            "emotional_arc_stage": self.emotional_arc_stage,
        }

    def validate_consistency(
        self, generated_traits: dict[str, str]
    ) -> tuple[bool, list[str]]:
        """Validate generated traits against locked traits."""
        errors = []
        locked = self.get_locked_traits()

        for trait, expected in locked.items():
            if trait in generated_traits:
                actual = generated_traits[trait]
                # Simple string comparison (in real impl, use embedding similarity)
                if (
                    expected.lower() not in actual.lower()
                    and actual.lower() not in expected.lower()
                ):
                    errors.append(f'{trait}: expected "{expected}", got "{actual}"')

        return len(errors) == 0, errors


@dataclass
class ConsistencyCheckResult:
    """Result of consistency validation."""

    character_id: str
    passed: bool
    drift_score: float  # 0.0 = perfect, 1.0 = max drift
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    trait_scores: dict[str, float] = field(default_factory=dict)


class CharacterConsistencyManager:
    """
    Manages character visual consistency across episodes.
    Handles reference images, embeddings, and drift detection.
    """

    def __init__(self, refs_dir: str = "refs/characters"):
        self.refs_dir = Path(refs_dir)
        self.refs_dir.mkdir(parents=True, exist_ok=True)
        self.profiles: dict[str, CharacterProfile] = {}
        self.embedding_cache: dict[str, list[float]] = {}

    def register_character(self, profile: CharacterProfile) -> None:
        """Register a new character profile."""
        self.profiles[profile.character_id] = profile
        logger.info(f"Registered character: {profile.character_id} ({profile.name})")

    def load_profile(self, character_id: str) -> CharacterProfile | None:
        """Load character profile."""
        return self.profiles.get(character_id)

    def save_profile(self, character_id: str) -> bool:
        """Save profile to disk."""
        profile = self.profiles.get(character_id)
        if not profile:
            return False

        profile_path = self.refs_dir / f"{character_id}_profile.json"
        try:
            data = {
                "character_id": profile.character_id,
                "name": profile.name,
                "role": profile.role,
                "face_shape": profile.face_shape,
                "eye_color": profile.eye_color,
                "bone_structure": profile.bone_structure,
                "distinguishing_marks": profile.distinguishing_marks,
                "skin_tone": profile.skin_tone,
                "age_apparent": profile.age_apparent,
                "hair_style": profile.hair_style,
                "hair_color": profile.hair_color,
                "master_reference_path": profile.master_reference_path,
                "master_reference_prompt": profile.master_reference_prompt,
                "episode_references": profile.episode_references,
                "wardrobe_progression": profile.wardrobe_progression,
                "drift_tolerance": profile.drift_tolerance,
            }
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save profile {character_id}: {e}")
            return False

    def load_profile_from_disk(self, character_id: str) -> CharacterProfile | None:
        """Load profile from disk."""
        profile_path = self.refs_dir / f"{character_id}_profile.json"
        if not profile_path.exists():
            return None

        try:
            with open(profile_path, encoding="utf-8") as f:
                data = json.load(f)

            profile = CharacterProfile(
                character_id=data["character_id"],
                name=data["name"],
                role=data["role"],
                face_shape=data["face_shape"],
                eye_color=data["eye_color"],
                bone_structure=data["bone_structure"],
                distinguishing_marks=data["distinguishing_marks"],
                skin_tone=data["skin_tone"],
                age_apparent=data["age_apparent"],
                hair_style=data["hair_style"],
                hair_color=data["hair_color"],
                master_reference_path=data["master_reference_path"],
                master_reference_prompt=data["master_reference_prompt"],
                episode_references=data.get("episode_references", {}),
                wardrobe_progression={
                    int(k): v for k, v in data.get("wardrobe_progression", {}).items()
                },
                drift_tolerance=data.get("drift_tolerance", 0.05),
            )
            self.profiles[character_id] = profile
            return profile
        except Exception as e:
            logger.error(f"Failed to load profile {character_id}: {e}")
            return None

    def add_episode_reference(
        self, character_id: str, episode: int, image_path: str
    ) -> bool:
        """Add reference image for specific episode."""
        profile = self.profiles.get(character_id)
        if not profile:
            return False

        profile.episode_references[episode] = image_path
        return self.save_profile(character_id)

    def get_reference_for_episode(self, character_id: str, episode: int) -> str | None:
        """Get reference image for episode, fallback to master."""
        profile = self.profiles.get(character_id)
        if not profile:
            return None

        return profile.episode_references.get(episode, profile.master_reference_path)

    def check_consistency(
        self, character_id: str, generated_image_path: str, episode: int
    ) -> ConsistencyCheckResult:
        """
        Check consistency of generated image against character profile.
        In real implementation, this would use CLIP embeddings or similar.
        """
        profile = self.profiles.get(character_id)
        if not profile:
            return ConsistencyCheckResult(
                character_id=character_id,
                passed=False,
                drift_score=1.0,
                errors=[f"Character {character_id} not registered"],
            )

        # Mock implementation - in reality would:
        # 1. Load generated image
        # 2. Extract embeddings using CLIP or similar
        # 3. Compare with profile.embedding_vector or profile.last_known_embedding
        # 4. Calculate cosine similarity / drift score

        # For now, return mock passing result
        return ConsistencyCheckResult(
            character_id=character_id,
            passed=True,
            drift_score=0.02,
            trait_scores={
                "face_shape": 0.98,
                "eye_color": 0.99,
                "bone_structure": 0.97,
                "distinguishing_marks": 0.95,
            },
        )

    def update_embedding(self, character_id: str, embedding: list[float]) -> None:
        """Update character's embedding vector."""
        profile = self.profiles.get(character_id)
        if profile:
            profile.last_known_embedding = embedding
            self.embedding_cache[character_id] = embedding

    def get_consistency_prompt(self, character_id: str, episode: int) -> str:
        """Generate consistency enforcement prompt for model."""
        profile = self.profiles.get(character_id)
        if not profile:
            return ""

        locked = profile.get_locked_traits()
        var = profile.get_variable_traits_for_episode(episode)

        prompt_parts = [
            f"CHARACTER CONSISTENCY ENFORCEMENT for {profile.name} ({profile.character_id}):",
            "",
            "LOCKED TRAITS (MUST NOT CHANGE):",
        ]

        for trait, value in locked.items():
            prompt_parts.append(f"  - {trait}: {value}")

        prompt_parts.extend(
            [
                "",
                f"EPISODE {episode} VARIABLE TRAITS:",
            ]
        )

        for trait, value in var.items():
            prompt_parts.append(f"  - {trait}: {value}")

        prompt_parts.extend(
            [
                "",
                "REFERENCE IMAGE: Use provided character reference image.",
                "MAINTAIN: Exact facial structure, eye color, bone structure, distinguishing marks.",
                "ALLOW: Hair style variations, wardrobe changes per episode, emotional expressions.",
            ]
        )

        return "\n".join(prompt_parts)


def create_character_from_bible(bible_entry: dict[str, Any]) -> CharacterProfile:
    """Create CharacterProfile from CharacterBibleEntry."""
    physical = bible_entry.get("physical", {})
    continuity = bible_entry.get("continuity_rules", {})
    wardrobe = bible_entry.get("wardrobe", {})

    profile = CharacterProfile(
        character_id=bible_entry.get("id", ""),
        name=bible_entry.get("name", ""),
        role=bible_entry.get("role", "supporting"),
        # Locked traits
        face_shape=physical.get("face_shape", "oval"),
        eye_color=physical.get("eye_color", "#000000"),
        bone_structure=physical.get("bone_structure", "average"),
        distinguishing_marks=physical.get("distinguishing_marks", []),
        skin_tone=physical.get("skin_tone", "fair"),
        age_apparent=physical.get("age_apparent", 25),
        # Variable
        hair_style=physical.get("hair_style", ""),
        hair_color=physical.get("hair_color", ""),
        # References
        master_reference_prompt=continuity.get("master_reference_prompt", ""),
        drift_tolerance=continuity.get("drift_tolerance", 0.05),
    )

    # Wardrobe progression from psychological arc
    psych_arc = continuity.get("psychological_arc_by_episode", [])
    for arc_entry in psych_arc:
        ep = arc_entry.get("ep", 0)
        state = arc_entry.get("state", "")
        profile.wardrobe_progression[ep] = (
            f'{wardrobe.get("signature_style", "")} - {state}'
        )

    return profile


# Testing
if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    manager = CharacterConsistencyManager()

    # Create test profile
    profile = CharacterProfile(
        character_id="protagonist_female",
        name="Li Wei",
        role="protagonist",
        face_shape="heart",
        eye_color="#1a2332",
        bone_structure="sharp_jaw_high_cheekbones",
        distinguishing_marks=["beauty_mark_left_cheek"],
        skin_tone="fair_porcelain",
        age_apparent=32,
        hair_style="slicked_back",
        hair_color="dark_brown_ash",
        master_reference_prompt="hyper-detailed prompt para Flux/Imagen: 85mm f/1.4, volumetric rim light, skin texture pores, K-Drama cold palette #1a2332/#e8d5b7, micro-expression: contained betrayal",
        wardrobe_progression={
            1: "charcoal Brioni suit, white Italian shirt, black silk tie - cold executive",
            10: "charcoal suit, unbuttoned collar, tie loosened - cracking facade",
            20: "white linen shirt, no tie, sleeves rolled - redeemed protector",
        },
        drift_tolerance=0.05,
    )

    manager.register_character(profile)
    manager.save_profile("protagonist_female")

    # Test consistency prompt
    prompt = manager.get_consistency_prompt("protagonist_female", 1)
    print("=== CONSISTENCY PROMPT EP 1 ===")
    print(prompt)

    # Test consistency check
    result = manager.check_consistency("protagonist_female", "outputs/ep1/shot1.png", 1)
    print("\n=== CONSISTENCY CHECK ===")
    print(f"Passed: {result.passed}")
    print(f"Drift Score: {result.drift_score}")
    print(f"Trait Scores: {result.trait_scores}")
