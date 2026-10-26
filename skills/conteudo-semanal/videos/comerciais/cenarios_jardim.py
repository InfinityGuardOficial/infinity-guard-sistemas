"""Cenário "jardim": casa térrea com garagem e jardim (bairro brasileiro), muro lateral com vasos, casal fictício,
um gato laranja e uma borboleta dourada; e a Câmera ASECAM PTZ 4K 8MP modelada a partir da foto do produto
(suporte de parede com duas antenas, cabeça branca com lente e 4 LEDs, globo preto com lente dupla e LEDs).
Também "ptz_estudio" (produto girando em fundo azul-marinho).
"""
import math, random
import lib3d as L
from lib3d import (bpy, Vector, mat, emat, box, cyl, sphere, ico, cone, empty, setmat, M, make_house, make_tree,
                   ground, world, sun, camera, hills, anime_clouds)
from cenarios import make_person, talk, walk, hold, look, key, vida, aim_dof

NAVY_IG, GOLD_IG = (14, 26, 43), (201, 162, 77)
MURO_X = -4.6            # muro lateral (divisa com o vizinho), ao longo de Y
VASOS_Y = (-5.2, -6.6, -8.0, -9.4)


def ptz(loc=(0, 0, 0), rot_z=0.0, s=1.0, parent=None):
    """câmera PTZ presa na parede (a parede fica atrás, em +Y). Devolve (raiz, cabeça que gira, força dos LEDs)."""
    r = empty(loc); r.rotation_euler = (0, 0, rot_z); r.scale = (s, s, s)
    if parent: r.parent = parent
    branco = mat("ptz_branco", (244, 244, 242), rough=0.35)
    preto = mat("ptz_preto", (18, 18, 22), rough=0.2)
    vidro = mat("ptz_vidro", (8, 8, 12), rough=0.05)
    led, led_s = emat("ptz_led", (255, 246, 226), 1.0)
    aro = mat("ptz_aro", (200, 200, 196), rough=0.3)
    # suporte de parede (base, braço) e antenas
    box((0, 0.11, 0.17), (0.12, 0.02, 0.1), branco, 0.008, r)
    box((0, 0.05, 0.2), (0.16, 0.12, 0.03), branco, 0.008, r)
    for x in (-0.095, 0.095):
        cyl((x, 0.1, 0.27), 0.007, 0.24, branco, verts=12, parent=r)
        cyl((x, 0.1, 0.15), 0.011, 0.03, branco, verts=12, parent=r)
    cab = empty((0, 0.0, 0.0)); cab.parent = r                 # tudo abaixo do suporte gira (pan)
    cyl((0, 0.0, 0.17), 0.035, 0.03, branco, verts=24, parent=cab)
    box((0, 0.0, 0.1), (0.15, 0.13, 0.1), branco, 0.025, cab)   # cabeça de cima (branca)
    box((0.02, -0.066, 0.1), (0.085, 0.006, 0.062), preto, 0.006, cab)
    cyl((0.02, -0.07, 0.1), 0.017, 0.008, vidro, rot=(math.pi / 2, 0, 0), verts=24, parent=cab)
    for dx in (-0.024, 0.024):
        for dz in (-0.018, 0.018):
            cyl((0.02 + dx, -0.071, 0.1 + dz), 0.0065, 0.004, aro, rot=(math.pi / 2, 0, 0), verts=12, parent=cab)
            cyl((0.02 + dx, -0.074, 0.1 + dz), 0.004, 0.002, led, rot=(math.pi / 2, 0, 0), verts=12, parent=cab)
    sphere((0, 0.0, -0.035), 0.078, preto, cab, 32, scale=(1, 1, 0.95))   # globo de baixo (preto)
    box((0, -0.072, -0.03), (0.105, 0.012, 0.035), vidro, 0.01, cab)      # faixa com lente dupla
    for x in (-0.025, 0.025):
        cyl((x, -0.079, -0.03), 0.011, 0.004, mat("ptz_lente2", (30, 30, 40), rough=0.05), rot=(math.pi / 2, 0, 0), verts=20, parent=cab)
    for z in (0.008, -0.068):                                         # fileiras de 4 LEDs acima e abaixo
        for i in range(4):
            x = -0.036 + i * 0.024
            cyl((x, -0.073 + abs(z + 0.03) * 0.25, z), 0.0065, 0.004, aro, rot=(math.pi / 2, 0, 0), verts=12, parent=cab)
            cyl((x, -0.0765 + abs(z + 0.03) * 0.25, z), 0.004, 0.002, led, rot=(math.pi / 2, 0, 0), verts=12, parent=cab)
    return r, cab, led_s


