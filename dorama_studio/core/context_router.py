#!/usr/bin/env python
"""Context Router for AI Dorama Studio.

Implements HOT/COLD memory routing protocol as defined in Mission Brief Section 3.
Levels:
  Level 0: Always read PROJECT_STATE.md
  Level 1: Read AGENTS_INDEX.md for agent dependencies
  Level 2: Load targeted agent specifications
  Level 3: Fetch domain-specific Cold Memory modules

Rule: NEVER read full chat histories or entire repository by default.
Execute minimum-context retrieval.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Hot memory - always active
HOT_DIR = Path("memory/hot")
COLD_DIR = Path("memory/cold")
RESEARCH_DIR = Path("research")

# Token budget constants
MAX_TOKEN_BUDGET = 8000
RESERVED_TOKENS = 1000
AVAILABLE_TOKENS = MAX_TOKEN_BUDGET - RESERVED_TOKENS


@dataclass
class TokensUsed:
    """Tracks token usage across context levels."""

    total: int = 0
    level_0: int = 0
    level_1: int = 0
    level_2: int = 0
    level_3: int = 0
    research: int = 0


@dataclass
class Payload:
    """Payload returned by ContextRouter."""

    content: str
    tokens_used: TokensUsed
    levels_loaded: list[int]
    metadata: dict[str, Any]


class State:
    """State object passed to ContextRouter."""

    def __init__(
        self,
        level: int = 0,
        agent_names: list[str] | None = None,
        research_modules: list[str] | None = None,
    ):
        self.level = level
        self.agent_names = agent_names or []
        self.research_modules = research_modules or []
        self.tokens_used = TokensUsed()
        self.levels_loaded = []


class ContextRouter:
    """Context Router with token budget management."""

    def __init__(self, max_tokens: int = MAX_TOKEN_BUDGET):
        self.max_tokens = max_tokens
        self.reserved_tokens = RESERVED_TOKENS
        self.available_tokens = max_tokens - self.reserved_tokens

    def _count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token ~= 4 chars)."""
        return len(text) // 4

    def _add_content(self, state: State, level: int, content: str) -> bool:
        """Add content to state if within token budget. Returns True if added."""
        tokens = self._count_tokens(content)
        if state.tokens_used.total + tokens > self.available_tokens:
            return False

        setattr(
            state.tokens_used,
            f"level_{level}",
            getattr(state.tokens_used, f"level_{level}") + tokens,
        )
        state.tokens_used.total += tokens
        state.levels_loaded.append(level)
        return True

    def load_project_state(self, state: State) -> str:
        """Level 0: Always read PROJECT_STATE.md"""
        project_file = Path("memory/hot") / "PROJECT_STATE.md"
        if project_file.exists():
            with open(project_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "# PROJECT_STATE.md not found - initialize first"

        if self._add_content(state, 0, content):
            return content
        return "# Token budget exceeded for Level 0"

    def load_current_task(self, state: State) -> str:
        """Level 0 auxiliary: current task context"""
        task_file = Path("memory/hot") / "HOT_CONTEXT" / "CURRENT_TASK.md"
        if task_file.exists():
            with open(task_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "# CURRENT_TASK.md not found"

        if self._add_content(state, 0, content):
            return content
        return "# Token budget exceeded for Level 0 task"

    def load_agents_index(self, state: State) -> dict[str, Any]:
        """Level 1: Identify necessary agent dependencies"""
        agents_dir = Path("dorama_studio/agents")
        agents_list = []
        if agents_dir.exists():
            for py_file in sorted(agents_dir.rglob("*.py")):
                if not py_file.name.startswith("__"):
                    agents_list.append(py_file.stem)

        content = "Agents: " + str(agents_list)
        self._add_content(state, 1, content)
        return {"agents": agents_list, "dependencies": {}}

    def load_agent_spec(self, state: State, agent_name: str) -> str:
        """Level 2: Load targeted agent specifications"""
        agent_file = Path("dorama_studio/agents/" + agent_name + ".py")
        if agent_file.exists():
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "# Agent spec not found: " + agent_name + ".py"

        self._add_content(state, 2, content)
        return content

    def load_cold_memory(self, state: State, module_name: str) -> str:
        """Level 3: Fetch domain-specific Cold Memory modules"""
        cold_file = Path("memory/cold") / module_name
        if cold_file.exists():
            with open(cold_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "# Cold memory module not found: " + module_name

        self._add_content(state, 3, content)
        return content

    def get_research_veo(self, state: State) -> dict[str, str]:
        """Research module for Veo 3.1 specifications"""
        veo_dir = Path("research") / "veo"
        if veo_dir.exists():
            files = list(veo_dir.glob("*.md"))
            result = {f.name: f.read_text(encoding="utf-8") for f in files}
            content = str(result)
            self._add_content(state, 3, content)  # Count as research level
            return result
        return {}

    def get_research_characters(self, state: State) -> dict[str, str]:
        """Research module for character standards"""
        char_dir = Path("research") / "characters"
        if char_dir.exists():
            files = list(char_dir.glob("*.md"))
            result = {f.name: f.read_text(encoding="utf-8") for f in files}
            content = str(result)
            self._add_content(state, 3, content)  # Count as research level
            return result
        return {}

    def route(self, state: State) -> Payload:
        """Route context based on state level and token budget."""
        all_content = []

        # Level 0: Always load project state
        proj = self.load_project_state(state)
        all_content.append("=== LEVEL 0: PROJECT STATE ===\n" + proj)
        task = self.load_current_task(state)
        all_content.append("=== LEVEL 0: CURRENT TASK ===\n" + task)

        if state.level >= 1:
            # Level 1: Agents index
            idx = self.load_agents_index(state)
            all_content.append(
                "=== LEVEL 1: AGENTS INDEX ===\nAgents: " + str(idx["agents"])
            )

            if state.level >= 2:
                # Level 2: Targeted agent specs
                for agent in state.agent_names:
                    spec = self.load_agent_spec(state, agent)
                    all_content.append(
                        "=== LEVEL 2: AGENT " + agent.upper() + " ===\n" + spec
                    )

                if state.level >= 3:
                    # Level 3: Cold memory and research
                    for module in ["template_master.md"]:
                        cold = self.load_cold_memory(state, module)
                        all_content.append(
                            "=== LEVEL 3: COLD MEMORY " + module + " ===\n" + cold
                        )

                    # Research modules
                    for module in state.research_modules:
                        if module == "veo":
                            research = self.get_research_veo(state)
                            all_content.append(
                                "=== RESEARCH: VEO ===\n" + str(research)
                            )
                        elif module == "characters":
                            research = self.get_research_characters(state)
                            all_content.append(
                                "=== RESEARCH: CHARACTERS ===\n" + str(research)
                            )

        # Combine all content
        combined = "\n\n".join(all_content)

        return Payload(
            content=combined,
            tokens_used=state.tokens_used,
            levels_loaded=state.levels_loaded,
            metadata={
                "max_tokens": self.max_tokens,
                "reserved_tokens": self.reserved_tokens,
                "available_tokens": self.available_tokens,
                "token_utilization_pct": round(
                    state.tokens_used.total / self.available_tokens * 100, 1
                ),
            },
        )


def load_project_state():
    """Level 0: Always read PROJECT_STATE.md (legacy function)"""
    project_file = Path("memory/hot") / "PROJECT_STATE.md"
    if project_file.exists():
        with open(project_file, "r", encoding="utf-8") as f:
            return f.read()
    return "# PROJECT_STATE.md not found - initialize first"


def load_current_task():
    """Level 0 auxiliary: current task context (legacy function)"""
    task_file = Path("memory/hot") / "HOT_CONTEXT" / "CURRENT_TASK.md"
    if task_file.exists():
        with open(task_file, "r", encoding="utf-8") as f:
            return f.read()
    return "# CURRENT_TASK.md not found"


def load_agents_index():
    """Level 1: Identify necessary agent dependencies (legacy function)"""
    agents_dir = Path("dorama_studio/agents")
    agents_list = []
    if agents_dir.exists():
        for py_file in sorted(agents_dir.rglob("*.py")):
            if not py_file.name.startswith("__"):
                agents_list.append(py_file.stem)
    return {"agents": agents_list, "dependencies": {}}


def load_agent_spec(agent_name):
    """Level 2: Load targeted agent specifications (legacy function)"""
    agent_file = Path("dorama_studio/agents/" + agent_name + ".py")
    if agent_file.exists():
        with open(agent_file, "r", encoding="utf-8") as f:
            return f.read()
    return "# Agent spec not found: " + agent_name + ".py"


def load_cold_memory(module_name):
    """Level 3: Fetch domain-specific Cold Memory modules (legacy function)"""
    cold_file = Path("memory/cold") / module_name
    if cold_file.exists():
        with open(cold_file, "r", encoding="utf-8") as f:
            return f.read()
    return "# Cold memory module not found: " + module_name


def get_research_veo():
    """Research module for Veo 3.1 specifications (legacy function)"""
    veo_dir = Path("research") / "veo"
    if veo_dir.exists():
        files = list(veo_dir.glob("*.md"))
        return {f.name: f.read_text(encoding="utf-8") for f in files}
    return {}


def get_research_characters():
    """Research module for character standards (legacy function)"""
    char_dir = Path("research") / "characters"
    if char_dir.exists():
        files = list(char_dir.glob("*.md"))
        return {f.name: f.read_text(encoding="utf-8") for f in files}
    return {}


def get_context_level(level=0):
    """Get context at specified level (legacy function)"""
    if level == 0:
        return load_project_state()
    elif level == 1:
        idx = load_agents_index()
        proj = load_project_state()
        return "Level 1: Agents index: " + str(idx) + "\n\n" + proj
    elif level == 2:
        idx = load_agents_index()
        agents_spec = {}
        for ag in idx["agents"]:
            agents_spec[ag] = load_agent_spec(ag)
        return (
            "Level 2: Agent specifications loaded ("
            + str(len(agents_spec))
            + " agents)\n"
            + "\n---\n".join(agents_spec.values())
        )
    elif level == 3:
        modules = ["template_master.md"]
        result = {}
        for mod in modules:
            result[mod] = load_cold_memory(mod)
        return "Level 3: Cold memory modules\n" + "\n---\n".join(result.values())
    return "# Invalid level specified"


# Protocol enforcement: never load entire repository
ENABLED_LEVELS = {0, 1, 2, 3}

print("Context Router initialized - HOT/COLD protocol active")
print("Enabled levels: " + str(ENABLED_LEVELS))
