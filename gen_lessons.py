#!/usr/bin/env python3
"""Génère la narration des cours animés (une voix Denise par étape de leçon)."""
import json, pathlib, subprocess

OUT = pathlib.Path("/root/clawd/maths/audio/lessons"); OUT.mkdir(parents=True, exist_ok=True)
EDGE = "/opt/whisper-venv/bin/edge-tts"; VOICE = "fr-FR-DeniseNeural"
data = json.loads(pathlib.Path("/root/clawd/maths/src_lessons.json").read_text(encoding="utf-8"))
total = sum(len(c["steps"]) for c in data)
print("steps", total, flush=True)
n = 0; ok = 0
for c in data:
    for i, st in enumerate(c["steps"]):
        n += 1
        dest = OUT / f'{c["id"]}_{i}.mp3'
        if dest.exists() and dest.stat().st_size > 800:
            ok += 1; continue
        txt = f'{st["h"]}. {st["p"]}'
        tmp = OUT / f'_{c["id"]}_{i}.tmp.mp3'
        try:
            subprocess.run([EDGE, "--voice", VOICE, "--rate=-4%", "--text", txt,
                            "--write-media", str(tmp)], check=True, capture_output=True, timeout=90)
            if tmp.stat().st_size > 800:
                tmp.replace(dest); ok += 1
            else:
                tmp.unlink(missing_ok=True)
        except Exception as e:
            tmp.unlink(missing_ok=True); print("ERR", c["id"], i, e, flush=True)
        if n % 15 == 0: print(f"{n}/{total}", flush=True)
print(f"DONE {ok}/{total}", flush=True)
