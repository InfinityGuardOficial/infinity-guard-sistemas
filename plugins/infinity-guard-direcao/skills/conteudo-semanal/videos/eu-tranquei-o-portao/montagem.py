"""Cenas de 'Eu tranquei o portão?' por cima das tomadas 3D. Uso: python montagem.py [video|still T...]"""
import os, sys
os.environ.setdefault("VIDEO_DIR", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "anime3d"))
from base import *  # noqa: F401,F403
import base

# ---------------- scenes ----------------
def s1(cv, t, lt):
    bg(cv, shot("A", lt * SFPS + 1)); scrims(cv)
    a = eout((lt - 0.3) / 0.5)
    draw_photo_circle(cv, 270, 520, 150, 255 * a)
    k = ease(lt / 3.6)
    cv.saveLayerAlpha(None, int(255 * a))
    cv.drawRRect(rrect(560, 430, 400, 150, 75), P(NAVY, 220)); cv.drawRRect(rrect(560, 430, 400, 150, 75), P(GOLD, stroke=4))
    text_c(cv, f"{int(40 * k)} km", 760, 532, font("m8", 84), P(CREAM))
    text_c(cv, "de casa", 760, 640, font("m7", 40), P(CREAM, 220))
    cv.restore()
    if lt > 3.9:
        kk = back((lt - 3.9) / 0.5)
        cv.save(); cv.translate(420, 360); cv.scale(kk, kk)
        cv.drawCircle(-70, 90, 14, P(CREAM)); cv.drawCircle(-40, 55, 22, P(CREAM))
        cv.drawCircle(40, -10, 72, P(CREAM)); text_c(cv, "?", 40, 24, font("m8", 100), P(NAVY))
        cv.restore()
    onscreen(cv, "Eu tranquei o portão?", 3.9, lt)

def s2(cv, t, lt):
    bg(cv, shot("B", lt * SFPS + 1)); scrims(cv)
    t2 = ts(2, 1) - SC[2]
    if lt > t2:
        kk = back((lt - t2 - 0.2) / 0.5)
        cv.save(); cv.translate(800, 520 + 8 * math.sin(t * 4)); cv.scale(kk, kk)
        cv.drawCircle(0, 0, 70, P(GOLD)); text_c(cv, "?", 0, 34, font("m8", 100), P(NAVY))
        cv.restore()
    onscreen(cv, "Fim de ano, carro cheio", 0.3, lt, size=64)

def call_screen(lt):
    def screen(x, y, w, h):
        cv = screen.cv
        cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), P("#101a2e"))
        ringing = lt < 1.9
        cy = y + h * 0.36
        for r in range(3):
            p = (lt * 1.2 + r / 3) % 1
            if ringing: cv.drawCircle(x + w / 2, cy, 90 + p * 120, P(GOLD, int(160 * (1 - p)), stroke=4))
        cv.drawCircle(x + w / 2, cy, 90, P("#2b3a5c"))
        cv.drawCircle(x + w / 2, cy - 22, 30, P(CREAM)); cv.drawCircle(x + w / 2, cy + 48, 48, P(CREAM))
        text_c(cv, "Vizinho", x + w / 2, y + h * 0.58, font("m8", 48), P(CREAM))
        if ringing:
            text_c(cv, "chamando" + "." * (int(lt * 3) % 4), x + w / 2, y + h * 0.64, font("m5", 32), P(CREAM, 180))
        else:
            k = back((lt - 1.9) / 0.4)
            cv.save(); cv.translate(x + w / 2, y + h * 0.66); cv.scale(k, k)
            cv.drawRRect(rrect(-150, -40, 300, 60, 30), P("#c0392b"))
            text_c(cv, "Não atendeu", 0, 2, font("m7", 30), P(CREAM)); cv.restore()
        cv.drawCircle(x + w / 2, y + h * 0.85, 46, P("#c0392b"))
        cv.drawRRect(rrect(x + w / 2 - 26, y + h * 0.85 - 8, 52, 16, 8), P(CREAM))
    return screen

