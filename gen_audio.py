#!/usr/bin/env python3
"""Pré-génère les dictées audio des nombres avec Kokoro (voix ff_siwis).

Sortie : maths/audio/<nombre>.mp3 + maths/audio/numbers.json
Chaque entrée : {"n": "127001", "f": "127001.mp3", "w": "cent vingt-sept mille un"}
"""
import json
import pathlib
import random
import subprocess
import urllib.request

API = "http://127.0.0.1:8880/v1/audio/speech"
VOICE = "ff_siwis"
OUT = pathlib.Path("/root/clawd/maths/audio")
OUT.mkdir(parents=True, exist_ok=True)

UNITS = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
         "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize",
         "dix-sept", "dix-huit", "dix-neuf"]
TENS = ["", "", "vingt", "trente", "quarante", "cinquante", "soixante"]


def b100(x):
    if x < 20:
        return UNITS[x]
    d, r = divmod(x, 10)
    if d == 7:
        return "soixante" + ("-et-" if r == 1 else "-") + UNITS[10 + r]
    if d == 9:
        return "quatre-vingt-" + UNITS[10 + r]
    if d == 8:
        return "quatre-vingt" + ("s" if r == 0 else "-" + UNITS[r])
    if r == 0:
        return TENS[d]
    if r == 1:
        return TENS[d] + "-et-un"
    return TENS[d] + "-" + UNITS[r]


def b1000(x):
    if x < 100:
        return b100(x)
    c, r = divmod(x, 100)
    head = "cent" if c == 1 else UNITS[c] + " cent" + ("s" if r == 0 else "")
    return head + (" " + b100(r) if r else "")


def fr_num(n):
    if n == 0:
        return "zéro"
    parts = []
    m, rest = divmod(n, 1_000_000)
    k, r = divmod(rest, 1000)
    if m:
        parts.append("un million" if m == 1 else b1000(m) + " millions")
    if k:
        parts.append("mille" if k == 1 else b1000(k) + " mille")
    if r:
        parts.append(b1000(r))
    return " ".join(parts)


def synth(text, dest_wav):
    body = json.dumps({
        "model": "kokoro", "input": text, "voice": VOICE,
        "speed": 0.92, "response_format": "wav",
    }).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        dest_wav.write_bytes(r.read())


def main():
    rnd = random.Random(20261026)
    nums = set()
    # 3 à 7 chiffres, réparti
    for length, count in [(3, 18), (4, 22), (5, 24), (6, 24), (7, 12)]:
        while sum(1 for x in nums if len(x) == length) < count:
            s = str(rnd.randint(1, 9)) + "".join(str(rnd.randint(0, 9)) for _ in range(length - 1))
            nums.add(s)

    entries = []
    ok = 0
    for i, n in enumerate(sorted(nums, key=lambda x: (len(x), x)), 1):
        wav = OUT / f"{n}.wav"
        mp3 = OUT / f"{n}.mp3"
        words = fr_num(int(n))
        try:
            if not mp3.exists():
                synth(words, wav)
                subprocess.run(
                    ["ffmpeg", "-v", "quiet", "-y", "-i", str(wav),
                     "-ac", "1", "-ar", "24000", "-b:a", "48k", str(mp3)],
                    check=True,
                )
                wav.unlink(missing_ok=True)
            entries.append({"n": n, "f": f"{n}.mp3", "w": words})
            ok += 1
            if i % 10 == 0:
                print(f"{i}/{len(nums)}", flush=True)
        except Exception as e:
            print("ERR", n, e, flush=True)
            wav.unlink(missing_ok=True)

    (OUT / "numbers.json").write_text(
        json.dumps(entries, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    total = sum(f.stat().st_size for f in OUT.glob("*.mp3"))
    print(f"DONE {ok} clips, {total/1024:.0f} Ko", flush=True)


if __name__ == "__main__":
    main()
