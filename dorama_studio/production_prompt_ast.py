"""ProductionPromptAST for DORAMA STUDIO IA V2.

Defines a normalized AST (Abstract Syntax Tree) representation of prompts
that can be consumed by any ProviderCompiler.  The structure is deliberately
kept simple and provider‑agnostic; each compiler translates the AST into
the specific format required by the underlying LLM provider (Claude, OpenAI,
Gemini, etc.).
"""

from __future__ import annotations

from typing import Any


class PromptNode:
    """Base node in the ProductionPromptAST."""

    node_type: str
    """Tipo de nodo (ej. "root", "section", "variable", "instruction")."""

    payload: dict[str, Any]
    """Diccionario con los datos asociados a este nodo."""

    def __str__(self) -> str:
        return f"<{self.node_type}: {self.payload}>"


class RootNode(PromptNode):
    """Nodo raíz que contiene el prompt completo."""

    def __init__(self, sections: list[PromptNode] | None = None) -> None:
        super().__init__(node_type="root", payload={})
        self.payload["sections"] = sections or []


class SectionNode(PromptNode):
    """Nodo que agrupa una sección temática del prompt (por ejemplo, “personaje”, “escenario”)."""

    def __init__(self, title: str, nodes: list[PromptNode] | None = None) -> None:
        super().__init__(node_type="section", payload={})
        self.payload["title"] = title
        self.payload["nodes"] = nodes or []


class VariableNode(PromptNode):
    """Nodo que representa una variable o placeholder que será rellenado en tiempo de ejecución."""

    def __init__(self, name: str, description: str | None = None, default: Any = None) -> None:
        super().__init__(node_type="variable", payload={})
        self.payload["name"] = name
        if description:
            self.payload["description"] = description
        self.payload["default"] = default


class InstructionNode(PromptNode):
    """Nodo que representa una instrucción directa al modelo (por ejemplo, “escribe un diálogo”)."""

    def __init__(self, text: str, role: str | None = None) -> None:
        super().__init__(node_type="instruction", payload={})
        self.payload["text"] = text
        if role:
            self.payload["role"] = role


# ---------------------------------------------------------------------------
# Helper to build a AST from simple inputs
# ---------------------------------------------------------------------------

def build_ast_from_parts(
    title: str,
    character: dict[str, Any] | None = None,
    plot_points: list[str] | None = None,
    tone: str | None = None,
) -> RootNode:
    """Convenience function to create a RootNode AST from typical V2 data."""
    root = RootNode()

    # Section: personaje
    char_nodes: list[PromptNode] = []
    if character:
        char_nodes.append(VariableNode("name", description="Nombre del personaje principal", default=character.get("name")))
        char_nodes.append(VariableNode("role", description="Rol del personaje", default=character.get("role")))
    root.payload["sections"].append(SectionNode("personaje", char_nodes))

    # Section: trama
    plot_nodes: list[PromptNode] = []
    if plot_points:
        for i, point in enumerate(plot_points, start=1):
            plot_nodes.append(InstructionNode(f"Punto {i}: {point}"))
    root.payload["sections"].append(SectionNode("trama", plot_nodes))

    # Section: tono
    if tone:
        root.payload["sections"].append(
            SectionNode("tono", [InstructionNode(f"Mantén un tono {tone}")])
        )

    return root


# ---------------------------------------------------------------------------
# Serialization to string (simple) – could be extended to JSON, etc.
# ---------------------------------------------------------------------------

def ast_to_string(root: RootNode, indent: int = 0) -> str:
    """Devuelve una representación en cadena legible del AST."""
    lines: list[str] = []
    prefix = "  " * indent
    lines.append(f"{prefix}root")
    for section in root.payload.get("sections", []):
        lines.append(ast_to_string_section(section, indent + 1))
    return "\n".join(lines)


def ast_to_string_section(section: SectionNode, indent: int) -> str:
    prefix = "  " * indent
    lines: list[str] = []
    lines.append(f"{prefix}section: {section.payload.get('title')}")
    for node in section.payload.get("nodes", []):
        lines.append(ast_to_string_node(node, indent + 1))
    return "\n".join(lines)


def ast_to_string_node(node: PromptNode, indent: int) -> str:
    prefix = "  " * indent
    type_label = node.node_type
    payload = node.payload
    # Simplify display: show name if present
    name = payload.get("name", "")
    txt = payload.get("text", "")
    if name:
        lines = [f"{prefix}{type_label}: {name}"]
    elif txt:
        lines = [f"{prefix}{type_label}: {txt[:60]}{'...' if len(txt) > 60 else ''}"]
    else:
        lines = [f"{prefix}{type_label}"]
    return lines[0]