def vaso(loc, s=1.0, caido=False, seed=0):
    rnd = random.Random(seed)
    g = empty(loc)
    terracota = mat("terracota", (178, 92, 58), rough=0.6); terra = mat("terra", (92, 62, 40), rough=0.9)
    cyl((0, 0, 0.13 * s), 0.12 * s, 0.26 * s, terracota, verts=20, parent=g, bev=0.01)
    cyl((0, 0, 0.255 * s), 0.13 * s, 0.03 * s, terracota, verts=20, parent=g)
    cyl((0, 0, 0.245 * s), 0.11 * s, 0.01 * s, terra, verts=20, parent=g)
    planta = empty((0, 0, 0.26 * s)); planta.parent = g
    for k in range(5):
        ico((rnd.uniform(-0.06, 0.06) * s, rnd.uniform(-0.06, 0.06) * s, (0.08 + k * 0.05) * s), (0.09 - k * 0.008) * s,
            M["leaf"] if k % 2 else M["leaf2"], 1)
        bpy.context.object.parent = planta
    for k in range(3):
        sphere((rnd.uniform(-0.07, 0.07) * s, rnd.uniform(-0.07, 0.07) * s, (0.2 + k * 0.04) * s), 0.025 * s,
               mat("flor%d" % k, [(230, 80, 110), (250, 200, 60), (240, 240, 250)][k]), planta, 10)
    if caido:
        g.rotation_euler = (math.radians(95), 0, rnd.uniform(0, 6.28))
        g.location.z = 0.12 * s
        for k in range(5):  # terra espalhada no chão
            sphere((loc[0] + rnd.uniform(-0.35, 0.35), loc[1] + rnd.uniform(-0.35, 0.35), 0.02), rnd.uniform(0.06, 0.12),
                   terra, seg=10, scale=(1.4, 1.1, 0.25))
    return g


def gato(loc, rot=0.0):
    """gato laranja estilizado (de frente para -Y)"""
    g = empty(loc); g.rotation_euler = (0, 0, rot)
    laranja = mat("gato_laranja", (226, 140, 60), rough=0.8); claro = mat("gato_claro", (246, 224, 196), rough=0.8)
    sphere((0, 0.05, 0.16), 0.11, laranja, g, 20, scale=(0.8, 1.5, 0.8))
    sphere((0, -0.06, 0.15), 0.06, claro, g, 14, scale=(0.9, 0.6, 1.1))
    cab = empty((0, -0.13, 0.25)); cab.parent = g
    sphere((0, 0, 0), 0.075, laranja, cab, 20)
    sphere((0, -0.055, -0.02), 0.035, claro, cab, 12, scale=(1.2, 0.8, 0.8))
    for x in (-0.04, 0.04):
        cone((x, -0.005, 0.07), 0.028, 0.06, laranja, 6); bpy.context.object.parent = cab
        sphere((x * 0.75, -0.066, 0.015), 0.012, mat("gato_olho", (90, 200, 90), emit=0.6), cab, 10)
        sphere((x * 0.75, -0.075, 0.017), 0.005, mat("gato_pupila", (10, 10, 10)), cab, 8)
    sphere((0, -0.085, -0.005), 0.008, mat("gato_nariz", (220, 120, 140)), cab, 8)
    for x in (-0.05, 0.05):
        for y in (-0.05, 0.14):
            cyl((x, y, 0.06), 0.02, 0.12, laranja, verts=8, parent=g)
    cauda = empty((0, 0.2, 0.18)); cauda.parent = g
    for i in range(5):
        cyl((0, 0.04 * i, 0.04 * i), 0.018, 0.07, laranja if i % 2 else claro, rot=(math.radians(-45), 0, 0), verts=8, parent=cauda)
    return g, cab, cauda


