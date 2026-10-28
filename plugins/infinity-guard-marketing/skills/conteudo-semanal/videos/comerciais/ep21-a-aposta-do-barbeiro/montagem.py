"""Montagem do episódio 21 — A aposta do barbeiro. Uso: python montagem.py [video|still T...|capa]"""
import math, os, sys
os.environ.setdefault("VIDEO_DIR", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import comercial as C
from comercial import P, font, clamp, W, H, CREAM, skia


def tela_monitor(cv, t, lt):
    """imagem ao vivo da dome no monitor do balcão (ilustrativa, sem gravação): moldura e selo AO VIVO"""
    for s in C.SEGS:
        for tl in s.get("tela", []):
            if tl.get("tipo") != "monitor" or not (tl["ini"] <= t < tl["fim"]): continue
            k = clamp((t - tl["ini"]) / 0.3) * (1 - clamp((t - tl["fim"] + 0.25) / 0.25))
            cv.saveLayerAlpha(None, int(255 * k))
            cv.drawRect(skia.Rect.MakeWH(W, H), P("#0a1420", 40))
            cv.drawRect(skia.Rect.MakeXYWH(18, 18, W - 36, H - 36), P(CREAM, 120, stroke=4))
            cv.drawRect(skia.Rect.MakeXYWH(0, 130, W, 120), P("#000000", 140))
            cv.drawString(tl["texto"], 60, 207, font("m8", 44), P(CREAM))
            cv.drawCircle(W - 230, 192, 11, P("#e04848", int(150 + 105 * math.sin(t * 5))))
            cv.drawString("AO VIVO", W - 205, 204, font("m7", 32), P(CREAM))
            cv.restore()


C.EXTRAS[3] = tela_monitor

if __name__ == "__main__":
    C.main()
