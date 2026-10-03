from dorama_studio.agents.schemas.video_animator_schemas import VideoAnimatorInput
from dorama_studio.agents.video_animator_agent import VideoAnimatorAgent

agent = VideoAnimatorAgent()
print("Agent creado")

# Test with master script and visual direction
input_data = VideoAnimatorInput(
    episode_num=1,
    master_script={
        "has_action": True,
        "has_dialogue": True,
        "has_emotional_scene": True,
        "scene_type": "action_drama",
    },
    visual_direction={"style": "cinematic", "mood": "tense"},
    animation_style="cinematic",
)

result = agent.process(input_data)
print(f"Total Prompts: {result.total_prompts}")
print(f"Status: {result.status}")
print("Video Prompts:")
for i, prompt in enumerate(result.video_prompts):
    print(f'  {i+1}. {prompt["description"]} - {prompt["duration"]}s')

# Test with minimal input
input_data_minimal = VideoAnimatorInput(
    episode_num=2, master_script={}, visual_direction={}, animation_style="cinematic"
)

result_minimal = agent.process(input_data_minimal)
print(f"\nMinimal Total Prompts: {result_minimal.total_prompts}")
print(f"Minimal Status: {result_minimal.status}")
