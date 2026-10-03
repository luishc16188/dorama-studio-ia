"""
Token Usage Tracking - Instrumentación para medir uso de tokens, llamadas LLM y contexto.
Proporciona métricas aproximadas cuando el proveedor no expone tokenización exacta.
"""

from __future__ import annotations

import time
import threading
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Dict, List
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from enum import Enum


class TokenEstimationMethod(str, Enum):
    """Método de estimación de tokens."""
    EXACT = "exact"           # Proveedor devolvió cuenta exacta
    TIKTOKEN = "tiktoken"     # Estimado con tiktoken
    CHAR_BASED = "char_based"  # Estimación basada en caracteres (1 token ≈ 4 chars)
    WORD_BASED = "word_based"  # Estimación basada en palabras (1 token ≈ 0.75 palabras)


@dataclass
class TokenUsage:
    """
    Registro de uso de tokens para una operación LLM.
    """
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated: bool
    estimation_method: TokenEstimationMethod
    model: str
    provider: str
    agent: str
    operation: str
    cache_hit: bool = False
    latency_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    context_size_chars: int = 0
    prompt_size_chars: int = 0
    output_size_chars: int = 0

    # Metadata para agregación
    episode_id: Optional[str] = None
    season_id: Optional[str] = None
    project_id: Optional[str] = None
    scene_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def estimation_label(self) -> str:
        return f"{self.estimation_method.value}{' (estimated)' if self.estimated else ''}"


@dataclass
class TokenUsageReport:
    """
    Reporte agregado de uso de tokens.
    """
    period_start: str
    period_end: str
    total_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_latency_ms: int = 0
    by_agent: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_operation: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_model: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_episode: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_scene: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    estimated_calls: int = 0
    exact_calls: int = 0

    def add_usage(self, usage: TokenUsage):
        """Agrega un registro de uso al reporte."""
        self.total_calls += 1
        self.total_input_tokens += usage.input_tokens
        self.total_output_tokens += usage.output_tokens
        self.total_tokens += usage.total_tokens
        self.total_latency_ms += usage.latency_ms

        if usage.cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        if usage.estimated:
            self.estimated_calls += 1
        else:
            self.exact_calls += 1

        # Por agente
        agent_key = usage.agent
        if agent_key not in self.by_agent:
            self.by_agent[agent_key] = {
                "calls": 0, "input_tokens": 0, "output_tokens": 0,
                "total_tokens": 0, "latency_ms": 0, "cache_hits": 0
            }
        a = self.by_agent[agent_key]
        a["calls"] += 1
        a["input_tokens"] += usage.input_tokens
        a["output_tokens"] += usage.output_tokens
        a["total_tokens"] += usage.total_tokens
        a["latency_ms"] += usage.latency_ms
        if usage.cache_hit:
            a["cache_hits"] += 1

        # Por operación
        op_key = usage.operation
        if op_key not in self.by_operation:
            self.by_operation[op_key] = {
                "calls": 0, "input_tokens": 0, "output_tokens": 0,
                "total_tokens": 0, "total_latency_ms": 0, "avg_latency_ms": 0
            }
        o = self.by_operation[op_key]
        o["calls"] += 1
        o["input_tokens"] += usage.input_tokens
        o["output_tokens"] += usage.output_tokens
        o["total_tokens"] += usage.total_tokens
        o["total_latency_ms"] += usage.latency_ms
        o["avg_latency_ms"] = o["total_latency_ms"] // o["calls"] if o["calls"] > 0 else 0

        # Por modelo
        model_key = f"{usage.provider}/{usage.model}"
        if model_key not in self.by_model:
            self.by_model[model_key] = {
                "calls": 0, "input_tokens": 0, "output_tokens": 0,
                "total_tokens": 0, "total_latency_ms": 0, "avg_latency_ms": 0
            }
        m = self.by_model[model_key]
        m["calls"] += 1
        m["input_tokens"] += usage.input_tokens
        m["output_tokens"] += usage.output_tokens
        m["total_tokens"] += usage.total_tokens
        m["total_latency_ms"] += usage.latency_ms
        m["avg_latency_ms"] = m["total_latency_ms"] // m["calls"] if m["calls"] > 0 else 0

        # Por episodio
        if usage.episode_id:
            ep_key = usage.episode_id
            if ep_key not in self.by_episode:
                self.by_episode[ep_key] = {
                    "calls": 0, "input_tokens": 0, "output_tokens": 0,
                    "total_tokens": 0, "agents": set()
                }
            e = self.by_episode[ep_key]
            e["calls"] += 1
            e["input_tokens"] += usage.input_tokens
            e["output_tokens"] += usage.output_tokens
            e["total_tokens"] += usage.total_tokens
            e["agents"].add(usage.agent)

        # Por escena
        if usage.scene_id:
            sc_key = usage.scene_id
            if sc_key not in self.by_scene:
                self.by_scene[sc_key] = {
                    "calls": 0, "input_tokens": 0, "output_tokens": 0,
                    "total_tokens": 0
                }
            s = self.by_scene[sc_key]
            s["calls"] += 1
            s["input_tokens"] += usage.input_tokens
            s["output_tokens"] += usage.output_tokens
            s["total_tokens"] += usage.total_tokens

    def to_dict(self) -> Dict[str, Any]:
        # Convertir sets a lists para serialización
        result = asdict(self)
        for ep_data in result["by_episode"].values():
            if isinstance(ep_data.get("agents"), set):
                ep_data["agents"] = list(ep_data["agents"])
        return result

    def get_summary(self) -> Dict[str, Any]:
        """Resumen ejecutivo del reporte."""
        cache_rate = 0
        if self.total_calls > 0:
            cache_rate = round(self.cache_hits / self.total_calls * 100, 1)

        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cache_hit_rate_pct": cache_rate,
            "avg_latency_ms": self.total_latency_ms // self.total_calls if self.total_calls > 0 else 0,
            "estimated_pct": round(self.estimated_calls / self.total_calls * 100, 1) if self.total_calls > 0 else 0,
            "top_agent_by_tokens": max(
                self.by_agent.items(),
                key=lambda x: x[1]["total_tokens"]
            )[0] if self.by_agent else None,
            "top_operation_by_tokens": max(
                self.by_operation.items(),
                key=lambda x: x[1]["total_tokens"]
            )[0] if self.by_operation else None,
        }


