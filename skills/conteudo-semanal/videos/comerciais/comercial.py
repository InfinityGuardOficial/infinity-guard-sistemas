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
PROD = next((p for p in CAT["produtos"] if p["id"] == EP.get("produto")), None)  # None: produto fora do catálogo
NOTAS = json.load(open(os.path.join(base.BUILD, "narracao_info.json")))
SEGS = EP["segmentos"]
TOMADA_PRODUTO = EP.get("tomada_produto", "P4")
if EP.get("cores"):  # cores da marca pedidas no briefing
    NAVY, GOLD = EP["cores"]["navy"], EP["cores"]["dourado"]
    NAVY2 = EP["cores"].get("navy2", NAVY); GOLD2 = EP["cores"].get("dourado_claro", GOLD2)
DESTAQUES = [d for d in PROD["destaques"] if d not in EP.get("nao_destacar", [])] if PROD else []
NOME_PRODUTO = PROD["nome"] if PROD else EP["produto_ilustrativo"]["nome"]

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
def callout(cv, texto, t0, t, y, icon=True, aviso=False):
    if t < t0: return
    k = eout((t - t0) / 0.4)
    f = font("m8", 44); w = f.measureText(texto) + (130 if icon else 70)
    x = W / 2 - w / 2
    cv.saveLayerAlpha(None, int(255 * k))
    cv.drawRRect(rrect(x, y - 52 + 20 * (1 - k), w, 92, 46), P(NAVY, 225))
    cv.drawRRect(rrect(x, y - 52 + 20 * (1 - k), w, 92, 46), P("#e05a4f" if aviso else GOLD, 220, stroke=3))
    if icon and aviso:  # proibido: círculo vermelho com traço
        cy = y - 6 + 20 * (1 - k)
        cv.drawCircle(x + 56, cy, 26 * back((t - t0) / 0.5), P("#e05a4f"))
        cv.drawLine(x + 42, cy, x + 70, cy, P(CREAM, stroke=6))
    elif icon: check_icon(cv, x + 56, y - 6 + 20 * (1 - k), 26, (t - t0) / 0.5)
    cv.drawString(texto, x + (100 if icon else 35), y + 10 + 20 * (1 - k), f, P(CREAM))
    cv.restore()

def cartao_produto(cv, t, lt):
    k = eout(lt / 0.6)
    y0 = 980 + 60 * (1 - k)
    cv.saveLayerAlpha(None, int(255 * k))
    alt = 560 if EP.get("mostrar_frete") else 520
    cv.drawRRect(rrect(60, y0, W - 120, alt, 40), P(NAVY, 235))
    cv.drawRRect(rrect(60, y0, W - 120, alt, 40), P(GOLD, stroke=3))
    fn = font("m8", 40)
    y = y0 + 70
    for ln in wrap(PROD["nome"], fn, W - 200):
        cv.drawString(ln, 100, y, fn, P(CREAM)); y += 50
    y += 10; x = 100
    fc = font("m7", 30)
    for d in DESTAQUES:
        w = fc.measureText(d) + 40
        if x + w > W - 100: x = 100; y += 60
        cv.drawRRect(rrect(x, y - 34, w, 48, 24), P(GOLD))
        cv.drawString(d, x + 20, y, fc, P(NAVY)); x += w + 14
    y += 85
    cv.drawString(brl(PROD["preco"]), 100, y, font("m8", 64), P(GOLD2))
    sj = " sem juros" if PROD.get("sem_juros") else ""  # só quando a página do produto confirma
    cv.drawString(f"ou {PROD['parcelas']}x de {brl(PROD['parcela_valor'])}{sj}", 100, y + 52, font("m7", 34), P(CREAM))
    cv.drawString(f"{brl(PROD['pix'])} no Pix", 560, y, font("m8", 44), P(CREAM))
    fs = font("m5", 26)
    data = "/".join(reversed(PROD.get("conferido_em", CAT["atualizado_em"]).split("-")))
    cv.drawString(f"Preços do site em {data}. Confira em {EP['site']}.", 100, y + 108, fs, P(CREAM, 200))
    req = " e ".join(PROD.get("requisitos", []))
    if req: cv.drawString(f"Requer {req}. Imagem ilustrativa.", 100, y + 142, fs, P(CREAM, 200))
    if EP.get("mostrar_frete"):
        # frete grátis só quando a página do produto mostra; senão, cálculo por CEP
        cv.drawString("Frete grátis (conforme o site)." if PROD.get("frete_gratis") else f"Frete: calcule pelo seu CEP em {EP['site']}.",
                      100, y + 176, fs, P(CREAM, 200))
    cv.restore()