def s3(cv, t, lt):
    t2 = ts(3, 1) - SC[3] - 0.25
    if lt < t2:
        bg(cv, shot("C", lt * SFPS + 1)); scrims(cv)
        k = eout(lt / 0.5)
        sc_ = call_screen(lt); sc_.cv = cv
        phone(cv, W / 2, 760 + 300 * (1 - k), 0.95, sc_, 255 * k)
    else:
        lt2 = lt - t2
        bg(cv, shot("M", lt2 * SFPS + 1)); scrims(cv)
        cx, cy = 170, 420
        cv.drawCircle(cx, cy, 90, P(CREAM, 235)); cv.drawCircle(cx, cy, 90, P(NAVY, stroke=7))
        a = lt2 * 2.2
        cv.drawLine(cx, cy, cx + 62 * math.sin(a), cy - 62 * math.cos(a), P(NAVY, stroke=6))
        cv.drawLine(cx, cy, cx + 40 * math.sin(a / 12), cy - 40 * math.cos(a / 12), P(NAVY, stroke=8))
        gloom(cv, (lt2 - 0.8) / 1.2, t)
        onscreen(cv, "Uma hora de preocupação", 1.6, lt2, size=64)

def s4(cv, t, lt):
    d = BOUNDS[3][2] - BOUNDS[3][1]
    f = NF["M"] - (NF["M"] - 1) * clamp(lt / d)
    bg(cv, shot("M", f)); scrims(cv)
    rng = np.random.default_rng(int(t * 30))
    for i in range(12):
        y = rng.uniform(0, H)
        cv.drawRect(skia.Rect.MakeXYWH(0, y, W, rng.uniform(2, 9)), P(CREAM, int(rng.uniform(30, 90))))
    speedlines(cv, t, 1.0, W / 2, 560)
    a = 255 if int(lt * 3) % 2 == 0 else 160
    cv.save(); cv.translate(W / 2, 560)
    for dx in (-80, 10):
        p = skia.Path(); p.moveTo(dx + 70, -70); p.lineTo(dx, 0); p.lineTo(dx + 70, 70); p.close()
        cv.drawPath(p, P(CREAM, a))
    cv.restore()
    onscreen(cv, "Agora volta a cena", 0.1, lt)

def s5(cv, t, lt):
    tap = ts(5, 1) - SC[5] + 1.5
    seen = ts(5, 2) - SC[5]
    bg(cv, shot("C", lt * SFPS + 1)); scrims(cv)
    if lt <= 0.9:
        onscreen(cv, "Mesma estrada, mesma dúvida", 0.0, lt, size=60)
        return
    k = eout((lt - 0.9) / 0.6)
    def screen(x, y, w, h):
        cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), P("#0f1a2e"))
        cv.drawString("Minhas câmeras", x + 34, y + 120, font("m8", 36), P(CREAM))
        ex = ease((lt - tap - 0.2) / 0.5)
        tx, ty, tw, th = x + 30, y + 160, w - 60, 260
        fx, fy, fw, fh = mix(tx, x, ex), mix(ty, y + 70, ex), mix(tw, w, ex), mix(th, h * 0.62, ex)
        cv.save(); cv.clipRRect(rrect(fx, fy, fw, fh, mix(24, 0, ex)), True)
        feed(cv, fx, fy, fw, fh, t)
        cv.restore()
        cv.drawString("Câmera da entrada", x + 34, fy + fh + 50, font("m7", 30), P(CREAM))
        if ex < 0.5:
            cv.drawRRect(rrect(tx, ty + th + 90, tw, 200, 24), P("#1b2742"))
            cv.drawString("Câmera da garagem", x + 34, ty + th + 330, font("m7", 30), P(CREAM, 150))
        if tap - 0.3 < lt < tap + 0.6:
            r = (lt - tap + 0.3) / 0.9
            cv.drawCircle(x + w / 2, ty + th / 2, 40 + 60 * r, P("#ffffff", int(180 * (1 - r))))
            cv.drawCircle(x + w / 2, ty + th / 2, 34, P("#ffffff", int(200 * (1 - r))))
        if lt > seen:
            kk = (lt - seen) / 0.5
            check_icon(cv, x + 70, y + h * 0.8, 36, kk)
            cv.drawString("Portão fechado", x + 124, y + h * 0.8 + 12, font("m8", 36), P(CREAM, int(255 * clamp(kk))))
            if lt > seen + 0.8:
                k2 = (lt - seen - 0.8) / 0.5
                check_icon(cv, x + 70, y + h * 0.9, 36, k2)
                cv.drawString("Rua calma", x + 124, y + h * 0.9 + 12, font("m8", 36), P(CREAM, int(255 * clamp(k2))))
    phone(cv, W / 2, 800 + 900 * (1 - k), 1.0, screen, 255)

