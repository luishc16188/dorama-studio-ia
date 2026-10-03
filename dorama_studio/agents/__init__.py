"""Agents package for DORAMA STUDIO IA V2 - Canonical Exports Only.

This module exports only the canonical agent implementations.
Duplicate/legacy agents are NOT exported from here.
Use dorama_studio.agents.legacy for deprecated agents if needed.
"""

from .base_agent import BaseAgent
from .contract import AgentContract, EpisodeSpecV2

# Canonical Agent Registry - maps capability to canonical implementation
CANONICAL_AGENTS = {
    # Research
    "trend_intelligence": "dorama_studio.agents.trend_hunter_agent.TrendHunterAgent",
    "reference_forensics": "dorama_studio.agents.investigation.viral_analyst.ViralAnalystAgent",
    "audience_evidence": "dorama_studio.agents.analytics_agent.AnalyticsAgent",
    "originality": "dorama_studio.agents.originality_engine_agent.OriginalityEngineAgent",

    # Story Development
    "season_architect": "dorama_studio.agents.story_architect_agent.StoryArchitectAgent",
    "episode_architect": "dorama_studio.agents.narrative.story_architect.StoryArchitectAgent",
    "mystery_planner": "dorama_studio.agents.narrative.master_writer.MasterWriterAgent",

    # Writing
    "master_writer": "dorama_studio.agents.narrative.master_writer.MasterWriterAgent",
    "dialogue_polisher": "dorama_studio.agents.narrative.master_writer.MasterWriterAgent",
    "hook_engine": "dorama_studio.agents.hook_engine_agent.HookEngineAgent",
    "retention_engine": "dorama_studio.agents.narrative.retention_engine.RetentionEngineAgent",
    "cliffhanger_engine": "dorama_studio.agents.narrative.cliffhanger_engine.CliffhangerEngineAgent",
    "cta_community": "dorama_studio.agents.cta_writer_agent.CTAWriterAgent",
    "story_critic": "dorama_studio.agents.narrative.episode_scorer.EpisodeScorerAgent",

    # Character
    "character_director": "dorama_studio.agents.character_director_agent.CharacterDirectorAgent",
    "continuity_state": "dorama_studio.agents.character_director_agent.CharacterDirectorAgent",

    # Directing
    "director_engine": "dorama_studio.agents.visual_director_agent.VisualDirectorAgent",
    "storyboard": "dorama_studio.agents.storyboard_agent.StoryboardAgent",
    "shot_planner": "dorama_studio.agents.shot_planner_agent.ShotPlannerAgent",
    "acting_motion_planner": "dorama_studio.agents.acting_motion_planner_agent.ActingMotionPlannerAgent",

    # Visual/Video
    "reference_frame": "dorama_studio.agents.visual.keyframe_agent.KeyframeAgent",
    "prompt_compiler": "dorama_studio.pipeline.prompt_compiler.PromptCompiler",
    "provider_router": "dorama_studio.router.model_router.ModelRouter",
    "video_renderer": "dorama_studio.agents.production.video_agent.VideoAgent",
    "render_qc": "dorama_studio.agents.quality_check_agent.QualityCheckAgent",

    # Voice/Sound/Music
    "voice_director": "dorama_studio.agents.audio.voice_director_agent.VoiceDirectorAgent",
    "sound_director": "dorama_studio.agents.audio.sound_designer_agent.SoundDesignerAgent",
    "music_supervisor": "dorama_studio.agents.audio.music_supervisor_agent.MusicSupervisorAgent",
    "audio_render": "dorama_studio.agents.audio_engineer_agent.AudioEngineerAgent",

    # Editing
    "edit_composer": "dorama_studio.agents.production.editor_agent.EditorAgent",
    "caption_composer": "dorama_studio.agents.production.subtitle_agent.SubtitleAgent",

    # Quality
    "story_qc": "dorama_studio.agents.narrative.episode_scorer.EpisodeScorerAgent",
    "visual_qc": "dorama_studio.agents.quality_check_agent.QualityCheckAgent",
    "audio_qc": "dorama_studio.agents.quality_check_agent.QualityCheckAgent",
    "continuity_qc": "dorama_studio.agents.narrative.continuity_lock_agent.ContinuityLockAgent",
    "platform_qc": "dorama_studio.agents.quality_check_agent.QualityCheckAgent",
    "final_scorer": "dorama_studio.agents.narrative.episode_scorer.EpisodeScorerAgent",
    "multimodal_quality": "dorama_studio.agents.multimodal_quality_agent.MultimodalQualityAgent",
    "selective_regeneration": "dorama_studio.agents.selective_regeneration_orchestrator.SelectiveRegenerationOrchestrator",

    # Distribution
    "distribution_publisher": "dorama_studio.agents.distribution_agent.DistributionAgent",

    # Analytics/Learning
    "measurement_engine": "dorama_studio.agents.analytics_engine_agent.AnalyticsEngineAgent",
    "feedback_loop": "dorama_studio.agents.feedback_loop_agent.FeedbackLoopAgent",
    "creative_genome_policy": "dorama_studio.agents.creative_genome_agent.CreativeGenomeAgent",
    "experiment": "dorama_studio.agents.learning.analytics_engine.AnalyticsEngineAgent",
    "analytics_v2": "dorama_studio.agents.analytics_engine_v2.AnalyticsEngineV2",
    "feedback_v2": "dorama_studio.agents.feedback_loop_v2.FeedbackLoopV2",

    # Orchestration
    "production_supervisor": "dorama_studio.pipeline.orchestrator.DoramaGraphFactory",
    "engineering_audit": "dorama_studio.agents.audit_agents.AuditAgents",
    "master_timeline": "dorama_studio.agents.master_timeline_agent.MasterTimelineAgent",
    "claude_codex_collaboration": "dorama_studio.agents.claude_codex_collaboration_agent.ClaudeCodexCollaborationAgent",
}

# Only export canonical agents to prevent duplicate execution
__all__ = [
    "BaseAgent",
    "EpisodeSpecV2",
    "AgentContract",
    "CANONICAL_AGENTS",
]

# Convenience imports for canonical agents
def get_canonical_agent(capability: str):
    """Get the canonical agent class for a capability."""
    import importlib
    path = CANONICAL_AGENTS.get(capability)
    if not path:
        raise ValueError(f"No canonical agent for capability: {capability}")
    module_path, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
