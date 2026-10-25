#!/usr/bin/env python3
"""Pipeline dos comerciais 3D da Infinity Guard (9:16, personagens fictícios, CTA para o site).

    python3 produzir.py validar    <episodio>   # roteiro x catálogo x regras (antes de gastar render)
    python3 produzir.py narrar     <episodio>   # vozes por fala em horário fixo + marks.json
    python3 produzir.py documentos <episodio>   # storyboard.md, roteiro_de_cenas.md e legendas.srt
    python3 produzir.py render     <episodio>   # tomadas 3D (Blender) + montagem
    python3 produzir.py checar     <episodio>   # confere o MP4 (duração, formato, áudio, falas, quadros)
    python3 produzir.py exportar   <episodio>   # só copia para exports/ se validar e checar passarem
    python3 produzir.py tudo       <episodio>

Voz do narrador: a Dave (Pippit) só entra se existir <episodio>/voz_dave/ com um arquivo por fala do narrador
(01.wav, 02.wav... na ordem do roteiro) e o arquivo voz_dave/AUTORIZACAO.txt. Sem isso, a narração usa a voz
gratuita Kokoro como PROVISÓRIA, o vídeo mostra "vozes sintéticas provisórias" e o arquivo exportado leva
"_PROVISORIO" no nome.
"""
import datetime, glob, json, os, re, shutil, subprocess, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
ANIME = os.path.join(AQUI, "..", "anime3d")
CATALOGO = os.path.join(AQUI, "..", "..", "..", "atendente-infinity-guard", "references", "catalogo.json")
BLENDER_PY = os.environ.get("BLENDER_PY", os.path.join(ANIME, ".venv-blender", "bin", "python"))
MAX_IDADE_CATALOGO = 7  # dias

# termos que não podem aparecer em fala ou texto de tela (não confirmados ou proibidos pelas regras da loja)
PROIBIDOS = {
    "gravação/gravar": r"\bgrav(a|am|ação|ações|ar|ando|ada|ado|e)\b", "áudio": r"\báudio\b", "alerta": r"\balerta",
    "notificação": r"\bnotifica", "Anatel": r"anatel", "garantia": r"garantia",
    "instalação": r"\binstala(ção|mos|dor)\b", "4G": r"\b4g\b", "sem juros": r"sem juros", "frete": r"\bfrete\b",
    "promoção/desconto": r"promo(ção|cional)|desconto|oferta|só hoje|últimas unidades|black friday",
    "identificação de pessoa": r"identific|reconhec|detect", "100%": r"100 ?%|totalmente seguro|à prova",
    "nuvem": r"\bnuvem\b",
    "rosto do proprietário": r"maximiliano",
}
# recursos de câmera: só podem ser citados se estiverem no nome ou nos destaques do produto
RECURSOS = {"visão noturna": r"visão noturna", "dupla lente": r"dupla lente|lente dupla",
            "wi-fi": r"wi-?fi", "zoom": r"\bzoom", "rastreamento": r"rastrea", "kit com 2": r"duas câmeras|2 câmeras|kit com 2",
            "monitoramento duplo": r"monitoramento duplo", "sensor": r"\bsensor",
            "aplicativo": r"\b(aplicativo|app)\b", "cartão": r"\bcart(ão|ões)\b", "senha": r"\bsenha",
            "impressão digital": r"biometr|impress(ão|ões) digita|\bdigital\b", "bluetooth": r"bluetooth",
            "resolução": r"\b(2k|4k|full ?hd|1080p|\d+ ?mp)\b", "poe": r"\bpoe\b"}
