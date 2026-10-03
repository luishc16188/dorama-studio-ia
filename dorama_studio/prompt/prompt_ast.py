"""
Prompt AST - Fase 11
Abstract Syntax Tree nodes for prompt templating.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PromptNodeType(str, Enum):
    """Types of prompt AST nodes."""
    TEMPLATE = "template"
    VARIABLE = "variable"
    TEXT = "text"
    CONDITION = "condition"
    LOOP = "loop"


@dataclass
class PromptNode:
    """Base class for all prompt AST nodes."""
    node_type: PromptNodeType = field(default_factory=lambda: PromptNodeType.TEXT)  # default, will be overridden
    children: list[PromptNode] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, context: dict[str, Any]) -> str:
        """Render the node with the given context."""
        raise NotImplementedError

    def add_child(self, child: PromptNode) -> None:
        """Add a child node."""
        self.children.append(child)

    def remove_child(self, child: PromptNode) -> None:
        """Remove a child node."""
        if child in self.children:
            self.children.remove(child)


class TemplateNode(PromptNode):
    """Root node representing a complete prompt template."""
    def __init__(self, children: list[PromptNode] | None = None, metadata: dict[str, Any] | None = None):
        # Initialize base class with correct node_type
        super().__init__(
            node_type=PromptNodeType.TEMPLATE,
            children=children or [],
            metadata=metadata or []
        )

    def render(self, context: dict[str, Any]) -> str:
        """Render the template by rendering all children in order."""
        return "".join(child.render(context) for child in self.children)


class VariableNode(PromptNode):
    """Node representing a variable to be substituted from context."""
    def __init__(self, variable_name: str, default_value: Any = None, metadata: dict[str, Any] | None = None):
        super().__init__(
            node_type=PromptNodeType.VARIABLE,
            children=[],
            metadata=metadata or {}
        )
        self.variable_name = variable_name
        self.default_value = default_value

    def render(self, context: dict[str, Any]) -> str:
        """Render by looking up the variable in context."""
        if self.variable_name in context:
            value = context[self.variable_name]
            # Convert to string if not already
            if isinstance(value, str):
                return value
            else:
                return str(value)
        elif self.default_value is not None:
            return str(self.default_value)
        else:
            # Return empty string or placeholder? We'll return empty for safety.
            return ""


class TextNode(PromptNode):
    """Node representing literal text."""
    def __init__(self, text: str, metadata: dict[str, Any] | None = None):
        super().__init__(
            node_type=PromptNodeType.TEXT,
            children=[],
            metadata=metadata or {}
        )
        self.text = text

    def render(self, context: dict[str, Any]) -> str:
        """Render by returning the literal text."""
        return self.text


class ConditionNode(PromptNode):
    """Node representing a conditional block."""
    def __init__(self, condition: str,
                 children: list[PromptNode] | None = None,
                 else_children: list[PromptNode] | None = None,
                 metadata: dict[str, Any] | None = None):
        super().__init__(
            node_type=PromptNodeType.CONDITION,
            children=children or [],
            metadata=metadata or {}
        )
        self.condition = condition
        self.children = children or []
        self.else_children = else_children or []

    def render(self, context: dict[str, Any]) -> str:
        """Render by evaluating the condition and choosing the appropriate branch."""
        # Check if condition variable exists and is truthy
        condition_value = context.get(self.condition, False)
        # Handle common falsy values: False, 0, "", [], {}, None
        if condition_value:
            # Render the if branch
            return "".join(child.render(context) for child in self.children)
        else:
            # Render the else branch
            return "".join(child.render(context) for child in self.else_children)


class LoopNode(PromptNode):
    """Node representing a loop over a list in context."""
    def __init__(self, list_variable: str, item_variable: str,
                 index_variable: str | None = None,
                 children: list[PromptNode] | None = None,
                 metadata: dict[str, Any] | None = None):
        super().__init__(
            node_type=PromptNodeType.LOOP,
            children=children or [],
            metadata=metadata or {}
        )
        self.list_variable = list_variable
        self.item_variable = item_variable
        self.index_variable = index_variable
        self.children = children or []
        # metadata already set by super

    def render(self, context: dict[str, Any]) -> str:
        """Render by iterating over the list and rendering children for each item."""
        if self.list_variable not in context:
            return ""

        items = context[self.list_variable]
        if not isinstance(items, list):
            # If it's not a list, treat it as a single-item list
            items = [items]

        result_parts = []
        for index, item in enumerate(items):
            # Create a new context for this iteration
            loop_context = context.copy()
            loop_context[self.item_variable] = item
            if self.index_variable is not None:
                loop_context[self.index_variable] = index

            # Render children with the loop context
            result_parts.append("".join(child.render(loop_context) for child in self.children))

        return "".join(result_parts)


# Convenience function to build a simple template from a string with variable substitutions
def build_simple_template(template_string: str) -> TemplateNode:
    """
    Build a simple template from a string containing {variable} placeholders.
    This is a convenience method for simple cases.
    """
    # This is a very simple parser that only handles {variable} placeholders
    # For a full implementation, we would use a proper parser, but this suffices for now.
    import re

    # Split the string by {variable} patterns
    parts = re.split(r'(\{[^}]+\})', template_string)

    root = TemplateNode()

    for part in parts:
        if part.startswith('{') and part.endswith('}'):
            # This is a variable placeholder
            var_name = part[1:-1]  # Remove the braces
            variable_node = VariableNode(var_name)
            root.add_child(variable_node)
        elif part:
            # This is literal text
            text_node = TextNode(part)
            root.add_child(text_node)

    return root
# Alias for backward compatibility and to satisfy imports expecting PromptAST
PromptAST = TemplateNode
