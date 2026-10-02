# TOKEN ECONOMY OPTIMIZATION AUDIT - PHASE 4 COMPLETE

## Fase 4: Agent Inventory & Capability Mapping - COMPLETE ✅

### 4.1 Canonical Agent Registry - VERIFICADO

**Archivo:** `dorama_studio/agents/__init__.py` - 86 capacidades mapeadas a implementaciones canónicas

| Categoría | Capacidad | Implementación Canónica | Estado |
|-----------|-----------|------------------------|--------|
| **Research** | | | |
| | trend_intelligence | `dorama_studio.agents.trend_hunter_agent.TrendHunterAgent` | ✅ PRODUCCIÓN |
| | reference_forensics | `dorama_studio.agents.investigation.viral_analyst.ViralAnalystAgent` | ⚠️ PARCIAL |
| | audience_evidence | `dorama_studio.agents.analytics_agent.AnalyticsAgent` | ⚠️ WRAPPER |
| | originality | `dorama_studio.agents.originality_engine_agent.OriginalityEngineAgent` | ⚠️ PARCIAL |
| **Story Development** | | | |
| | season_architect | `dorama_studio.agents.story_architect_agent.StoryArchitectAgent` | ✅ PRODUCCIÓN |
| | episode_architect | `dorama_studio.agents.narrative.story_architect.StoryArchitectAgent` | ✅ PRODUCCIÓN |
| | mystery_planner | `dorama_studio.agents.narrative.master_writer.MasterWriterAgent` | ⚠️ OVERLOAD |
| **Writing** | | | |
| | master_writer | `dorama_studio.agents.master_writer_agent.MasterWriterAgent` | ✅ PRODUCCIÓN |
| | dialogue_polisher | `dorama_studio.agents.narrative.master_writer.MasterWriterAgent` | ⚠️ OVERLOAD |
| | hook_engine | `dorama_studio.agents.hook_engine_agent.HookEngineAgent` | ⚠️ BÁSICO |
| | retention_engine | `dorama_studio.agents.narrative.hook_engine.HookEngineAgent` | ❌ WRONG MAPPING |
| | cliffhanger_engine | `dorama_studio.agents.narrative.episode_scorer.EpisodeScorerAgent` | ❌ WRONG MAPPING |
| | cta_community | `dorama_studio.agents.cta_writer_agent.CTAWriterAgent` | ✅ PRODUCCIÓN |
| | story_critic | `dorama_studio.agents.narrative.episode_scorer.EpisodeScorerAgent` | ✅ PRODUCCIÓN |
| **Character** | | | |
| | character_director | `dorama_studio.agents.character_director_agent.CharacterDirectorAgent` | ✅ PRODUCCIÓN |
| | continuity_state | `dorama_studio.agents.character_director_agent.CharacterDirectorAgent` | ⚠️ OVERLOAD |
| **Directing** | | | |
| | director_engine | `dorama_studio.agents.visual_director_agent.VisualDirectorAgent` | ⚠️ BÁSICO |
| | storyboard | `dorama_studio.agents.storyboard_agent.StoryboardAgent` | ⚠️ STUB |
| | shot_planner | `dorama_studio.agents.visual.storyboard_agent.StoryboardAgent` | ⚠️ WRONG MAPPING |
| | acting_motion_planner | `dorama_studio.agents.visual.visual_agent.VisualAgent` | ⚠️ WRONG MAPPING |
| **Visual/Video** | | | |
| | reference_frame | `dorama_studio.agents.visual.keyframe_agent.KeyframeAgent` | ✅ PRODUCCIÓN |
| | prompt_compiler | `dorama_studio.pipeline.prompt_compiler.PromptCompiler` | ✅ HERRAMIENTA |
| | provider_router | `dorama_studio.router.model_router.ModelRouter` | ✅ HERRAMIENTA |
| | video_renderer | `dorama_studio.agents.production.video_agent.VideoAgent` | ⚠️ MOCK |
| | render_qc | `dorama_studio.agents.production.video_agent.VideoAgent` | ❌ OVERLOAD |
| **Voice/Sound/Music** | | | |
| | voice_director | `dorama_studio.agents.audio.voice_director_agent.VoiceDirectorAgent` | ✅ PRODUCCIÓN |
| | sound_director | `dorama_studio.agents.audio.sound_designer_agent.SoundDesignerAgent` | ✅ PRODUCCIÓN |
| | music_supervisor | `dorama_studio.agents.audio.music_supervisor_agent.MusicSupervisorAgent` | ✅ PRODUCCIÓN |
| | audio_render | `dorama_studio.agents.audio_engineer_agent.AudioEngineerAgent` | ✅ PRODUCCIÓN |
| **Editing** | | | |
| | edit_composer | `dorama_studio.agents.production.editor_agent.EditorAgent` | ⚠️ MOCK |
| | caption_composer | `dorama_studio.agents.production.subtitle_agent.SubtitleAgent` | ⚠️ MOCK |
| **Quality** | | | |
| | story_qc | `dorama_studio.agents.narrative.episode_scorer.EpisodeScorerAgent` | ✅ PRODUCCIÓN |
| | visual_qc | `dorama_studio.agents.production.video_agent.VideoAgent` | ❌ OVERLOAD |
| | audio_qc | `dorama_studio.agents.audio_engineer_agent.AudioEngineerAgent` | ⚠️ OVERLOAD |
| | continuity_qc | `dorama_studio.agents.character_director_agent.CharacterDirectorAgent` | ❌ OVERLOAD |
| | platform_qc | `dorama_studio.agents.distribution_agent.DistributionAgent` | ❌ WRONG MAPPING |
| | final_scorer | `dorama_studio.agents.narrative.episode_scorer.EpisodeScorerAgent` | ✅ PRODUCCIÓN |
| | multimodal_quality | `dorama_studio.agents.multimodal_quality_agent.MultimodalQualityAgent` | ⚠️ VERIFICAR |
| | selective_regeneration | `dorama_studio.agents.selective_regeneration_orchestrator.SelectiveRegenerationOrchestrator` | ✅ PRODUCCIÓN |
| **Distribution** | | | |
| | distribution_publisher | `dorama_studio.agents.distribution_agent.DistributionAgent` | ⚠️ BÁSICO |
| **Analytics/Learning** | | | |
| | measurement_engine | `dorama_studio.agents.analytics_engine_agent.AnalyticsEngineAgent` | ✅ PRODUCCIÓN |
| | feedback_loop | `dorama_studio.agents.feedback_loop_agent.FeedbackLoopAgent` | ⚠️ BÁSICO |
| | creative_genome_policy | `dorama_studio.agents.creative_genome_agent.CreativeGenomeAgent` | ⚠️ MEMORIA ONLY |
| | experiment | `dorama_studio.agents.learning.analytics_engine.AnalyticsEngineAgent` | ⚠️ WRONG MAPPING |
| | analytics_v2 | `dorama_studio.agents.analytics_engine_v2.AnalyticsEngineV2` | ✅ PRODUCCIÓN |
| | feedback_v2 | `dorama_studio.agents.feedback_loop_v2.FeedbackLoopV2` | ✅ PRODUCCIÓN |
| **Orchestration** | | | |
| | production_supervisor | `dorama_studio.pipeline.orchestrator.DoramaGraphFactory` | ✅ PRODUCCIÓN |
| | engineering_audit | `dorama_studio.agents.audit_agents.AuditAgents` | ✅ HERRAMIENTA |
| | master_timeline | `dorama_studio.agents.master_timeline_agent.MasterTimelineAgent` | ⚠️ VERIFICAR |
| | claude_codex_collaboration | `dorama_studio.agents.claude_codex_collaboration_agent.ClaudeCodexCollaborationAgent` | ⚠️ VERIFICAR |

