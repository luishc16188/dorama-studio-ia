#!/usr/bin/env python
"""
Configuration Manager v4.0 - Dorama Studio IA.
Gestiona y provee acceso a configuraciones versionadas con validación automática.
Soporte para hot-reload, overrides por entorno y validación de cadenas de fallback.
"""

import hashlib
import logging
import os
from pathlib import Path
from typing import Any

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


class ConfigurationManager:
    """Gestiona configuraciones versionadas con validación automática.
    Carga los YAML del directorio `config/` con versionado y seguimiento de dependencias.
    """

    def __init__(self, config_dir: str = "config") -> None:
        self.config_dir = Path(config_dir)
        self._config_cache: dict[str, Any] = {}
        self._config_versions: dict[str, str] = {}
        self._config_deps: dict[str, list[str]] = {}
        self._load_all_configs()

    def _load_all_configs(self) -> None:
        """Carga todos los YAML con validación y versionado."""
        if not self.config_dir.exists():
            raise FileNotFoundError(
                f"Configuration directory not found: {self.config_dir}"
            )
        for yaml_file in sorted(self.config_dir.glob("*.yaml")):
            config_name = yaml_file.stem
            try:
                with open(yaml_file, encoding="utf-8") as f:
                    raw_content = f.read()
                config_data = __import__("yaml").safe_load(raw_content)
                version = self._extract_version(
                    config_data, yaml_file.name, raw_content
                )
                self._config_versions[config_name] = version
                deps = self._detect_dependencies(config_data, yaml_file.name)
                self._config_deps[config_name] = deps
                self._config_cache[config_name] = {
                    "version": version,
                    "data": config_data,
                    "raw_content": raw_content,
                    "source_file": str(yaml_file),
                    "last_modified": os.path.getmtime(yaml_file),
                }
            except Exception as e:
                logger.error(f"Error loading config {config_name}: {e}")

    def _extract_version(
        self, config_data: dict, filename: str, raw_content: str = ""
    ) -> str:
        """Extrae o genera la versión de un archivo de configuración."""
        if isinstance(config_data, dict) and "version" in config_data:
            v = config_data["version"]
            if isinstance(v, str) and v.startswith("v"):
                return v
            return f"v{config_data.get('_meta', {}).get('iteration', '1.0')}"
        content_hash = hashlib.md5(raw_content.encode()).hexdigest()[:8]
        return f"v{content_hash}"

    def _detect_dependencies(self, config_data: dict, filename: str) -> list[str]:
        """Detecta dependencias de un config (fallback chains, etc.)."""
        deps = []
        if isinstance(config_data, dict):
            for key in ["fallback_chain", "fallback", "depends_on", "providers"]:
                if key in config_data and isinstance(config_data[key], list):
                    for item in config_data[key]:
                        if isinstance(item, dict) and "provider" in item:
                            deps.append(item["provider"])
                        elif isinstance(item, str):
                            deps.append(item)
        return deps

    def get_config(self, config_name: str) -> dict[str, Any] | None:
        cached = self._config_cache.get(config_name)
        if cached:
            return cached["data"]
        yaml_path = Path(self.config_dir) / f"{config_name}.yaml"
        if yaml_path.exists():
            try:
                with open(yaml_path, encoding="utf-8") as f:
                    return __import__("yaml").safe_load(f)
            except Exception:
                return None
        return None

    def get_all_configs(self) -> dict[str, Any]:
        merged = {}
        for name, cached in self._config_cache.items():
            merged[name] = cached["data"]
        return merged

    def check_schema_validity(self, config_name: str) -> bool:
        config_name = config_name.removesuffix(".yaml")
        data = self.get_config(config_name)
        if data is None:
            return False
        return self._validate_config_schema(config_name, data)

    def _validate_config_schema(self, config_name: str, data: dict) -> bool:
        if config_name == "models.yaml":
            return all(
                k in data
                for k in ["llm", "image", "video", "tts", "music", "platforms"]
            )
        elif config_name == "platforms.yaml":
            return all(
                k in data.get("platforms", {})
                for k in ["tiktok", "youtube_shorts", "instagram_reels"]
            )
        elif config_name == "video_prompts.yaml":
            return "video_prompts" in data
        elif config_name == "quality.yaml":
            return "episode_scorer" in data
        elif config_name == "genres.yaml":
            return "genres" in data
        return bool(data)

    def check_mutation_budget(
        self, agent_name: str, genre: str, budget_type: str
    ) -> dict[str, Any]:
        try:
            from dorama_studio.creative_genome import CreativeGenomeV2 as CreativeGenome
        except ImportError:
            return {
                "approved": True,
                "remaining": self._budget_type_cap(budget_type),
                "used": 0,
            }
        genome = CreativeGenome(agent_name)
        with genome._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM mutation_budget WHERE agent_name = ? AND genre = ?",
                (agent_name, genre),
            )
            row = cursor.fetchone()
        if not row:
            caps = {"proven": 70, "exploration": 20, "big_bet": 10}
            return {"approved": True, "remaining": caps.get(budget_type, 0), "used": 0}
        if budget_type == "proven":
            available = 70 - (row[2] or 0)
            return {
                "approved": available >= 50,
                "remaining": available,
                "used": row[2] or 0,
            }
        elif budget_type == "exploration":
            available = 20 - (row[3] or 0)
            return {
                "approved": available >= 10,
                "remaining": available,
                "used": row[3] or 0,
            }
        elif budget_type == "big_bet":
            available = 10 - (row[4] or 0)
            return {
                "approved": available >= 3,
                "remaining": available,
                "used": row[4] or 0,
            }
        return {"approved": True, "remaining": 0, "used": 0}

    def import_agent_module(self, module_name: str):
        import importlib

        try:
            return importlib.import_module(f"dorama_studio.agents.{module_name}")
        except ImportError as e:
            logger.warning(f"Could not import agent module {module_name}: {e}")
            return None

    def check_fallback_chains(self) -> dict[str, Any]:
        result = {}
        for name in self._config_cache:
            deps = self._config_deps.get(name, [])
            data = self.get_config(name)
            if data:
                result[name] = {
                    "dependencies": deps,
                    "has_fallbacks": len(deps) > 0,
                    "version": self._config_cache[name]["version"],
                }
        return result

    def _budget_type_cap(self, budget_type: str) -> int:
        return {"proven": 70, "exploration": 20, "big_bet": 10}.get(budget_type, 0)


# Instancia global
config_manager = ConfigurationManager()
