# dorama_studio/pipeline/prompt_linter.py
"""
Prompt Linter for Dorama Studio - validates Dense Temporal Matrix prompts.
Checks:
* Prohibited keywords.
* Prompt length for Veo 3.1.
* Presence of the five required sections: [HEADER], [REFERENCE_LOCKS], [TIMELINE],
  [COLOR_LIGHTING_MATRIX], [GENERATIVE_CONTROL].
* Each line ends with newline and no inline comments.
"""

import re


class PromptLinterError(Exception):
    pass


# Configuration according to 06_PROMPT_LINTER.md
PROHIBITED_KEYWORDS = [
    "masterpiece",
    "4k",
    "8k",
    "trending",
    "best quality",
    "ultra-detailed",
]

# Max words for Veo 3.1
MAX_WORDS_VEO_3_1 = 180

# Required section headers for Dense Temporal Matrix
REQUIRED_SECTIONS = [
    r"\[HEADER\]",
    r"\[REFERENCE_LOCKS\]",
    r"\[TIMELINE\]",
    r"\[COLOR_LIGHTING_MATRIX\]",
    r"\[GENERATIVE_CONTROL\]",
]


def validate(prompt: str, model: str) -> list[str]:
    """Validate the prompt.

    Returns a list of error messages; empty list means success.
    """
    errors = []

    # 1. Prohibited keywords
    for kw in PROHIBITED_KEYWORDS:
        if kw in prompt.lower():
            errors.append(f'Keyword "{kw}" is prohibited')

    # 2. Length check for Veo 3.1
    if model == "veo" or model.startswith("veo"):
        word_count = len(re.findall(r"\w+", prompt))
        if word_count > MAX_WORDS_VEO_3_1:
            errors.append(f"Prompt length {word_count} exceeds max {MAX_WORDS_VEO_3_1}")

    # 3. Required sections
    for section in REQUIRED_SECTIONS:
        if not re.search(section, prompt, re.IGNORECASE):
            errors.append(f"Missing section:{section}")

    # 4. Each line ends with \n and no inline comments
    for i, line in enumerate(prompt.splitlines(), 1):
        if line.strip().startswith("#"):
            errors.append(f"Inline comment at line {i}")

    return errors


# Example usage
if __name__ == "__main__":
    from dorama_studio.pipeline.prompt_compiler import PromptCompiler, ShotSpec

    compiler = PromptCompiler()
    shot = ShotSpec(
        shot_id="t1",
        shot_type="CU",
        angle="eye_level",
        movement="push_in",
        lens="85mm f/1.4",
        characters=["protagonist_female"],
        emotion="joy",
        beat_name="Hook",
        dialogue="¡Hola!",
    )
    compiled = compiler.compile(shot, "veo")
    errs = validate(compiled.prompt, "veo")
    print("Errors:", errs)
    if not errs:
        print("Compiled prompt OK (first 500 chars):")
        print(compiled.prompt[:500])