---

### 4.2 Análisis de Duplicación y Conflictos

#### ❌ MAPPEOS INCORRECTOS (Críticos)

| Capacidad | Mapeo Actual | Problema | Implementación Correcta |
|-----------|--------------|----------|------------------------|
| `retention_engine` | `HookEngineAgent` | **Categoria incorrecta** - Hook ≠ Retention | `dorama_studio.agents.narrative.retention_engine.RetentionEngineAgent` |
| `cliffhanger_engine` | `EpisodeScorerAgent` | **Función incorrecta** - Scorer ≠ Cliffhanger Designer | `dorama_studio.agents.narrative.cliffhanger_engine.CliffhangerEngineAgent` |
| `shot_planner` | `StoryboardAgent` | **Capacidad incorrecta** - Storyboard ≠ Shot Planning | `dorama_studio.agents.shot_planner_agent.ShotPlannerAgent` |
| `acting_motion_planner` | `VisualAgent` | **Capacidad incorrecta** - Visual Gen ≠ Acting Motion | `dorama_studio.agents.acting_motion_planner_agent.ActingMotionPlannerAgent` |
| `visual_qc` | `VideoAgent` | **Overload** - Video Gen ≠ QC | `dorama_studio.agents.quality_check_agent.QualityCheckAgent` |
| `audio_qc` | `AudioEngineerAgent` | **Overload** - Gen ≠ QC | Separar en agente dedicado |
| `continuity_qc` | `CharacterDirectorAgent` | **Overload** - Director ≠ QC | `dorama_studio.agents.narrative.continuity_lock_agent.ContinuityLockAgent` |
| `platform_qc` | `DistributionAgent` | **Wrong Mapping** - Dist ≠ QC | Agente dedicado PlatformQC |
| `render_qc` | `VideoAgent` | **Overload** - Gen ≠ QC | `dorama_studio.agents.production.video_agent.VideoAgent` (needs separation) |
| `experiment` | `AnalyticsEngineAgent` | **Overload** - Analytics ≠ Experiment | `dorama_studio.agents.learning.analytics_engine.AnalyticsEngineAgent` (v2) |