LOGO_A = None
def logo_arquivo():
    global LOGO_A
    if LOGO_A is None:
        LOGO_A = base.load_img(np.array(Image.open(os.path.join(base.VIDEO, EP["logo_arquivo"])).convert("RGBA")))
    return LOGO_A

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
        n = base.NF.get(TOMADA_PRODUTO, 1)
        im = Image.open(os.path.join(base.SHOTS, TOMADA_PRODUTO, f"{max(1, n // 2):04d}.png")).convert("RGB")
        a = np.asarray(im).astype(int).sum(axis=2)
        ys, xs = np.where(a[: int(im.height * 0.62)] > 600)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        m = int(0.12 * (x1 - x0))
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
        MINI = base.load_img(np.array(im.convert("RGBA")))
    return MINI

def selo_produto(cv, t, lt):
    """selo do produto no canto de cima: miniatura, nome curto e site"""
    k = eout(lt / 0.5)
    x, y = 60, 120 - 40 * (1 - k)
    cv.saveLayerAlpha(None, int(255 * k))
    cv.drawRRect(rrect(x, y, W - 120, 170, 30), P(NAVY, 230)); cv.drawRRect(rrect(x, y, W - 120, 170, 30), P(GOLD, stroke=3))
    pk = miniatura_produto(); s_ = min(170 / pk.width(), 130 / pk.height())
    cv.drawImageRect(pk, skia.Rect.MakeXYWH(x + 20, y + 20, pk.width() * s_, pk.height() * s_), SAMP)
    nome = PROD["nome"].split(" — ")[0]
    cv.drawString(nome, x + 210, y + 70, font("m8", 32), P(CREAM))
    dz = ", ".join(DESTAQUES); tam = 28
    while font("m5", tam).measureText(dz) > W - 120 - 240 and tam > 16: tam -= 1
    cv.drawString(dz, x + 210, y + 110, font("m5", tam), P(CREAM, 210))
    cv.drawString(EP["site"], x + 210, y + 145, font("m7", 26), P(GOLD2))
    cv.restore()

FOTO = None
def foto_produto():
    """foto real do produto (fiel à aparência), recortada para tirar selos e textos de fornecedor"""
    global FOTO
    if FOTO is None:
        im = Image.open(os.path.join(base.VIDEO, EP["foto_produto"])).convert("RGBA")
        if EP.get("foto_recorte"): im = im.crop(tuple(EP["foto_recorte"]))
        FOTO = base.load_img(np.array(im))
    return FOTO

def fundo_marca(cv, t):
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [col(NAVY), col(NAVY2)])
    cv.drawRect(skia.Rect.MakeWH(W, H), P(NAVY, shader=sh))
    rng = np.random.default_rng(3)
    for i in range(30):
        x0, y0, sp, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(8, 22), rng.uniform(1.5, 3.5)
        cv.drawCircle(x0, (y0 - t * sp) % H, r, P(GOLD, 45))

def logo_circular(cv, cx, cy, r):
    pth = skia.Path(); pth.addCircle(cx, cy, r)
    cv.save(); cv.clipPath(pth, skia.ClipOp.kIntersect, True)
    cv.drawImageRect(base.LOGO, skia.Rect.MakeXYWH(cx - r * 1.02, cy - r * 1.02, r * 2.04, r * 2.04), SAMP)
    cv.restore()

