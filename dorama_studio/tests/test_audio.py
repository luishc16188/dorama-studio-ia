from dorama_studio.agents.audio_engineer_agent import AudioEngineerAgent

agent = AudioEngineerAgent()
print("Agent created")

input_data = {
    "episode_num": 1,
    "beats": [
        {"beat_name": "hook", "sound": {"ambience": "dark_room"}},
        {"beat_name": "twist1", "sound": {"ambience": "tension", "silence_drop": True}},
        {"beat_name": "climax", "sound": {"ambience": "epic"}},
    ],
}

result = agent.process(input_data)
print(f'Status: {result["status"]}')
print(f'Prompts: {len(result["audio_prompts"])}')
for p in result["audio_prompts"][:3]:
    print(f'  {p["beat_name"]}: {p["music"]["genre"]} @ {p["music"]["bpm"]}bpm')
