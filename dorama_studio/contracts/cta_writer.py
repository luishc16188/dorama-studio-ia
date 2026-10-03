"""
Data contracts for CTA Writer.
"""

from typing import Literal

from pydantic import BaseModel, Field


class CTAOutput(BaseModel):
    """CTA output model."""

    cta_type: Literal[
        "MORAL_DILEMMA", "REVENGE_CHOICE", "IDENTITY_TEASE", "TEAM_WAR"
    ] = Field(..., description="Type of call to action")
    cta_text: str = Field(..., description="The call to action text")
    urgency_level: int = Field(
        ge=1, le=10, description="Urgency level of the CTA (1-10)"
    )
    target_emotion: Literal["FEAR", "HOPE", "ANGER", "SADNESS", "JOY", "SURPRISE"] = (
        Field(..., description="Target emotion to evoke")
    )
