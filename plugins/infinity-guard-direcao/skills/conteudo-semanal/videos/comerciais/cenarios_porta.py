"""Cenário "porta": o primeiro apartamento (vazio, com caixas de mudança) + corredor do prédio, com a fechadura
de alavanca modelada a partir da foto do produto (painel externo alto e preto com teclado de toque, faixa azul e
alavanca com anel do leitor; painel interno com tela e botões). Sem a marca do fornecedor.
E o cenário "lembranca": quarto com escrivaninha para as lembranças (estudo, trabalho e planos).

Planta (metros): sala de x -4 a 4 e y 0 a 5; porta na parede do fundo (y=5), dobradiça em x=-0.5, a folha abre
para dentro da sala; corredor do prédio em y>5. A lembrança fica em x=20.
"""
import math, random
import lib3d as L
from lib3d import bpy, mat, emat, box, cyl, sphere, ico, empty, setmat, M, camera
from cenarios import make_person, hold, look, key, vida, walk, aim_dof
from cenarios_ape import texto3d

NAVY_IG, GOLD_IG = (14, 26, 43), (201, 162, 77)
LX = 0.86            # fechadura na folha (local); no mundo x = -0.5 + LX
LXW = -0.5 + LX
ZA = 1.0             # altura do eixo da alavanca
TECLAS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", ""]


def pos_tecla(i):
    """posição (local do painel externo) da tecla i, já espelhada para ler certo de fora"""
    r, c = divmod(i, 3)
    return ((1 - c) * 0.019, 0.0262, 1.198 - r * 0.024)


def fechadura_alavanca(porta):
    """painéis da fechadura presos à folha; devolve dict com as partes animáveis"""
    preto = mat("lk_preto", (14, 14, 16), rough=0.3)
    lado = mat("lk_lado", (30, 30, 34), rough=0.5)
    dig, dig_s = emat("lk_digitos", (235, 242, 255), 0.3)
    azul, azul_s = emat("lk_azul", (40, 150, 255), 2.5)
    anel, anel_s = emat("lk_anel", (40, 150, 255), 0.6)  # leitor da alavanca: aparece, mas não é usado
    ext = empty((LX, 0.0225, 0)); ext.parent = porta
    box((0, 0.012, 1.08), (0.074, 0.024, 0.44), lado, 0.012, ext)
    box((0, 0.0245, 1.08), (0.066, 0.002, 0.43), preto, 0.0, ext)
    for dx in (-0.012, 0.012): sphere((dx, 0.026, 1.268), 0.003, mat("lk_ir", (60, 60, 66)), ext, 8)
    cyl((0, 0.026, 1.268), 0.0065, 0.003, mat("lk_lente", (40, 70, 60), rough=0.1), rot=(math.pi / 2, 0, 0), verts=16, parent=ext)
    box((0, 0.0262, 1.232), (0.03, 0.001, 0.003), azul, 0.0, ext)
    for i, tk in enumerate(TECLAS):
        x, y, z = pos_tecla(i)
        if tk: texto3d(tk, (x, y, z), 0.011, dig, (math.pi / 2, 0, math.pi), parent=ext)
        else:  # campainha
            bpy.ops.mesh.primitive_torus_add(major_radius=0.005, minor_radius=0.0009, location=(x, y, z), rotation=(math.pi / 2, 0, 0))
            t = bpy.context.object; setmat(t, dig); t.parent = ext
    toque, toque_s = emat("lk_toque", (120, 220, 255), 0.0)
    brilho = sphere((0, 0.027, 1.2), 0.0085, toque, ext, 12, scale=(1, 0.2, 1))
    cyl((0, 0.032, ZA), 0.026, 0.02, lado, rot=(math.pi / 2, 0, 0), verts=32, parent=ext)
    alav_e = empty((0, 0.042, ZA)); alav_e.parent = ext
    cyl((0, 0.008, 0), 0.02, 0.026, preto, rot=(math.pi / 2, 0, 0), verts=32, parent=alav_e)
    box((-0.075, 0.012, 0), (0.135, 0.02, 0.03), preto, 0.008, alav_e)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.012, minor_radius=0.0022, location=(0, 0.0215, 0), rotation=(math.pi / 2, 0, 0))
    a = bpy.context.object; setmat(a, anel); a.parent = alav_e
    cyl((0, 0.021, 0), 0.0095, 0.002, mat("lk_sensor", (24, 30, 44), rough=0.2), rot=(math.pi / 2, 0, 0), verts=24, parent=alav_e)
    inn = empty((LX, -0.0225, 0)); inn.parent = porta
    box((0, -0.012, 1.08), (0.074, 0.024, 0.46), lado, 0.012, inn)
    box((0, -0.0245, 1.08), (0.066, 0.002, 0.45), preto, 0.0, inn)
    tela, _ = emat("lk_tela", (60, 80, 110), 0.6)
    box((0, -0.026, 1.215), (0.05, 0.001, 0.07), tela, 0.0, inn)
    for dx in (-0.016, 0, 0.016): sphere((dx, -0.026, 1.165), 0.004, lado, inn, 8)
    box((0, -0.027, 0.9), (0.008, 0.004, 0.022), lado, 0.002, inn)
    alav_i = empty((0, -0.042, ZA)); alav_i.parent = inn
    cyl((0, -0.008, 0), 0.02, 0.026, preto, rot=(math.pi / 2, 0, 0), verts=32, parent=alav_i)
    box((-0.075, -0.012, 0), (0.135, 0.02, 0.03), preto, 0.008, alav_i)
    ling = box((1.005, 0, ZA + 0.03), (0.03, 0.022, 0.03), mat("lk_lingueta", (170, 172, 178), rough=0.4), 0.002, porta)
    return {"ext": ext, "inn": inn, "dig": dig_s, "azul": azul_s, "toque": toque_s, "brilho": brilho,
            "alav_e": alav_e, "alav_i": alav_i, "ling": ling}


