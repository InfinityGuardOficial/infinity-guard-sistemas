#!/usr/bin/env python3
"""Catálogo e preços da Infinity Guard: confere, atualiza e calcula margem no catalogo.json (fonte única
de preço de todas as skills, dentro da skill atendente-infinity-guard).

Uso:
  python3 catalogo.py validar                                   (confere Pix, parcelas, links, ids e idade)
  python3 catalogo.py atualizar --produto kit-cam-2 --preco 379.90 [--preco-de 413] [--ativo nao]
  python3 catalogo.py atualizar ... --gravar                    (sem --gravar só mostra o que mudaria)
  python3 catalogo.py margem --custos custos.json [--taxa 0.05] [--frete 0] [--minima 0.25]
  python3 catalogo.py estoque --estoque estoque.json [--minimo 3]
  ... --catalogo outro.json | --json

custos.json   {"kit-cam-2": 210.00, ...}  custo de compra por produto
estoque.json  {"kit-cam-2": 4, ...}       unidades em estoque
"""
import argparse
import json
import math
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
CATALOGOS = [AQUI.parent / "atendente-infinity-guard" / "references" / "catalogo.json",
             AQUI / "references" / "catalogo.json"]
PARCELA_MINIMA = 30.0
IDADE_MAXIMA = 30


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def caminho_catalogo(caminho=None):
    cam = Path(caminho) if caminho else next((c for c in CATALOGOS if c.exists()), None)
    if not cam:
        raise SystemExit("catálogo não encontrado: instale a skill atendente-infinity-guard ao lado desta")
    return cam