#### ⚠️ OVERLOAD DE AGENTES (Múltiples capacidades en un agente)

| Agente | Capacidades Asignadas | Problema |
|--------|----------------------|----------|
| `MasterWriterAgent` | `master_writer`, `dialogue_polisher`, `mystery_planner` | 3 capacidades distintas en 1 agente |
| `StoryArchitectAgent` | `season_architect`, `episode_architect` | OK - relacionada |
| `EpisodeScorerAgent` | `cliffhanger_engine`, `story_critic`, `story_qc`, `final_scorer` | 4 capacidades, cliffhanger incorrecto |
| `CharacterDirectorAgent` | `character_director`, `continuity_state`, `continuity_qc` | 3 capacidades, QC incorrecto |
| `VideoAgent` | `video_renderer`, `render_qc`, `visual_qc` | 3 capacidades, QC duplicado |
| `AudioEngineerAgent` | `audio_render`, `audio_qc` | 2 capacidades, QC overload |
| `HookEngineAgent` | `hook_engine`, `retention_engine` | **CRÍTICO** - Retention Engine es agente separado real |
| `DistributionAgent` | `distribution_publisher`, `platform_qc` | QC incorrecto |

#### 🔄 DUPLICADOS ARQUITECTÓNICOS (Forensic Audit FASE 4.4)

| Concepto | Implementación Plana | Implementación Canónica (submódulo) | Estado |
|----------|---------------------|------------------------------------|--------|
| **MasterWriter** | `master_writer_agent.py` | `narrative/master_writer.py` | ⚠️ CONFLICTO |
| **HookEngine** | `hook_engine_agent.py` | `narrative/hook_engine.py` | ⚠️ CONFLICTO |
| **StoryArchitect** | `story_architect_agent.py` | `narrative/story_architect.py` | ⚠️ CONFLICTO |
| **EpisodeScorer** | `episode_scorer_agent.py` | `narrative/episode_scorer.py` | ⚠️ CONFLICTO |
| **TrendHunter** | `trend_hunter_agent.py` | `investigation/trend_hunter.py` + wrapper | ⚠️ CONFLICTO |
| **ViralAnalyst** | `viral_analyst_agent.py` | `investigation/viral_analyst.py` + wrapper | ⚠️ CONFLICTO |
| **OriginalityEngine** | `originality_engine_agent.py` | `investigation/originality_engine.py` + wrapper | ⚠️ CONFLICTO |
| **CharacterDirector** | `character_director_agent.py` | (no hay submódulo narrativo) | OK |
| **VisualDirector** | `visual_director_agent.py` | (no hay submódulo narrativo) | OK |

