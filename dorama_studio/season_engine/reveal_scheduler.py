"""
Reveal Scheduler - Phase 6
Schedules and tracks reveals across a 40-episode season.
Manages open loops, foreshadowing, and reveal density.
"""

from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class RevealStatus(str, Enum):
    """Status of a reveal in the schedule."""
    PLANNED = "planned"
    FORESHADOWED = "foreshadowed"
    REVEALED = "revealed"
    PAID_OFF = "paid_off"
    CANCELLED = "cancelled"


class OpenLoop(BaseModel):
    """An open narrative loop that needs to be closed."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    loop_id: str
    description: str
    opened_episode: int
    expected_close_episode: int | None = None
    actual_close_episode: int | None = None
    characters_involved: list[str] = Field(default_factory=list)
    urgency: Literal["low", "medium", "high", "critical"] = "medium"
    status: Literal["open", "closing", "closed", "abandoned"] = "open"
    clues_planted: list[dict[str, Any]] = Field(default_factory=list)  # episode, clue


class Reveal(BaseModel):
    """A scheduled reveal in the season."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    reveal_id: str
    reveal_type: str  # "identity", "betrayal", "power_source", etc.
    description: str
    episode: int = Field(ge=1, le=40)

    # Foreshadowing
    foreshadowing_episodes: list[int] = Field(default_factory=list)
    foreshadowing_strength: float = Field(default=0.5, ge=0.0, le=1.0)

    # Impact
    characters_affected: list[str] = Field(default_factory=list)
    impact_level: Literal["personal", "relational", "global"] = "personal"
    status: RevealStatus = RevealStatus.PLANNED

    # Payoff tracking
    payoff_episodes: list[int] = Field(default_factory=list)
    actual_payoff_episodes: list[int] = Field(default_factory=list)

    # Quality
    surprise_factor: float = Field(default=0.5, ge=0.0, le=1.0)
    emotional_impact: float = Field(default=0.5, ge=0.0, le=1.0)


