"""
Prompt Provider - Fase 11
Provides prompt templating services with context-based generation and template management.
"""

from __future__ import annotations

from typing import Any

from .prompt_ast import TemplateNode, build_simple_template
from .prompt_compiler import PromptCompiler


class PromptTemplate:
    """
    A reusable prompt template with variables and optional compilation.
    """

    def __init__(self, name: str, template: Union[str, TemplateNode],
                 description: str | None = None):
        self.name = name
        self.description = description

        # Store the template as either a string or AST
        if isinstance(template, str):
            self._template_string = template
            self._template_ast = build_simple_template(template)
        elif isinstance(template, TemplateNode):
            self._template_string = None  # We'll generate it if needed
            self._template_ast = template
        else:
            raise ValueError("Template must be a string or TemplateNode")

        self._compiled_template: str | None = None
        self._compiler = PromptCompiler()

    def render(self, context: dict[str, Any]) -> str:
        """
        Render the template with the given context.

        Args:
            context: Dictionary of variable names to values

        Returns:
            The rendered prompt string
        """
        # Use the compiler to render the AST
        return self._compiler.render(self._template_ast, context)

    def compile(self) -> str:
        """
        Compile the template into a compiled string representation.
        This caches the compiled version for faster rendering.

        Returns:
            The compiled template string
        """
        if self._compiled_template is None:
            self._compiled_template = self._compiler.compile(self._template_ast)
        return self._compiled_template

    @property
    def template_string(self) -> str:
        """Get the original template string."""
        if self._template_string is not None:
            return self._template_string
        else:
            # If we only have AST, we could generate a string representation
            # but for now we'll require the original string to be provided
            # when constructing from string
            return "<AST only template>"

    @property
    def template_ast(self) -> TemplateNode:
        """Get the template AST."""
        return self._template_ast


class PromptProvider:
    """
    Provides prompt templating services with template management and context-based generation.
    """

    def __init__(self):
        self._templates: dict[str, PromptTemplate] = {}
        self._compiler = PromptCompiler()

    def register_template(self, name: str, template: Union[str, TemplateNode],
                         description: str | None = None) -> None:
        """
        Register a new prompt template.

        Args:
            name: Unique name for the template
            template: Template string or AST
            description: Optional description of the template's purpose
        """
        self._templates[name] = PromptTemplate(name, template, description)

    def get_template(self, name: str) -> PromptTemplate | None:
        """
        Get a registered template by name.

        Args:
            name: Template name

        Returns:
            The PromptTemplate if found, None otherwise
        """
        return self._templates.get(name)

    def render_template(self, name: str, context: dict[str, Any]) -> str | None:
        """
        Render a registered template with the given context.

        Args:
            name: Template name
            context: Dictionary of variable names to values

        Returns:
            The rendered prompt string, or None if template not found
        """
        template = self.get_template(name)
        if template is None:
            return None
        return template.render(context)

    def add_template_from_string(self, name: str, template_string: str,
                                description: str | None = None) -> None:
        """
        Convenience method to add a template from a string.

        Args:
            name: Template name
            template_string: Template string with {variable} placeholders
            description: Optional description
        """
        self.register_template(name, template_string, description)

    def list_templates(self) -> list[str]:
        """
        List all registered template names.

        Returns:
            List of template names
        """
        return list(self._templates.keys())

    def get_template_info(self, name: str) -> dict[str, Any] | None:
        """
        Get information about a registered template.

        Args:
            name: Template name

        Returns:
            Dictionary with template info, or None if not found
        """
        template = self.get_template(name)
        if template is None:
            return None

        return {
            "name": template.name,
            "description": template.description,
            "template_string": template.template_string,
            "has_ast": template.template_ast is not None
        }


# Global prompt provider instance
prompt_provider = PromptProvider()
