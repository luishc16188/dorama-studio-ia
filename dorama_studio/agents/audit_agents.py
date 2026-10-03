"""
Agent Audit Script - Standardized with Pydantic schemas.
"""

import ast
import logging
import os
from pathlib import Path
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent

# Import the base agent to inherit from

logger = logging.getLogger(__name__)


class AuditAgents(BaseAgent):
    """
    Agent Audit Script - Standardized with Pydantic schemas.
    Walks through the agents directory and performs basic checks:
    - File existence
    - Syntax validity
    - Presence of required methods
    """

    InputSchema = "AuditInput"
    OutputSchema = "AuditOutput"

    def __init__(self):
        super().__init__("AuditAgents")
        self.agents_root = Path(__file__).parent

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the audit agents."""
        return self.process(input_data)

    def _process(self, validated_input) -> dict[str, Any]:
        """
        Audit all agents in the agents directory.
        Returns audit results for all agents.
        """
        results = []
        # Handle both dict and Pydantic model
        if hasattr(validated_input, 'model_dump'):
            agents_dir = getattr(validated_input, 'agents_dir', str(Path(__file__).parent))
        elif hasattr(validated_input, 'get'):
            agents_dir = validated_input.get("agents_dir", str(Path(__file__).parent))
        else:
            agents_dir = str(Path(__file__).parent)
        agents_root = Path(agents_dir)

        for root, dirs, files in os.walk(agents_root):
            for f in files:
                if f.endswith(".py") and not f.startswith("__"):
                    p = Path(root) / f
                    info = self._check_file(p)
                    results.append(info)

        return {"audit_results": {"results": results}, "status": "completed"}

    def _check_file(self, path: Path) -> dict[str, Any]:
        """Return a dict with status and any errors."""
        result = {"file": str(path), "syntax_ok": False, "has_process": False}
        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source)
            result["syntax_ok"] = True
            if "def process" in source or "async def process" in source:
                result["has_process"] = True
        except Exception as e:
            result["error"] = str(e)
        return result

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Public process method that calls _process."""
        return self._process(input_data)


if __name__ == "__main__":

    agent = AuditAgents()
    # Run with default agents directory
    result = agent.process({"agents_dir": str(Path(__file__).parent)})
    print(f"Audit completed: {result['status']}")
    print(f"Agents checked: {len(result['audit_results']['results'])}")