def s6(cv, t, lt):
    m = [ts(6, k) - SC[6] for k in range(4)]
    if lt < m[1] - 0.15:
        bg(cv, shot("C", 60 + lt * SFPS)); scrims(cv)
        k = clamp(lt / 1.6)
        cx, cy = W / 2, 520
        cv.drawCircle(cx, cy, 140, P(NAVY, 225))
        cv.drawCircle(cx, cy, 120, P("#ffffff", 40, stroke=16))
        arc = skia.Path(); arc.addArc(skia.Rect.MakeXYWH(cx - 120, cy - 120, 240, 240), -90, 360 * k)
        cv.drawPath(arc, P(GOLD, stroke=16))
        text_c(cv, f"{int(10 * k)} s", cx, cy + 28, font("m8", 80), P(CREAM))
        if k >= 1:
            check_icon(cv, cx + 110, cy - 100, 36, (lt - 1.6) / 0.5)
            sparkles(cv, t, cx, cy, (lt - 1.6) / 0.4)
    elif lt < m[3] - 0.15:
        lt2 = lt - (m[1] - 0.15)
        bg(cv, shot("D", lt2 * SFPS + 1)); scrims(cv)
        if lt > m[2] - 0.1:
            kk = back((lt - m[2]) / 0.4)
            cv.save(); cv.translate(200, 470); cv.scale(kk, kk)
            cv.drawCircle(0, 0, 95, P(NAVY, 235))
            eye = skia.Path(); eye.moveTo(-58, 0); eye.quadTo(0, -50, 58, 0); eye.quadTo(0, 50, -58, 0); eye.close()
            cv.drawPath(eye, P(CREAM, stroke=7)); cv.drawCircle(0, 0, 17, P(CREAM))
            cv.drawLine(-52, 52, 52, -52, P("#d9534f", stroke=11))
            cv.restore()
    else:
        lt3 = lt - (m[3] - 0.15)
        bg(cv, shot("E", lt3 * SFPS + 1)); scrims(cv)
        night = clamp((lt3 * SFPS / NF["E"] - 0.4) / 0.4)
        def screen(x, y, w, h): feed(cv, x, y, w, h, t, night)
        k = eout(lt3 / 0.5)
        phone(cv, 250, 700 + 500 * (1 - k), 0.55, screen, 255 * k)
        onscreen(cv, "É pra tirar a dúvida, de onde você estiver", 0.2, lt3, size=62)

def s7(cv, t, lt):
    t3 = ts(7, 2) - SC[7] - 0.15
    if lt < t3:
        bg(cv, blurred("D", NF["D"])); scrims(cv)
        k = eout(lt / 0.6)
        draw_photo_card(cv, 190, 290 + 60 * (1 - k), 700, 860, 255 * k, zoom=1.0 + 0.04 * lt / 6)
        cv.drawRRect(rrect(W / 2 - 300, 1100, 600, 92, 46), P(NAVY))
        cv.drawRRect(rrect(W / 2 - 300, 1100, 600, 92, 46), P(GOLD, stroke=3))
        text_c(cv, "Maximiliano", W / 2, 1162, font("m8", 44), P(CREAM))
        onscreen(cv, "Segurança boa começa pela casa de quem vai usar", 0.5, lt, y=1330, size=56)
    else:
        lt2 = lt - t3
        bg(cv, shot("F", lt2 * SFPS + 1)); scrims(cv)
        if lt2 > 0.9:
            kk = back((lt2 - 0.9) / 0.5)
            cv.save(); cv.translate(W / 2 + 40, 480 + 8 * math.sin(t * 4)); cv.scale(kk, kk)
            cv.drawCircle(0, -40, 60, P(GOLD))
            tri = skia.Path(); tri.moveTo(-38, 0); tri.lineTo(0, 64); tri.lineTo(38, 0); tri.close(); cv.drawPath(tri, P(GOLD))
            text_c(cv, "1ª", 0, -20, font("m8", 56), P(NAVY))
            cv.restore()
        onscreen(cv, "A primeira câmera vai na entrada", 0.1, lt2)

