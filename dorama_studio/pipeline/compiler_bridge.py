def build_token_index(casting) -> dict[str, str]:
    """Build a mapping from role names to character IDs (tokens)."""
    token_index = {}
    for role_name, (actor_id, _) in casting.assignments.items():
        token_index[role_name] = casting.get_character_id(role_name)
    return token_index


def get_compiler_bridge():
    """Return a compiler bridge instance."""

    # For now, we'll return a simple object that has the compile_episode method.
    # In a real implementation, this would be more complex.
    class CompilerBridge:
        def compile_episode(self, bible, storyboard, universe, target_engines=None):
            # Return a mock manifest object
            class Manifest:
                def summary(self):
                    return "Manifest summary (mock)"

                packages = {}

            return Manifest()

    return CompilerBridge
