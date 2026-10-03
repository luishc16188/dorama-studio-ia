"""
Caching and Idempotency Layer - Evita llamadas LLM repetidas mediante cache keys deterministas.
"""

from __future__ import annotations

import hashlib
import json
import time
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from enum import Enum
from functools import wraps


class CacheLevel(str, Enum):
    """Niveles de cache."""
    L1_MEMORY = "l1_memory"       # En memoria (rápido, volátil)
    L2_DISK = "l2_disk"           # Disco local (persistente)
    L3_ARTIFACT = "l3_artifact"   # Artefactos en JobStore
    L4_PROVIDER = "l4_provider"   # Prompt cache del proveedor (ej. Anthropic prompt caching)


@dataclass
class CacheEntry:
    """Entrada de cache."""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Para invalidación
    dependencies: List[str] = field(default_factory=list)  # Claves de las que depende
    version: str = "1.0"

    def touch(self):
        self.accessed_at = time.time()
        self.access_count += 1

    def is_expired(self, ttl_seconds: float) -> bool:
        return (time.time() - self.created_at) > ttl_seconds


@dataclass
class CacheKey:
    """Clave de cache determinista."""
    stable_context_hash: str
    dynamic_context_hash: str
    task_hash: str
    prompt_version: str
    model: str
    provider: str
    agent: str
    operation: str

    def to_string(self) -> str:
        """Genera string de clave único."""
        parts = [
            self.stable_context_hash[:8],
            self.dynamic_context_hash[:8],
            self.task_hash[:8],
            self.prompt_version,
            self.model,
            self.provider,
            self.agent,
            self.operation,
        ]
        return "|".join(parts)

    @classmethod
    def from_components(
        cls,
        stable_context: Any,
        dynamic_context: Any,
        task: Any,
        prompt_version: str,
        model: str,
        provider: str,
        agent: str,
        operation: str,
    ) -> 'CacheKey':
        """Crea CacheKey desde componentes serializables."""
        def hash_obj(obj: Any) -> str:
            if obj is None:
                return "none"
            if isinstance(obj, (str, int, float, bool)):
                return hashlib.sha256(str(obj).encode()).hexdigest()[:16]
            try:
                content = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
            except TypeError:
                content = str(obj)
            return hashlib.sha256(content.encode()).hexdigest()[:16]

        return cls(
            stable_context_hash=hash_obj(stable_context),
            dynamic_context_hash=hash_obj(dynamic_context),
            task_hash=hash_obj(task),
            prompt_version=prompt_version,
            model=model,
            provider=provider,
            agent=agent,
            operation=operation,
        )


class CacheBackend:
    """Backend de cache abstracto."""

    def get(self, key: str) -> Optional[CacheEntry]:
        raise NotImplementedError

    def set(self, key: str, entry: CacheEntry) -> None:
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def get_stats(self) -> Dict[str, Any]:
        raise NotImplementedError


class MemoryCacheBackend(CacheBackend):
    """Cache en memoria (L1)."""

    def __init__(self, max_entries: int = 10000):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_entries = max_entries
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            entry = self._cache.get(key)
            if entry:
                entry.touch()
                self._hits += 1
                return entry
            self._misses += 1
            return None

    def set(self, key: str, entry: CacheEntry) -> None:
        with self._lock:
            # Eviction simple si excede máximo
            if len(self._cache) >= self._max_entries:
                # Eliminar el más antiguo (LRU aproximado)
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].accessed_at)
                del self._cache[oldest_key]
            self._cache[key] = entry

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            return {
                "level": CacheLevel.L1_MEMORY.value,
                "entries": len(self._cache),
                "max_entries": self._max_entries,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total * 100, 1) if total > 0 else 0,
            }


