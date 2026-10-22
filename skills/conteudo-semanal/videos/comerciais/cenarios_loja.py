"""Cenário "loja": pequeno comércio de bairro brasileiro (loja de variedades fictícia).

Planta (metros): fachada em y=0 virada para a rua (-Y), salão de x -4 a 4 e y 0 a 8. Porta de enrolar em
x -2..1, vitrine em x 1.5..3.6, balcão com caixa à direita, prateleiras no fundo e à esquerda, e um cômodo
privado (banheiro e estoque) no canto do fundo à esquerda, x -4..-1.4, y 5.6..8, onde não vai câmera.
"""
import math, random
import lib3d as L
from lib3d import bpy, Vector, mat, emat, box, cyl, sphere, ico, cone, empty, setmat, M, make_tree, make_car, ground, world, sun, camera, anime_clouds, hills
from cenarios import make_person, talk, walk, hold, look, key, vida, dual_cam, fov_cone, aim_dof, package

NOME_LOJA = "Variedades da Rosa"
PRIV = (-4.0, -1.4, 5.6, 8.0)  # área privada: x0, x1, y0, y1


def texto3d(txt, loc, size, m, rot=(math.pi / 2, 0, 0), parent=None, extr=0.02):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.object; t.data.body = txt; t.data.size = size; t.data.align_x = "CENTER"
    t.data.extrude = extr; t.data.materials.append(m)
    if parent: t.parent = parent
    return t


def prateleira(x, y, w, rot=0.0, seed=0):
    """gôndola com 4 níveis cheios de produtos coloridos"""
    rnd = random.Random(seed)
    g = empty((x, y, 0)); g.rotation_euler = (0, 0, rot)
    wood = mat("gondola", (225, 225, 220))
    box((0, 0.25, 1.0), (w, 0.08, 2.0), wood, 0.02, g)
    cores = [(214, 64, 52), (240, 180, 40), (52, 120, 200), (70, 160, 90), (240, 120, 40), (150, 80, 170), (250, 245, 235)]
    for k in range(4):
        z = 0.12 + k * 0.48
        box((0, 0, z), (w, 0.5, 0.04), wood, 0.01, g)
        xx = -w / 2 + 0.08
        while xx < w / 2 - 0.12:
            bw = rnd.uniform(0.1, 0.22); bh = rnd.uniform(0.18, 0.36)
            c = rnd.choice(cores)
            if rnd.random() < 0.35:
                cyl((xx + bw / 2, 0, z + 0.02 + bh / 2), bw / 2.2, bh, mat("prod%d%d%d" % c, c), verts=10, parent=g)
            else:
                box((xx + bw / 2, 0, z + 0.02 + bh / 2), (bw, 0.3, bh), mat("prod%d%d%d" % c, c), 0.01, g)
            xx += bw + 0.03
    return g


def porta_enrolar(x0, x1, top=3.0):
    """porta de aço de enrolar: as lâminas sobem para dentro da caixa acima da porta"""
    g = empty((0, 0, 0))
    aco = mat("aco", (176, 180, 188), rough=0.4); aco2 = mat("aco2", (150, 154, 162), rough=0.4)
    n = int(top / 0.12)
    for k in range(n):
        box(((x0 + x1) / 2, -0.02, 0.06 + k * 0.12), (x1 - x0, 0.05, 0.11), aco if k % 2 else aco2, 0.01, g)
    box(((x0 + x1) / 2, -0.06, 0.05), (x1 - x0, 0.08, 0.1), mat("aco_base", (90, 94, 100)), 0.02, g)
    placa = texto3d("ABRE ÀS 8H", ((x0 + x1) / 2, -0.06, 1.4), 0.28, mat("tinta_placa", (200, 40, 40)), parent=g)
    return g


