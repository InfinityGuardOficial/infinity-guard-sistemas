"""Cenário "barbearia": barbearia brasileira moderna (piso xadrez, espelhos com moldura dourada, três cadeiras
de barbeiro, balcão com monitor, sofá de espera, parede azul-marinho com friso dourado) e a câmera bullet ASECAM
DualLight Pro na parede do fundo, cobrindo só a área de atendimento. Dois barbeiros fictícios: Toninho (grisalho, bigode) e Lucas.

Planta (metros): salão de x -4 a 4 e y 0 a 6; vitrine em y=0; espelhos e cadeiras na parede esquerda (x=-4),
cadeiras viradas para -X; balcão com monitor à direita, perto da entrada; câmera bullet na parede do fundo, à direita.
"""
import math, random
import lib3d as L
from lib3d import bpy, mat, emat, box, cyl, sphere, ico, empty, setmat, M, camera
from cenarios import make_person, talk, hold, look, key, vida, walk, aim_dof
from cenarios_ape import texto3d

NAVY_IG, GOLD_IG = (14, 26, 43), (201, 162, 77)
CADEIRAS_Y = (1.6, 3.2, 4.8)
ALINHADA = (-3.0, 3.2, -90.0)       # cadeira do meio no lugar (x, y, rotação em graus)
DESLOCADA = (-2.45, 3.6, -52.0)     # cadeira do meio fora do lugar
CAM = (3.08, 5.75, 2.74)    # frente da câmera bullet (o suporte fica na parede do fundo, y=6)


def bullet(loc, yaw_deg, pitch_deg):
    """câmera bullet ASECAM DualLight Pro (branca, viseira, face preta com lente e três LEDs) com suporte de parede;
    loc é o ponto do suporte na parede do fundo; o corpo aponta para yaw/pitch"""
    branco = mat("bullet_branco", (244, 244, 242), rough=0.35)
    preto = mat("bullet_preto", (16, 16, 20), rough=0.15)
    base = empty(loc)
    box((0, -0.008, 0), (0.11, 0.016, 0.11), branco, 0.008, base)
    for dx, dz in ((-0.038, 0.038), (0.038, -0.038)): sphere((dx, -0.017, dz), 0.006, mat("bullet_parafuso", (150, 150, 150)), base, 8)
    cyl((0, -0.07, 0), 0.016, 0.11, branco, rot=(math.pi / 2, 0, 0), verts=16, parent=base)
    sphere((0, -0.13, 0), 0.024, branco, base, 16)
    corpo = empty((0, -0.13, -0.035)); corpo.parent = base
    corpo.rotation_euler = (math.radians(pitch_deg), 0, math.radians(yaw_deg))
    box((0, 0.01, 0), (0.09, 0.2, 0.08), branco, 0.016, corpo)                  # corpo
    box((0, -0.035, 0.045), (0.1, 0.17, 0.012), branco, 0.004, corpo)            # viseira
    box((0, -0.092, 0), (0.084, 0.012, 0.074), preto, 0.012, corpo)              # face preta
    box((0, -0.0985, 0.012), (0.044, 0.002, 0.03), mat("bullet_janela", (34, 34, 42), rough=0.05), 0.003, corpo)
    sphere((0.004, -0.1, 0.012), 0.009, mat("bullet_lente", (40, 30, 60), rough=0.05), corpo, 16)
    led, led_s = emat("bullet_led", (255, 236, 200), 1.0)
    for dx in (-0.016, 0.0, 0.016):
        cyl((dx, -0.099, -0.018), 0.0065, 0.003, led, rot=(math.pi / 2, 0, 0), verts=16, parent=corpo)
    return base, led_s