def packshot(cv, t, lt):
    """produto (foto real), logo original, slogan e oferta do catálogo"""
    fundo_marca(cv, t)
    k = eout(lt / 0.7)
    cv.saveLayerAlpha(None, int(255 * k))
    if EP.get("logo") == "arquivo":  # logo original fornecido no episódio (fundo transparente), sem alterar
        img = logo_arquivo(); lw = 560; lh = lw * img.height() / img.width()
        cv.drawImageRect(img, skia.Rect.MakeXYWH(W / 2 - lw / 2, 95, lw, lh), SAMP)
    elif EP.get("logo") == "horizontal":  # logo original fornecido (preto sobre branco), sem alterar
        img = logo_original(); lw = 500; lh = lw * img.height() / img.width()
        cv.drawRRect(rrect(W / 2 - lw / 2 - 24, 70, lw + 48, lh + 40, 26), P("#ffffff"))
        cv.drawImageRect(img, skia.Rect.MakeXYWH(W / 2 - lw / 2, 90, lw, lh), SAMP)
    else:
        logo_circular(cv, W / 2, 170, 105)
        text_c(cv, CAT["slogan"], W / 2, 328, font("pf", 38), P(GOLD2))
    img = foto_produto(); fw = 500; fh = fw * img.height() / img.width()
    y0 = (420 if EP.get("logo") in ("horizontal", "arquivo") else 375) + 30 * (1 - k)
    cv.drawRRect(rrect(W / 2 - fw / 2 - 20, y0 - 20, fw + 40, fh + 40, 32), P("#ffffff"))
    cv.drawRRect(rrect(W / 2 - fw / 2 - 20, y0 - 20, fw + 40, fh + 40, 32), P(GOLD, stroke=4))
    cv.drawImageRect(img, skia.Rect.MakeXYWH(W / 2 - fw / 2, y0, fw, fh), SAMP)
    cv.drawString("Imagem do produto", W / 2 + fw / 2 - 210, y0 + fh + 8, font("m5", 22), P("#8a8a92"))
    y = y0 + fh + 78
    fn = font("m8", 36)
    for ln in wrap(NOME_PRODUTO, fn, W - 160):
        text_c(cv, ln, W / 2, y, fn, P(CREAM)); y += 46
    if not PROD:  # fora do catálogo: nada de preço, recurso ou frete
        y += 30
        for ln in EP["produto_ilustrativo"].get("linhas", ["Modelos e preços: link na bio"]):
            text_c(cv, ln, W / 2, y, font("m7", 34), P(CREAM, 225)); y += 48
        cv.restore()
        selo_campanha(cv, t, lt)
        cta_botao(cv, lt)
        return
    fc = font("m7", 28); linhas_ch, atual = [], []
    for d in DESTAQUES:  # quebra os destaques em linhas que cabem na tela
        if atual and sum(fc.measureText(q) + 54 for q in atual + [d]) > W - 120: linhas_ch.append(atual); atual = []
        atual.append(d)
    if atual: linhas_ch.append(atual)
    for li, lin in enumerate(linhas_ch):
        ws = [fc.measureText(d) + 40 for d in lin]; x = W / 2 - (sum(ws) + 14 * (len(ws) - 1)) / 2
        for d, w_ in zip(lin, ws):
            cv.drawRRect(rrect(x, y - 30, w_, 44, 22), P(GOLD)); cv.drawString(d, x + 20, y + 2, fc, P(NAVY)); x += w_ + 14
        if li < len(linhas_ch) - 1: y += 54
    y += 82
    text_c(cv, brl(PROD["preco"]), W / 2, y, font("m8", 72), P(GOLD2))
    sj = " sem juros" if PROD.get("sem_juros") else ""  # só quando a página do produto confirma
    text_c(cv, f"ou {PROD['parcelas']}x de {brl(PROD['parcela_valor'])}{sj}   ·   {brl(PROD['pix'])} no Pix", W / 2, y + 54, font("m7", 34), P(CREAM))
    fs = font("m5", 25); data = "/".join(reversed(PROD.get("conferido_em", CAT["atualizado_em"]).split("-")))
    frete = None
    if EP.get("mostrar_frete"):
        frete = "Frete grátis (conforme o site)." if PROD.get("frete_gratis") else f"Frete: calcule pelo seu CEP em {EP['site']}."
    req = None
    if PROD.get("requisitos"):
        r0 = PROD["requisitos"][0]
        req = (r0[0].upper() + r0[1:] + ".") if ": " in r0 else f"Requer {r0}."
    linhas = [frete, req, f"Preços do site em {data}. Confira em {EP['site']}."]
    for i, ln in enumerate(l_ for l_ in linhas if l_):
        text_c(cv, ln, W / 2, y + 100 + i * 33, fs, P(CREAM, 210))
    cv.restore()
    faixa_campanha(cv, lt, y0 - 4)
    cta_botao(cv, lt)

def faixa_campanha(cv, lt, y):
    """selo da campanha como faixa sobre a foto (sem preço nem desconto enquanto não estiver confirmada)"""
    c = EP.get("campanha")
    if not c: return
    k = back((lt - 0.6) / 0.5)
    if k <= 0: return
    txt = f"{c['nome'].upper()} · {c['chamada'].split(' · ')[0]}"
    f = font("m8", 30); w = f.measureText(txt) + 50
    cv.save(); cv.translate(W / 2, y); cv.scale(k, k)
    cv.drawRRect(rrect(-w / 2, -26, w, 52, 26), P("#000000")); cv.drawRRect(rrect(-w / 2, -26, w, 52, 26), P(GOLD, stroke=3))
    text_c(cv, txt, 0, 11, f, P(GOLD2))
    cv.restore()

