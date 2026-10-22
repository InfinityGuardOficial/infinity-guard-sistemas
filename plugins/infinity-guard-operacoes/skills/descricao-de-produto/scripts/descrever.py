#!/usr/bin/env python3
"""Gera a página de produto da Infinity Guard para a Nuvemshop: título SEO, descrição curta, meta description
e o texto completo em HTML (para colar no editor) a partir do catálogo.

Uso:
  python3 descrever.py --produto kit-cam-2
  python3 descrever.py --produto alarme-ikerui --garantia "12 meses"
  python3 descrever.py --todos --saida paginas/          (um arquivo .html por produto ativo)
  ... --json

A página nunca cita Anatel nem código de homologação (dropshipping: o fornecedor não fornece os códigos).
--garantia só com documento do fornecedor. Sem ele, a página diz "Garantia em todos os produtos".
"""
import argparse
import html
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
CATEGORIAS = AQUI / "references" / "categorias.json"
CATALOGOS = [AQUI.parent / "atendente-infinity-guard" / "references" / "catalogo.json",
             AQUI / "references" / "catalogo.json"]
TITULO_MAX = 60
META_MAX = 155


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_catalogo(caminho=None):
    cam = Path(caminho) if caminho else next((c for c in CATALOGOS if c.exists()), None)
    if not cam:
        raise SystemExit("catálogo não encontrado: instale a skill atendente-infinity-guard ao lado desta")
    dados = json.loads(cam.read_text(encoding="utf-8"))
    dados["por_id"] = {p["id"]: p for p in dados["produtos"]}
    return dados


def cortar(texto, limite):
    if len(texto) <= limite:
        return texto
    corte = texto[:limite - 1].rsplit(" ", 1)[0].rstrip(" ,.—-")
    return corte + "…"


def titulo_seo(p):
    base = " ".join(p["nome"].split("—")[0].replace("Infinity Guard", "").split())
    extra = p["destaques"][0].capitalize() if p.get("destaques") else ""
    com_extra = f"{base} {extra}".strip()
    for t in (f"{com_extra} | Infinity Guard", f"{base} | Infinity Guard", com_extra, base):
        if len(t) <= TITULO_MAX:
            return t
    return cortar(base, TITULO_MAX)


def descrever(p, cat, cats, garantia=None):
    c = cats["categorias"].get(p["categoria"], cats["categorias"]["complemento"])
    pix = brl(p["pix"])
    parc = f" ou em até {p['parcelas']}x" if p["parcelas"] > 1 else ""
    preco = f"{pix} no Pix{parc}. Suporte no WhatsApp."
    nome = " ".join(p["nome"].split("—")[0].split())
    destaques = ", ".join(p.get("destaques", [])[:2])
    meta = f"{c['promessa']} {nome}" + (f": {destaques}" if destaques else "") + f". {preco}"
    if len(meta) > META_MAX:
        meta = cortar(f"{c['promessa']} {nome}. {preco}", META_MAX)
    compra = list(cats["compra_segura"])
    if garantia:
        compra[-1] = f"Garantia de {garantia}"
    pendencias = []
    if not garantia:
        pendencias.append("prazo de garantia por escrito do fornecedor")
    e = html.escape
    partes = [f"<h2>{e(c['promessa'])}</h2>",
              "<p><strong>Destaques:</strong> " + e(", ".join(p.get("destaques", []))) + ".</p>",
              "<h3>Para quem é</h3><ul>" + "".join(f"<li>{e(x)}</li>" for x in c["para_quem"]) + "</ul>",
              "<h3>Como funciona</h3><ul>" + "".join(f"<li>{e(x)}</li>" for x in c["como_funciona"]) + "</ul>"]
    if p.get("requisitos"):
        partes.append("<h3>Antes de comprar, confira</h3><ul>" + "".join(f"<li>{e(x)}</li>" for x in p["requisitos"]) + "</ul>")
    if p.get("unidades", 1) > 1:
        partes.append(f"<p>Este kit vem com <strong>{p['unidades']} unidades</strong>.</p>")
    partes.append("<h3>Compra segura Infinity Guard</h3><ul>" + "".join(f"<li>{e(x)}</li>" for x in compra) + "</ul>")
    partes.append(f"<p>Dúvida sobre qual escolher para a sua casa? Chame no WhatsApp {e(cat['whatsapp'])} "
                  "que a gente te ajuda a montar o kit certo.</p>")
    return {"id": p["id"], "titulo_seo": titulo_seo(p), "meta_description": meta,
            "descricao_curta": f"{c['promessa']} {pix} no Pix" + (f" ou em até {p['parcelas']}x de {brl(p['parcela_valor'])}." if p["parcelas"] > 1 else "."),
            "html": "\n".join(partes), "palavras_seo": c["palavras_seo"], "pendencias": pendencias}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--produto")
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--garantia")
    ap.add_argument("--catalogo")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args()
    cat = carregar_catalogo(a.catalogo)
    cats = json.loads(CATEGORIAS.read_text(encoding="utf-8"))
    if a.todos:
        alvo = [p for p in cat["produtos"] if p["ativo"]]
    elif a.produto in cat["por_id"]:
        alvo = [cat["por_id"][a.produto]]
    else:
        ap.error("use --produto <id do catálogo> ou --todos")
    for p in alvo:
        if not p["ativo"]:
            print(f"[para o dono] {p['id']} está inativo no catálogo")
        d = descrever(p, cat, cats, a.garantia)
        if a.json:
            texto = json.dumps(d, ensure_ascii=False, indent=2)
        else:
            texto = (f"TÍTULO SEO ({len(d['titulo_seo'])}): {d['titulo_seo']}\n"
                     f"META ({len(d['meta_description'])}): {d['meta_description']}\n"
                     f"DESCRIÇÃO CURTA: {d['descricao_curta']}\n\n--- HTML para o editor da Nuvemshop ---\n{d['html']}")
        if a.saida:
            Path(a.saida).mkdir(parents=True, exist_ok=True)
            (Path(a.saida) / f"{p['id']}.{'json' if a.json else 'html'}").write_text(
                (texto if a.json else d["html"]) + "\n", encoding="utf-8")
            print(f"{p['id']}: salvo")
        else:
            print(texto)
        for pend in d["pendencias"]:
            print(f"[para o dono] {p['id']}: falta {pend}")


if __name__ == "__main__":
    main()
