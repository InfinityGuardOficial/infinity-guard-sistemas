#!/usr/bin/env python3
"""Revisa um texto da Infinity Guard (anúncio, post, roteiro, mensagem de WhatsApp, página) antes de publicar.

Uso:
  python3 revisar.py --arquivo anuncio.md
  python3 revisar.py --texto "Câmera 100% segura, instalação grátis!"
  cat roteiro.md | python3 revisar.py
  ... --json             (saída em JSON)
  ... --estrito          (sai com código 1 se houver algo que bloqueia; bom para conferir em lote)
  ... --liberar garantia-sem-prazo-documentado   (regra já resolvida: por exemplo, prazo documentado e publicado no site)

Cada achado traz a linha, o trecho, a gravidade (bloqueia | ajustar), o porquê e como reescrever.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REGRAS = Path(__file__).resolve().parent.parent / "references" / "regras.json"
NEGACAO = re.compile(r"\b(n[aã]o|nunca|sem|nem|jamais|evite|proibido)\b", re.IGNORECASE)
JANELA = 60  # caracteres antes e depois do trecho onde uma negação muda o sentido


def carregar_regras(caminho=REGRAS, liberar=()):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    regras = [r for r in dados["regras"] if r["id"] not in set(liberar)]
    for r in regras:
        r["re"] = re.compile(r["padrao"], re.IGNORECASE)
    return regras


def negado(linha, ini, fim, titulo):
    """A promessa aparece negada ("não vendemos instalação", seção "O que não está incluso") ou é a pergunta do cliente?"""
    if linha.rstrip(' *"\'').endswith("?"):
        return True
    return bool(NEGACAO.search(linha[max(0, ini - JANELA):ini]) or NEGACAO.search(linha[fim:fim + JANELA])
                or NEGACAO.search(titulo))


def revisar(texto, regras):
    achados, titulo = [], ""
    for n, linha in enumerate(texto.splitlines(), 1):
        if linha.lstrip().startswith("#"):
            titulo = linha
        for r in regras:
            for m in r["re"].finditer(linha):
                a = {"linha": n, "trecho": m.group(0), "regra": r["id"], "gravidade": r["gravidade"],
                     "porque": r["porque"], "reescrever": r["reescrever"]}
                if r["gravidade"] == "bloqueia" and negado(linha, m.start(), m.end(), titulo):
                    a["gravidade"] = "ajustar"
                    a["porque"] = "Parece negação ou pergunta do cliente; confira se fica claro que a loja não promete isso. " + r["porque"]
                achados.append(a)
    ordem = {"bloqueia": 0, "ajustar": 1}
    achados.sort(key=lambda a: (ordem[a["gravidade"]], a["linha"]))
    bloqueia = sum(a["gravidade"] == "bloqueia" for a in achados)
    veredito = "BLOQUEADO" if bloqueia else ("AJUSTAR" if achados else "LIBERADO")
    return {"veredito": veredito, "bloqueia": bloqueia, "ajustar": len(achados) - bloqueia, "achados": achados}


def para_texto(res):
    linhas = [f"Veredito: {res['veredito']} ({res['bloqueia']} bloqueia, {res['ajustar']} ajustar)"]
    if not res["achados"]:
        linhas.append("Nenhuma promessa arriscada encontrada. Ainda assim confira preço e link com o catálogo.")
    for a in res["achados"]:
        marca = "❌" if a["gravidade"] == "bloqueia" else "⚠️"
        linhas += [f"\n{marca} linha {a['linha']}: \"{a['trecho']}\" [{a['regra']}]",
                   f"   Por quê: {a['porque']}", f"   Reescreva: {a['reescrever']}"]
    return "\n".join(linhas)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arquivo")
    ap.add_argument("--texto")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--estrito", action="store_true")
    ap.add_argument("--liberar", action="append", default=[], help="id de regra já resolvida (pode repetir)")
    a = ap.parse_args()
    if a.texto is not None:
        texto = a.texto
    elif a.arquivo:
        texto = Path(a.arquivo).read_text(encoding="utf-8")
    else:
        texto = sys.stdin.read()
    res = revisar(texto, carregar_regras(liberar=a.liberar))
    print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else para_texto(res))
    if a.estrito and res["bloqueia"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
