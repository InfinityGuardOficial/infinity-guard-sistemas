#!/usr/bin/env python3
"""Gera um Reel 9:16 a partir de um cenas.json.

Etapas:
  gerar  -> para cada cena com IA: cria a imagem da cena preservando o rosto da foto
            de referência (fal.ai, Nano Banana edit) e anima essa imagem (fal.ai, Kling
            image-to-video). Salva em <pasta>/clips/cenaN.mp4. Cena já gerada é pulada.
  montar -> junta as cenas (clipes de IA, gravações do dono ou a foto), aplica texto na
            tela, legenda da narração, aviso de IA e cartela final, e põe a narração.

Uso:
  FAL_KEY=... python3 gerar_video.py eu-tranquei-o-portao gerar
  python3 gerar_video.py eu-tranquei-o-portao montar [--saida video.mp4]

Arquivos opcionais na pasta do vídeo:
  cena7.mp4, cena8.mp4 ...  gravações reais (campo "gravado"); sem elas entra a foto
  narracao.mp3|.m4a|.wav    narração gravada; sem ela o vídeo sai mudo
"""
import argparse, base64, json, math, os, re, subprocess, sys, time, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).resolve().parent
REF = AQUI / "ref-maximiliano.jpg"
LOGO = AQUI / "logo-infinity-guard.jpg"

# Modelos do fal.ai (troque aqui se quiser outro modelo da mesma família)
MODELO_IMAGEM = "fal-ai/nano-banana/edit"
MODELO_VIDEO = "fal-ai/kling-video/v2.1/standard/image-to-video"
FAL = "https://queue.fal.run"

W, H, FPS = 1080, 1920, 30
NAVY, GOLD, WHITE, GREY = (10, 22, 44), (212, 170, 82), (245, 242, 235), (200, 205, 215)
F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


# ---------- fal.ai ----------

def fal(modelo, entrada):
    chave = os.environ.get("FAL_KEY")
    if not chave:
        sys.exit("Falta a variável FAL_KEY (chave da API do fal.ai).")
    cab = {"Authorization": f"Key {chave}", "Content-Type": "application/json"}
    req = urllib.request.Request(f"{FAL}/{modelo}", json.dumps(entrada).encode(), cab)
    fila = json.load(urllib.request.urlopen(req, timeout=60))
    while True:
        time.sleep(5)
        st = json.load(urllib.request.urlopen(urllib.request.Request(fila["status_url"], headers=cab), timeout=60))
        if st["status"] == "COMPLETED":
            break
        if st["status"] not in ("IN_QUEUE", "IN_PROGRESS"):
            sys.exit(f"{modelo} falhou: {st}")
    return json.load(urllib.request.urlopen(urllib.request.Request(fila["response_url"], headers=cab), timeout=60))


def data_uri(caminho):
    return "data:image/jpeg;base64," + base64.b64encode(Path(caminho).read_bytes()).decode()


def baixar(url, destino):
    urllib.request.urlretrieve(url, destino)


def gerar(pasta, roteiro):
    clips = pasta / "clips"
    clips.mkdir(exist_ok=True)
    for c in roteiro["cenas"]:
        if not c.get("ia") or "imagem" not in c:
            continue
        mp4 = clips / f"cena{c['id']}.mp4"
        if mp4.exists():
            print(f"cena {c['id']}: já existe, pulando")
            continue
        png = clips / f"cena{c['id']}.png"
        if not png.exists():
            print(f"cena {c['id']}: gerando imagem...")
            r = fal(MODELO_IMAGEM, {
                "prompt": f"{roteiro['identidade']} {c['imagem']}",
                "image_urls": [data_uri(REF)],
                "aspect_ratio": "9:16",
                "num_images": 1,
            })
            baixar(r["images"][0]["url"], png)
        dur = c["fim"] - c["inicio"]
        print(f"cena {c['id']}: animando ({'10' if dur > 5 else '5'} s)...")
        r = fal(MODELO_VIDEO, {
            "prompt": f"{c['movimento']} Mantenha o rosto idêntico ao da imagem, movimentos realistas.",
            "image_url": data_uri(png),
            "duration": "10" if dur > 5 else "5",
            "negative_prompt": "rosto diferente, deformação, texto, logotipo, legenda",
        })
        baixar(r["video"]["url"], mp4)
    print("Clipes prontos em", clips)


# ---------- montagem ----------

def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def duracao(arq):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                         capture_output=True, text=True).stdout
    return float(out.strip() or 0)


VF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1"


