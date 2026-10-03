"""
Master test for all agents with schemas.
Instantiates each agent and runs a simple process call to ensure no errors.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dorama_studio.agents.analytics_agent import AnalyticsAgent
from dorama_studio.agents.audio_engineer_agent import AudioEngineerAgent
from dorama_studio.agents.audit_agents import AuditAgents
from dorama_studio.agents.character_director_agent import CharacterDirectorAgent
from dorama_studio.agents.creative_genome_agent import CreativeGenomeAgent
from dorama_studio.agents.cta_writer_agent import CTAWriterAgent
from dorama_studio.agents.distribution_agent import DistributionAgent
from dorama_studio.agents.episode_scorer_agent import EpisodeScorerAgent
from dorama_studio.agents.feedback_loop_agent import FeedbackLoopAgent
from dorama_studio.agents.hook_engine_agent import HookEngineAgent
from dorama_studio.agents.narrative.master_writer import MasterWriterAgent
from dorama_studio.agents.originality_engine_agent import OriginalityEngineAgent
from dorama_studio.agents.quality_gate_agent import QualityGateAgent
from dorama_studio.agents.schemas.analytics_schemas import (
    AnalyticsInput,
)
from dorama_studio.agents.schemas.audio_schemas import (
    AudioEngineerInput,
)
from dorama_studio.agents.schemas.audit_schemas import AuditInput
from dorama_studio.agents.schemas.character_director_schemas import (
    CharacterDirectorInput,
)
from dorama_studio.agents.schemas.creative_genome_schemas import (
    CreativeGenomeInput,
)
from dorama_studio.agents.schemas.cta_writer_schemas import (
    CTAWriterInput,
)
from dorama_studio.agents.schemas.distribution_schemas import (
    DistributionInput,
)
from dorama_studio.agents.schemas.episode_scorer_schemas import (
    EpisodeScorerInput,
)
from dorama_studio.agents.schemas.feedback_loop_schemas import (
    FeedbackLoopInput,
)
from dorama_studio.agents.schemas.hook_engine_schemas import (
    HookEngineInput,
)
from dorama_studio.agents.schemas.originality_engine_schemas import (
    OriginalityEngineInput,
)
from dorama_studio.agents.schemas.quality_gate_schemas import (
    QualityGateInput,
)
from dorama_studio.agents.schemas.sfx_designer_schemas import (
    SFXDesignerInput,
)
from dorama_studio.agents.schemas.story_architect_schemas import (
    StoryArchitectInput,
)
from dorama_studio.agents.schemas.trend_hunter_schemas import (
    TrendHunterInput,
)
from dorama_studio.agents.schemas.video_animator_schemas import (
    VideoAnimatorInput,
)
from dorama_studio.agents.schemas.viral_analyst_schemas import (
    ViralAnalystInput,
)
from dorama_studio.agents.schemas.visual_director_schemas import (
    VisualDirectorInput,
)
from dorama_studio.agents.sfx_designer_agent import SFXDesignerAgent
from dorama_studio.agents.story_architect_agent import StoryArchitectAgent
from dorama_studio.agents.trend_hunter_agent import TrendHunterAgent
from dorama_studio.agents.video_animator_agent import VideoAnimatorAgent
from dorama_studio.agents.viral_analyst_agent import ViralAnalystAgent
from dorama_studio.agents.visual_director_agent import VisualDirectorAgent


def test_agent(agent_name, agent_instance, input_obj):
    try:
        result = agent_instance.process(input_obj)
        print(
            f"[OK] {agent_name}: process executed, result type: {type(result).__name__}"
        )
        return True
    except Exception as e:
        print(f"[FAIL] {agent_name}: {e}")
        return False


def main():
    print("=== Running agent schema tests ===")
    passed = 0
    total = 0

    # Analytics
    total += 1
    if test_agent(
        "AnalyticsAgent",
        AnalyticsAgent(),
        AnalyticsInput(episode_num=1, distribution_packages=[], released_episodes=[]),
    ):
        passed += 1

    # Audio Engineer
    total += 1
    if test_agent(
        "AudioEngineerAgent",
        AudioEngineerAgent(),
        AudioEngineerInput(episode_num=1, beats=[], master_script={}, breakdown={}),
    ):
        passed += 1

    # Audit
    total += 1
    if test_agent("AuditAgents", AuditAgents(), AuditInput(agents_dir=".")):
        passed += 1

    # Character Director
    total += 1
    if test_agent(
        "CharacterDirectorAgent",
        CharacterDirectorAgent(),
        CharacterDirectorInput(character_bible={}, story_arc={}),
    ):
        passed += 1

    # Creative Genome
    total += 1
    if test_agent(
        "CreativeGenomeAgent",
        CreativeGenomeAgent(),
        CreativeGenomeInput(episode_num=1, genome_data={}),
    ):
        passed += 1

    # CTA Writer
    total += 1
    if test_agent(
        "CTAWriterAgent",
        CTAWriterAgent(),
        CTAWriterInput(episode_num=1, cliffhanger_data={}),
    ):
        passed += 1

    # Distribution
    total += 1
    if test_agent(
        "DistributionAgent",
        DistributionAgent(),
        DistributionInput(
            episode_num=1,
            video_prompts=[],
            audio_prompts=[],
            sfx_cues=[],
            platform="tiktok",
        ),
    ):
        passed += 1

    # Episode Scorer
    total += 1
    if test_agent(
        "EpisodeScorerAgent",
        EpisodeScorerAgent(),
        EpisodeScorerInput(episode_num=1, episode_package={}),
    ):
        passed += 1

    # Feedback Loop
    total += 1
    if test_agent(
        "FeedbackLoopAgent",
        FeedbackLoopAgent(),
        FeedbackLoopInput(episode_num=1, feedback_data={}),
    ):
        passed += 1

    # Hook Engine
    total += 1
    if test_agent(
        "HookEngineAgent",
        HookEngineAgent(),
        HookEngineInput(episode_num=1, hook_category="betrayal", hook_strength=0.5),
    ):
        passed += 1

    # Master Writer
    total += 1
    if test_agent(
        "MasterWriterAgent",
        MasterWriterAgent(),
        {
            "blueprint": {
                "hook_category": "betrayal",
                "core_conflict": "test conflict",
                "twist": "test twist",
                "cliffhanger": "test cliffhanger",
                "cta_type": "question"
            },
            "characters": [],
            "ep": 1,
            "total_episodes": 10,
        },
    ):
        passed += 1

    # Originality Engine
    total += 1
    if test_agent(
        "OriginalityEngineAgent",
        OriginalityEngineAgent(),
        OriginalityEngineInput(
            viral_potential={"hook_categories": ["betrayal"]}, creative_genome={}
        ),
    ):
        passed += 1

    # Quality Gate
    total += 1
    if test_agent(
        "QualityGateAgent",
        QualityGateAgent(),
        QualityGateInput(episode_num=1, episode_score=50.0),
    ):
        passed += 1

    # SFX Designer
    total += 1
    if test_agent(
        "SFXDesignerAgent",
        SFXDesignerAgent(),
        SFXDesignerInput(episode_num=1, master_script={}, audio_direction={}),
    ):
        passed += 1

    # Story Architect
    total += 1
    if test_agent(
        "StoryArchitectAgent",
        StoryArchitectAgent(),
        StoryArchitectInput(
            viral_potential={"hook_categories": ["betrayal"]},
            originality_report={"is_original": True, "novelty_score": 50},
        ),
    ):
        passed += 1

    # Trend Hunter
    total += 1
    if test_agent("TrendHunterAgent", TrendHunterAgent(), TrendHunterInput()):
        passed += 1

    # Video Animator
    total += 1
    if test_agent(
        "VideoAnimatorAgent",
        VideoAnimatorAgent(),
        VideoAnimatorInput(episode_num=1, master_script={}, visual_direction={}),
    ):
        passed += 1

    # Visual Director
    total += 1
    if test_agent(
        "VisualDirectorAgent",
        VisualDirectorAgent(),
        VisualDirectorInput(episode_num=1, universe={}, visual_requirements={}),
    ):
        passed += 1

    # Viral Analyst
    total += 1
    if test_agent(
        "ViralAnalystAgent",
        ViralAnalystAgent(),
        ViralAnalystInput(
            trend_signal={
                "trend_id": "test",
                "trend": "test",
                "growth_rate_pct": 50,
                "sentiment": "neutral",
                "saturation_level": "emerging",
            },
            historical_data=[],
        ),
    ):
        passed += 1

    print(f"\n=== Summary: {passed}/{total} agents passed ===")
    if passed == total:
        print("All agents processed successfully!")
        return 0
    else:
        print("Some agents failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
