"""
Analytics Database – SQLite schema y helpers para métricas de episodios.
Tabla: episode_metrics
  - episode_id (PK)
  - season_id
  - project_id
  - episode_number
  - quality_score
  - quality_state
  - media_duration_sec
  - render_time_sec
  - qc_passed (bool)
  - regeneration_count
  - fetched_at (timestamp)
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = Path("dorama_studio_data/analytics.db")


def init_db():
    """Crea la tabla si no existe."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS episode_metrics (
                episode_id TEXT PRIMARY KEY,
                season_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                episode_number INTEGER NOT NULL,
                quality_score REAL,
                quality_state TEXT,
                media_duration_sec REAL,
                render_time_sec REAL,
                qc_passed BOOLEAN,
                regeneration_count INTEGER DEFAULT 0,
                fetched_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_season_episode
            ON episode_metrics(season_id, episode_number)
        """)


@contextmanager
def get_conn():
    """Context manager para conexión SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_episode_metric(
    episode_id: str,
    season_id: str,
    project_id: str,
    episode_number: int,
    quality_score: Optional[float] = None,
    quality_state: Optional[str] = None,
    media_duration_sec: Optional[float] = None,
    render_time_sec: Optional[float] = None,
    qc_passed: Optional[bool] = None,
    regeneration_count: int = 0,
) -> None:
    """Inserta o actualiza métricas de un episodio."""
    init_db()
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO episode_metrics (
                episode_id, season_id, project_id, episode_number,
                quality_score, quality_state, media_duration_sec,
                render_time_sec, qc_passed, regeneration_count, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(episode_id) DO UPDATE SET
                quality_score = excluded.quality_score,
                quality_state = excluded.quality_state,
                media_duration_sec = excluded.media_duration_sec,
                render_time_sec = excluded.render_time_sec,
                qc_passed = excluded.qc_passed,
                regeneration_count = excluded.regeneration_count,
                fetched_at = excluded.fetched_at
        """, (
            episode_id, season_id, project_id, episode_number,
            quality_score, quality_state, media_duration_sec,
            render_time_sec, qc_passed, regeneration_count,
            datetime.utcnow().isoformat() + "Z"
        ))


def get_season_metrics(season_id: str) -> List[Dict[str, Any]]:
    """Obtiene todas las métricas de una temporada."""
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM episode_metrics WHERE season_id = ? ORDER BY episode_number",
            (season_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_project_summary(project_id: str) -> Dict[str, Any]:
    """Resumen agregado del proyecto."""
    init_db()
    with get_conn() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) as total_episodes,
                AVG(quality_score) as avg_quality,
                SUM(CASE WHEN qc_passed = 1 THEN 1 ELSE 0 END) as passed_count,
                SUM(regeneration_count) as total_regenerations,
                AVG(render_time_sec) as avg_render_time
            FROM episode_metrics
            WHERE project_id = ?
        """, (project_id,)).fetchone()
        return dict(row) if row else {}


def get_latest_metrics(limit: int = 10) -> List[Dict[str, Any]]:
    """Últimos episodios registrados."""
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM episode_metrics ORDER BY fetched_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# Auto-inicializar al importar
init_db()