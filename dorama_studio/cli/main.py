#!/usr/bin/env python3
"""
DORAMA STUDIO IA - CLI Principal
Fabrica automatizada de microdramas virales verticales
"""

import typer

# Import all agents
from dorama_studio.agents import (
    AnalyticsEngineAgent,
    FeedbackLoopAgent,
    MasterWriterAgent,
    OriginalityEngineAgent,
    StoryArchitectAgent,
    TrendHunterAgent,
    ViralAnalystAgent,
)
from dorama_studio.data.schemas import *

app = typer.Typer(
    help="DORAMA STUDIO IA - Fabrica automatizada de microdramas virales verticales"
)


@app.command()
def create_season(
    idea: str = typer.Argument(..., help="Idea básica para la temporada"),
    genre: str = typer.Option("romance_traicion", help="Género de la temporada"),
    episodes: int = typer.Option(20, help="Número de episodios"),
    dry_run: bool = typer.Option(False, help="Ejecutar en modo simulación"),
):
    """Crear una temporada completa"""
    typer.echo(f"Creando temporada: {idea}")
    typer.echo(f"Género: {genre}")
    typer.echo(f"Episodios: {episodes}")
    if dry_run:
        typer.echo("Modo: SIMULACIÓN (sin generar archivos reales)")
    else:
        typer.echo("Modo: PRODUCCIÓN")

    # Use real agents
    try:
        # Step 1: Hunt trends
        trend_hunter = TrendHunterAgent()
        trends_result = trend_hunter.hunt_trends(
            genre=genre,
            platforms=["TikTok", "YouTube Shorts", "Instagram Reels"],
            concept_seed=idea,
            num_episodes=episodes,
        )
        typer.echo(
            f"[OK] Tendencias cazadas: {len(trends_result.get('top_trends', []))} tendencias principales encontradas"
        )

        # Step 2: Check originality
        originality_engine = OriginalityEngineAgent()
        originality_result = originality_engine.check_originality(
            seed=idea,
            genre=genre,
            cliches={},  # In real implementation, this would come from trend analysis
            autoplagio={},  # In real implementation, this would come from previous seasons
            trends=trends_result,
        )
        typer.echo(
            f"[OK] Originalidad evaluada: {originality_result.get('originality_score', 0)}/100"
        )

        # Step 3: Architect story
        story_architect = StoryArchitectAgent()
        story_result = story_architect.architect_story(
            concept_seed=idea, genre=genre, num_episodes=episodes
        )
        typer.echo(
            f"[OK] Historia arquitectada: {len(story_result.get('episodes', []))} episodios planeados"
        )

        # Step 4: Create characters and bible (already in story_result)
        typer.echo(
            f"[OK] Biblia de personajes creada con {len(story_result.get('character_bible', []))} personajes"
        )

        if not dry_run:
            # In a real implementation, we would save these results to files/database
            typer.echo("[OK] Temporada creada exitosamente (resultados en memoria)")
        else:
            typer.echo("[OK] Temporada creada exitosamente (modo simulación)")

    except Exception as e:
        typer.echo(f"[ERROR] Error al crear temporada: {e!s}")
        raise typer.Exit(code=1)


