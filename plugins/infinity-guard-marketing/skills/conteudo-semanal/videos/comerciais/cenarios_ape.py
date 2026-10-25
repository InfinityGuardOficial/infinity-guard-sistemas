"""Cenário "ape": sala de apartamento contemporâneo à noite + corredor do prédio, com a fechadura inteligente
modelada a partir das fotos do produto (variante preta): painel externo com anel do leitor, teclado de toque
0–9 * # e puxador redondo; lado interno com corpo retangular e girador. O cartão é preto.

Planta (metros): sala de x -4 a 4 e y 0 a 5; porta de entrada na parede do fundo (y=5), dobradiça em x=-0.5,
fechadura em x=0.38; corredor do prédio do outro lado (y>5).
"""
import math, random
import lib3d as L
from lib3d import bpy, Vector, mat, emat, box, cyl, sphere, ico, empty, setmat, M, camera
from cenarios import make_person, talk, hold, look, key, vida, aim_dof

NAVY_IG, GOLD_IG = (14, 26, 43), (201, 162, 77)
LX, LZ = 0.88, 1.05  # posição da fechadura na folha da porta (local)
LXW = -0.5 + LX      # mesma posição no mundo (a dobradiça fica em x=-0.5)


def texto3d(txt, loc, size, m, rot, parent=None):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.object; t.data.body = txt; t.data.size = size; t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
    t.data.materials.append(m)
    if parent: t.parent = parent
    return t


def fechadura(porta, apagado=True):
    """fechadura preta presa à folha da porta; devolve (força dos dígitos, lingueta)"""
    preto = mat("lock_preto", (16, 16, 18), rough=0.35)
    borda = mat("lock_borda", (34, 34, 38), rough=0.5)
    knob = mat("lock_knob", (30, 30, 34), rough=0.5)
    dig, dig_s = emat("lock_digitos", (235, 240, 255), 0.25)
    anel, _ = emat("lock_anel", (70, 170, 255), 3.0)
    ext = empty((LX, 0.03, LZ)); ext.parent = porta            # lado de fora (corredor, +Y)
    box((0, 0.012, 0), (0.074, 0.024, 0.178), borda, 0.008, ext)
    box((0, 0.025, 0), (0.066, 0.004, 0.17), preto, 0.004, ext)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.0115, minor_radius=0.0016, location=(0, 0.028, 0.062), rotation=(math.pi / 2, 0, 0))
    a = bpy.context.object; setmat(a, anel); a.parent = ext
    cyl((0, 0.027, 0.062), 0.0095, 0.002, mat("lock_sensor", (30, 32, 38), rough=0.4), rot=(math.pi / 2, 0, 0), verts=24, parent=ext)
    teclas = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
    for i, tk in enumerate(teclas):
        r, c = divmod(i, 3)
        texto3d(tk, ((1 - c) * 0.019, 0.0295, 0.032 - r * 0.02), 0.0105, dig, (math.pi / 2, 0, math.pi), parent=ext)
    cyl((0, 0.028, -0.062), 0.021, 0.012, knob, rot=(math.pi / 2, 0, 0), verts=40, parent=ext)
    cyl((0, 0.0345, -0.062), 0.017, 0.002, mat("lock_knob2", (48, 48, 54), rough=0.4), rot=(math.pi / 2, 0, 0), verts=40, parent=ext)
    inn = empty((LX, -0.03, LZ)); inn.parent = porta            # lado de dentro (sala, -Y)
    box((0, -0.017, -0.005), (0.078, 0.034, 0.17), preto, 0.006, inn)
    gir = empty((0, -0.036, -0.045)); gir.parent = inn
    cyl((0, 0, 0), 0.018, 0.008, preto, rot=(math.pi / 2, 0, 0), verts=24, parent=gir)
    box((0, -0.008, 0), (0.008, 0.012, 0.03), preto, 0.003, gir)
    texto3d("OPEN", (0, -0.0345, 0.02), 0.008, mat("lock_txt", (90, 90, 96)), (math.pi / 2, 0, 0), parent=inn)
    ling = box((1.005, 0, LZ), (0.03, 0.022, 0.022), mat("lingueta", (170, 172, 178), rough=0.4), 0.002, porta)
    return dig_s, ling, gir


