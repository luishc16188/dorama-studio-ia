# TOKEN ECONOMY OPTIMIZATION AUDIT - PHASE 0 BASELINE COMPLETE

## Baseline Verification Complete

### Entry Points Identified:
- `dorama_studio/cli/main.py` - CLI entry point (line 1)
- `dorama_studio/cli/pipeline.py` - Pipeline CLI commands
- `dorama_studio/pipeline/benchmark_token_economy.py` - Benchmark script
- `dorama_studio/tests/test_e2e_40x90.py` - 40x90 smoke test
- `dorama_studio/tests/test_token_economy.py` - Token economy unit tests

### Orchestrator Principal:
- `dorama_studio/pipeline/orchestrator.py` - `DoramaGraphFactory.build()` line 112-191
- Primary graph with main nodes + episode subgraph with 23 nodes

### LangGraph Graphs/Subgraphs:
- Main graph: intake → research (parallel) → season bible → character/world bibles → season arc → episode router → episode subgraph → season packaging → HITL → END
- Episode subgraph: episode_architect → hook_engine → master_writer → dialogue_polish → retention → cliffhanger → director_engine → shot_planner → acting_motion → character_state → continuity_lock → prompt_compile → visual_render/voice_render/sfx_render/music_render → audio_mix → edit → subtitles → quality_check → selective_regeneration → HITL → final_package → END
- Uses `InMemorySaver` checkpoint

### Main State:
- `dorama_studio/core/state.py` - `DoramaState`, `EpisodeProductionState`, `SeasonProductionState`
- All fields use `Annotated` with custom `merge_*` reducers for parallel node updates

### Agent Registration/Registry:
- `dorama_studio/pipeline/orchestrator.py` - `DoramaGraphFactory._init_agents()` lines 60-105
- 41 agents imported and initialized
- Most agents inherit from `BaseAgent`

### PromptContextBuilder Location:
- `dorama_studio/core/prompt_context.py` - Complete implementation with hierarchical context

### LLM Client:
- `dorama_studio/llm_client.py` - Functions `call_llm`, `call_llm_structured`, `call_llm_tracked`, `call_llm_structured_tracked`

### Token Economy System:
- `dorama_studio/core/token_usage.py` - TokenUsage, TokenUsageReport, TokenTracker
- `dorama_studio/core/cache.py` - MultiLevelCache, IdempotencyManager, CacheEntry
- `dorama_studio/core/prompt_context.py` - PromptContextBuilder with budgets
- `dorama_studio/core/agent_handoff.py` - AgentHandoffSchema, HandoffRegistry

### Tests Principal:
- `dorama_studio/tests/test_token_economy.py` - 46 unit tests
- `dorama_studio/tests/test_e2e_40x90.py` - 2 smoke tests (40x90)
- `dorama_studio/tests/test_all_agents.py` - Tests de agentes (pending verification)

---

## FASE 0 COMPLETE - Baseline established successfully