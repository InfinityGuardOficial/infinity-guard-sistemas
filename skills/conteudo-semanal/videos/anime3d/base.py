"""Base visual dos vídeos animados: tempo das falas, legendas, textos, celular, foto, efeitos de anime,
cartela final e o motor que monta o MP4 (quadros 3D + sobreposições + áudio).

Cada vídeo tem um `montagem.py` que define as cenas (FN = {1: s1, 2: s2, ...}) e chama `base.main(FN)`.
Lê de <video>/build/: marks.json, audio_final.wav e shots/<TOMADA>/####.png.
"""
import json, math, os, re, subprocess, sys
from functools import lru_cache
import numpy as np, skia
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.abspath(os.environ["VIDEO_DIR"])
BUILD = os.path.join(VIDEO, "build")
SHOTS = os.path.join(BUILD, "shots")
FOTO = os.path.join(AQUI, "..", "ref-maximiliano.jpg")
LOGO_ARQ = os.path.join(AQUI, "..", "logo-infinity-guard.jpg")
W, H, FPS = 1080, 1920, 24
SFPS = 12  # tomadas 3D animadas "em dois"
AUDIO = os.path.join(BUILD, "audio_final.wav")

# ---------------- tempo ----------------
MARKS = json.load(open(os.path.join(BUILD, "marks.json")))
AUDIO_T = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO],
                               capture_output=True, text=True).stdout.strip())

scenes = {}
for m in MARKS:
    scenes.setdefault(m["cena"], [m["ini"], m["fim"]])
    scenes[m["cena"]][1] = m["fim"]
order = sorted(scenes)
SC = {}
for i, c in enumerate(order):
    st = 0 if i == 0 else scenes[c][0] - 0.25
    SC[c] = st
END_CARD = MARKS[-1]["fim"] + 0.6
BOUNDS = [(c, SC[c], (SC[order[i + 1]] if i + 1 < len(order) else END_CARD)) for i, c in enumerate(order)]
TOTAL = AUDIO_T

def mark_t(cena, k):  # start time of k-th sentence of a scene
    return [m for m in MARKS if m["cena"] == cena][k]["ini"]

# subtitles: split sentences into chunks of whole words
SUBS = []
for i, m in enumerate(MARKS):
    words = m["texto"].split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 8 or (w.endswith(",") and len(cur) >= 4):
            chunks.append(cur); cur = []
    if cur:
        if chunks and len(cur) <= 2:
            chunks[-1] += cur
        else:
            chunks.append(cur)
    tot = sum(len(" ".join(c)) for c in chunks)
    t = m["ini"]
    nxt = MARKS[i + 1]["ini"] if i + 1 < len(MARKS) else m["fim"] + 0.6
    for j, c in enumerate(chunks):
        d = (m["fim"] - m["ini"]) * len(" ".join(c)) / tot
        end = t + d if j < len(chunks) - 1 else min(nxt, m["fim"] + 0.5)
        SUBS.append((t - 0.05, end, " ".join(c)))
        t += d


# ---------------- style ----------------
def col(h, a=255):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(a))

NAVY, NAVY2, GOLD, GOLD2, CREAM = "#0a1630", "#13264a", "#d4aa52", "#f0d48a", "#f5f1e8"
FD = os.path.join(AQUI, "fonts") + "/"
TF = {k: skia.Typeface.MakeFromFile(FD + f) for k, f in
      {"m5": "Montserrat-500.ttf", "m7": "Montserrat-700.ttf", "m8": "Montserrat-800.ttf", "pf": "Playfair-700.ttf", "cv": "Caveat-600.ttf"}.items()}

def font(k, s): return skia.Font(TF[k], s)

def P(c, a=255, stroke=0, cap=True, shader=None):
    p = skia.Paint(AntiAlias=True, Color=col(c, a) if isinstance(c, str) else c)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap: p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if shader: p.setShader(shader)
    return p

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def mix(a, b, k): return a + (b - a) * k
def mixc(c1, c2, k, a=255):
    c1, c2 = c1.lstrip("#"), c2.lstrip("#")
    r = [int(mix(int(c1[i:i + 2], 16), int(c2[i:i + 2], 16), clamp(k))) for i in (0, 2, 4)]
    return skia.Color(*r, int(a))

def text_c(cv, s, x, y, f, paint, outline=None):
    w = f.measureText(s)
    if outline:
        cv.drawString(s, x - w / 2, y, f, outline)
    cv.drawString(s, x - w / 2, y, f, paint)
    return w