class DiskCacheBackend(CacheBackend):
    """Cache en disco (L2) - persistente entre sesiones."""

    def __init__(self, cache_dir: str = ".cache/llm", max_entries: int = 50000):
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self._cache_dir / "index.json"
        self._index: Dict[str, Dict[str, Any]] = {}
        self._max_entries = max_entries
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._load_index()

    def _load_index(self):
        if self._index_file.exists():
            try:
                with open(self._index_file, "r", encoding="utf-8") as f:
                    self._index = json.load(f)
            except Exception:
                self._index = {}

    def _save_index(self):
        try:
            with open(self._index_file, "w", encoding="utf-8") as f:
                json.dump(self._index, f, ensure_ascii=False)
        except Exception:
            pass

    def _entry_path(self, key: str) -> Path:
        # Hash de la clave para nombre de archivo seguro
        safe_key = hashlib.sha256(key.encode()).hexdigest()[:32]
        return self._cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            if key not in self._index:
                self._misses += 1
                return None

            meta = self._index[key]
            path = self._entry_path(key)

            if not path.exists():
                # Índice inconsistente
                del self._index[key]
                self._save_index()
                self._misses += 1
                return None

            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                entry = CacheEntry(
                    key=key,
                    value=data["value"],
                    created_at=data["created_at"],
                    accessed_at=data["accessed_at"],
                    access_count=data["access_count"],
                    metadata=data.get("metadata", {}),
                    dependencies=data.get("dependencies", []),
                    version=data.get("version", "1.0"),
                )
                entry.touch()
                # Actualizar metadatos en índice
                meta["accessed_at"] = entry.accessed_at
                meta["access_count"] = entry.access_count
                self._save_index()

                self._hits += 1
                return entry
            except Exception:
                self._misses += 1
                return None

    def set(self, key: str, entry: CacheEntry) -> None:
        with self._lock:
            path = self._entry_path(key)

            # Eviction si excede máximo
            if len(self._index) >= self._max_entries:
                # Eliminar el más antiguo
                oldest_key = min(self._index.keys(), key=lambda k: self._index[k]["accessed_at"])
                self.delete(oldest_key)

            try:
                data = {
                    "value": entry.value,
                    "created_at": entry.created_at,
                    "accessed_at": entry.accessed_at,
                    "access_count": entry.access_count,
                    "metadata": entry.metadata,
                    "dependencies": entry.dependencies,
                    "version": entry.version,
                }
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)

                self._index[key] = {
                    "created_at": entry.created_at,
                    "accessed_at": entry.accessed_at,
                    "access_count": entry.access_count,
                    "dependencies": entry.dependencies,
                    "version": entry.version,
                }
                self._save_index()
            except Exception:
                pass

    def delete(self, key: str) -> bool:
        with self._lock:
            path = self._entry_path(key)
            deleted = False
            if path.exists():
                try:
                    path.unlink()
                    deleted = True
                except Exception:
                    pass

            if key in self._index:
                del self._index[key]
                self._save_index()
                deleted = True

            return deleted

    def clear(self) -> None:
        with self._lock:
            for path in self._cache_dir.glob("*.json"):
                try:
                    path.unlink()
                except Exception:
                    pass
            self._index = {}
            self._save_index()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            return {
                "level": CacheLevel.L2_DISK.value,
                "entries": len(self._index),
                "max_entries": self._max_entries,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total * 100, 1) if total > 0 else 0,
                "cache_dir": str(self._cache_dir),
            }


class MultiLevelCache:
    """
    Cache multi-nivel (L1 -> L2 -> L3 -> L4).
    Busca en orden, promueve hits a niveles superiores.
    """

    def __init__(
        self,
        l1: Optional[MemoryCacheBackend] = None,
        l2: Optional[DiskCacheBackend] = None,
        # L3 y L4 serían backends especializados (JobStore, Provider cache)
    ):
        self.l1 = l1 or MemoryCacheBackend()
        self.l2 = l2 or DiskCacheBackend()
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[CacheEntry]:
        """Busca en L1, luego L2. Promueve hits de L2 a L1."""
        # L1
        entry = self.l1.get(key)
        if entry:
            return entry

        # L2
        entry = self.l2.get(key)
        if entry:
            # Promover a L1
            self.l1.set(key, entry)
            return entry

        return None

    def set(self, key: str, entry: CacheEntry, levels: List[CacheLevel] = None) -> None:
        """Guarda en niveles especificados (default: L1 + L2)."""
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_DISK]

        if CacheLevel.L1_MEMORY in levels:
            self.l1.set(key, entry)
        if CacheLevel.L2_DISK in levels:
            self.l2.set(key, entry)

    def delete(self, key: str) -> bool:
        """Elimina de todos los niveles."""
        deleted = False
        if self.l1.delete(key):
            deleted = True
        if self.l2.delete(key):
            deleted = True
        return deleted

    def invalidate_dependencies(self, dependency_key: str) -> int:
        """Invalida todas las entradas que dependen de una clave."""
        count = 0
        # Buscar en L1
        for key, entry in list(self.l1._cache.items()):
            if dependency_key in entry.dependencies:
                self.l1.delete(key)
                count += 1

        # Buscar en L2 (via índice)
        for key, meta in list(self.l2._index.items()):
            if dependency_key in meta.get("dependencies", []):
                self.l2.delete(key)
                count += 1

        return count

    def clear(self) -> None:
        self.l1.clear()
        self.l2.clear()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "l1": self.l1.get_stats(),
            "l2": self.l2.get_stats(),
        }


