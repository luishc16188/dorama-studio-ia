"""Quality Control module for DORAMA STUDIO IA V2.

Provides multimodal quality gates and a scoring function for episodes,
beats, and scripts.  Returns a ``quality_score`` in [0,1] and a list of
hard‑failure flags that trigger selective regeneration.
"""

from __future__ import annotations

from typing import Any

from dorama_studio.agents.contract import EpisodeSpecV2

# ---------------------------------------------------------------------------
# Thresholds (tunable)
# ---------------------------------------------------------------------------
MIN_DURATION_SEC = 30.0
MAX_DURATION_SEC = 120.0
MIN_BEATS = 3                       # episodio debe tener al menos 3 beats
QUALITY_PASS_THRESHOLD = 0.7        # por debajo -> regeneración selectiva


def _check_duration(spec: EpisodeSpecV2) -> tuple[bool, str]:
    """Validate that the episode duration is within the allowed range."""
    dur = spec.duration_seconds
    if MIN_DURATION_SEC <= dur <= MAX_DURATION_SEC:
        return True, "duration OK"
    return False, f"duration {dur}s fuera de rango [{MIN_DURATION_SEC}, {MAX_DURATION_SEC}]"


def _check_beats(spec: EpisodeSpecV2) -> tuple[bool, str]:
    """Validate that the episode has enough beats."""
    n = len(spec.beats or [])
    if n >= MIN_BEATS:
        return True, f"{n} beats (≥ {MIN_BEATS})"
    return False, f"solo {n} beat(s), se necesitan al menos {MIN_BEATS}"


def _check_title_nonempty(spec: EpisodeSpecV2) -> tuple[bool, str]:
    if spec.title and spec.title.strip():
        return True, "title OK"
    return False, "title vacío o nulo"


def evaluate_spec(spec: EpisodeSpecV2) -> dict[str, Any]:
    """Ejecutar todas las gates y devolver score + flags."""
    gates: list[tuple[bool, str]] = [
        _check_duration(spec),
        _check_beats(spec),
        _check_title_nonempty(spec),
    ]

    # Score simple: 1.0 menos 0.15 por cada fallo (máx 3 gates -> resta m áx 0.45)
    failures = sum(1 for ok, _ in gates if not ok)
    score = max(0.0, 1.0 - 0.15 * failures)

    hard_failures: list[str] = [msg for ok, msg in gates if not ok]

    return {
        "quality_score": round(score, 3),
        "passed": score >= QUALITY_PASS_THRESHOLD,
        "hard_failures": hard_failures,
        "gate_details": [{"ok": ok, "message": msg} for ok, msg in gates],
    }


# ---------------------------------------------------------------------------
# Función de conveniencia para evaluar beats y duración sin necesidad de
# un Episodio completo (útil en iteraciones rápidas).
# ---------------------------------------------------------------------------
def evaluate_beats(beats: list[dict[str, Any]], duration_sec: float) -> dict[str, Any]:
    """Evaluación rápida sobre una lista de beats y duración.

    Crea un EpisodeSpecV2 ficticio en interno y reutiliza ``evaluate_spec``.
    """
    # Import local para evitar circularidades al cargar el módulo
    from dorama_studio.agents.contract import EpisodeSpecV2 as ES  # type: ignore
    spec = ES(
        episode_id="temp",
        title="temp",
        beats=beats,
        duration_seconds=duration_sec,
        season=1,
        episode_number=1,
    )
    return evaluate_spec(spec)
