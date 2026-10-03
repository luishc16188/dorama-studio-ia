"""
CLI Pipeline – Re‑escribe la llamada a la pipeline de generación de episodios
Utiliza el `OrchestrationEngine`, `PersistenceManager` y `PipelineContext`.
"""

from __future__ import annotations

import typer

from dorama_studio.agents.analytics_engine_agent import AnalyticsEngineAgent
from dorama_studio.agents.narrative.master_writer import MasterWriterAgent
from dorama_studio.agents.originality_engine_agent import OriginalityEngineAgent
from dorama_studio.agents.publisher_agent import PublisherAgent
from dorama_studio.agents.seo_optimizer_agent import SEOOptimizerAgent
from dorama_studio.agents.story_architect_agent import StoryArchitectAgent
from dorama_studio.agents.trend_hunter_agent import TrendHunterAgent
from dorama_studio.agents.video_animator_agent import VideoAnimatorAgent
from dorama_studio.agents.viral_analyst_agent import ViralAnalystAgent
from dorama_studio.core.orchestration_engine import orchestrator
from dorama_studio.core.persistence import persistence
from dorama_studio.core.pipeline_context import PipelineContext

app = typer.Typer(help="DORAMA STUDIO: Pipeline CLI")

# Register the agents once
orchestrator.register_agent(
    "TrendHunterAgent", TrendHunterAgent(), dependencies=[], max_retries=2
)
orchestrator.register_agent(
    "ViralAnalystAgent",
    ViralAnalystAgent(),
    dependencies=["TrendHunterAgent"],
    max_retries=2,
)
orchestrator.register_agent(
    "OriginalityEngineAgent",
    OriginalityEngineAgent(),
    dependencies=["TrendHunterAgent"],
    max_retries=2,
)
orchestrator.register_agent(
    "StoryArchitectAgent",
    StoryArchitectAgent(),
    dependencies=["ViralAnalystAgent", "OriginalityEngineAgent"],
    max_retries=2,
)
orchestrator.register_agent(
    "MasterWriterAgent",
    MasterWriterAgent(),
    dependencies=["StoryArchitectAgent"],
    max_retries=2,
)
orchestrator.register_agent(
    "VideoAnimatorAgent",
    VideoAnimatorAgent(),
    dependencies=["MasterWriterAgent"],
    max_retries=2,
)
orchestrator.register_agent(
    "PublisherAgent",
    PublisherAgent(),
    dependencies=["VideoAnimatorAgent"],
    max_retries=2,
)
orchestrator.register_agent(
    "SEOOptimizerAgent",
    SEOOptimizerAgent(),
    dependencies=["PublisherAgent"],
    max_retries=2,
)
orchestrator.register_agent(
    "AnalyticsEngineAgent",
    AnalyticsEngineAgent(),
    dependencies=["SEOOptimizerAgent"],
    max_retries=2,
)


@app.command()
def create_project(
    name: str,
    genre: str,
    episodes: int = typer.Argument(10, help="Número de episodios"),
    concept_seed: str = typer.Option("actor:teacher", help="Semilla del concepto"),
):
    """Create a new project entry in the persistence layer."""
    project_id = persistence.create_project(
        name=name, genre=genre, total_episodes=episodes, concept_seed=concept_seed
    )
    typer.echo(f"Proyecto creado: id={project_id}")
    return project_id


@app.command()
def generate_episode(project_id: str, episode_num: int):
    """Generate a full episode pipeline from start to publish."""
    # Load project data
    project = persistence.get_project(project_id)
    if not project:
        typer.echo(f"Error: proyecto {project_id} no encontrado")
        raise typer.Exit(1)

    # Build initial context
    ctx = PipelineContext(
        project_id=project_id,
        project_name=project["name"],
        genre=project["genre"],
        concept_seed=project["concept_seed"],
        total_episodes=project["total_episodes"],
        episode_num=episode_num,
    )

    # Load characters from persistence (none yet)
    ctx.characters = persistence.get_characters_by_project(project_id)

    # Run the pipeline
    final_ctx = orchestrator.execute_pipeline(ctx)

    # Persist results: episode, beats, visual prompts, etc.
    episode_blueprint = final_ctx.episode_blueprint
    episode_id = persistence.save_episode(project_id, episode_num, episode_blueprint)
    ctx.episode_id = episode_id

    # Save beats
    for beat in final_ctx.beats:
        persistence.save_beat(episode_id, beat)

    # Persist generated visual prompts, audio, videos, etc.
    for vp in final_ctx.visual_prompts:
        persistence.log_generation(
            project_id=project_id,
            agent_name="VideoAnimator",
            input_data=vp,
            output_data={},
            model_used="Veo",
            episode_id=episode_id,
        )

    # Update episode status to finished
    persistence.update_episode_status(episode_id, "completed")
    typer.echo(f"Episodio {episode_num} generado y guardado con id {episode_id}")


if __name__ == "__main__":
    app()
