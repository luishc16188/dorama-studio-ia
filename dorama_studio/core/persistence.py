"""
Persistence Layer - SQLite-backed storage for Dorama Studio.
Provides SSOT for character bibles, episode outlines, approved prompts, and generation logs.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path("dorama_studio_data/studio.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    genre TEXT,
    concept_seed TEXT,
    total_episodes INTEGER,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    role TEXT,
    archetype TEXT,
    want TEXT,
    need TEXT,
    lie TEXT,
    ghost TEXT,
    secret TEXT,
    physical_json TEXT,
    micro_expressions_json TEXT,
    voice_profile_json TEXT,
    wardrobe_json TEXT,
    continuity_rules_json TEXT,
    seed INTEGER,
    p0 TEXT,
    p1 TEXT,
    p2 TEXT,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_num INTEGER NOT NULL,
    hook_category TEXT,
    core_conflict TEXT,
    twist TEXT,
    cliffhanger TEXT,
    cta_type TEXT,
    blueprint_json TEXT,
    status TEXT DEFAULT 'planned',
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    UNIQUE(project_id, episode_num)
);

CREATE TABLE IF NOT EXISTS beats (
    id TEXT PRIMARY KEY,
    episode_id TEXT NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    beat_index INTEGER NOT NULL,
    beat_name TEXT NOT NULL,
    action TEXT,
    dialogue TEXT,
    emotion TEXT,
    tension INTEGER,
    pacing TEXT,
    duration REAL,
    camera_json TEXT,
    sound_json TEXT,
    visual_prompt TEXT,
    negative_prompt TEXT,
    continuity_json TEXT,
    character_ids_json TEXT,
    seed INTEGER,
    fractal_stage TEXT,
    pattern_interrupt TEXT,
    curiosity_loop_planted TEXT,
    information_asymmetry TEXT,
    subversion_applied TEXT,
    status TEXT DEFAULT 'draft',
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    UNIQUE(episode_id, beat_index)
);

CREATE TABLE IF NOT EXISTS generation_logs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id TEXT REFERENCES episodes(id) ON DELETE SET NULL,
    beat_id TEXT REFERENCES beats(id) ON DELETE SET NULL,
    agent_name TEXT NOT NULL,
    input_json TEXT,
    output_json TEXT,
    model_used TEXT,
    latency_ms INTEGER,
    tokens_used INTEGER,
    status TEXT,
    error_message TEXT,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS continuity_snapshots (
    id TEXT PRIMARY KEY,
    episode_id TEXT NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    beat_index INTEGER NOT NULL,
    illumination_json TEXT,
    subject_state_json TEXT,
    space_json TEXT,
    key_objects_json TEXT,
    hash TEXT NOT NULL,
    created_at REAL NOT NULL,
    UNIQUE(episode_id, beat_index)
);

CREATE TABLE IF NOT EXISTS quality_gates (
    id TEXT PRIMARY KEY,
    episode_id TEXT NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    beat_id TEXT REFERENCES beats(id) ON DELETE SET NULL,
    dimension TEXT NOT NULL,
    score REAL,
    passed INTEGER,
    feedback TEXT,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS creative_genome (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_num INTEGER,
    character_id TEXT,
    mutation_type TEXT,
    mutation_value TEXT,
    budget_used REAL,
    created_at REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_characters_project ON characters(project_id);
CREATE INDEX IF NOT EXISTS idx_episodes_project ON episodes(project_id);
CREATE INDEX IF NOT EXISTS idx_beats_episode ON beats(episode_id);
CREATE INDEX IF NOT EXISTS idx_logs_project ON generation_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_continuity_episode ON continuity_snapshots(episode_id);
CREATE INDEX IF NOT EXISTS idx_quality_episode ON quality_gates(episode_id);
CREATE INDEX IF NOT EXISTS idx_genome_project ON creative_genome(project_id);
"""


class PersistenceManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript(_SCHEMA)
            conn.commit()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _now(self) -> float:
        return time.time()

    def _gen_id(self, prefix: str = "") -> str:
        return f"{prefix}{hashlib.md5(f'{time.time()}{threading.get_ident()}'.encode()).hexdigest()[:12]}"

    # ==================== PROJECTS ====================
    def create_project(
        self,
        name: str,
        genre: str,
        concept_seed: str,
        total_episodes: int,
        metadata: dict = None,
    ) -> str:
        pid = self._gen_id("proj_")
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO projects (id, name, genre, concept_seed, total_episodes, created_at, updated_at, metadata_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    pid,
                    name,
                    genre,
                    concept_seed,
                    total_episodes,
                    now,
                    now,
                    json.dumps(metadata or {}),
                ),
            )
            conn.commit()
        return pid

    def get_project(self, project_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            return dict(row) if row else None

    def update_project(self, project_id: str, **fields):
        if not fields:
            return
        fields["updated_at"] = self._now()
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        with self._connect() as conn:
            conn.execute(
                f"UPDATE projects SET {set_clause} WHERE id = ?",
                (*fields.values(), project_id),
            )
            conn.commit()

    # ==================== CHARACTERS ====================
    def save_character(self, project_id: str, character: dict) -> str:
        cid = character.get("id") or self._gen_id("char_")
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO characters
                   (id, project_id, name, role, archetype, want, need, lie, ghost, secret,
                    physical_json, micro_expressions_json, voice_profile_json, wardrobe_json,
                    continuity_rules_json, seed, p0, p1, p2, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    cid,
                    project_id,
                    character.get("name"),
                    character.get("role"),
                    character.get("archetype"),
                    character.get("want"),
                    character.get("need"),
                    character.get("lie"),
                    character.get("ghost"),
                    character.get("secret"),
                    json.dumps(character.get("physical")),
                    json.dumps(character.get("micro_expressions")),
                    json.dumps(character.get("voice_profile")),
                    json.dumps(character.get("wardrobe")),
                    json.dumps(character.get("continuity_rules")),
                    character.get("seed"),
                    character.get("p0"),
                    character.get("p1"),
                    character.get("p2"),
                    now,
                    now,
                ),
            )
            conn.commit()
        return cid

    def get_character(self, character_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM characters WHERE id = ?", (character_id,)
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            for field in [
                "physical_json",
                "micro_expressions_json",
                "voice_profile_json",
                "wardrobe_json",
                "continuity_rules_json",
            ]:
                if d[field]:
                    d[field.replace("_json", "")] = json.loads(d[field])
            return d

    def get_characters_by_project(self, project_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM characters WHERE project_id = ?", (project_id,)
            ).fetchall()
            result = []
            for row in rows:
                d = dict(row)
                for field in [
                    "physical_json",
                    "micro_expressions_json",
                    "voice_profile_json",
                    "wardrobe_json",
                    "continuity_rules_json",
                ]:
                    if d[field]:
                        d[field.replace("_json", "")] = json.loads(d[field])
                result.append(d)
            return result

    # ==================== EPISODES ====================
    def save_episode(self, project_id: str, episode_num: int, blueprint: dict) -> str:
        eid = self._gen_id(f"ep{episode_num}_")
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO episodes
                   (id, project_id, episode_num, hook_category, core_conflict, twist, cliffhanger,
                    cta_type, blueprint_json, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'planned', ?, ?)""",
                (
                    eid,
                    project_id,
                    episode_num,
                    blueprint.get("hook_category"),
                    blueprint.get("core_conflict"),
                    blueprint.get("twist"),
                    blueprint.get("cliffhanger"),
                    blueprint.get("cta_type"),
                    json.dumps(blueprint),
                    now,
                    now,
                ),
            )
            conn.commit()
        return eid

    def get_episode(self, episode_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM episodes WHERE id = ?", (episode_id,)
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            if d["blueprint_json"]:
                d["blueprint"] = json.loads(d["blueprint_json"])
            return d

    def get_episode_by_num(self, project_id: str, episode_num: int) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM episodes WHERE project_id = ? AND episode_num = ?",
                (project_id, episode_num),
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            if d["blueprint_json"]:
                d["blueprint"] = json.loads(d["blueprint_json"])
            return d

    def list_episodes(self, project_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM episodes WHERE project_id = ? ORDER BY episode_num",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def update_episode_status(self, episode_id: str, status: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE episodes SET status = ?, updated_at = ? WHERE id = ?",
                (status, self._now(), episode_id),
            )
            conn.commit()

    # ==================== BEATS ====================
    def save_beat(self, episode_id: str, beat: dict) -> str:
        bid = self._gen_id(f"beat{beat.get('beat_index',0)}_")
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO beats
                   (id, episode_id, beat_index, beat_name, action, dialogue, emotion, tension,
                    pacing, duration, camera_json, sound_json, visual_prompt, negative_prompt,
                    continuity_json, character_ids_json, seed, fractal_stage, pattern_interrupt,
                    curiosity_loop_planted, information_asymmetry, subversion_applied,
                    status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)""",
                (
                    bid,
                    episode_id,
                    beat.get("beat_index"),
                    beat.get("beat_name"),
                    beat.get("action"),
                    beat.get("dialogue"),
                    beat.get("emotion"),
                    beat.get("tension"),
                    beat.get("pacing"),
                    beat.get("duration"),
                    json.dumps(beat.get("camera")),
                    json.dumps(beat.get("sound")),
                    beat.get("visual_prompt"),
                    beat.get("negative_prompt"),
                    json.dumps(beat.get("continuity_block")),
                    json.dumps(beat.get("character_ids")),
                    beat.get("seed"),
                    beat.get("fractal_stage"),
                    beat.get("pattern_interrupt"),
                    beat.get("curiosity_loop_planted"),
                    beat.get("information_asymmetry"),
                    beat.get("subversion_applied"),
                    now,
                    now,
                ),
            )
            conn.commit()
        return bid

    def get_beats(self, episode_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM beats WHERE episode_id = ? ORDER BY beat_index",
                (episode_id,),
            ).fetchall()
            result = []
            for row in rows:
                d = dict(row)
                for field in [
                    "camera_json",
                    "sound_json",
                    "continuity_json",
                    "character_ids_json",
                ]:
                    if d[field]:
                        d[field.replace("_json", "")] = json.loads(d[field])
                result.append(d)
            return result

    def update_beat_status(self, beat_id: str, status: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE beats SET status = ?, updated_at = ? WHERE id = ?",
                (status, self._now(), beat_id),
            )
            conn.commit()

    # ==================== GENERATION LOGS ====================
    def log_generation(
        self,
        project_id: str,
        agent_name: str,
        input_data: dict,
        output_data: dict,
        model_used: str = "",
        latency_ms: int = 0,
        tokens_used: int = 0,
        status: str = "success",
        error_message: str = "",
        episode_id: str = None,
        beat_id: str = None,
    ) -> str:
        lid = self._gen_id("log_")
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO generation_logs
                   (id, project_id, episode_id, beat_id, agent_name, input_json, output_json,
                    model_used, latency_ms, tokens_used, status, error_message, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    lid,
                    project_id,
                    episode_id,
                    beat_id,
                    agent_name,
                    json.dumps(input_data, ensure_ascii=False),
                    json.dumps(output_data, ensure_ascii=False),
                    model_used,
                    latency_ms,
                    tokens_used,
                    status,
                    error_message,
                    self._now(),
                ),
            )
            conn.commit()
        return lid

    # ==================== CONTINUITY SNAPSHOTS ====================
    def save_continuity_snapshot(
        self,
        episode_id: str,
        beat_index: int,
        illumination: dict,
        subject_state: dict,
        space: dict,
        key_objects: dict,
    ) -> str:
        # Compute hash for integrity
        combined = json.dumps(
            {
                "illumination": illumination,
                "subject_state": subject_state,
                "space": space,
                "key_objects": key_objects,
            },
            sort_keys=True,
        )
        snap_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]

        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO continuity_snapshots
                   (id, episode_id, beat_index, illumination_json, subject_state_json,
                    space_json, key_objects_json, hash, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    self._gen_id("cont_"),
                    episode_id,
                    beat_index,
                    json.dumps(illumination),
                    json.dumps(subject_state),
                    json.dumps(space),
                    json.dumps(key_objects),
                    snap_hash,
                    self._now(),
                ),
            )
            conn.commit()
        return snap_hash

    def get_continuity_snapshot(self, episode_id: str, beat_index: int) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM continuity_snapshots WHERE episode_id = ? AND beat_index = ?",
                (episode_id, beat_index),
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            for field in [
                "illumination_json",
                "subject_state_json",
                "space_json",
                "key_objects_json",
            ]:
                if d[field]:
                    d[field.replace("_json", "")] = json.loads(d[field])
            return d

    def get_previous_continuity(self, episode_id: str, beat_index: int) -> dict | None:
        """Get continuity from previous beat for HEREDA"""
        if beat_index <= 0:
            return None
        return self.get_continuity_snapshot(episode_id, beat_index - 1)

    # ==================== QUALITY GATES ====================
    def save_quality_gate(
        self,
        episode_id: str,
        dimension: str,
        score: float,
        passed: bool,
        feedback: str = "",
        beat_id: str = None,
    ):
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO quality_gates (id, episode_id, beat_id, dimension, score, passed, feedback, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    self._gen_id("qg_"),
                    episode_id,
                    beat_id,
                    dimension,
                    score,
                    int(passed),
                    feedback,
                    self._now(),
                ),
            )
            conn.commit()

    def get_quality_gates(self, episode_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM quality_gates WHERE episode_id = ?", (episode_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    # ==================== CREATIVE GENOME ====================
    def log_mutation(
        self,
        project_id: str,
        mutation_type: str,
        mutation_value: str,
        budget_used: float,
        episode_num: int = None,
        character_id: str = None,
    ):
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO creative_genome
                   (id, project_id, episode_num, character_id, mutation_type, mutation_value, budget_used, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    self._gen_id("mut_"),
                    project_id,
                    episode_num,
                    character_id,
                    mutation_type,
                    mutation_value,
                    budget_used,
                    self._now(),
                ),
            )
            conn.commit()

    def get_genome_budget(self, project_id: str) -> float:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT SUM(budget_used) FROM creative_genome WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            return row[0] if row and row[0] else 0.0


# Singleton instance
persistence = PersistenceManager()


# Convenience functions
def get_persistence() -> PersistenceManager:
    return persistence


def get_all_projects() -> list:
    """Retorna todos los proyectos de la base de datos."""
    with persistence._connect() as conn:
        rows = conn.execute(
            "SELECT id, name, genre, total_episodes, created_at FROM projects ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
