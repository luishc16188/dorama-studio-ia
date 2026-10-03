"""
Prompt Compiler - Fase 11
Compiles Prompt AST into executable prompt strings with context binding.
"""

from __future__ import annotations

from typing import Any

from .prompt_ast import (
    PromptNode,
    PromptNodeType,
    TemplateNode,
)


class PromptCompiler:
    """
    Compiles Prompt AST into optimized prompt strings.
    Provides caching and optimization strategies for prompt generation.
    """

    def __init__(self, enable_cache: bool = True):
        self.enable_cache = enable_cache
        self._cache: dict[str, str] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def compile(self, ast: TemplateNode) -> str:
        """
        Compile a Prompt AST into a prompt string.
        This is the entry point - returns a string template ready for context substitution.

        For simplicity in this implementation, we return a string that can be used
        with Python's string formatting or template engines.
        In a production system, this might return a compiled template object.

        Args:
            ast: The Prompt AST to compile

        Returns:
            A string representation of the compiled template
        """
        if not isinstance(ast, TemplateNode):
            raise ValueError("AST must be a TemplateNode")

        # For now, we'll generate a Python-format string
        # In a real implementation, we might generate Jinja2 templates or similar
        return self._compile_node(ast)

    def _compile_node(self, node: PromptNode) -> str:
        """Compile a single node and its children."""
        if node.node_type == PromptNodeType.TEXT:
            # Escape braces for Python format strings if they're not placeholders
            text = node.text
            # Simple approach: just return the text as-is
            # A real implementation would handle escaping properly
            return text

        elif node.node_type == PromptNodeType.VARIABLE:
            var_name = node.variable_name
            # Return a placeholder for string formatting
            return f"{{{var_name}}}"

        elif node.node_type == PromptNodeType.CONDITION:
            # For conditions, we'll generate a more complex structure
            # In practice, this would need a template engine that supports conditionals
            # For now, we'll generate a simple representation
            condition_var = node.condition
            if_true = "".join(self._compile_node(child) for child in node.children)
            if_false = "".join(self._compile_node(child) for child in node.else_children)

            # This is a simplified representation - in reality we'd need
            # a proper templating engine
            return f"{{{{ IF {condition_var} }}}}{if_true}{{{{ ELSE }}}}{if_false}{{{{ ENDIF }}}}"

        elif node.node_type == PromptNodeType.LOOP:
            list_var = node.list_variable
            item_var = node.item_variable
            index_var = node.index_variable

            compiled_children = "".join(self._compile_node(child) for child in node.children)

            if index_var is not None:
                return f"{{{{ FOR {item_var}, {index_var} IN {list_var} }}}}{compiled_children}{{{{ ENDFOR }}}}"
            else:
                return f"{{{{ FOR {item_var} IN {list_var} }}}}{compiled_children}{{{{ ENDFOR }}}}"

        elif node.node_type == PromptNodeType.TEMPLATE:
            # Recursively compile children
            return "".join(self._compile_node(child) for child in node.children)

        else:
            # Fallback - treat as text
            return str(node)

    def render(self, ast: TemplateNode, context: dict[str, Any]) -> str:
        """
        Compile and render a Prompt AST with the given context.
        This combines compilation and rendering in one step.

        Args:
            ast: The Prompt AST to compile and render
            context: The context data for variable substitution

        Returns:
            The fully rendered prompt string
        """
        # Check cache first
        if self.enable_cache:
            # Create a cache key from the AST structure and context keys
            cache_key = self._create_cache_key(ast, context)
            if cache_key in self._cache:
                self._cache_hits += 1
                return self._cache[cache_key]

        # Render the AST
        result = self._render_node(ast, context)

        # Cache the result
        if self.enable_cache:
            self._cache[cache_key] = result
            self._cache_misses += 1

        return result

    def _render_node(self, node: PromptNode, context: dict[str, Any]) -> str:
        """Render a node with the given context (without caching)."""
        if node.node_type == PromptNodeType.TEXT:
            return node.text

        elif node.node_type == PromptNodeType.VARIABLE:
            if node.variable_name in context:
                value = context[node.variable_name]
                if isinstance(value, str):
                    return value
                else:
                    return str(value)
            elif node.default_value is not None:
                return str(node.default_value)
            else:
                return ""

        elif node.node_type == PromptNodeType.CONDITION:
            condition_value = context.get(node.condition, False)
            # Handle common falsy values
            if condition_value:
                # Render if branch
                return "".join(self._render_node(child, context) for child in node.children)
            else:
                # Render else branch
                return "".join(self._render_node(child, context) for child in node.else_children)

        elif node.node_type == PromptNodeType.LOOP:
            if node.list_variable not in context:
                return ""

            items = context[node.list_variable]
            if not isinstance(items, list):
                items = [items]

            result_parts = []
            for index, item in enumerate(items):
                loop_context = context.copy()
                loop_context[node.item_variable] = item
                if node.index_variable is not None:
                    loop_context[node.index_variable] = index

                result_parts.append("".join(self._render_node(child, loop_context) for child in node.children))

            return "".join(result_parts)

        elif node.node_type == PromptNodeType.TEMPLATE:
            return "".join(self._render_node(child, context) for child in node.children)

        else:
            # Fallback
            return str(node)

    def _create_cache_key(self, ast: TemplateNode, context: dict[str, Any]) -> str:
        """Create a cache key for the AST and context."""
        # Simple approach: hash the AST structure and context keys
        # In practice, we might want a more sophisticated key
        import hashlib

        # Create a representation of the AST structure
        ast_structure = self._ast_to_string(ast)

        # Use the keys of the context (not values, as they might be large/unhashable)
        context_keys = sorted(context.keys())

        key_string = f"{ast_structure}:{','.join(context_keys)}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _ast_to_string(self, node: PromptNode) -> str:
        """Convert AST to a string representation for caching."""
        if node.node_type == PromptNodeType.TEXT:
            return f"TEXT:{node.text}"
        elif node.node_type == PromptNodeType.VARIABLE:
            return f"VAR:{node.variable_name}:{node.default_value}"
        elif node.node_type == PromptNodeType.CONDITION:
            children_str = "".join(self._ast_to_string(child) for child in node.children)
            else_children_str = "".join(self._ast_to_string(child) for child in node.else_children)
            return f"COND:{node.condition}:[{children_str}][{else_children_str}]"
        elif node.node_type == PromptNodeType.LOOP:
            children_str = "".join(self._ast_to_string(child) for child in node.children)
            return f"LOOP:{node.list_variable}:{node.item_variable}:{node.index_variable}:[{children_str}]"
        elif node.node_type == PromptNodeType.TEMPLATE:
            children_str = "".join(self._ast_to_string(child) for child in node.children)
            return f"TEMPLATE:[{children_str}]"
        else:
            return f"UNKNOWN:{node.node_type}"

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0.0
        return {
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": hit_rate
        }

    def clear_cache(self) -> None:
        """Clear the compilation cache."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0


# Global compiler instance
prompt_compiler = PromptCompiler()
