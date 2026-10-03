"""
Audience Evidence Agent –
Analiza señales de audiencia para convertir en requisitos creativos medibles.
"""

from __future__ import annotations

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext


class AudienceEvidenceAgent(BaseAgent):
    """Agent that analyzes audience signals to derive creative requirements."""

    def __init__(self):
        super().__init__("AudienceEvidenceAgent")

    def _process(self, ctx: PipelineContext) -> AgentResult:
        """Process the context to analyze audience evidence."""
        # In a real implementation, this would analyze comments, retention, demographic data
        # For now, we'll simulate audience evidence analysis

        # Simulate extracting audience insights from platform data
        audience_insights = {
            "audience_tensions": [
                "Desire for faster plot progression",
                "Need for clearer character motivations",
                "Request for more diverse representation"
            ],
            "desires": [
                "More plot twists per episode",
                "Stronger female leads",
                "Authentic cultural representation"
            ],
            "confusion_points": [
                "Complex relationship mappings",
                "Historical context references",
                "Technical jargon without explanation"
            ],
            "engagement_patterns": {
                "peak_engagement_moments": ["0-3s hook", "20-30s twist", "60-70s revelation", "85-90s cliffhanger"],
                "drop_off_points": ["45-55s exposition heavy scenes"],
                "rewatch_triggers": ["unanswered questions", "emotional payoff moments"]
            }
        }

        # Update state with audience evidence
        if hasattr(ctx, 'state') and ctx.state:
            state_dict = ctx.state.dict() if hasattr(ctx.state, 'dict') else dict(ctx.state) if hasattr(ctx.state, '__dict__') else {}
            state_dict['audience_evidence'] = audience_insights

            # Try to update the state object if it supports it
            if hasattr(ctx.state, '__dict__'):
                for key, value in state_dict.items():
                    setattr(ctx.state, key, value)
            elif hasattr(ctx.state, '__setitem__'):
                for key, value in state_dict.items():
                    ctx.state[key] = value

        return AgentResult(
            success=True,
            agent_name=self.name,
            output_data={
                "audience_evidence_analyzed": True,
                "insights_categories": list(audience_insights.keys())
            },
            context_updates={
                "audience_evidence": audience_insights
            },
            logs=[{
                "step": "AudienceEvidence",
                "insights_generated": len(audience_insights["audience_tensions"]) +
                                    len(audience_insights["desires"]) +
                                    len(audience_insights["confusion_points"])
            }],
        )
