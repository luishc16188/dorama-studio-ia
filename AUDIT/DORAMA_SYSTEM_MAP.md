# DORAMA STUDIO AI — MAPA DEL SISTEMA

## VISIÓ general

```
graph TD
    %% Entrada
    IDÉA --> CONCEPTUALIZACIÓN

    %% Research Paralelo
    CONCEPTUALIZACIÓN --> TREND_HUNTER
    CONCEPTUALIZACIÓN --> VIRAL_ANALYST
    CONCEPTUALIZACIÓN --> ORIGINALITY_ENGINE

    %% Story Sequence
    ORIGINALITY_ENGINE --> STORY_ARCHITECT
    STORY_ARCHITECT --> MASTER_WRITER
    MASTER_WRITER --> HOOK_ENGINE
    HOOK_ENGINE --> DIALOGUE_POLISHER
    DIALOGUE_POLISHER --> RETENTION_ENGINE
    RETENTION_ENGINE --> CLIFFHANGER_ENGINE
    CLIFFHANGER_ENGINE --> DIRECTOR_ENGINE

    %% Character/Bible
    STORY_ARCHITECT --> CHARACTER_DIRECTOR
    CHARACTER_DIRECTOR --> LOCATION_BIBLE
    CHARACTER_DIRECTOR --> CONTINUITY_LOCK

    %% Script & Beats
    MASTER_WRITER --> BLUEPRINT
    BLUEPRINT --> SCRIPT
    DIALOGUE_POLISHER --> DIALOGUE_FINAL

    %% Media Fan-out
    SHOT_PLANNER --> PROMPT_COMPILER
    PROMPT_COMPILER --> VISUAL_ENGINE
    PROMPT_COMPILER --> SPEECH_TO_TEXT
    PROMPT_COMPILER --> AUDIO_AGENT

    %% Post-production Fan-in
    VISUAL_ENGINE --> AUDIO_MIX
    SPEECH_TO_TEXT --> AUDIO_MIX
    AUDIO_AGENT --> AUDIO_MIX
    AUDIO_MIX --> EDITOR_AGENT
    EDITOR_AGENT --> SUBTITLE_AGENT
    SUBTITLE_AGENT --> QUALITY_CHECK

    %% QC Loop
    QUALITY_CHECK --> SELECTIVE_REGENERATION
    SELECTIVE_REGENERATION --> QUALITY_CHECK

    %% Distribution
    QUALITY_CHECK --> FINAL_PACKAGING
    FINAL_PACKAGING --> ANALYTICS_ENGINE
    ANALYTICS_ENGINE --> FEEDBACK_LOOP
    FEEDBACK_LOOP --> CREATIVE_GENOME
    CREATIVE_GENOME --> NEXT_EPISODE

    %% Estado/Cache
    style LR
    classDef research fill:#bbdefb,stroke:#0b5394,stroke-width:2px
    classDef narrative fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef production fill:#ffe0b2,oxia:#bf360c,stroke-width:2px
    classDef media fill:#fff3e0,stroke:#fb8c00,stroke-width:2px
    classDef qc fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef dist fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

## ARQUITECTURA ACTUAL

### Directorios Principales

```
_dorama_studio/
├── agents/                    # 52 archivos de agentes Python
│   ├── narrative/            # 14 agentes narrativos
│   ├── visual/               # 4 agentes visuales
│   ├── audio/                # 5 agentes de audio
│   ├── production/           # 3 agentes de producción
│   ├── learning/             # 2 agentes de aprendizaje
│   ├── distribution/         # 4 agentes de distribución
│   ├── research/             # 3 agentes de investigación
│   ├── contracts/            # Esquemas y contratos
│   ├── schemas/              # 11 archivos de esquemas Pydantic
│   └── base_agent.py         # Base class para todos los agentes
├── config/                   # Configuración YAML y Python
│   ├── models.yaml           # Mapeo de modelos freellmapi (100+ modelos)
│   ├── prompts.yaml          # Prompts versionados por agente (22 agentes)
│   ├── quality.yaml          # Pesos y umbrales QA (15 dimensiones, umbral 85/75/70)
│   ├── video_prompts.yaml    # Dialectos de video por proveedor (Kling, Runway, Veo, Hailuo, Luma)
│   └── orchestration.yaml    # Configuración orquestación
├── orchestration/           # Motor LangGraph
│   ├── graph.py              # StateGraph completo (~300 nodos, 270+ aristas)
│   ├── graph_builder.py      # Constructor de grafo con _init_agents()
│   ├── orchestrator.py       # Orquestador triple (Claude + Codex + Harness)
│   ├── checkpoints.py       # CheckpointManager (SQLite + fallback memoria)
│   ├── human_in_loop.py     # Nodos HITL con aprobación humana
│   └── state.py             # Schemas Pydantic del estado (DoramaState, Episodio, Temporada)
├── data/                    # Schemas y datos compartidos
│   └── schemas.py           # Contratos Pydantic v3 (fuente de verdad de campos)
├── intelligence/           # Nuevos módulos de inteligencia (integrados desde SOURCE)
│   ├── character_brain.py    # Análisis de rasgos de personaje
│   ├── emotional_director.py # Dirección emocional de escenas
│   ├── global_trend_hunter.py # Predicción de tendencias de mercado
│   ├── hit_predictor.py      # Predicción de hits virales
│   └── global_entertainment.py # Sistema integral de entretenimiento
├── creative_genome.py       # Memoria persistente SQLite 70/20/10
├── contracts/               # Contratos tipo Pydantic entre agentes
├── pipeline/               # Utilidades de producción
│   ├── prompt_compiler.py   # Compilador de prompts por proveedor
│   └── delivery_pack.py     # Render/manifiesto de entrega
├── tests/                   # Suite de tests (110 tests pasando)
└── outputs/                 # Salidas generadas (video, audio, subtítulos)
```

### Agentes Activos (23 total)

**Narrativa (8):**
- StoryArchitectAgent - Arquitectura de historia y arcos
- MasterWriterAgent - Generación de guiones y blueprints
- HookEngineAgent - Generación de hooks explosivos (0-3s)
- RetentionEngineAgent - Análisis de retención y beats
- CliffhangerEngineAgent - Generación de cliffhangers
- DialoguePolisherAgent - Pulido de diálogos
- CTAWriterAgent - Escritura de CTA (call-to-action)
- EpisodeScorerAgent - Scoring de calidad 100pts/15 dimensiones

**Visual (4):**
- VisualAgent - Generación de prompts visuales
- KeyframeAgent - Generación de keyframes
- StoryboardAgent - Storyboards con consistencia visual
- VisualDirectorAgent - Dirección visual coherente

**Audio (5):**
- VoiceDirectorAgent - Dirección de voz y lip-sync
- SoundDesignerAgent - Diseño de SFX
- MusicSupervisorAgent - Música y BGM
- AudioMixerAgent - Mezcla de audio master
- SpeechToTextAgent - Síntesis de voz TTS

**Producción (3):**
- EditorAgent - Edición y timeline de video
- SubtitleAgent - Generación de subtítulos
- PublisherAgent - Publicación y distribución

**Investigación (3):**
- TrendHunterAgent - Investigación de tendencias virales
- ViralAnalystAgent - Análisis multidimensional viral
- OriginalityEngineAgent - Motor anti-copia/anti-plagio

**Learning (2):**
- AnalyticsEngineAgent - Métricas de performance
- FeedbackLoopAgent - Bucle de aprendizaje y mejora

**Distribution (2):**
- SEOOptimizerAgent - Optimización para plataformas
- DistributionPublisherAgent - Publicación final

### Flujo de Datos Completo

```
IDEAS
  │
  ├──► TREND_HUNTER ──┬──► VIRAL_ANALYST ──┬──► ORIGINALITY_ENGINE
  │                   │                      │
  │                   └──► ANÁLISIS VIRAL    │
  │                                              │
  └──► STORY_ARCHITECT ──► MASTER_WRITER ──► HOOK_ENGINE
                              │                   │
                              │                   ├──► DIALOGUE_POLISHER
                              │                   │
                              │                   ├──► RETENTION_ENGINE
                              │                   │
                              │                   └──► CLIFFHANGER_ENGINE
                              │
                              └──► GENERACIÓN DE BLUEPRINTS