def wrap(s, f, maxw):
    out, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if f.measureText(t) <= maxw: cur = t
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out

def rrect(x, y, w, h, r): return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)

# ---------------- images ----------------
def load_img(arr): return skia.Image.fromarray(np.ascontiguousarray(arr))
ph = Image.open(FOTO).convert("RGBA")
ph = ph.crop((0, 0, 212, 262)).resize((636, 786), Image.LANCZOS)
PHOTO = load_img(np.array(ph))
lg = Image.open(LOGO_ARQ).convert("RGBA").crop((0, 443, 1080, 1523)).resize((900, 900), Image.LANCZOS)
LOGO = load_img(np.array(lg))
SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def draw_photo_circle(cv, cx, cy, r, alpha=255, ring=True):
    cv.saveLayerAlpha(None, int(alpha))
    if ring:
        cv.drawCircle(cx, cy, r + 10, P(GOLD))
    path = skia.Path(); path.addCircle(cx, cy, r)
    cv.save(); cv.clipPath(path, skia.ClipOp.kIntersect, True)
    # face sits around 52% x, 50% y of the crop
    s = 2 * r / 520
    w, h = PHOTO.width() * s, PHOTO.height() * s
    cv.drawImageRect(PHOTO, skia.Rect.MakeXYWH(cx - w * 0.53, cy - h * 0.50, w, h), SAMP)
    cv.restore(); cv.restore()

def draw_photo_card(cv, x, y, w, h, alpha=255, zoom=1.0):
    cv.saveLayerAlpha(None, int(alpha))
    cv.drawRRect(rrect(x - 8, y - 8, w + 16, h + 16, 48), P(GOLD))
    cv.save(); cv.clipRRect(rrect(x, y, w, h, 40), True)
    iw, ih = w * zoom, w * zoom * PHOTO.height() / PHOTO.width()
    cv.drawImageRect(PHOTO, skia.Rect.MakeXYWH(x + (w - iw) / 2, y + (h - ih) * 0.35, iw, ih), SAMP)
    cv.restore(); cv.restore()

# ---------------- illustrations ----------------
def background(cv, t):
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [col(NAVY), col(NAVY2)])
    cv.drawRect(skia.Rect.MakeWH(W, H), P(NAVY, shader=sh))
    # subtle drifting gold particles
    rng = np.random.default_rng(3)
    for i in range(26):
        x0, y0, sp, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(8, 22), rng.uniform(1.5, 3.5)
        y = (y0 - t * sp) % H
        cv.drawCircle(x0 + 10 * math.sin(t * 0.5 + i), y, r, P(GOLD, 40))


def phone(cv, cx, cy, s, draw_screen, alpha=255):
    w, h = 470 * s, 900 * s
    cv.saveLayerAlpha(None, int(alpha))
    cv.drawRRect(rrect(cx - w / 2 - 14, cy - h / 2 - 14, w + 28, h + 28, 70 * s), P("#05070d"))
    cv.drawRRect(rrect(cx - w / 2 - 14, cy - h / 2 - 14, w + 28, h + 28, 70 * s), P("#3a4560", stroke=3))
    cv.save(); cv.clipRRect(rrect(cx - w / 2, cy - h / 2, w, h, 58 * s), True)
    draw_screen(cx - w / 2, cy - h / 2, w, h)
    cv.restore()
    cv.drawRRect(rrect(cx - 60 * s, cy - h / 2 + 16 * s, 120 * s, 30 * s, 15 * s), P("#05070d"))
    cv.restore()

def check_icon(cv, x, y, r, k, c="#3fb67a"):
    cv.drawCircle(x, y, r * back(k), P(c))
    if k > 0.3:
        kk = clamp((k - 0.3) / 0.5)
        p = skia.Path(); p.moveTo(x - r * 0.45, y + r * 0.02)
        mx, my = x - r * 0.1, y + r * 0.35
        ex, ey = x + r * 0.5, y - r * 0.35
        if kk < 0.4:
            p.lineTo(mix(x - r * 0.45, mx, kk / 0.4), mix(y + r * 0.02, my, kk / 0.4))
        else:
            p.lineTo(mx, my); p.lineTo(mix(mx, ex, (kk - 0.4) / 0.6), mix(my, ey, (kk - 0.4) / 0.6))
        cv.drawPath(p, P(CREAM, stroke=r * 0.18))


