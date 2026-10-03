"""
Hook Engine - Generates and selects viral hook candidates for drama episodes.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from dorama_studio.contracts.trend_signal import TrendSignal


@dataclass
class HookCandidate:
    """Represents a potential hook for an episode."""

    hook_id: str
    description: str
    hook_type: str  # revelation, threat, question, visual_shock, etc.
    intrigue_score: float  # 0-100
    emotion_score: float  # 0-100
    retention_score: float  # 0-100
    novelty_score: float  # 0-100
    total_score: float = 0.0
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Calculate total score as weighted average
        self.total_score = (
            self.intrigue_score * 0.4
            + self.emotion_score * 0.3
            + self.retention_score * 0.3
        ) * (
            1 + self.novelty_score / 200
        )  # Novelty boosts score


class HookEngine:
    """
    Generates hook candidates and selects the best ones for episode openings.
    """

    def __init__(self):
        # Hook templates by type
        self.hook_templates = {
            "revelation": [
                "Alguien descubre que todo lo que creía era una mentira",
                "Un documento secreto revela la verdadera identidad del antagonista",
                "El protagonista encuentra una prueba que cambia el curso de la investigación",
                "Una grabación de seguridad muestra lo que realmente pasó aquella noche",
                "Un test de ADN confirma una relación que nadie esperaba",
            ],
            "threat": [
                "Un mensaje anónimo advierte: 'Si vas a la policía, morirás'",
                "El protagonista recibe un paquete con una evidencia comprometedora",
                "Una cámara oculta captura al protagonista en una situación comprometedora",
                "Un desconocido se acerca y susurra: 'Te estoy viendo'",
                "El teléfono suena con un número desconocido: solo dice 'Mírate atrás'",
            ],
            "question": [
                "¿Quién envió esa flor negra a su puerta cada mañana?",
                "¿Por qué el espejo muestra una habitación que no existe?",
                "¿Qué significa el símbolo que aparece en todas las escenas del crimen?",
                "¿Quién está enviando esas cartas sin remitente y por qué?",
                "¿Por qué todos los relojes se detienen a las 3:33 AM exactamente?",
            ],
            "visual_shock": [
                "Un cuerpo cae del cielo justo frente a la ventana del protagonista",
                "El espejo del baño se rompe solo, reflejando una habitación distinta",
                "Las plantas del jardín se marchitan en segundos al tocar el suelo",
                "Un niño señala al cielo y grita: '¡Miren! Eso no es un avión'",
                "El reflejo en el lago muestra lo que debería estar detrás, pero no está",
            ],
            "emotional_punch": [
                "Un abrazo que dura demasiado tiempo, como diciendo adiós para siempre",
                "Una carta encontrada en el bolsillo de un traje que ya no se usa",
                "El sonido de un reloj de arena que se acaba en el momento más crítico",
                "Una canción de infancia que solo suena cuando está a punto de pasar algo",
                "El último mensaje de voz de alguien que ya no está, pero sigue sonando cada noche",
            ],
            "action_launch": [
                "El protagonista salta del edificio justo cuando explota detrás de él",
                "Un disparo resuena y el protagonista ve a su aliado caer frente a él",
                "El auto del protagonista arranca solo y se dirige hacia el peligro",
                "Una puerta se cierra de golpe y se escucha un llanto desde el otro lado",
                "El protagonista corre hacia el grito, pero al llegar, solo encuentra silencio",
            ],
            "mystery_object": [
                "Una llave antigua que no abre ninguna puerta conocida de la casa",
                "Un reloj que marca la hora correcta pero va hacia atrás",
                "Un libro cuyas páginas se escriben solas mientras duerme",
                "Un espejo que no refleja a quien está delante, sino a quien estuvo antes",
                "Una moneda que siempre cae cara arriba, sin importar cuántas veces se tire",
            ],
        }

        # Tags for novelty scoring
        self.novelty_tags = {
            "timely": ["elección", "referéndum", "cumbre", "festival", "aniversario"],
            "emerging_trend": [
                "IA",
                "realidad virtual",
                "cripto",
                "metaverso",
                "sostenibilidad",
            ],
            "classic_renewed": [
                "amor imposible",
                "venganza",
                "secreto familiar",
                "traición",
                "redención",
            ],
            "visual_innovation": [
                "toma continua",
                "perspectiva invertida",
                "color simbólico",
                "iluminación emocional",
            ],
        }

    def generate_candidates(self, count: int = 50) -> list[HookCandidate]:
        """
        Generate a pool of hook candidates.
        """
        candidates = []
        used_descriptions = set()

        for i in range(count):
            # Select hook type randomly but with some weighting
            hook_type = random.choice(list(self.hook_templates.keys()))
            template_list = self.hook_templates[hook_type]
            base_description = random.choice(template_list)

            # Ensure uniqueness (simple check)
            attempt = 0
            while base_description in used_descriptions and attempt < 5:
                base_description = random.choice(template_list)
                attempt += 1
            if base_description in used_descriptions:
                # If we can't get unique, add a modifier
                base_description = f"{base_description} (variante {i})"

            used_descriptions.add(base_description)

            # Generate scores based on hook type and randomness
            intrigue, emotion, retention, novelty = self._score_hook(
                hook_type, base_description
            )

            candidate = HookCandidate(
                hook_id=f"HOOK-{i+1:03d}",
                description=base_description,
                hook_type=hook_type,
                intrigue_score=intrigue,
                emotion_score=emotion,
                retention_score=retention,
                novelty_score=novelty,
                tags=self._generate_tags(hook_type, base_description),
            )
            candidates.append(candidate)

        return candidates

    def _score_hook(
        self, hook_type: str, description: str
    ) -> tuple[float, float, float, float]:
        """
        Score a hook on intrigue, emotion, retention, and novelty.
        Simplified scoring based on hook type and keywords.
        """
        # Base scores by hook type
        base_scores = {
            "revelation": (85, 75, 80, 70),
            "threat": (90, 80, 85, 65),
            "question": (95, 70, 75, 80),
            "visual_shock": (80, 85, 90, 75),
            "emotional_punch": (70, 95, 70, 60),
            "action_launch": (85, 70, 80, 70),
            "mystery_object": (90, 65, 70, 85),
        }

        base_intrigue, base_emotion, base_retention, base_novelty = base_scores.get(
            hook_type, (75, 75, 75, 70)
        )

        # Add some randomness (±10 points)
        intrigue = max(0, min(100, base_intrigue + random.randint(-10, 10)))
        emotion = max(0, min(100, base_emotion + random.randint(-10, 10)))
        retention = max(0, min(100, base_retention + random.randint(-10, 10)))
        novelty = max(0, min(100, base_novelty + random.randint(-15, 15)))

        # Boost for certain keywords that increase novelty
        description_lower = description.lower()
        novelty_boosters = [
            "IA",
            "inteligencia artificial",
            "realidad aumentada",
            "blockchain",
            "quantum",
            "nanotecnología",
            "biotecnología",
            "crímenes cibernéticos",
            "deepfake",
            "algoritmo",
            "ciberseguridad",
        ]
        if any(booster in description_lower for booster in novelty_boosters):
            novelty = min(100, novelty + 15)

        # Boost for timely topics
        timely_topics = [
            "elección",
            "referéndum",
            "olímpicos",
            "mundial",
            "festival de cine",
            "premios nobel",
            "cumbre climática",
            "día internacional",
        ]
        if any(topic in description_lower for topic in timely_topics):
            novelty = min(100, novelty + 10)
            intrigue = min(100, intrigue + 5)

        return intrigue, emotion, retention, novelty

    def _generate_tags(self, hook_type: str, description: str) -> list[str]:
        """Generate tags for a hook based on its content."""
        tags = [hook_type]
        description_lower = description.lower()

        # Add novelty tags
        for category, keywords in self.novelty_tags.items():
            if any(keyword in description_lower for keyword in keywords):
                tags.append(category)

        # Add emotion tags
        emotion_indicators = {
            "miedo": ["amenaza", "peligro", "asesinato", "asesino", "arma", "disparo"],
            "sorpresa": ["descubre", "encuentra", "revela", "secreto", "oculto"],
            "tristeza": [
                "despedida",
                "adiós",
                "última vez",
                "recuerdo",
                "foto antigua",
            ],
            "felicidad": ["reencuentro", "sorpresa", "regalo", "celebración", "fiesta"],
            "asco": ["sangre", "herida", "enfermedad", "contaminación", "tóxico"],
        }
        for emotion, indicators in emotion_indicators.items():
            if any(ind in description_lower for ind in indicators):
                tags.append(emotion)

        return tags

    def select_top_hooks(
        self, candidates: list[HookCandidate], top_n: int = 3
    ) -> list[HookCandidate]:
        """
        Select the top N hooks based on total score.
        """
        sorted_candidates = sorted(
            candidates, key=lambda x: x.total_score, reverse=True
        )
        return sorted_candidates[:top_n]

    def get_hook_for_episode(
        self, episode_num: int, trend_signal: Optional[TrendSignal] = None
    ) -> HookCandidate:
        """
        Get the best hook for a specific episode, considering trends.
        """
        candidates = self.generate_candidates(30)  # Generate a reasonable pool

        # If we have trend data, we could adjust novelty scores based on trend alignment
        # For simplicity, we'll just select top 3 and rotate based on episode number
        top_hooks = self.select_top_hooks(candidates, 3)
        selected_index = episode_num % len(top_hooks)
        return top_hooks[selected_index]


# Convenience function
def get_best_hook(
    episode_num: int, trend_signal: Optional[TrendSignal] = None
) -> HookCandidate:
    """Get the best hook for an episode."""
    engine = HookEngine()
    return engine.get_hook_for_episode(episode_num, trend_signal)


if __name__ == "__main__":
    # Quick test
    engine = HookEngine()
    candidates = engine.generate_candidates(10)
    print(f"Generated {len(candidates)} hook candidates:")
    for i, cand in enumerate(candidates[:3], 1):
        print(f"{i}. [{cand.hook_type}] {cand.description}")
        print(
            f"   Scores: I:{cand.intrigue_score:.1f} E:{cand.emotion_score:.1f} R:{cand.retention_score:.1f} N:{cand.novelty_score:.1f} Total:{cand.total_score:.1f}"
        )
        print(f"   Tags: {cand.tags}")
        print()

    top_3 = engine.select_top_hooks(candidates, 3)
    print("Top 3 hooks:")
    for i, cand in enumerate(top_3, 1):
        print(f"{i}. {cand.description} (Score: {cand.total_score:.1f})")
