"""Montagem do episódio 19 — O mistério das plantas. Uso: python montagem.py [video|still T...|capa]"""
import math, os, sys
os.environ.setdefault("VIDEO_DIR", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import comercial as C
from comercial import P, font, rrect, text_c, clamp, W, H, CREAM, skia


def tela_app(cv, t, lt):
    """interface ilustrativa do aplicativo por cima da imagem da câmera (ao vivo, sem gravação)"""
    for s in C.SEGS:
        for tl in s.get("tela", []):
            if tl.get("tipo") != "app" or not (tl["ini"] <= t < tl["fim"]): continue
            k = clamp((t - tl["ini"]) / 0.3)
            cv.saveLayerAlpha(None, int(255 * k))
            cv.drawRect(skia.Rect.MakeXYWH(0, 0, W, 210), P("#000000", 150))
            cv.drawString(tl["texto"], 60, 150, font("m8", 44), P(CREAM))
            cv.drawCircle(W - 210, 136, 11, P("#3fb67a", int(150 + 105 * math.sin(t * 5))))
            cv.drawString("AO VIVO", W - 185, 148, font("m7", 32), P(CREAM))
            cx, cy = W - 170, 1330  # controle de giro (PTZ)
            cv.drawCircle(cx, cy, 110, P("#000000", 130)); cv.drawCircle(cx, cy, 110, P(CREAM, 160, stroke=3))
            for a in range(4):
                ang = a * math.pi / 2
                p = skia.Path(); x, y = cx + 72 * math.cos(ang), cy + 72 * math.sin(ang)
                p.moveTo(x + 18 * math.cos(ang), y + 18 * math.sin(ang))
                p.lineTo(x + 16 * math.cos(ang + 2.2), y + 16 * math.sin(ang + 2.2)); p.lineTo(x + 16 * math.cos(ang - 2.2), y + 16 * math.sin(ang - 2.2)); p.close()
                cv.drawPath(p, P(CREAM, 220))
            cv.restore()


C.EXTRAS[3] = tela_app
C.EXTRAS[4] = tela_app

if __name__ == "__main__":
    C.main()