@app.command()
def create_episode(
    project_id: str = typer.Argument(..., help="ID del proyecto"),
    episode: int = typer.Argument(..., help="Número de episodio"),
    feedback: str | None = typer.Option(None, help="Feedback para mejorar el episodio"),
):
    """Producir un solo episodio con feedback"""
    typer.echo(f"Creando episodio {episode} para proyecto {project_id}")
    if feedback:
        typer.echo(f"Feedback: {feedback}")

    # Use real agents
    try:
        # For demonstration, we'll create a mock blueprint and character bible
        # In a real implementation, these would come from the project data

        # Mock character bible entry (simplified)
        from dorama_studio.data.schemas import (
            CharacterBibleEntry,
            ContinuityRules,
            MicroExpressions,
            PhysicalTraits,
            VoiceProfile,
            Wardrobe,
        )

        mock_character = CharacterBibleEntry(
            id="char_001",
            name="Protagonista Ejemplo",
            role="protagonist",
            archetype="ruler",
            want="Ejemplo de deseo",
            need="Ejemplo de necesidad",
            lie="Ejemplo de mentira",
            ghost="Ejemplo de fantasma",
            secret="Ejemplo de secreto",
            physical=PhysicalTraits(
                height_cm=170,
                build="athletic",
                hair_color="brown",
                hair_style="short",
                eye_color="#000000",
                skin_tone="fair",
                distinguishing_marks=[],
                age_apparent=25,
                face_shape="oval",
                bone_structure="average",
            ),
            micro_expressions=MicroExpressions(
                tell="none",
                eye_dart="none",
                micro_smile=False,
                jaw_clench=False,
                breath_hitch=False,
            ),
            voice_profile=VoiceProfile(
                voice_id="example",
                accent="es-419",
                pitch_range="medium",
                speaking_rate="medium",
                breathiness=0.0,
                roughness=0.0,
                emotional_range={"neutral": 0.5},
            ),
            wardrobe=Wardrobe(
                signature_style="casual",
                color_palette=["black", "white"],
                key_items=["t-shirt", "jeans"],
                accessories=[],
            ),
            continuity_rules=ContinuityRules(
                locked_traits=["eye_color", "bone_structure"],
                allowed_variations={"hair_style": ["short", "long"]},
                drift_tolerance=0.05,
                deform_prohibited=["eye_color"],
                master_reference_prompt="prompt de ejemplo",
                psychological_arc_by_episode=[],
            ),
        )

        # Mock episode blueprint (simplified)
        from dorama_studio.data.schemas import CTAType, EpisodeBlueprint, HookCategory

        mock_blueprint = EpisodeBlueprint(
            ep=episode,
            hook_category=HookCategory.revelation,
            core_conflict="Conflicto de ejemplo",
            twist="Giro de ejemplo",
            cliffhanger="Revelación que lleva al próximo episodio",
            cta_type=CTAType.MORAL_DILEMMA,
        )

        # Use MasterWriterAgent to write the episode
        master_writer = MasterWriterAgent()
        # We need to call a method that writes the episode - looking at the agent, we see _deterministic_beats
        # For now, we'll call that method to demonstrate usage
        beats_result = master_writer._deterministic_beats(
            blueprint=mock_blueprint,
            characters=[mock_character],
            ep=episode,
            total_episodes=20,
            seed={"theme": "ejemplo"},
        )

        typer.echo(
            f"[OK] Episodio escrito: {len(beats_result.get('beats', []))} beats generados"
        )

        # In a real implementation, we would also use other agents:
        # - StoryboardAgent to create storyboards
        # - VisualAgent for visual direction
        # - etc.

        typer.echo("[OK] Episodio creado exitosamente")

    except Exception as e:
        typer.echo(f"[ERROR] Error al crear episodio: {e!s}")
        raise typer.Exit(code=1)


