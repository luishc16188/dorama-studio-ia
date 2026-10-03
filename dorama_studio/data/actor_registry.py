from typing import Any


# Mock Actor Registry
class Actor:
    def __init__(self, id: str, name: str, archetype: str):
        self.id = id
        self.name = name
        self.archetype = archetype


ACTOR_REGISTRY: dict[str, Actor] = {
    "kim_jun_ho": Actor("kim_jun_ho", "Kim Jun-ho", "CEO"),
    "park_so_yoon": Actor("park_so_yoon", "Park So-yoon", "Heiress"),
    "choi_min_seok": Actor("choi_min_seok", "Choi Min-seok", "Rival"),
    "jung_ha_eun": Actor("jung_ha_eun", "Jung Ha-eun", "Friend"),
}


# Mock Casting for Episode 1
class RoleOverlay:
    def __init__(
        self,
        role_name: str,
        archetype: str,
        wardrobe_override: str = None,
        age_apparent: str = None,
    ):
        self.role_name = role_name
        self.archetype = archetype
        self.wardrobe_override = wardrobe_override
        self.age_apparent = age_apparent


class Casting:
    def __init__(self, assignments: dict[str, tuple[str, RoleOverlay]]):
        self.assignments = assignments

    def get_character_id(self, role_name: str) -> str:
        # Return the actor id (with @ prefix as used in the code)
        actor_id, _ = self.assignments[role_name]
        return f"@{actor_id}"


CASTING_LA_SECRETARIA_HEREDERA_EP1 = Casting(
    {
        "protagonist": (
            "kim_jun_ho",
            RoleOverlay("CEO", "ruler", "from_lock", "early_30s"),
        ),
        "antagonist": (
            "park_so_yoon",
            RoleOverlay("Heiress", "rebel_in_disguise", "from_lock", "late_20s"),
        ),
        # Add more if needed, but the script only uses these two in the bible creation
    }
)


def resolve_packages_from_casting(casting: Casting) -> dict[str, dict[str, Any]]:
    """Resolve packages from casting (mock)."""
    packages = {}
    for role_name, (actor_id, overlay) in casting.assignments.items():
        char_id = casting.get_character_id(role_name)
        packages[char_id] = {
            "name_es": overlay.role_name,
            "character_id": char_id,
            # Add other fields as needed by the code
        }
    return packages


def resolve_overlays_from_casting(casting: Casting) -> dict[str, RoleOverlay]:
    """Resolve overlays from casting (mock)."""
    overlays = {}
    for role_name, (_, overlay) in casting.assignments.items():
        overlays[role_name] = overlay
    return overlays