def cartao(parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    c = empty(loc); c.rotation_euler = rot
    if parent: c.parent = parent
    ouro = mat("cartao_ouro", GOLD_IG, rough=0.4)
    box((0, 0, 0), (0.054, 0.0018, 0.0856), mat("cartao_preto", (22, 22, 26), rough=0.3), 0.001, c)
    for sy in (-1, 1):  # filete dourado nas duas faces, para o cartão aparecer contra a fechadura preta
        box((0, sy * 0.001, 0.039), (0.05, 0.0003, 0.002), ouro, 0.0, c); box((0, sy * 0.001, -0.039), (0.05, 0.0003, 0.002), ouro, 0.0, c)
        box((0.023, sy * 0.001, 0), (0.002, 0.0003, 0.078), ouro, 0.0, c); box((-0.023, sy * 0.001, 0), (0.002, 0.0003, 0.078), ouro, 0.0, c)
        box((0, sy * 0.0011, 0.012), (0.014, 0.0003, 0.01), ouro, 0.0, c)
    return c


def ape(kind):
    N, FPS = L.N, L.FPS
    f = lambda sec: 1 + sec * FPS
    random.seed(17)
    madeira = mat("piso_madeira", (150, 104, 70), rough=0.45)
    for i in range(16):
        box((0, 0.2 + i * 0.32, 0.01), (8.0, 0.31, 0.02), mat("tabua%d" % (i % 3), [(150, 104, 70), (140, 96, 64), (158, 112, 76)][i % 3], rough=0.45), 0.0)
    for i in range(10):
        box((0, 5.6 + i * 0.4, 0.01), (6, 0.39, 0.02), mat("piso_corr%d" % (i % 2), (200, 196, 188) if i % 2 else (188, 184, 176), rough=0.3), 0.0)
    bege = mat("parede_bege", (222, 206, 182)); navy = mat("parede_navy", NAVY_IG, rough=0.6)
    box((-4.1, 2.5, 1.5), (0.2, 5, 3.0), bege, 0.0); box((4.1, 2.5, 1.5), (0.2, 5, 3.0), bege, 0.0)
    # parede da porta em azul-marinho com o vão da porta (x -0.55..0.55, até 2.15 m)
    box((-2.3, 5.0, 1.5), (3.5, 0.15, 3.0), navy, 0.0); box((2.3, 5.0, 1.5), (3.5, 0.15, 3.0), navy, 0.0)
    box((0, 5.0, 2.6), (1.1, 0.15, 0.9), navy, 0.0)
    ouro = mat("friso_ouro", GOLD_IG, rough=0.3, metal=0.8)
    for x in (-0.58, 0.58): box((x, 4.92, 1.08), (0.04, 0.03, 2.16), ouro, 0.0)
    box((0, 4.92, 2.17), (1.2, 0.03, 0.04), ouro, 0.0)
    box((0, 2.5, 3.05), (8.4, 5.2, 0.1), mat("forro", (236, 230, 220)), 0.0)
    # corredor do prédio
    corr = mat("corredor", (214, 210, 202))
    box((-3.1, 7.5, 1.5), (0.15, 5, 3.0), corr, 0.0); box((3.1, 7.5, 1.5), (0.15, 5, 3.0), corr, 0.0)
    box((0, 9.6, 1.5), (6.2, 0.15, 3.0), corr, 0.0); box((0, 7.5, 3.05), (6.2, 5, 0.1), corr, 0.0)
    box((0, 7.5, 3.0), (0.6, 0.6, 0.02), mat("plafon", (255, 245, 225), emit=4), 0.0)
    bpy.ops.object.light_add(type="AREA", location=(0, 7.2, 2.9)); lc = bpy.context.object; lc.data.energy = 60; lc.data.size = 1.0
    lc.data.color = (1, 0.88, 0.72)
    texto3d("302", (0, 5.09, 1.95), 0.08, ouro, (math.pi / 2, 0, math.pi))
    # porta (folha de madeira escura) com dobradiça
    porta = empty((-0.5, 5.0, 0)); porta.name = "porta"
    folha = box((0.5, 0, 1.06), (1.0, 0.045, 2.1), mat("porta_nogueira", (92, 60, 40), rough=0.4), 0.004, porta)
    for z in (0.5, 1.6): box((0.5, -0.025, z), (0.8, 0.004, 0.006), mat("porta_veio", (80, 50, 34)), 0.0, porta)
    dig_s, ling, gir = fechadura(porta)
    # sala: sofá, tapete, mesa de centro com bolo, luminárias, janela com a cidade, quadros e plantas
    tecido = mat("sofa", (64, 78, 104), rough=0.8)
    box((-2.6, 1.0, 0.25), (2.6, 0.95, 0.42), tecido, 0.08); box((-2.6, 0.62, 0.7), (2.6, 0.22, 0.6), tecido, 0.08)
    for x in (-3.8, -1.4): box((x, 1.0, 0.45), (0.25, 0.95, 0.5), tecido, 0.06)
    for x in (-3.1, -2.2): box((x, 0.85, 0.72), (0.5, 0.15, 0.4), mat("almofada", GOLD_IG, rough=0.8), 0.07, rot=(0.25, 0, 0))
    cyl((-0.9, 2.3, 0.02), 1.5, 0.02, mat("tapete", (200, 186, 160), rough=0.9), verts=48)
    cyl((-0.9, 2.3, 0.4), 0.55, 0.05, mat("mesa_tampo", (230, 226, 218), rough=0.2), verts=48)
    cyl((-0.9, 2.3, 0.2), 0.08, 0.38, ouro, verts=16)
    cyl((-0.75, 2.2, 0.5), 0.14, 0.13, mat("bolo", (250, 240, 232)), verts=32)
    cyl((-0.75, 2.2, 0.572), 0.142, 0.015, mat("calda", (120, 60, 40)), verts=32)
    cyl((-0.75, 2.2, 0.62), 0.006, 0.08, mat("vela", (240, 200, 210)), verts=8)
    fl, fs = emat("chama", (255, 190, 90), 12)
    sphere((-0.75, 2.2, 0.675), 0.012, fl, seg=8, scale=(0.7, 0.7, 1.4))
    bpy.ops.object.light_add(type="POINT", location=(-0.75, 2.2, 0.72)); vl = bpy.context.object; vl.data.energy = 6; vl.data.color = (1, 0.7, 0.4)
    # janela com a cidade à noite
    box((4.0, 2.4, 1.6), (0.05, 2.6, 1.8), mat("vidro_noite", (20, 30, 60), rough=0.1), 0.0)
    cid, _ = emat("cidade", (255, 214, 140), 2.2)
    for i in range(70):
        box((4.3 + random.uniform(0, 6), random.uniform(0.8, 4.0), random.uniform(0.8, 2.5)), (0.02, 0.06, 0.05), cid, 0.0)
    for x, y in ((-3.6, 4.4), (3.6, 4.4)):
        cyl((x, y, 0.22), 0.22, 0.44, mat("vaso_preto", (30, 30, 34)), verts=20)
        for k in range(5):
            ico((x + random.uniform(-0.15, 0.15), y + random.uniform(-0.15, 0.15), 0.7 + k * 0.18), 0.22, M["leaf"] if k % 2 else M["leaf2"], 1)
    for x, w in ((-2.6, 0.9), (-1.4, 0.6)):
        box((x, 4.9, 1.75), (w, 0.03, 0.7), ouro, 0.0); box((x, 4.88, 1.75), (w - 0.08, 0.02, 0.62), mat("quadro%d" % int(w * 10), (230, 220, 200)), 0.0)
    for x in (-1.8, 1.4):  # pendentes quentes
        cyl((x, 2.3, 2.85), 0.005, 0.4, mat("fio_preto", (20, 20, 20)), verts=6)
        sphere((x, 2.3, 2.6), 0.12, mat("pendente", (255, 220, 160), emit=5), seg=16)
        bpy.ops.object.light_add(type="POINT", location=(x, 2.3, 2.45)); pl = bpy.context.object; pl.data.energy = 90; pl.data.color = (1, 0.78, 0.5)
        pl.data.shadow_soft_size = 0.2
    bpy.ops.object.light_add(type="AREA", location=(0, 1.5, 2.9)); ar = bpy.context.object; ar.data.energy = 40; ar.data.size = 3; ar.data.color = (1, 0.85, 0.7)
    w = bpy.data.worlds.new("noite"); bpy.context.scene.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.015, 0.03, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.3
    # o casal (personagens fictícios)
    ela = make_person((30, 30, -20), skin="morena", hair="castanho", style="longo", shirt=GOLD_IG, pants=(40, 40, 52))
    ele = make_person((30, 30, -20), skin="parda", hair="preto", style="curto", shirt=(236, 236, 240), pants=(50, 56, 70), height=1.05)
    for i, p in enumerate((ela, ele)): vida(p, N, i + 3)
    cam = camera((0, 0, 0), (0, 0, 0), 35)
    lens = lambda mm: setattr(cam.data, "lens", mm)

    def presente(parent, loc):
        g = empty(loc); g.parent = parent
        box((0, 0, 0.04), (0.16, 0.12, 0.08), mat("caixa_navy", NAVY_IG, rough=0.5), 0.006, g)
        tampa = empty((0, 0.06, 0.085)); tampa.parent = g
        box((0, -0.06, 0.006), (0.168, 0.128, 0.014), mat("caixa_navy", NAVY_IG, rough=0.5), 0.004, tampa)
        box((0, -0.06, 0.016), (0.03, 0.13, 0.004), ouro, 0.0, tampa)
        box((0, -0.06, 0.016), (0.17, 0.03, 0.004), ouro, 0.0, tampa)
        return g, tampa

    if kind == "entrega":        # 0–5 s: ela entrega a caixinha; ele abre e tira o cartão preto
        ela["root"].location = (-0.2, 1.8, 0.02); ela["root"].rotation_euler = (0, 0, math.radians(-90))
        ele["root"].location = (-1.2, 1.8, 0.02); ele["root"].rotation_euler = (0, 0, math.radians(90))
        g, tampa = presente(ela["root"], (0, -0.42, 1.0))
        hold(ela, 1, True)
        key(g, "location", f(0.6), (0, -0.42, 1.0)); key(g, "location", f(1.4), (0, -0.62, 1.0))
        g.scale = (1, 1, 1); g.keyframe_insert("scale", frame=int(f(1.4)))
        g.scale = (0.001, 0.001, 0.001); g.keyframe_insert("scale", frame=int(f(1.5)))
        g2, tampa2 = presente(ele["root"], (0, -0.4, 1.0))
        g2.scale = (0.001, 0.001, 0.001); g2.keyframe_insert("scale", frame=int(f(1.4)))
        g2.scale = (1, 1, 1); g2.keyframe_insert("scale", frame=int(f(1.5)))
        hold(ele, f(1.2), True); hold(ela, f(1.8), False)
        key(tampa2, "rotation_euler", f(2.2), (0, 0, 0)); key(tampa2, "rotation_euler", f(2.8), (math.radians(-110), 0, 0))
        c = cartao(ele["root"], (0, -0.4, 1.06), (0, 0, 0))
        c.scale = (0.001, 0.001, 0.001); c.keyframe_insert("scale", frame=int(f(2.8)))
        c.scale = (1, 1, 1); c.keyframe_insert("scale", frame=int(f(2.9)))
        key(c, "location", f(3.0), (0, -0.4, 1.06)); key(c, "location", f(4.0), (0.05, -0.36, 1.32))
        look(ele, f(2.0), 0.4, 0); look(ela, f(2.0), 0.15, 0)
        aim_dof(cam, (-0.7, -1.3, 1.45), (-0.7, 1.8, 1.25), 1, 2.4)
        aim_dof(cam, (-0.7, -0.8, 1.42), (-0.75, 1.8, 1.25), N, 2.4)
    elif kind == "examina":      # 5–11 s: close nele examinando o cartão, intrigado
        ele["root"].location = (-1.2, 1.8, 0.02); ele["root"].rotation_euler = (0, 0, math.radians(60))
        ela["root"].location = (-0.2, 1.8, 0.02); ela["root"].rotation_euler = (0, 0, math.radians(-100))
        hold(ele, 1, True); key(ele["armR"], "rotation_euler", 1, (-1.5, 0, -0.2))
        c = cartao(ele["root"], (0.08, -0.36, 1.36), (0.2, 0, 0))
        key(c, "rotation_euler", f(1.0), (0.2, 0, 0)); key(c, "rotation_euler", f(2.4), (0.2, 0, math.radians(180)))
        key(c, "rotation_euler", f(3.8), (0.2, 0, math.radians(360)))
        look(ele, 1, 0.35, 0); look(ele, f(3.0), 0.35, math.radians(12)); look(ele, f(4.6), 0.2, math.radians(-10))
        key(ele["head"], "rotation_euler", f(5.2), (0.2, 0.18, math.radians(-10)))
        aim_dof(cam, (-0.2, 0.75, 1.62), (-1.15, 1.75, 1.5), 1, 1.8)
        aim_dof(cam, (-0.35, 0.85, 1.6), (-1.15, 1.75, 1.52), N, 1.8)
    elif kind == "aponta":       # 11–18 s: ela aponta para a porta; a câmera vai até a fechadura nova
        ele["root"].location = (-1.2, 1.8, 0.02); ele["root"].rotation_euler = (0, 0, math.radians(60))
        ela["root"].location = (-0.2, 1.8, 0.02); ela["root"].rotation_euler = (0, 0, math.radians(-100))
        hold(ele, 1, True); c = cartao(ele["root"], (0.08, -0.36, 1.36), (0.2, 0, 0))
        key(ela["root"], "rotation_euler", f(0.3), (0, 0, math.radians(-100))); key(ela["root"], "rotation_euler", f(1.0), (0, 0, math.radians(170)))
        key(ela["armR"], "rotation_euler", f(0.8), (0, 0, 0)); key(ela["armR"], "rotation_euler", f(1.4), (-1.6, 0, -0.3))
        key(ela["armR"], "rotation_euler", f(5.0), (-1.6, 0, -0.3)); key(ela["armR"], "rotation_euler", f(5.6), (0, 0, 0))
        key(ele["root"], "rotation_euler", f(1.6), (0, 0, math.radians(60))); key(ele["root"], "rotation_euler", f(2.4), (0, 0, math.radians(170)))
        aim_dof(cam, (-0.6, -1.0, 1.5), (-0.7, 1.8, 1.4), 1, 2.8)
        aim_dof(cam, (-0.2, 0.6, 1.4), (0.2, 5.0, 1.15), int(f(3.2)), 2.8)
        aim_dof(cam, (0.25, 4.2, 1.1), (LXW, 4.97, 1.0), N, 2.0)
    elif kind == "revela":       # 18–27 s: revelação da fechadura (lado de fora), teclado acendendo
        for t_, e in ((0, 0.25), (2.0, 0.25), (3.0, 4.0)):
            dig_s.default_value = e; dig_s.keyframe_insert("default_value", frame=int(f(t_)))
        aim_dof(cam, (0.75, 5.45, 1.18), (LXW, 5.03, LZ), 1, 1.4)
        aim_dof(cam, (0.38, 5.4, 1.08), (LXW, 5.03, LZ), int(f(4.5)), 1.4)
        aim_dof(cam, (0.05, 5.5, 1.0), (LXW, 5.03, LZ), N, 1.4)
        lens(60)
    elif kind == "cartao":       # 27–37 s: simulação ilustrativa: o cartão aproxima, bipe, a lingueta recolhe e a porta abre
        ele["root"].location = (0.15, 5.75, 0.02); ele["root"].rotation_euler = (0, 0, math.radians(180))
        key(ele["armR"], "rotation_euler", f(0.5), (0, 0, 0)); key(ele["armR"], "rotation_euler", f(1.8), (-1.35, 0, 0.35))
        c = cartao(None, (0, 0, 0), (0, 0, 0))
        key(c, "location", 1, (LXW + 0.25, 5.45, 0.95)); key(c, "location", f(1.8), (LXW + 0.02, 5.08, 1.06))
        key(c, "location", f(3.4), (LXW + 0.02, 5.08, 1.06)); key(c, "location", f(4.2), (LXW + 0.25, 5.4, 0.98))
        for t_, e in ((0, 0.25), (1.9, 0.25), (2.1, 4.5), (4.0, 4.5), (4.6, 0.8)):
            dig_s.default_value = e; dig_s.keyframe_insert("default_value", frame=int(f(t_)))
        key(ling, "location", f(2.3), (1.005, 0, LZ)); key(ling, "location", f(2.8), (0.97, 0, LZ))
        key(gir, "rotation_euler", f(2.3), (0, 0, 0)); key(gir, "rotation_euler", f(2.8), (0, math.radians(90), 0))
        key(porta, "rotation_euler", f(4.6), (0, 0, 0)); key(porta, "rotation_euler", f(6.4), (0, 0, math.radians(35)))
        aim_dof(cam, (0.62, 5.42, 1.13), (LXW, 5.03, LZ), 1, 2.0)
        aim_dof(cam, (0.7, 5.55, 1.18), (LXW, 5.03, LZ), int(f(4.2)), 2.0)
        aim_dof(cam, (1.05, 6.0, 1.4), (0.2, 4.8, 1.15), N, 3.0)
        lens(45)
    elif kind == "sorriso":      # 37–41 s: o casal sorri junto à porta aberta
        key(porta, "rotation_euler", 1, (0, 0, math.radians(35)))
        ela["root"].location = (-0.15, 4.2, 0.02); ela["root"].rotation_euler = (0, 0, math.radians(15))
        ele["root"].location = (0.45, 4.25, 0.02); ele["root"].rotation_euler = (0, 0, math.radians(-15))
        key(ela["armR"], "rotation_euler", 1, (-0.5, 0, -0.6)); key(ele["armL"], "rotation_euler", 1, (-0.5, 0, 0.6))
        look(ela, 1, 0, math.radians(-25)); look(ela, f(1.5), 0.05, math.radians(-30))
        look(ele, 1, 0, math.radians(25)); look(ele, f(1.2), 0.05, math.radians(30))
        for p in (ela, ele):  # sorriso: boca mais larga
            p["mouth"].scale = (1.9, 0.3, 0.45); p["mouth"].keyframe_insert("scale", frame=1)
        aim_dof(cam, (0.2, 1.6, 1.55), (0.15, 4.2, 1.5), 1, 2.4)
        aim_dof(cam, (0.15, 2.0, 1.55), (0.15, 4.2, 1.52), N, 2.4)
    elif kind == "close":        # 41–45 s: close no cartão diante da fechadura
        c = cartao(None, (LXW + 0.07, 5.1, 0.99), (0, math.radians(18), math.radians(-14)))
        dig_s.default_value = 2.0
        aim_dof(cam, (LXW + 0.22, 5.42, 1.12), (LXW + 0.02, 5.07, 1.07), 1, 1.2)
        aim_dof(cam, (LXW + 0.12, 5.34, 1.1), (LXW + 0.02, 5.07, 1.07), N, 1.2)
        lens(70)
    return cam


L.CENARIOS["ape"] = lambda kind="entrega": ape(kind)