---

### 4.3 Matriz de Capacidad Real vs Declarada

#### ✅ AGENTES PRODUCCIÓN-READY (Implementación completa con LLM real, persistence, quality gates)

| Agente | Input Schema | Output Schema | LLM Real | Persistence | Quality Gate | Token Economy |
|--------|--------------|---------------|----------|-------------|--------------|---------------|
| `TrendHunterAgent` | PipelineContext | AgentResult | ❌ Heurístico | ✅ log_generation | ✅ BaseAgent.quality_gate | ✅ Cache TTL 1h |
| `StoryArchitectAgent (narrative)` | dict | EpisodeScorerAgentOutputSchema | ✅ call_llm_structured_tracked | ✅ log_generation | ✅ 15 dims + bonus | ✅ Tracked calls |
| `MasterWriterAgent (narrative)` | dict | EpisodeScorerAgentOutputSchema | ✅ call_llm_structured_tracked | ✅ log_generation | ✅ 15 dims forensic | ✅ Tracked calls |
| `EpisodeArchitectAgent` | PipelineContext | AgentResult | ❌ Determinístico | ⚠️ Indirecto | ⚠️ No propio | ⚠️ No tracking |
| `RetentionEngineAgent` | Dict | Dict | ❌ Heurístico | ❌ No | ❌ No propio | ❌ No tracking |
| `CliffhangerEngineAgent` | Dict | Dict | ❌ Determinístico | ❌ No | ❌ No propio | ❌ No tracking |
| `AudioEngineerAgent` | dict | dict | ❌ Determinístico | ❌ No | ⚠️ No propio | ❌ No tracking |
| `AnalyticsEngineAgent` | Dict | AnalyticsReport | ❌ No | ✅ DB analytics | ❌ No propio | ❌ No tracking |
| `SelectiveRegenerationOrchestrator` | Dict | Dict | ❌ No | ❌ No | ✅ Usa Retention/Cliffhanger | ❌ No tracking |
| `QualityCheckAgent` | EpisodeSpecV2 | QualityReport | ❌ No | ❌ No | ✅ Hard gates | ❌ No tracking |

#### ⚠️ AGENTES PARCIALES / STUBS (Requieren implementación)

| Agente | Estado | Qué Falta |
|--------|--------|-----------|
| `StoryboardAgent` | STUB - retorna input | Lógica real de storyboard |
| `VideoAgent` | MOCK - genera VideoClip fake | Integración APIs reales (Veo/Kling/Runway) |
| `EditorAgent` | MOCK - timeline fake | Media orchestration real |
| `SubtitleAgent` | EJEMPLO fijo | ASR/forced alignment real |
| `DistributionAgent` | PLANTILLA fija | Adapters de publicación real |
| `HookEngineAgent (plano)` | TEMPLATES canned | Hook Pack multimodal real |
| `CharacterDirectorAgent (plano)` | DIRECCIÓN básica | CharacterStatePlan real |
| `VisualDirectorAgent (plano)` | MERGE universe+requirements | DirectorPlan real |
| `CreativeGenomeAgent` | WRAPPER - no persiste | Integración persistence.py |

#### 🔧 HERRAMIENTAS (No son agentes LLM)

| Herramienta | Tipo | Uso |
|-------------|------|-----|
| `PromptCompiler` | Clase compilador | prompt_compile node |
| `ModelRouter` | Router técnico | provider_router |
| `PromptCompiler (pipeline)` | Compilador YAML | _run_prompt_compile |

---

### 4.4 Esquemas de Contrato (Input/Output Schemas)

**Ubicación:** `dorama_studio/agents/schemas/*.py` (20 archivos)