def cadeira_barbeiro(loc, rot_deg):
    """cadeira de barbeiro (couro preto, base cromada), de frente para -Y no local"""
    r = empty(loc); r.rotation_euler = (0, 0, math.radians(rot_deg))
    couro = mat("couro_preto", (24, 22, 24), rough=0.35)
    cromo = mat("cromo", (200, 202, 210), rough=0.2, metal=0.9)
    cyl((0, 0, 0.02), 0.32, 0.04, cromo, verts=40, parent=r)
    cyl((0, 0, 0.25), 0.07, 0.42, cromo, verts=24, parent=r)
    box((0, 0, 0.5), (0.56, 0.56, 0.14), couro, 0.05, r)
    box((0, 0.27, 0.86), (0.54, 0.12, 0.62), couro, 0.06, r, rot=(math.radians(-10), 0, 0))
    box((0, 0.33, 1.28), (0.26, 0.1, 0.16), couro, 0.04, r)
    for x in (-0.31, 0.31):
        box((x, -0.02, 0.7), (0.08, 0.5, 0.06), couro, 0.03, r)
        box((x, -0.02, 0.6), (0.03, 0.04, 0.2), cromo, 0.0, r)
    box((0, -0.42, 0.18), (0.4, 0.2, 0.025), cromo, 0.005, r, rot=(math.radians(15), 0, 0))
    box((0, -0.33, 0.3), (0.04, 0.04, 0.26), cromo, 0.0, r)
    return r


def vassoura(parent):
    g = empty((0, 0, 0)); g.parent = parent
    cyl((0, -0.52, 0.5), 0.016, 1.05, mat("cabo_madeira", (150, 110, 70)), rot=(-0.36, 0, 0), verts=10, parent=g)
    box((0, -0.71, 0.05), (0.42, 0.07, 0.07), mat("vassoura_cabeca", (40, 40, 46)), 0.01, g)
    box((0, -0.71, 0.0), (0.4, 0.06, 0.04), mat("vassoura_cerdas", (180, 70, 50)), 0.0, g)
    return g