def macaneta_antiga(porta):
    """maçaneta simples que estava na porta (sai na troca)"""
    g = empty((LX, 0, 0)); g.parent = porta
    inox = mat("inox_velho", (150, 150, 150), rough=0.35, metal=0.6)
    for sy in (-1, 1):
        cyl((0, sy * 0.03, ZA), 0.028, 0.012, inox, rot=(math.pi / 2, 0, 0), verts=24, parent=g)
        box((-0.06, sy * 0.05, ZA), (0.12, 0.018, 0.02), inox, 0.006, g)
        box((0, sy * 0.025, ZA - 0.11), (0.03, 0.01, 0.06), inox, 0.004, g)
    return g


def caixa_mudanca(loc, s=(0.5, 0.4, 0.4), rot=0.0, fita=True):
    papelao = mat("papelao_mud", (196, 150, 98))
    b = box(loc, s, papelao, 0.01, rot=(0, 0, rot))
    if fita: box((loc[0], loc[1], loc[2] + s[2] / 2), (0.06, s[1] + 0.005, 0.004), mat("fita", (210, 190, 150)), 0.0, rot=(0, 0, rot))
    return b


def mao(cor="parda"):
    """antebraço e mão para os closes do teclado (indicador esticado)"""
    from cenarios import SKIN
    pele = mat("skin_" + cor, SKIN[cor])
    r = empty((0, 0, 0))
    cyl((0, 0.16, 0), 0.03, 0.24, mat("manga_terracota", (186, 92, 70)), rot=(math.pi / 2, 0, 0), verts=16, parent=r)
    sphere((0, 0.02, 0), 0.034, pele, r, 14, scale=(1.0, 1.25, 0.6))
    cyl((0, -0.04, 0.004), 0.008, 0.05, pele, rot=(math.pi / 2, 0, 0), verts=10, parent=r)
    sphere((0, -0.065, 0.004), 0.0085, pele, r, 10)
    for dx in (-0.022, 0.012, 0.024):  # dedos dobrados
        sphere((dx, -0.014, -0.012), 0.011, pele, r, 8)
    return r


def chaves(parent=None, loc=(0, 0, 0)):
    g = empty(loc)
    if parent: g.parent = parent
    ouro = mat("chave_ouro", GOLD_IG, rough=0.4)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.011, minor_radius=0.0018, location=(0, 0, 0), rotation=(math.pi / 2, 0, 0))
    a = bpy.context.object; setmat(a, ouro); a.parent = g
    for dx, rz in ((-0.008, 0.3), (0.01, -0.25)):
        k = empty((dx, 0, -0.02)); k.parent = g; k.rotation_euler = (0, rz, 0)
        box((0, 0, -0.012), (0.018, 0.003, 0.02), mat("chave_inox", (150, 152, 158), rough=0.4), 0.002, k)
        box((0, 0, -0.045), (0.007, 0.002, 0.05), mat("chave_inox", (150, 152, 158), rough=0.4), 0.0, k)
    tag = empty((0.0, 0, -0.04)); tag.parent = g
    box((0, 0, -0.03), (0.05, 0.003, 0.07), mat("tag_navy", NAVY_IG), 0.006, tag)
    texto3d("302", (0, 0.0025, -0.03), 0.022, mat("tag_ouro", GOLD_IG, emit=0.8), (math.pi / 2, 0, math.pi), parent=tag)
    return g


