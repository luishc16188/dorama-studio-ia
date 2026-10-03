# dorama_studio/pipeline/compile_test.py
# Demo script that compiles a ShotSpec and runs the linter

from dorama_studio.pipeline.prompt_compiler import PromptCompiler, ShotSpec
from dorama_studio.pipeline.prompt_linter import validate

if __name__ == "__main__":
    compiler = PromptCompiler()
    shot = ShotSpec(
        shot_id="demo_1",
        shot_type="CU",
        angle="eye_level",
        movement="push_in",
        lens="85mm f/1.4",
        characters=["protagonist_female"],
        emotion="joy",
        beat_name="Hook",
        dialogue="¡Hola mundo!",
    )
    compiled = compiler.compile(shot, "veo", character_refs=None)
    errors = validate(compiled.prompt, "veo")
    if errors:
        print("Linter errors:", errors)
    else:
        print("Compiled prompt OK:")
        print(compiled.prompt[:500])
        print("...")