class RevealScheduler(BaseModel):
    """
    Schedules and manages reveals across a 40-episode season.
    Ensures proper foreshadowing, reveal density, and payoff structure.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", arbitrary_types_allowed=True)

    season_id: str
    total_episodes: int = 40

    # Reveal tracking
    reveals: dict[str, Reveal] = Field(default_factory=dict)
    reveals_by_episode: dict[int, list[str]] = Field(default_factory=lambda: defaultdict(list))

    # Open loops tracking
    open_loops: dict[str, OpenLoop] = Field(default_factory=dict)

    # Density tracking
    reveals_per_episode: dict[int, int] = Field(default_factory=lambda: defaultdict(int))
    target_density: dict[str, float] = Field(default_factory=lambda: {
        "setup": 0.5,           # Acts 1-2: 0.5 reveals/ep
        "confrontation": 1.0,   # Acts 2-3: 1.0 reveals/ep
        "climax": 1.5,          # Act 3: 1.5 reveals/ep
        "resolution": 0.3,      # Act 4: 0.3 reveals/ep
    })

    # Act boundaries
    act_boundaries: dict[int, tuple[int, int]] = Field(default_factory=lambda: {
        1: (1, 10),    # Setup
        2: (11, 25),   # Confrontation
        3: (26, 35),   # Climax
        4: (36, 40),   # Resolution
    })

    def get_act_for_episode(self, episode: int) -> int:
        """Get act number for an episode."""
        for act_num, (start, end) in self.act_boundaries.items():
            if start <= episode <= end:
                return act_num
        return 1

    def get_target_density_for_episode(self, episode: int) -> float:
        """Get target reveal density for an episode."""
        act = self.get_act_for_episode(episode)
        act_names = {1: "setup", 2: "confrontation", 3: "climax", 4: "resolution"}
        return self.target_density.get(act_names.get(act, "setup"), 0.5)

    def schedule_reveal(self, reveal: Reveal) -> bool:
        """
        Schedule a reveal at the specified episode.
        Returns True if successful, False if conflicts.
        """
        # Validate episode
        if not (1 <= reveal.episode <= self.total_episodes):
            return False

        # Check density
        current_density = self.reveals_per_episode[reveal.episode]
        target = self.get_target_density_for_episode(reveal.episode)
        if current_density >= target + 0.5:  # Allow some flexibility
            return False

        # Add reveal
        self.reveals[reveal.reveal_id] = reveal
        self.reveals_by_episode[reveal.episode].append(reveal.reveal_id)
        self.reveals_per_episode[reveal.episode] += 1

        return True

    def add_foreshadowing(self, reveal_id: str, episode: int) -> bool:
        """Add a foreshadowing beat for a reveal."""
        if reveal_id not in self.reveals:
            return False
        if not (1 <= episode < self.reveals[reveal_id].episode):
            return False

        reveal = self.reveals[reveal_id]
        if episode not in reveal.foreshadowing_episodes:
            reveal.foreshadowing_episodes.append(episode)
            reveal.foreshadowing_episodes.sort()
        return True

    def create_open_loop(
        self,
        loop_id: str,
        description: str,
        opened_episode: int,
        expected_close: int | None = None,
        characters: list[str] | None = None,
        urgency: Literal["low", "medium", "high", "critical"] = "medium",
    ) -> OpenLoop:
        """Create a new open narrative loop."""
        loop = OpenLoop(
            loop_id=loop_id,
            description=description,
            opened_episode=opened_episode,
            expected_close_episode=expected_close,
            characters_involved=characters or [],
            urgency=urgency,
        )
        self.open_loops[loop_id] = loop
        return loop

    def close_loop(self, loop_id: str, closed_episode: int) -> bool:
        """Mark an open loop as closed."""
        if loop_id not in self.open_loops:
            return False
        loop = self.open_loops[loop_id]
        loop.actual_close_episode = closed_episode
        loop.status = "closed"
        return True

    def get_reveals_for_episode(self, episode: int) -> list[Reveal]:
        """Get all reveals scheduled for an episode."""
        reveal_ids = self.reveals_by_episode.get(episode, [])
        return [self.reveals[rid] for rid in reveal_ids]

    def get_open_loops_at_episode(self, episode: int) -> list[OpenLoop]:
        """Get all open loops active at a given episode."""
        active = []
        for loop in self.open_loops.values():
            if loop.opened_episode <= episode and loop.status == "open":
                active.append(loop)
        return active

    def get_upcoming_reveals(self, from_episode: int, count: int = 3) -> list[Reveal]:
        """Get next N reveals after an episode."""
        upcoming = [r for r in self.reveals.values() if r.episode > from_episode]
        upcoming.sort(key=lambda r: r.episode)
        return upcoming[:count]

    def get_density_report(self) -> dict[str, Any]:
        """Generate reveal density report."""
        act_densities = {}
        for act_num in range(1, 5):
            start, end = self.act_boundaries[act_num]
            total_reveals = sum(self.reveals_per_episode[ep] for ep in range(start, end + 1))
            ep_count = end - start + 1
            act_densities[f"act_{act_num}"] = {
                "episodes": f"{start}-{end}",
                "total_reveals": total_reveals,
                "avg_per_episode": total_reveals / ep_count if ep_count > 0 else 0,
                "target": self.target_density.get(
                    ["setup", "confrontation", "climax", "resolution"][act_num - 1], 0.5
                ),
            }

        return {
            "total_reveals": len(self.reveals),
            "total_episodes": self.total_episodes,
            "overall_density": len(self.reveals) / self.total_episodes if self.total_episodes > 0 else 0,
            "by_act": act_densities,
            "open_loops": len([l for l in self.open_loops.values() if l.status == "open"]),
            "closed_loops": len([l for l in self.open_loops.values() if l.status == "closed"]),
        }

    def validate_schedule(self) -> list[str]:
        """Validate the reveal schedule."""
        issues = []

        # Check each reveal has proper foreshadowing
        for reveal in self.reveals.values():
            if reveal.foreshadowing_strength > 0.7 and len(reveal.foreshadowing_episodes) < 2:
                issues.append(f"Reveal {reveal.reveal_id}: high foreshadowing strength but < 2 foreshadowing episodes")

            # Check foreshadowing happens before reveal
            for ep in reveal.foreshadowing_episodes:
                if ep >= reveal.episode:
                    issues.append(f"Reveal {reveal.reveal_id}: foreshadowing at ep {ep} not before reveal at ep {reveal.episode}")

        # Check open loops
        for loop in self.open_loops.values():
            if loop.status == "open" and loop.expected_close_episode:
                if loop.expected_close_episode < loop.opened_episode:
                    issues.append(f"Loop {loop.loop_id}: expected close before open")

        # Check density
        for ep in range(1, self.total_episodes + 1):
            current = self.reveals_per_episode[ep]
            target = self.get_target_density_for_episode(ep)
            if current > target + 1:
                issues.append(f"Episode {ep}: reveal density {current} exceeds target {target}")

        return issues

    def auto_schedule_standard_reveals(self) -> None:
        """Auto-schedule standard reveal types across the season."""
        standard_reveals = [
            # Act 1: Setup reveals
            ("identity_1", "identity", "Protagonist's true lineage revealed", 5, 0.6),
            ("betrayal_1", "betrayal", "Trusted ally revealed as antagonist", 8, 0.7),

            # Act 2: Confrontation reveals
            ("power_1", "power_source", "True nature of power source discovered", 15, 0.8),
            ("conspiracy_1", "conspiracy", "Hidden organization controlling events", 18, 0.7),
            ("betrayal_2", "double_agent", "Key ally playing both sides", 22, 0.8),

            # Act 3: Climax reveals
            ("identity_2", "identity", "Protagonist's true identity revealed", 28, 0.9),
            ("power_2", "power_source", "How to control/defeat the power", 30, 0.9),
            ("fake_death", "fake_death", "Presumed dead character returns", 32, 0.85),

            # Act 4: Resolution reveals
            ("conspiracy_2", "conspiracy", "Mastermind's true identity", 37, 0.8),
            ("prophecy", "prophecy_twist", "Prophecy fulfilled in unexpected way", 39, 0.9),
        ]

        for reveal_id, rtype, desc, ep, strength in standard_reveals:
            # Scale the episode number to the total_episodes (assuming base of 40 episodes)
            scaled_ep = int(round(ep * (self.total_episodes / 40.0)))
            # Clamp to valid range
            if scaled_ep < 1:
                scaled_ep = 1
            if scaled_ep > self.total_episodes:
                scaled_ep = self.total_episodes
            reveal = Reveal(
                reveal_id=reveal_id,
                reveal_type=rtype,
                description=desc,
                episode=scaled_ep,
                foreshadowing_strength=strength,
            )
            self.schedule_reveal(reveal)

            # Add foreshadowing (scaled accordingly)
            if scaled_ep > 3:
                self.add_foreshadowing(reveal_id, scaled_ep - 3)
            if scaled_ep > 6:
                self.add_foreshadowing(reveal_id, scaled_ep - 1)


# Default scheduler
default_scheduler = RevealScheduler(season_id="season_1")