def borboleta(loc):
    b = empty(loc)
    ouro, _ = emat("asa_ouro", GOLD_IG, 1.4)
    sphere((0, 0, 0), 0.008, mat("borb_corpo", (30, 24, 20)), b, 8, scale=(1, 1, 3))
    asas = []
    for sx in (-1, 1):
        a = empty((0, 0, 0)); a.parent = b
        box((sx * 0.03, 0, 0.01), (0.055, 0.003, 0.05), ouro, 0.0, a)
        box((sx * 0.024, 0, -0.022), (0.04, 0.003, 0.03), ouro, 0.0, a)
        asas.append((a, sx))
    return b, asas


def bater_asas(asas, n):
    for f in range(1, n + 1):
        ang = 0.9 * math.sin(f * 2.4)
        for a, sx in asas:
            a.rotation_euler = (0, sx * ang, 0); a.keyframe_insert("rotation_euler", frame=f)


def cenario_base(manha=True):
    ground(400, "grass")
    house, _cam, _sl = make_house((0, 0, 0), decor=False, camdev=False)
    for o in list(house.children):  # tira o muro baixo da frente da casa: o jardim fica aberto até o muro da rua
        if o.type != "MESH": continue
        cy = sum(v[1] for v in o.bound_box) / 8; cz = sum(v[2] for v in o.bound_box) / 8  # a posição fica na malha
        if abs(cy + 6.6) < 0.05 and cz < 1.0:
            bpy.data.objects.remove(o, do_unlink=True)
    make_house((-14.5, 1.0, 0), wall_color="wall2")          # casa do vizinho, do outro lado do muro
    tijolo = mat("muro_reboco", (232, 214, 184))
    box((MURO_X, -6.6, 0.75), (0.25, 7.6, 1.5), tijolo, 0.03)     # muro lateral com os vasos
    box((MURO_X, -6.6, 1.52), (0.32, 7.7, 0.06), mat("muro_topo", (200, 186, 160)), 0.01)
    box((-0.2, -10.6, 0.5), (9.0, 0.25, 1.0), tijolo, 0.03)       # muro da frente
    box((0, -12.5, 0.02), (60, 3.0, 0.04), M["road"], 0.0)
    box((2.2, -7.0, 0.035), (3.0, 7.0, 0.05), mat("piso_garagem", (190, 186, 178)), 0.0)  # entrada da garagem
    for y in (-4.5, -6.0, -7.5, -9.0):  # canteiro junto ao muro
        ico((MURO_X + 0.55, y, 0.25), 0.35, M["leaf2"], 1, scale=(1, 1.4, 0.7))
    make_tree((-2.6, -8.8, 0), 1.0)
    hills(0, 90, 10, 220)
    world((110, 170, 235), (250, 226, 196), 1.0)
    anime_clouds(0, 140, 6, 260, (28, 50))
    sun((math.radians(62), 0, math.radians(-55)), 3.4, (1, 0.9, 0.75))


