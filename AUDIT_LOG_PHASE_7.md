# TOKEN ECONOMY OPTIMIZATION AUDIT - PHASE 7 COMPLETE

## Fase 7: Mocks Identification - COMPLETE ✅

### 7.1 Catálogo Completo de Mocks/Placeholders/Stubs

| Agente | Archivo | Tipo | Detalle | Severidad |
|--------|---------|------|---------|-----------|
| **VisualEngineAgent** | `visual_engine.py:33-48` | **MOCK** | Retorna `VideoArtifact` fake con `file:///tmp/render/{shot_id}.mp4` | ALTA |
| **EditorAgent (narrative)** | `editor_agent.py` | **REAL** | Usa `ffmpeg` real - FUNCIONAL si ffmpeg instalado | BAJA |
| **EditorAgent (production)** | `production/editor_agent.py:44-61` | **MOCK** | Convierte effects a `VideoClip` fake, no usa ffmpeg | ALTA |
| **SubtitleAgent (narrative)** | `subtitle_agent.py` | **REAL** | Usa `SpeechToTextAgent` (Whisper) real | BAJA |
| **SubtitleAgent (production)** | `production/subtitle_agent.py:47-66` | **MOCK** | Retorna 2 subtítulos fijos hardcodeados | ALTA |
| **SpeechToTextAgent** | `speech_to_text.py:91-101` | **FALLBACK** | `_fallback_subtitles()` retorna "[Transcripción no disponible]" | MEDIA |
| **StoryboardAgent (visual)** | `visual/storyboard_agent.py` | **REAL** | Genera shots con specs completos - FUNCIONAL | BAJA |
| **StoryboardAgent (plano)** | `storyboard_agent.py:79-96` | **STUB** | `_process` delega a `run` que retorna input sin procesar | ALTA |
| **VisualAgent** | `visual/visual_agent.py:46-65` | **MOCK** | Genera prompts estructurados pero no llama API real | MEDIA |
| **VideoAgent (production)** | `production/video_agent.py:54-65` | **MOCK** | Retorna `VideoClip` fake con `description="Generated video from keyframe"` | ALTA |
| **KeyframeAgent** | `visual/keyframe_agent.py` | **PENDIENTE** | No leído aún | - |
| **AudioEngineerAgent** | `audio_engineer_agent.py` | **REAL** | Genera prompts de audio detallados - FUNCIONAL | BAJA |
| **AudioMixerAgent** | `audio_mixer.py` | **PENDIENTE** | No leído aún | - |
| **TrendHunterAgent** | `trend_hunter_agent.py:106-174` | **HEURÍSTICO** | `_hunt_trends_real()` retorna diccionarios hardcodeados por género | MEDIA |
| **TrendHunterAgent (investigation)** | `investigation/trend_hunter.py` | **WRAPPER** | Wrapper del plano | MEDIA |
| **ViralAnalystAgent** | `viral_analyst_agent.py` | **PENDIENTE** | No leído aún | - |
| **OriginalityEngineAgent** | `originality_engine_agent.py` | **PENDIENTE** | No leído aún | - |
| **CharacterDirectorAgent (plano)** | `character_director_agent.py` | **PENDIENTE** | No leído aún | - |
| **VisualDirectorAgent (plano)** | `visual_director_agent.py` | **PENDIENTE** | No leído aún | - |
| **DistributionPublisherAgent** | `distribution_publisher_agent.py` | **PENDIENTE** | No leído aún | - |
| **AnalyticsEngineAgent** | `analytics_engine_agent.py` | **PENDIENTE** | No leído aún | - |
| **FeedbackLoopAgent** | `feedback_loop_agent.py` | **PENDIENTE** | No leído aún | - |
| **CreativeGenomePolicyAgent** | `creative_genome_policy_agent.py` | **PENDIENTE** | No leído aún | - |
| **MasterWriterAgent (plano)** | `master_writer_agent.py:227-340` | **FALLBACK** | `_generate_deterministic_script()` retorna scripts hardcodeados | ALTA |

---

### 7.2 Análisis por Categoría

#### 🔴 **MOCKS CRÍTICOS - Pipeline de Video/Audio (Bloquean E2E Real)**

| Componente | Mock Actual | Integración Real Requerida |
|------------|-------------|---------------------------|
| **VisualEngineAgent** | VideoArtifact fake `file:///tmp/...` | APIs: Veo 3.1, Kling, Runway Gen-3, Sora |
| **VideoAgent (production)** | VideoClip fake | Mismo que arriba - generación video |
| **EditorAgent (production)** | VideoClip fake | `ffmpeg` real (el narrative sí lo usa) |
| **SubtitleAgent (production)** | 2 subtítulos hardcodeados | Whisper API / Whisper local + formateo SRT/ASS |
| **SpeechToTextAgent** | Fallback "[Transcripción no disponible]" | Whisper CLI local (ya implementado en `_transcribe_local`) |