def subtitle(cv, t):
    s = next((x for x in SUBS if x[0] <= t < x[1]), None)
    if not s: return
    f = font("m8", 54)
    lines = wrap(s[2], f, 900)
    y = 1560
    k = eout((t - s[0]) / 0.18)
    cv.saveLayerAlpha(None, int(255 * k))
    bw = max(f.measureText(l) for l in lines) + 70
    bh = len(lines) * 70 + 34
    cv.drawRRect(rrect(W / 2 - bw / 2, y - 62, bw, bh, 26), P("#05080f", 170))
    for i, l in enumerate(lines):
        text_c(cv, l, W / 2, y + i * 70, f, P(CREAM))
    cv.restore()

def onscreen(cv, s, t0, t, y=1390, size=76):
    if t < t0: return
    k = eout((t - t0) / 0.5)
    f = font("pf", size)
    lines = wrap(s, f, 960)
    cv.saveLayerAlpha(None, int(255 * k))
    for i, l in enumerate(lines):
        text_c(cv, l, W / 2, y + 30 * (1 - k) + i * (size + 12) - (len(lines) - 1) * (size + 12) / 2, f, P(GOLD2),
               outline=P("#000000", 200, stroke=8))
    cv.restore()

def header(cv):
    f = font("m7", 30)
    s = "I N F I N I T Y   G U A R D"
    text_c(cv, s, W / 2, 175, f, P(GOLD))
    cv.drawLine(W / 2 - 260, 195, W / 2 + 260, 195, P(GOLD, 120, stroke=2))


def endcard(cv, t, lt):
    k = eout(lt / 0.8)
    cv.saveLayerAlpha(None, int(255 * k))
    s = 0.92 + 0.08 * k
    cv.save(); cv.translate(W / 2, 820); cv.scale(s, s)
    path = skia.Path(); path.addCircle(0, 0, 440)
    cv.save(); cv.clipPath(path, skia.ClipOp.kIntersect, True)
    cv.drawImageRect(LOGO, skia.Rect.MakeXYWH(-450, -450, 900, 900), SAMP)
    cv.restore(); cv.restore()
    text_c(cv, "Fale comigo no WhatsApp", W / 2, 1400, font("m8", 54), P(CREAM))
    text_c(cv, "link na bio", W / 2, 1475, font("m7", 46), P(GOLD))
    cv.restore()


# ---------------- 3D + efeitos ----------------
TOTAL = AUDIO_T
NF = {s: len(os.listdir(os.path.join(SHOTS, s))) for s in (os.listdir(SHOTS) if os.path.isdir(SHOTS) else []) if os.path.isdir(os.path.join(SHOTS, s))}

@lru_cache(maxsize=8)
def shot(s, f):
    f = int(max(1, min(NF[s], f)))
    im = Image.open(os.path.join(SHOTS, s, f"{f:04d}.png")).convert("RGBA").resize((W, H), Image.LANCZOS)
    return skia.Image.fromarray(np.ascontiguousarray(np.array(im)))

@lru_cache(maxsize=8)
def blurred(s, f, dark=0.45):
    f = int(max(1, min(NF[s], f)))
    im = Image.open(os.path.join(SHOTS, s, f"{f:04d}.png")).convert("RGB").resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6))
    im = im.resize((W, H), Image.BILINEAR)
    a = (np.array(im).astype(np.float32) * (1 - dark)).astype(np.uint8)
    return skia.Image.fromarray(np.ascontiguousarray(np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])))

@lru_cache(maxsize=2)
def feed_img(night):
    im = Image.open(os.path.join(SHOTS, "FEEDN" if night else "FEED", "0001.png")).convert("RGBA")
    return skia.Image.fromarray(np.ascontiguousarray(np.array(im)))

def bg(cv, img):
    cv.drawImageRect(img, skia.Rect.MakeWH(W, H), SAMP)

def scrims(cv):
    top = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 330)], [skia.Color(5, 10, 22, 170), skia.Color(5, 10, 22, 0)])
    cv.drawRect(skia.Rect.MakeWH(W, 330), P(NAVY, shader=top))
    bot = skia.GradientShader.MakeLinear([skia.Point(0, 1150), skia.Point(0, H)], [skia.Color(5, 10, 22, 0), skia.Color(5, 10, 22, 215)])
    cv.drawRect(skia.Rect.MakeXYWH(0, 1150, W, H - 1150), P(NAVY, shader=bot))

