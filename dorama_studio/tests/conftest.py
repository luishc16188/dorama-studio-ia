import pytest


@pytest.fixture
def agent_name():
    return "TestAgent"

@pytest.fixture
def agent_instance():
    from dorama_studio.agents.base_agent import BaseAgent

    class TestAgent(BaseAgent):
        def _process(self, input_data):
            return {"status": "ok"}

        def run(self, input_data):
            return self.process(input_data)
    return TestAgent("Test")

@pytest.fixture
def input_obj():
    return {"test_key": "test_value"}
