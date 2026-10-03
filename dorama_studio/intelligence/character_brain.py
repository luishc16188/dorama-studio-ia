"""
Character Brain AI - Crea personajes con memoria psicológica completa.
Cada personaje tiene: historia completa, personalidad, trauma, deseos, miedos, secretos, relaciones y evolución emocional.
Los personajes deben sentirse humanos, no generados automáticamente.
"""

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class PsychologicalProfile:
    """Perfil psicológico profundo de un personaje."""
    # Rasgos de personalidad (modelo OCEAN o similar)
    openness: float = 0.5          # Apertura a la experiencia
    conscientiousness: float = 0.5  # Responsabilidad
    extraversion: float = 0.5      # Extroversión
    agreeableness: float = 0.5     # Amabilidad
    neuroticism: float = 0.5       # Inestabilidad emocional

    # Motivaciones profundas
    want: str = ""                 # Lo que el personaje cree que quiere (meta externa)
    need: str = ""                 # Lo que el personaje realmente necesita (crecimiento interno)
    lie: str = ""                  # La mentira que se cree a sí mismo
    ghost: str = ""                # El trauma del pasado que aún lo afecta
    secret: str = ""               # El secreto que guarda y que cambiaría todo si se revela

    # Historia y背景
    backstory: str = ""            # Historia completa del personaje
    key_memories: list[str] = field(default_factory=list)  # Recuerdos clave que lo definen
    relationships: dict[str, str] = field(default_factory=dict)  # Relaciones con otros personajes

    # Estado actual
    current_fear: str = ""         # Lo que más teme perder o enfrentar ahora
    current_desire: str = ""       # Lo que más desea en este momento
    emotional_state: str = "neutral"  # Estado emocional actual
    stress_level: float = 0.0      # Nivel de estrés actual (0-1)

    # Evolución
    character_arc_stage: str = "setup"  # setup, confrontation, transformation, resolution
    growth_achieved: list[str] = field(default_factory=list)  # Lecciones aprendidas

@dataclass
class CharacterBrain:
    """Representación completa de un personaje en el Character Brain AI."""
    character_id: str
    name: str
    role: str  # protagonist, antagonist, love interest, mentor, etc.
    archetype: str  # Arquetipo junguiano o de narrativa
    psychological_profile: PsychologicalProfile = field(default_factory=PsychologicalProfile)

    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    usage_count: int = 0  # Cuántas veces se ha usado este personaje
    last_used_episode: int | None = None

    # Consistencia y evolución
    consistency_tags: list[str] = field(default_factory=list)  # Rasgos que NO deben cambiar
    evolution_path: list[dict[str, Any]] = field(default_factory=list)  # Cómo evoluciona por episodio