def loja(kind):
    N, FPS = L.N, L.FPS
    f = lambda sec: 1 + sec * FPS
    random.seed(11)
    ground(400, "grass")
    # rua, calçada em ondas (estilo calçada portuguesa) e meio-fio
    box((0, -9, 0.02), (80, 7, 0.04), M["road"], 0.0)
    for x in range(-40, 40, 6): box((x, -9, 0.05), (2.4, 0.18, 0.02), M["line"], 0.0)
    pedra1, pedra2 = mat("pedra1", (236, 232, 222)), mat("pedra2", (60, 60, 64))
    box((0, -2.75, 0.06), (80, 5.5, 0.1), pedra1, 0.0)
    for i in range(-40, 40):
        for j in range(3):
            box((i + 0.5 + 0.25 * math.sin(j * 1.7), -1.1 - j * 1.6, 0.115), (0.55, 0.22, 0.012), pedra2, 0.0,
                rot=(0, 0, 0.6 * math.sin(i * 0.9 + j)))
    box((0, -5.55, 0.08), (80, 0.18, 0.16), mat("meiofio", (190, 190, 186)), 0.01)
    # fachada com abertura da porta e vitrine
    fach = mat("fach_rosa", (238, 160, 150)); fach2 = mat("fach_creme", (240, 228, 200))
    box((-3.0, 0.1, 2.1), (2.0, 0.2, 4.2), fach, 0.03)
    box((1.25, 0.1, 2.1), (0.5, 0.2, 4.2), fach, 0.03)
    box((3.8, 0.1, 2.1), (0.4, 0.2, 4.2), fach, 0.03)
    box((0, 0.1, 3.6), (8.0, 0.2, 1.2), fach, 0.03)
    box((2.55, 0.1, 0.4), (2.1, 0.2, 0.8), fach, 0.03)
    box((2.55, 0.05, 1.9), (2.1, 0.06, 2.2), M["glass"], 0.01)  # vitrine
    for x in (1.5, 3.6): box((x, 0.0, 1.9), (0.06, 0.08, 2.3), mat("caixilho", (60, 60, 66)), 0.0)
    # letreiro e toldo listrado
    box((0, -0.12, 3.62), (5.4, 0.12, 0.8), mat("letreiro", (25, 40, 80)), 0.04)
    texto3d(NOME_LOJA, (0, -0.2, 3.5), 0.42, mat("letra", (250, 220, 120), emit=0.6))
    for k in range(8):
        box((1.6 + k * 0.27, -0.55, 3.0), (0.26, 1.1, 0.06), mat("toldo%d" % (k % 2), (200, 50, 50) if k % 2 else (245, 245, 240)), 0.0,
            rot=(math.radians(-22), 0, 0))
    # salão: piso, paredes, forro
    for i in range(8):
        for j in range(8):
            box((-3.5 + i, 0.5 + j, 0.03), (0.98, 0.98, 0.04), mat("piso_bege%d" % ((i + j) % 2), (226, 214, 190) if (i + j) % 2 else (212, 198, 172)), 0.0)
    parede = mat("parede_int", (226, 218, 200))
    box((-4.1, 4, 2.1), (0.2, 8, 4.2), parede, 0.0); box((4.1, 4, 2.1), (0.2, 8, 4.2), parede, 0.0)
    box((0, 8.1, 2.1), (8.4, 0.2, 4.2), parede, 0.0)
    if kind != "planta":
        box((0, 4, 4.25), (8.4, 8.2, 0.1), parede, 0.0)
        for x in (-2, 0, 2):
            box((x, 4, 4.18), (0.25, 7, 0.04), mat("lumin", (255, 255, 240), emit=2), 0.0)
            bpy.ops.object.light_add(type="AREA", location=(x, 4, 4.0)); l = bpy.context.object
            l.data.energy = 35; l.data.size = 1.5; l.rotation_euler = (0, 0, 0)
    # cômodo privado (banheiro e estoque) com porta e plaquinha
    x0, x1, y0, y1 = PRIV
    box(((x0 + x1) / 2 + 0.55, y0, 1.5), (x1 - x0 - 1.1, 0.12, 3.0), parede, 0.0)
    box((x1, (y0 + y1) / 2, 1.5), (0.12, y1 - y0, 3.0), parede, 0.0)
    box((x0 + 0.5, y0 - 0.03, 1.05), (0.9, 0.06, 2.1), mat("porta_wc", (120, 150, 190)), 0.02)
    texto3d("BANHEIRO · ESTOQUE", (x0 + 0.5, y0 - 0.08, 2.25), 0.13, mat("tinta_preta", (30, 30, 36)))
    # prateleiras, balcão e caixa
    prateleira(-1.0, 7.4, 3.6, 0, 1); prateleira(1.9, 7.4, 3.0, 0, 2)
    prateleira(-3.6, 3.0, 4.0, math.radians(90), 3)
    prateleira(-0.6, 3.6, 3.0, 0, 4)
    balcao = mat("balcao", (150, 100, 64)); tampo = mat("tampo", (230, 226, 216), rough=0.3)
    box((2.6, 2.2, 0.5), (1.0, 2.6, 1.0), balcao, 0.03); box((2.6, 2.2, 1.03), (1.15, 2.75, 0.06), tampo, 0.02)
    box((2.55, 1.6, 1.2), (0.36, 0.3, 0.26), mat("caixa_reg", (40, 44, 52)), 0.03)
    box((2.55, 1.52, 1.45), (0.3, 0.04, 0.22), mat("tela_caixa", (90, 200, 160), emit=1.5), 0.01, rot=(math.radians(-15), 0, 0))
    box((2.6, 2.7, 1.1), (0.4, 0.3, 0.08), mat("maquininha", (30, 30, 34)), 0.02)
    for k in range(5):  # potes de bala no balcão
        cyl((2.35 + (k % 2) * 0.3, 2.9 + k * 0.12, 1.2), 0.08, 0.22, mat("pote%d" % k, [(240, 90, 90), (250, 200, 60), (90, 170, 230), (130, 200, 110), (240, 140, 200)][k]), verts=12)
    ico((-3.5, 0.6, 0.5), 0.5, M["leaf"], 1, scale=(1, 1, 1.4)); cyl((-3.5, 0.6, 0.2), 0.3, 0.4, mat("vaso", (170, 90, 60)), verts=14)
    # lojas vizinhas, poste com fios, árvore e carro estacionado
    for cx, cor, nome in ((-8.6, (150, 196, 210), "PADARIA"), (8.6, (230, 210, 120), "FARMÁCIA")):
        box((cx, 0.1, 2.1), (8.8, 0.2, 4.2), mat("viz%d%d%d" % cor, cor), 0.03)
        box((cx, -0.05, 1.5), (3.0, 0.1, 3.0), mat("aco_viz", (160, 164, 172), rough=0.4), 0.0)
        box((cx, -0.14, 3.62), (4.0, 0.1, 0.7), mat("letreiro_viz", (240, 240, 236)), 0.03)
        texto3d(nome, (cx, -0.2, 3.5), 0.4, mat("letra_viz", (40, 60, 120)))
    for x in (-6, 6):
        cyl((x, -5.2, 3.5), 0.12, 7, M["pole"], verts=10)
        box((x, -5.2, 6.6), (1.4, 0.1, 0.1), M["pole"], 0.0)
    for z in (6.4, 6.2):
        box((0, -5.2, z), (12, 0.02, 0.02), mat("fio", (20, 20, 20)), 0.0)
    make_tree((-12.5, -4.4, 0), 1.1); make_tree((12.5, -4.4, 0), 1.0)
    car, _w = make_car((-9.5, -6.6, 0), luggage=False, body="suitcase2"); car.scale = (0.95, 0.95, 0.95)
    hills(0, 90, 10, 220)
    world((70, 140, 230), (190, 226, 250), 1.0); anime_clouds(0, 140, 6, 260, (28, 50))
    sun((math.radians(58), 0, math.radians(-28)), 3.4, (1, 0.95, 0.85))

    # personagens fictícios
    rosa = make_person((30, 30, -20), skin="clara", hair="castanho", style="coque", shirt=(230, 110, 140), pants=(50, 60, 90), avental=(40, 120, 80))
    julia = make_person((30, 30, -20), skin="negra", hair="preto", style="rabo", shirt=(250, 240, 230), pants=(40, 40, 50), avental=(40, 120, 80), height=0.97)
    paulo = make_person((30, 30, -20), skin="morena", hair="preto", style="curto", shirt=(70, 110, 170), pants=(80, 70, 60), bone=(230, 120, 40), height=1.03)
    for i, p in enumerate((rosa, julia, paulo)): vida(p, N, i)
    porta = porta_enrolar(-2.0, 1.0)
    cam = camera((0, 0, 0), (0, 0, 0), 35)
    estado = {"porta_aberta": kind not in ("chegada", "relogio", "abre"), "personagens": (rosa, julia, paulo)}
    if estado["porta_aberta"]:
        porta.location.z = 3.3

    if kind == "chegada":       # 0–2,6 s: o cliente chega, a loja ainda fechada
        paulo["root"].location = (-6.0, -2.4, 0.12)
        walk(paulo, 1, f(2.2), (-6.0, -2.4), (-0.6, -1.3))
        key(paulo["root"], "rotation_euler", 1, (0, 0, math.radians(90)))
        key(paulo["root"], "rotation_euler", f(2.0), (0, 0, math.radians(90)))
        key(paulo["root"], "rotation_euler", f(2.5), (0, 0, math.radians(180)))
        aim_dof(cam, (-4.0, -9.5, 2.4), (-1.2, -1.2, 1.6), 1, 4.0)
        aim_dof(cam, (-2.4, -8.6, 2.2), (-0.6, -1.2, 1.5), N, 4.0)
    elif kind == "relogio":     # 2,6–5 s: olha o relógio diante da porta fechada
        paulo["root"].location = (-0.6, -1.0, 0.12); paulo["root"].rotation_euler = (0, 0, math.radians(-15))
        key(paulo["armL"], "rotation_euler", f(0.3), (0, 0, 0)); key(paulo["armL"], "rotation_euler", f(0.8), (-1.25, 0, 0.45))
        key(paulo["armL"], "rotation_euler", f(1.8), (-1.25, 0, 0.45)); key(paulo["armL"], "rotation_euler", f(2.2), (0, 0, 0))
        look(paulo, f(0.5), 0.0, 0); look(paulo, f(0.9), 0.45, math.radians(-15)); look(paulo, f(1.8), 0.45, math.radians(-15))
        look(paulo, f(2.2), -0.1, math.radians(-10))
        aim_dof(cam, (0.5, -3.6, 1.55), (-0.6, -1.0, 1.5), 1, 2.4)
        aim_dof(cam, (0.3, -3.2, 1.58), (-0.6, -1.0, 1.55), N, 2.4)
    elif kind == "abre":        # 5–9 s: a porta sobe, Rosa cumprimenta e o cliente entra
        key(porta, "location", 1, (0, 0, 0)); key(porta, "location", f(0.3), (0, 0, 0)); key(porta, "location", f(1.6), (0, 0, 3.3))
        rosa["root"].location = (-0.4, 1.2, 0.07)
        paulo["root"].location = (-0.6, -1.3, 0.12); paulo["root"].rotation_euler = (0, 0, math.radians(180))
        key(rosa["armR"], "rotation_euler", f(1.6), (0, 0, 0)); key(rosa["armR"], "rotation_euler", f(2.0), (-2.5, 0, -0.3))
        key(rosa["armR"], "rotation_euler", f(2.6), (-2.5, 0, -0.3)); key(rosa["armR"], "rotation_euler", f(3.0), (0, 0, 0))
        talk(rosa, f(0.7), f(2.9))
        walk(paulo, f(3.0), f(4.0), (-0.6, -1.3), (-0.5, 0.4))
        aim_dof(cam, (2.2, -4.6, 1.5), (-0.5, 0.2, 1.45), 1, 3.2)
        aim_dof(cam, (1.6, -4.0, 1.55), (-0.5, 0.4, 1.5), N, 3.2)
    elif kind == "conversa":    # 9–15 s: Rosa no caixa conversa com Júlia; cliente nas prateleiras ao fundo
        rosa["root"].location = (3.4, 2.0, 0.07); rosa["root"].rotation_euler = (0, 0, math.radians(-90 - 20))
        julia["root"].location = (1.0, 2.4, 0.07); julia["root"].rotation_euler = (0, 0, math.radians(90 - 10))
        paulo["root"].location = (-0.8, 5.2, 0.07); paulo["root"].rotation_euler = (0, 0, math.radians(0))
        talk(rosa, f(0.4), f(3.0)); talk(julia, f(3.4), f(5.7))
        look(rosa, f(3.2), 0, math.radians(10)); look(julia, f(0.2), 0, math.radians(-8))
        key(paulo["armR"], "rotation_euler", f(1.0), (0, 0, 0)); key(paulo["armR"], "rotation_euler", f(2.0), (-1.2, 0, 0.2))
        key(paulo["armR"], "rotation_euler", f(4.0), (-1.2, 0, 0.2)); key(paulo["armR"], "rotation_euler", f(4.6), (0, 0, 0))
        aim_dof(cam, (-0.4, -0.3, 1.75), (2.2, 2.3, 1.45), 1, 2.8)
        aim_dof(cam, (-0.1, 0.0, 1.7), (2.2, 2.3, 1.45), N, 2.8)
        cam.data.lens = 24
    elif kind == "planta":      # 15–23 s: vista de cima, campo de visão só na entrada e no caixa
        rosa["root"].location = (3.3, 2.0, 0.07); rosa["root"].rotation_euler = (0, 0, math.radians(-90))
        julia["root"].location = (-2.6, 3.0, 0.07)
        paulo["root"].location = (-0.4, 5.0, 0.07)
        c1 = dual_cam((-3.6, 0.35, 3.0), rot=(math.radians(-35), 0, math.radians(-120)), s=1.2)
        c2 = dual_cam((3.8, 4.4, 3.0), rot=(math.radians(-35), 0, math.radians(150)), s=1.2)
        cone1, s1 = fov_cone((-3.5, 0.5, 2.9), (-0.6, 1.0, 0.1), spread=1.6, strength=0.0)
        cone2, s2 = fov_cone((3.6, 4.2, 2.9), (2.4, 1.8, 0.1), spread=1.5, strength=0.0)
        for sk, t0 in ((s1, 1.5), (s2, 3.0)):
            for t_, e in ((0, 0), (t0, 0), (t0 + 1.0, 0.22)):
                sk.default_value = e; sk.keyframe_insert("default_value", frame=int(f(t_)))
        # área privada destacada em vermelho translúcido (sem câmera)
        mp, sp = emat("privado", (230, 60, 60), 0.0)
        box(((PRIV[0] + PRIV[1]) / 2, (PRIV[2] + PRIV[3]) / 2, 0.08), (PRIV[1] - PRIV[0] - 0.1, PRIV[3] - PRIV[2] - 0.1, 0.02), mp, 0.0)
        for t_, e in ((0, 0), (5.0, 0), (5.8, 0.6)):
            sp.default_value = e; sp.keyframe_insert("default_value", frame=int(f(t_)))
        aim_dof(cam, (0.0, -0.8, 17.0), (0.0, 4.0, 0.0), 1, 16)
        aim_dof(cam, (1.2, 0.2, 16.0), (0.0, 4.2, 0.0), N, 16)
        cam.data.lens = 28
    elif kind == "rotina":      # 23–29 s: a câmera na parede e a equipe atendendo normalmente
        dual_cam((3.8, 4.4, 3.0), rot=(math.radians(-35), 0, math.radians(150)), s=1.2)
        rosa["root"].location = (3.4, 2.0, 0.07); rosa["root"].rotation_euler = (0, 0, math.radians(-90))
        paulo["root"].location = (1.6, 2.0, 0.07); paulo["root"].rotation_euler = (0, 0, math.radians(90))
        julia["root"].location = (-1.6, 6.6, 0.07); julia["root"].rotation_euler = (0, 0, math.radians(180))
        talk(rosa, f(0.6), f(2.4)); talk(paulo, f(3.0), f(4.2))
        key(julia["armR"], "rotation_euler", f(0.5), (0, 0, 0)); key(julia["armR"], "rotation_euler", f(1.4), (-1.9, 0, 0))
        key(julia["armR"], "rotation_euler", f(4.0), (-1.9, 0, 0)); key(julia["armR"], "rotation_euler", f(4.8), (0, 0, 0))
        aim_dof(cam, (3.2, 6.4, 3.1), (3.6, 4.5, 3.0), 1, 2.0)
        aim_dof(cam, (-0.2, -0.2, 2.1), (2.5, 2.2, 1.4), int(f(2.2)), 3.5)
        aim_dof(cam, (-0.5, -0.3, 2.0), (2.5, 2.2, 1.4), N, 3.5)
        cam.data.lens = 24
    elif kind == "atende":      # 41–47,5 s: Rosa entrega a sacola, o cliente sai satisfeito
        rosa["root"].location = (3.4, 2.0, 0.07); rosa["root"].rotation_euler = (0, 0, math.radians(-90))
        paulo["root"].location = (1.65, 2.0, 0.07); paulo["root"].rotation_euler = (0, 0, math.radians(90))
        julia["root"].location = (-0.6, 3.0, 0.07); julia["root"].rotation_euler = (0, 0, math.radians(180))
        sacola = empty((0, 0, 0)); sacola.parent = rosa["root"]; sacola.location = (0, -0.5, 1.05)
        box((0, 0, 0.12), (0.3, 0.14, 0.3), mat("sacola", (250, 250, 245)), 0.02, sacola)
        hold(rosa, f(0.2), False); hold(rosa, f(0.9), True)
        talk(rosa, f(0.6), f(2.2))
        key(sacola, "location", f(1.8), (0, -0.5, 1.05)); key(sacola, "location", f(2.4), (0, -1.3, 1.05))
        sacola.scale = (1, 1, 1); sacola.keyframe_insert("scale", frame=int(f(2.4)))
        sacola.scale = (0.001, 0.001, 0.001); sacola.keyframe_insert("scale", frame=int(f(2.5)))
        s2 = empty((0, 0, 0)); s2.parent = paulo["root"]; s2.location = (0.32, -0.2, 0.65)
        box((0, 0, 0.12), (0.3, 0.14, 0.3), mat("sacola", (250, 250, 245)), 0.02, s2)
        s2.scale = (0.001, 0.001, 0.001); s2.keyframe_insert("scale", frame=int(f(2.4)))
        s2.scale = (1, 1, 1); s2.keyframe_insert("scale", frame=int(f(2.5)))
        hold(rosa, f(2.6), False)
        talk(paulo, f(2.7), f(3.8))
        key(paulo["root"], "rotation_euler", f(3.8), (0, 0, math.radians(90)))
        key(paulo["root"], "rotation_euler", f(4.1), (0, 0, math.radians(180)))
        walk(paulo, f(4.1), f(5.0), (1.65, 2.0), (0.8, 0.6))
        aim_dof(cam, (0.0, -0.3, 1.7), (2.5, 2.0, 1.4), 1, 2.8)
        aim_dof(cam, (-0.3, -0.4, 1.7), (2.2, 1.9, 1.4), N, 2.8)
        cam.data.lens = 24
    return cam


L.CENARIOS["loja"] = lambda kind="chegada": loja(kind)
