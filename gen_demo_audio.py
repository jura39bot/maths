#!/usr/bin/env python3
"""Génère les 10 narrations de la leçon animée avec edge-tts (voix Denise)."""
import pathlib
import subprocess

OUT = pathlib.Path("/root/clawd/maths/audio/demo")
OUT.mkdir(parents=True, exist_ok=True)
EDGE = "/opt/whisper-venv/bin/edge-tts"
VOICE = "fr-FR-DeniseNeural"

CLIPS = {
    # Addition 845 + 327
    "a0": "On aligne les nombres : unités sous unités, dizaines sous dizaines, centaines sous centaines.",
    "a1": "Unités : 5 plus 7 égale 12. J'écris 2, et je retiens 1 au-dessus des dizaines.",
    "a2": "Dizaines : 4 plus 2, plus 1 de retenue, égale 7. J'écris 7, rien à retenir.",
    "a3": "Centaines : 8 plus 3 égale 11. J'écris 11, le 1 des dizaines passe dans la colonne des milliers.",
    "a4": "Résultat : 845 plus 327 égale 1 172.",
    # Soustraction 734 - 258
    "s0": "On aligne les nombres comme pour l'addition.",
    "s1": "Unités : 4 moins 8, impossible. J'emprunte une dizaine : 14 moins 8 égale 6. Je note la retenue au-dessus du 3.",
    "s2": "Dizaines : 3 moins 1 égale 2. 2 moins 5, impossible : j'emprunte aux centaines. 12 moins 5 égale 7.",
    "s3": "Centaines : 7 moins 1 égale 6. 6 moins 2 égale 4.",
    "s4": "Résultat : 734 moins 258 égale 476. Vérification : 476 plus 258 égale 734. C'est juste.",
}

ok = 0
for k, txt in CLIPS.items():
    dest = OUT / f"{k}.mp3"
    if dest.exists() and dest.stat().st_size > 1000:
        ok += 1
        continue
    tmp = OUT / f"{k}.new.mp3"
    try:
        subprocess.run([EDGE, "--voice", VOICE, "--rate=-5%", "--text", txt,
                        "--write-media", str(tmp)], check=True, capture_output=True, timeout=90)
        if tmp.stat().st_size > 1000:
            tmp.replace(dest)
            ok += 1
            print("ok", k, dest.stat().st_size)
        else:
            tmp.unlink(missing_ok=True)
            print("petit", k)
    except Exception as e:
        tmp.unlink(missing_ok=True)
        print("ERR", k, e)

print(f"DONE {ok}/{len(CLIPS)}")
