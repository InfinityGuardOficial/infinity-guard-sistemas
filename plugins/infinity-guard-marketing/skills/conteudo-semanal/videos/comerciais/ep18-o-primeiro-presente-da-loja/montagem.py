"""Montagem do episódio 18 — O primeiro presente da loja. Uso: python montagem.py [video|still T...|capa]"""
import os, sys
os.environ.setdefault("VIDEO_DIR", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import comercial as C
from comercial import P, font, rrect, text_c, eout, back, clamp, W, H, skia

BILHETE = "Para cuidar do que você levou anos para construir."

def bilhete(cv, t, lt):
    """o bilhete da mãe, em letra de mão, quando a tela pede"""
    for s in C.SEGS:
        for tl in s.get("tela", []):
            if tl.get("tipo") == "bilhete" and tl["ini"] <= t < tl["fim"]:
                k = back((t - tl["ini"]) / 0.45) * (1 - clamp((t - tl["fim"] + 0.3) / 0.3))
                cv.save(); cv.translate(W / 2, 560); cv.scale(k, k); cv.rotate(-4)
                cv.drawRRect(rrect(-392, -182, 800, 380, 16), P("#000000", 80))
                cv.drawRRect(rrect(-400, -190, 800, 380, 16), P("#fbf6ea"))
                for i in range(5): cv.drawLine(-360, -90 + i * 62, 360, -90 + i * 62, P("#d9cdb2", stroke=2))
                f = font("cv", 66); y = -100
                for ln in C.wrap(BILHETE, f, 700):
                    cv.drawString(ln, -350, y, f, P("#1d2a5a")); y += 70
                cv.drawString("— Mãe", 150, y + 10, font("cv", 62), P("#1d2a5a"))
                cv.restore()

def sepia(cv, t, lt):
    """lembrança da véspera: tom sépia e vinheta"""
    k = clamp(lt / 0.4) * (1 - clamp((lt - 5.6) / 0.4))
    cv.drawRect(skia.Rect.MakeWH(W, H), P("#704a1c", int(95 * k)))
    sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), H * 0.62, [skia.Color(0, 0, 0, 0), skia.Color(20, 10, 0, int(200 * k))])
    cv.drawRect(skia.Rect.MakeWH(W, H), P("#000000", shader=sh))

def segundo(cv, t, lt):
    if lt < 6: sepia(cv, t, lt)
    bilhete(cv, t, lt)

C.EXTRAS[1] = bilhete
C.EXTRAS[2] = segundo

if __name__ == "__main__":
    C.main()