def trecho(c, pasta, tmp):
    """Gera tmp/sN.mp4 com a duração exata da cena, sem áudio."""
    dur = c["fim"] - c["inicio"]
    out = tmp / f"s{c['id']}.mp4"
    clip = pasta / "clips" / f"cena{c['id']}.mp4"
    gravado = pasta / c["gravado"] if c.get("gravado") else None
    if c.get("rebobinar"):
        base = pasta / "clips" / f"cena{c['rebobinar']}.mp4"
        if base.exists():
            ff("-sseof", f"-{dur * 2}", "-i", str(base), "-vf", f"{VF},reverse,setpts=0.5*PTS", "-t", str(dur), "-an", str(out))
            return out
    if gravado and gravado.exists():
        src = gravado
    elif clip.exists():
        src = clip
    else:
        src = None
    if src:
        # se o clipe for mais curto que a cena, desacelera para caber
        fator = max(1.0, dur / max(duracao(src), 0.1))
        ff("-i", str(src), "-vf", f"{VF},setpts={fator:.4f}*PTS", "-t", str(dur), "-an", str(out))
    else:
        # sem clipe: foto (ou logo na cartela) com zoom lento sobre fundo desfocado
        img = Image.open(LOGO if c.get("cartela") else REF).convert("RGB")
        if c.get("cartela"):
            fundo = Image.new("RGB", (W, H), NAVY)
            lg = img.crop((0, 440, 1080, 1520)).resize((900, 900))
            m = Image.new("L", lg.size, 0)
            ImageDraw.Draw(m).ellipse((10, 10, 890, 890), fill=255)
            fundo.paste(lg, (90, 420), m)
        else:
            img = img.crop((0, 0, img.width, int(img.height * 0.8)))
            fundo = img.resize((W, H)).filter(ImageFilter.GaussianBlur(40))
            fg = img.resize((900, int(900 * img.height / img.width)), Image.LANCZOS)
            fundo.paste(fg, ((W - fg.width) // 2, 220))
        still = tmp / f"s{c['id']}.png"
        fundo.save(still)
        z = 1 if c.get("cartela") else 1.06
        ff("-loop", "1", "-i", str(still), "-vf",
           f"scale={W*2}:{H*2},zoompan=z='1+({z}-1)*on/({dur}*{FPS})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur*FPS}:s={W}x{H}:fps={FPS}",
           "-t", str(dur), "-pix_fmt", "yuv420p", str(out))
    return out


def blocos(texto, dur, inicio):
    palavras, saida, cur = texto.split(), [], []
    for p in palavras:
        cur.append(p)
        if len(cur) >= 7 or (re.search(r"[.?!:]$", p) and len(cur) >= 3):
            saida.append(" ".join(cur)); cur = []
    if cur:
        saida.append(" ".join(cur))
    total, t, res = sum(map(len, saida)) or 1, inicio, []
    for s in saida:
        d = dur * len(s) / total
        res.append((t, t + d, s)); t += d
    return res


def overlay_frames(roteiro):
    fTela, fSub, fAviso = ImageFont.truetype(F_SERIF, 72), ImageFont.truetype(F_BOLD, 58), ImageFont.truetype(F_REG, 30)
    subs = []
    for c in roteiro["cenas"]:
        if c.get("fala"):
            subs += blocos(c["fala"], c["fim"] - c["inicio"] - 0.2, c["inicio"] + 0.1)

    def linhas(d, texto, f, maxw=960):
        out, cur = [], ""
        for w in texto.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: out.append(cur); cur = w
        return out + ([cur] if cur else [])

    def escrever(d, y, texto, f, cor, alpha=255):
        for ln in linhas(d, texto, f):
            w = d.textlength(ln, font=f)
            d.text(((W - w) / 2, y), ln, font=f, fill=cor + (alpha,), stroke_width=4, stroke_fill=(0, 0, 0, int(alpha * 0.85)))
            y += f.size + 14

    for i in range(roteiro["duracao"] * FPS):
        t = i / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = next((x for x in roteiro["cenas"] if x["inicio"] <= t < x["fim"]), roteiro["cenas"][-1])
        lt = t - c["inicio"]
        if c.get("cartela"):
            escrever(d, 1400, c["tela"], ImageFont.truetype(F_BOLD, 44), GOLD, int(255 * min(1, lt / 0.6)))
        else:
            if c.get("tela"):
                escrever(d, 260, c["tela"], fTela, GOLD, int(255 * min(1, lt / 0.4)))
            s = next((x for x in subs if x[0] <= t < x[1]), None)
            if s:
                escrever(d, 1420, s[2], fSub, WHITE)
            if c.get("ia"):
                d.text((40, H - 90), "Cena ilustrativa criada com IA", font=fAviso, fill=GREY + (230,),
                       stroke_width=2, stroke_fill=(0, 0, 0, 200))
        yield im.tobytes()


def montar(pasta, roteiro, saida):
    tmp = pasta / "tmp"
    tmp.mkdir(exist_ok=True)
    partes = [trecho(c, pasta, tmp) for c in roteiro["cenas"]]
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p.resolve()}'\n" for p in partes))
    base = tmp / "base.mp4"
    ff("-f", "concat", "-safe", "0", "-i", str(lista), "-vf", f"fps={FPS},format=yuv420p", "-an", str(base))

    narr = next((pasta / f"narracao{e}" for e in (".mp3", ".m4a", ".wav") if (pasta / f"narracao{e}").exists()), None)
    audio = ["-i", str(narr)] if narr else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(base),
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", *audio,
           "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]", "-map", "[v]", "-map", "2:a",
           "-t", str(roteiro["duracao"]), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(saida)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in overlay_frames(roteiro):
        p.stdin.write(fr)
    p.stdin.close()
    if p.wait():
        sys.exit("ffmpeg falhou na montagem")
    print("Vídeo pronto:", saida, "| narração:", narr.name if narr else "nenhuma (mudo)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("etapa", choices=["gerar", "montar", "tudo"])
    ap.add_argument("--saida")
    a = ap.parse_args()
    pasta = (AQUI / a.pasta) if not Path(a.pasta).is_absolute() else Path(a.pasta)
    roteiro = json.loads((pasta / "cenas.json").read_text())
    if a.etapa in ("gerar", "tudo"):
        gerar(pasta, roteiro)
    if a.etapa in ("montar", "tudo"):
        montar(pasta, roteiro, Path(a.saida) if a.saida else pasta / f"{pasta.name}.mp4")


if __name__ == "__main__":
    main()
