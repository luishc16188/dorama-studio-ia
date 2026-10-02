# DORAMA STUDIO IA DEFINITIVO

Fábrica automatizada de microdramas virales verticales (episodios de **90s** para TikTok / YouTube Shorts / Reels).

Toma una idea → investiga tendencias → crea universo + personajes + arco de temporada → genera 20 episodios con hooks, guiones, storyboards, keyframes, video, voz, música, SFX, edición, subtítulos y CTA narrativa → puntúa la calidad → publica → analiza → aprende → mejora el siguiente episodio.

## Arquitectura: 22 agentes en pipeline (LangGraph)

```
Investigación          Narrativa & Retención         Personajes        Visual
01 Trend Hunter        04 Story Architect             Character Bible   11 Storyboard Agent
02 Viral Analyst       05 Master Writer                (+Continuity)    12 Visual Agent
03 Originality Engine  06 Hook Engine                                   13 Keyframe Agent
                      07 CTA Writer
                      17 Episode Scorer (QA)

Audio                 Producción                   Distribución       Aprendizaje
14 Voice Director     18 Video Agent               20 Publisher        21 Analytics Engine
15 Sound Designer     19 Editor Agent              SEO Optimizer      22 Feedback Loop
16 Music Supervisor   Subtitle Agent
```

> Los 22 agentes están versionados en **v3.0** (ver `config/prompts.yaml`). Altas de agentes nuevas deben seguir el orden: **1) schema → 2) prompts.yaml → 3) agente Python**.

Orquestación por **LangGraph**: state machine, checkpoints (SQLite/memoria), **quality gates** con retry y feedback, **HITL** para aprobaciones y **validación cruzada** entre agentes consecutivos (storyboard→visual, keyframe→video, audio→editor). Los proveedores generativos son **intercambiables** vía adapter pattern con fallback chain (llm.py, image.py, video.py, tts.py, music.py).

## ✨ NUEVA ARQUITECTURA (v4.0 - 2026-09-18)

### 🔧 Modelo Router Inteligente (freellmapi)
- **Servidor local:** `http://127.0.0.1:31415/v1` con `freellmapi/*` models
- **100+ modelos disponibles:** Claude (Opus/Sonnet/Haiku 4.5), DeepSeek (R1/V3), Qwen, Kimi, GLM, Nemotron, Gemma, etc.
- **Budget 70/20/10 por Creative Genome:**
  - **Proven (70%):** claude-opus-4-5, claude-sonnet-4-5, deepseek-r1, gemini-3.5-flash
  - **Exploration (20%):** claude-haiku-4-5, deepseek-v3, kimi-k2.x
  - **Big Bet (10%):** freellmapi/auto, freellmapi/fusion, experimental

### 🎯 Quality Gate 100pts (15 dimensiones) - Integrado en TODOS los agentes narrativos
| Dimensión | Pts | Validación |
|-----------|-----|------------|
| Hook 0-3s (explosivo + shock visual) | 20 | ✅ BaseAgent.quality_gate() |
| Conflict concrete | 15 | ✅ |
| Protagonist desire clarified | 15 | ✅ |
| Unresolved question | 15 | ✅ |
| Situation worsens (escalation) | 15 | ✅ |
| Partial answer (reward) | 10 | ✅ |
| Surprise element (reversal) | 10 | ✅ |
| Strong cliffhanger | 10 | ✅ |
| Emotional impact | 5 | ✅ |
| Show don't tell | 5 | ✅ |
| Dialogue advances story | 5 | ✅ |
| **Bonus arquitectura** | | |
| Central secret compelling | +5 | StoryArchitect |
| Antagonist understandable | +5 | StoryArchitect |
| Genre consistency | +5 | StoryArchitect |
| Episode structure complete | +5 | StoryArchitect |

**Threshold:** ≥85/100 = PASS, <75 = REWRITE, <70 = HUMAN_REVIEW

### 🧬 Creative Genome 70/20/10 - Persistente (SQLite)
- **Base de datos:** `dorama_studio/data/creative_genome.db`
- **Tablas:** `mutation_budget`, `originality_records`, `genre_preferences`
- **Tracking por agente + semilla + género**
- **Integración:** Todos los agentes narrativos verifican presupuesto antes de ejecutar

### 📊 Viral Analyst Agent (NUEVO)
- Análisis multidimensional de contenido viral existente
- Genera `viral_ruleset` accionable para otros agentes
- Detección de mecanismos outlier (>2x engagement)
- Quality Gate aplicado al output para asegurar reglas accionables

## Estructura de episodio (90s — fórmula viral fractal)

**Fórmula maestra fractal (se repite en TODOS los niveles):**
```
H → P → Q → E → R → Q2 → C
H=Hook(0-3s) → P=Promise(3-10s) → Q=Question(10-25s) → E=Escalation(25-40s) → R=Reward(40-55s) → Q2=New Question(55-70s) → C=Cliffhanger(70-90s)
```

**9 Beats obligatorios (10s cada uno = 90s total):**

| Beat | Rango | Función Psicológica | Tensión | Pacing |
|------|-------|---------------------|---------|--------|
| 1 | 0-10s | **HOOK EXPLOSIVO** - Stop-scroll visual + pregunta | 8/10 | hyper |
| 2 | 10-20s | **CONTEXTO MÍNIMO** - Promesa + stakes concretos | 5/10 | fast |
| 3 | 20-30s | **PROBLEMA INMEDIATO** - Conflicto visceral | 6/10 | fast |
| 4 | 30-40s | **ESCALADA** - Complicación + subtrama | 7/10 | medium |
| 5 | 40-50s | **GIRO / REVELACIÓN** - Micro-payoff informativo | 8/10 | medium |
| 6 | 50-60s | **COMPLICACIÓN** - Nueva amenaza / traición | 8/10 | fast |
| 7 | 60-70s | **REVERSAL MAYOR** - Inversión de poder | 9/10 | hyper |
| 8 | 70-80s | **NUEVA INFORMACIÓN** - Pista del misterio mayor | 7/10 | medium |
| 9 | 80-90s | **CLIFFHANGER** - Ruptura sin resolución | 10/10 | hyper |