def jardim(kind):
    N, FPS = L.N, L.FPS
    f = lambda sec: 1 + sec * FPS
    random.seed(19)
    cenario_base()
    ele = make_person((30, 30, -20), skin="morena", hair="castanho", style="curto", shirt=(60, 130, 90), pants=(60, 64, 80))
    ela = make_person((30, 30, -20), skin="negra", hair="preto", style="rabo", shirt=(240, 200, 120), pants=(70, 60, 90), height=0.97)
    for i, p in enumerate((ele, ela)): vida(p, N, i + 11)
    cam = camera((0, 0, 0), (0, 0, 0), 35)
    lens = lambda mm: setattr(cam.data, "lens", mm)
    instalada = kind in ("pov", "gato", "constrangido", "instala")
    vasos_em_pe = []
    if kind in ("descoberta", "recolhe", "ideia"):   # manhã seguinte: três vasos no chão
        for i, y in enumerate(VASOS_Y[:3]):
            vaso((MURO_X + 0.55 + 0.25 * (i % 2), y + 0.2, 0.0), caido=True, seed=i)
        vasos_em_pe.append(vaso((MURO_X, VASOS_Y[3], 1.55), seed=9))
    else:
        for i, y in enumerate(VASOS_Y):
            vasos_em_pe.append(vaso((MURO_X, y, 1.55), seed=i + 3))
    cam_ptz = cab = led_s = None
    if instalada:  # na quina da casa, de frente para o jardim e a garagem
        cam_ptz, cab, led_s = ptz((-3.95, -3.12, 2.55), rot_z=math.radians(-15), s=1.6)

    if kind == "descoberta":     # 0–5 s: ele sai e encontra os vasos no chão; olha desconfiado para o muro
        ele["root"].location = (-1.2, -3.4, 0.03)
        walk(ele, 1, f(1.6), (-1.2, -3.4), (-2.4, -5.6))
        key(ele["root"], "rotation_euler", 1, (0, 0, math.radians(-28)))
        key(ele["root"], "rotation_euler", f(1.6), (0, 0, math.radians(-28)))
        key(ele["root"], "rotation_euler", f(2.4), (0, 0, math.radians(-70)))
        look(ele, f(1.8), 0.35, 0); look(ele, f(3.0), 0.0, math.radians(-30))
        for b in ele["brows"]:  # sobrancelhas baixam: desconfiança
            z0 = b.location.z; b.keyframe_insert("location", frame=int(f(2.9)))
            b.location.z = z0 - 0.014; b.keyframe_insert("location", frame=int(f(3.3)))
        aim_dof(cam, (-0.4, -9.8, 1.7), (-2.8, -5.8, 1.1), 1, 3.0)
        aim_dof(cam, (-1.0, -8.6, 1.65), (-2.5, -5.6, 1.4), N, 3.0)
    elif kind == "recolhe":      # 5–11 s: ele recolhe a terra; ela chega com o café e conversa
        ele["root"].location = (-3.5, -5.4, -0.5); ele["root"].rotation_euler = (0, 0, math.radians(-30))
        key(ele["armR"], "rotation_euler", 1, (-1.2, 0, 0)); key(ele["armL"], "rotation_euler", 1, (-1.2, 0, 0))
        for i in range(4):
            key(ele["armR"], "rotation_euler", f(0.3 + i * 1.1), (-1.0, 0, 0)); key(ele["armR"], "rotation_euler", f(0.85 + i * 1.1), (-1.5, 0, 0))
        look(ele, 1, 0.6, 0)
        walk(ela, 1, f(2.0), (-1.2, -4.6), (-2.4, -6.4))
        key(ela["root"], "rotation_euler", 1, (0, 0, math.radians(-60)))
        key(ela["root"], "rotation_euler", f(2.2), (0, 0, math.radians(-132)))
        caneca = cyl((0, -0.45, 0.95), 0.04, 0.09, mat("caneca", (250, 250, 248)), verts=16, parent=ela["root"])
        key(ela["armR"], "rotation_euler", 1, (-1.1, 0, -0.2))
        talk(ela, f(2.6), f(5.4)); look(ela, f(2.4), 0.25, 0)
        look(ele, f(3.0), 0.15, math.radians(25))
        aim_dof(cam, (-0.6, -9.6, 1.5), (-3.0, -5.9, 0.95), 1, 2.6)
        aim_dof(cam, (-0.9, -9.2, 1.45), (-3.0, -5.9, 1.0), N, 2.6)
    elif kind == "ideia":        # 11–17 s: ela sugere observar antes de acusar; aponta a quina da casa
        ele["root"].location = (-3.2, -6.0, 0.03); ele["root"].rotation_euler = (0, 0, math.radians(40))
        ela["root"].location = (-2.3, -5.5, 0.03); ela["root"].rotation_euler = (0, 0, math.radians(-50))
        talk(ela, f(0.4), f(2.6))
        key(ela["armR"], "rotation_euler", f(2.6), (0, 0, 0)); key(ela["armR"], "rotation_euler", f(3.2), (-2.4, 0, -0.5))
        key(ela["armR"], "rotation_euler", f(5.2), (-2.4, 0, -0.5))
        look(ela, f(2.8), -0.3, math.radians(-60)); look(ele, f(3.2), -0.3, math.radians(70))
        key(ele["head"], "rotation_euler", f(4.6), (-0.1, 0, math.radians(-10))); key(ele["head"], "rotation_euler", f(5.0), (0.15, 0, math.radians(-10)))
        aim_dof(cam, (-0.6, -8.8, 1.6), (-2.9, -5.7, 1.4), 1, 2.6)
        aim_dof(cam, (-0.9, -8.2, 1.7), (-3.0, -5.0, 1.8), N, 2.6)
    elif kind == "instala":      # 17–26 s: câmera na quina da casa; a cabeça gira (enquadramento ajustável)
        ele["root"].location = (-3.0, -4.8, 0.03); ele["root"].rotation_euler = (0, 0, math.radians(20))
        ela["root"].location = (-2.2, -4.7, 0.03); ela["root"].rotation_euler = (0, 0, math.radians(-15))
        look(ele, 1, -0.45, 0); look(ela, 1, -0.4, 0)
        tel = box((0, -0.42, 1.05), (0.07, 0.01, 0.14), mat("celular", (20, 20, 26), rough=0.2), 0.008, ela["root"])
        key(ela["armR"], "rotation_euler", 1, (-1.2, 0, -0.1))
        cam_ptz.scale = (0.01, 0.01, 0.01); cam_ptz.keyframe_insert("scale", frame=1)
        cam_ptz.keyframe_insert("scale", frame=int(f(0.5)))
        cam_ptz.scale = (1.8, 1.8, 1.8); cam_ptz.keyframe_insert("scale", frame=int(f(1.1)))
        cam_ptz.scale = (1.6, 1.6, 1.6); cam_ptz.keyframe_insert("scale", frame=int(f(1.4)))
        for t_, a in ((2.0, 0), (3.6, -35), (5.4, 30), (7.0, 0)):   # demonstração do giro motorizado
            cab.rotation_euler = (0, 0, math.radians(a)); cab.keyframe_insert("rotation_euler", frame=int(f(t_)))
        aim_dof(cam, (-2.6, -5.0, 1.9), (-3.95, -3.12, 2.5), 1, 2.0)
        aim_dof(cam, (-1.4, -7.4, 1.7), (-3.4, -3.6, 2.0), int(f(4.0)), 3.0)
        aim_dof(cam, (-1.2, -7.8, 1.65), (-3.2, -3.8, 1.9), N, 3.0)
    elif kind in ("pov", "gato"):  # 26–41 s: o que a câmera mostra no app (jardim, muro e garagem)
        hide = [ele, ela]
        # vista do ponto da câmera, lente grande-angular
        base = (-3.95, -3.25, 2.45)
        if kind == "pov":
            for t_, alvo in ((0, (-2.6, -7.6, 0.4)), (4.5, (-4.5, -7.0, 1.2)), (N / FPS, (-4.5, -7.2, 1.25))):
                aim_dof(cam, base, alvo, int(f(t_)) if t_ else 1, 8.0)
        else:
            aim_dof(cam, base, (-4.5, -7.2, 1.3), 1, 8.0)
            g, gcab, cauda = gato((MURO_X, -10.2, 1.55), rot=math.radians(180))
            b, asas = borboleta((MURO_X + 0.3, -7.4, 2.0))
            bater_asas(asas, N)
            for t_, (y, z) in ((0, (-7.4, 2.0)), (1.2, (-7.0, 2.2)), (2.4, (-6.4, 1.95)), (3.6, (-5.8, 2.3)), (6.0, (-4.6, 2.6))):
                b.location = (MURO_X + 0.3 + 0.15 * math.sin(t_ * 3), y, z); b.keyframe_insert("location", frame=int(f(t_)))
            for t_, y in ((0, -10.2), (1.5, -8.6), (2.2, -8.0)):      # o gato anda pelo muro atrás da borboleta
                g.location = (MURO_X, y, 1.55); g.keyframe_insert("location", frame=int(f(t_)))
            for t_, (y, z) in ((2.6, (-7.3, 1.9)), (3.0, (-6.7, 1.75)), (3.3, (-6.5, 1.55))):  # o pulo
                g.location = (MURO_X, y, z); g.keyframe_insert("location", frame=int(f(t_)))
            alvo = vasos_em_pe[1]                                      # o vaso que ele derruba
            alvo.keyframe_insert("location", frame=int(f(3.1))); alvo.keyframe_insert("rotation_euler", frame=int(f(3.1)))
            alvo.location = (MURO_X + 0.55, alvo.location.y + 0.2, 0.12); alvo.rotation_euler = (math.radians(100), 0, 0.6)
            alvo.keyframe_insert("location", frame=int(f(3.7))); alvo.keyframe_insert("rotation_euler", frame=int(f(3.7)))
            for t_, a in ((0, 0), (1.0, 0.4), (2.0, -0.3), (3.0, 0.5), (4.0, -0.2), (5.0, 0.3)):
                cauda.rotation_euler = (0, a, 0); cauda.keyframe_insert("rotation_euler", frame=int(f(t_)))
            key(gcab, "rotation_euler", f(3.6), (0, 0, 0)); key(gcab, "rotation_euler", f(4.2), (0.2, 0, math.radians(-60)))
        lens(26)
    elif kind == "constrangido":  # 41–45 s: ele, sem graça, com a mão na testa; ela ri
        ele["root"].location = (-2.0, -4.6, 0.03); ele["root"].rotation_euler = (0, 0, math.radians(15))
        ela["root"].location = (-1.3, -4.5, 0.03); ela["root"].rotation_euler = (0, 0, math.radians(-25))
        key(ele["armR"], "rotation_euler", f(0.2), (0, 0, 0)); key(ele["armR"], "rotation_euler", f(0.8), (-2.6, 0, 0.9))
        look(ele, f(0.8), 0.35, math.radians(-10))
        ela["mouth"].scale = (2.0, 0.3, 0.7); ela["mouth"].keyframe_insert("scale", frame=1)
        for i in range(5):
            key(ela["head"], "rotation_euler", f(i * 0.6), (-0.15 if i % 2 else -0.05, 0, math.radians(-15)))
        tel = box((0, -0.42, 1.05), (0.07, 0.01, 0.14), mat("celular", (20, 20, 26), rough=0.2), 0.008, ela["root"])
        key(ela["armR"], "rotation_euler", 1, (-1.2, 0, -0.1))
        aim_dof(cam, (-1.6, -7.0, 1.6), (-1.65, -4.55, 1.55), 1, 2.4)
        aim_dof(cam, (-1.62, -6.6, 1.6), (-1.65, -4.55, 1.58), N, 2.4)
    return cam