class TokenTracker:
    """
    Rastreador global de uso de tokens con persistencia opcional.
    Thread-safe para uso concurrente.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self._usages: List[TokenUsage] = []
        self._current_report = TokenUsageReport(
            period_start=datetime.utcnow().isoformat(),
            period_end=datetime.utcnow().isoformat()
        )
        self._session_start = datetime.utcnow()
        self._persist_path: Optional[Path] = None
        self._auto_persist = False
        self._persist_interval = 10  # persistir cada N registros
        self._count_since_persist = 0

    def configure(self, persist_path: Optional[str] = None, auto_persist: bool = False, persist_interval: int = 10):
        """Configura persistencia automática."""
        if persist_path:
            self._persist_path = Path(persist_path)
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        self._auto_persist = auto_persist
        self._persist_interval = persist_interval

    def record(self, usage: TokenUsage):
        """Registra un uso de tokens."""
        with self._lock:
            self._usages.append(usage)
            self._current_report.add_usage(usage)
            self._current_report.period_end = datetime.utcnow().isoformat()
            self._count_since_persist += 1

            if self._auto_persist and self._count_since_persist >= self._persist_interval:
                self._persist()
                self._count_since_persist = 0

    def _persist(self):
        """Persiste el reporte actual a disco."""
        if not self._persist_path:
            return
        try:
            data = {
                "session_start": self._session_start.isoformat(),
                "last_update": datetime.utcnow().isoformat(),
                "report": self._current_report.to_dict(),
                "recent_usages": [u.to_dict() for u in self._usages[-100:]]  # últimos 100
            }
            with open(self._persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # Silenciar errores de persistencia

    def get_report(self) -> TokenUsageReport:
        """Obtiene el reporte actual."""
        with self._lock:
            return self._current_report

    def get_usages(self,
                   agent: Optional[str] = None,
                   episode_id: Optional[str] = None,
                   operation: Optional[str] = None,
                   since: Optional[datetime] = None) -> List[TokenUsage]:
        """Filtra usos registrados."""
        with self._lock:
            results = self._usages
            if agent:
                results = [u for u in results if u.agent == agent]
            if episode_id:
                results = [u for u in results if u.episode_id == episode_id]
            if operation:
                results = [u for u in results if u.operation == operation]
            if since:
                results = [u for u in results if datetime.fromisoformat(u.timestamp) >= since]
            return results

    def reset(self):
        """Reinicia el rastreador para nueva sesión."""
        with self._lock:
            self._usages = []
            self._current_report = TokenUsageReport(
                period_start=datetime.utcnow().isoformat(),
                period_end=datetime.utcnow().isoformat()
            )
            self._session_start = datetime.utcnow()
            self._count_since_persist = 0

    @contextmanager
    def track_call(self,
                   agent: str,
                   operation: str,
                   model: str,
                   provider: str,
                   episode_id: Optional[str] = None,
                   season_id: Optional[str] = None,
                   project_id: Optional[str] = None,
                   scene_id: Optional[str] = None):
        """
        Context manager para trackear una llamada LLM automáticamente.

        Usage:
            with tracker.track_call("MasterWriter", "generate_script", "claude-opus-4-5", "freellmapi") as ctx:
                # ... make LLM call ...
                ctx.set_result(input_tokens=1000, output_tokens=500, estimated=True)
        """
        start_time = time.time()
        ctx = _TrackContext(self, agent, operation, model, provider,
                           episode_id, season_id, project_id, scene_id, start_time)
        try:
            yield ctx
        finally:
            if ctx._recorded:
                self.record(ctx._usage)


class _TrackContext:
    """Contexto interno para trackear una llamada LLM."""

    def __init__(self, tracker: TokenTracker, agent: str, operation: str,
                 model: str, provider: str, episode_id: Optional[str],
                 season_id: Optional[str], project_id: Optional[str],
                 scene_id: Optional[str], start_time: float):
        self._tracker = tracker
        self._agent = agent
        self._operation = operation
        self._model = model
        self._provider = provider
        self._episode_id = episode_id
        self._season_id = season_id
        self._project_id = project_id
        self._scene_id = scene_id
        self._start_time = start_time
        self._recorded = False
        self._usage: Optional[TokenUsage] = None

    def set_result(self,
                   input_text: str = "",
                   output_text: str = "",
                   input_tokens: Optional[int] = None,
                   output_tokens: Optional[int] = None,
                   estimated: bool = True,
                   estimation_method: TokenEstimationMethod = TokenEstimationMethod.CHAR_BASED,
                   cache_hit: bool = False):
        """Establece el resultado de la llamada LLM."""
        latency_ms = int((time.time() - self._start_time) * 1000)

        # Estimar tokens si no se proporcionan exactos
        if input_tokens is None:
            input_tokens = self._estimate_tokens(input_text, estimation_method)
        if output_tokens is None:
            output_tokens = self._estimate_tokens(output_text, estimation_method)

        self._usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated=estimated,
            estimation_method=estimation_method,
            model=self._model,
            provider=self._provider,
            agent=self._agent,
            operation=self._operation,
            cache_hit=cache_hit,
            latency_ms=latency_ms,
            context_size_chars=len(input_text),
            prompt_size_chars=len(input_text),
            output_size_chars=len(output_text),
            episode_id=self._episode_id,
            season_id=self._season_id,
            project_id=self._project_id,
            scene_id=self._scene_id,
        )
        self._recorded = True

    def _estimate_tokens(self, text: str, method: TokenEstimationMethod) -> int:
        """Estima tokens basándose en el método."""
        if not text:
            return 0

        if method == TokenEstimationMethod.CHAR_BASED:
            return max(1, len(text) // 4)
        elif method == TokenEstimationMethod.WORD_BASED:
            return max(1, int(len(text.split()) / 0.75))
        elif method == TokenEstimationMethod.TIKTOKEN:
            # Fallback a char-based si tiktoken no disponible
            try:
                import tiktoken
                enc = tiktoken.get_encoding("cl100k_base")
                return len(enc.encode(text))
            except ImportError:
                return max(1, len(text) // 4)
        else:
            return max(1, len(text) // 4)


# Instancia global
token_tracker = TokenTracker()


def estimate_tokens(text: str, method: TokenEstimationMethod = TokenEstimationMethod.CHAR_BASED) -> int:
    """Función de conveniencia para estimar tokens."""
    if not text:
        return 0
    if method == TokenEstimationMethod.CHAR_BASED:
        return max(1, len(text) // 4)
    elif method == TokenEstimationMethod.WORD_BASED:
        return max(1, int(len(text.split()) / 0.75))
    elif method == TokenEstimationMethod.TIKTOKEN:
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except ImportError:
            return max(1, len(text) // 4)
    return max(1, len(text) // 4)


def create_baseline_report() -> Dict[str, Any]:
    """Crea un reporte baseline para comparar antes/después de optimizaciones."""
    report = token_tracker.get_report()
    return {
        "baseline_timestamp": datetime.utcnow().isoformat(),
        "summary": report.get_summary(),
        "detailed": report.to_dict()
    }


def compare_reports(baseline: Dict[str, Any], optimized: Dict[str, Any]) -> Dict[str, Any]:
    """Compara dos reportes y calcula ahorros."""
    b = baseline.get("summary", {})
    o = optimized.get("summary", {})

    def calc_reduction(before: int, after: int) -> Dict[str, Any]:
        if before == 0:
            return {"reduction": 0, "pct": 0, "before": before, "after": after}
        reduction = before - after
        return {
            "reduction": reduction,
            "pct": round(reduction / before * 100, 1),
            "before": before,
            "after": after
        }

    return {
        "input_tokens": calc_reduction(b.get("input_tokens", 0), o.get("input_tokens", 0)),
        "output_tokens": calc_reduction(b.get("output_tokens", 0), o.get("output_tokens", 0)),
        "total_tokens": calc_reduction(b.get("total_tokens", 0), o.get("total_tokens", 0)),
        "llm_calls": calc_reduction(b.get("total_calls", 0), o.get("total_calls", 0)),
        "avg_latency_ms": calc_reduction(b.get("avg_latency_ms", 0), o.get("avg_latency_ms", 0)),
        "cache_hit_rate_change": round(
            o.get("cache_hit_rate_pct", 0) - b.get("cache_hit_rate_pct", 0), 1
        ),
    }