def cta_botao(cv, lt, y=1448):
    kk = back((lt - 0.8) / 0.5)
    if kk > 0:
        cv.save(); cv.translate(W / 2, y); cv.scale(kk, kk)
        tam = 40
        while font("m8", tam).measureText(EP["cta"]) + 80 > W - 80 and tam > 22: tam -= 1
        f_ = font("m8", tam); w_ = f_.measureText(EP["cta"]) + 80
        cv.drawRRect(rrect(-w_ / 2, -44, w_, 84, 42), P(GOLD)); text_c(cv, EP["cta"], 0, tam * 0.35, f_, P(NAVY))
        cv.restore()

def selo_campanha(cv, t, lt, y=1290):
    """campanha (ex.: Black Friday): sem confirmação, só nome, datas e link na bio"""
    c = EP.get("campanha")
    if not c: return
    k = eout((lt - 0.5) / 0.5)
    if k <= 0: return
    cv.saveLayerAlpha(None, int(255 * k))
    cv.drawRRect(rrect(110, y - 70, W - 220, 150, 28), P("#000000"))
    cv.drawRRect(rrect(110, y - 70, W - 220, 150, 28), P(GOLD, stroke=4))
    text_c(cv, c["nome"].upper(), W / 2, y - 6, font("m8", 56), P(GOLD2))
    text_c(cv, c["chamada"], W / 2, y + 50, font("m7", 32), P(CREAM))
    cv.restore()

def capa():
    """capa 9:16 com o título do briefing sobre um quadro 3D"""
    c = EP["capa"]; surf = skia.Surface(W, H); cv = surf.getCanvas()
    bg(cv, shot(c["tomada"], c.get("quadro", 1))); scrims(cv)
    sh = skia.GradientShader.MakeLinear([skia.Point(0, H * 0.45), skia.Point(0, H)], [skia.Color(0, 0, 0, 0), col(NAVY, 245)])
    cv.drawRect(skia.Rect.MakeXYWH(0, H * 0.45, W, H * 0.55), P(NAVY, shader=sh))
    f = font("m8", 92); lines = wrap(c["titulo"], f, W - 140); y = c.get("y_titulo", 1240 - (len(lines) - 1) * 60)
    for ln in lines:
        text_c(cv, ln, W / 2, y, f, P(GOLD2 if ln == lines[-1] else CREAM), outline=P("#000000", 160, stroke=10)); y += 106
    if EP.get("logo") == "arquivo":
        img = logo_arquivo(); lw = 440; lh = lw * img.height() / img.width()
        cv.drawImageRect(img, skia.Rect.MakeXYWH(W / 2 - lw / 2, 1640, lw, lh), SAMP)
    elif EP.get("logo") == "horizontal":  # só o logo original fornecido
        img = logo_original(); lw = 380; lh = lw * img.height() / img.width()
        cv.drawRRect(rrect(W / 2 - lw / 2 - 18, 1655, lw + 36, lh + 30, 20), P("#ffffff"))
        cv.drawImageRect(img, skia.Rect.MakeXYWH(W / 2 - lw / 2, 1670, lw, lh), SAMP)
    else:
        logo_circular(cv, W / 2, 1640, 95)
        text_c(cv, EP["site"], W / 2, 1790, font("m7", 36), P(GOLD2))
    out = os.path.join(base.VIDEO, "capa.png")
    Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)).convert("RGB").save(out)
    print("capa:", out)

