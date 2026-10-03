from dorama_studio.agents.quality_gate_agent import QualityGateAgent
from dorama_studio.agents.schemas.quality_gate_schemas import QualityGateInput

agent = QualityGateAgent()
print("Agent created")

# Test passing score
input_data = QualityGateInput(
    episode_num=1,
    episode_score=90.0,
    breakdown={"hook": 25, "story": 20, "emotion": 20, "audio": 15, "visual": 10},
    feedback=["Great hook", "Good pacing"],
    threshold=85.0,
)

result = agent.process(input_data)
print(f"Verdict: {result.verdict}")
print(f"Passed: {result.passed}")
print(f"Score: {result.score}")
print(f"Threshold: {result.threshold}")
print(f"Notes: {result.notes}")
print(f"Status: {result.status}")

# Test failing score
input_data_fail = QualityGateInput(
    episode_num=2,
    episode_score=70.0,
    breakdown={"hook": 15, "story": 15, "emotion": 15, "audio": 15, "visual": 10},
    feedback=["Weak hook", "Slow pacing"],
    threshold=85.0,
)

result_fail = agent.process(input_data_fail)
print(f"\\nFail Verdict: {result_fail.verdict}")
print(f"Fail Passed: {result_fail.passed}")
print(f"Fail Score: {result_fail.score}")
print(f"Fail Notes: {result_fail.notes}")
print(f"Fail Status: {result_fail.status}")
