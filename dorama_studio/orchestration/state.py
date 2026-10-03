# Re-export core state models for orchestration import convenience
from dorama_studio.core.state import DoramaState, EpisodeProductionState, SeasonProductionState, GraphState


def qc_condition(state):
    """
    Conditional edge function for quality check.
    Returns "pass" if no critical failures, otherwise "fail".
    """
    # state.active_quality_issues is a list of critical failure descriptions
    if hasattr(state, 'active_quality_issues') and state.active_quality_issues:
        return "fail"
    else:
        return "pass"
