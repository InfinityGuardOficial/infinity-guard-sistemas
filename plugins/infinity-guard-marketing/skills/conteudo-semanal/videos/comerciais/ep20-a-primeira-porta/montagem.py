"""Montagem do episódio 20 — A primeira porta. Uso: python montagem.py [video|still T...|capa]"""
import os, sys
os.environ.setdefault("VIDEO_DIR", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import comercial as C
from comercial import P, clamp, W, H, skia


def lembranca(cv, t, lt):
    """estudo, trabalho e planos (5 a 16 s): tom sépia e vinheta"""
    if not 5.0 <= t < 16.0: return
    k = clamp((t - 5.0) / 0.4) * (1 - clamp((t - 15.6) / 0.4))
    cv.drawRect(skia.Rect.MakeWH(W, H), P("#704a1c", int(95 * k)))
    sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), H * 0.62, [skia.Color(0, 0, 0, 0), skia.Color(20, 10, 0, int(200 * k))])
    cv.drawRect(skia.Rect.MakeWH(W, H), P("#000000", shader=sh))


C.EXTRAS[2] = lembranca

if __name__ == "__main__":
    C.main()
