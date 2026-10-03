"""ProviderCapabilityRegistry for DORAMA STUDIO IA V2.

Registra las capacidades de cada proveedor de LLM (modelos soportados,
formato de entrada/salida, restricciones, precios aproximados).  Este
registro es consultado por los ProviderCompiladores para decidir cómo
transformar un ProductionPromptAST en la llamada concreta al modelo.

El registro es una singleton global que puede ser poblada al arranque
o cargada desde un archivo de configuración JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Datos por defecto – puede ser sobrescrito cargando un JSON externo
# ---------------------------------------------------------------------------

DEFAULT_CAPABILITIES: dict[str, dict[str, Any]] = {
    "claude-3-opus-20240229": {
        "max_input_tokens": 100_000,
        "max_output_tokens": 4096,
        "pricing_usd_per_1k_output": 0.075,
        "pricing_usd_per_1k_input": 0.015,
        "supported_formats": ["text", "json"],
        "features": ["system", "tool_use", "stop_sequence"],
    },
    "claude-3-sonnet-20240229": {
        "max_input_tokens": 100_000,
        "max_output_tokens": 4096,
        "pricing_usd_per_1k_output": 0.03,
        "pricing_usd_per_1k_input": 0.003,
        "supported_formats": ["text", "json"],
        "features": ["system", "tool_use", "stop_sequence"],
    },
    "gpt-4o-mini-2024-07-18": {
        "max_input_tokens": 128_000,
        "max_output_tokens": 16_384,
        "pricing_usd_per_1k_output": 0.0015,
        "pricing_usd_per_1k_input": 0.00015,
        "supported_formats": ["text", "json"],
        "features": ["system", "function_calling"],
    },
    "gemini-1.5-pro-20240515": {
        "max_input_tokens": 100_000,
        "max_output_tokens": 8192,
        "pricing_usd_per_1k_output": 0.02,
        "pricing_usd_per_1k_input": 0.001,
        "supported_formats": ["text"],
        "features": ["system", "stop_sequence"],
    },
}


class ProviderCapabilityRegistry:
    """Singleton que contiene las capacidades de cada proveedor."""

    _instance: ProviderCapabilityRegistry | None = None
    _capabilities: dict[str, dict[str, Any]]

    def __new__(cls) -> ProviderCapabilityRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._capabilities = dict(DEFAULT_CAPABILITIES)
        return cls._instance

    # -----------------------------------------------------------------
    # Acceso y consulta
    # -----------------------------------------------------------------
    def get(self, model_id: str) -> dict[str, Any] | None:
        """Devolver el diccionario de capacidades para *model_id* o None."""
        return self._capabilities.get(model_id)

    def list_models(self) -> list[str]:
        """Devolver los modelos registrados."""
        return list(self._capabilities.keys())

    # -----------------------------------------------------------------
    # Carga/guardado persistente
    # -----------------------------------------------------------------
    @classmethod
    def load_from_json(cls, path: str | Path) -> ProviderCapabilityRegistry:
        """Cargar capacidades desde un archivo JSON y reemplazar el default."""
        instance = cls()
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo de capacidades no encontrado: {path}")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        # Mezclar con defaults: cualquier clave nueva se añade, las existentes se actualizan
        instance._capabilities.update(data)
        return instance

    def save_to_json(self, path: str | Path) -> None:
        """Persistir el diccionario actual a un archivo JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._capabilities, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Convenience function to obtain the singleton
# ---------------------------------------------------------------------------

def get_registry() -> ProviderCapabilityRegistry:
    """Devolver la instancia global del registry."""
    return ProviderCapabilityRegistry()