**Reglas obligatorias:**
- ✅ Rotación de cliffhangers (8 tipos, no repetir consecutivos)
- ✅ Escalada de presión monótona (Ep1:20% → Ep20:100%)
- ✅ Alternancia emocional obligatoria (60% tensión / 25% calidez / 15% humor)
- ✅ Subversión de tropo por episodio
- ✅ Fórmula fractal H→P→Q→E→R→Q2→C en cada beat

## Quickstart

```bash
poetry install

# Copia y rellena credenciales (ver .env.example)
cp .env.example .env

# (Opcional) Validación pre-deploy: 24 checks, 0 errores = deploy autorizado
python pre_deploy_check.py

# Crear temporada completa (20 episodios)
dorama-studio create-season "CEO millonario se enamora de su secretaria que es heredera oculta" --genre romance-traicion --episodes 20

# Producir un solo episodio con feedback (iteración rápida)
dorama-studio create-episode <project-id> --episode 5 --feedback "el hook del ep 4 fue débil"

# Analizar rendimiento
dorama-studio analyze <project-id> --platform tiktok

# Listar agentes
dorama-studio list-agents
```

> **Modo determinista/mock:** Sin API keys el pipeline corre con guiones, storyboards y beats generados localmente.
> **Generación real:** Configura al menos `OPENAI_API_KEY` (freellmapi server) y `ELEVENLABS_API_KEY`, y un proveedor de video (`KLING_API_KEY` / `RUNWAY_API_KEY`).

## Calidad (Episode Scorer)

100 puntos: Hook 20 · Historia 15 · Emoción 15 · Retención 15 · Personajes 10 · Visual 10 · Audio 5 · Cliffhanger 5 · CTA 5. Umbral **PASS = 85**; por debajo se reescribe automáticamente con feedback específico referido a beats/planos/líneas concretas.

## Configuración

- `config/models.yaml` — **Modelos freellmapi por tarea + fallback chain + budget 70/20/10** (actualizado v4.0)
- `config/prompts.yaml` — 22 agentes v3.0 con prompts versionados
- `config/video_prompts.yaml` — prompts por proveedor de video (Kling / Runway / Veo / Hailuo)
- `config/quality.yaml` — pesos de scoring, umbrales, reglas de continuity
- `config/genres.yaml` — 5 líneas narrativas con tropos y beats
- `config/platforms.yaml` — specs TikTok / YouTube Shorts / Reels
- `dorama_studio/data/schemas.py` — esquemas Pydantic v3.0 (fuente de verdad de campos)
- `dorama_studio/config/model_router.py` — Router inteligente freellmapi + Creative Genome
- `dorama_studio/creative_genome.py` — Persistencia SQLite 70/20/10 + originalidad
- `dorama_studio/agents/base_agent.py` — BaseAgent v5.0 con Quality Gate integrado

## Agentes Clave (v4.0)

| Agente | Archivo | Quality Gate | Creative Genome | Notas |
|--------|---------|--------------|-----------------|-------|
| **StoryArchitectAgent** | `agents/narrative/story_architect.py` | ✅ 15+4 dims | ✅ Budget check + record | Arquitectura completa con fractal formula |
| **MasterWriterAgent** | `agents/narrative/master_writer.py` | ✅ 15 dims | ⚠️ Partial | Guiones desde blueprints |
| **HookEngineAgent** | `agents/narrative/hook_engine.py` | ✅ Via BaseAgent | ✅ Novelty scoring | Hook Lab: 150 hipótesis + novelty check |
| **ViralAnalystAgent** | `agents/narrative/viral_analyst.py` | ✅ Output QG | ✅ Analysis budget | **NUEVO** - Análisis viral + ruleset |
| **EpisodeScorerAgent** | `agents/narrative/episode_scorer.py` | ✅ 15 dims | - | Pre-flight judge adversarial |

## Stack

Python 3.11+ · LangGraph · Pydantic v2 · **freellmapi local** (Claude/DeepSeek/Qwen/Kimi/GLM/...) · Imagen 3 / Flux / DALL-E (imagen) · Kling / Runway / Veo / Hailuo (video) · ElevenLabs (voz) · Suno + Epidemic Sound (música) · MoviePy / FFmpeg (edición).

## Documentación técnica

Ver `docs/`: `ARQUITECTURA_TECNICA.md`, `FLUJO_DATOS_ENTRE_AGENTES.md`, `CAMPOS_SCHEMA_V3.md`, `VALIDACION_CRUZADA_AGENTES.md`, `DEBUGGING_GUIDE.md`.

## Limpieza del proyecto (v4.0)

- ✅ **30+ archivos `fix_*.py` archivados** en `archive/fixes/`
- ✅ Directorio raíz limpio: solo archivos esenciales
- ✅ Tests pasando: 5/5 (pytest)
- ✅ Configuración freellmapi completa y validada

## Conventions

- **Coding style**: PEP 8 con `black` como formateador y `isort` para imports.
- **Type hints**: Siempre que sea posible usar `typing` y pydantic.
- **Logging**: Uso de `logging` con formato JSON (`JsonFormatter` en `base_agent.py`).
- **Testing**: Los tests deben usar `pytest` + `pytest-asyncio`, con `uvicorn` para integraciones.
- **Version control**: `git commit -m "..."` con mensajes claros.
- **Docstrings**: Triple quotes con descripción, argumentos y retorno.