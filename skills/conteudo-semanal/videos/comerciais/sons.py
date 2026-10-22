"""Efeitos sonoros e ambiente sintetizados por código (sem bancos de som, sem direitos autorais).

Uso no episodio.json:  "sons": [{"t": 0, "tipo": "ambiente_rua", "dur": 9}, {"t": 5.2, "tipo": "porta_enrolar"}]
Tipos: ambiente_rua, ambiente_loja, passos, porta_enrolar, sino, caixa, sacola, transicao.
"""
import numpy as np

SR = 24000
RNG = np.random.default_rng(7)


def _banda(x, lo, hi):
    """filtro passa-faixa por FFT"""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x)).astype(np.float32)


def _env(n, ataque=0.01, queda=0.2):
    t = np.arange(n) / SR
    return (np.minimum(1, t / max(ataque, 1e-4)) * np.exp(-t / max(queda, 1e-4))).astype(np.float32)


def _norm(x, nivel):
    m = np.max(np.abs(x)) or 1
    return (x / m * nivel).astype(np.float32)


def ambiente_rua(dur=8.0):
    n = int(dur * SR); t = np.arange(n) / SR
    base = _banda(RNG.standard_normal(n), 80, 900) * 0.6 + _banda(RNG.standard_normal(n), 900, 3000) * 0.15
    x = _norm(base, 0.05)
    for _ in range(int(dur * 0.9)):  # passarinhos
        t0 = RNG.uniform(0, max(0.1, dur - 0.5)); m = int(0.09 * SR); i0 = int(t0 * SR)
        for k in range(RNG.integers(2, 4)):
            j = i0 + k * int(0.13 * SR)
            if j + m >= n: break
            tt = np.arange(m) / SR; fq = RNG.uniform(3200, 4500)
            x[j:j + m] += 0.04 * np.sin(2 * np.pi * (fq + 1800 * tt / 0.09) * tt) * np.hanning(m)
    if dur > 3:  # um carro passando ao longe
        c = _banda(RNG.standard_normal(n), 60, 500)
        x += _norm(c, 0.05) * np.exp(-((t - dur * 0.6) / 1.2) ** 2)
    fade = np.minimum(1, np.minimum(t / 0.4, (dur - t) / 0.4))
    return (x * fade).astype(np.float32)


def ambiente_loja(dur=8.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = _norm(_banda(RNG.standard_normal(n), 60, 400), 0.035)
    x += 0.008 * np.sin(2 * np.pi * 120 * t)  # zumbido leve de geladeira/luminária
    fade = np.minimum(1, np.minimum(t / 0.4, (dur - t) / 0.4))
    return (x * fade).astype(np.float32)


def passos(dur=2.0, ritmo=0.5):
    n = int(dur * SR); x = np.zeros(n, np.float32); m = int(0.07 * SR)
    for i, k in enumerate(np.arange(0, dur - 0.08, ritmo)):
        j = int(k * SR); s = _banda(RNG.standard_normal(m), 150, 1800) * _env(m, 0.002, 0.02)
        x[j:j + m] += _norm(s, 0.22 if i % 2 else 0.18)
    return x


def porta_enrolar(dur=1.4):
    n = int(dur * SR); t = np.arange(n) / SR
    chacoalho = (np.sin(2 * np.pi * 22 * t) > 0.3).astype(np.float32)
    metal = _banda(RNG.standard_normal(n), 700, 3500) * chacoalho
    zumbido = np.sin(2 * np.pi * (180 + 60 * t / dur) * t) * 0.3
    x = _norm(metal + zumbido, 0.32)
    fim = int(0.12 * SR); x[-fim:] += _norm(_banda(RNG.standard_normal(fim), 100, 900) * _env(fim, 0.002, 0.05), 0.35)
    return (x * np.minimum(1, (dur - t) / 0.1 + 0.2)).astype(np.float32)


def sino(dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n, np.float32)
    for k, (fq, t0) in enumerate(((1318.5, 0.0), (1046.5, 0.18))):
        j = int(t0 * SR); tt = t[: n - j]
        x[j:] += (np.sin(2 * np.pi * fq * tt) + 0.3 * np.sin(2 * np.pi * fq * 2.76 * tt)) * np.exp(-tt / 0.35)
    return _norm(x, 0.22)


def caixa(dur=0.8):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 2093 * t) * np.exp(-t / 0.18)
    m = int(0.04 * SR); x[:m] += _banda(RNG.standard_normal(m), 1500, 6000) * _env(m, 0.001, 0.01)
    return _norm(x, 0.2)


def sacola(dur=0.6):
    n = int(dur * SR); x = _banda(RNG.standard_normal(n), 2000, 9000)
    x *= (RNG.random(n) < 0.15).astype(np.float32) * 0.6 + 0.2
    return _norm(x * _env(n, 0.02, 0.25), 0.14)


def transicao(dur=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    x = _banda(RNG.standard_normal(n), 300, 5000) * np.sin(np.pi * t / dur) ** 2
    return _norm(x, 0.1)


TIPOS = {"ambiente_rua": ambiente_rua, "ambiente_loja": ambiente_loja, "passos": passos, "porta_enrolar": porta_enrolar,
         "sino": sino, "caixa": caixa, "sacola": sacola, "transicao": transicao}


def trilha_sons(lista, duracao, sr=SR):
    out = np.zeros(int(duracao * sr), np.float32)
    for s in lista:
        kw = {k: v for k, v in s.items() if k in ("dur", "ritmo")}
        x = TIPOS[s["tipo"]](**kw)
        x = x * s.get("volume", 1.0)
        i = int(s["t"] * sr); out[i:i + len(x)] += x[: max(0, len(out) - i)]
    return out
