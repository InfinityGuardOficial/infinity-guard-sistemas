"""Narração com voz sintética gratuita (Kokoro, pt-BR) a partir de <video>/narracao.json.

narracao.json: {"voz": "pm_alex", "velocidade": 0.95,
                "frases": [{"cena": 1, "texto": "como aparece na legenda", "fala": "como a voz deve ler (opcional)"}]}
Use "fala" para palavras que a voz pronuncia errado (ex.: "uótsápi" para WhatsApp, "Massimiliano").
Gera em <video>/build/: narracao.wav, marks.json (tempo de cada frase) e audio_final.wav (voz + trilha suave).
Cada frase é gerada inteira e separada por pausa, então nenhuma palavra é cortada.
"""
import json, os, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

AQUI = os.path.dirname(os.path.abspath(__file__))
video = os.path.abspath(sys.argv[1])
build = os.path.join(video, "build"); os.makedirs(build, exist_ok=True)
cfg = json.load(open(os.path.join(video, "narracao.json")))
k = Kokoro(os.path.join(AQUI, "modelos", "kokoro-v1.0.onnx"), os.path.join(AQUI, "modelos", "voices-v1.0.bin"))

PAUSA_CENA, PAUSA_FRASE, FIM = 0.55, 0.28, 0.8
frases = cfg["frases"]
sr = 24000; out = [np.zeros(int(sr * 0.6), np.float32)]; t = 0.6; marks = []
for i, f in enumerate(frases):
    s, sr = k.create(f.get("fala") or f["texto"], voice=cfg.get("voz", "pm_alex"), speed=cfg.get("velocidade", 0.95), lang="pt-br")
    s = s.astype(np.float32)
    idx = np.where(np.abs(s) > 0.01)[0]
    s = s[max(0, idx[0] - int(sr * 0.06)):idx[-1] + int(sr * 0.12)]  # apara silêncio, com folga
    d = len(s) / sr
    marks.append({"cena": f["cena"], "texto": f["texto"], "ini": round(t, 3), "fim": round(t + d, 3)})
    out.append(s); t += d
    p = FIM if i + 1 == len(frases) else (PAUSA_CENA if frases[i + 1]["cena"] != f["cena"] else PAUSA_FRASE)
    out.append(np.zeros(int(sr * p), np.float32)); t += p
voz = np.concatenate(out); voz = voz / np.max(np.abs(voz)) * 0.89
sf.write(os.path.join(build, "narracao.wav"), voz, sr)
json.dump(marks, open(os.path.join(build, "marks.json"), "w"), ensure_ascii=False, indent=1)

# trilha ambiente suave (Am F C G), gerada por código, sem direitos autorais
T = len(voz) / sr + 4.5; n = int(T * sr); tt = np.arange(n) / sr
nota = lambda m: 440 * 2 ** ((m - 69) / 12)
prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]
pad = np.zeros(n)
for i in range(int(T / 4) + 1):
    a, b = int(i * 4 * sr), min(n, int((i * 4 + 4.6) * sr))
    if a >= n: break
    x = np.arange(b - a) / sr; env = np.minimum(1, x / 1.2) * np.minimum(1, (b - a) / sr - x + 0.01)
    for m in prog[i % 4]:
        fq = nota(m); pad[a:b] += env * (np.sin(2 * np.pi * fq * x) + 0.3 * np.sin(4 * np.pi * fq * x) + 0.15 * np.sin(2 * np.pi * fq * 1.003 * x))
pad = pad / np.max(np.abs(pad)) * 0.07 * np.minimum(1, tt / 2) * np.minimum(1, (T - tt) / 2.5)
mix = pad.copy(); mix[:len(voz)] += voz
mix /= max(1, np.max(np.abs(mix)) / 0.95)
sf.write(os.path.join(build, "audio_final.wav"), mix.astype(np.float32), sr)
print(f"narração: {t:.1f} s · vídeo: {T:.1f} s")
for m in marks: print(m["cena"], m["ini"], m["fim"], m["texto"][:50])
