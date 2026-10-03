"""
Benchmark test for Prompt Compiler: verify Dense Temporal Matrix structure.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dorama_studio.pipeline.prompt_compiler import PromptCompiler, ShotSpec


def test_prompt_structure():
    compiler = PromptCompiler()
    shot = ShotSpec(
        shot_id="bench1",
        shot_type="CU",
        angle="eye_level",
        movement="push_in",
        lens="85mm f/1.4",
        characters=["protagonist_female"],
        emotion="joy",
        beat_name="Hook",
        duration_sec=10.0,
        dialogue="¡Hola mundo!",
        lighting={"key_light": "harsh side key", "fill_light": "minimal bounce"},
        sfx=["heartbeat"],
        ambience="silence",
        physics_details="fabric rustle",
        setting="intimate bedroom, night",
    )
    # Use dummy character refs (none) and palette
    compiled = compiler.compile(
        shot,
        "veo",
        character_refs=None,
        palette_hex=["#0A1128", "#FFDFC4", "#FFE49E", "#FF3344"],
    )
    prompt = compiled.prompt

    # Check for the five required sections
    required_sections = [
        r"\[HEADER\]",
        r"\[REFERENCE_LOCKS\]",
        r"\[TIMELINE\]",
        r"\[COLOR_LIGHTING_MATRIX\]",
        r"\[GENERATIVE_CONTROL\]",
    ]
    missing = []
    for section in required_sections:
        if not re.search(section, prompt, re.IGNORECASE):
            missing.append(section)

    # Check length (approx words)
    words = len(re.findall(r"\w+", prompt))
    print(f"Prompt word count: {words}")
    print(f"Missing sections: {missing}")
    print(f"Prompt preview (first 300 chars):\\n{prompt[:300]}")

    if missing:
        raise AssertionError(f"Missing sections: {missing}")
    if words < 120:
        raise AssertionError(
            f"Prompt too short: {words} words, expected at least 120 for Veo 3.1"
        )
    if words > 200:
        # Not failing, just warning
        print(f"Warning: prompt length {words} words, exceeds typical upper bound 200.")

    print("Benchmark PASSED: Prompt has all five sections and reasonable length.")


if __name__ == "__main__":
    test_prompt_structure()