def encerramento(cv, t, lt):
    k = eout(lt / 0.6)
    bg(cv, blurred(TOMADA_PRODUTO, base.NF.get(TOMADA_PRODUTO, 1), 0.35)); scrims(cv)
    cv.saveLayerAlpha(None, int(255 * k))
    if EP.get("logo") == "circular":  # logo original navy e dourado
        cv.save(); cv.translate(W / 2, 520); s_ = 0.94 + 0.06 * k; cv.scale(s_, s_)
        pth = skia.Path(); pth.addCircle(0, 0, 330)
        cv.save(); cv.clipPath(pth, skia.ClipOp.kIntersect, True)
        cv.drawImageRect(base.LOGO, skia.Rect.MakeXYWH(-337, -337, 674, 674), SAMP)
        cv.restore(); cv.restore()
    else:
        img = logo_original()
        w = 880; h = w * img.height() / img.width()
        cv.drawRRect(rrect(W / 2 - w / 2 - 30, 300 - 30, w + 60, h + 60, 36), P("#ffffff"))
        cv.drawImageRect(img, skia.Rect.MakeXYWH(W / 2 - w / 2, 300, w, h), SAMP)
    pk = miniatura_produto()
    my, mh = (900, 300) if EP.get("logo") == "circular" else (820, 420)
    cv.save(); cv.clipRRect(rrect(W / 2 - 230, my, 460, mh, 30), True)
    cv.drawRect(skia.Rect.MakeXYWH(W / 2 - 230, my, 460, mh), P(NAVY))
    s_ = min(460 / pk.width(), mh / pk.height())
    cv.drawImageRect(pk, skia.Rect.MakeXYWH(W / 2 - pk.width() * s_ / 2, my + mh / 2 - pk.height() * s_ / 2, pk.width() * s_, pk.height() * s_), SAMP)
    cv.restore()
    cv.drawRRect(rrect(W / 2 - 230, my, 460, mh, 30), P(GOLD, stroke=3))
    text_c(cv, EP["site"], W / 2, 1310, font("m8", 58), P(GOLD2))
    cv.restore()
    kk = back((lt - 0.4) / 0.5)
    cv.save(); cv.translate(W / 2, 1440); cv.scale(kk, kk)
    tam = 38
    while font("m7", tam).measureText(EP["cta"]) + 70 > W - 60 and tam > 22: tam -= 1  # CTA sempre cabe na tela
    f = font("m7", tam); w = f.measureText(EP["cta"]) + 70
    cv.drawRRect(rrect(-w / 2, -45, w, 84, 42), P(GOLD))
    text_c(cv, EP["cta"], 0, tam * 0.32, f, P(NAVY))
    cv.restore()

# ---------------- motor de segmentos ----------------
EXTRAS = {}  # segmento (1..n) -> função(cv, t, lt) desenhada por cima

def make_seg(i, s):
    def draw(cv, t, lt):
        tom, lt_t = s.get("tomada"), lt
        for sub in s.get("tomadas", []):  # cortes de câmera dentro do segmento
            if sub["ini"] <= t < sub["fim"]: tom, lt_t = sub["tomada"], t - sub["ini"]
        if tom:
            img = shot(tom, lt_t * SFPS + 1)
            if any(x.get("tipo") == "produto" for x in s.get("tela", [])):
                # produto: sobe o 3D para o cartão de preço não cobrir as câmeras
                cv.drawImageRect(img, skia.Rect.MakeXYWH(0, -330, W, H), SAMP)
            else:
                bg(cv, img)
            scrims(cv)
        if i + 1 in EXTRAS: EXTRAS[i + 1](cv, t, lt)
        selo_simulacao(cv, t)
        for tl in s.get("tela", []):
            tipo = tl.get("tipo", "texto")
            if tipo == "produto": cartao_produto(cv, t, t - tl["ini"])
            elif tipo == "encerramento": encerramento(cv, t, t - tl["ini"])
            elif tipo == "selo_produto": selo_produto(cv, t, t - tl["ini"])
            elif tipo == "packshot": packshot(cv, t, t - tl["ini"])
            elif tipo == "texto" and t >= tl["ini"] and t < tl.get("fim", s["fim"]):
                if i == 0: onscreen(cv, tl["texto"], tl["ini"] - s["ini"], lt, y=tl.get("y", 430), size=76)
                else:
                    others = [x for x in s["tela"] if x.get("tipo", "texto") == "texto" and x["ini"] <= t]
                    pos = others.index(tl)
                    callout(cv, tl["texto"], tl["ini"], t, 300 + pos * 120, aviso=tl.get("aviso", False))
    return draw

def selo_simulacao(cv, t):
    for a, b in EP.get("simulacao", []):
        if a <= t < b:
            f = font("m7", 28); w = f.measureText("Simulação ilustrativa") + 40
            cv.drawRRect(rrect(W - w - 40, 60, w, 48, 24), P("#000000", 150))
            cv.drawString("Simulação ilustrativa", W - w - 20, 94, f, P(CREAM, 230))

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "capa":
        return capa()
    base.main({i + 1: make_seg(i, s) for i, s in enumerate(SEGS)})
