#!/usr/bin/env python
"""
Agent Contract - Defines the input/output contract for agents.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class AgentContract(BaseModel):
    """
    Contract that wraps the payload for agent processing.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    payload: Any
    metadata: dict[str, Any] | None = None
    # Optional fields for tracking, versioning, etc.
    version: str = "1.0"
    agent_id: str | None = None
