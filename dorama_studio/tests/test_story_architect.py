from dorama_studio.agents.schemas.story_architect_schemas import StoryArchitectInput
from dorama_studio.agents.story_architect import StoryArchitectAgent

agent = StoryArchitectAgent()
print("Agent created")

# Test with sample data
input_data = StoryArchitectInput(
    viral_potential={
        "hook_categories": ["revenge", "betrayal", "identity"],
        "hook_strength": 0.8,
    },
    originality_report={
        "is_original": True,
        "novelty_score": 75.0,
        "cliche_score": 25.0,
        "mechanism_extracted": "Trust violation and reconstruction",
    },
)

result = agent.process(input_data)
print(f"Status: {result.status}")
print(f"Beat Hook: {result.beat_hook[:50]}...")
print(f"Beat Promise: {result.beat_promise[:50]}...")
print(f"Beat Question: {result.beat_question[:50]}...")
print(f"Beat Escalation: {result.beat_escalation[:50]}...")
print(f"Beat Reward: {result.beat_reward[:50]}...")
print(f"Beat Question2: {result.beat_question2[:50]}...")
print(f"Beat Cliffhanger: {result.beat_cliffhanger[:50]}...")
print(f"Narrative Mechanism: {result.narrative_mechanism}")
print(f"Emotional Arc: {result.emotional_arc}")
print(f"Beat Ratings: {result.beat_ratings}")
print(f"Total Score: {result.total_narrative_score}")