SHOT_PLANNER ──► PROMPT_COMPILER ──► VISUAL_ENGINE ──► AUDIO_MIX ──► EDITOR_AGENT
                     │                      │                      │
                     │                      ├──► SPEECH_TO_TEXT ──►│
                     │                      ├──► AUDIO_AGENT (music)──►│
                     │                      │                      │
                     └──►──────────────────►─────────────────────┘

CONTINUIDAD ──► PERFORMANCE ──► FEEDBACK_LOOP ──► CREATIVE_GENOME ──► NEXT_EPISODE
```

### Contratos entre Agentes (Input/Output Schemas)

| De → A | Input Schema | Output Schema | Estado |
|--------|-------------|--------------|--------|
| StoryArchitect → MasterWriter | EpisodeBlueprint | Scripts + beats | ✅ Válido |
| MasterWriter → HookEngine | Script + hook_ref | Hook pack | ✅ Válido |
| HookEngine → MasterWriter | Blueprint + hook_ref | Blueprint actualizado | ✅ Válido |
| MasterWriter → DialoguePolisher | Beats | Diálogo polish | ✅ Válido |
| RetentionEngine → QC | Microbeats + episodio | Acciones de retention | ✅ Válido |
| QualityCheck → SelectiveRegeneration | QC report + episodio | Report regenerado | ✅ Válido |
| VisualEngine → PromptCompiler | Shots + motion_ref + character_refs | PromptAsts | ✅ Válido |
| PromptCompiler → VisualEngine | Prompts compilados | Shots con prompts | ✅ Válido |
| VoiceDirector → AudioMixer | Voice tracks | Capas de voz | ✅ Válido |
| SoundDesigner → AudioMixer | SFX layers | Capas de SFX | ✅ Válido |
| MusicSupervisor → AudioMixer | Music timeline | Capas de música | ✅ Válido |
| AudioMixer → EditorAgent | Tracks de audio | Master audio | ✅ Válido |
| EditorAgent → SubtitleAgent | Master audio +shots | Subtitle file | ✅ Válido |
| SubtitleAgent → QC | Master audio | Quality report | ✅ Válido |
| QC → AnalyticsEngine | Episodio + quality_score | Analytics report | ✅ Válido |
| AnalyticsEngine → FeedbackLoop | Reporte | Instrucciones de aprendizaje | ✅ Válido |
| FeedbackLoop → CreativeGenome | Instrucciones | Memoria persistente | ✅ Válido |

### Dependencias Críticas

```
BASE AGENT → Todos los agentes heredan de BaseAgent
├── InputSchema: Validación de entrada Pydantic
├── OutputSchema: Validación de salida Pydantic
├── _validate_input(): Validación y conversión
├── _process(): Lógica específica (abstract)
├── _validate_output(): Validación de salida
├── quality_gate(): Gate de 100pts/15 dimensiones
└── process(): Pipeline con validación

