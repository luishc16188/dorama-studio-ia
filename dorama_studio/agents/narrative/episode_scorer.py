# dorama_studio/agents/narrative/episode_scorer.py
"""
Episode Scorer Agent v4.0 - Pre-Flight Judge + Adversarial Scorer.
Evalúa el GUION ANTES de producir video con rúbrica 100 pts enfocada en diálogo viral.
Implementa simulador adversarial (como espectador con TDAH) y hard-fails automáticos.
"""

import json
import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.knowledge_ledger import knowledge_ledger, KnowledgeState
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)


class EpisodeScorerAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    def __init__(self):
        super().__init__("EpisodeScorerAgent")

    def _process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process method required by BaseAgent."""
        return self.score_episode(input_data)

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the episode scorer agent."""
        result = self.process(input_data)
        # Return dict-like object with payload attribute for test compatibility
        class ResultWrapper:
            def __init__(self, payload):
                self.payload = payload
            def get(self, key, default=None):
                if isinstance(self.payload, dict):
                    return self.payload.get(key, default)
                return default
            def __getitem__(self, key):
                if isinstance(self.payload, dict):
                    return self.payload[key]
                raise KeyError(key)
            def __contains__(self, key):
                if isinstance(self.payload, dict):
                    return key in self.payload
                return False
        return ResultWrapper(result)

    def score_episode(
        self, episode_package: dict[str, Any], total_prev_score: float = 0.0
    ) -> dict[str, Any]:
        """
        Evalúa el episodio completo usando rúbrica forense y simulador adversarial.
        Returns dict con total_score, passed, hard_fails, scores_breakdown, feedback_items, y rewrite_instructions.
        """
        logger.info("Starting pre-flight adversarial scoring")

        # 1. VALIDACIÓN DE HARD FAILS (automáticos, score = 0 si alguno ocurre)
        hard_fails = self._check_hard_fails(episode_package)
        if hard_fails:
            logger.warning(f"Hard fails detected: {hard_fails}")
            return {
                "total_score": 0.0,
                "passed": False,
                "hard_fails": hard_fails,
                "scores_breakdown": {},
                "feedback_items": [],
                "verdict": EpisodeVerdict.REWRITE.value,
                "rewrite_instructions": "HARD FAIL DETECTED: Rechazar guion inmediatamente. Fixes requeridos: "
                + "; ".join(hard_fails),
            }

        # 2. SCORING NORMAL (rúbrica 100 pts)
        scores_breakdown = self._score_rubric(episode_package)

        # 3. SIMULADOR ADVERSARIAL (como espectador con TDAH)
        adhd_penalty = self._adhd_simulation_penalty(episode_package)
        total_score = sum(scores_breakdown.values()) - adhd_penalty
        total_score = max(0.0, min(100.0, total_score))  # clamp

        # 4. GENERAR FEEDBACK ITEMS (si score < 85 o para mejora)
        feedback_items = []
        if total_score < 85.0:
            feedback_items = self._generate_detailed_feedback(
                episode_package, scores_breakdown
            )
        else:
            # Incluso si pasa, dar feedback para optimización (ej: subir de 85 a 90+)
            feedback_items = self._generate_optimization_feedback(
                episode_package, scores_breakdown
            )

        # 5. DETERMINAR VERDICTO
        if total_score >= 85.0:
            verdict = EpisodeVerdict.PASS
        elif total_score >= 70.0:
            verdict = EpisodeVerdict.HUMAN_REVIEW
        else:
            verdict = EpisodeVerdict.REWRITE

        # 6. REWRITE INSTRUCTIONS
        rewrite_instructions = self._generate_rewrite_instructions(
            feedback_items, verdict
        )

        logger.info(
            f"Scoring complete: {total_score:.1f}/100, verdict: {verdict.value}"
        )

        return {
            "total_score": round(total_score, 1),
            "passed": verdict == EpisodeVerdict.PASS,
            "hard_fails": hard_fails,
            "scores_breakdown": scores_breakdown,
            "feedback_items": feedback_items,
            "verdict": verdict.value,
            "rewrite_instructions": rewrite_instructions,
        }
        # Record scoring event in Knowledge Ledger
        try:
            knowledge_ledger.acquire_knowledge(
                character_id="episode_scorer",
                knowledge_type="episode_scored",
                knowledge_state=KnowledgeState.PROVED,
                source=KnowledgeSource.DIRECT,
                source_reference=f"episode_{episode_package.get('episode_id', 'unknown')}",
                confidence=1.0,
                context={
                    "total_score": total_score,
                    "verdict": verdict.value,
                    "beats_count": len(episode_package.get("beats", []))
                }
            )
        except Exception as e:
            logger.warning(f"Knowledge Ledger record error: {e}")

    # -------------------- HARD FAILS --------------------
    def _check_hard_fails(self, episode_package: dict[str, Any]) -> list[str]:
        """
        Revisa condiciones que hacen automáticamente inválido el guion (score = 0).
        Basado en reglas no negociables del sistema.
        """
        fails = []

        beats = episode_package.get("beats", [])
        if not isinstance(beats, list) or len(beats) != 9:
            fails.append(
                "Debe haber exactamente 9 beats (actual: {})".format(
                    len(beats) if isinstance(beats, list) else "invalid"
                )
            )
            return fails  # temprano si no hay 9 beats

        # Revisar cada beat
        for i, beat in enumerate(beats):
            beat_name = [
                "Hook",
                "Context",
                "Problem",
                "Escalation",
                "Twist1",
                "Conflict2",
                "Revelation",
                "Cliffhanger",
                "CTA",
            ][i]

            # 1. CADA beat TIENE diálogo obligatorio
            dialogue = beat.get("dialogue", "")
            if not dialogue or not isinstance(dialogue, str) or dialogue.strip() == "":
                fails.append(f"Beat {i+1} ({beat_name}): Diálogo faltante o vacío")
                continue

            # 2. Diálogo MÁXIMO 15 palabras, español latino natural
            words = dialogue.split()
            if len(words) > 15:
                fails.append(
                    f"Beat {i+1} ({beat_name}): Diálogo demasiado largo ({len(words)} palabras, máximo 15)"
                )

            # 3. CERO exposición pasiva (detectar palabras como "siente", "está", etc.)
            expositive_indicators = [
                "siente",
                "está",
                "parece",
                "parecía",
                "cree",
                "piensa",
                "opina",
                "considera",
            ]
            dialogue_lower = dialogue.lower()
            if any(indicator in dialogue_lower for indicator in expositive_indicators):
                # Pero permitir si es parte de un doble filo o contexto permitido (más complejo)
                # Por ahora, marcar como warning, no hard fail (se maneja en scoring)
                pass

            # 4. Twist1 (beat 5, índice 4) DEBE incluir subversion_applied explícito
            if i == 4:  # Twist1
                subversion = beat.get("subversion_applied", "")
                if (
                    not subversion
                    or not isinstance(subversion, str)
                    or subversion.strip() == ""
                ):
                    fails.append("Beat 5 (Twist1): subversion_applied faltante o vacío")

            # 5. Cliffhanger (beat 8, índice 7) DEBE terminar EN MEDIO de una frase (corte abrupto)
            if i == 7:  # Cliffhanger
                # Revisar si el diálogo termina con puntuación de continuidad (., !, ?) sin indicador de corte
                # En realidad, debería haber indicador como [CORTE] o similar en specific_fix, pero aquí revisamos si termina normalmente
                if dialogue and dialogue[-1] in ".!?":
                    # Podría estar bien si hay indicador interno, pero por simplicidad, asumimos que debe haber marcado
                    # En versiones futuras, revisar metadata o specific_fix de episodios previos
                    pass  # Por ahora no hard fail, pero sí feedback

            # 6. CTA (beat 9, índice 8) DEBE ser pregunta tribal (nunca "suscríbete")
            if i == 8:  # CTA
                lower_dialogue = dialogue.lower()
                forbidden_ctas = [
                    "suscríbete",
                    "sígueme",
                    "dale like",
                    "comparte",
                    "activa notificaciones",
                    "suscribe",
                ]
                if any(forbidden in lower_dialogue for forbidden in forbidden_ctas):
                    fails.append(f"Beat 9 (CTA): CTA genérico prohibido: '{dialogue}'")

            # 7. Camera ejecutable: shot_type, angle, movement, lens, focus_pull
            camera = beat.get("camera", {})
            if not isinstance(camera, dict):
                fails.append(
                    f"Beat {i+1} ({beat_name}): Camera no es un diccionario válido"
                )
            else:
                required_cam = ["shot_type", "angle", "movement", "lens"]
                missing = [f for f in required_cam if f not in camera]
                if missing:
                    fails.append(
                        "Beat {} ({}): Cámara faltante campos: {}".format(
                            i + 1, beat_name, ", ".join(missing)
                        )
                    )

            # 8. Sound: ambience, sfx, music_cue, silence_drop (boolean)
            sound = beat.get("sound", {})
            if not isinstance(sound, dict):
                fails.append(
                    f"Beat {i+1} ({beat_name}): Sound no es un diccionario válido"
                )
            else:
                # sfx debe ser lista (puede estar vacío)
                sfx = sound.get("sfx", [])
                if not isinstance(sfx, list):
                    fails.append(f"Beat {i+1} ({beat_name}): SFX debe ser una lista")
                # silence_drop debe ser boolean si existe
                silence_drop = sound.get("silence_drop")
                if silence_drop is not None and not isinstance(silence_drop, bool):
                    fails.append(
                        f"Beat {i+1} ({beat_name}): silence_drop debe ser booleano"
                    )

        # 9. Revisar durations: cada beat debe ser exactamente 10.0 segundos
        for i, beat in enumerate(beats):
            duration = beat.get("duration_sec")
            if duration is not None and abs(duration - 10.0) > 0.001:
                fails.append(
                    f"Beat {i+1} duration debe ser exactamente 10.0s, actual: {duration}"
                )

        # 10. CERO Setup Disease: cada beat debe aportar nuevo conflicto, secreto o avance narrativo
        # Elimina beats que son puramente expositivos o connective tissue sin valor narrativo propio
        setup_keywords_es = [
            "introduce",
            "presenta",
            "contextualiza",
            "retoma",
            "continua",
            "seguidamente",
            "mientras tanto",
            "de repente",
            "más tarde",
            "más adelante",
            "años después",
            "de repente",
            "de pronto",
            "en ese momento",
            "de repente",
            "de pronto",
            "por fin",
            "finalmente",
            "al fin",
            "de pronto",
            "de pronto",
            "de repente",
            "gracias",
            "por favor",
            "hola",
            "adiós",
            "perdón",
            "con permiso",
        ]
        setup_indicators_narrative = [
            "dialogue",
            "action",
            "conflict",
            "secret",
            "revelation",
            "twist",
            "question",
            "answer",
            "decision",
            "change",
            "discovery",
        ]
        for i, beat in enumerate(beats):
            # Contar indicadores de setup vs avances
            dialogue = beat.get("dialogue", "").lower()
            action = beat.get("action", "").lower()
            combined = f"{dialogue} {action}"
            # Contar cuántos keywords de avances hay
            advance_count = sum(
                1 for kw in setup_indicators_narrative if kw in combined
            )
            # Contar cuántos keywords de setup hay
            setup_count = sum(1 for kw in setup_keywords_es if kw in combined)
            # Si el beat tiene muchos keywords de setup y pocos de avances, es setup disease
            if setup_count >= 2 and advance_count <= 1:
                fails.append(
                    f"Beat {i+1}: Possible Setup Disease - beat aporta poco conflicto/avance y parece expositivo/connective tissue. Asegurar que cada beat introduzca nuevo elemento (secreto, conflicto, descubrimiento o giro)."
                )

        # 11. MATRIZ DE SECRETOS: cada beat debe tener secret_matrix con main_conflict, revealed_secret, unresolved_question
        # La matriz de secretos es obligatoria para asegurar continuidad narrativa entre beats y episodios
        for i, beat in enumerate(beats):
            secret_matrix = beat.get("secret_matrix", {})
            if not isinstance(secret_matrix, dict):
                fails.append(
                    f"Beat {i+1} ({beat_name}): secret_matrix faltante o no es diccionario"
                )
                continue
            required_secret_fields = [
                "main_conflict",
                "revealed_secret",
                "unresolved_question",
            ]
            missing_fields = [
                f
                for f in required_secret_fields
                if f not in secret_matrix or not secret_matrix[f]
            ]
            if missing_fields:
                fails.append(
                    "Beat {} ({}): secret_matrix incompleto, campos faltantes: {}".format(
                        i + 1, beat_name, ", ".join(missing_fields)
                    )
                )
            else:
                # Validar que revealed_secret no sea idéntico al main_conflict (debe ser revelación parcial)
                main = secret_matrix.get("main_conflict", "").lower()
                revealed = secret_matrix.get("revealed_secret", "").lower()
                if main and revealed and main == revealed:
                    fails.append(
                        f"Beat {i+1} ({beat_name}): revealed_secret no puede ser idéntico a main_conflict (debe ser revelación parcial)"
                    )
                # Validar que unresolved_question no esté vacío y sea una pregunta real
                unresolved = secret_matrix.get("unresolved_question", "")
                if (
                    not unresolved
                    or not isinstance(unresolved, str)
                    or len(unresolved.strip()) < 10
                ):
                    fails.append(
                        f"Beat {i+1} ({beat_name}): unresolved_question demasiado corto o vacío (mínimo 10 chars)"
                    )
                elif "?" not in unresolved:
                    fails.append(
                        f"Beat {i+1} ({beat_name}): unresolved_question debe ser una pregunta (contener ?)"
                    )

        return fails

    # -------------------- RÚBRICA DE SCORING (100 pts) --------------------
    def _score_rubric(self, episode_package: dict[str, Any]) -> dict[str, float]:
        """
        Aplica la rúbrica 100 pts:
        - Hook: 20 pts (diálogo de doble filo + shock visual)
        - Dialogue Quality: 15 pts (cada beat tiene línea viral, ≤15 palabras, español latino, CERO exposición)
        - Story Structure: 15 pts (9 beats exactos, info beat cada 15-30s, subversion en Twist1)
        - Secret Matrix: 5 pts (cada beat tiene secret_matrix completa: main_conflict, revealed_secret, unresolved_question)
        - Emotional Damage: 15 pts (cada línea inflige daño emocional específico)
        - Retention Cadence: 15 pts (pattern interrupt cada 2.5s, pacing dinámico)
        - Character Voice: 10 pts (voz como identidad: fría/quebrada/pausada por personaje)
        - Visual Potential: 5 pts (cámara ejecutable, micro-expresiones observables)
        - Audio Design: 5 pts (4 pistas: voz, foley, sub-bass, music + silence_drop)
        - Cliffhanger: 5 pts (línea CORTADA abruptamente, no completa)
        - CTA Tribal: 5 pts (pregunta tribal, nunca genérico, genera bandos)
        """
        beats = episode_package.get("beats", [])
        scores = {}

        # Hook (20 pts)
        scores["hook"] = self._score_hook(beats[0] if beats else {})

        # Dialogue Quality (15 pts)
        scores["dialogue_quality"] = self._score_dialogue_quality(beats)

        # Story Structure (15 pts)
        scores["story_structure"] = self._score_story_structure(episode_package)

        # Secret Matrix (5 pts)
        scores["secret_matrix"] = self._score_secret_matrix(beats)

        # Emotional Damage (15 pts)
        scores["emotional_damage"] = self._score_emotional_damage(beats)

        # Retention Cadence (15 pts)
        scores["retention_cadence"] = self._score_retention_cadence(episode_package)

        # Character Voice (10 pts)
        scores["character_voice"] = self._score_character_voice(episode_package)

        # Visual Potential (5 pts)
        scores["visual_potential"] = self._score_visual_potential(beats)

        # Audio Design (5 pts)
        scores["audio_design"] = self._score_audio_design(beats)

        # Cliffhanger (5 pts)
        scores["cliffhanger"] = self._score_cliffhanger(
            beats[7] if len(beats) > 7 else {}
        )

        # CTA Tribal (5 pts)
        scores["cta_tribal"] = self._score_cta_tribal(
            beats[8] if len(beats) > 8 else {}
        )

        return scores

    def _score_hook(self, beat: dict) -> float:
        """Hook: 20 pts (diálogo de doble filo + shock visual)"""
        score = 0.0
        dialogue = beat.get("dialogue", "")
        # Doble filo: detectar si tiene doble significado (simplificado: contar comillas, preguntas, contrastes)
        if dialogue:
            # Señales de doble filo: presencia de contraste, ironía, pregunta retórica
            double_filero_indicators = [
                "pero",
                "sin embargo",
                "aunque",
                "¿",
                "?",
                "¡",
                "!",
            ]
            if any(ind in dialogue.lower() for ind in double_filero_indicators):
                score += 10.0
            # Shock visual: revisar action y camera for visual shock indicators
            action = beat.get("action", "").lower()
            shock_indicators = [
                "gira",
                "sorpresa",
                "impacto",
                "explosión",
                "grito",
                "lágrima",
                "sangre",
                "arma",
            ]
            if any(ind in action for ind in shock_indicators):
                score += 10.0
            # Bonus: si tiene ambos
            if any(ind in dialogue.lower() for ind in double_filero_indicators) and any(
                ind in action for ind in shock_indicators
            ):
                score = 20.0  # máximo
        return min(20.0, score)

    def _score_dialogue_quality(self, beats: list[dict]) -> float:
        """Dialogue Quality: 15 pts (cada beat tiene línea viral, ≤15 palabras, español latino, CERO exposición)"""
        if not beats or len(beats) != 9:
            return 0.0
        total = 0.0
        for beat in beats:
            dialogue = beat.get("dialogue", "")
            if not dialogue:
                continue  # 0 pts for this beat
            words = dialogue.split()
            # Longitud ≤15 palabras
            if len(words) <= 15:
                total += 1.0  # 1/15 por beat cumplido
            # Español latino (heurística: presencia de palabras típicas)
            latino_indicators = [
                "vos",
                "ustedes",
                "che",
                "chévere",
                "bacán",
                "chido",
                "wey",
                "güey",
                "pendejo",
            ]
            dialogue_lower = dialogue.lower()
            if any(ind in dialogue_lower for ind in latino_indicators):
                total += 1.0
            # CERO exposición pasiva (penalizar si contiene indicadores expositivos fuertes)
            expositive = [
                "siente que",
                "está pensando que",
                "cree que",
                "piensa que",
                "opina que",
            ]
            if not any(exp in dialogue_lower for exp in expositive):
                total += 1.0
            # Si cumple los 3, máximo 3 pts por beat
        # Máximo 15 pts (9 beats * 1.666... pero simplificamos a 15 si todos cumplen los 3)
        # Mejor: cada beat puede dar hasta 1.666 puntos, pero usamos escala 0-15
        # Si cada beat da 1 punto por cada criterio cumplido (máx 3), entonces 9*3=27, necesitamos escalar a 15
        # Simplificación: si todos los beats cumplen los 3 criterios => 15 pts
        # Contamos beats que cumplen al menos 2 de 3 criterios como partial
        # Pero para simplicidad en este mock:
        if total >= 27:  # todos los 9 beats con 3/3
            return 15.0
        elif total >= 18:  # promedio 2/3
            return 10.0
        elif total >= 9:  # promedio 1/3
            return 5.0
        else:
            return 0.0

    def _score_story_structure(self, episode_package: dict) -> float:
        """Story Structure: 15 pts (9 beats exactos, info beat cada 15-30s, subversion en Twist1)"""
        score = 0.0
        beats = episode_package.get("beats", [])
        # 9 beats exactos
        if len(beats) == 9:
            score += 5.0
        # Info beat cada 15-30s (al menos uno en cada rango)
        # Simplificado: revisar que haya beats con información (no solo acción)
        info_beats = 0
        for beat in beats:
            action = beat.get("action", "").lower()
            # Indicadores de info beat: descubrimiento, revelación, explicación breve, etc.
            info_indicators = [
                "descubre",
                "revela",
                "explica",
                "entender",
                "saber",
                "recordar",
                "memoria",
                "flashback",
            ]
            if any(ind in action for ind in info_indicators):
                info_beats += 1
        if info_beats >= 3:  # al menos 3 info beats en 90s
            score += 5.0
        # Subversion en Twist1 (beat 5)
        if len(beats) > 4:
            twist1 = beats[4]  # índice 4
            subversion = twist1.get("subversion_applied", "")
            if (
                subversion
                and isinstance(subversion, str)
                and len(subversion.strip()) > 0
            ):
                score += 5.0
        return min(15.0, score)

    def _score_secret_matrix(self, beats: list[dict]) -> float:
        """Secret Matrix: 5 pts (cada beat tiene secret_matrix completa: main_conflict, revealed_secret, unresolved_question)"""
        if not beats or len(beats) != 9:
            return 0.0
        total = 0.0
        required_fields = ["main_conflict", "revealed_secret", "unresolved_question"]
        for beat in beats:
            secret_matrix = beat.get("secret_matrix", {})
            if not isinstance(secret_matrix, dict):
                continue  # 0 pts for this beat
            # Verificar campos obligatorios
            has_all_fields = all(
                f in secret_matrix and secret_matrix[f] for f in required_fields
            )
            if has_all_fields:
                total += 0.5  # 9 beats * 0.5 = 4.5 max, bonus si hay validación extra
                # Bonus: revealed_secret no es idéntico a main_conflict
                main = secret_matrix.get("main_conflict", "").lower()
                revealed = secret_matrix.get("revealed_secret", "").lower()
                if main and revealed and main != revealed:
                    total += 0.05  # bonus por revelación parcial real
                # Bonus: unresolved_question es una pregunta real con longitud adecuada
                unresolved = secret_matrix.get("unresolved_question", "")
                if unresolved and "?" in unresolved and len(unresolved.strip()) >= 10:
                    total += 0.05  # bonus por pregunta real
        return min(5.0, total)

    def _score_emotional_damage(self, beats: list[dict]) -> float:
        """Emotional Damage: 15 pts (cada línea inflige daño emocional específico)"""
        if not beats:
            return 0.0
        total = 0.0
        # Emotional damage indicators por beat
        damage_map = {
            "Hook": ["shock", "surprise", "betrayal"],
            "Context": ["curiosity", "tension", "mystery"],
            "Problem": ["fear", "anger", "sadness"],
            "Escalation": ["anger", "fear", "tension"],
            "Twist1": ["surprise", "shock", "revelation"],
            "Conflict2": ["anger", "betrayal", "fear"],
            "Revelation": ["revelation", "truth", "shock"],
            "Cliffhanger": ["suspense", "anxiety", "dread"],
            "CTA": ["decision", "conflict", "urgency"],
        }
        beat_names = [
            "Hook",
            "Context",
            "Problem",
            "Escalation",
            "Twist1",
            "Conflict2",
            "Revelation",
            "Cliffhanger",
            "CTA",
        ]
        for i, beat in enumerate(beats):
            if i >= len(beat_names):
                break
            expected_emotions = damage_map.get(beat_names[i], [])
            dialogue = beat.get("dialogue", "").lower()
            action = beat.get("action", "").lower()
            combined = f"{dialogue} {action}"
            # Revisar si hay coincidencia con emociones esperadas
            matches = sum(1 for emo in expected_emotions if emo in combined)
            if matches >= 1:
                total += 1.667  # 15/9 approx
            elif matches == 0:
                # Dar crédito parcial si hay alguna emoción fuerte
                strong_emotions = [
                    "shock",
                    "surprise",
                    "betrayal",
                    "fear",
                    "anger",
                    "sadness",
                    "revelation",
                    "truth",
                ]
                if any(emo in combined for emo in strong_emotions):
                    total += 0.834  # medio punto approx
        return min(15.0, total)

    def _score_retention_cadence(self, episode_package: dict) -> float:
        """Retention Cadence: 15 pts (pattern interrupt cada 2.5s, pacing dinámico)"""
        if not episode_package:
            return 0.0
        beats = episode_package.get("beats", [])
        score = 0.0
        # Revisar pattern interrupts en cada beat (debería haber al menos 2-3 por beat de 10s)
        # Simplificado: asumir que si el campo pattern_interrupt existe y no es vacío, hay al menos uno
        interrupt_counts = []
        for beat in beats:
            interrupts = beat.get("pattern_interrupt", [])
            if not isinstance(interrupts, list):
                interrupts = [interrupts] if interrupts else []
            interrupt_counts.append(len(interrupts))
        # Esperamos al menos 2 interrupts por beat (cada 2.5s en 10s = 4 interrupts)
        # Pero siendo conservadores: al menos 1 por beat es aceptable, 2+ es bueno
        beats_with_interrupt = sum(1 for cnt in interrupt_counts if cnt >= 1)
        beats_with_good_interrupt = sum(1 for cnt in interrupt_counts if cnt >= 2)
        # Score basado en proporción
        if beats_with_good_interrupt >= 9:  # todos los beats con 2+ interrupts
            score += 15.0
        elif beats_with_interrupt >= 9:  # todos los beats con al menos 1 interrupt
            score += 10.0
        elif beats_with_interrupt >= 6:  # al menos 2/3
            score += 5.0
        # Además, revisar pacing dinámico (variación en intensidad emocional)
        # Simplificado: revisar que no haya 3 beats seguidos con misma intensidad
        intensities = [beat.get("emotion", "") for beat in beats]
        # Cambiar si hay variación
        if len(set(intensities)) >= 3:  # al menos 3 emociones diferentes
            score += 5.0  # bonus por pacing dinámico
        return min(15.0, score)

    def _score_character_voice(self, episode_package: dict) -> float:
        """Character Voice: 10 pts (voz como identidad: fría/quebrada/pausada por personaje)"""
        # Simplificado: revisar que cada personaje tenga voz consistente y distintiva
        beats = episode_package.get("beats", [])
        if not beats:
            return 0.0
        # Recopilar character_emotion y ver si hay patrón
        character_emotions = {}
        for beat in beats:
            char_emotion = beat.get("character_emotion", {})
            for char_id, emotion in char_emotion.items():
                if char_id not in character_emotions:
                    character_emotions[char_id] = []
                character_emotions[char_id].append(emotion)
        # Score: si cada personaje tiene al menos 2 emociones distintas (muestra rango) y consistencia
        score = 0.0
        for char_id, emotions in character_emotions.items():
            if len(emotions) >= 2:
                score += 2.0  # hasta 5 personajes para llegar a 10 pts
        return min(10.0, score)

    def _score_visual_potential(self, beats: list[dict]) -> float:
        """Visual Potential: 5 pts (cámara ejecutable, micro-expresiones observables)"""
        if not beats:
            return 0.0
        total = 0.0
        for beat in beats:
            camera = beat.get("camera", {})
            # Cámara ejecutable: tiene todos los campos requeridos
            if isinstance(camera, dict):
                required = ["shot_type", "angle", "movement", "lens"]
                if all(f in camera for f in required):
                    total += 2.5  # mitad del puntaje
            # Micro-expresiones observables: revisar que haya expresión específica
            emotion = beat.get("emotion", "")
            # Asumir que si hay emoción, hay micro-expresión asociada (en versión real revisaríamos micro_expressions field)
            if emotion and emotion not in ["neutral", ""]:
                total += 2.5
        return min(5.0, total)

    def _score_audio_design(self, beats: list[dict]) -> float:
        """Audio Design: 5 pts (4 pistas: voz, foley, sub-bass, music + silence_drop)"""
        if not beats:
            return 0.0
        total = 0.0
        for beat in beats:
            sound = beat.get("sound", {})
            if not isinstance(sound, dict):
                continue
            pistas = 0
            # Voz: asumir presente si hay diálogo
            if beat.get("dialogue", "").strip():
                pistas += 1
            # Foley: revisar sfx por pasos, ropa, objetos
            sfx = sound.get("sfx", [])
            if isinstance(sfx, list) and any(
                str(s).lower() in ["footsteps", "cloth", "fabric", "paper", "metal"]
                for s in sfx
            ):
                pistas += 1
            # Sub-bass: revisar frecuencia baja en music_cue o sfx
            music_cue = sound.get("music_cue", {})
            if isinstance(music_cue, dict):
                bpm = music_cue.get("bpm", 0)
                if bpm < 90:  # sub-bass asociado a tempos lentos
                    pistas += 1
                # También revisar explícitamente en sfx
                sfx_str = " ".join(str(s).lower() for s in sfx)
                if "sub-bass" in sfx_str or "40hz" in sfx_str or "60hz" in sfx_str:
                    pistas += 1
            # Music: presente si hay music_cue o sfx musical
            if music_cue or any(
                str(s).lower() in ["piano", "strings", "synth", "orchestral"]
                for s in sfx
            ):
                pistas += 1
            # Silence drop: revisar campo silencio_drop
            if sound.get("silence_drop") is True:
                pistas += 1
            # Esperamos 4 pistas para puntaje completo
            if pistas >= 4:
                total += 5.0
            elif pistas >= 3:
                total += 3.75
            elif pistas >= 2:
                total += 2.5
            elif pistas >= 1:
                total += 1.25
        return min(5.0, total)

    def _score_cliffhanger(self, beat: dict) -> float:
        """Cliffhanger: 5 pts (línea CORTADA abruptamente, no completa)"""
        if not beat:
            return 0.0
        score = 0.0
        dialogue = beat.get("dialogue", "")
        # Revisar si hay indicador de corte en el diálogo o en metadata
        # En versión real, revisaríamos specific_fix o notas de producción
        # Por ahora, dar crédito si el diálogo parece incompleto (termina en coma, y, o sin puntuación final fuerte)
        if dialogue:
            # Si termina en coma o con y/o, es más probable que esté cortado
            if (
                dialogue.endswith(",")
                or dialogue.endswith(" y ")
                or dialogue.endswith(" o ")
            ):
                score += 3.0
            # O si tiene indicador explícito como [CORTE] o ...
            if "[CORTE]" in dialogue or "..." in dialogue or dialogue.endswith("..."):
                score += 5.0
            # Penalizar si termina con punto fuerte sin indicador de corte
            elif (
                dialogue.endswith(".")
                or dialogue.endswith("!")
                or dialogue.endswith("?")
            ):
                # Podría estar bien si es parte de la técnica, pero sin indicador arriesgamos
                score += 2.0  # medio crédito
            else:
                # Otro caso (termina en letra o número)
                score += 1.0
        return min(5.0, score)

    def _score_cta_tribal(self, beat: dict) -> float:
        """CTA Tribal: 5 pts (pregunta tribal, nunca genérico, genera bandos)"""
        if not beat:
            return 0.0
        score = 0.0
        dialogue = beat.get("dialogue", "").lower()
        # Revisar que sea una pregunta (termina en ?) o tenga indicadores de dilema
        if "?" in dialogue:
            score += 2.0
        # Revisar que NO sea genérico
        forbidden = [
            "suscríbete",
            "sígueme",
            "dale like",
            "comparte",
            "activa notificaciones",
            "suscribe",
            "sigue la página",
        ]
        if not any(forb in dialogue for forb in forbidden):
            score += 2.0
        # Revisar que genere bandos (palabras como "equipo", "bando", "línea", "elige", "decides")
        band_indicators = [
            "equipo",
            "bando",
            "elige",
            "decides",
            "qué harías",
            "qué elegirías",
            "lado",
            "lado a",
            "vs",
            "versus",
        ]
        if any(ind in dialogue for ind in band_indicators):
            score += 1.0
        return min(5.0, score)

    # -------------------- SIMULADOR ADVERSARIAL (TDAH) --------------------
    def _adhd_simulation_penalty(self, episode_package: dict) -> float:
        """
        Simula cómo un espectador con TDAH percibiría el episodio.
        Penaliza si hay períodos > 2.5s sin cambio visual/auditivo significativo.
        Basado en investigación: el ojo humano se aburre a los 2.5s.
        """
        penalty = 0.0
        beats = episode_package.get("beats", [])
        if not beats or len(beats) != 9:
            return 10.0  # penalización máxima si estructura básica falla

        # Revisar cada beat para cambios internos suficientemente frecuentes
        for i, beat in enumerate(beats):
            # Esperamos al menos 2-3 cambios significativos por beat de 10s (cada 2.5-3.3s)
            # Cambios significativos: pattern_interrupt, cambio de cámara, cambio de emoción fuerte, etc.
            changes = 0
            # Pattern interrupts
            interrupts = beat.get("pattern_interrupt", [])
            if isinstance(interrupts, list):
                changes += len(interrupts)
            # Cambios en cámara (shot_type, angle, movement changes dentro del beat - simplificado)
            # En versión real, habría múltiples shots por beat con cambios
            # Aquí asumimos que si hay pattern interrupts, ya cuenta como cambio
            # Cambios en emotion (revisar si hay variación dentro del beat - no disponible en este modelo simplificado)
            # Cambios en action (verbos diferentes)
            action = beat.get("action", "").lower()
            # Contar verbos distintos en action (simplificado: separar por comas o "y")
            if " y " in action or ", " in action:
                changes += 1  # asumo múltiples acciones
            # Si el beat tiene menos de 2 cambios significativos, aplicar penalty
            if changes < 2:
                # Penalty proporcional: menos cambios = más penalty
                beat_penalty = (
                    2 - changes
                ) * 2.0  # cada cambio faltante = 2pts penalty (máx 4pts per beat)
                penalty += beat_penalty
        # Limitar penalty máximo a 20 pts (para no dejar score negativo en casos extremos)
        return min(penalty, 20.0)

    # -------------------- FEEDBACK GENERATION --------------------
    def _generate_detailed_feedback(
        self, episode_package: dict, scores_breakdown: dict[str, float]
    ) -> list[dict[str, Any]]:
        """Genera feedback items específicos cuando score < 85"""
        feedback = []
        beats = episode_package.get("beats", [])
        beat_names = [
            "Hook",
            "Context",
            "Problem",
            "Escalation",
            "Twist1",
            "Conflict2",
            "Revelation",
            "Cliffhanger",
            "CTA",
        ]

        # Revisar cada aspecto de scoring y generar feedback para los más bajos
        # Ordenar aspectos por score ascendente (peores primero)
        sorted_aspects = sorted(scores_breakdown.items(), key=lambda x: x[1])

        for aspect, score in sorted_aspects[:3]:  # Top 3 peores aspectos
            if aspect == "hook" and score < 15.0:  # esperando cerca de 20
                feedback.append(
                    {
                        "beat": "Hook",
                        "issue": "Hook insuficiente: falta de doble filo o shock visual",
                        "specific_fix": "Agregar contraste irónico o pregunta retórica + acción visual impactante (ej: giro súbito, objeto que revela secreto)",
                        "priority": "high",
                    }
                )
            elif aspect == "dialogue_quality" and score < 10.0:
                feedback.append(
                    {
                        "beat": "Múltiples beats",
                        "issue": "Diálogo de calidad inferior: muy largo, exposición pasiva, o falta de sabor latino",
                        "specific_fix": "Reducir diálogos a máximo 15 palabras, eliminar verbos como 'siente/piensa/cree', agregar modismos latinos y contraste",
                        "priority": "high",
                    }
                )
            elif aspect == "story_structure" and score < 10.0:
                feedback.append(
                    {
                        "beat": "Estructura general",
                        "issue": "Estructura de historia débil: falta de info beats regulares o subversion en Twist1",
                        "specific_fix": "Agregar al menos uno info beat cada 15-30s (descubrimiento, revelación breve) y asegurar que Twist1 tenga subversion_applied explícito",
                        "priority": "high",
                    }
                )
            elif aspect == "emotional_damage" and score < 10.0:
                feedback.append(
                    {
                        "beat": "Múltiples beats",
                        "issue": "Daño emocional insuficiente: líneas no infligen suficiente impacto",
                        "specific_fix": "Cada línea debe provocar una emoción fuerte: shock, miedo, ira, sorpresa, revelación, traición. Usar verbos fuertes y situaciones límite",
                        "priority": "high",
                    }
                )
            elif aspect == "retention_cadence" and score < 10.0:
                feedback.append(
                    {
                        "beat": "Múltiples beats",
                        "issue": "Ritmo de retención insuficiente: pocos pattern interrupts o pacing monótono",
                        "specific_fix": "Agregar pattern interrupt cada 2.0-2.5s máximo (zoom-punch, whip-pan, speed-ramp, match-cut). Variar emociones y acciones para mantener pacing dinámico",
                        "priority": "high",
                    }
                )
            elif aspect == "character_voice" and score < 5.0:
                feedback.append(
                    {
                        "beat": "Voces de personajes",
                        "issue": "Voces de personajes poco distintivas o monótonas",
                        "specific_fix": "Asignar a cada personaje un rango vocal distintivo (ej: CEO frío vs heroína quebrada vs rival cálido). Variar tono, velocidad y énfasis según arco emocional",
                        "priority": "medium",
                    }
                )
            elif aspect == "visual_potential" and score < 3.0:
                feedback.append(
                    {
                        "beat": "Potencial visual",
                        "issue": "Potencial visual bajo: cámara poco ejecutable o falta de micro-expresiones observables",
                        "specific_fix": "Asegurar que cada beat tenga cámara definida (shot_type, angle, movement, lens) y emoción clara asociada a micro-expresión (ej: shock → ojos muy abiertos)",
                        "priority": "medium",
                    }
                )
            elif aspect == "audio_design" and score < 3.0:
                feedback.append(
                    {
                        "beat": "Diseño de audio",
                        "issue": "Diseño de audio insuficiente: falta de capas de voz, foley, sub-bass, music o silence_drop",
                        "specific_fix": "Incluir las 4 pistas: voz clara, foley de pasos/ropa/objetos, sub-bass (40-60Hz), música ambiental, y silence drops estratégicos (0.5s ANTES de twists/revelations)",
                        "priority": "medium",
                    }
                )
            elif aspect == "cliffhanger" and score < 3.0:
                feedback.append(
                    {
                        "beat": "Cliffhanger",
                        "issue": "Cliffhanger no suficientemente abrupto o falta de tensión",
                        "specific_fix": "El cliffhanger debe cortar la frase EN MEDIO de una palabra o pensamiento crítico (ej: 'La razón por la que volví no es lo que...' [CORTE]). Nunca completar la frase.",
                        "priority": "high",
                    }
                )
            elif aspect == "cta_tribal" and score < 3.0:
                feedback.append(
                    {
                        "beat": "CTA",
                        "issue": "CTA no tribal o genérico",
                        "specific_fix": "El CTA debe ser una pregunta que divida a la audiencia en bandos opuestos (moral dilemma, identity tease, revenge choice, team war). Nunca usar 'suscríbete' o similares.",
                        "priority": "high",
                    }
                )
        # Limitar a máximo 5 feedback items
        return feedback[:5]

    def _generate_optimization_feedback(
        self, episode_package: dict, scores_breakdown: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Genera feedback para optimización incluso cuando pasa (ej: de 85 a 92)"""
        feedback = []
        # Buscar aspectos que estén cerca del máximo pero puedan mejorar
        for aspect, score in scores_breakdown.items():
            max_possible = {
                "hook": 20,
                "dialogue_quality": 15,
                "story_structure": 15,
                "emotional_damage": 15,
                "retention_cadence": 15,
                "character_voice": 10,
                "visual_potential": 5,
                "audio_design": 5,
                "cliffhanger": 5,
                "cta_tribal": 5,
            }.get(aspect, 0)
            if score < max_possible * 0.9:  # menos del 90% del máximo
                if aspect == "hook" and score < 18.0:
                    feedback.append(
                        {
                            "beat": "Hook",
                            "issue": "Hook bueno pero podría ser más impactante",
                            "specific_fix": "Considerar aumentar el contraste en el doble filo o hacer el shock visual más inesperado",
                            "priority": "low",
                        }
                    )
                elif aspect == "retention_cadence" and score < 13.0:
                    feedback.append(
                        {
                            "beat": "Ritmo general",
                            "issue": "Ritmo de retención adecuado pero podría ser más dinámico",
                            "specific_fix": "Agregar un pattern interrupt adicional en beats de baja actividad o variar el tipo de interrupts para predecibilidad",
                            "priority": "low",
                        }
                    )
        return feedback[:3]  # máximo 3 para optimization

    def _generate_rewrite_instructions(
        self, feedback_items: list[dict], verdict: str
    ) -> str:
        """Genera instrucciones de reescritura basado en feedback y veredicto"""
        if verdict == EpisodeVerdict.PASS.value:
            if not feedback_items:
                return "GUIÓN APROBADO. Mantener los elementos que funcionaron bien, especialmente los hooks visuales y los pattern interrupts cada 2.5s."
            else:
                return (
                    "GUIÓN APROBADO CON OBSERVACIONES: Considerar las sugerencias de optimización para subir el score aún más. "
                    + "; ".join(
                        [
                            f.get("specific_fix", "")
                            for f in feedback_items
                            if f.get("priority") == "low"
                        ]
                    )
                )
        elif verdict == EpisodeVerdict.HUMAN_REVIEW.value:
            return (
                "SE REQUIERE REVISIÓN HUMANA: El guion muestra potencial pero necesita ajustes creativos antes de producción. "
                + "; ".join(
                    [
                        f.get("specific_fix", "")
                        for f in feedback_items
                        if f.get("priority") in ["high", "medium"]
                    ]
                )
            )
        else:  # REWRITE
            if not feedback_items:
                return "REESCRIBIR GUION: El guion no cumple con los estándares mínimos. Revisar estructura básica y requisitos de formato."
            else:
                return (
                    "REESCRIBIR GUION CON FEEDBACK DETALLADO: Aplicar los siguientes fixes específicos por orden de prioridad: "
                    + "; ".join([f.get("specific_fix", "") for f in feedback_items])
                )

    # Para evitar errores de importación circular, dejamos los métodos helper como stubs que serán implementados en versiones futuras
    # Estos métodos existen para que el código no falle, pero en esta versión retornan valores por defecto seguros

    # Métodos de ayuda (stubs para evitar errores, en implementación real tendrían lógica completa)
    def _analyze_internal_cliches(self, cliches: dict, genre: str) -> dict[str, Any]:
        return {"detected": [], "risk_level": "low"}

    def _analyze_external_cliches(
        self, seed: str, genre: str, trends: dict
    ) -> dict[str, Any]:
        return {
            "detected": [],
            "competition_saturation": "medium",
            "emerging_alternatives": [],
        }

    def _extract_mechanism(
        self, seed: str, genre: str, internal: dict, external: dict
    ) -> dict[str, Any]:
        return {
            "core_mechanism": "identity_disguise_reveal",
            "description": "El personaje aparente es débil, pero posee habilidades ocultas",
            "variations": [
                "apparent_weakness → hidden mastery",
                "apparent_innocence → calculated_villain",
                "apparent_helplessness → strategic_manipulator",
            ],
        }

    def _calculate_originality_score(
        self, mechanism: dict, internal: dict, external: dict
    ) -> float:
        return 85.5

    def _generate_recommended_angle(self, mechanism: dict, internal: dict) -> str:
        return "El personaje aparentemente poderoso pierde todo y descubre que su mayor enemigo es su propia reflexión"

    def _assess_plagiarism_risk(self, mechanism: dict, trends: dict) -> str:
        return "low"

    def _assess_autoplagio_risk(self, autoplagio: dict, internal: dict) -> str:
        return "medium"

    def _generate_forbidden_combos(self, internal: dict, external: dict) -> list[str]:
        return [
            "heredera oculta + palacio empresarial + romance prohibido (season 3 saturation)",
            "amnesia + identidad falsa + triangulo amoroso (platform saturation)",
        ]

    def _generate_detailed_reasoning(
        self, score: float, mechanism: dict, forbidden: list
    ) -> str:
        return f"Originality score: {score}/100. Mechanism: {mechanism.get('core_mechanism', 'unknown')}. Forbidden combinations identified: {len(forbidden)}. Recommendation: Apply 70/20/10 mutation budget focusing on exploration variations."

    def _generate_cross_platform_insights(
        self, mechanism: dict, trends: dict
    ) -> dict[str, Any]:
        return {
            "tiktok": {"angle_variation": "shorten to 3s reveal", "hashtags": ["#fyp"]},
            "youtube_shorts": {
                "angle_variation": "expand with backstory",
                "hashtags": ["#shorts"],
            },
            "instagram_reels": {
                "angle_variation": "add visual effects",
                "hashtags": ["#reelsviral"],
            },
        }