# recurso que o catálogo chama por outro nome
SINONIMOS = {"aplicativo": "app"}


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def por_extenso(n):
    """inteiro de 0 a 999.999 por extenso (pt-BR), para a voz ler preços"""
    u = "zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete dezoito dezenove".split()
    d = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
    c = "_ cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()
    def ate999(x):
        if x == 100: return "cem"
        p = []
        if x >= 100: p.append(c[x // 100]); x %= 100
        if x >= 20: p.append(d[x // 10]); x %= 10
        if x or not p: p.append(u[x])
        return " e ".join(q for q in p if q)
    if n < 1000: return ate999(n)
    mil, resto = divmod(n, 1000)
    txt = "mil" if mil == 1 else ate999(mil) + " mil"
    if resto: txt += (" e " if resto < 100 or resto % 100 == 0 else " ") + ate999(resto)
    return txt


def reais_falado(v):
    r, c = int(v), int(round((v - int(v)) * 100))
    t = f"{por_extenso(r)} {'real' if r == 1 else 'reais'}"
    if c: t += f" e {por_extenso(c)}"  # como em locução de anúncio: "... reais e cinquenta e quatro"
    return t


def preencher(texto, prod, falado=False):
    """troca {preco}, {pix}, {parcelas} e {parcela} pelos valores do catálogo"""
    if not prod: return texto
    f = reais_falado if falado else brl
    return (texto.replace("{preco}", f(prod["preco"])).replace("{pix}", f(prod["pix"]))
            .replace("{parcela}", f(prod["parcela_valor"])).replace("{parcelas}", str(prod["parcelas"])))


def norm(s):
    return unicodedata.normalize("NFC", s.lower())


def carregar(ep):
    d = json.load(open(os.path.join(ep, "episodio.json")))
    cat = json.load(open(CATALOGO))
    return d, cat


def textos(d):
    for s in d["segmentos"]:
        for f in s["falas"]:
            yield f"fala {f['quem']} {f['ini']}s", f["texto"]
        for t in s.get("tela", []):
            if t.get("texto"): yield f"tela {t['ini']}s", t["texto"]
    yield "CTA", d["cta"]


def validar(ep, quieto=False):
    d, cat = carregar(ep)
    erros, avisos = [], []
    prod = next((p for p in cat["produtos"] if p["id"] == d.get("produto")), None)
    if d.get("produto") is None and d.get("produto_ilustrativo"):
        avisos.append(f"produto fora do catálogo ({d['produto_ilustrativo']['nome']}): o vídeo não mostra preço nem recursos; "
                      "cadastre o produto no catálogo para exibir a oferta")
    elif not prod: erros.append(f"produto {d['produto']} não existe no catálogo")
    elif not prod.get("ativo"): erros.append(f"produto {d['produto']} está inativo (esgotado?)")
    data_preco = (prod or {}).get("conferido_em", cat["atualizado_em"])  # produto conferido no site depois do catálogo
    idade = (datetime.date.today() - datetime.date.fromisoformat(data_preco)).days
    if idade > MAX_IDADE_CATALOGO:
        erros.append(f"preço com {idade} dias: atualize os preços (skill catalogo-e-precos) antes de produzir")
    else:
        avisos.append(f"preço do catálogo de {data_preco} ({idade} dias): reconfira no site antes de publicar")
    confirmados = norm(prod["nome"] + " " + " ".join(prod.get("destaques", []))) if prod else ""
    informados = set(d.get("recursos_informados", []))
    for r_ in informados:
        avisos.append(f"recurso '{r_}' informado pelo dono e não listado no catálogo: confira na página do produto antes de publicar")
    for onde, txt in textos(d):
        t = norm(txt)
        if not prod and re.search(r"\{\w+\}", txt): erros.append(f"{onde}: preço do catálogo pedido, mas o produto não está no catálogo")
        for ph in re.findall(r"\{(\w+)\}", txt):
            if ph not in ("preco", "pix", "parcelas", "parcela"): erros.append(f"{onde}: campo desconhecido {{{ph}}}")
        for nome, rx in PROIBIDOS.items():
            if re.search(rx, t): erros.append(f"{onde}: '{nome}' não pode aparecer — \"{txt}\"")
        for nome, rx in RECURSOS.items():
            if nome in informados: continue
            if re.search(rx, t) and not re.search(rx, confirmados) and SINONIMOS.get(nome, "§") not in confirmados:
                erros.append(f"{onde}: recurso '{nome}' não confirmado para {d['produto']} — \"{txt}\"")
        if re.search(r"r\$ ?\d", t): erros.append(f"{onde}: preço escrito à mão; o preço sai só do catálogo")
    # estrutura
    segs = d["segmentos"]
    if abs(segs[-1]["fim"] - d["duracao"]) > 0.01 or segs[0]["ini"] != 0:
        erros.append("os segmentos não cobrem 0 até a duração do vídeo")
    for a, b in zip(segs, segs[1:]):
        if abs(a["fim"] - b["ini"]) > 0.01: erros.append(f"buraco/sobreposição entre {a['fim']} e {b['ini']}")
    for s in segs:
        for f in s["falas"]:
            if not (s["ini"] <= f["ini"] < s["fim"]): erros.append(f"fala fora do segmento: {f['texto'][:30]}")
    if not any(t.get("tipo") in ("encerramento", "packshot") for s in segs for t in s.get("tela", [])):
        erros.append("falta o encerramento com o site, o logo e o CTA")
    if not d.get("cta"): erros.append("falta o CTA")
    if not prod and any(t.get("tipo") in ("produto", "selo_produto") for s_ in segs for t in s_.get("tela", [])):
        erros.append("cartão ou selo com preço pedido para um produto fora do catálogo")
    camp = d.get("campanha")
    if camp:
        if camp.get("confirmada"):
            avisos.append(f"campanha {camp['nome']} marcada como confirmada: confira cupom e preços na loja")
        else:
            avisos.append(f"campanha {camp['nome']} não confirmada: só nome, datas e link na bio (sem preço, desconto ou cupom)")
            if any(camp.get(k) for k in ("preco", "desconto", "cupom")): erros.append("campanha não confirmada não pode ter preço, desconto ou cupom")
    if norm(d["site"]) not in norm(cat["site"]): erros.append(f"site {d['site']} diferente do catálogo ({cat['site']})")
    tomadas = set(re.findall(r'"(P\d+)":', open(os.path.join(ep, "shots3d.py")).read()))
    tomadas = set(tomadas) | set(re.findall(r'"([A-Z]\w*)": \(', open(os.path.join(ep, "shots3d.py")).read()))
    for s in segs:
        usadas = [s["tomada"]] if s.get("tomada") else [x["tomada"] for x in s.get("tomadas", [])]
        for u in usadas:
            if u not in tomadas: erros.append(f"tomada {u} não existe em shots3d.py")
        subs = s.get("tomadas", [])
        if subs and (abs(subs[0]["ini"] - s["ini"]) > 0.01 or abs(subs[-1]["fim"] - s["fim"]) > 0.01):
            erros.append(f"as tomadas do segmento {s['ini']}–{s['fim']} não cobrem o segmento inteiro")
    if not quieto:
        print(f"== validar {os.path.basename(ep)}")
        for a in avisos: print("  aviso:", a)
        for e in erros: print("  ERRO:", e)
        print("  OK" if not erros else f"  {len(erros)} erro(s)")
    return erros, avisos


# ---------------- narração ----------------
def voz_dave(ep, d):
    pasta = os.path.join(ep, "voz_dave")
    narr = [f for s in d["segmentos"] for f in s["falas"] if f["quem"] == "narrador"]
    arqs = sorted(glob.glob(os.path.join(pasta, "*.wav")))
    if os.path.isfile(os.path.join(pasta, "AUTORIZACAO.txt")) and len(arqs) == len(narr):
        return dict(zip([id(f) for f in narr], arqs))
    return None


def narrar(ep):
    import numpy as np, soundfile as sf
    d, cat = carregar(ep)
    prod = next((p for p in cat["produtos"] if p["id"] == d.get("produto")), None)
    build = os.path.join(ep, "build"); os.makedirs(build, exist_ok=True)
    dave = voz_dave(ep, d)
    kok = None
    sr = 24000; T = d["duracao"]; trilha = np.zeros(int(T * sr), np.float32)
    falas = [f for s in d["segmentos"] for f in s["falas"]]
    fins = {id(f): s["fim"] for s in d["segmentos"] for f in s["falas"]}
    marks, erros = [], []
    for i, f in enumerate(falas):
        limite = min(fins[id(f)], falas[i + 1]["ini"] - 0.15 if i + 1 < len(falas) else T) - 0.05
        cfg = d["vozes"][f["quem"]]
        if f["quem"] == "narrador" and dave:
            a, r = sf.read(dave[id(f)], dtype="float32")
            if a.ndim > 1: a = a.mean(axis=1)
            if r != sr:
                a = np.interp(np.arange(int(len(a) * sr / r)) / sr, np.arange(len(a)) / r, a).astype(np.float32)
        else:
            if kok is None:
                from kokoro_onnx import Kokoro
                kok = Kokoro(os.path.join(ANIME, "modelos", "kokoro-v1.0.onnx"), os.path.join(ANIME, "modelos", "voices-v1.0.bin"))
            vel = cfg.get("velocidade", 1.0)
            while True:
                a, _ = kok.create(preencher(f.get("fala") or f["texto"], prod, falado=True), voice=cfg["provisoria"], speed=vel, lang="pt-br")
                a = a.astype(np.float32); idx = np.where(np.abs(a) > 0.01)[0]
                a = a[max(0, idx[0] - int(sr * 0.06)):idx[-1] + int(sr * 0.12)]
                if f["ini"] + len(a) / sr <= limite or vel >= 1.2: break
                vel = round(vel + 0.05, 2)
        dur = len(a) / sr
        if f["ini"] + dur > limite + 1e-3:
            erros.append(f"fala não cabe no horário ({f['ini']}s + {dur:.2f}s > {limite:.2f}s): {f['texto']}")
        i0 = int(f["ini"] * sr); trilha[i0:i0 + len(a)] += a[:max(0, len(trilha) - i0)]
        marks.append({"cena": next(k + 1 for k, s in enumerate(d["segmentos"]) if f in s["falas"]), "quem": f["quem"],
                      "texto": preencher(f["texto"], prod), "ini": f["ini"], "fim": round(f["ini"] + dur, 3)})
    trilha = trilha / max(1e-6, np.max(np.abs(trilha))) * 0.89
    # trilha musical suave gerada por código (sem direitos autorais)
    n = len(trilha); tt = np.arange(n) / sr
    nota = lambda m: 440 * 2 ** ((m - 69) / 12)
    prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]
    pad = np.zeros(n)
    for i in range(int(T / 4) + 1):
        a0, b0 = int(i * 4 * sr), min(n, int((i * 4 + 4.6) * sr))
        if a0 >= n: break
        x = np.arange(b0 - a0) / sr; env = np.minimum(1, x / 1.2) * np.minimum(1, (b0 - a0) / sr - x + 0.01)
        for m in prog[i % 4]:
            fq = nota(m); pad[a0:b0] += env * (np.sin(2 * np.pi * fq * x) + 0.3 * np.sin(4 * np.pi * fq * x))
    pad = pad / np.max(np.abs(pad)) * 0.07 * np.minimum(1, tt / 2) * np.minimum(1, (T - tt) / 2)
    if d.get("trilha") == "piano":
        sys.path.insert(0, AQUI); import sons
        pad = sons.trilha_piano(T, sr)[:n]
    sfx = np.zeros(n, np.float32)
    if d.get("sons"):
        sys.path.insert(0, AQUI); import sons
        sfx = sons.trilha_sons(d["sons"], T, sr)[:n]
    mix = (trilha + pad + sfx); mix /= max(1, np.max(np.abs(mix)) / 0.95)
    sf.write(os.path.join(build, "audio_final.wav"), mix.astype(np.float32), sr)
    json.dump(marks, open(os.path.join(build, "marks.json"), "w"), ensure_ascii=False, indent=1)
    info = {"provisoria": dave is None, "narrador": "dave" if dave else "kokoro:" + d["vozes"]["narrador"]["provisoria"],
            "motivo": None if dave else "voz Dave não disponível: nenhuma ferramenta de áudio com a Dave configurada "
                                        "(falta voz_dave/ com AUTORIZACAO.txt e um arquivo por fala do narrador)"}
    json.dump(info, open(os.path.join(build, "narracao_info.json"), "w"), ensure_ascii=False, indent=1)
    print(f"== narrar: narrador = {info['narrador']}" + (" (PROVISÓRIA)" if dave is None else ""))
    for m in marks: print(f"  {m['ini']:5.1f}–{m['fim']:5.2f}s {m['quem']:12s} {m['texto']}")
    for e in erros: print("  ERRO:", e)
    return erros


# ---------------- documentos ----------------
def srt_t(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def documentos(ep):
    d, cat = carregar(ep)
    prod = next((p for p in cat["produtos"] if p["id"] == d.get("produto")), None)
    marks = json.load(open(os.path.join(ep, "build", "marks.json")))
    info = json.load(open(os.path.join(ep, "build", "narracao_info.json")))
    # legendas
    with open(os.path.join(ep, "legendas.srt"), "w") as fo:
        for i, m in enumerate(marks, 1):
            quem = "" if m["quem"] == "narrador" else f"{m['quem'].upper()}: "
            fo.write(f"{i}\n{srt_t(m['ini'])} --> {srt_t(m['fim'] + 0.3)}\n{quem}{m['texto']}\n\n")
    # storyboard
    nome_prod = prod["nome"] if prod else d["produto_ilustrativo"]["nome"] + " (fora do catálogo: sem preço nem recursos)"
    L = [f"# Storyboard — {d['titulo']}", "",
         f"{d['formato']} · {d['duracao']:.0f} s · produto: {nome_prod} · CTA: {d['cta']} · {d['site']}", "",
         "Personagens fictícios: " + "; ".join(f"**{k}** — {v}" for k, v in d["personagens"].items()), "",
         f"Narrador: {info['narrador']}" + (" — **PROVISÓRIA**: " + info["motivo"] if info["provisoria"] else ""), ""]
    for i, s in enumerate(d["segmentos"], 1):
        img = f"storyboard/seg{i}.png"
        tom = s.get("tomada") or ", ".join(f"{x['tomada']} ({x['ini']}–{x['fim']} s)" for x in s.get("tomadas", [])) or "cartela"
        L += [f"## {i}. {s['titulo']} ({s['ini']:.0f}–{s['fim']:.0f} s · tomada {tom})", "",
              f"![seg{i}]({img})" if os.path.exists(os.path.join(ep, img)) else "_(quadro gerado após o render)_", "",
              f"- **Ação:** {s['storyboard']}", f"- **Câmera:** {s['camera']}"]
        for f in s["falas"]: L.append(f"- **{f['quem']}** ({f['ini']} s): \"{f['texto']}\"")
        for t in s.get("tela", []):
            if t.get("texto"): L.append(f"- **Tela** ({t['ini']} s): {t['texto']}")
            elif t.get("tipo") == "produto":
                L.append(f"- **Tela** ({t['ini']} s): cartão do produto — {nome_prod}; destaques: {', '.join(prod['destaques']) if prod else '—'}; "
                         f"preço do catálogo de {cat['atualizado_em']}; requisitos: {', '.join(prod.get('requisitos', []))}")
            elif t.get("tipo") == "packshot":
                L.append(f"- **Tela** ({t['ini']} s): packshot com a foto do produto, logo original, " +
                         ("preço e condições do catálogo" if prod else "sem preço (produto fora do catálogo)") +
                         (f", selo {d['campanha']['nome']}: {d['campanha']['chamada']}" if d.get("campanha") else "") + f" e o CTA \"{d['cta']}\"")
            elif t.get("tipo") == "encerramento":
                L.append(f"- **Tela** ({t['ini']} s): kit, logo original com o slogan, {d['site']} e o CTA")
        L.append("")
    L += ["## Regras do episódio", ""] + [f"- {r}" for r in d.get("regras_do_episodio", [])]
    open(os.path.join(ep, "storyboard.md"), "w").write("\n".join(L) + "\n")
    if d.get("descricao"):
        open(os.path.join(ep, "descricao.md"), "w").write(f"# Descrição do post — {d['titulo']}\n\n" + d["descricao"].strip() + "\n")
    # roteiro de cenas (para animação e áudio)
    R = [f"# Roteiro de cenas — {d['titulo']}", "", "| Tempo | Tomada 3D | O que acontece | Fala | Tela |", "|---|---|---|---|---|"]
    for s in d["segmentos"]:
        falas = "<br>".join(f"{f['ini']} s **{f['quem']}**: {f['texto']}" for f in s["falas"])
        tela = "<br>".join(f"{t['ini']} s {t.get('texto') or t.get('tipo')}" for t in s.get("tela", []))
        tom = s.get("tomada") or ", ".join(x["tomada"] for x in s.get("tomadas", [])) or "—"
        R.append(f"| {s['ini']:.0f}–{s['fim']:.0f} s | {tom} | {s['storyboard']} | {falas} | {tela} |")
    open(os.path.join(ep, "roteiro_de_cenas.md"), "w").write("\n".join(R) + "\n")
    print("== documentos: storyboard.md, roteiro_de_cenas.md, legendas.srt" + (", descricao.md" if d.get("descricao") else ""))


# ---------------- render ----------------
def tomadas(ep):
    import ast
    tree = ast.parse(open(os.path.join(ep, "shots3d.py")).read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "TOMADAS":
            return ast.literal_eval(node.value)


def render(ep):
    q_ = carregar(ep)[0].get("qualidade", {})
    samples = q_.get("samples", 8)
    env = dict(os.environ, LIB3D_RES=q_.get("resolucao_3d", "640x1138"))
    shots = os.path.join(ep, "build", "shots"); os.makedirs(shots, exist_ok=True)
    for nome, (dur, *_r) in tomadas(ep).items():
        q = max(1, round(dur * 12))
        pasta = os.path.join(shots, nome)
        if os.path.isdir(pasta) and len(os.listdir(pasta)) >= q:
            print(f"  {nome}: pronta"); continue
        print(f"  {nome}: {q} quadros...", flush=True)
        with open(os.path.join(ep, "build", f"log_{nome}.txt"), "w") as log:
            r = subprocess.run([BLENDER_PY, os.path.join(ep, "shots3d.py"), nome, "--samples", str(samples), "--saida", shots],
                               stdout=log, stderr=subprocess.STDOUT, env=env)
        if r.returncode: sys.exit(f"falhou a tomada {nome} (veja build/log_{nome}.txt)")
    subprocess.run([sys.executable, os.path.join(ep, "montagem.py"), "video", saida_mp4(ep)], check=True)
    if carregar(ep)[0].get("capa"):
        subprocess.run([sys.executable, os.path.join(ep, "montagem.py"), "capa"], check=True)
    # quadros do storyboard: meio de cada segmento, já com as sobreposições
    d, _ = carregar(ep)
    os.makedirs(os.path.join(ep, "storyboard"), exist_ok=True)
    for i, s in enumerate(d["segmentos"], 1):
        t = s["ini"] + (s["fim"] - s["ini"]) * 0.6
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", saida_mp4(ep), "-frames:v", "1",
                        "-vf", "scale=360:-1", os.path.join(ep, "storyboard", f"seg{i}.png")], check=True)


def saida_mp4(ep):
    return os.path.join(ep, "build", os.path.basename(ep) + ".mp4")


# ---------------- checagem do vídeo ----------------
def checar(ep):
    d, _ = carregar(ep)
    mp4 = saida_mp4(ep); erros = []
    if not os.path.exists(mp4): return [f"vídeo não encontrado: {mp4}"]
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", mp4],
                                   capture_output=True, text=True).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), None)
    dur = float(pr["format"]["duration"])
    if (v["width"], v["height"]) != (1080, 1920): erros.append(f"resolução {v['width']}x{v['height']} (esperado 1080x1920)")
    if abs(dur - d["duracao"]) > 0.3: erros.append(f"duração {dur:.2f}s (esperado {d['duracao']}s)")
    if not a: erros.append("sem áudio")
    lo = subprocess.run(["ffmpeg", "-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    lo = lo[lo.rfind("Summary:"):]  # só o resumo final (as linhas de antes são medições parciais)
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", lo); pk = re.search(r"Peak:\s+(-?[\d.]+) dBFS", lo)
    if m and not (-17 <= float(m.group(1)) <= -12): erros.append(f"volume {m.group(1)} LUFS fora de -17..-12")
    if pk and float(pk.group(1)) > -0.5: erros.append(f"pico {pk.group(1)} dBFS (risco de estouro)")
    marks = json.load(open(os.path.join(ep, "build", "marks.json")))
    segs = d["segmentos"]
    for mk in marks:
        s = segs[mk["cena"] - 1]
        if mk["fim"] > s["fim"] + 0.01: erros.append(f"fala passa do fim do segmento: {mk['texto']}")
    # quadros pretos ou congelados demais
    bl = subprocess.run(["ffmpeg", "-i", mp4, "-vf", "blackdetect=d=0.4:pix_th=0.05", "-an", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    if "black_start" in bl: erros.append("trecho preto no vídeo: " + re.findall(r"black_start:\S+ black_end:\S+", bl)[0])
    print(f"== checar: {v['width']}x{v['height']}, {dur:.2f}s, {m.group(1) if m else '?'} LUFS, pico {pk.group(1) if pk else '?'} dBFS")
    for e in erros: print("  ERRO:", e)
    print("  OK" if not erros else f"  {len(erros)} erro(s)")
    return erros


def exportar(ep):
    e1, _ = validar(ep, quieto=True); e2 = checar(ep)
    if e1 or e2: sys.exit("exportação bloqueada: corrija os erros acima (rode 'validar' e 'checar').")
    info = json.load(open(os.path.join(ep, "build", "narracao_info.json")))
    out = os.path.join(AQUI, "exports"); os.makedirs(out, exist_ok=True)
    nome = os.path.basename(ep) + ("_PROVISORIO" if info["provisoria"] else "") + ".mp4"
    shutil.copy(saida_mp4(ep), os.path.join(out, nome))
    shutil.copy(os.path.join(ep, "legendas.srt"), os.path.join(out, os.path.basename(ep) + ".srt"))
    for extra in ("capa.png", "descricao.md"):
        if os.path.exists(os.path.join(ep, extra)):
            shutil.copy(os.path.join(ep, extra), os.path.join(out, os.path.basename(ep) + "-" + extra))
    # arquivo de projeto: roteiro, scripts, imagens, áudio e as cenas do Blender (.blend) de cada tomada
    import zipfile
    zp = os.path.join(out, os.path.basename(ep) + "-projeto.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for raiz, _dirs, arqs in os.walk(ep):
            rel = os.path.relpath(raiz, ep)
            if rel.startswith(os.path.join("build", "shots")) or rel.startswith("storyboard"): continue
            for a_ in arqs:
                if a_.endswith(".mp4") or a_.startswith("quadro_") or a_.startswith("log_"): continue
                z.write(os.path.join(raiz, a_), os.path.join(os.path.basename(ep), rel, a_))
        for f_ in ("cenarios.py", "cenarios_loja.py", "cenarios_ape.py", "cenarios_inauguracao.py", "comercial.py", "produzir.py", "sons.py"):
            if os.path.exists(os.path.join(AQUI, f_)): z.write(os.path.join(AQUI, f_), os.path.join("pipeline", f_))
    print("== projeto:", zp)
    print("== exportado:", os.path.join(out, nome))


def main():
    cmd, ep = sys.argv[1], os.path.abspath(sys.argv[2])
    if cmd in ("validar", "tudo"):
        if validar(ep)[0]: sys.exit(1)
    if cmd in ("narrar", "tudo"):
        if narrar(ep): sys.exit(1)
    if cmd in ("documentos", "tudo"): documentos(ep)
    if cmd in ("render", "tudo"): render(ep)
    if cmd == "tudo": documentos(ep)  # de novo, agora com os quadros
    if cmd in ("checar",): sys.exit(1 if checar(ep) else 0)
    if cmd in ("exportar", "tudo"): exportar(ep)


if __name__ == "__main__":
    main()