PROMPT COMPILER → Convierte master scene a model-specific prompts
├── Lee universal_template de video_prompts.yaml
├── Compila para cada proveedor (Kling, Runway, Veo, Hailuo, Luma)
├── Aplica negative_bank por modelo
└── Genera prompts image_to_video o text_prompt_camera_explicit

CREATIVE GENOME (SQLite) → 70/20/10 budget allocation
├── Tabla: winning - patrones ganadores
├── Tabla: overused - patrones sobreusados
├── Tabla: failed - patrones fallidos
├── Tabla: emerging - patrones emergentes
├── check_budget(): Presupuesto por categoría
├── record_mutation(): Eventos de mutación
└── record_low_quality(): Patrones low quality

LANGGRAPH STATE → Orchestration complete
├── DoramaState: Estado base (project_id, season_id, episode_id)
├── EpisodeProductionState: Episodio individual
└── SeasonProductionState: Temporada completa
```

### Puntos de Falla Detectados

1. **Convención de nombres**: `character_id` vs `characterId` en diferentes agentes
2. **Imports circulares**: Potenciales en `contract.py` y `base_agent.py`
3. **Cobertura Creative Genome**: Faltando Visual DNA completo y Audio DNA detallado
4. **Cobertura de prompts**: Algunos agentes usan prompts hardcodeados en lugar de prompt_compiler
5. **Validación QA**: Superficial - no verifica continuidad visual/audio detallada
6. **Contratos incompletos**: Algunos agentes carecen de schemas definidos explícitamente

### Próximos Pasos Automatizados

Continuaré inmediatamente con la Fase 2: Auditoría de agentes.