def ptz_estudio():
    N = L.N
    world(NAVY_IG, (8, 16, 30), 0.6)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.5)); fl = bpy.context.object; setmat(fl, mat("floor_navy", (16, 30, 58), rough=0.3))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.004, location=(0, 0, -0.16))
    t = bpy.context.object; setmat(t, mat("aro_ouro", GOLD_IG, rough=0.3))
    r, cab, _ = ptz((0, 0, 0), rot_z=0.0, s=1.0)
    for t_, a in ((1, -30), (N, 30)):
        r.rotation_euler = (0, 0, math.radians(a)); r.keyframe_insert("rotation_euler", frame=int(t_))
    L._linear(r)
    bpy.ops.object.light_add(type="AREA", location=(0, -0.8, 0.6)); k = bpy.context.object; k.data.energy = 22; k.data.size = 0.8
    k.rotation_euler = (math.radians(50), 0, 0)
    for x in (-0.6, 0.6):
        bpy.ops.object.light_add(type="AREA", location=(x, 0.4, 0.3)); rr = bpy.context.object; rr.data.energy = 10; rr.data.size = 0.3
        rr.data.color = (1, 0.8, 0.45); d = Vector((0, 0, 0.05)) - rr.location; rr.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam = camera((0, 0, 0), (0, 0, 0), 55)
    aim_dof(cam, (0, -0.72, 0.08), (0, 0, 0.06), 1, 3.5)
    aim_dof(cam, (0, -0.62, 0.06), (0, 0, 0.06), N, 3.5)


L.CENARIOS["jardim"] = lambda kind="descoberta": jardim(kind)
L.CENARIOS["ptz_estudio"] = lambda **k: ptz_estudio()
