# Registro de sub-agentes disponibles
# Este archivo declara qué subagentes están disponibles y sus capacidades.

SUBAgENT_POOL = {
    'claude_code': {
        'name': 'Claude Code',
        'role': 'Forensic Prompt & Creative Systems Specialist',
        'capabilities': [
            'prompt_analysis',
            'architectural_design',
            'creative_writing',
            'audit',
            'pattern_recognition',
            'benchmark_design'
        ],
        'input_format': 'json',
        'output_format': 'json',
        'activation': 'requires_approval',  # Typically requires user approval
        'description': 'Forensic analysis of prompt engineering, model behaviors, and creative systems'
    },
    'codex': {
        'name': 'Codex',
        'role': 'Implementation & Benchmarking Engine',
        'capabilities': [
            'code_implementation',
            'test_generation',
            'benchmark_execution',
            'refactoring',
            'debugging',
            'benchmark_design'
        ],
        'input_format': 'json',
        'output_format': 'json',
        'activation': 'auto',  # Auto-activates after approval
        'description': 'Implementation & benchmarking engine for code and prompts'
    }
}

def get_subagent(name):
    """Get subagent config by name."""
    if name in SUBAgENT_POOL:
        return SUBAgENT_POOL[name]
    raise ValueError(f"Unknown subagent: {name}")

def list_subagents():
    """List all available subagents."""
    return list(SUBAgENT_POOL.keys())

def get_subagent_capabilities(name):
    """Get capabilities of a subagent."""
    if name in SUBAgENT_POOL:
        return SUBAgENT_POOL[name]['capabilities']
    raise ValueError(f"Unknown subagent: {name}")