def nota(parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """nota de dinheiro estilizada (sem valor escrito)"""
    g = empty(loc); g.rotation_euler = rot
    if parent: g.parent = parent
    box((0, 0, 0), (0.15, 0.002, 0.07), mat("nota_azul", (90, 140, 170)), 0.0, g)
    box((0, 0.0012, 0), (0.13, 0.0005, 0.055), mat("nota_centro", (150, 190, 205)), 0.0, g)
    sphere((0.04, 0.0015, 0), 0.015, mat("nota_selo", (70, 110, 140)), g, 10, scale=(1, 0.1, 1))
    return g


def barbeiro(kind, skin, hair, shirt, avental, height=1.0):
    p = make_person((30, 30, -20), skin=skin, hair=hair, style="curto", shirt=shirt, pants=(36, 36, 44), height=height, avental=avental)
    if kind == "toninho":  # bigode grisalho
        box((0, -0.168, 0.104), (0.09, 0.022, 0.02), mat("bigode", (105, 102, 100)), 0.008, p["head"])
    return p


def barbearia(kind):
    N, FPS = L.N, L.FPS
    f = lambda sec: 1 + sec * FPS
    random.seed(21)
    claro, escuro = mat("piso_claro", (232, 228, 220), rough=0.3), mat("piso_escuro", (30, 30, 34), rough=0.3)
    for i in range(16):
        for j in range(12):
            box((-3.75 + i * 0.5, 0.25 + j * 0.5, 0.005), (0.5, 0.5, 0.01), claro if (i + j) % 2 else escuro, 0.0)
    navy = mat("parede_navy", NAVY_IG, rough=0.6); ouro = mat("friso_ouro", GOLD_IG, rough=0.3, metal=0.8)
    tijolo = mat("parede_tijolo", (150, 86, 62), rough=0.8)
    box((-4.1, 3, 1.6), (0.2, 6.2, 3.2), navy, 0.0); box((0, 6.1, 1.6), (8.4, 0.2, 3.2), tijolo, 0.0)
    for i in range(14):  # juntas do tijolo aparente
        box((0, 6.0, 0.15 + i * 0.22), (8.2, 0.01, 0.015), mat("rejunte", (200, 190, 175)), 0.0)
    box((4.1, 3, 1.6), (0.2, 6.2, 3.2), mat("parede_clara", (226, 218, 204)), 0.0)
    box((0, 3, 3.25), (8.4, 6.4, 0.1), mat("forro_escuro", (40, 40, 46)), 0.0)
    box((0, -0.1, 0.3), (8.4, 0.2, 0.6), navy, 0.0)
    box((0, -0.1, 1.7), (8.4, 0.05, 2.2), mat("vitrine_dia", (225, 238, 250), emit=1.6), 0.0)
    texto3d("BARBEARIA", (0, 5.98, 2.55), 0.32, mat("letreiro", GOLD_IG, emit=1.8), (math.pi / 2, 0, 0))
    box((0, 5.99, 2.12), (2.6, 0.01, 0.02), ouro, 0.0)
    # bancadas com espelhos e as três cadeiras
    espelho = mat("espelho", (190, 205, 215), rough=0.05, metal=1.0)
    cadeiras = []
    for y in CADEIRAS_Y:
        box((-3.97, y, 1.55), (0.04, 0.95, 1.2), ouro, 0.01); box((-3.94, y, 1.55), (0.03, 0.87, 1.12), espelho, 0.0)
        box((-3.75, y, 0.85), (0.5, 1.0, 0.06), mat("bancada", (60, 44, 34), rough=0.4), 0.01)
        for k in range(3):
            cyl((-3.82, y - 0.3 + k * 0.12, 0.95), 0.025, 0.14, mat("frasco%d" % k, [(201, 162, 77), (40, 60, 90), (230, 230, 230)][k]), verts=12)
        bpy.ops.object.light_add(type="POINT", location=(-3.2, y, 2.6)); pl = bpy.context.object; pl.data.energy = 80
        pl.data.color = (1, 0.82, 0.6); pl.data.shadow_soft_size = 0.25
        cyl((-3.2, y, 2.95), 0.005, 0.6, mat("fio_preto", (20, 20, 20)), verts=6)
        sphere((-3.2, y, 2.62), 0.1, mat("pendente", (255, 220, 160), emit=5), None, 14)
        if y != ALINHADA[1]: cadeiras.append(cadeira_barbeiro((-3.0, y, 0), -90))
    meio = cadeira_barbeiro((ALINHADA[0], ALINHADA[1], 0), ALINHADA[2])
    # balcão com monitor, perto da entrada
    madeira = mat("balcao_madeira", (92, 62, 42), rough=0.4)
    box((2.9, 1.25, 0.55), (0.7, 1.6, 1.1), madeira, 0.02); box((2.9, 1.25, 1.12), (0.8, 1.7, 0.05), mat("tampo_preto", (20, 20, 24)), 0.01)
    box((2.55, 1.25, 0.55), (0.02, 1.5, 0.08), ouro, 0.0)
    mon = empty((2.95, 1.25, 1.15)); mon.rotation_euler = (0, 0, math.radians(90))  # tela virada para -X
    box((0, 0, 0.03), (0.2, 0.15, 0.02), mat("monitor", (24, 24, 28)), 0.005, mon)
    box((0, 0.0, 0.12), (0.03, 0.03, 0.18), mat("monitor", (24, 24, 28)), 0.0, mon)
    box((0, -0.01, 0.38), (0.56, 0.03, 0.34), mat("monitor", (24, 24, 28)), 0.008, mon)
    tela, tela_s = emat("tela_monitor", (150, 190, 230), 1.4)
    box((0, -0.027, 0.38), (0.52, 0.002, 0.3), tela, 0.0, mon)
    # espera: sofá de couro caramelo, mesinha, plantas e quadros
    caramelo = mat("sofa_caramelo", (150, 92, 52), rough=0.5)
    box((3.6, 4.2, 0.25), (0.75, 1.9, 0.42), caramelo, 0.08); box((3.9, 4.2, 0.65), (0.22, 1.9, 0.6), caramelo, 0.08)
    cyl((2.9, 4.2, 0.25), 0.25, 0.04, mat("mesinha", (30, 30, 34)), verts=24)
    for x, y in ((3.6, 5.6), (3.6, 2.7), (-3.6, 5.7)):
        cyl((x, y, 0.22), 0.2, 0.44, mat("vaso_preto", (30, 30, 34)), verts=20)
        for k in range(5):
            ico((x + random.uniform(-0.12, 0.12), y + random.uniform(-0.12, 0.12), 0.65 + k * 0.17), 0.2, M["leaf"] if k % 2 else M["leaf2"], 1)
    for x in (-1.6, 1.6):
        box((x, 5.98, 1.55), (0.8, 0.02, 0.6), ouro, 0.0); box((x, 5.97, 1.55), (0.72, 0.02, 0.52), mat("quadro_bw", (60, 60, 64)), 0.0)
    bpy.ops.object.light_add(type="AREA", location=(0, 3, 3.1)); ar = bpy.context.object; ar.data.energy = 220; ar.data.size = 5
    ar.data.color = (1, 0.92, 0.82)
    bpy.ops.object.light_add(type="AREA", location=(0, 0.3, 2.0), rotation=(math.radians(-80), 0, 0)); vl = bpy.context.object
    vl.data.energy = 180; vl.data.size = 6; vl.data.color = (0.92, 0.96, 1)
    w = bpy.data.worlds.new("barbearia"); bpy.context.scene.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.06, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.5
    # a câmera bullet na parede do fundo, mirando as cadeiras (área de atendimento)
    d, led = bullet((3.3, 5.99, 2.85), -63, 17)
    # personagens fictícios
    toninho = barbeiro("toninho", "negra", "grisalho", (44, 44, 52), (110, 72, 46))
    lucas = barbeiro("lucas", "parda", "preto", (240, 240, 244), (24, 24, 28), height=1.03)
    vida(toninho, N, 21); vida(lucas, N, 22)
    cam = camera((0, 0, 0), (0, 0, 0), 35)
    lens = lambda mm: setattr(cam.data, "lens", mm)
    poe = lambda p, x, y, deg: (setattr(p["root"], "location", (x, y, 0.0)), setattr(p["root"], "rotation_euler", (0, 0, math.radians(deg))))
    sorri = lambda p, fr, s=(1.9, 0.3, 0.45): (setattr(p["mouth"], "scale", s), p["mouth"].keyframe_insert("scale", frame=max(1, int(fr))))

    def cadeira_em(fr, pos):
        key(meio, "location", fr, (pos[0], pos[1], 0)); key(meio, "rotation_euler", fr, (0, 0, math.radians(pos[2])))

    def ri(p, f0, f1):
        """gargalhada: boca aberta e cabeça balançando"""
        sorri(p, f0, (1.8, 0.3, 1.1))
        for i, fr in enumerate(range(int(f0), int(f1), 3)):
            key(p["head"], "rotation_euler", fr, (-0.18 if i % 2 else -0.05, 0, 0.05 * math.sin(i)))
        key(p["head"], "rotation_euler", f1, (0, 0, 0)); sorri(p, f1, (1.9, 0.3, 0.45))

    def aponta(p, fr, braco="armR"):
        key(p[braco], "rotation_euler", fr, (-1.5, 0, 0))

    def solta(p, fr):
        key(p["armL"], "rotation_euler", fr, (0, 0, 0)); key(p["armR"], "rotation_euler", fr, (0, 0, 0))

    def cintura(p, fr):  # mãos na cintura
        key(p["armL"], "rotation_euler", fr, (0, 0.55, 0)); key(p["armR"], "rotation_euler", fr, (0, -0.55, 0))

    if kind == "aposta":         # 0–5 s: os dois discutem, sorrindo, diante da cadeira deslocada
        cadeira_em(1, DESLOCADA)
        poe(toninho, -1.8, 3.0, 35); poe(lucas, -0.75, 2.65, -55)
        talk(toninho, f(0.2), f(1.6)); aponta(toninho, f(0.3)); key(toninho["armR"], "rotation_euler", f(1.6), (-1.5, 0, 0))
        key(toninho["armR"], "rotation_euler", f(2.0), (-0.9, -0.7, 0))  # mão no peito: "não mexeram"
        nt = nota(lucas["armR"], (0, -0.05, -0.62), (math.pi / 2, 0, 0))
        key(lucas["armR"], "rotation_euler", f(2.2), (0, 0, 0)); key(lucas["armR"], "rotation_euler", f(2.8), (-1.25, 0, 0.15))
        talk(lucas, f(2.6), f(4.0)); sorri(toninho, f(2.2)); sorri(lucas, 1)
        look(lucas, 1, 0, 0); look(toninho, f(3.5), 0.05, -0.2)
        aim_dof(cam, (-1.2, 0.55, 1.62), (-1.55, 2.95, 1.4), 1, 2.4)
        aim_dof(cam, (-1.25, 0.85, 1.6), (-1.55, 2.95, 1.4), N, 2.4)
        lens(22)
    elif kind == "manha":        # 5–11 s: de manhã, Lucas chega e encontra a cadeira fora do lugar outra vez
        cadeira_em(1, DESLOCADA)
        poe(lucas, 1.0, 0.4, 20)
        walk(lucas, f(0.3), f(3.0), (1.0, 0.4), (-1.15, 2.45))
        key(lucas["root"], "rotation_euler", f(2.6), (0, 0, math.radians(20))); key(lucas["root"], "rotation_euler", f(3.4), (0, 0, math.radians(140)))
        cintura(lucas, f(3.8)); look(lucas, f(3.6), 0.2, 0); look(lucas, f(5.0), 0.15, 0.25)
        aim_dof(cam, (-2.2, 5.5, 1.15), (-1.0, 2.2, 1.3), 1, 2.8)
        aim_dof(cam, (-2.05, 5.3, 1.2), (-1.1, 2.4, 1.35), N, 2.8)
        lens(28)
    elif kind == "insiste":      # 11–18 s: Toninho insiste que deixou a cadeira alinhada; Lucas desconfia
        cadeira_em(1, DESLOCADA)
        poe(lucas, -0.8, 2.35, -45); poe(toninho, -1.85, 2.75, 40)
        cintura(lucas, 1); look(lucas, 1, 0.05, 0.3)
        key(toninho["armR"], "rotation_euler", f(0.5), (0, 0, 0)); key(toninho["armR"], "rotation_euler", f(1.1), (-1.5, 0, 0.3))
        key(toninho["armR"], "rotation_euler", f(2.6), (-1.5, 0, 0.3)); key(toninho["armR"], "rotation_euler", f(3.2), (-0.9, -0.7, 0))
        key(toninho["armR"], "rotation_euler", f(5.6), (-0.9, -0.7, 0)); key(toninho["armR"], "rotation_euler", f(6.2), (0, 0, 0))
        talk(toninho, f(0.6), f(3.0)); talk(toninho, f(3.6), f(5.4))
        for i, t_ in enumerate((3.6, 4.0, 4.4, 4.8)):  # "não fui eu" balançando a cabeça
            key(toninho["head"], "rotation_euler", f(t_), (0, 0, 0.25 if i % 2 else -0.25))
        key(toninho["head"], "rotation_euler", f(5.2), (0, 0, 0))
        key(lucas["head"], "rotation_euler", f(5.0), (0.05, 0.12, 0.3)); sorri(lucas, f(5.5), (1.5, 0.3, 0.3))
        aim_dof(cam, (-1.2, 0.45, 1.62), (-1.32, 2.55, 1.5), 1, 2.2)
        aim_dof(cam, (-1.25, 0.75, 1.6), (-1.32, 2.55, 1.5), N, 2.2)
        lens(22)
    elif kind == "camera":       # 18–24 s: a câmera na parede; Lucas vai ao monitor do balcão
        cadeira_em(1, DESLOCADA)
        poe(lucas, 2.1, 2.2, 160)
        walk(lucas, f(2.0), f(3.6), (2.1, 2.2), (2.2, 1.25))
        key(lucas["root"], "rotation_euler", f(3.4), (0, 0, math.radians(160))); key(lucas["root"], "rotation_euler", f(4.0), (0, 0, math.radians(90)))
        look(lucas, f(4.2), 0.2, 0)
        for t_, e in ((0, 0.6), (4.0, 0.6), (4.4, 2.0)):
            tela_s.default_value = e; tela_s.keyframe_insert("default_value", frame=int(f(t_)))
        aim_dof(cam, (2.92, 5.3, 2.6), (3.24, 5.83, 2.8), 1, 1.6)
        aim_dof(cam, (2.85, 5.2, 2.56), (3.24, 5.83, 2.8), int(f(1.8)), 1.6)
        aim_dof(cam, (0.6, 2.4, 1.75), (2.6, 1.25, 1.35), N, 2.6)
        lens(35)
    elif kind == "pov":          # 24–31 s: imagem da câmera (ao vivo): Toninho varre e empurra a cadeira sem perceber
        cadeira_em(1, ALINHADA)
        poe(toninho, -1.7, 1.2, 0); vassoura(toninho["root"])
        key(toninho["armL"], "rotation_euler", 1, (-0.6, 0, -0.15)); key(toninho["armR"], "rotation_euler", 1, (-0.6, 0, 0.15))
        walk(toninho, f(0.2), f(5.0), (-1.7, 1.2), (-2.25, 4.1), arms=False)
        key(toninho["root"], "rotation_euler", 1, (0, 0, math.radians(170)))
        for i, t_ in enumerate([x * 0.4 for x in range(15)]):  # varrendo: o corpo gira de leve
            key(toninho["root"], "rotation_euler", f(t_), (0, 0, math.radians(170 + (14 if i % 2 else -14))))
        cadeira_em(f(2.9), ALINHADA); cadeira_em(f(3.6), DESLOCADA)  # o quadril bate na cadeira
        poe(lucas, 2.2, 1.25, 90)
        cam.data.lens = 30
        aim_dof(cam, CAM, (-2.3, 3.0, 0.8), 1, 16.0)
    elif kind == "flagra":       # 31–36 s: Lucas se vira do monitor e flagra Toninho com a vassoura ao lado da cadeira
        cadeira_em(1, DESLOCADA)
        poe(toninho, -2.25, 4.1, 170); vassoura(toninho["root"])
        key(toninho["armL"], "rotation_euler", 1, (-0.6, 0, -0.15)); key(toninho["armR"], "rotation_euler", 1, (-0.6, 0, 0.15))
        poe(lucas, 2.2, 1.25, 90)
        key(lucas["root"], "rotation_euler", f(0.6), (0, 0, math.radians(90))); key(lucas["root"], "rotation_euler", f(1.4), (0, 0, math.radians(-123)))
        key(toninho["root"], "rotation_euler", f(2.0), (0, 0, math.radians(170))); key(toninho["root"], "rotation_euler", f(2.6), (0, 0, math.radians(57)))
        for b in toninho["brows"]:
            key(b, "location", f(2.7), (b.location.x, b.location.y, b.location.z)); key(b, "location", f(2.9), (b.location.x, b.location.y, b.location.z + 0.02))
        sorri(toninho, f(2.8), (0.9, 0.3, 0.9)); sorri(lucas, f(2.2), (1.9, 0.3, 0.5))
        aim_dof(cam, (0.9, 1.6, 1.7), (-2.15, 3.95, 1.4), 1, 2.6)
        aim_dof(cam, (0.6, 1.9, 1.68), (-2.15, 3.95, 1.4), N, 2.6)
        lens(42)
    elif kind == "risos":        # 36–42 s: os dois riem; Toninho admite e paga a aposta
        cadeira_em(1, DESLOCADA)
        poe(toninho, -1.65, 2.6, 55); poe(lucas, -0.95, 2.45, -60)
        key(toninho["armL"], "rotation_euler", f(0.3), (0, 0, 0)); key(toninho["armL"], "rotation_euler", f(0.9), (-2.7, 0, 0.3))  # mão na testa
        key(toninho["armL"], "rotation_euler", f(2.6), (-2.7, 0, 0.3)); key(toninho["armL"], "rotation_euler", f(3.1), (0, 0, 0))
        ri(toninho, f(0.6), f(4.6)); ri(lucas, f(0.4), f(4.4))
        nt = nota(toninho["armR"], (0, -0.05, -0.62), (math.pi / 2, 0, 0))
        nt.scale = (0.001, 0.001, 0.001); nt.keyframe_insert("scale", frame=int(f(3.0)))
        nt.scale = (1, 1, 1); nt.keyframe_insert("scale", frame=int(f(3.1)))
        key(toninho["armR"], "rotation_euler", f(3.2), (0, 0, 0)); key(toninho["armR"], "rotation_euler", f(3.9), (-1.3, 0, 0))
        nt.scale = (1, 1, 1); nt.keyframe_insert("scale", frame=int(f(4.4)))
        nt.scale = (0.001, 0.001, 0.001); nt.keyframe_insert("scale", frame=int(f(4.5)))
        n2 = nota(lucas["armR"], (0, -0.05, -0.62), (math.pi / 2, 0, 0))
        n2.scale = (0.001, 0.001, 0.001); n2.keyframe_insert("scale", frame=int(f(4.4)))
        n2.scale = (1, 1, 1); n2.keyframe_insert("scale", frame=int(f(4.5)))
        key(lucas["armR"], "rotation_euler", f(3.4), (0, 0, 0)); key(lucas["armR"], "rotation_euler", f(4.0), (-1.3, 0, 0))
        key(lucas["armR"], "rotation_euler", f(5.0), (-1.3, 0, 0)); key(lucas["armR"], "rotation_euler", f(5.6), (-0.5, 0, 0))
        aim_dof(cam, (-1.25, 0.55, 1.62), (-1.3, 2.55, 1.48), 1, 2.4)
        aim_dof(cam, (-1.28, 0.8, 1.6), (-1.3, 2.55, 1.48), N, 2.4)
        lens(22)
    elif kind == "final":        # 42–46 s: Lucas devolve a cadeira ao lugar; o salão em plano aberto
        poe(lucas, -2.2, 3.0, -60)
        cadeira_em(1, DESLOCADA); cadeira_em(f(0.4), DESLOCADA); cadeira_em(f(1.6), ALINHADA)
        hold(lucas, f(0.2), True); hold(lucas, f(1.8), False)
        walk(lucas, f(0.4), f(1.6), (-2.2, 3.0), (-2.45, 3.05), arms=False)
        poe(toninho, -0.9, 2.0, 50); sorri(toninho, 1); sorri(lucas, f(1.8))
        key(lucas["root"], "rotation_euler", f(1.8), (0, 0, math.radians(-60))); key(lucas["root"], "rotation_euler", f(2.4), (0, 0, math.radians(-110)))
        aim_dof(cam, (1.4, 0.9, 1.7), (-2.0, 3.2, 1.2), 1, 5.0)
        aim_dof(cam, (2.2, 0.5, 2.1), (-1.6, 3.4, 1.4), N, 5.0)
        lens(24)
    return cam


L.CENARIOS["barbearia"] = lambda kind="aposta": barbearia(kind)
