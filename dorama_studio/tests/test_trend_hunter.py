from dorama_studio.agents.trend_hunter_agent import TrendHunterAgent
from dorama_studio.core.pipeline_context import PipelineContext

# Create a proper PipelineContext for testing
context = PipelineContext(
    project_id="test_project",
    project_name="Test Project",
    genre="romance_traicion",
    concept_seed="test concept",
    total_episodes=30,
    episode_num=1,
    episode_id="e01"
)

agent = TrendHunterAgent()
print('Agent created')

# Test with default parameters
result = agent.process(context)
print(f'Success: {result.success}')
print(f'Agent: {result.agent_name}')
print(f'Trends data: {result.output_data.get("trends", {})}')
print(f'Latency: {result.latency_ms}ms')
