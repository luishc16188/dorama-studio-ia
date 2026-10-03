"""
Checkpoint persistence for DORAMA STUDIO orchestration.
Supports InMemory, PostgreSQL, and Redis backends.
"""

import json
from collections.abc import AsyncIterator
from typing import Any

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langgraph.checkpoint.memory import InMemorySaver

# ============================================================
# Checkpointer Factory
# ============================================================

def get_checkpointer(
    backend: str = "memory",
    **kwargs
) -> BaseCheckpointSaver:
    """
    Factory function to get a checkpointer instance.

    Args:
        backend: "memory" | "postgres" | "redis"
        **kwargs: Backend-specific configuration

    Returns:
        BaseCheckpointSaver instance
    """
    if backend == "memory":
        return InMemorySaver()
    elif backend == "postgres":
        return PostgresCheckpointer(**kwargs)
    elif backend == "redis":
        return RedisCheckpointer(**kwargs)
    else:
        raise ValueError(f"Unknown checkpointer backend: {backend}")


# ============================================================
# PostgreSQL Checkpointer
# ============================================================

class PostgresCheckpointer(BaseCheckpointSaver):
    """
    PostgreSQL-based checkpoint saver using asyncpg.
    Requires: pip install psycopg2-binary asyncpg
    """

    def __init__(
        self,
        dsn: str | None = None,
        host: str = "localhost",
        port: int = 5432,
        database: str = "dorama_studio",
        user: str = "postgres",
        password: str = "postgres",
        pool_size: int = 10,
    ):
        """
        Initialize PostgreSQL checkpointer.

        Args:
            dsn: Full PostgreSQL DSN (overrides individual params)
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            pool_size: Connection pool size
        """
        self.dsn = dsn or f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.pool_size = pool_size
        self._pool = None
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        import psycopg2
        conn = psycopg2.connect(self.dsn)
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS checkpoints (
                        thread_id TEXT NOT NULL,
                        checkpoint_ns TEXT NOT NULL DEFAULT '',
                        checkpoint_id TEXT NOT NULL,
                        parent_checkpoint_id TEXT,
                        checkpoint JSONB NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{}',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_ns
                    ON checkpoints (thread_id, checkpoint_ns);

                    CREATE INDEX IF NOT EXISTS idx_checkpoints_created
                    ON checkpoints (created_at DESC);
                """)
                conn.commit()
        finally:
            conn.close()

    def _get_pool(self):
        """Get or create async connection pool."""
        if self._pool is None:
            import asyncpg
            self._pool = asyncpg.create_pool(
                self.dsn,
                min_size=1,
                max_size=self.pool_size,
            )
        return self._pool

    async def aput(
        self,
        config: dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> None:
        """Store a checkpoint asynchronously."""
        pool = self._get_pool()
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = checkpoint.get("parent_config", {}).get("configurable", {}).get("checkpoint_id")

        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, checkpoint, metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (thread_id, checkpoint_ns, checkpoint_id) DO UPDATE SET
                    checkpoint = EXCLUDED.checkpoint,
                    metadata = EXCLUDED.metadata,
                    parent_checkpoint_id = EXCLUDED.parent_checkpoint_id
            """, thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id,
                json.dumps(checkpoint), json.dumps(metadata))

    async def aget_tuple(self, config: dict[str, Any]) -> CheckpointTuple | None:
        """Get a checkpoint tuple asynchronously."""
        pool = self._get_pool()
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"].get("checkpoint_id")

        async with pool.acquire() as conn:
            if checkpoint_id:
                row = await conn.fetchrow("""
                    SELECT checkpoint, metadata, parent_checkpoint_id
                    FROM checkpoints
                    WHERE thread_id = $1 AND checkpoint_ns = $2 AND checkpoint_id = $3
                """, thread_id, checkpoint_ns, checkpoint_id)
            else:
                row = await conn.fetchrow("""
                    SELECT checkpoint, metadata, parent_checkpoint_id
                    FROM checkpoints
                    WHERE thread_id = $1 AND checkpoint_ns = $2
                    ORDER BY created_at DESC
                    LIMIT 1
                """, thread_id, checkpoint_ns)

            if not row:
                return None

            checkpoint = json.loads(row["checkpoint"])
            metadata = json.loads(row["metadata"])
            parent_checkpoint_id = row["parent_checkpoint_id"]

            parent_config = None
            if parent_checkpoint_id:
                parent_config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": parent_checkpoint_id,
                    }
                }

            return CheckpointTuple(
                config=config,
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=parent_config,
            )

    async def alist(
        self,
        config: dict[str, Any] | None = None,
        *,
        filter: dict[str, Any] | None = None,
        before: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """List checkpoints asynchronously."""
        pool = self._get_pool()

        # Build query
        where_clauses = []
        params = []
        param_idx = 1

        if config:
            thread_id = config["configurable"]["thread_id"]
            checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
            where_clauses.append(f"thread_id = ${param_idx}")
            params.append(thread_id)
            param_idx += 1
            where_clauses.append(f"checkpoint_ns = ${param_idx}")
            params.append(checkpoint_ns)
            param_idx += 1

        if before and "checkpoint_id" in before:
            where_clauses.append(f"created_at < (SELECT created_at FROM checkpoints WHERE thread_id = ${1} AND checkpoint_ns = ${2} AND checkpoint_id = ${param_idx})")
            params.append(before["checkpoint_id"])
            param_idx += 1

        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        limit_sql = f" LIMIT {limit}" if limit else ""

        query = f"""
            SELECT thread_id, checkpoint_ns, checkpoint_id, checkpoint, metadata, parent_checkpoint_id
            FROM checkpoints
            {where_sql}
            ORDER BY created_at DESC
            {limit_sql}
        """

        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

            for row in rows:
                checkpoint = json.loads(row["checkpoint"])
                metadata = json.loads(row["metadata"])
                parent_checkpoint_id = row["parent_checkpoint_id"]

                parent_config = None
                if parent_checkpoint_id:
                    parent_config = {
                        "configurable": {
                            "thread_id": row["thread_id"],
                            "checkpoint_ns": row["checkpoint_ns"],
                            "checkpoint_id": parent_checkpoint_id,
                        }
                    }

                yield CheckpointTuple(
                    config={
                        "configurable": {
                            "thread_id": row["thread_id"],
                            "checkpoint_ns": row["checkpoint_ns"],
                            "checkpoint_id": row["checkpoint_id"],
                        }
                    },
                    checkpoint=checkpoint,
                    metadata=metadata,
                    parent_config=parent_config,
                )

    def put(
        self,
        config: dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> None:
        """Sync version - delegates to async."""
        import asyncio
        asyncio.run(self.aput(config, checkpoint, metadata, new_versions))

    def get_tuple(self, config: dict[str, Any]) -> CheckpointTuple | None:
        import asyncio
        return asyncio.run(self.aget_tuple(config))

    def list(
        self,
        config: dict[str, Any] | None = None,
        *,
        filter: dict[str, Any] | None = None,
        before: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> list[CheckpointTuple]:
        import asyncio

        async def _collect():
            results = []
            async for item in self.alist(config, filter=filter, before=before, limit=limit):
                results.append(item)
            return results

        return asyncio.run(_collect())


# ============================================================
# Redis Checkpointer
# ============================================================

class RedisCheckpointer(BaseCheckpointSaver):
    """
    Redis-based checkpoint saver.
    Requires: pip install redis
    """

    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        key_prefix: str = "dorama:checkpoint:",
        ttl: int = 86400 * 7,  # 7 days default
    ):
        """
        Initialize Redis checkpointer.

        Args:
            url: Redis connection URL
            key_prefix: Prefix for all checkpoint keys
            ttl: Time-to-live in seconds (default 7 days)
        """
        self.url = url
        self.key_prefix = key_prefix
        self.ttl = ttl
        self._redis = None
        self._init_client()

    def _init_client(self):
        """Initialize Redis client."""
        import redis
        self._redis = redis.from_url(self.url, decode_responses=True)

    def _make_key(self, thread_id: str, checkpoint_ns: str, checkpoint_id: str) -> str:
        """Create Redis key."""
        return f"{self.key_prefix}{thread_id}:{checkpoint_ns}:{checkpoint_id}"

    def _make_thread_key(self, thread_id: str, checkpoint_ns: str) -> str:
        """Create thread index key."""
        return f"{self.key_prefix}thread:{thread_id}:{checkpoint_ns}"

    def put(
        self,
        config: dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> None:
        """Store a checkpoint."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = checkpoint.get("parent_config", {}).get("configurable", {}).get("checkpoint_id")

        key = self._make_key(thread_id, checkpoint_ns, checkpoint_id)
        thread_key = self._make_thread_key(thread_id, checkpoint_ns)

        data = {
            "checkpoint": checkpoint,
            "metadata": metadata,
            "parent_checkpoint_id": parent_checkpoint_id,
        }

        pipe = self._redis.pipeline()
        pipe.set(key, json.dumps(data), ex=self.ttl)
        pipe.zadd(thread_key, {checkpoint_id: checkpoint["ts"]})
        pipe.expire(thread_key, self.ttl)
        pipe.execute()

    def get_tuple(self, config: dict[str, Any]) -> CheckpointTuple | None:
        """Get a checkpoint tuple."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"].get("checkpoint_id")

        if checkpoint_id:
            key = self._make_key(thread_id, checkpoint_ns, checkpoint_id)
            data = self._redis.get(key)
        else:
            # Get latest
            thread_key = self._make_thread_key(thread_id, checkpoint_ns)
            checkpoint_id = self._redis.zrevrange(thread_key, 0, 0)
            if not checkpoint_id:
                return None
            checkpoint_id = checkpoint_id[0]
            key = self._make_key(thread_id, checkpoint_ns, checkpoint_id)
            data = self._redis.get(key)

        if not data:
            return None

        data = json.loads(data)
        checkpoint = data["checkpoint"]
        metadata = data["metadata"]
        parent_checkpoint_id = data["parent_checkpoint_id"]

        parent_config = None
        if parent_checkpoint_id:
            parent_config = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": parent_checkpoint_id,
                }
            }

        return CheckpointTuple(
            config=config,
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=parent_config,
        )

    def list(
        self,
        config: dict[str, Any] | None = None,
        *,
        filter: dict[str, Any] | None = None,
        before: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> list[CheckpointTuple]:
        """List checkpoints."""
        if not config:
            return []

        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        thread_key = self._make_thread_key(thread_id, checkpoint_ns)

        # Get checkpoint IDs in reverse chronological order
        checkpoint_ids = self._redis.zrevrange(thread_key, 0, limit - 1 if limit else -1)

        results = []
        for cid in checkpoint_ids:
            if before and "checkpoint_id" in before:
                # Check if this checkpoint is before the specified one
                checkpoint_ts = self._redis.zscore(thread_key, cid)
                before_ts = self._redis.zscore(thread_key, before["checkpoint_id"])
                if checkpoint_ts is not None and before_ts is not None:
                    if checkpoint_ts >= before_ts:
                        continue

            key = self._make_key(thread_id, checkpoint_ns, cid)
            data = self._redis.get(key)
            if not data:
                continue

            data = json.loads(data)
            checkpoint = data["checkpoint"]
            metadata = data["metadata"]
            parent_checkpoint_id = data["parent_checkpoint_id"]

            parent_config = None
            if parent_checkpoint_id:
                parent_config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": parent_checkpoint_id,
                    }
                }

            results.append(CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": cid,
                    }
                },
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=parent_config,
            ))

        return results
