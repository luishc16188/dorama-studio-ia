"""Utilities para exportar artifacts (JSON, markdown, SVG, etc.)."""

import json
from pathlib import Path
from typing import Any


def write_json(data: Any, destination: Path) -> None:
    """Escribe un diccionario/objeto como JSON formateado."""
    destination.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(source: Path) -> Any:
    """Lee un archivo JSON y devuelve el objeto Python correspondiente."""
    return json.loads(source.read_text(encoding="utf-8"))