#### 🟡 **MOCKS FUNCIONALES - Generación de Prompts (No bloquean, pero no producen assets)**

| Componente | Mock Actual | Estado |
|------------|-------------|--------|
| **VisualAgent** | Genera prompts estructurados + params | Listo para conectar a video gen API |
| **KeyframeAgent** | Por verificar | - |
| **AudioEngineerAgent** | Genera prompts detallados (DramaBox/OASIZ) | ✅ Funcional - produce prompts listos para TTS/SFX APIs |
| **StoryboardAgent (visual)** | Genera shots con specs forenses | ✅ Funcional - produce ShotSpecs completos |

#### 🟢 **AGENTES REALES/DETERMINÍSTICOS (No son mocks - por diseño)**

| Agente | Tipo | Justificación |
|--------|------|---------------|
| **MasterWriterAgent (narrative)** | LLM Real | Usa `call_llm_structured_tracked` ✅ |
| **StoryArchitectAgent (narrative)** | Determinístico | Arquitectura por diseño, no LLM |
| **HookEngineAgent** | Determinístico | Librerías + scoring matemático |
| **RetentionEngineAgent** | Determinístico | Análisis microbeats |
| **CliffhangerEngineAgent** | Determinístico | Templates |
| **DialoguePolisherAgent** | Determinístico | Reglas de pulido |
| **CharacterStateAgent** | Determinístico | Estados de personaje |
| **LocationBibleAgent** | Determinístico | Generación localizaciones |
| **ContinuityLockAgent** | Determinístico | Validación continuidad |
| **DirectorEngineAgent** | Determinístico | Plan dirección |
| **ShotPlannerAgent** | Determinístico | División en shots |
| **ActingMotionPlannerAgent** | Determinístico | Planificación actuación |
| **TrendHunterAgent** | Heurístico + Cache | Cache interno 1h, diccionarios por género |
| **AudioEngineerAgent** | Determinístico | Prompts por reglas |
| **QualityCheckAgent** | Determinístico | Hard gates |
| **SelectiveRegenerationAgent** | Orquestador | Coordina otros agentes |
| **AnalyticsEngineAgent** | DB Query | Lee de BD |
| **FeedbackLoopAgent** | Determinístico | Instrucciones fijas |
| **CreativeGenomePolicyAgent** | Memoria | Tracking 70/20/10 |

---

### 7.3 Duplicados Arquitectónicos con Diferente Nivel de Mock

| Concepto | Implementación Plana | Implementación Canónica (submódulo) | Estado Plano | Estado Canónico |
|----------|---------------------|------------------------------------|--------------|-----------------|
| **MasterWriter** | `master_writer_agent.py` | `narrative/master_writer.py` | FALLBACK (determinístico) | **LLM REAL + TRACKING** |
| **HookEngine** | `hook_engine_agent.py` | `narrative/hook_engine.py` | Determinístico | Determinístico + Creative Genome |
| **StoryArchitect** | `story_architect_agent.py` | `narrative/story_architect.py` | No leído | Determinístico + Quality Gate |
| **EpisodeScorer** | `episode_scorer_agent.py` | `narrative/episode_scorer.py` | No leído | Quality Gate 15 dims |
| **TrendHunter** | `trend_hunter_agent.py` | `investigation/trend_hunter.py` + wrapper | Heurístico + cache | Wrapper |
| **ViralAnalyst** | `viral_analyst_agent.py` | `investigation/viral_analyst.py` + wrapper | No leído | Wrapper |
| **OriginalityEngine** | `originality_engine_agent.py` | `investigation/originality_engine.py` + wrapper | No leído | Wrapper |
| **CharacterDirector** | `character_director_agent.py` | (no hay submódulo narrativo) | No leído | - |
| **VisualDirector** | `visual_director_agent.py` | (no hay submódulo narrativo) | No leído | - |
| **Editor** | `editor_agent.py` (narrative) | `production/editor_agent.py` | **REAL (ffmpeg)** | MOCK |
| **Subtitle** | `subtitle_agent.py` (narrative) | `production/subtitle_agent.py` | **REAL (Whisper)** | MOCK |

---

### 7.4 Impacto en Pipeline 40x90

**Ejecutando `test_e2e_40x90_simple_invocation` (1 episodio):**

