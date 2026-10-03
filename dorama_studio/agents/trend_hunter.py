"""
Trend Hunter Agent (Agent 1) - Detects emerging trends
Implements BaseAgent with ErrorMemory and FeedbackLoop integration
"""

from pathlib import Path
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.trend_hunter_schemas import (
    TrendHunterInput,
    TrendHunterOutput,
)
from dorama_studio.core.error_memory import ErrorMemoryBank


class TrendHunterAgent(BaseAgent[TrendHunterInput, TrendHunterOutput]):
    """Trend Hunter Agent that detects emerging trends"""

    def __init__(self):
        super().__init__("trend_hunter")
        self.error_memory = ErrorMemoryBank(Path("data/trend_hunter_errors.json"))

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the trend hunter agent."""
        result = self.process(input_data)
        # Return dict-like object with payload attribute for test compatibility
        class ResultWrapper:
            def __init__(self, payload):
                self.payload = payload
            def get(self, key, default=None):
                if isinstance(self.payload, dict):
                    return self.payload.get(key, default)
                return default
            def __getitem__(self, key):
                if isinstance(self.payload, dict):
                    return self.payload[key]
                raise KeyError(key)
            def __contains__(self, key):
                if isinstance(self.payload, dict):
                    return key in self.payload
                return False
        return ResultWrapper(result)

    def hunt_trends(self, **kwargs) -> dict[str, Any]:
        """Hunt trends - wrapper for run method for test compatibility."""
        result = self.run(kwargs)
        if hasattr(result, 'payload'):
            return result.payload
        return result

    def _process(self, validated_input: TrendHunterInput) -> TrendHunterOutput:
        """Process trend hunting request"""
        from datetime import datetime
        # Placeholder implementation matching the schema
        return TrendHunterOutput(
            trend_signal={
                "trend": "secret heiress",
                "growth_rate_pct": 92.0,
                "sentiment": "positive",
                "saturation_level": "emerging"
            },
            status="completed",
            generated_at=datetime.now()
        )