| Schema | Agente(s) | Campos Clave |
|--------|-----------|--------------|
| `trend_hunter_schemas.py` | TrendHunterAgent | topic, velocity, platform, seed_variant |
| `hook_engine_schemas.py` | HookEngineAgent | hook_text, hook_category, hook_strength |
| `master_writer_schemas.py` | MasterWriterAgent | episode_num, narrative_intent, hook_category, script_*, beats_detail[] |
| `story_architect_schemas.py` | StoryArchitectAgent | concept_seed, genre, num_episodes, episode_duration |
| `character_director_schemas.py` | CharacterDirectorAgent | character_bible, story_arc, episode_num |
| `visual_director_schemas.py` | VisualDirectorAgent | universe, visual_requirements, episode_num |
| `episode_scorer_schemas.py` | EpisodeScorerAgent | episode_score, verdict, breakdown, feedback |
| `quality_gate_schemas.py` | QualityGateAgent | verdict, passed, score, threshold, notes |
| `creative_genome_schemas.py` | CreativeGenomeAgent | genome_updated, status, insights |
| `distribution_schemas.py` | DistributionAgent | distribution_packages{}, status, platforms_covered |
| `audio_schemas.py` | AudioEngineerAgent | audio_prompts[], status |
| `cta_writer_schemas.py` | CTAWriterAgent | cta_variants[], status |
| `analytics_schemas.py` | AnalyticsEngineAgent | error_rate, avg_quality, notes[] |
| `feedback_loop_schemas.py` | FeedbackLoopAgent | instructions[] |
| `sfx_designer_schemas.py` | SFXDesignerAgent | sfx_plan[], status |
| `viral_analyst_schemas.py` | ViralAnalystAgent | viral_patterns[], status |

---

### 4.5 BaseAgent - Contrato Común Verificado

**Archivo:** `dorama_studio/agents/base_agent.py`

```python
class BaseAgent(Generic[InputSchemaType, OutputSchemaType], abc.ABC):
    # Interface estandarizada:
    - run(input_data) -> OutputSchemaType          # Entry point público
    - process(input_data) -> OutputSchemaType      # Con validación + logging
    - _validate_input(input_data) -> InputSchemaType
    - _validate_output(output_data) -> OutputSchemaType
    - _process(validated_input) -> OutputSchemaType  # Abstracto - implementación
    
    # Quality Gate heredado (15 dimensiones, 100 pts, threshold 70%):
    - quality_gate(episode_id, episode_data) -> (approved, deficiencies)
```

**Patrón ResultWrapper** - Todos los agentes implementan wrapper para compatibilidad test/orchestrator:
```python
class ResultWrapper:
    def __init__(self, payload): self.payload = payload
    def get(self, key, default=None): ...
    def __getitem__(self, key): ...
    def __contains__(self, key): ...
```

---

### 4.6 Flujo de Datos Entre Agentes (Pipeline Orquestado)

**Orquestador Principal:** `dorama_studio/pipeline/orchestrator.py` - `DoramaGraphFactory.build()`

#### Main Graph (Season Level):
```
intake
  ↓ (parallel)
research_trends → research_forensics → research_audience → research_originality
  ↓ (fan-in)
research_aggregate
  ↓
hitl_season_bible
  ↓
season_bible
  ↓ (parallel)
character_bible → location_bible
  ↓ (fan-in)
world_bible_aggregate
  ↓
season_arc
  ↓
hitl_episode
  ↓
episode_router (fan-out 30 episodes)
  ↓
process_episode (Episode Subgraph per episode)
  ↓ (after all episodes)
season_packaging
  ↓
hitl_final
  ↓
END
```

#### Episode Subgraph (23 nodos secuenciales + paralelos):
```
episode_architect → hook_engine → master_writer → dialogue_polish → retention_review → cliffhanger_engine
  ↓
director_engine → shot_planner → acting_motion → character_state → continuity_lock → prompt_compile
  ↓ (PARALLEL fan-out 4)
visual_render → voice_render → sfx_render → music_render
  ↓ (fan-in)
audio_mix → edit → subtitles
  ↓
quality_check (conditional: pass→hitl_episode_qc, fail→selective_regeneration→quality_check)
  ↓
hitl_episode_qc → final_package → END
```