def porta(kind):
    N, FPS = L.N, L.FPS
    f = lambda sec: 1 + sec * FPS
    random.seed(20)
    for i in range(16):
        box((0, 0.2 + i * 0.32, 0.01), (8.0, 0.31, 0.02), mat("tabua_clara%d" % (i % 3), [(186, 146, 104), (176, 138, 98), (194, 154, 110)][i % 3], rough=0.45), 0.0)
    for i in range(10):
        box((0, 5.6 + i * 0.4, 0.01), (6, 0.39, 0.02), mat("piso_corr%d" % (i % 2), (200, 196, 188) if i % 2 else (188, 184, 176), rough=0.3), 0.0)
    branco = mat("parede_nova", (238, 232, 222))
    box((-4.1, 2.5, 1.5), (0.2, 5, 3.0), branco, 0.0); box((4.1, 2.5, 1.5), (0.2, 5, 3.0), branco, 0.0)
    box((0, -0.3, 1.5), (8.4, 0.2, 3.0), branco, 0.0)
    navy = mat("parede_navy", NAVY_IG, rough=0.6)
    box((-2.3, 5.0, 1.5), (3.5, 0.15, 3.0), navy, 0.0); box((2.3, 5.0, 1.5), (3.5, 0.15, 3.0), navy, 0.0)
    box((0, 5.0, 2.6), (1.1, 0.15, 0.9), navy, 0.0)
    ouro = mat("friso_ouro", GOLD_IG, rough=0.3, metal=0.8)
    for x in (-0.58, 0.58):
        box((x, 4.92, 1.08), (0.04, 0.03, 2.16), ouro, 0.0); box((x, 5.08, 1.08), (0.04, 0.03, 2.16), mat("batente", (230, 226, 218)), 0.0)
    box((0, 4.92, 2.17), (1.2, 0.03, 0.04), ouro, 0.0)
    box((0, 2.5, 3.05), (8.4, 5.6, 0.1), mat("forro", (240, 236, 228)), 0.0)
    corr = mat("corredor", (214, 210, 202))
    box((-3.1, 7.5, 1.5), (0.15, 5, 3.0), corr, 0.0); box((3.1, 7.5, 1.5), (0.15, 5, 3.0), corr, 0.0)
    box((0, 9.6, 1.5), (6.2, 0.15, 3.0), corr, 0.0); box((0, 7.5, 3.05), (6.2, 5, 0.1), corr, 0.0)
    for y in (6.2, 8.4):
        box((0, y, 3.0), (0.5, 0.5, 0.02), mat("plafon", (255, 245, 225), emit=4), 0.0)
        bpy.ops.object.light_add(type="AREA", location=(0, y, 2.9)); lc = bpy.context.object; lc.data.energy = 45; lc.data.size = 0.9
        lc.data.color = (1, 0.88, 0.72)
    texto3d("302", (0, 5.09, 1.95), 0.08, ouro, (math.pi / 2, 0, math.pi))
    box((2.0, 5.09, 1.2), (0.5, 0.02, 0.7), mat("quadro_aviso", (200, 190, 170)), 0.0)  # quadro de avisos do andar
    pt = empty((-0.5, 5.0, 0)); pt.name = "porta"
    box((0.5, 0, 1.06), (1.0, 0.045, 2.1), mat("porta_nogueira", (92, 60, 40), rough=0.4), 0.004, pt)
    for z in (0.5, 1.6):
        for sy in (-1, 1): box((0.5, sy * 0.025, z), (0.8, 0.004, 0.006), mat("porta_veio", (80, 50, 34)), 0.0, pt)
    lk = fechadura_alavanca(pt)
    velha = macaneta_antiga(pt)
    instalada = kind not in ("corredor", "chaves", "medir", "instala")
    if not instalada:
        for o in (lk["ext"], lk["inn"]): o.scale = (0.001, 0.001, 0.001)
    else:
        velha.scale = (0.001, 0.001, 0.001)
    # sala nova: caixas de mudança, planta, luminária, janela com o fim de tarde
    for loc, s, r in (((-2.8, 3.6, 0.2), (0.6, 0.45, 0.4), 0.2), ((-2.7, 3.6, 0.58), (0.5, 0.4, 0.36), -0.1),
                      ((-3.3, 2.6, 0.18), (0.5, 0.5, 0.36), 0.5), ((2.6, 3.9, 0.22), (0.7, 0.5, 0.44), -0.3),
                      ((2.9, 3.0, 0.16), (0.45, 0.35, 0.32), 0.1), ((-1.6, 1.2, 0.17), (0.5, 0.4, 0.34), 0.7)):
        caixa_mudanca(loc, s, r)
    cyl((3.4, 4.4, 0.22), 0.22, 0.44, mat("vaso_terracota", (170, 90, 60)), verts=20)
    for k in range(5):
        ico((3.4 + random.uniform(-0.15, 0.15), 4.4 + random.uniform(-0.15, 0.15), 0.7 + k * 0.18), 0.22, M["leaf"] if k % 2 else M["leaf2"], 1)
    box((4.0, 2.4, 1.6), (0.05, 2.6, 1.8), mat("ceu_tarde", (255, 196, 140), emit=2.2), 0.0)
    for z in (0.7, 2.5): box((3.98, 2.4, z), (0.06, 2.7, 0.08), mat("caixilho", (240, 240, 240)), 0.0)
    bpy.ops.object.light_add(type="AREA", location=(3.6, 2.4, 1.8), rotation=(0, math.radians(-90), 0))
    jl = bpy.context.object; jl.data.energy = 260; jl.data.size = 2.2; jl.data.color = (1, 0.78, 0.55)
    bpy.ops.object.light_add(type="AREA", location=(0, 2.0, 2.9)); ar = bpy.context.object; ar.data.energy = 70; ar.data.size = 3
    ar.data.color = (1, 0.9, 0.8)
    w = bpy.data.worlds.new("tarde"); bpy.context.scene.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.04, 0.04, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.4
    # personagens fictícios
    ela = make_person((30, 30, -20), skin="parda", hair="castanho", style="longo", shirt=(186, 92, 70), pants=(44, 52, 76))
    tec = make_person((30, 30, -20), skin="morena", hair="preto", style="curto", shirt=(120, 128, 138), pants=(60, 64, 72), height=1.04, bone=(120, 128, 138))
    vida(ela, N, 5); vida(tec, N, 6)
    cam = camera((0, 0, 0), (0, 0, 0), 35)
    lens = lambda mm: setattr(cam.data, "lens", mm)
    sorri = lambda p, fr: (setattr(p["mouth"], "scale", (1.9, 0.3, 0.45)), p["mouth"].keyframe_insert("scale", frame=int(fr)))
    abre = lambda f0, f1, ang=-75: (key(pt, "rotation_euler", f0, (0, 0, 0)), key(pt, "rotation_euler", f1, (0, 0, math.radians(ang))))

    def pisca(sock, t0, alto, base=0.3, dur=0.5):
        for t_, e in ((t0 - 0.05, base), (t0, alto), (t0 + dur, alto), (t0 + dur + 0.3, base)):
            sock.default_value = e; sock.keyframe_insert("default_value", frame=max(1, int(f(t_))))

    def destrava(t0):
        key(lk["ling"], "location", f(t0), (1.005, 0, ZA + 0.03)); key(lk["ling"], "location", f(t0 + 0.4), (0.975, 0, ZA + 0.03))

    def aperta(t0, i):
        """dedo na tecla i: o brilho aparece sobre ela"""
        x, y, z = pos_tecla(i)
        key(lk["brilho"], "location", f(t0) - 1, (x, 0.027, z))
        for t_, e in ((t0 - 0.05, 0.0), (t0, 6.0), (t0 + 0.25, 0.0)):
            lk["toque"].default_value = e; lk["toque"].keyframe_insert("default_value", frame=max(1, int(f(t_))))

    if kind == "corredor":       # 0–5 s: ela chega pelo corredor e para diante da porta 302
        ela["root"].location = (0.9, 8.6, 0.02); ela["root"].rotation_euler = (0, 0, math.radians(-12))
        walk(ela, 1, f(3.0), (0.9, 8.6), (0.35, 6.0))
        key(ela["root"], "rotation_euler", f(2.6), (0, 0, math.radians(-12))); key(ela["root"], "rotation_euler", f(3.4), (0, 0, 0))
        look(ela, f(3.2), -0.12, 0); look(ela, f(4.5), -0.05, 0)
        aim_dof(cam, (-1.4, 8.9, 1.25), (0.2, 5.2, 1.4), 1, 2.8)
        aim_dof(cam, (-1.1, 7.6, 1.35), (0.3, 5.6, 1.5), N, 2.8)
    elif kind == "chaves":       # 16–18 s: as chaves com a etiqueta 302 diante da porta
        ch = chaves(None, (0.25, 5.7, 1.45))
        key(ch, "rotation_euler", 1, (0, 0, -0.35)); key(ch, "rotation_euler", f(1.0), (0, 0, 0.25)); key(ch, "rotation_euler", N, (0, 0, -0.1))
        aim_dof(cam, (0.32, 6.05, 1.47), (0.25, 5.7, 1.42), 1, 1.2)
        aim_dof(cam, (0.3, 5.98, 1.46), (0.25, 5.7, 1.42), N, 1.2)
        lens(60)
    elif kind == "medir":        # 18–24 s: na sala vazia, ela mede a porta antes de escolher a fechadura
        abre(1, 2, -35)
        ela["root"].location = (0.75, 4.0, 0.02); ela["root"].rotation_euler = (0, 0, math.radians(225))
        trena = box((0, 0, -0.62), (0.07, 0.07, 0.07), mat("trena", (240, 200, 40)), 0.01, ela["armR"])
        key(ela["armR"], "rotation_euler", 1, (-0.9, 0, 0.3)); key(ela["armR"], "rotation_euler", f(2.0), (-1.2, 0, 0.45))
        key(ela["armR"], "rotation_euler", f(4.0), (-1.2, 0, 0.45)); key(ela["armR"], "rotation_euler", f(4.8), (-0.6, 0, 0.2))
        look(ela, 1, 0.25, 0.2); look(ela, f(4.6), 0.1, -0.3)
        sorri(ela, f(4.8))
        aim_dof(cam, (-1.25, 3.0, 1.45), (0.4, 4.35, 1.15), 1, 2.6)
        aim_dof(cam, (-1.0, 3.25, 1.42), (0.4, 4.35, 1.15), N, 2.6)
    elif kind == "instala":      # 24–30 s: a fechadura nova entra no lugar da maçaneta antiga
        tec["root"].location = (0.72, 5.5, 0.02); tec["root"].rotation_euler = (0, 0, math.radians(-39))
        key(tec["armL"], "rotation_euler", 1, (-1.3, 0, 0.1))
        for i, t_ in enumerate((0, 0.4, 0.8, 1.2, 1.6, 2.0)):  # parafusadeira indo e vindo
            key(tec["armR"], "rotation_euler", f(t_), (-1.25 - 0.08 * (i % 2), 0, -0.25))
        box((0, 0, -0.6), (0.04, 0.12, 0.05), mat("parafusadeira", (230, 150, 30)), 0.01, tec["armR"])
        look(tec, 1, 0.45, 0)
        key(velha, "scale", f(1.8), (1, 1, 1)); key(velha, "scale", f(2.0), (0.001, 0.001, 0.001))
        for o in (lk["ext"], lk["inn"]):
            key(o, "scale", f(2.0), (0.001, 0.001, 0.001)); key(o, "scale", f(2.1), (1, 1, 0.6)); key(o, "scale", f(2.6), (1, 1, 1))
        pisca(lk["dig"], 3.2, 3.5, dur=1.2)
        key(tec["root"], "location", f(3.6), (0.72, 5.5, 0.02)); key(tec["root"], "location", f(4.6), (1.5, 6.2, 0.02))
        key(tec["root"], "rotation_euler", f(3.6), (0, 0, math.radians(-39))); key(tec["root"], "rotation_euler", f(4.4), (0, 0, math.radians(-60)))
        key(tec["armR"], "rotation_euler", f(3.8), (0, 0, 0)); key(tec["armL"], "rotation_euler", f(3.8), (0, 0, 0))
        aim_dof(cam, (-1.0, 7.0, 1.6), (0.55, 5.3, 1.25), 1, 2.6)
        aim_dof(cam, (-0.8, 6.75, 1.55), (0.5, 5.25, 1.2), N, 2.6)
    elif kind == "demo":         # 30–38 s: simulação: cartão no teclado; depois a senha
        from mathutils import Euler, Vector
        h = mao("parda"); h.rotation_euler = (-0.5, 0, math.radians(35))
        R = Euler(h.rotation_euler).to_matrix(); ponta = R @ Vector((0, -0.0735, 0.004))
        dedo = lambda x, y, z: tuple(Vector((x, y, z)) - ponta)  # mão posicionada pela ponta do indicador
        key(h, "location", 1, dedo(LXW + 0.2, 5.35, 0.98))
        from cenarios_ape import cartao
        c = cartao(None, (0, 0, 0), (0, 0, 0))
        _, _, z5 = pos_tecla(4)
        key(c, "location", 1, (LXW + 0.22, 5.32, 1.05)); key(c, "location", f(1.0), (LXW, 5.075, z5 - 0.005))
        key(c, "location", f(2.4), (LXW, 5.075, z5 - 0.005)); key(c, "location", f(3.0), (LXW + 0.3, 5.4, 1.0))
        pisca(lk["dig"], 1.05, 4.0, dur=0.9); pisca(lk["azul"], 1.05, 9.0, base=2.5, dur=0.9); destrava(1.3)
        key(lk["ling"], "location", f(3.0), (0.975, 0, ZA + 0.03)); key(lk["ling"], "location", f(3.4), (1.005, 0, ZA + 0.03))
        seq = [6, 1, 8, 3, 5, 0]  # 7 2 9 4 6 1 (só ilustração)
        key(h, "location", f(3.6), dedo(LXW + 0.15, 5.3, 1.1))
        for k_, i in enumerate(seq):
            x, y, z = pos_tecla(i); t_ = 4.2 + k_ * 0.42
            key(h, "location", f(t_) - 2, dedo(LXW + x, 5.09, z)); key(h, "location", f(t_), dedo(LXW + x, 5.052, z))
            aperta(t_, i)
        key(h, "location", f(7.2), dedo(LXW + 0.2, 5.35, 0.98))
        pisca(lk["dig"], 6.8, 4.0, dur=0.8); pisca(lk["azul"], 6.8, 9.0, base=2.5, dur=0.8); destrava(6.9)
        aim_dof(cam, (LXW + 0.16, 5.5, 1.16), (LXW, 5.04, 1.14), 1, 1.6)
        aim_dof(cam, (LXW + 0.06, 5.42, 1.16), (LXW, 5.04, 1.15), int(f(3.4)), 1.6)
        aim_dof(cam, (LXW - 0.04, 5.4, 1.17), (LXW, 5.04, 1.15), N, 1.6)
        lens(55)
    elif kind == "senha":        # 38–44 s: ela digita a senha, abaixa a alavanca e a porta abre
        ela["root"].location = (0.1, 5.6, 0.02); ela["root"].rotation_euler = (0, 0, math.radians(-12))
        key(ela["armR"], "rotation_euler", 1, (0, 0, 0)); key(ela["armR"], "rotation_euler", f(0.8), (-1.45, 0, 0.25))
        for k_, i in enumerate((6, 1, 8, 3, 5, 0)):
            t_ = 1.0 + k_ * 0.4
            key(ela["armR"], "rotation_euler", f(t_), (-1.45 - 0.05 * (k_ % 2), 0, 0.25)); aperta(t_, i)
        pisca(lk["dig"], 3.4, 4.0, dur=0.8); pisca(lk["azul"], 3.4, 9.0, base=2.5, dur=0.8); destrava(3.5)
        key(ela["armR"], "rotation_euler", f(3.8), (-0.8, 0, 0.1))
        key(lk["alav_e"], "rotation_euler", f(3.9), (0, 0, 0)); key(lk["alav_e"], "rotation_euler", f(4.2), (0, math.radians(-30), 0))
        key(lk["alav_e"], "rotation_euler", f(5.2), (0, math.radians(-30), 0)); key(lk["alav_e"], "rotation_euler", f(5.5), (0, 0, 0))
        abre(f(4.2), f(5.8), -80)
        look(ela, 1, 0.3, 0.1); look(ela, f(3.6), 0.0, 0.0); sorri(ela, f(3.7))
        aim_dof(cam, (1.7, 6.4, 1.6), (0.25, 5.25, 1.25), 1, 2.6)
        aim_dof(cam, (1.55, 6.2, 1.55), (0.25, 5.25, 1.25), N, 2.6)
    elif kind == "entra":        # 44–48 s: de dentro, a porta aberta, ela entra e olha a sala
        key(pt, "rotation_euler", 1, (0, 0, math.radians(-90)))
        ela["root"].location = (0.0, 5.7, 0.02); ela["root"].rotation_euler = (0, 0, 0)
        walk(ela, 1, f(2.2), (0.0, 5.7), (0.05, 4.0))
        key(ela["root"], "rotation_euler", f(2.2), (0, 0, 0)); key(ela["root"], "rotation_euler", f(3.4), (0, 0, math.radians(30)))
        look(ela, 1, 0, 0); look(ela, f(2.6), -0.15, 0.2); sorri(ela, f(1.0))
        key(ela["armL"], "rotation_euler", f(2.6), (0, 0, 0)); key(ela["armL"], "rotation_euler", f(3.2), (-0.4, 0, 0.5))
        aim_dof(cam, (0.9, 1.6, 1.5), (0.0, 4.6, 1.45), 1, 2.6)
        aim_dof(cam, (0.75, 1.9, 1.5), (0.0, 4.1, 1.45), N, 2.6)
    return cam


