from dorama_studio.agents.originality_engine_agent import OriginalityEngineAgent
from dorama_studio.core.pipeline_context import PipelineContext

# Create a proper PipelineContext for testing
context = PipelineContext(
    project_id="test_project",
    project_name="Test Project",
    genre="romance_traicion",
    concept_seed="secret heiress forbidden love betrayal",  # Contains cliches for testing
    total_episodes=30,
    episode_num=1,
    episode_id="e01"
)

agent = OriginalityEngineAgent()
print("Agent creado")

result = agent.process(context)
print(f"Success: {result.success}")
print(f"Agent: {result.agent_name}")
print(f"Originality data: {result.output_data.get('originality', {})}")
print(f"Latency: {result.latency_ms}ms")