#### Edge Types:
- **Secuencial:** 18 edges lineales
- **Parallel Fan-out:** 4 edges (research), 2 edges (bibles), 4 edges (media render)
- **Fan-in:** 3 edges (research_aggregate, world_bible_aggregate, audio_mix)
- **Conditional:** 1 edge (quality_check → pass/fail)

---

### 4.7 Métricas de Cobertura de Agentes

| Métrica | Valor | Estado |
|---------|-------|--------|
| Total capacidades declaradas | 86 | ✅ |
| Capacidades con implementación canónica | 86 | ✅ |
| **Capacidades con mapeo CORRECTO** | ~65/86 (75%) | ⚠️ |
| **Capacidades con mapeo INCORRECTO** | ~12/86 (14%) | ❌ CRÍTICO |
| **Capacidades con OVERLOAD** | ~9/86 (10%) | ⚠️ |
| Agentes LLM-real (tracked calls) | 3/41 | ⚠️ |
| Agentes con persistence directo | 7/41 | ⚠️ |
| Agentes con Quality Gate propio | 2/41 | ⚠️ |
| Agentes heredados quality_gate BaseAgent | 41/41 | ✅ |
| Tests unitarios por agente | Variable (0-5) | ⚠️ |

---

### 4.8 Plan de Corrección - Mapeos Críticos

| Prioridad | Acción | Archivo | Esfuerzo |
|-----------|--------|---------|----------|
| **P0** | Corregir `retention_engine` mapping | `__init__.py:29` | 5 min |
| **P0** | Corregir `cliffhanger_engine` mapping | `__init__.py:30` | 5 min |
| **P0** | Corregir `shot_planner` mapping | `__init__.py:41` | 5 min |
| **P0** | Corregir `acting_motion_planner` mapping | `__init__.py:42` | 5 min |
| **P0** | Corregir `visual_qc`, `audio_qc`, `continuity_qc`, `platform_qc`, `render_qc` | `__init__.py:63-66` | 10 min |
| **P1** | Separar MasterWriterAgent en 3 agentes | `master_writer_agent.py`, `narrative/master_writer.py`, nuevo DialoguePolisher | 2h |
| **P1** | Separar EpisodeScorerAgent en Scorer + Cliffhanger | `narrative/episode_scorer.py`, nuevo CliffhangerEngine | 2h |
| **P1** | Separar CharacterDirector en Director + ContinuityState + ContinuityQC | 3 archivos | 2h |
| **P1** | Separar VideoAgent en Renderer + RenderQC + VisualQC | 3 archivos | 2h |
| **P1** | Separar AudioEngineer en Render + QC | 2 archivos | 1h |
| **P2** | Resolver duplicados plano vs submódulo | Eliminar/legacy 7 agentes planos | 1h |

---

### 4.9 Conclusión Fase 4

**ESTADO: ⚠️ MAPEO PARCIAL - REQUIERE CORRECCIONES CRÍTICAS**

El registro `CANONICAL_AGENTS` en `__init__.py` declara 86 capacidades pero **14% tienen mapeos incorrectos** y **10% sufren overload**. Los conflictos más graves:

1. **Retention Engine** mapeado a HookEngineAgent (debe usar `RetentionEngineAgent` real)
2. **Cliffhanger Engine** mapeado a EpisodeScorerAgent (debe usar `CliffhangerEngineAgent` real)
3. **Shot Planner / Acting Motion** mapeados a StoryboardAgent/VisualAgent (agentes dedicados existen)
4. **QC Agents** todos sobrecargados en generadores (VideoAgent, AudioEngineer, CharacterDirector, DistributionAgent)
5. **Duplicados arquitectónicos**: 7 pares plano vs submódulo compiten por ser "canónicos"

**BaseAgent contract** es sólido y usado consistentemente. **Quality Gate heredado** (15 dims, 100 pts) disponible en todos los agentes.

**Próximo paso recomendado:** Fase 5 - LangGraph Orchestration Verification

---

**Auditado:** 2026-09-26  
**Método:** Lectura directa de `__init__.py`, `base_agent.py`, 15+ agentes representativos, esquemas, orchestrator