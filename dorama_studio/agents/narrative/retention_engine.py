"""
Retention Engine Agent - Attention Risk Model for 0.5-1s windows.
Implements the Attention Risk Model to generate retention actions (KEEP, SHORTEN, etc.)
based on novelty, information delta, emotion delta, motion delta, social tension,
question pressure, visual change, sound change, reward signal, and fatigue risk.
"""
from __future__ import annotations

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)


class RetentionEngineAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Retention Engine Agent that evaluates episode microbeats for attention risk
    and recommends retention actions.
    """

    def __init__(self):
        super().__init__("RetentionEngineAgent")
        # Thresholds for risk factors (0-1 scale)
        self.risk_thresholds = {
            "novelty_low": 0.3,
            "information_delta_low": 0.2,
            "emotion_delta_low": 0.2,
            "motion_delta_low": 0.2,
            "social_tension_low": 0.3,
            "question_pressure_low": 0.3,
            "visual_change_low": 0.3,
            "sound_change_low": 0.3,
            "reward_signal_low": 0.2,
            "fatigue_risk_high": 0.7,
        }
        # Maximum allowed duration without change (seconds)
        self.max_narrative_stasis = 3.0

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)
        self.max_dialogue_without_change = 2.5  # for high rhythm segments

    def _process(self, ctx: dict[str, Any]) -> dict[str, Any]:
        """
        Process the context to evaluate retention risks and generate actions.

        Expects ctx to contain:
        - microbeats: list of microbeat dicts from MicroBeatEngineAgent
        - episode_num: current episode number
        - season_memory: optional, for continuity checks

        Returns:
        - retention_actions: list of actions per microbeat or per window
        - risk_scores: detailed risk scores per microbeat
        - recommendations: human-readable recommendations
        """
        microbeats = ctx.get("microbeats", [])
        episode_num = ctx.get("episode_num", 1)
        season_memory = ctx.get("season_memory", {})

        if not microbeats:
            logger.warning("No microbeats provided for retention analysis")
            return self._empty_result()

        # Evaluate each microbeat (or split into 0.5s windows)
        retention_actions = []
        risk_scores = []

        cumulative_time = 0.0
        for i, beat in enumerate(microbeats):
            beat_start = cumulative_time
            beat_end = cumulative_time + beat.get("duration", 0)
            cumulative_time = beat_end

            # Evaluate risk factors for this beat
            risks = self._evaluate_beat_risks(beat, i, microbeats, season_memory)
            risk_scores.append(risks)

            # Determine retention action based on risks
            action = self._determine_retention_action(risks, beat)
            retention_actions.append(
                {
                    "microbeat_index": i,
                    "time_range": [beat_start, beat_end],
                    "action": action,
                    "risks": risks,
                    "reason": self._explain_action(risks, action),
                }
            )

        # Generate overall recommendations
        recommendations = self._generate_recommendations(retention_actions, risk_scores)

        return {
            "retention_actions": retention_actions,
            "risk_scores": risk_scores,
            "recommendations": recommendations,
            "episode_num": episode_num,
            "total_microbeats_analyzed": len(microbeats),
        }

    def _evaluate_beat_risks(
        self, beat: dict[str, Any], index: int, all_beats: list[dict], season_memory: dict
    ) -> dict[str, float]:
        """
        Evaluate the 10 risk factors for a single microbeat.
        Returns a dict of risk scores (0-1, where higher = higher risk).
        """
        risks = {}

        # 1. Novelty - based on Creative Genome or mechanism rarity
        risks["novelty"] = 1.0 - self._calculate_novelty(beat, index, all_beats)

        # 2. Information delta - new information revealed vs withheld
        risks["information_delta"] = 1.0 - self._calculate_information_delta(beat)

        # 3. Emotion delta - change in emotion intensity
        risks["emotion_delta"] = 1.0 - self._calculate_emotion_delta(beat, index, all_beats)

        # 4. Motion delta - change in motion/action intensity
        risks["motion_delta"] = 1.0 - self._calculate_motion_delta(beat, index, all_beats)

        # 5. Social tension - interpersonal conflict or stakes
        risks["social_tension"] = 1.0 - self._calculate_social_tension(beat, season_memory)

        # 6. Question pressure - unresolved questions or curiosity gaps
        risks["question_pressure"] = 1.0 - self._calculate_question_pressure(beat, season_memory)

        # 7. Visual change - significant visual shift
        risks["visual_change"] = 1.0 - self._calculate_visual_change(beat, index, all_beats)

        # 8. Sound change - significant audio shift
        risks["sound_change"] = 1.0 - self._calculate_sound_change(beat, index, all_beats)

        # 9. Reward signal - emotional or narrative payoff
        risks["reward_signal"] = 1.0 - self._calculate_reward_signal(beat)

        # 10. Fatigue risk - cumulative fatigue from previous beats
        risks["fatigue_risk"] = self._calculate_fatigue_risk(index, all_beats)

        return risks

    def _calculate_novelty(self, beat: dict, index: int, all_beats: list[dict]) -> float:
        """Calculate novelty score (0-1, higher = more novel)."""
        # Simplified: check if mechanism is rare in recent beats
        mechanism = beat.get("mechanism", "")
        if not mechanism:
            return 0.5
        # Count usage in last 5 beats
        recent_mechanisms = [b.get("mechanism", "") for b in all_beats[max(0, index - 5):index]]
        usage_count = recent_mechanisms.count(mechanism)
        # Normalize: 0 uses = 1.0 novelty, 5 uses = 0.0 novelty
        return max(0.0, 1.0 - (usage_count / 5.0))

    def _calculate_information_delta(self, beat: dict[str, Any]) -> float:
        """Calculate information delta (0-1, higher = more information change)."""
        revealed = beat.get("information_revealed", 0)
        withheld = beat.get("information_withheld", 0)
        total = revealed + withheld
        if total == 0:
            return 0.5
        # Ratio of revealed to total, normalized to 0-1
        return min(1.0, revealed / max(1, total))

    def _calculate_emotion_delta(self, beat: dict, index: int, all_beats: list[dict]) -> float:
        """Calculate emotion delta (0-1, higher = more emotion change)."""
        if index == 0:
            return 0.5  # no previous beat to compare
        prev_emotion = all_beats[index - 1].get("emotion_end", "neutral")
        curr_emotion = beat.get("emotion_end", "neutral")
        # Simple emotion change detection
        emotion_intensity = {
            "neutral": 0.0,
            "curiosity": 0.3,
            "tension": 0.5,
            "shock": 0.9,
            "betrayal": 0.9,
            "anger": 0.8,
            "fear": 0.8,
            "joy": 0.7,
            "sadness": 0.7,
            "surprise": 0.8,
            "suspense": 0.7,
        }
        prev_intensity = emotion_intensity.get(prev_emotion, 0.0)
        curr_intensity = emotion_intensity.get(curr_emotion, 0.0)
        delta = abs(curr_intensity - prev_intensity)
        return min(1.0, delta * 2.0)  # scale so 0.5 delta = 1.0

    def _calculate_motion_delta(self, beat: dict, index: int, all_beats: list[dict]) -> float:
        """Calculate motion delta (0-1, higher = more motion change)."""
        if index == 0:
            return 0.5
        prev_motion = all_beats[index - 1].get("motion_intensity", 0.0)
        curr_motion = beat.get("motion_intensity", 0.0)
        delta = abs(curr_motion - prev_motion)
        return min(1.0, delta * 2.0)  # scale

    def _calculate_social_tension(self, beat: dict[str, Any], season_memory: dict) -> float:
        """Calculate social tension (0-1, higher = more tension)."""
        # Based on character conflicts, stakes, secrets
        conflict_level = beat.get("conflict_level", 0.0)
        stakes = beat.get("stakes", 0.0)
        secrecy = beat.get("secrecy_level", 0.0)
        # Combine factors
        tension = (conflict_level + stakes + secrecy) / 3.0
        return min(1.0, tension)

    def _calculate_question_pressure(self, beat: dict[str, Any], season_memory: dict) -> float:
        """Calculate question pressure (0-1, higher = more question pressure)."""
        unresolved_questions = beat.get("unresolved_questions", 0)
        curiosity_gaps = beat.get("curiosity_gaps", 0)
        # Normalize assuming max 5 questions/gaps per beat
        pressure = (unresolved_questions + curiosity_gaps) / 10.0
        return min(1.0, pressure)

    def _calculate_visual_change(self, beat: dict, index: int, all_beats: list[dict]) -> float:
        """Calculate visual change (0-1, higher = more visual change)."""
        if index == 0:
            return 0.5
        # Compare visual descriptors
        prev_visual = all_beats[index - 1].get("visual_focus", "")
        curr_visual = beat.get("visual_focus", "")
        # Simple string comparison - in production would use embeddings
        if prev_visual == curr_visual:
            return 0.0  # no change
        # Check for major shifts (e.g., ECU to WS)
        visual_shift_indicators = [
            ("ecu", "ws"),
            ("ws", "ecu"),
            ("close_up", "wide_shot"),
            ("wide_shot", "close_up"),
        ]
        prev_lower = prev_visual.lower()
        curr_lower = curr_visual.lower()
        for shift in visual_shift_indicators:
            if shift[0] in prev_lower and shift[1] in curr_lower:
                return 1.0  # major shift
        return 0.5  # minor change

    def _calculate_sound_change(self, beat: dict, index: int, all_beats: list[dict]) -> float:
        """Calculate sound change (0-1, higher = more sound change)."""
        if index == 0:
            return 0.5
        # Compare audio descriptors
        prev_sound = all_beats[index - 1].get("sound_state", "")
        curr_sound = beat.get("sound_state", "")
        if prev_sound == curr_sound:
            return 0.0
        # Check for major audio shifts
        audio_shift_indicators = [
            ("silence", "bass_drop"),
            ("bass_drop", "silence"),
            ("heartbeat", "shout"),
            ("shout", "heartbeat"),
            ("music", "sfx"),
            ("sfx", "music"),
        ]
        prev_lower = prev_sound.lower()
        curr_lower = curr_sound.lower()
        for shift in audio_shift_indicators:
            if shift[0] in prev_lower and shift[1] in curr_lower:
                return 1.0
        return 0.5

    def _calculate_reward_signal(self, beat: dict[str, Any]) -> float:
        """Calculate reward signal (0-1, higher = more reward)."""
        # Based on emotional payoff, revelation, or goal achievement
        emotion = beat.get("emotion_end", "").lower()
        revelation = beat.get("information_revealed", 0)
        goal_progress = beat.get("goal_progress", 0.0)
        # Emotions associated with reward
        reward_emotions = ["joy", "satisfaction", "relief", "validation", "vindication", "euphoria"]
        emotion_score = 1.0 if any(emo in emotion for emo in reward_emotions) else 0.0
        # Normalize revelation and goal progress
        revelation_score = min(1.0, revelation / 5.0)  # assume max 5 revelations
        goal_score = min(1.0, goal_progress)
        return (emotion_score + revelation_score + goal_score) / 3.0

    def _calculate_fatigue_risk(self, index: int, all_beats: list[dict]) -> float:
        """Calculate fatigue risk (0-1, higher = more fatigue)."""
        if index == 0:
            return 0.0
        # Simple cumulative fatigue: more beats = more fatigue
        # Reset after high-reward beats
        fatigue = index / len(all_beats)  # linear increase
        # Reduce fatigue if previous beat was high reward
        if index > 0:
            prev_reward = self._calculate_reward_signal(all_beats[index - 1])
            if prev_reward > 0.7:
                fatigue *= 0.5  # halve fatigue after reward
        return min(1.0, fatigue)

    def _determine_retention_action(self, risks: dict[str, float], beat: dict[str, Any]) -> str:
        """
        Determine retention action based on risk factors.
        Returns one of: KEEP, SHORTEN, SPLIT, REFRAME, INSERT, MOVE, SILENCE, REVEAL-LATER, ADD-QUESTION, REMOVE-EXPOSITION
        """
        # Check for hard fails first (should trigger specific actions)
        if risks["fatigue_risk"] > self.risk_thresholds["fatigue_risk_high"]:
            # High fatigue suggests need for change
            if risks["novelty"] < self.risk_thresholds["novelty_low"]:
                return "REFRAME"  # change the framing to renew interest
            elif risks["information_delta"] < self.risk_thresholds["information_delta_low"]:
                return "ADD-QUESTION"  # add a question to re-engage
            else:
                return "SHORTEN"  # shorten to reduce fatigue

        # Check for stagnation risks
        if risks["information_delta"] < self.risk_thresholds["information_delta_low"] and \
           risks["emotion_delta"] < self.risk_thresholds["emotion_delta_low"] and \
           risks["motion_delta"] < self.risk_thresholds["motion_delta_low"]:
            # Low information, emotion, motion -> likely exposition or stagnation
            if risks["question_pressure"] < self.risk_thresholds["question_pressure_low"]:
                return "ADD-QUESTION"  # need to open a question
            elif risks["novelty"] < self.risk_thresholds["novelty_low"]:
                return "INSERT"  # insert something novel
            else:
                return "REFRAME"  # reframe the same content

        # Check for predictability (low novelty)
        if risks["novelty"] < self.risk_thresholds["novelty_low"]:
            if risks["question_pressure"] > 0.7:
                return "REVEAL-LATER"  # delay revealing to maintain question pressure
            else:
                return "REFRAME"  # change the approach

        # Check for missing question pressure when needed
        if risks["question_pressure"] < self.risk_thresholds["question_pressure_low"] and \
           risks["information_delta"] > 0.5:  # we gave information but no question
            return "ADD-QUESTION"

        # Check for excessive dialogue without change (would need dialogue analysis)
        # For now, rely on emotion/motion delta
        if risks["emotion_delta"] < self.risk_thresholds["emotion_delta_low"] and \
           risks["motion_delta"] < self.risk_thresholds["motion_delta_low"]:
            # Dialogue-heavy beat with no change
            if risks["visual_change"] > 0.7 or risks["sound_change"] > 0.7:
                return "KEEP"  # visual/audio change carries it
            else:
                return "SHORTEN"  # shorten dialogue-heavy segment

        # Check for reward signal - if we just had a reward, we can maintain
        if risks["reward_signal"] > 0.7:
            return "KEEP"  # reward justifies keeping

        # Default to KEEP if no strong signals
        return "KEEP"

    def _explain_action(self, risks: dict[str, float], action: str) -> str:
        """Generate human-readable explanation for the retention action."""
        explanations = {
            "KEEP": "Segment maintains adequate engagement across multiple dimensions",
            "SHORTEN": "Segment shows signs of stagnation; shortening recommended to maintain pace",
            "SPLIT": "Segment too dense; splitting into sub-segments recommended",
            "REFRAME": "Segment needs different framing or perspective to renew interest",
            "INSERT": "Segment benefits from inserting a novel element or pattern interrupt",
            "MOVE": "Segment would be more effective at a different temporal position",
            "SILENCE": "Segment needs strategic silence to process information or build tension",
            "REVEAL-LATER": "Information should be delayed to maintain question pressure",
            "ADD-QUESTION": "Segment needs an open question to engage audience curiosity",
            "REMOVE-EXPOSITION": "Segment contains excessive exposition without narrative stakes",
        }
        base = explanations.get(action, "Action determined by risk factor analysis")
        # Add key risk factors
        high_risks = [k for k, v in risks.items() if v > 0.7]
        low_risks = [k for k, v in risks.items() if v < 0.3]
        details = []
        if high_risks:
            details.append(f"High risk: {', '.join(high_risks)}")
        if low_risks:
            details.append(f"Low risk: {', '.join(low_risks)}")
        if details:
            return f"{base} ({'; '.join(details)})"
        return base

    def _generate_recommendations(self, actions: list[dict], risks: list[dict]) -> list[str]:
        """Generate overall recommendations for the episode."""
        recommendations = []
        # Count actions
        action_counts = {}
        for act in actions:
            a = act["action"]
            action_counts[a] = action_counts.get(a, 0) + 1

        total = len(actions)
        if total == 0:
            return ["No microbeats analyzed"]

        # Recommend based on prevalent actions
        if action_counts.get("SHORTEN", 0) > total * 0.3:
            recommendations.append(
                f"Consider shortening {action_counts['SHORTEN']} segments to improve pacing"
            )
        if action_counts.get("ADD-QUESTION", 0) > total * 0.2:
            recommendations.append(
                f"Add open questions in {action_counts['ADD-QUESTION']} segments to maintain curiosity"
            )
        if action_counts.get("REFRAME", 0) > total * 0.25:
            recommendations.append(
                f"Reframe {action_counts['REFRAME']} segments with different perspectives or visual approaches"
            )
        if action_counts.get("INSERT", 0) > total * 0.15:
            recommendations.append(
                f"Insert novel elements or pattern interrupts in {action_counts['INSERT']} segments"
            )
        if action_counts.get("REVEAL-LATER", 0) > total * 0.1:
            recommendations.append(
                f"Delay revelation in {action_counts['REVEAL-LATER']} segments to build sustained question pressure"
            )

        # Check for fatigue accumulation
        fatigue_scores = [r.get("fatigue_risk", 0) for r in risks]
        if fatigue_scores and max(fatigue_scores) > 0.8:
            recommendations.append(
                "High fatigue detected toward end; consider inserting a reward or major shift before fatigue peak"
            )

        # Check for lack of novelty
        novelty_scores = [r.get("novelty", 0) for r in risks]
        if novelty_scores and sum(n for n in novelty_scores if n < 0.3) > total * 0.4:
            recommendations.append(
                "Low novelty in many segments; consider varying mechanisms, emotions, or visual approaches"
            )

        if not recommendations:
            recommendations.append(
                "Retention analysis shows good engagement dynamics across segments"
            )

        return recommendations[:5]  # limit to top 5

    def _empty_result(self) -> dict[str, Any]:
        """Return empty result when no input."""
        return {
            "retention_actions": [],
            "risk_scores": [],
            "recommendations": ["No microbeats provided for retention analysis"],
            "episode_num": 0,
            "total_microbeats_analyzed": 0,
        }


# Alias for backward compatibility
RetentionEngine = RetentionEngineAgent
