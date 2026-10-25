"""Montagem do episódio 15 — Quem deixou isso na porta? Uso: python montagem.py [video|still T...]"""
import os, sys
os.environ.setdefault("VIDEO_DIR", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import comercial as C
from comercial import P, font, rrect, text_c, eout, back, clamp, W, H, NAVY, CREAM, GOLD, skia

ET = next(x for x in C.SEGS[1]["tela"] if x.get("tipo") == "etiqueta")

def etiqueta(cv, t, lt):
    """close da etiqueta: o nome é de outra pessoa"""
    if not (ET["ini"] <= t < ET["fim"]): return
    k = back((t - ET["ini"]) / 0.45) * (1 - clamp((t - ET["fim"] + 0.3) / 0.3))
    cv.save(); cv.translate(W / 2, 520); cv.scale(k, k); cv.rotate(-3)
    cv.drawRRect(rrect(-400, -170, 800, 340, 18), P("#000000", 90))
    cv.drawRRect(rrect(-410, -185, 800, 340, 18), P("#fbfaf5"))
    cv.drawRect(skia.Rect.MakeXYWH(-410, -185, 800, 64), P("#e9e4d6"))
    cv.drawString("DESTINATÁRIO", -380, -140, font("m8", 30), P("#5a5a66"))
    para, end = ET["texto"].replace("Para: ", "").split(" · ")
    cv.drawString(para, -380, -40, font("m8", 58), P("#1c1c24"))
    cv.drawString(end, -380, 30, font("m7", 40), P("#3a3a46"))
    for i in range(14):  # código de barras ilustrativo
        cv.drawRect(skia.Rect.MakeXYWH(-380 + i * 22, 70, 6 + (i * 7) % 11, 60), P("#1c1c24"))
    cv.restore()

def noite(cv, t, lt):
    """escurece a cena quando anoitece (visão noturna)"""
    k = clamp((t - 21.4) / 1.6)
    if k > 0: cv.drawRect(skia.Rect.MakeWH(W, H), P("#081030", int(110 * k)))

C.EXTRAS[2] = etiqueta
C.EXTRAS[3] = noite

if __name__ == "__main__":
    C.main()
