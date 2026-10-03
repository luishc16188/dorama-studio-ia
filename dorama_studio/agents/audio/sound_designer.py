# dorama_studio/agents/audio/sound_designer.py
"""
Sound Designer Agent - Creates sound effect layers based on script and emotional context.
"""

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import Script, SFXLayer, SoundDesignerAgentOutputSchema

logger = logging.getLogger(__name__)


class SoundDesignerAgent(BaseAgent[Script, SoundDesignerAgentOutputSchema]):
    """
    Sound Designer Agent that takes a script and generates sound effect layers.
    """

    InputSchema = Script
    OutputSchema = SoundDesignerAgentOutputSchema

    def __init__(self):
        super().__init__("SoundDesignerAgent")

    def process(self, validated_input: Script) -> SoundDesignerAgentOutputSchema:
        """
        Process script to generate sound effect layers.

        Args:
            validated_input: Script containing scene details

        Returns:
            SoundDesignerAgentOutputSchema with SFX layers
        """
        logger.info(f"Processing sound design for scene {validated_input.scene_number}")

        # In a real implementation, this would:
        # 1. Analyze the script for sound opportunities (events, actions, emotions)
        # 2. Map to appropriate sound effects from a library
        # 3. Layer sounds (ambience, Foley, etc.) with timing and volume
        # 4. Ensure audio consistency and quality

        # For now, we'll create a structured output based on script content
        sfx_layers = []

        # Combine dialogue and action for analysis
        combined_text = f"{validated_input.dialogue} {validated_input.action}".lower()

        # Define sound effect mappings based on keywords
        sfx_mapping = [
            # (keywords, description, sound_file, volume, duration_estimate, priority_tags)
            (
                ["door", "open", "close", "knock"],
                "Door knock or opening/closing",
                "door_knock.wav",
                0.7,
                1.0,
                ["foley"],
            ),
            (
                ["footsteps", "walking", "running", "steps", "tacones"],
                "Footsteps (tactile)",
                "footsteps_concrete.wav",
                0.7,
                2.0,
                ["foley", "amplified"],
            ),
            (
                ["rain", "storm", "thunder"],
                "Rain and thunder ambience",
                "rain_thunder.wav",
                0.6,
                5.0,
                ["ambience"],
            ),
            (
                ["sword", "fight", "battle", "clash"],
                "Metal clash and sword fight",
                "sword_clash.wav",
                0.8,
                1.5,
                ["impact"],
            ),
            (
                ["glass", "break", "shatter", "copa"],
                "Breaking glass (DramaBox Ear-Candy)",
                "glass_break_high_fidelity.wav",
                0.95,
                0.5,
                ["ear_candy", "impact", "amplified"],
            ),
            (
                ["pearl", "perla", "jewelry", "anillo", "necklace"],
                "Jewelry/Pearl scattering on marble",
                "pearl_scatter_marble.wav",
                0.85,
                1.5,
                ["ear_candy", "foley", "amplified"],
            ),
            (
                ["silk", "seda", "pañuelo", "vestido", "abrigo"],
                "Silk/Fabric rustle (tactile)",
                "silk_rustle_hq.wav",
                0.75,
                1.0,
                ["foley", "amplified"],
            ),
            (
                ["paper", "papel", "billete", "documento", "fajo"],
                "Paper/Money crisp rustle",
                "paper_rustle_money.wav",
                0.7,
                0.5,
                ["foley", "amplified"],
            ),
            (
                ["car", "engine", "drive"],
                "Car engine and driving",
                "car_engine_loop.wav",
                0.4,
                3.0,
                ["ambience"],
            ),
            (
                ["phone", "ring", "call"],
                "Phone ringing",
                "phone_ring.wav",
                0.6,
                2.0,
                ["foley"],
            ),
            (
                ["alarm", "siren", "alert"],
                "Alarm or siren",
                "alarm_siren.wav",
                0.8,
                3.0,
                ["ambience"],
            ),
            (
                ["heartbeat", "pulse", "latido"],
                "Heartbeat sound (tension)",
                "heartbeat_40hz.wav",
                0.6,
                4.0,
                ["impact", "sub_bass"],
            ),
            (
                ["wind", "breeze"],
                "Wind ambience",
                "wind_ambience.wav",
                0.3,
                5.0,
                ["ambience"],
            ),
            (
                ["fire", "burn"],
                "Fire crackling",
                "fire_crackle.wav",
                0.4,
                3.0,
                ["ambience"],
            ),
            (
                ["water", "splash", "wave"],
                "Water splash or waves",
                "water_splash.wav",
                0.6,
                1.0,
                ["foley"],
            ),
            (
                ["crowd", "people", "chatter"],
                "Background crowd chatter",
                "crowd_chatter.wav",
                0.4,
                4.0,
                ["ambience"],
            ),
            (["laugh", "laughter"], "Laughter", "laughter.wav", 0.5, 1.0, ["voice"]),
            (
                ["cry", "crying", "sob"],
                "Crying or sobbing",
                "crying.wav",
                0.5,
                2.0,
                ["voice"],
            ),
            (
                ["punch", "hit", "slap"],
                "Punch or hit impact",
                "punch_impact.wav",
                0.7,
                0.3,
                ["impact"],
            ),
            (
                ["explosion", "blast"],
                "Explosion",
                "explosion.wav",
                0.9,
                2.0,
                ["impact"],
            ),
            (
                ["shock", "reveal", "revelación", "status", "alerta", "reloj", "patek"],
                "Status shock/Reveal (Sub-bass 40Hz)",
                "stinger_40hz_shock.wav",
                1.0,
                1.0,
                ["impact", "sub_bass", "ear_candy"],
            ),
        ]

        # Generate SFX layers based on detected keywords
        layer_id_counter = 1
        current_time = 0.0  # Start time in seconds

        for (
            keywords,
            description,
            sound_file,
            base_volume,
            duration,
            tags,
        ) in sfx_mapping:
            if any(keyword in combined_text for keyword in keywords):
                # Adjust volume based on priority tags (DramaBox/OASIZ patterns)
                volume = base_volume
                if "amplified" in tags:
                    volume = min(1.0, volume * 1.3)  # Boost amplified foley
                if "sub_bass" in tags:
                    volume = 1.0  # Maximize impact stingers

                if "angry" in combined_text or "fight" in combined_text:
                    volume = min(1.0, volume * 1.1)
                elif "sad" in combined_text or "scared" in combined_text:
                    volume = max(0.1, volume * 0.9)

                sfx_layer = SFXLayer(
                    layer_id=f"sfx_{layer_id_counter:03d}",
                    description=f"{description} [{'|'.join(tags)}]",
                    sound_file=sound_file,
                    volume=volume,
                    start_time=current_time,
                    end_time=current_time + duration,
                )
                sfx_layers.append(sfx_layer)
                layer_id_counter += 1
                current_time += 0.2  # Tight overlap for fast pace

        # If no SFX detected, add a default ambience
        if not sfx_layers:
            sfx_layer = SFXLayer(
                layer_id="sfx_001",
                description="Default room tone ambience",
                sound_file="room_tone.wav",
                volume=0.2,
                start_time=0.0,
                end_time=5.0,
            )
            sfx_layers.append(sfx_layer)

        # Create output schema instance
        output = SoundDesignerAgentOutputSchema(sfx_layers=sfx_layers)

        return output
