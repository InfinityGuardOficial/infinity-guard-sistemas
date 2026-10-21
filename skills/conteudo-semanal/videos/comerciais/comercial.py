"""Montagem dos comerciais: lê episodio.json + catálogo, desenha legendas, textos, cartão do produto e
encerramento por cima das tomadas 3D e exporta o MP4 (motor de ../anime3d/base.py).

Cada episódio tem um montagem.py curto que chama comercial.main() e pode acrescentar desenhos próprios
(ex.: o close da etiqueta) em EXTRAS[segmento].
"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "anime3d"))
import base
from base import (skia, P, font, text_c, wrap, rrect, check_icon, clamp, ease, eout, back, mix, col, W, H, SAMP,
                  NAVY, NAVY2, GOLD, GOLD2, CREAM, shot, blurred, bg, scrims, onscreen, SFPS, Image, np)

CATALOGO = os.path.join(AQUI, "..", "..", "..", "atendente-infinity-guard", "references", "catalogo.json")
EP = json.load(open(os.path.join(base.VIDEO, "episodio.json")))
CAT = json.load(open(CATALOGO))
PROD = next(p for p in CAT["produtos"] if p["id"] == EP["produto"])
NOTAS = json.load(open(os.path.join(base.BUILD, "narracao_info.json")))
SEGS = EP["segmentos"]

def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------- tempo: segmentos fixos do roteiro ----------------
base.BOUNDS = [(i + 1, s["ini"], s["fim"]) for i, s in enumerate(SEGS)]
base.END_CARD = EP["duracao"] + 1  # o encerramento é um segmento normal

# legendas com o nome de quem fala (personagens) e sem nome para o narrador
SUBS = []
for i, m in enumerate(base.MARKS):
    words = m["texto"].split(); chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 7 or (w.endswith((",", "?", ".")) and len(cur) >= 4):
            chunks.append(cur); cur = []
    if cur:
        if chunks and len(cur) <= 2: chunks[-1] += cur
        else: chunks.append(cur)
    tot = sum(len(" ".join(c)) for c in chunks); t = m["ini"]
    nxt = base.MARKS[i + 1]["ini"] if i + 1 < len(base.MARKS) else m["fim"] + 0.5
    for j, c in enumerate(chunks):
        d = (m["fim"] - m["ini"]) * len(" ".join(c)) / tot
        end = t + d if j < len(chunks) - 1 else min(nxt, m["fim"] + 0.5)
        SUBS.append((t - 0.05, end, " ".join(c), m["quem"]))
        t += d

COR_PERS = {"Ana": "#f08a6a", "Marcos": "#5fbf8a", "Seu Joaquim": "#9fb3d9"}

def subtitle(cv, t):
    s = next((x for x in SUBS if x[0] <= t < x[1]), None)
    if not s: return
    f = font("m8", 52); lines = wrap(s[2], f, 900); y = 1590
    k = eout((t - s[0]) / 0.18)
    cv.saveLayerAlpha(None, int(255 * k))
    bw = max(f.measureText(l) for l in lines) + 70; bh = len(lines) * 68 + 34
    cv.drawRRect(rrect(W / 2 - bw / 2, y - 60, bw, bh, 26), P("#05080f", 175))
    if s[3] != "narrador":
        fn = font("m7", 30); nw = fn.measureText(s[3]) + 40
        cv.drawRRect(rrect(W / 2 - bw / 2 + 20, y - 108, nw, 46, 23), P(COR_PERS.get(s[3], GOLD)))
        cv.drawString(s[3], W / 2 - bw / 2 + 40, y - 74, fn, P(NAVY))
    for i, l in enumerate(lines):
        text_c(cv, l, W / 2, y + i * 68, f, P(CREAM))
    cv.restore()

base.subtitle = subtitle

def disclaimer(cv):
    txt = "Personagens fictícios · animação 3D"
    if NOTAS.get("provisoria"): txt += " · vozes sintéticas provisórias"
    cv.drawString(txt, 40, H - 44, font("m5", 26), P(CREAM, 170))

base.disclaimer = disclaimer

def header(cv):
    pass  # comerciais sem faixa no topo: o logo aparece no encerramento

base.header = header

# ---------------- peças reutilizáveis ----------------
def callout(cv, texto, t0, t, y, icon=True):
    if t < t0: return
    k = eout((t - t0) / 0.4)
    f = font("m8", 44); w = f.measureText(texto) + (130 if icon else 70)
    x = W / 2 - w / 2
    cv.saveLayerAlpha(None, int(255 * k))
    cv.drawRRect(rrect(x, y - 52 + 20 * (1 - k), w, 92, 46), P(NAVY, 225))
    cv.drawRRect(rrect(x, y - 52 + 20 * (1 - k), w, 92, 46), P(GOLD, 200, stroke=3))
    if icon: check_icon(cv, x + 56, y - 6 + 20 * (1 - k), 26, (t - t0) / 0.5)
    cv.drawString(texto, x + (100 if icon else 35), y + 10 + 20 * (1 - k), f, P(CREAM))
    cv.restore()

def cartao_produto(cv, t, lt):
    k = eout(lt / 0.6)
    y0 = 980 + 60 * (1 - k)
    cv.saveLayerAlpha(None, int(255 * k))
    cv.drawRRect(rrect(60, y0, W - 120, 520, 40), P(NAVY, 235))
    cv.drawRRect(rrect(60, y0, W - 120, 520, 40), P(GOLD, stroke=3))
    fn = font("m8", 40)
    y = y0 + 70
    for ln in wrap(PROD["nome"], fn, W - 200):
        cv.drawString(ln, 100, y, fn, P(CREAM)); y += 50
    y += 10; x = 100
    fc = font("m7", 30)
    for d in PROD["destaques"]:
        w = fc.measureText(d) + 40
        if x + w > W - 100: x = 100; y += 60
        cv.drawRRect(rrect(x, y - 34, w, 48, 24), P(GOLD))
        cv.drawString(d, x + 20, y, fc, P(NAVY)); x += w + 14
    y += 85
    cv.drawString(brl(PROD["preco"]), 100, y, font("m8", 64), P(GOLD2))
    cv.drawString(f"ou {PROD['parcelas']}x de {brl(PROD['parcela_valor'])}", 100, y + 52, font("m7", 34), P(CREAM))
    cv.drawString(f"{brl(PROD['pix'])} no Pix", 560, y, font("m8", 44), P(CREAM))
    fs = font("m5", 26)
    data = "/".join(reversed(CAT["atualizado_em"].split("-")))
    cv.drawString(f"Preços do site em {data}. Confira em {EP['site']}.", 100, y + 108, fs, P(CREAM, 200))
    req = " e ".join(PROD.get("requisitos", []))
    if req: cv.drawString(f"Requer {req}. Imagem ilustrativa.", 100, y + 142, fs, P(CREAM, 200))
    cv.restore()

LOGO_H = None
def logo_original():
    global LOGO_H
    if LOGO_H is None:
        im = Image.open(os.path.join(AQUI, "logo-infinity-guard-horizontal.jpg")).convert("RGBA").crop((40, 330, 1214, 900))
        LOGO_H = base.load_img(np.array(im))
    return LOGO_H

MINI = None
def miniatura_produto():
    """recorte automático das câmeras (partes claras) num quadro da tomada do produto"""
    global MINI
    if MINI is None:
        n = base.NF.get("P4", 1)
        im = Image.open(os.path.join(base.SHOTS, "P4", f"{max(1, n // 2):04d}.png")).convert("RGB")
        a = np.asarray(im).astype(int).sum(axis=2)
        ys, xs = np.where(a[: int(im.height * 0.62)] > 600)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        m = int(0.12 * (x1 - x0))
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
        MINI = base.load_img(np.array(im.convert("RGBA")))
    return MINI

def encerramento(cv, t, lt):
    k = eout(lt / 0.6)
    bg(cv, blurred("P4", base.NF.get("P4", 1), 0.35)); scrims(cv)
    cv.saveLayerAlpha(None, int(255 * k))
    img = logo_original()
    w = 880; h = w * img.height() / img.width()
    cv.drawRRect(rrect(W / 2 - w / 2 - 30, 300 - 30, w + 60, h + 60, 36), P("#ffffff"))
    cv.drawImageRect(img, skia.Rect.MakeXYWH(W / 2 - w / 2, 300, w, h), SAMP)
    pk = miniatura_produto()
    cv.save(); cv.clipRRect(rrect(W / 2 - 230, 820, 460, 420, 30), True)
    cv.drawRect(skia.Rect.MakeXYWH(W / 2 - 230, 820, 460, 420), P(NAVY))
    s_ = min(460 / pk.width(), 420 / pk.height())
    cv.drawImageRect(pk, skia.Rect.MakeXYWH(W / 2 - pk.width() * s_ / 2, 1030 - pk.height() * s_ / 2, pk.width() * s_, pk.height() * s_), SAMP)
    cv.restore()
    cv.drawRRect(rrect(W / 2 - 230, 820, 460, 420, 30), P(GOLD, stroke=3))
    text_c(cv, EP["site"], W / 2, 1330, font("m8", 58), P(GOLD2))
    cv.restore()
    kk = back((lt - 0.4) / 0.5)
    cv.save(); cv.translate(W / 2, 1440); cv.scale(kk, kk)
    f = font("m7", 38); w = f.measureText(EP["cta"]) + 70
    cv.drawRRect(rrect(-w / 2, -45, w, 84, 42), P(GOLD))
    text_c(cv, EP["cta"], 0, 12, f, P(NAVY))
    cv.restore()

# ---------------- motor de segmentos ----------------
EXTRAS = {}  # segmento (1..n) -> função(cv, t, lt) desenhada por cima

def make_seg(i, s):
    def draw(cv, t, lt):
        if s.get("tomada"):
            img = shot(s["tomada"], lt * SFPS + 1)
            if any(x.get("tipo") == "produto" for x in s.get("tela", [])):
                # produto: sobe o 3D para o cartão de preço não cobrir as câmeras
                cv.drawImageRect(img, skia.Rect.MakeXYWH(0, -330, W, H), SAMP)
            else:
                bg(cv, img)
            scrims(cv)
        if i + 1 in EXTRAS: EXTRAS[i + 1](cv, t, lt)
        for tl in s.get("tela", []):
            tipo = tl.get("tipo", "texto")
            if tipo == "produto": cartao_produto(cv, t, t - tl["ini"])
            elif tipo == "encerramento": encerramento(cv, t, t - tl["ini"])
            elif tipo == "texto" and t >= tl["ini"] and t < tl.get("fim", s["fim"]):
                if i == 0: onscreen(cv, tl["texto"], tl["ini"] - s["ini"], lt, y=430, size=76)
                else:
                    others = [x for x in s["tela"] if x.get("tipo", "texto") == "texto" and x["ini"] <= t]
                    pos = others.index(tl)
                    callout(cv, tl["texto"], tl["ini"], t, 300 + pos * 120)
    return draw

def main():
    base.main({i + 1: make_seg(i, s) for i, s in enumerate(SEGS)})