def feed(cv, x, y, w, h, t, night_k=0.0):
    cv.save(); cv.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    for img, a in ((feed_img(False), 1 - night_k), (feed_img(True), night_k)):
        if a <= 0: continue
        iw, ih = img.width(), img.height()
        s = max(w / iw, h / ih)
        cv.saveLayerAlpha(None, int(255 * a))
        cv.drawImageRect(img, skia.Rect.MakeXYWH(x + (w - iw * s) / 2, y + (h - ih * s) / 2, iw * s, ih * s), SAMP)
        cv.restore()
    cv.restore()
    cv.drawRRect(rrect(x + 16, y + 16, 150, 40, 20), P("#000000", 130))
    cv.drawCircle(x + 38, y + 36, 8, P("#3fb67a", int(150 + 105 * math.sin(t * 5))))
    cv.drawString("AO VIVO", x + 54, y + 45, font("m7", 22), P(CREAM))

def gloom(cv, k, t):
    """anime 'gloom' lines hanging from the top"""
    if k <= 0: return
    for i in range(16):
        x = 30 + i * 68
        L = (260 + 160 * math.sin(i * 2.7)) * ease(k) + 10 * math.sin(t * 3 + i)
        cv.drawLine(x, 0, x, L, P("#2a1f4a", int(150 * k), stroke=7 if i % 2 else 4))

def speedlines(cv, t, k, cx=W / 2, cy=760):
    if k <= 0: return
    rng = np.random.default_rng(int(t * 24))
    for i in range(46):
        a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(430, 620); r1 = r0 + rng.uniform(300, 900)
        cv.drawLine(cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                    P(CREAM, int(170 * k), stroke=rng.uniform(2, 7)))

def sparkle(cv, x, y, r, a=255):
    p = skia.Path(); p.moveTo(x, y - r)
    for i, (dx, dy) in enumerate([(1, 0), (0, 1), (-1, 0), (0, -1)]):
        p.quadTo(x, y, x + dx * r, y + dy * r)
    cv.drawPath(p, P(GOLD2, a))

def sparkles(cv, t, cx, cy, k, spread=230):
    if k <= 0: return
    for i in range(7):
        ang = i * 0.9 + t * 0.6
        rr = spread * (0.7 + 0.3 * math.sin(i * 1.7))
        s = 18 + 16 * abs(math.sin(t * 4 + i))
        sparkle(cv, cx + rr * math.cos(ang), cy + rr * math.sin(ang) * 0.8, s * ease(k), int(255 * clamp(k)))

def ts(name, k, off=0.0):  # time of k-th sentence of scene, relative helpers
    return mark_t(name, k) + off



def disclaimer(cv):
    cv.drawString("Narração com voz gerada por IA", 40, H - 44, font("m5", 26), P(CREAM, 160))

def frame(t):
    surf = skia.Surface(W, H); cv = surf.getCanvas()
    cv.clear(col(NAVY))
    if t >= END_CARD:
        background(cv, t)
        endcard(cv, t, t - END_CARD)
    else:
        c, st, en = next(b for b in BOUNDS if b[1] <= t < b[2])
        CENAS[c](cv, t, t - st)
        if c > 1 and t - st < 0.25:  # quick dip between scenes
            cv.drawRect(skia.Rect.MakeWH(W, H), P(NAVY, int(255 * (1 - (t - st) / 0.25) * 0.8)))
        header(cv)
        subtitle(cv, t)
    disclaimer(cv)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)



CENAS = {}

def _parte(a, b, out):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(round(a * FPS)), int(round(b * FPS))):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()

def main(cenas):
    """python montagem.py still 5 9.5 ...   -> build/quadro_<t>.png
       python montagem.py video [saida.mp4] -> monta em 4 partes paralelas e junta com o áudio"""
    CENAS.update(cenas)
    modo = sys.argv[1] if len(sys.argv) > 1 else "video"
    if modo == "still":
        for x in sys.argv[2:]:
            Image.fromarray(frame(float(x))).convert("RGB").save(os.path.join(BUILD, f"quadro_{x}.png"))
        return
    if modo == "parte":
        _parte(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]); return
    saida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(VIDEO, os.path.basename(VIDEO) + ".mp4")
    n = 4; cortes = [round(TOTAL * i / n * FPS) / FPS for i in range(n + 1)]
    partes = [os.path.join(BUILD, f"parte{i}.mp4") for i in range(n)]
    procs = [subprocess.Popen([sys.executable, sys.argv[0], "parte", str(cortes[i]), str(cortes[i + 1]), partes[i]]) for i in range(n)]
    if any(p.wait() for p in procs): sys.exit("falhou ao montar uma das partes")
    lista = os.path.join(BUILD, "partes.txt")
    open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-i", AUDIO,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", saida], check=True)
    print("Vídeo pronto:", saida)
