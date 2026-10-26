#!/usr/bin/env python3
"""Regénère les dictées audio avec edge-tts (voix neuronale Microsoft)."""
import pathlib, subprocess, sys
sys.path.insert(0, "/root/clawd/maths")
from gen_audio import fr_num

VOICE = "fr-FR-DeniseNeural"
RATE = "-5%"
OUT = pathlib.Path("/root/clawd/maths/audio")
EDGE = "/opt/whisper-venv/bin/edge-tts"

files = sorted([p for p in OUT.glob("*.mp3") if p.stem.isdigit()], key=lambda p: (len(p.stem), p.stem))
print("clips:", len(files), flush=True)
ok = 0
for i, p in enumerate(files, 1):
    text = fr_num(int(p.stem))
    tmp = p.with_suffix(".new.mp3")
    try:
        subprocess.run([EDGE, "--voice", VOICE, f"--rate={RATE}",
                        "--text", text, "--write-media", str(tmp)],
                       check=True, capture_output=True, timeout=60)
        if tmp.stat().st_size > 1000:
            tmp.replace(p); ok += 1
        else:
            tmp.unlink(missing_ok=True)
    except Exception as e:
        tmp.unlink(missing_ok=True)
        print("ERR", p.stem, e, flush=True)
    if i % 20 == 0:
        print(f"{i}/{len(files)}", flush=True)
print(f"DONE {ok}/{len(files)}", flush=True)
