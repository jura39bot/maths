#!/usr/bin/env python3
"""Génère les versions lentes (débit -25%) avec la même voix naturelle."""
import pathlib, subprocess, sys
sys.path.insert(0, "/root/clawd/maths")
from gen_audio import fr_num

VOICE = "fr-FR-DeniseNeural"
RATE = "-25%"
OUT = pathlib.Path("/root/clawd/maths/audio/slow")
EDGE = "/opt/whisper-venv/bin/edge-tts"

nums = sorted([p.stem for p in pathlib.Path("/root/clawd/maths/audio").glob("*.mp3") if p.stem.isdigit()],
              key=lambda x: (len(x), x))
print("clips:", len(nums), flush=True)
ok = 0
for i, n in enumerate(nums, 1):
    dest = OUT / f"{n}.mp3"
    if dest.exists() and dest.stat().st_size > 1000:
        ok += 1; continue
    tmp = OUT / f"{n}.new.mp3"
    try:
        subprocess.run([EDGE, "--voice", VOICE, f"--rate={RATE}",
                        "--text", fr_num(int(n)), "--write-media", str(tmp)],
                       check=True, capture_output=True, timeout=60)
        if tmp.stat().st_size > 1000:
            tmp.replace(dest); ok += 1
        else:
            tmp.unlink(missing_ok=True)
    except Exception as e:
        tmp.unlink(missing_ok=True)
        print("ERR", n, e, flush=True)
    if i % 20 == 0: print(f"{i}/{len(nums)}", flush=True)
print(f"DONE {ok}/{len(nums)}", flush=True)