class IdempotencyManager:
    """
    Gestor de idempotencia para operaciones LLM.
    Evita re-ejecutar la misma operación si inputs no han cambiado.
    """

    def __init__(self, cache: MultiLevelCache = None):
        self.cache = cache or MultiLevelCache()
        self._lock = threading.Lock()

    def generate_key(
        self,
        agent: str,
        operation: str,
        stable_context: Any,
        dynamic_context: Any,
        task_input: Any,
        model: str,
        provider: str,
        prompt_version: str = "1.0",
    ) -> str:
        """Genera clave de idempotencia determinista."""
        cache_key = CacheKey.from_components(
            stable_context=stable_context,
            dynamic_context=dynamic_context,
            task=task_input,
            prompt_version=prompt_version,
            model=model,
            provider=provider,
            agent=agent,
            operation=operation,
        )
        return cache_key.to_string()

    def check_and_store(
        self,
        key: str,
        compute_fn: Callable[[], Any],
        ttl_seconds: float = 86400,  # 24 horas default
        dependencies: List[str] = None,
    ) -> Any:
        """
        Verifica cache; si miss, ejecuta compute_fn y almacena resultado.
        Retorna (value, cache_hit).
        """
        # Verificar cache
        entry = self.cache.get(key)
        if entry and not entry.is_expired(ttl_seconds):
            return entry.value, True

        # Cache miss - ejecutar
        value = compute_fn()

        # Almacenar
        new_entry = CacheEntry(
            key=key,
            value=value,
            dependencies=dependencies or [],
            metadata={"ttl_seconds": ttl_seconds},
        )
        self.cache.set(key, new_entry)

        return value, False

    def invalidate(self, key: str) -> bool:
        """Invalida una clave específica."""
        return self.cache.delete(key)

    def invalidate_by_dependency(self, dependency_key: str) -> int:
        """Invalida todas las entradas que dependen de una clave."""
        return self.cache.invalidate_dependencies(dependency_key)

    def get_stats(self) -> Dict[str, Any]:
        return self.cache.get_stats()


# Instancias globales
multi_level_cache = MultiLevelCache()
idempotency_manager = IdempotencyManager(multi_level_cache)


def cached_llm_call(
    agent: str,
    operation: str,
    model: str,
    provider: str,
    prompt_version: str = "1.0",
    ttl_seconds: float = 86400,
    dependencies: List[str] = None,
):
    """
    Decorador para cachear llamadas LLM automáticamente.

    Usage:
        @cached_llm_call("MasterWriter", "generate_script", "claude-opus-4-5", "freellmapi")
        def generate_script(stable_ctx, dynamic_ctx, task_input):
            return call_llm(...)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(stable_context, dynamic_context, task_input, *args, **kwargs):
            key = idempotency_manager.generate_key(
                agent=agent,
                operation=operation,
                stable_context=stable_context,
                dynamic_context=dynamic_context,
                task_input=task_input,
                model=model,
                provider=provider,
                prompt_version=prompt_version,
            )

            def compute():
                return func(stable_context, dynamic_context, task_input, *args, **kwargs)

            result, cache_hit = idempotency_manager.check_and_store(
                key=key,
                compute_fn=compute,
                ttl_seconds=ttl_seconds,
                dependencies=dependencies,
            )

            # Adjuntar info de cache al resultado si es dict
            if isinstance(result, dict):
                result["_cache_hit"] = cache_hit
                result["_cache_key"] = key[:32]

            return result
        return wrapper
    return decorator


def create_stable_context_hash(
    system_rules: str = "",
    architecture: str = "",
    style: str = "",
    contracts: str = "",
    instructions: str = "",
    prompt_version: str = "1.0",
) -> str:
    """Crea hash del contexto estable para cache keys."""
    content = f"{system_rules}|{architecture}|{style}|{contracts}|{instructions}|{prompt_version}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def create_dynamic_context_hash(
    season_arc: str = "",
    characters: List = None,
    relationships: Dict = None,
    world_rules: str = "",
    visual_identity: str = "",
    episode_objective: str = "",
    episode_beats: List = None,
    episode_characters: List = None,
    continuity: Dict = None,
) -> str:
    """Crea hash del contexto dinámico."""
    data = {
        "season_arc": season_arc,
        "characters": characters or [],
        "relationships": relationships or {},
        "world_rules": world_rules,
        "visual_identity": visual_identity,
        "episode_objective": episode_objective,
        "episode_beats": episode_beats or [],
        "episode_characters": episode_characters or [],
        "continuity": continuity or {},
    }
    content = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def create_task_hash(
    agent: str,
    operation: str,
    task_description: str,
    constraints: List[str] = None,
    output_schema: str = "",
) -> str:
    """Crea hash de la tarea específica."""
    data = {
        "agent": agent,
        "operation": operation,
        "task": task_description,
        "constraints": constraints or [],
        "schema": output_schema,
    }
    content = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(content.encode()).hexdigest()[:16]