def carregar(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def derivados(preco, desconto_pix, parcelas_max):
    parcelas = max(1, min(parcelas_max, math.floor(preco / PARCELA_MINIMA)))
    return {"pix": round(preco * (1 - desconto_pix), 2), "parcelas": parcelas,
            "parcela_valor": round(preco / parcelas, 2)}


def validar(cat, hoje=None):
    hoje = hoje or date.today()
    erros, avisos = [], []
    cond = cat["condicoes"]
    ids = [p["id"] for p in cat["produtos"]]
    for dup in {i for i in ids if ids.count(i) > 1}:
        erros.append(f"id repetido: {dup}")
    for p in cat["produtos"]:
        esp = derivados(p["preco"], cond["desconto_pix"], cond["parcelas_max"])
        for campo, valor in esp.items():
            if abs(p[campo] - valor) > 0.011:
                erros.append(f"{p['id']}: {campo} = {p[campo]}, deveria ser {valor}")
        if not p["url"].startswith("https://"):
            erros.append(f"{p['id']}: link sem https")
        if p.get("preco_de") and p["preco_de"] < p["preco"]:
            erros.append(f"{p['id']}: preço 'de' menor que o preço atual")
        if p["preco"] <= 0:
            erros.append(f"{p['id']}: preço inválido")
    idade = (hoje - date.fromisoformat(cat["atualizado_em"])).days
    if idade > IDADE_MAXIMA:
        avisos.append(f"catálogo com {idade} dias: reconfira os preços no site")
    return {"ok": not erros, "erros": erros, "avisos": avisos, "produtos": len(ids),
            "ativos": sum(p["ativo"] for p in cat["produtos"]), "idade_dias": idade}


def atualizar(cat, pid, preco=None, preco_de=None, ativo=None, hoje=None):
    p = next((x for x in cat["produtos"] if x["id"] == pid), None)
    if not p:
        raise ValueError(f"produto '{pid}' não existe no catálogo")
    antes = {k: p[k] for k in ("preco", "preco_de", "pix", "parcelas", "parcela_valor", "ativo")}
    if preco is not None:
        if preco <= 0:
            raise ValueError("preço precisa ser positivo")
        p["preco"] = round(preco, 2)
        p.update(derivados(p["preco"], cat["condicoes"]["desconto_pix"], cat["condicoes"]["parcelas_max"]))
    if preco_de is not None:
        p["preco_de"] = round(preco_de, 2)
    if ativo is not None:
        p["ativo"] = ativo
    if p.get("preco_de") and p["preco_de"] < p["preco"]:
        raise ValueError("preço 'de' menor que o preço atual: corrija o --preco-de")
    cat["atualizado_em"] = (hoje or date.today()).isoformat()
    depois = {k: p[k] for k in antes}
    return {k: (antes[k], depois[k]) for k in antes if antes[k] != depois[k]}


def margens(cat, custos, taxa=0.0, frete=0.0, minima=None):
    linhas = []
    for p in cat["produtos"]:
        if not p["ativo"] or p["id"] not in custos:
            continue
        for forma, receita in (("cartão", p["preco"]), ("pix", p["pix"])):
            lucro = receita * (1 - taxa) - custos[p["id"]] - frete
            m = round(lucro / receita, 4)
            linhas.append({"id": p["id"], "forma": forma, "receita": receita, "lucro": round(lucro, 2), "margem": m,
                           "abaixo": minima is not None and m < minima})
    faltam = [p["id"] for p in cat["produtos"] if p["ativo"] and p["id"] not in custos]
    return {"linhas": linhas, "sem_custo": faltam}


def estoque_baixo(cat, estoque, minimo=3):
    alertas = []
    for p in cat["produtos"]:
        qtd = estoque.get(p["id"])
        if qtd is None:
            continue
        if qtd <= 0 and p["ativo"]:
            alertas.append({"id": p["id"], "qtd": qtd, "acao": "desativar no catálogo (--ativo nao) e no site"})
        elif 0 < qtd <= minimo:
            alertas.append({"id": p["id"], "qtd": qtd, "acao": "repor com o fornecedor"})
        elif qtd > 0 and not p["ativo"]:
            alertas.append({"id": p["id"], "qtd": qtd, "acao": "voltou ao estoque: reativar (--ativo sim)"})
    return alertas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalogo")
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="modo", required=True)
    sub.add_parser("validar")
    s = sub.add_parser("atualizar")
    s.add_argument("--produto", required=True)
    s.add_argument("--preco", type=float)
    s.add_argument("--preco-de", type=float)
    s.add_argument("--ativo", choices=["sim", "nao"])
    s.add_argument("--gravar", action="store_true")
    s = sub.add_parser("margem")
    s.add_argument("--custos", required=True)
    s.add_argument("--taxa", type=float, default=0.0, help="taxa do meio de pagamento (ex.: 0.05)")
    s.add_argument("--frete", type=float, default=0.0, help="frete pago pela loja por pedido")
    s.add_argument("--minima", type=float)
    s = sub.add_parser("estoque")
    s.add_argument("--estoque", required=True)
    s.add_argument("--minimo", type=int, default=3)
    a = ap.parse_args()
    cam = caminho_catalogo(a.catalogo)
    cat = carregar(cam)
    saida = lambda obj, texto: print(json.dumps(obj, ensure_ascii=False, indent=2) if a.json else texto)  # noqa: E731

    if a.modo == "validar":
        r = validar(cat)
        texto = [f"{'OK' if r['ok'] else 'COM ERROS'}: {r['produtos']} produtos, {r['ativos']} ativos, "
                 f"atualizado há {r['idade_dias']} dias"] + [f"❌ {e}" for e in r["erros"]] + [f"⚠️ {x}" for x in r["avisos"]]
        saida(r, "\n".join(texto))
    elif a.modo == "atualizar":
        ativo = None if a.ativo is None else a.ativo == "sim"
        mud = atualizar(cat, a.produto, a.preco, a.preco_de, ativo)
        texto = "\n".join(f"{k}: {antes} → {depois}" for k, (antes, depois) in mud.items()) or "nada mudou"
        if a.gravar:
            cam.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            texto += f"\nGravado em {cam}. Rode os testes das skills e exporte de novo o prompt do robô."
        else:
            texto += "\n(simulação: use --gravar para salvar)"
        saida(mud, texto)
    elif a.modo == "margem":
        r = margens(cat, json.loads(Path(a.custos).read_text(encoding="utf-8")), a.taxa, a.frete, a.minima)
        texto = [f"{'⚠️' if x['abaixo'] else '  '} {x['id']:<18} {x['forma']:<6} {brl(x['receita']):>12} "
                 f"lucro {brl(x['lucro']):>11}  margem {x['margem']:.1%}" for x in r["linhas"]]
        if r["sem_custo"]:
            texto.append("Sem custo informado: " + ", ".join(r["sem_custo"]))
        saida(r, "\n".join(texto))
    else:
        r = estoque_baixo(cat, json.loads(Path(a.estoque).read_text(encoding="utf-8")), a.minimo)
        saida(r, "\n".join(f"{x['id']}: {x['qtd']} un. → {x['acao']}" for x in r) or "Estoque ok.")


if __name__ == "__main__":
    main()