def s8(cv, t, lt):
    m = [ts(8, k) - SC[8] for k in range(4)]
    if lt < m[1] - 0.1:
        bg(cv, blurred("B", 1, 0.35)); scrims(cv)
        k = back(lt / 0.6)
        cv.save(); cv.translate(W / 2, 720); cv.scale(k, k)
        cv.drawRRect(rrect(-280, -320, 560, 640, 40), P(CREAM))
        cv.drawRRect(rrect(-280, -320, 560, 170, 40), P("#c0392b")); cv.drawRect(skia.Rect.MakeXYWH(-280, -190, 560, 40), P("#c0392b"))
        text_c(cv, "DEZEMBRO", 0, -210, font("m8", 68), P(CREAM))
        for i in range(5):
            for j in range(7):
                n = i * 7 + j + 1
                if n > 31: continue
                cx, cy = -225 + j * 75, -85 + i * 82
                if n in (24, 25): cv.drawCircle(cx, cy - 12, 32, P(GOLD))
                text_c(cv, str(n), cx, cy, font("m7", 32), P(NAVY))
        cv.restore()
    elif lt < m[2] - 0.1:
        lt2 = lt - (m[1] - 0.1)
        bg(cv, shot("C", 15 + lt2 * SFPS)); scrims(cv)
        for i, s in enumerate(["Instale antes de viajar", "Teste com calma"]):
            kk = (lt2 - 0.2 - i * 1.3) / 0.5
            if kk <= 0: continue
            y = 520 + i * 200
            cv.saveLayerAlpha(None, int(255 * clamp(kk)))
            cv.drawRRect(rrect(90, y - 78, 900, 156, 40), P(NAVY2, 235))
            cv.drawRRect(rrect(90, y - 78, 900, 156, 40), P(GOLD, 180, stroke=3))
            check_icon(cv, 180, y, 44, kk)
            cv.drawString(s, 250, y + 18, font("m8", 50), P(CREAM))
            cv.restore()
    elif lt < m[3] - 0.1:
        lt2 = lt - (m[2] - 0.1)
        bg(cv, shot("G", lt2 * SFPS + 1)); scrims(cv)
        k = eout(lt2 / 0.5)
        text_c(cv, "KIT 2 CÂMERAS", W / 2, 420 - 30 * (1 - k), font("m8", 80), P(GOLD2, 255 * k))
        kk = back((lt2 - 0.6) / 0.4)
        cv.save(); cv.translate(W / 2, 1230); cv.scale(kk, kk)
        cv.drawRRect(rrect(-250, -55, 500, 110, 55), P(GOLD))
        text_c(cv, "link na bio", 0, 18, font("m8", 52), P(NAVY))
        cv.restore()
    else:
        lt2 = lt - (m[3] - 0.1)
        bg(cv, blurred("E", NF["E"], 0.3)); scrims(cv)
        k = eout(lt2 / 0.5)
        draw_photo_circle(cv, W / 2, 620, 290, 255 * k)
        cv.drawRRect(rrect(W / 2 - 260, 945, 520, 160, 40), P(NAVY, int(210 * k)))
        text_c(cv, "Maximiliano", W / 2, 1010, font("m8", 64), P(CREAM, 255 * k))
        text_c(cv, "Infinity Guard", W / 2, 1075, font("m7", 40), P(GOLD, 255 * k))
        kk = back((lt2 - 1.6) / 0.5)
        cv.save(); cv.translate(W / 2, 1200); cv.scale(kk, kk)
        cv.drawRRect(rrect(-330, -52, 660, 104, 52), P("#25a35a"))
        text_c(cv, "Fale comigo no WhatsApp", 0, 16, font("m8", 44), P(CREAM))
        cv.restore()
    if lt >= m[3] - 0.1:
        onscreen(cv, "Instale antes de viajar · link na bio", m[3] - 0.1, lt, y=1390, size=60)

FN = {1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6, 7: s7, 8: s8}

if __name__ == "__main__":
    base.main(FN)