def lembranca(kind):
    """quarto das lembranças (x=20): escrivaninha; estudo (noite), trabalho (dia) e planos (fim de tarde)"""
    N, FPS = L.N, L.FPS
    f = lambda sec: 1 + sec * FPS
    random.seed(21)
    X = 20.0
    box((X, 2, 0.0), (6, 6, 0.02), mat("piso_quarto", (170, 130, 96), rough=0.5), 0.0)
    parede = mat("parede_quarto", (226, 214, 196))
    box((X, 3.2, 1.5), (6, 0.15, 3), parede, 0.0); box((X - 2.6, 2, 1.5), (0.15, 6, 3), parede, 0.0)
    box((X + 2.6, 2, 1.5), (0.15, 6, 3), parede, 0.0)
    noite = kind == "estudo"
    janela = mat("janela_noite" if noite else "janela_dia", (30, 40, 80) if noite else (190, 220, 245), emit=0.8 if noite else 2.0)
    box((X + 1.3, 3.12, 1.6), (1.1, 0.03, 1.0), janela, 0.0)
    for dx in (-0.55, 0.55): box((X + 1.3 + dx, 3.1, 1.6), (0.05, 0.04, 1.05), mat("caixilho", (240, 240, 240)), 0.0)
    madeira = mat("mesa_madeira", (140, 98, 64), rough=0.4)
    box((X, 1.6, 0.74), (1.6, 0.7, 0.04), madeira, 0.005)
    box((X, 1.27, 0.37), (1.6, 0.03, 0.72), madeira, 0.0)  # painel frontal: esconde as pernas da personagem sentada
    for dx in (-0.78, 0.78): box((X + dx, 1.6, 0.37), (0.04, 0.68, 0.72), madeira, 0.0)
    ela = make_person((30, 30, -20), skin="parda", hair="castanho",
                      style={"estudo": "rabo", "trabalho": "coque"}.get(kind, "longo"),
                      shirt={"estudo": (120, 124, 140), "trabalho": (240, 240, 244)}.get(kind, (214, 190, 150)),
                      pants=(44, 52, 76))
    ela["root"].location = (X, 1.95, -0.42)
    vida(ela, N, 9)
    box((X, 2.25, 0.55), (0.5, 0.06, 0.8), mat("cadeira", (60, 60, 70)), 0.02)
    cam = camera((0, 0, 0), (0, 0, 0), 35)
    lampada, ls = emat("abajur", (255, 220, 160), 6.0)
    cyl((X - 0.6, 1.75, 0.77), 0.07, 0.02, mat("abajur_base", (40, 40, 44)), verts=16)
    cyl((X - 0.6, 1.75, 0.95), 0.008, 0.36, mat("abajur_base", (40, 40, 44)), verts=8)
    sphere((X - 0.6, 1.72, 1.12), 0.07, mat("abajur_cupula", (240, 210, 150), emit=1.5), None, 14, scale=(1, 1, 0.7))
    bpy.ops.object.light_add(type="POINT", location=(X - 0.55, 1.6, 1.05)); al = bpy.context.object
    al.data.energy = 45 if noite else 12; al.data.color = (1, 0.8, 0.55); al.data.shadow_soft_size = 0.15
    bpy.ops.object.light_add(type="AREA", location=(X + 1.3, 2.8, 1.8), rotation=(math.radians(-70), 0, 0)); wl = bpy.context.object
    wl.data.energy = 15 if noite else 160; wl.data.size = 1.2; wl.data.color = (0.7, 0.8, 1) if noite else (1, 0.92, 0.82)
    bpy.ops.object.light_add(type="AREA", location=(X, -0.6, 2.4), rotation=(math.radians(60), 0, 0)); fl = bpy.context.object
    fl.data.energy = 35 if noite else 70; fl.data.size = 2.0; fl.data.color = (1, 0.9, 0.8)
    w = bpy.data.worlds.new("quarto"); bpy.context.scene.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.04, 0.035, 0.03, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.4
    hold(ela, 1, True)
    if kind == "estudo":         # 5–9,5 s: noite, livros, ela escreve
        cores = [(150, 40, 40), (40, 80, 140), (60, 120, 70), (200, 160, 60), (90, 60, 120)]
        for i in range(5):
            box((X + 0.55, 1.55, 0.78 + i * 0.045), (0.3 - 0.01 * i, 0.22, 0.04), mat("livro%d" % i, cores[i]), 0.004, rot=(0, 0, 0.08 * (i % 2)))
        box((X - 0.08, 1.55, 0.765), (0.42, 0.3, 0.01), mat("caderno", (250, 248, 240)), 0.0)
        for i in range(6): box((X - 0.08, 1.48 + i * 0.03, 0.771), (0.34, 0.012, 0.002), mat("linha_azul", (150, 170, 210)), 0.0)
        caneta = box((0, -0.02, -0.6), (0.008, 0.008, 0.13), mat("caneta", (30, 50, 140)), 0.0, ela["armR"], rot=(0.6, 0, 0))
        for i in range(N // 3):
            key(ela["armR"], "rotation_euler", 1 + i * 3, (-1.1 - 0.06 * (i % 2), 0, 0.12 + 0.05 * math.sin(i)))
        look(ela, 1, 0.45, 0); look(ela, f(3.0), 0.5, -0.1)
        aim_dof(cam, (X + 0.5, 0.35, 1.35), (X, 1.75, 1.0), 1, 2.4)
        aim_dof(cam, (X + 0.35, 0.55, 1.3), (X, 1.75, 1.0), N, 2.4)
    elif kind == "trabalho":     # 9,5–13,5 s: dia, notebook, ela trabalha
        tela, _ = emat("tela_note", (200, 225, 255), 2.0)
        box((X, 1.6, 0.77), (0.4, 0.28, 0.015), mat("note", (60, 62, 70)), 0.004)
        nt = empty((X, 1.46, 0.78)); nt.rotation_euler = (math.radians(12), 0, 0)  # tela virada para ela
        box((0, 0, 0.13), (0.4, 0.012, 0.26), mat("note", (60, 62, 70)), 0.004, nt)
        box((0, 0.008, 0.13), (0.36, 0.002, 0.22), tela, 0.0, nt)
        cyl((X + 0.5, 1.5, 0.82), 0.04, 0.1, mat("caneca", (201, 162, 77)), verts=16)
        for i in range(N // 2):
            key(ela["armR"], "rotation_euler", 1 + i * 2, (-1.15 - 0.05 * (i % 2), 0, 0.12))
            key(ela["armL"], "rotation_euler", 2 + i * 2, (-1.15 - 0.05 * (i % 2), 0, -0.12))
        look(ela, 1, 0.25, 0); look(ela, f(2.5), 0.3, 0.05)
        aim_dof(cam, (X - 0.7, 0.5, 1.35), (X, 1.8, 1.15), 1, 2.4)
        aim_dof(cam, (X - 0.5, 0.65, 1.32), (X, 1.8, 1.15), N, 2.4)
    else:                        # 13,5–16 s: planos: caderno com contas, cofrinho de moedas, calendário
        box((X - 0.1, 1.55, 0.765), (0.42, 0.3, 0.01), mat("caderno", (250, 248, 240)), 0.0)
        for i, hgt in enumerate((0.04, 0.07, 0.1, 0.14, 0.18)):  # gráfico de barras desenhado à mão
            box((X - 0.24 + i * 0.07, 1.5, 0.771), (0.04, hgt, 0.002), mat("barra_verde", (60, 140, 90)), 0.0)
        vidro = mat("pote_vidro", (200, 225, 230), rough=0.05, alpha=0.4)
        cyl((X + 0.45, 1.55, 0.86), 0.08, 0.2, vidro, verts=24)
        moeda = mat("moeda", GOLD_IG, rough=0.3, metal=0.8)
        for i in range(12): cyl((X + 0.45 + random.uniform(-0.04, 0.04), 1.55 + random.uniform(-0.04, 0.04), 0.77 + i * 0.008), 0.02, 0.006, moeda, verts=16)
        m_ = cyl((0, 0, 0), 0.02, 0.006, moeda, rot=(math.pi / 2, 0, 0), verts=16)
        key(m_, "location", 1, (X + 0.45, 1.55, 1.12)); key(m_, "location", f(0.8), (X + 0.45, 1.55, 1.12))
        key(m_, "location", f(1.3), (X + 0.45, 1.55, 0.88))
        key(ela["armR"], "rotation_euler", 1, (-1.6, 0, -0.1)); key(ela["armR"], "rotation_euler", f(0.8), (-1.6, 0, -0.1))
        key(ela["armR"], "rotation_euler", f(1.4), (-1.1, 0, 0.12))
        cal = empty((X - 1.2, 3.11, 1.6))
        box((0, 0, 0), (0.6, 0.02, 0.55), mat("calendario", (250, 250, 246)), 0.0, cal)
        box((0, -0.012, 0.22), (0.6, 0.004, 0.1), mat("calendario_topo", (180, 50, 50)), 0.0, cal)
        xm = mat("xis", (190, 40, 40))
        for i in range(21):
            r, c = divmod(i, 7)
            texto3d("x", (-0.24 + c * 0.08, -0.013, 0.1 - r * 0.1), 0.06, xm, (math.pi / 2, 0, 0), parent=cal)
        look(ela, 1, 0.3, -0.25); look(ela, f(1.6), 0.15, 0.3); look(ela, N, 0.1, 0.35)
        ela["mouth"].scale = (1.9, 0.3, 0.45); ela["mouth"].keyframe_insert("scale", frame=int(f(1.8)))
        aim_dof(cam, (X + 0.9, 0.4, 1.4), (X, 1.8, 1.1), 1, 2.6)
        aim_dof(cam, (X + 0.75, 0.6, 1.38), (X, 1.8, 1.12), N, 2.6)
    return cam


L.CENARIOS["porta"] = lambda kind="corredor": porta(kind)
L.CENARIOS["lembranca"] = lambda kind="estudo": lembranca(kind)