class CharacterBrainAI:
    """
    Character Brain AI que crea y gestiona personajes con memoria psicológica profunda.
    Los personajes evolucionan de manera creíble a lo largo de la temporada.
    """

    def __init__(self):
        # Base de datos de personajes creados (en producción sería persistente)
        self.character_database: dict[str, CharacterBrain] = {}

        # Plantillas de arquetipos y rasgos psicológicos
        self.archetype_templates = self._load_archetype_templates()
        self.name_banks = self._load_name_banks()

        # Contadores para generar IDs únicos
        self.id_counters = {}

        logger.info("CharacterBrainAI initialized")

    def _load_archetype_templates(self) -> dict[str, dict[str, Any]]:
        """Carga plantillas de arquetipos con rasgos psicológicos típicos."""
        return {
            "protagonist": {
                "openness": (0.6, 0.9),
                "conscientiousness": (0.4, 0.8),
                "extraversion": (0.3, 0.7),
                "agreeableness": (0.5, 0.9),
                "neuroticism": (0.2, 0.7),
                "common_wants": ["amar", "ser aceptado", "encontrar la verdad", "proteger a su familia"],
                "common_needs": ["superar su miedo más profundo", "perdón a sí mismo", "confianza", "autonomía"],
                "common_lies": ["No soy suficiente", "No merezco el amor", "Debo hacerlo todo solo", "El mundo es peligroso y no puedo confiar"],
                "common_ghosts": ["Trauma infantil", "Pérdida de un ser querido", "Fallo pasado", "Traición"],
                "common_secrets": ["Tiene una habilidad oculta", "Está viviendo bajo una falsa identidad", "Cometió un crimen en el pasado", "Es el hijo ilegítimo de alguien poderoso"]
            },
            "antagonist": {
                "openness": (0.3, 0.7),
                "conscientiousness": (0.6, 0.9),
                "extraversion": (0.5, 0.8),
                "agreeableness": (0.1, 0.4),
                "neuroticism": (0.4, 0.8),
                "common_wants": ["poder", "control", "venganza", "reconocimiento"],
                "common_needs": ["sanar una herida profunda", "sentirse amado", "tener un propósito", "perdón"],
                "common_lies": ["El poder es la única forma de estar a salvo", "El amor es una debilidad", "No puedo confiar en nadie", "Solo los fuertes sobreviven"],
                "common_ghosts": ["Trauma de abandono", "Trauma de abuso", "Humillación pública", "Pérdida de poder"],
                "common_secrets": ["En realidad está protegiendo a alguien", "Está siendo chantajeado", "No es realmente malvado, está obligado", "Busca redención a través del daño que causa"]
            },
            "love_interest": {
                "openness": (0.5, 0.8),
                "conscientiousness": (0.5, 0.8),
                "extraversion": (0.6, 0.9),
                "agreeableness": (0.7, 0.95),
                "neuroticism": (0.2, 0.6),
                "common_wants": ["encontrar el amor verdadero", "ser visto por quien realmente es", "tener una relación estable", "felicidad"],
                "common_needs": ["superar el miedo al compromiso", "confiar en sí mismo", "perdonar un pasado doloroso", "ser independiente"],
                "common_lies": ["No merezco ser amado", "Soy demasiado roto para una relación", "Todos los que amo me abandonan", "Debo cambiar para ser amado"],
                "common_ghosts": ["Relación tóxica pasada", "Heartbreak profundo", "Trauma de abandono", "Miedo al compromiso por experiencia previa"],
                "common_secrets": ["Tiene un hijo de una relación anterior", "Está endeudado peligrosamente", "Tiene una enfermedad crónica", "Está huyendo de su pasado"]
            },
            "mentor": {
                "openness": (0.7, 0.95),
                "conscientiousness": (0.7, 0.9),
                "extraversion": (0.4, 0.7),
                "agreeableness": (0.6, 0.9),
                "neuroticism": (0.1, 0.5),
                "common_wants": ["guiar al héroe", "ver crecer al protegido", "dejar un legado", "ver justicia"],
                "common_needs": ["perdonarse por un error del pasado", "dejar ir el necesidad de controlar", "encontrar paz", "aceptar su mortalidad"],
                "common_lies": ["Soy responsable de todo lo que les pasa a quienes quiero", "Si no soy fuerte, todos morirán", "Mi valor está en lo que hago por los otros", "No merezco felicidad"],
                "common_ghosts": ["Fallo al proteger a alguien importante", "Pérdida de un protegido", "Error que costó vidas", "Trauma de guerra o conflicto"],
                "common_secrets": ["Está enfermo y no tiene mucho tiempo", "En realidad es el verdadero antagonista", "Está manipulando al héroe para un propósito oscuro", "Tiene un hijo secreto con el antagonista"]
            }
        }

    def _load_name_banks(self) -> dict[str, list[str]]:
        """Carga bancos de nombres por origen/cultura."""
        # En producción, estos seriamás extensos y vendrían de archivos externos
        return {
            "korean": ["Min-joon", "Soo-yeon", "Jae-hyun", "Hana", "Tae-woong", "Yoo-jin", "Seung-ho", "Irina", "Do-hyun", "Ga-eul"],
            "spanish": ["Alejandro", "Isabella", "Diego", "Valentina", "Mateo", "Camila", "Lucas", "Martina", "Sebastian", "Victoria"],
            "japanese": ["Haruto", "Aoi", "Sota", "Akari", "Ren", "Hina", "Soshi", "Yui", "Kaito", "Mei"],
            "chinese": ["Wei", "Li Na", "Zhang Wei", "Wang Lei", "Liu Yang", " Zhao Min", "Sun Yan", "Zhou Qian", "Huang Jun", "Xu Ling"],
            "universal": ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Riley", "Quinn", "Avery", "Peyton", "Quinn"]
        }

    def _generate_character_id(self, prefix: str = "char") -> str:
        """Genera un ID único para un personaje."""
        if prefix not in self.id_counters:
            self.id_counters[prefix] = 0
        self.id_counters[prefix] += 1
        return f"{prefix}_{self.id_counters[prefix]:03d}"

    def create_character(
        self,
        name: str | None = None,
        role: str = "protagonist",
        archetype: str | None = None,
        cultural_origin: str = "universal",
        seed_data: dict[str, Any] | None = None,
        episode_number: int = 1
    ) -> CharacterBrain:
        """
        Crea un nuevo personaje con perfil psicológico profundo.

        Args:
            name: Nombre del personaje (si es None, se elige aleatoriamente)
            role: Rol en la historia (protagonist, antagonist, etc.)
            archetype: Arquetipo junguiano (si es None, se deriva del rol)
            cultural_origin: Origen cultural para el nombre
            seed_data: Datos semilla para personalizar el personaje
            episode_number: Episodio en el que se introduce el personaje

        Returns:
            CharacterBrain con perfil psicológico completo
        """
        logger.info(f"Creating {role} character: {name or '[random]'}")

        # Determinar arquetipo si no se proporciona
        if archetype is None:
            archetype_map = {
                "protagonist": "hero",
                "antagonist": "shadow",
                "love_interest": "lover",
                "mentor": "wise_old_man",
                "ally": "ally",
                "trickster": "trickster"
            }
            archetype = archetype_map.get(role, "everyman")

        # Generar o seleccionar nombre
        if name is None:
            name_bank = self.name_banks.get(cultural_origin, self.name_banks["universal"])
            name = random.choice(name_bank)

        # Generar ID único
        character_id = self._generate_character_id()

        # Obtener plantilla de arquetipo
        template = self.archetype_templates.get(role, self.archetype_templates["protagonist"])

        # Crear perfil psicológico basado en plantilla y semilla
        profile = self._create_psychological_profile(template, seed_data, role)

        # Crear el personaje
        character = CharacterBrain(
            character_id=character_id,
            name=name,
            role=role,
            archetype=archetype,
            psychological_profile=profile
        )

        # Establecer consistencia y evolución inicial
        self._initialize_character_consistency_and_evolution(character, episode_number)

        # Guardar en base de datos
        self.character_database[character_id] = character

        logger.info(f"Created character {character_id}: {name} ({role}/{archetype})")
        return character

    def _create_psychological_profile(
        self,
        template: dict[str, Any],
        seed_data: dict[str, Any] | None,
        role: str
    ) -> PsychologicalProfile:
        """Crea un perfil psicológico basado en plantilla de arquetipo y datos semilla."""
        # Inicializar con valores medios
        profile = PsychologicalProfile()

        # Aplicar rangos de la plantilla con variación aleatoria
        for trait, (min_val, max_val) in [
            ("openness", template.get("openness", (0.3, 0.7))),
            ("conscientiousness", template.get("conscientiousness", (0.3, 0.7))),
            ("extraversion", template.get("extraversion", (0.3, 0.7))),
            ("agreeableness", template.get("agreeableness", (0.3, 0.7))),
            ("neuroticism", template.get("neuroticism", (0.3, 0.7)))
        ]:
            # Si tenemos semilla para este rasgo, usarla; sino, valor aleatorio en el rango
            if seed_data and trait in seed_data:
                value = max(min_val, min(max_val, float(seed_data[trait])))
            else:
                value = random.uniform(min_val, max_val)
            setattr(profile, trait, value)

        # Establecer want, need, lie, ghost, secret
        for field in ["want", "need", "lie", "ghost", "secret"]:
            options = template.get(f"common_{field}s", [])
            if options:
                if seed_data and field in seed_data and seed_data[field]:
                    value = seed_data[field]
                else:
                    value = random.choice(options) if options else ""
                setattr(profile, field, value)

        # Si tenemos semilla de backstory o recuerdos, usarlos
        if seed_data:
            if "backstory" in seed_data:
                profile.backstory = seed_data["backstory"]
            if "key_memories" in seed_data:
                profile.key_memories = seed_data["key_memories"]
            if "relationships" in seed_data:
                profile.relationships = seed_data["relationships"]
            if "current_fear" in seed_data:
                profile.current_fear = seed_data["current_fear"]
            if "current_desire" in seed_data:
                profile.current_desire = seed_data["current_desire"]
            if "emotional_state" in seed_data:
                profile.emotional_state = seed_data["emotional_state"]
            if "stress_level" in seed_data:
                profile.stress_level = max(0.0, min(1.0, float(seed_data["stress_level"])))

        # Generar backstory básico si no se proporciona
        if not profile.backstory:
            profile.backstory = self._generate_backstory(profile, role)

        # Generar recuerdos clave si no se proporcionan
        if not profile.key_memories:
            profile.key_memories = self._generate_key_memories(profile, role)

        # Generar relaciones básicas si no se proporcionan
        if not profile.relationships:
            profile.relationships = self._generate_initial_relationships(role)

        # Establecer estado emocional inicial basado en want/need/lie
        if not profile.emotional_state:
            profile.emotional_state = self._determine_initial_emotional_state(profile)

        # Establecer miedos y deseos actuales
        if not profile.current_fear:
            profile.current_fear = profile.ghost or profile.lie or "ser descubierto"

        if not profile.current_desire:
            profile.current_desire = profile.want or "superar su miedo"

        return profile

    def _generate_backstory(self, profile: PsychologicalProfile, role: str) -> str:
        """Genera una historia de fondo básica para el personaje."""
        # Plantillas simples de backstory
        backstory_templates = {
            "protagonist": [
                "Creció en un entorno {adjective1} que le enseñó {lesson1}. Un evento traumático en su {age} años ({event}) lo marcó para siempre.",
                "Fue el {position} en su familia, lo que lo hizo desarrollar {trait}. La {event} cambió su perspectiva sobre {aspecto de la vida}."
            ],
            "antagonist": [
                "Su camino hacia la oscuridad comenzó cuando {event} a los {age} años. Aprendió que {lesson1} y decidió que {belief}.",
                "Nunca recibió el {thing} que necesitaba, por eso cree que {belief} y actúa según ello."
            ],
            "love_interest": [
                "Aprender a amar de nuevo fue difícil después de {event}. Ahora busca {need} mientras protege su corazón de {fear}.",
                "Su pasado romanticamente {adjective1} le ha enseñado que {lesson1}, pero aún espera encontrar alguien que {hope}."
            ],
            "mentor": [
                "Después de años de experiencia en {field}, aprendió que la verdadera {value} viene de {lesson1}. Ahora busca guiar a otros para que no cometan sus mismos errores.",
                "La {event} que vivió a los {age} años le enseñó lo importante que es {value}, y dedica su vida a transmitir esa lección."
            ]
        }

        templates = backstory_templates.get(role, backstory_templates["protagonist"])
        template = random.choice(templates) if templates else "Tiene un pasado complejo que influye en sus decisiones actuales."

        # Llenar placeholders con valores aleatorios o basados en el perfil
        replacements = {
            "adjective1": random.choice(["difícil", "privilegiado", "traumático", "nómada", "estricto", "artístico"]),
            "lesson1": random.choice([
                "confiar en nadie", "depender solo de sí mismo", "que el amor es una debilidad",
                "que la verdad siempre sale a la luz", "que el poder corrompe", "que la familia es lo más importante"
            ]),
            "age": random.randint(5, 25),
            "event": random.choice([
                "la pérdida de un ser querido", "un fracaso público", "una traición de un amigo cercano",
                "un diagnóstico médico grave", "un cambio forzado de residencia", "un accidente que cambió su vida"
            ]),
            "position": random.choice(["hijo mayor", "hijo del medio", "hijo menor", "hijo único"]),
            "trait": random.choice(["autosufficencia", "independencia", "empatía extrema", "ambición desmedida"]),
            "aspecto de la vida": random.choice(["las relaciones", "el trabajo", "la familia", "el éxito", "la felicidad"]),
            "thing": random.choice(["amor paterno", "reconocimiento", "un hogar estable", "aprobación", "seguridad"]),
            "belief": random.choice([
                "el poder es la única forma de estar a salvo", "el amor siempre lleva al dolor",
                "solo los fuertes sobreviven", "la felicidad es efímera y no se debe buscar",
                "el mundo es justo y quienes sufren lo merecen"
            ]),
            "field": random.choice(["medicina", "derecho", "negocios", "arte", "educación", "militar"]),
            "value": random.choice(["verdad", "justicia", "amor", "lealtad", "integridad", "coraje"]),
        }

        try:
            backstory = template.format(**replacements)
        except KeyError:
            backstory = "Tiene un pasado complejo que influye en sus decisiones actuales."

        return backstory

    def _generate_key_memories(self, profile: PsychologicalProfile, role: str) -> list[str]:
        """Genera recuerdos clave que definen al personaje."""
        memories = []

        # Memoria relacionada con el ghost/trauma
        if profile.ghost:
            memories.append(f"El evento que causó su {profile.ghost.lower()}")

        # Memoria relacionada con el lie/mentira
        if profile.lie:
            memories.append(f"El momento en que comenzó a creer que '{profile.lie}'")

        # Memoria relacionada con el want/necesidad superficial
        if profile.want:
            memories.append(f"La primera vez que persiguió fuertemente '{profile.want}'")

        # Memoria relacionada con el need/necesidad profunda
        if profile.need:
            memories.append(f"El instante en que sintió por primera vez que necesitaba '{profile.need}'")

        # Memoria relacionada con el secret
        if profile.secret:
            memories.append(f"El día en que decidió ocultar que '{profile.secret}'")

        # Añadir algunos recuerdos genéricos si es necesario
        generic_memories = [
            "Un acto de bondad inesperado que cambió su perspectiva sobre la humanidad",
            "Un fracaso que le enseñó una lección valiosa sobre sí mismo",
            "Un momento de conexión profunda con alguien que ya no está en su vida",
            "Una decisión tomada bajo presión que aún le causa dudas",
            "Un logro temprano que estableció sus estándares de éxito personales"
        ]

        # Añadir hasta 3 recuerdos genéricos si tenemos menos de 3
        while len(memories) < 3 and generic_memories:
            memories.append(generic_memories.pop(random.randint(0, len(generic_memories)-1)))

        return memories[:5]  # Máximo 5 recuerdos clave

    def _generate_initial_relationships(self, role: str) -> dict[str, str]:
        """Genera relaciones iniciales básicas para el personaje."""
        relationships = {}

        # Relaciones básicas por rol
        if role == "protagonist":
            relationships = {
                "familia": "Relación compleja, mezcla de amor y responsabilidad",
                "mejor_amigo": "Confidente y contraparte, conoce sus fortalezas y debilidades",
                "interes_potencial": "Alguien que despierta emociones confusas y potencial romántico"
            }
        elif role == "antagonist":
            relationships = {
                "objetivo_venganza": "La persona o entidad que cree que le hizo daño",
                "aliado_reluctante": "Alguien que trabaja con él por conveniencia, no por lealtad",
                "figura_autoridad": "Alguien que representa el sistema o autoridad que él desafía"
            }
        elif role == "love_interest":
            relationships = {
                "protagonista": "Relación romántica central con potencial y obstáculos",
                "confidente": "Amigo íntimo al que le cuenta sus vulnerabilidades",
                "rival": "Alguien que compite por la misma atención o posición"
            }
        elif role == "mentor":
            relationships = {
                "protegido": "El personaje al que está guiando y desarrollando",
                "par_historico": "Alguien de su pasado con quien tiene asuntos sin resolver",
                "institución": "Organización o lugar que representa su vida laboral o de servicio"
            }

        return relationships

    def _determine_initial_emotional_state(self, profile: PsychologicalProfile) -> str:
        """Determina el estado emocional inicial basado en el perfil psicológico."""
        # Si el lie es fuerte, probablemente esté en defensiva o negación
        if profile.lie and ("suficiente" in profile.lie.lower() or "merecer" in profile.lie.lower()):
            return "anxious"  # Ansioso por ser descubierto

        # Si el ghost es reciente o poderoso, probablemente esté afectado por él
        if profile.ghost and any(word in profile.ghost.lower() for word in ["pérdida", "trauma", "abuso"]):
            return "sad"  # Triste o deprimido

        # Si tiene un want fuerte pero siente que no lo puede alcanzar, probablemente esté frustrado
        if profile.want and profile.need:
            if "poder" in profile.want.lower() or "control" in profile.want.lower():
                return "determined"  # Determinado a obtener lo que quiere
            elif "amor" in profile.want.lower() or "conexion" in profile.want.lower():
                return "hopeful"  # Esperanzado de encontrar conexión

        # Por defecto, basado en neuroticismo y otros factores
        if profile.neuroticism > 0.7:
            return "anxious"
        elif profile.extraversion > 0.7 and profile.agreeableness > 0.7:
            return "joyful"
        elif profile.openness > 0.8:
            return "curious"
        else:
            return "neutral"

    def _initialize_character_consistency_and_evolution(self, character: CharacterBrain, episode_number: int) -> None:
        """Inicializa los rasgos de consistencia y el camino de evolución."""
        # Rasgos de consistencia (cosas que NO deben cambiar fácilmente)
        character.consistency_tags = [
            character.character_id,  # ID nunca cambia
            f"name:{character.name}",  # Nombre es consistente (a menos que haya razón narrativa fuerte)
            f"archetype:{character.archetype}",  # Arquetipo básico es consistente
            f"role:{character.role}"  # Rol en la historia es consistente (a menos que haya cambio de rol importante)
        ]

        # Añadir rasgos psicológicos profundos que son consistentes
        if character.psychological_profile.lie:
            character.consistency_tags.append(f"lie:{character.psychological_profile.lie}")
        if character.psychological_profile.ghost:
            character.consistency_tags.append(f"ghost:{character.psychological_profile.ghost}")
        if character.psychological_profile.secret:
            character.consistency_tags.append(f"secret:{character.psychological_profile.secret}")

        # Inicializar camino de evolución
        character.evolution_path = [
            {
                "episode": episode_number,
                "stage": "introduction",
                "changes": ["Introducido al público"],
                "psychological_shifts": [],
                "relationship_changes": [],
                "key_events": []
            }
        ]

    def evolve_character(
        self,
        character: CharacterBrain,
        episode_number: int,
        story_events: list[dict[str, Any]],
        emotional_arc: Any | None = None
    ) -> CharacterBrain:
        """
        Evoluciona el personaje basado en los eventos del episodio y el arco emocional.

        Args:
            character: Personaje a evolucionar
            episode_number: Número del episodio actual
            story_events: Eventos importantes que sucedieron en el episodio
            emotional_arc: Arco emocional del episodio (si está disponible)

        Returns:
            El personaje evolucionado (se modifica in-place)
        """
        logger.info(f"Evolving character {character.name} for episode {episode_number}")

        # Actualizar timestamp
        character.updated_at = datetime.utcnow()
        character.usage_count += 1
        character.last_used_episode = episode_number

        # Analizar eventos para cambios psicológicos
        psychological_shifts = self._analyze_psychological_impact(
            character, story_events, emotional_arc
        )

        # Actualizar perfil psicológico basado en cambios
        self._apply_psychological_shifts(character, psychological_shifts)

        # Actualizar relaciones
        relationship_changes = self._analyze_relationship_impact(
            character, story_events
        )
        self._update_relationships(character, relationship_changes)

        # Actualizar estado emocional basado en el arco emocional del episodio
        if emotional_arc:
            self._update_emotional_state_from_arc(character, emotional_arc, episode_number)

        # Avanzar etapa de arco de personaje si es apropiado
        self._advance_character_arc_stage(character, episode_number, story_events)

        # Registrar esta evolución en el camino
        evolution_entry = {
            "episode": episode_number,
            "stage": character.psychological_profile.character_arc_stage,
            "changes": [shift["description"] for shift in psychological_shifts if shift["magnitude"] > 0.3],
            "psychological_shifts": psychological_shifts,
            "relationship_changes": relationship_changes,
            "key_events": [event.get("description", "") for event in story_events if event.get("impact", "") in ["high", "medium"]]
        }
        character.evolution_path.append(evolution_entry)

        logger.info(f"Character {character.name} evolved: {len(psychological_shifts)} psychological shifts applied")
        return character

    def _analyze_psychological_impact(
        self,
        character: CharacterBrain,
        story_events: list[dict[str, Any]],
        emotional_arc: Any | None
    ) -> list[dict[str, Any]]:
        """Analiza cómo los eventos del episodio impactan el perfil psicológico."""
        shifts = []

        for event in story_events:
            event_type = event.get("type", "")
            description = event.get("description", "")
            impact = event.get("impact", "low")  # low, medium, high

            # Skip eventos de bajo impacto para cambios psicológicos significativos
            if impact == "low":
                continue

            # Analizar tipo de evento para determinar qué aspecto psicológico afecta
            if event_type == "trauma" or event_type == "loss":
                # Evento traumático o de pérdida puede reforzar o cambiar el ghost
                if random.random() < 0.7:  # 70% de probabilidad de afectar el ghost
                    shifts.append({
                        "aspect": "ghost",
                        "description": f"El evento '{description}' reforzó su trauma de {character.psychological_profile.ghost}",
                        "magnitude": random.uniform(0.4, 0.8),
                        "direction": "reinforce"  # Puede ser reinforce, modify, overcome
                    })

            elif event_type == "revelation" or event_type == "truth_discovered":
                # Revelación de verdad puede desafiar el lie o el secret
                if character.psychological_profile.lie and random.random() < 0.6:
                    shifts.append({
                        "aspect": "lie",
                        "description": f"Descubrió evidencia que desafía su creencia de que '{character.psychological_profile.lie}'",
                        "magnitude": random.uniform(0.5, 0.9),
                        "direction": "challenge"
                    })

                if character.psychological_profile.secret and random.random() < 0.4:
                    shifts.append({
                        "aspect": "secret",
                        "description": f"Alguien descubrió o se acerca a descubrir su secreto: '{character.psychological_profile.secret}'",
                        "magnitude": random.uniform(0.6, 1.0),
                        "direction": "exposure_risk"
                    })

            elif event_type == "success" or event_type == "achievement":
                # Éxitos pueden afectar la necesidad o el want
                if character.psychological_profile.need and random.random() < 0.5:
                    shifts.append({
                        "aspect": "need",
                        "description": f"Logró progreso hacia su necesidad de '{character.psychological_profile.need}'",
                        "magnitude": random.uniform(0.3, 0.7),
                        "direction": "partial_fulfillment"
                    })

            elif event_type == "betrayal" or event_type == "conflict":
                # Traiciones o conflictos pueden afectar la confianza y el miedo
                if random.random() < 0.6:
                    shifts.append({
                        "aspect": "current_fear",
                        "description": f"El evento '{description}' intensificó su miedo a '{character.psychological_profile.current_fear}'",
                        "magnitude": random.uniform(0.4, 0.8),
                        "direction": "reinforce"
                    })

            elif event_type == "connection" or event_type == "intimacy":
                # Conexiones íntimas pueden afectar el estado emocional y las necesidades
                if random.random() < 0.5:
                    shifts.append({
                        "aspect": "emotional_state",
                        "description": "Experimentó una conexión significativa que afectó su estado emocional",
                        "magnitude": random.uniform(0.4, 0.7),
                        "direction": "shift_to_positive"  # Puede ser a joy, hope, romance, etc.
                    })

        return shifts

    def _apply_psychological_shifts(
        self,
        character: CharacterBrain,
        shifts: list[dict[str, Any]]
    ) -> None:
        """Aplica los cambios psicológicos al perfil del personaje."""
        for shift in shifts:
            aspect = shift["aspect"]
            description = shift["description"]
            magnitude = shift["magnitude"]
            direction = shift["direction"]

            # Aplicar cambio basado en el aspecto
            if aspect == "ghost":
                if direction == "reinforce":
                    # Refuerza el ghost (hace que sea más presente en la mente)
                    # En términos de perfil, podríamos aumentar la influencia del ghost en decisiones
                    # Por ahora, lo anotamos pero no cambiamos el valor del ghost directamente
                    pass  # El ghost en sí no cambia, pero su influencia sí
                elif direction == "modify":
                    # El evento cambia la naturaleza del trauma
                    # Esto sería más complejo - podríamos añadir matices al ghost
                    pass
                elif direction == "overcome":
                    # El personaje comienza a superar su trauma
                    pass

            elif aspect == "lie":
                if direction == "challenge":
                    # La mentira comienza a ser cuestionada
                    # Podríamos reducir ligeramente la creencia en la lie
                    # Por ahora, no cambiamos el valor de la lie, pero sí su influencia
                    pass
                elif direction == "break":
                    # La mentira se rompe completamente
                    pass

            elif aspect == "secret":
                if direction == "exposure_risk":
                    # Aumenta el riesgo de exposición del secreto
                    # Podríamos aumentar el stress_level
                    character.psychological_profile.stress_level = min(
                        1.0,
                        character.psychological_profile.stress_level + magnitude * 0.5
                    )
                elif direction == "exposed":
                    # El secreto se revela
                    # Esto tendría consecuencias masivas
                    pass

            elif aspect == "current_fear":
                if direction == "reinforce":
                    character.psychological_profile.current_fear = description.split("'")[1] if "'" in description else character.psychological_profile.current_fear
                elif direction == "shift":
                    # Cambia el miedo a algo nuevo relacionado con el evento
                    pass

            elif aspect == "emotional_state":
                if direction == "shift_to_positive":
                    # Cambiar a un estado emocional más positivo basado en el contexto
                    positive_emotions = ["joy", "hope", "romance", "relief", "contentment"]
                    character.psychological_profile.emotional_state = random.choice(positive_emotions)
                elif direction == "shift_to_negative":
                    negative_emotions = ["sadness", "anger", "fear", "anxiety", "despair"]
                    character.psychological_profile.emotional_state = random.choice(negative_emotions)
                elif direction == "shift_to_neutral":
                    character.psychological_profile.emotional_state = "neutral"

            elif aspect == "need":
                if direction == "partial_fulfillment":
                    # Avanzar parcialmente hacia satisfacer la necesidad
                    # Podríamos reducir la urgencia de la need
                    pass  # La need en sí no cambia, pero su urgencia sí
                elif direction == "fulfilled":
                    # La necesidad se ha satisfecho
                    pass  # En realidad, esto sería un cambio masivo en el arco de personaje

            elif aspect == "stress_level":
                # Cambiar directamente el nivel de estrés
                if direction == "increase":
                    character.psychological_profile.stress_level = min(
                        1.0,
                        character.psychological_profile.stress_level + magnitude
                    )
                elif direction == "decrease":
                    character.psychological_profile.stress_level = max(
                        0.0,
                        character.psychological_profile.stress_level - magnitude
                    )

    def _update_relationships(
        self,
        character: CharacterBrain,
        changes: list[dict[str, Any]]
    ) -> None:
        """Actualiza las relaciones del personaje basado en los cambios."""
        for change in changes:
            relation_type = change.get("type", "")
            description = change.get("description", "")
            # Esto sería más complejo en implementación real
            # Por ahora, solo registramos que hubo un cambio
            pass

    def _update_emotional_state_from_arc(
        self,
        character: CharacterBrain,
        emotional_arc: Any,
        episode_number: int
    ) -> None:
        """Actualiza el estado emocional basado en el arco emocional del episodio."""
        if not emotional_arc or not hasattr(emotional_arc, 'emotion_points'):
            return

        # Encontrar el punto emocional correspondiente a este episodio en el arco
        # Esto sería más complejo - necesitaríamos mapear episodio a tiempo en el arco
        # Por ahora, usamos una simplificación

        # Si el arco emocional tiene puntos, tomar el estado emocional promedio o final
        if emotional_arc.emotion_points:
            # Usar la emoción dominante del arco como influencia
            dominant_emotion = getattr(emotional_arc, 'dominant_emotion', 'neutral')
            # No reemplazamos completamente el estado emocional, sino que lo mezclamos
            current_state = character.psychological_profile.emotional_state

            # Si el estado actual es neutral, permitir que la emoción del arco tenga más influencia
            if current_state == "neutral":
                character.psychological_profile.emotional_state = dominant_emotion
            # Si hay conflicto, el estado actual gana (el personaje tiene su propia trayectoria)
            # Pero si el arco emocional es muy fuerte, puede sobrescribir
            elif dominant_emotion in ["joy", "hope", "romance"] and current_state in ["sad", "fear", "anger"]:
                # Emociones fuertes positivas pueden superar estados negativos temporales
                character.psychological_profile.emotional_state = dominant_emotion

    def _advance_character_arc_stage(
        self,
        character: CharacterBrain,
        episode_number: int,
        story_events: list[dict[str, Any]]
    ) -> None:
        """Avanza la etapa del arco de personaje basado en el progreso de la historia."""
        current_stage = character.psychological_profile.character_arc_stage

        # Definir las etapas típicas del arco de personaje
        stages = ["setup", "confrontation", "transformation", "resolution"]

        try:
            current_index = stages.index(current_stage)
        except ValueError:
            # Si la etapa actual no está en nuestra lista, asumimos setup
            current_index = 0
            character.psychological_profile.character_arc_stage = "setup"

        # Determinar si es tiempo de avanzar basado en:
        # 1. Episodio número (progresión a lo largo de la temporada)
        # 2. Eventos importantes que marcaron un giro
        # 3. Cambios psicológicos significativos

        # Factor de progresión estacional (asumiendo 20 episodios por temporada)
        season_progress = episode_number / 20.0  # Esto debería venir de parámetros externos

        # Eventos que indican transición de etapa
        transition_events = []
        for event in story_events:
            if event.get("type") in ["revelation", "betrayal", "death", "major_conflict", "sacrifice", "realization"]:
                transition_events.append(event)

        # Decidir si avanzar de etapa
        should_advance = False

        # Criterio 1: Hemos pasado suficiente tiempo en la temporada
        if season_progress > 0.25 and current_index == 0 or season_progress > 0.50 and current_index == 1 or season_progress > 0.75 and current_index == 2:  # Pasado el primer cuarto, listo para confrontation
            should_advance = True

        # Criterio 2: Eventos significativos de transición
        if len(transition_events) >= 2:  # Dos o más eventos importantes sugieren giro de etapa
            should_advance = True

        # Criterio 3: Cambios psicológicos profundos (esto sería más complejo de medir)
        # Por ahora, lo dejamos como factor secundario

        if should_advance and current_index < len(stages) - 1:
            new_stage = stages[current_index + 1]
            old_stage = character.psychological_profile.character_arc_stage
            character.psychological_profile.character_arc_stage = new_stage

            logger.info(f"Character {character.name} advanced arc stage: {old_stage} -> {new_stage}")

            # Al avanzar de etapa, podríamos resetear ciertos aspectos o permitir crecimiento
            if new_stage == "transformation":
                # En transformación, el personaje comienza a internalizar lecciones
                pass
            elif new_stage == "resolution":
                # En resolución, el personaje debería haber integrado su arco
                pass

    def get_character_summary(self, character: CharacterBrain) -> dict[str, Any]:
        """Obtiene un resumen legible del personaje para depuración o presentación."""
        return {
            "character_id": character.character_id,
            "name": character.name,
            "role": character.role,
            "archetype": character.archetype,
            "psychological_profile": {
                "want": character.psychological_profile.want,
                "need": character.psychological_profile.need,
                "lie": character.psychological_profile.lie,
                "ghost": character.psychological_profile.ghost,
                "secret": character.psychological_profile.secret,
                "emotional_state": character.psychological_profile.emotional_state,
                "stress_level": character.psychological_profile.stress_level,
                "character_arc_stage": character.psychological_profile.character_arc_stage
            },
            "consistency_tags": character.consistency_tags,
            "usage_count": character.usage_count,
            "last_used_episode": character.last_used_episode,
            "evolution_path_length": len(character.evolution_path)
        }

# Instancia singleton
character_brain = CharacterBrainAI()
