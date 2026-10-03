"""ProviderCompilers for DORAMA STUDIO IA V2.

Cada compilador recibe un *ProductionPromptAST* (o una representación
simplificada) y produce la llamada concreta al modelo del proveedor
correspondiente (Claude, OpenAI, Gemini, etc.).  El diseño permite
agregar nuevos proveedores sin modificar el núcleo del sistema.

Los compiladores esperan que el *prompt* venga dado como un diccionario
con las claves habituales (`model`, `messages`, `temperature`, etc.), pero
la lógica de mapeo está encapsulada en cada clase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .production_prompt_ast import RootNode
from .provider_capability_registry import get_registry


# ---------------------------------------------------------------------------
# DTO que devuelve cada compilador
# ---------------------------------------------------------------------------
@dataclass
class CompilationResult:
    """Resultado de compilar un prompt para un proveedor concreto."""

    model_id: str
    messages: list[dict[str, Any]]
    system: str | None = None
    temperature: float = 0.5
    max_tokens: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Compilador para proveedores Claude (serie 3)
# ---------------------------------------------------------------------------
class ClaudeCompiler:
    """Compila un ProductionPromptAST en mensajes para un modelo Claude."""

    # Model IDs compatibles (se consultan al Runtime contra el registry)
    COMPATIBLE_MODELS = {"claude-3-opus-20240229", "claude-3-sonnet-20240229"}

    def __init__(self, model_id: str = "claude-3-sonnet-20240229") -> None:
        if model_id not in self.COMPATIBLE_MODELS:
            raise ValueError(f"Modelo no compatible con ClaudeCompiler: {model_id}")
        self.model_id = model_id
        self.registry = get_registry()

    # -----------------------------------------------------------------
    # Transformación principal
    # -----------------------------------------------------------------
    def compile(self, ast: RootNode) -> CompilationResult:
        """Convierte el AST en la estructura de mensajes de Claude."""
        # Extraer system prompt, user message, etc. de forma sencilla
        system_prompt: str | None = None
        user_messages: list[dict[str, Any]] = []

        for section in ast.payload.get("sections", []):
            for node in section.payload.get("nodes", []):
                node_type = node.node_type
                payload = node.payload

                if node_type == "instruction":
                    text = payload.get("text", "")
                    role = payload.get("role", "user")
                    if role == "system":
                        system_prompt = text
                    else:
                        user_messages.append({"role": role, "content": text})

                elif node_type == "variable":
                    # Las variables se insertan como contenido de ejemplo
                    name = payload.get("name", "unknown")
                    default = payload.get("default", "")
                    user_messages.append(
                        {"role": "user", "content": f"[{name}]: {default}"}
                    )

                # Otros tipos pueden ignorarse o lanzarse un warning

        # Si no hay mensaje de usuario, insertamos un placeholder
        if not user_messages:
            user_messages.append({"role": "user", "content": "Genera el contenido solicitado."})

        # Consultar límites del modelo desde el registry
        caps = self.registry.get(self.model_id)
        max_output = caps.get("max_output_tokens") if caps else None

        return CompilationResult(
            model_id=self.model_id,
            messages=user_messages,
            system=system_prompt,
            max_tokens=max_output,
        )


# ---------------------------------------------------------------------------
# Compilador para OpenAI (GPT‑4o‑mini como ejemplo)
# ---------------------------------------------------------------------------
class OpenAICompiler:
    """Compila un ProductionPromptAST en mensajes para un modelo OpenAI GPT‑4o‑mini."""

    COMPATIBLE_MODELS = {"gpt-4o-mini-2024-07-18"}

    def __init__(self, model_id: str = "gpt-4o-mini-2024-07-18") -> None:
        if model_id not in self.COMPATIBLE_MODELS:
            raise ValueError(f"Modelo no compatible con OpenAICompiler: {model_id}")
        self.model_id = model_id
        self.registry = get_registry()

    def compile(self, ast: RootNode) -> CompilationResult:
        system_prompt: str | None = None
        user_messages: list[dict[str, Any]] = []

        for section in ast.payload.get("sections", []):
            for node in section.payload.get("nodes", []):
                node_type = node.node_type
                payload = node.payload

                if node_type == "instruction":
                    text = payload.get("text", "")
                    role = payload.get("role", "user")
                    if role == "system":
                        system_prompt = text
                    else:
                        user_messages.append({"role": role, "content": text})

                elif node_type == "variable":
                    name = payload.get("name", "unknown")
                    default = payload.get("default", "")
                    user_messages.append(
                        {"role": "user", "content": f"[{name}]: {default}"}
                    )

        if not user_messages:
            user_messages.append({"role": "user", "content": "Genera el contenido solicitado."})

        caps = self.registry.get(self.model_id)
        max_output = caps.get("max_output_tokens") if caps else None

        return CompilationResult(
            model_id=self.model_id,
            messages=user_messages,
            system=system_prompt,
            max_tokens=max_output,
        )


# ---------------------------------------------------------------------------
# Compilador para Gemini (versión mínima)
# ---------------------------------------------------------------------------
class GeminiCompiler:
    """Compila un ProductionPromptAST en la forma que espera el modelo Gemini."""

    COMPATIBLE_MODELS = {"gemini-1.5-pro-20240515"}

    def __init__(self, model_id: str = "gemini-1.5-pro-20240515") -> None:
        if model_id not in self.COMPATIBLE_MODELS:
            raise ValueError(f"Modelo no compatible con GeminiCompiler: {model_id}")
        self.model_id = model_id
        self.registry = get_registry()

    def compile(self, ast: RootNode) -> CompilationResult:
        # Gemini usa un formato ligeramente distinto: contents[].role + content
        system_instruction: str | None = None
        contents: list[dict[str, Any]] = []

        for section in ast.payload.get("sections", []):
            for node in section.payload.get("nodes", []):
                node_type = node.node_type
                payload = node.payload

                if node_type == "instruction":
                    text = payload.get("text", "")
                    # En Gemini la instrucción del sistema se mete en system_instruction
                    if node.payload.get("role") == "system":
                        system_instruction = text
                    else:
                        contents.append({"role": "user", "parts": [text]})

                elif node_type == "variable":
                    name = payload.get("name", "unknown")
                    default = payload.get("default", "")
                    contents.append({"role": "user", "parts": [f"[{name}]: {default}"]})

        if not contents:
            contents.append({"role": "user", "parts": ["Genera el contenido solicitado."]})

        caps = self.registry.get(self.model_id)
        max_output = caps.get("max_output_tokens") if caps else None

        return CompilationResult(
            model_id=self.model_id,
            messages=[],  # Gemini usa 'contents', no 'messages' estrictamente
            system=system_instruction,
            max_tokens=max_output,
            extra={"contents": contents},
        )


# ---------------------------------------------------------------------------
# Helper de un solo paso: dado un AST y un proveedor, devolver el resultado
# ---------------------------------------------------------------------------
def compile_prompt(ast: RootNode, provider: str = "claude", model_id: str | None = None) -> CompilationResult:
    """Función de conveniencia que devuelve el CompilationResult correspondiente."""
    registry = get_registry()
    # Si el usuario indicó un model_id, usarlo; si no, elegir el primero del registry
    selected_model = model_id or (registry.list_models()[0] if registry.list_models() else "claude-3-sonnet-20240229")

    if provider == "claude":
        compiler = ClaudeCompiler(model_id=selected_model)
    elif provider == "openai":
        compiler = OpenAICompiler(model_id=selected_model)
    elif provider == "gemini":
        compiler = GeminiCompiler(model_id=selected_model)
    else:
        raise ValueError(f"Proveedor desconocido: {provider}")

    return compiler.compile(ast)