@app.command()
def analyze(
    project_id: str = typer.Argument(..., help="ID del proyecto"),
    platform: str = typer.Option("tiktok", help="Plataforma a analizar"),
):
    """Analizar rendimiento de un proyecto"""
    typer.echo(f"Analizando proyecto {project_id} en plataforma {platform}")

    # Use real agents
    try:
        # For demonstration, we'll use AnalyticsEngineAgent and FeedbackLoopAgent
        # In a real implementation, we would fetch actual project data

        # Mock video data for ViralAnalystAgent (if we had it)
        mock_video_data = [
            {
                "id": "vid_001",
                "platform": platform,
                "duration": 90,
                "hook_retention": 0.85,
                "completion_rate": 0.75,
                "engagement_rate": 0.12,
            }
        ]

        # Use ViralAnalystAgent to analyze viral patterns
        viral_analyst = ViralAnalystAgent()
        viral_result = viral_analyst.analyze_viral_patterns(
            video_data=mock_video_data,
            genre="romance_traicion",  # In real implementation, this would come from project data
        )
        typer.echo(
            f"[OK] Análisis viral completado: {len(viral_result.get('actionable_insights', []))} insights accionables"
        )

        # Use AnalyticsEngineAgent to analyze metrics
        analytics_engine = AnalyticsEngineAgent()
        # In real implementation, we would pass actual metrics
        mock_metrics = {
            "views": [1000, 1500, 2000, 1800, 2200],
            "likes": [50, 75, 100, 90, 110],
            "comments": [10, 15, 20, 18, 22],
            "shares": [5, 8, 12, 10, 15],
        }
        mock_published_episodes = {
            "video_metadata": {"fps": 30, "duration_seconds": 90},
            "platform_analytics": {"retention": [0.95, 0.85, 0.80, 0.75]},
            "episode_package": {"beats": []},
        }
        analytics_result = analytics_engine.analyze_performance(
            published_episodes=mock_published_episodes, project_id=project_id
        )
        typer.echo(
            f"[OK] Análisis de analytics completado: crecimiento estimado {analytics_result.get('growth_rate', 0):.1f}%"
        )

        # Use FeedbackLoopAgent to process feedback
        feedback_loop = FeedbackLoopAgent()
        mock_comments = [
            {"text": "¡Me encantó el giro!", "likes": 25},
            {"text": "¿Quién es el verdadero villano?", "likes": 18},
            {"text": "Esperaba más acción", "likes": 5},
        ]
        mock_analytics = {
            "retention_curve": {"overall": 0.8},
            "drop_off_points": [],
            "hook_performance": {"hook_retention": 0.9},
            "character_engagement": {"protagonist": 0.9},
            "cta_conversion": {"ctr": 0.08, "comment_rate": 0.03},
            "completion_rate": 0.75,
            "benchmark_vs_genre": {"vs_genre": "above_average"},
            "causal_heatmap": [],
            "causal_attributions": [],
            "optimization_recommendations": [],
        }
        feedback_input = {
            "analytics_report": mock_analytics,
            "next_episode_num": 2,
            "season_arc": {},
            "character_bible": [],
            "genome_state": {},
            "untested_ideas": [],
        }
        feedback_result = feedback_loop.run(feedback_input)
        typer.echo(
            f"[OK] Procesamiento de feedback completado: {feedback_result.get('next_hypothesis', 'no hypothesis')}"
        )

        typer.echo("[OK] Análisis completado exitosamente")

    except Exception as e:
        typer.echo(f"[ERROR] Error al analizar: {e!s}")
        raise typer.Exit(code=1)


@app.command()
def list_agents():
    """Listar todos los agentes disponibles"""
    agents = [
        "01 Trend Hunter",
        "02 Viral Analyst",
        "03 Originality Engine",
        "04 Story Architect",
        "05 Master Writer",
        "06 Hook Engine",
        "07 CTA Writer",
        "08 Episode Scorer",
        "09 Hook Engine",  # Note: This appears to be a duplicate in the original list
        "10 Visual Agent",
        "11 Storyboard Agent",
        "12 Keyframe Agent",
        "13 Voice Director",
        "14 Sound Designer",
        "15 Music Supervisor",
        "16 Video Agent",
        "17 Editor Agent",
        "18 Subtitle Agent",
        "19 Publisher",
        "20 SEO Optimizer",
        "21 Analytics Engine",
        "22 Feedback Loop",
    ]
    typer.echo("[OK] Agentes disponibles en Dorama Studio IA:")
    for i, agent in enumerate(agents, 1):
        typer.echo(f"{i:2d}. {agent}")


@app.command()
def version():
    """Mostrar versión de Dorama Studio IA"""
    typer.echo("DORAMA STUDIO IA v0.1.0")


if __name__ == "__main__":
    app()
