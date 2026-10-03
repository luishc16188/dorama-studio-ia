"""
Story Architect Agent (Agent 4) - Narrative structure and 9-beat mapping.
"""
import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.story_architect_schemas import (
    StoryArchitectInput,
    StoryArchitectOutput,
)

logger = logging.getLogger(__name__)


class StoryArchitectAgent(BaseAgent):
    """
    Agent 4: Story Architect
    Maps viral insights to 9-beat structure using H→P→Q→E→R→Q2→C fractal formula.
    """

    InputSchema = StoryArchitectInput
    OutputSchema = StoryArchitectOutput

    def __init__(self):
        super().__init__("StoryArchitectAgent")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the story architect agent."""
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

        # Beat mapping rules
        self.beat_mapping = {
            "hook": ["impossible_romance", "revenge", "betrayal", "identity", "power", "revelation", "threat", "mystery", "humiliation", "prohibition", "visual_shock", "question"],
            "promise": ["hook_reinforcement", "stakes_clarification", "goal_establishment"],
            "question": ["information_gap", "character_mystery", "plot_enigma"],
            "escalation": ["obstacle_intensification", "character_pressure", "stakes_raising"],
            "reward": ["partial_victory", "emotional_payoff", "alliance_formation"],
            "question2": ["twist_setup", "new_mystery", "deeper_question"],
            "cliffhanger": ["visual_punch", "emotional_sting", "question_amplification"]
        }

        # Emotional arc templates
        self.emotional_arcs = [
            "esperanza -> desesperanza -> esperanza renovada",
            "inocencia -> desilusión -> sabiduría",
            "soledad -> conexión forzada -> vínculo auténtico",
            "miedo -> confrontación -> coraje",
            "odio -> comprensión -> perdón",
            "duda -> decisión -> convicción",
            "tristeza -> acción -> propósito",
            "ira -> reflexión -> paz",
            "confusión -> claridad -> acción decisiva"
        ]

    def _process(self, validated_input: StoryArchitectInput) -> StoryArchitectOutput:
        """
        Process the input to create a 9-beat story outline.

        Args:
            validated_input: Contains 'viral_potential' and 'originality_report'.

        Returns:
            StoryArchitectOutput with the 9-beat structure and status.
        """
        try:
            viral_potential = validated_input.viral_potential
            originality_report = validated_input.originality_report

            if not viral_potential or not originality_report:
                raise ValueError("viral_potential and originality_report required")

            # Create story outline
            outline = self._create_story_outline(viral_potential, originality_report)

            return StoryArchitectOutput(
                beat_hook=outline.beat_hook,
                beat_promise=outline.beat_promise,
                beat_question=outline.beat_question,
                beat_escalation=outline.beat_escalation,
                beat_reward=outline.beat_reward,
                beat_question2=outline.beat_question2,
                beat_cliffhanger=outline.beat_cliffhanger,
                narrative_mechanism=outline.narrative_mechanism,
                emotional_arc=outline.emotional_arc,
                beat_ratings=outline.beat_ratings,
                total_narrative_score=outline.total_narrative_score,
                status="completed"
            )

        except Exception as e:
            logger.error(f"Story architecture failed: {e!s}")
            return StoryArchitectOutput(
                beat_hook="",
                beat_promise="",
                beat_question="",
                beat_escalation="",
                beat_reward="",
                beat_question2="",
                beat_cliffhanger="",
                narrative_mechanism="",
                emotional_arc="",
                beat_ratings={},
                total_narrative_score=0.0,
                status="error"
            )

    def _create_story_outline(
        self,
        viral_potential: Any,
        originality_report: Any
    ) -> Any:
        """Create 9-beat story outline."""
        # Extract data
        hook_categories = viral_potential.hook_categories if hasattr(viral_potential, 'hook_categories') else viral_potential.get('hook_categories', [])
        mechanism = originality_report.mechanism_extracted if hasattr(originality_report, 'mechanism_extracted') else getattr(originality_report, 'mechanism_extracted', 'Unknown')

        # Map beats
        beats = self._map_beats(hook_categories)

        # Determine emotional arc
        emotional_arc = self._select_emotional_arc(hook_categories, mechanism)

        # Rate each beat
        beat_ratings = self._rate_beats(beats, hook_categories, originality_report)

        # Calculate total score
        total_score = sum(beat_ratings.values()) / len(beat_ratings) if beat_ratings else 0

        return type('StoryOutline', (), {
            'beat_hook': beats.get('hook', ''),
            'beat_promise': beats.get('promise', ''),
            'beat_question': beats.get('question', ''),
            'beat_escalation': beats.get('escalation', ''),
            'beat_reward': beats.get('reward', ''),
            'beat_question2': beats.get('question2', ''),
            'beat_cliffhanger': beats.get('cliffhanger', ''),
            'narrative_mechanism': mechanism,
            'emotional_arc': emotional_arc,
            'beat_ratings': beat_ratings,
            'total_narrative_score': round(total_score, 1)
        })()

    def _map_beats(self, hook_categories: list[str]) -> dict[str, str]:
        """Map hook categories to 9-beat structure."""
        beats = {}

        # Primary hook category determines hook beat
        primary_hook = hook_categories[0] if hook_categories else "question"
        beats['hook'] = self._generate_hook_beat(primary_hook)

        # Promise: reinforce the hook's promise
        beats['promise'] = self._generate_promise_beat(primary_hook)

        # Initial question: what the hook makes us wonder
        beats['question'] = self._generate_question_beat(primary_hook)

        # Escalation: obstacles and pressure
        beats['escalation'] = self._generate_escalation_beat(hook_categories)

        # Reward: partial satisfaction
        beats['reward'] = self._generate_reward_beat(hook_categories)

        # Question 2: new mystery after reward
        beats['question2'] = self._generate_question2_beat(hook_categories)

        # Cliffhanger: unresolved tension
        beats['cliffhanger'] = self._generate_cliffhanger_beat(hook_categories)

        return beats

    def _generate_hook_beat(self, hook_category: str) -> str:
        """Generate hook beat based on category."""
        hook_templates = {
            "impossible_romance": "Dos personas de mundos opuestos se atraen pese a todo lo que las separa",
            "revenge": "Un protagonista busca justicia tras una herida que el sistema ignora",
            "betrayal": "La persona en quien más confiaba resulta ser la amenaza más grande",
            "identity": "Alguien descubre que su vida entera se basa en una mentira fundamental",
            "power": "Una persona común obtiene un poder que cambia las reglas del juego",
            "revelation": "Un secreto enterrado sale a la luz y redefine todo lo conocido",
            "threat": "Un peligro inminente obliga a actuar antes de que sea demasiado tarde",
            "mystery": "Un enigma aparece sin explicación lógica y exige ser resuelto",
            "humiliation": "Un personaje público sufre una caída que destruye su reputación",
            "prohibition": "Un deseo se vuelve peligroso cuando lo prohibido llama con fuerza",
            "visual_shock": "Una imagen impactante desafía toda expectativa de realidad",
            "question": "Un fenómeno inexplicable aparece y exige una respuesta inmediata"
        }
        return hook_templates.get(hook_category, "Un evento inesperado rompe la cotidianidad")

    def _generate_promise_beat(self, hook_category: str) -> str:
        """Generate promise beat."""
        promise_templates = {
            "impossible_romance": "Prometen intentarlo pese a las consecuencias sociales",
            "revenge": "Juran descubrir la verdad y hacer pagar a los responsables",
            "betrayal": "Deciden investigar por su cuenta para encontrar pruebas",
            "identity": "Emprenden un viaje para descubrir quiénes son realmente",
            "power": "Aprenden a controlar su nueva habilidad antes de que los controle a ellos",
            "revelation": "Buscan entender por qué se les ocultó la verdad tanto tiempo",
            "threat": "Forman un plan para neutralizar el peligro antes del plazo límite",
            "mystery": "Empiezan a reunir pistas siguiendo la única señal disponible",
            "humiliation": "Trabajan en secreto para recuperar su honor y dignidad perdida",
            "prohibition": "Arriesgan todo por un momento de autenticidad prohibida",
            "visual_shock": "Investigan qué significa esa anomalía para su comprensión del mundo",
            "question": "Deciden seguir la pista dondequiera que los lleve, pese al riesgo"
        }
        return promise_templates.get(hook_category, "Se comprometen a descubrir la verdad")

    def _generate_question_beat(self, hook_category: str) -> str:
        """Generate question beat."""
        question_templates = {
            "impossible_romance": "¿Podrán superar las diferencias que los separan?",
            "revenge": "¿Está justificada la venganza o perpetúa el ciclo de violencia?",
            "betrayal": "¿Quién más está involucrado en la conspiración?",
            "identity": "¿Qué otros aspectos de su vida fueron fabricados?",
            "power": "¿Cuál es el precio real de este poder recién adquirido?",
            "revelation": "¿Quién se benefició de mantener este secreto oculto?",
            "threat": "¿Podrán detenerlo a tiempo sin sacrificar lo que más aman?",
            "mystery": "¿Qué conexión tiene este enigma con su pasado olvidado?",
            "humiliation": "¿Quién estuvo detrás de esta humillación y por qué?",
            "prohibition": "¿Vale la pena perderlo todo por un instante de verdad?",
            "visual_shock": "¿Esta anomalía es un mensaje, una advertencia o un fenómeno natural?",
            "question": "¿Qué patrones se repiten en estos eventos inexplicables?"
        }
        return question_templates.get(hook_category, "¿Cuál es la verdadera naturaleza de esto?")

    def _generate_escalation_beat(self, hook_categories: list[str]) -> str:
        """Generate escalation beat."""
        if "revenge" in hook_categories or "betrayal" in hook_categories:
            return "Cada paso hacia la verdad revela aliados inesperados y enemigos más cercanos"
        elif "power" in hook_categories:
            return "El poder atrae atención no deseada de quienes quieren aprovecharse"
        elif "mystery" in hook_categories or "revelation" in hook_categories:
            return "Las respuestas encontradas solo plantean preguntas más profundas y peligrosas"
        elif "romance" in str(hook_categories):
            return "Las fuerzas externas intentan separarlos mientras crece la atracción prohibida"
        else:
            return "Los obstáculos se multiplican y el costo del fracaso aumenta exponencialmente"

    def _generate_reward_beat(self, hook_categories: list[str]) -> str:
        """Generate reward beat."""
        if "revelation" in hook_categories:
            return "Descubren una pieza clave que explica parcialmente el misterio central"
        elif "power" in hook_categories:
            return "Logran usar su poder para proteger a alguien importante por primera vez"
        elif "betrayal" in hook_categories:
            return "Obtienen evidencia concreta que confirma sus sospechas más temidas"
        elif "romance" in str(hook_categories):
            return "Un momento de vulnerabilidad compartida crea un vínculo genuino"
        else:
            return "Un pequeño éxito les da esperanza y confirma que van por el buen camino"

    def _generate_question2_beat(self, hook_categories: list[str]) -> str:
        """Generate question 2 beat."""
        if "threat" in hook_categories:
            return "¿Quién está realmente detrás de la amenaza y qué quiere realmente?"
        elif "identity" in hook_categories:
            return "Si no son quién creían ser, ¿cuál es su verdadero propósito?"
        elif "revene" in hook_categories:  # Fixed typo
            return "¿La justicia que buscan vale lo que están convirtiéndose para lograrla?"
        elif "power" in hook_categories:
            return "¿Qué responsabilidades vienen con este poder y están preparados para ellas?"
        else:
            return "¿Qué implica realmente esta victoria parcial para el conflicto mayor?"

    def _generate_cliffhanger_beat(self, hook_categories: list[str]) -> str:
        """Generate cliffhanger beat."""
        cliffhanger_templates = {
            "threat": "El villano se revela como alguien íntimamente conocido... y sostiene un detonador",
            "betrayal": "El aliado más confiable susurra: 'Lo hice por ti' mientras apunta el arma",
            "mystery": "La última pieza del rompecabezas muestra su propio rostro en el futuro",
            "power": "El poder se vuelve inestable justo cuando más lo necesitan",
            "revelation": "Al leer el documento final, descubren que el autor es su yo del futuro",
            "romance": "Justo cuando confían plenamente, llega una prueba irrefutable de traición",
            "identity": "El espejo refleja no su rostro, sino el del enemigo que han estado buscando",
            "visual_shock": "La anomalía comienza a crecer y ahora es visible a simple vista",
            "question": "Las lecturas del instrumento se vuelven imposibles según las leyes físicas conocidas"
        }

        primary_hook = hook_categories[0] if hook_categories else "question"
        return cliffhanger_templates.get(primary_hook, "Un desarrollo inesperado pone en duda todo lo asumido hasta ahora")

    def _select_emotional_arc(self, hook_categories: list[str], mechanism: str) -> str:
        """Select appropriate emotional arc."""
        # Map hook categories to emotional arcs
        arc_mapping = {
            "revenge": "odio -> comprensión -> perdón",
            "betrayal": "confianza -> desilusión -> cautela optimista",
            "identity": "confusión -> autodescubrimiento -> propósito",
            "power": "miedo -> responsabilidad -> sabiduría",
            "romance": "soledad -> conexión vulnerable -> intimidad auténtica",
            "threat": "miedo -> acción decidida -> victoria amarga",
            "mystery": "curiosidad -> frustración -> iluminación",
            "humiliation": "vergüenza -> resistencia -> dignidad recuperada"
        }

        for category in hook_categories:
            if category in arc_mapping:
                return arc_mapping[category]

        # Default arcs
        return self.emotional_arcs[0]  # esperanza -> desesperanza -> esperanza renovada

    def _rate_beats(
        self,
        beats: dict[str, str],
        hook_categories: list[str],
        originality_report: Any
    ) -> dict[str, float]:
        """Rate each beat from 0-10."""
        ratings = {}

        # Base rating from originality (more original = higher potential)
        base_score = originality_report.novelty_score if hasattr(originality_report, 'novelty_score') else 50
        base_rating = base_score / 10  # Convert 0-100 to 0-10

        for beat_name, beat_content in beats.items():
            if not beat_content:
                ratings[beat_name] = 0.0
                continue

            # Start with base rating
            rating = base_rating

            # Adjust based on beat completeness and specificity
            if len(beat_content) > 20:  # Substantial content
                rating += 1.0
            if "¿" in beat_content or "?" in beat_content:  # Contains question
                rating += 0.5
            if any(word in beat_content.lower() for word in ["descubren", "revelan", "aprenden", "logran"]):
                rating += 0.5  # Active progression

            # Cap at 10
            ratings[beat_name] = min(10.0, max(0.0, rating))

        return ratings


if __name__ == "__main__":
    print("StoryArchitectAgent module loaded successfully")