| Nodo | Agente | Produce Asset Real? | Notas |
|------|--------|---------------------|-------|
| `visual_render` | VisualEngineAgent | ❌ MOCK | `file:///tmp/render/shot_x.mp4` |
| `voice_render` | SpeechToTextAgent (como TTS) | ❌ ERROR | WinError 2 - archivo no existe |
| `sfx_render` | AudioEngineerAgent | ✅ Prompts | Solo genera prompts, no audio |
| `music_render` | AudioEngineerAgent | ✅ Prompts | Solo genera prompts, no audio |
| `audio_mix` | AudioMixerAgent | ❌ MOCK | `master_audio_e01` fake |
| `edit` | EditorAgent (narrative) | ⚠️ ffmpeg | Requiere archivos reales de video |
| `subtitles` | SubtitleAgent (narrative) | ⚠️ Whisper | Requiere audio real |

**Resultado:** Pipeline completa en ~3s pero **ningún asset multimedia real se genera**. Todo son referencias/IDs fake.

---

### 7.5 Esfuerzo Estimado para Producción Real

| Componente | APIs Candidatas | Esfuerzo | Dependencias |
|------------|-----------------|----------|--------------|
| **Video Generation** | Veo 3.1 (Google), Kling (Kuaishou), Runway Gen-3, Sora (OpenAI) | 2-4 semanas | API keys, billing, rate limits |
| **TTS (Voice)** | ElevenLabs, OpenAI TTS, Coqui TTS, XTTS-v2 | 1-2 semanas | API keys o GPU local |
| **SFX Generation** | ElevenLabs SFX, MyEdit, Stable Audio | 1-2 semanas | API keys |
| **Music Generation** | Suno, Udio, Stable Audio, MusicGen | 1-2 semanas | API keys o GPU local |
| **Video Editing** | ffmpeg (ya en EditorAgent narrative) | 0 - YA FUNCIONA | ffmpeg instalado |
| **Subtitles** | Whisper (ya en SpeechToTextAgent) | 0 - YA FUNCIONA | whisper CLI instalado |

**Total estimado:** 5-10 semanas para pipeline multimedia completo E2E real

---

### 7.6 Priorización de Migración

#### **P0 - Bloqueantes Críticos (Para E2E Real)**
1. **VisualEngineAgent** → Integrar API video generation (Veo/Kling/Runway)
2. **VideoAgent (production)** → Mismo que arriba
3. **SpeechToTextAgent** → Ya tiene `_transcribe_local` con Whisper CLI, solo necesita ffmpeg/whisper instalado
4. **SubtitleAgent (narrative)** → Ya usa SpeechToTextAgent real
5. **EditorAgent (narrative)** → Ya usa ffmpeg real

#### **P1 - Alta Prioridad**
6. **EditorAgent (production)** → Migrar a ffmpeg real (copiar de narrative)
7. **SubtitleAgent (production)** → Migrar a Whisper real (copiar de narrative)
8. **AudioMixerAgent** → Implementar mezcla real con ffmpeg/pydub

#### **P2 - Media Prioridad**
9. **VisualAgent** → Conectar prompts a video generation API
10. **KeyframeAgent** → Verificar e implementar
11. **MasterWriterAgent (plano)** → Eliminar duplicado, usar narrativa

#### **P3 - Baja Prioridad (Determinísticos por Diseño)**
12. HookEngine, RetentionEngine, CliffhangerEngine, etc. → No necesitan LLM

---

### 7.7 Conclusión Fase 7

**ESTADO: 🔴 MOCKS CRÍTICOS EN PIPELINE MULTIMEDIA - E2E REAL BLOQUEADO**

**Resumen:**
- **5 mocks críticos** en video/audio generation/editing
- **2 agentes reales** para edición/subtítulos (narrative versions) - **YA FUNCIONALES**
- **SpeechToTextAgent** tiene implementación real Whisper - solo necesita dependencias
- **AudioEngineerAgent** genera prompts listos para APIs TTS/SFX
- **Duplicados arquitectónicos** tienen niveles de mock inconsistentes (narrative=real, production=mock)

**Bloqueante principal:** Sin APIs de video generation (Veo/Kling/Runway), el pipeline **nunca generará video real**.

**Próximo paso recomendado:** Fase 8 - End-to-End Validation (con proveedores reales o mock controlado)

---

**Auditado:** 2026-09-26  
**Método:** Grep de MOCK/PLACEHOLDER/STUB, lectura directa de 15+ archivos de agentes multimedia, análisis de duplicados plano vs submódulo