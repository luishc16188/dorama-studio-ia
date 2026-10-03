from dorama_studio.agents.schemas.sfx_designer_schemas import SFXDesignerInput
from dorama_studio.agents.sfx_designer_agent import SFXDesignerAgent

agent = SFXDesignerAgent()
print('Agent created')

# Test with master script and audio direction
input_data = SFXDesignerInput(
    episode_num=1,
    master_script={
        'has_action': True,
        'has_dialogue': True,
        'has_emotional_scene': True,
        'scene_type': 'action_drama'
    },
    audio_direction={
        'style': 'cinematic',
        'mood': 'tense'
    }
)

result = agent.process(input_data)
print(f'Total SFX: {result.total_sfx}')
print(f'Status: {result.status}')
print('SFX Cues:')
for i, cue in enumerate(result.sfx_cues):
    print(f'  {i+1}. {cue["description"]} at {cue["timing"]}')

# Test with minimal input
input_data_minimal = SFXDesignerInput(
    episode_num=2,
    master_script={},
    audio_direction={}
)

result_minimal = agent.process(input_data_minimal)
print(f'\\nMinimal Total SFX: {result_minimal.total_sfx}')
print(f'Minimal Status: {result_minimal.status}')
