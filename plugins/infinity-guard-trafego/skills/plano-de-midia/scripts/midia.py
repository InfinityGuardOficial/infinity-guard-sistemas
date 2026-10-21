#!/usr/bin/env python3
"""Plano de mídia e régua de decisão do tráfego pago da Infinity Guard (Meta Ads).

Uso:
  python3 midia.py plano --ticket 1100 --margem 0.35 --meta-vendas 20 --dias 30 [--prova pendente|ok]
  python3 midia.py plano --kit kit-casa-vigiada --margem 0.35 --orcamento-dia 40
  python3 midia.py avaliar --resultados resultados.csv --ticket 1100 --margem 0.35
  ... --json

plano    calcula o CPA máximo (quanto pode custar uma venda sem prejuízo), o CPA alvo, o ROAS de equilíbrio,
         o orçamento para a meta (ou a meta que cabe no orçamento) e a divisão frio/morno/quente.
avaliar  lê o CSV exportado do Gerenciador (colunas: conjunto;gasto;compras;receita, aceita ; ou , e 1.234,56)
         e diz, por conjunto, ESCALAR, MANTER, OBSERVAR ou PAUSAR pela régua abaixo.

--margem  margem bruta por venda (preço menos custo do produto, frete e taxas), de 0 a 1. Sem ela não há plano.
--prova   pendente (padrão) = CNPJ e garantia ainda não estão no site: o plano sai só com remarketing
          e WhatsApp (sem público frio), como manda a skill prova-da-loja.
"""
import argparse
import csv
import json
import math
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
OFERTAS = AQUI.parent / "campanha-sazonal" / "references" / "ofertas.json"
CATALOGOS = [AQUI.parent / "atendente-infinity-guard" / "references" / "catalogo.json"]
ALVO_DO_MAXIMO = 0.6       # CPA alvo = 60% do máximo: sobra lucro depois do anúncio
GASTO_SEM_VENDA = 2.0      # pausar conjunto que gastou 2x o CPA máximo sem venda
ESCALA = 0.2               # escalar 20% por vez, no máximo a cada 3 dias
DIVISAO = {"frio": 0.6, "morno": 0.25, "quente": 0.15}
DIVISAO_SEM_PROVA = {"frio": 0.0, "morno": 0.4, "quente": 0.6}
ORCAMENTO_MINIMO_DIA = 6.0  # abaixo disso o conjunto não sai da fase de aprendizado


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def ticket_do_kit(kit_id):
    ofertas = json.loads(OFERTAS.read_text(encoding="utf-8"))
    cat = json.loads(next(c for c in CATALOGOS if c.exists()).read_text(encoding="utf-8"))
    precos = {p["id"]: p["preco"] for p in cat["produtos"]}
    kit = next((k for k in ofertas["kits"] if k["id"] == kit_id), None)
    if not kit:
        raise ValueError(f"kit '{kit_id}' não está em ofertas.json")
    return round(sum(precos[i] * q for i, q in kit["itens"].items()), 2)


def plano(ticket, margem, meta_vendas=None, dias=30, orcamento_dia=None, prova_ok=False):
    if not 0 < margem < 1:
        raise ValueError("margem precisa estar entre 0 e 1 (ex.: 0.35)")
    if ticket <= 0:
        raise ValueError("ticket precisa ser positivo")
    cpa_max = round(ticket * margem, 2)
    cpa_alvo = round(cpa_max * ALVO_DO_MAXIMO, 2)
    roas_eq = round(1 / margem, 2)
    roas_alvo = round(ticket / cpa_alvo, 2)
    avisos = []
    if orcamento_dia:
        total = round(orcamento_dia * dias, 2)
        vendas = math.floor(total / cpa_alvo)
    else:
        meta_vendas = meta_vendas or 20
        total = round(meta_vendas * cpa_alvo, 2)
        orcamento_dia = round(total / dias, 2)
        vendas = meta_vendas
    divisao = DIVISAO if prova_ok else DIVISAO_SEM_PROVA
    if not prova_ok:
        avisos.append("prova da loja pendente: sem público frio; só remarketing (quem visitou o site, engajou ou "
                      "chamou no WhatsApp) até CNPJ e garantia estarem no site")
    por_funil = {k: round(orcamento_dia * v, 2) for k, v in divisao.items() if v}
    for etapa, valor in por_funil.items():
        if valor < ORCAMENTO_MINIMO_DIA:
            avisos.append(f"{etapa}: {brl(valor)}/dia é pouco para sair do aprendizado; junte etapas ou aumente o orçamento")
    avisos.append("as vendas esperadas assumem que o CPA alvo será atingido; nos primeiros 7 dias o número real manda")
    return {"ticket": ticket, "margem": margem, "cpa_maximo": cpa_max, "cpa_alvo": cpa_alvo,
            "roas_equilibrio": roas_eq, "roas_alvo": roas_alvo, "dias": dias, "orcamento_dia": orcamento_dia,
            "orcamento_total": total, "vendas_esperadas": vendas, "por_funil_dia": por_funil, "avisos": avisos,
            "regua": {"pausar": f"gastou {GASTO_SEM_VENDA:.0f}x o CPA máximo ({brl(cpa_max * GASTO_SEM_VENDA)}) sem venda, "
                                f"ou CPA acima do máximo ({brl(cpa_max)}) depois de 3 vendas",
                      "escalar": f"CPA abaixo do alvo ({brl(cpa_alvo)}) com 3 vendas ou mais: +{ESCALA:.0%} no orçamento, "
                                 "no máximo a cada 3 dias",
                      "manter": "CPA entre o alvo e o máximo",
                      "observar": "menos de 3 vendas e ainda não gastou o limite de pausa"}}


def numero(txt):
    txt = (txt or "0").strip().replace("R$", "").replace(" ", "")
    if "," in txt or re.fullmatch(r"\d{1,3}(\.\d{3})+", txt):
        txt = txt.replace(".", "").replace(",", ".")
    return float(txt or 0)


def ler_resultados(caminho):
    bruto = Path(caminho).read_text(encoding="utf-8-sig")
    sep = ";" if bruto.count(";") >= bruto.count(",") else ","
    linhas = list(csv.DictReader(bruto.splitlines(), delimiter=sep))
    norm = lambda d: {k.strip().lower(): v for k, v in d.items()}  # noqa: E731
    return [{"conjunto": r["conjunto"], "gasto": numero(r["gasto"]), "compras": int(numero(r["compras"])),
             "receita": numero(r.get("receita"))} for r in map(norm, linhas)]


def avaliar(resultados, ticket, margem):
    p = plano(ticket, margem, prova_ok=True)
    cpa_max, cpa_alvo = p["cpa_maximo"], p["cpa_alvo"]
    saida = []
    for r in resultados:
        cpa = round(r["gasto"] / r["compras"], 2) if r["compras"] else None
        roas = round(r["receita"] / r["gasto"], 2) if r["gasto"] else None
        if r["compras"] == 0:
            decisao = "PAUSAR" if r["gasto"] >= cpa_max * GASTO_SEM_VENDA else "OBSERVAR"
        elif r["compras"] < 3:
            decisao = "PAUSAR" if cpa > cpa_max * GASTO_SEM_VENDA else "OBSERVAR"
        elif cpa > cpa_max:
            decisao = "PAUSAR"
        elif cpa <= cpa_alvo:
            decisao = "ESCALAR"
        else:
            decisao = "MANTER"
        saida.append({**r, "cpa": cpa, "roas": roas, "decisao": decisao})
    return {"cpa_maximo": cpa_max, "cpa_alvo": cpa_alvo, "conjuntos": saida}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="modo", required=True)
    for nome in ("plano", "avaliar"):
        s = sub.add_parser(nome)
        g = s.add_mutually_exclusive_group(required=True)
        g.add_argument("--ticket", type=float)
        g.add_argument("--kit")
        s.add_argument("--margem", type=float, required=True)
        s.add_argument("--json", action="store_true")
    sub.choices["plano"].add_argument("--meta-vendas", type=int)
    sub.choices["plano"].add_argument("--dias", type=int, default=30)
    sub.choices["plano"].add_argument("--orcamento-dia", type=float)
    sub.choices["plano"].add_argument("--prova", choices=["pendente", "ok"], default="pendente")
    sub.choices["avaliar"].add_argument("--resultados", required=True)
    a = ap.parse_args()
    ticket = a.ticket if a.ticket else ticket_do_kit(a.kit)

    if a.modo == "plano":
        r = plano(ticket, a.margem, a.meta_vendas, a.dias, a.orcamento_dia, a.prova == "ok")
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
            return
        print(f"Ticket {brl(r['ticket'])} · margem {r['margem']:.0%}\n"
              f"CPA máximo (empata): {brl(r['cpa_maximo'])} · CPA alvo: {brl(r['cpa_alvo'])}\n"
              f"ROAS de equilíbrio: {r['roas_equilibrio']} · ROAS alvo: {r['roas_alvo']}\n"
              f"Orçamento: {brl(r['orcamento_dia'])}/dia por {r['dias']} dias = {brl(r['orcamento_total'])} "
              f"→ {r['vendas_esperadas']} vendas no CPA alvo")
        print("Divisão por dia: " + ", ".join(f"{k} {brl(v)}" for k, v in r["por_funil_dia"].items()))
        print("\nRégua:\n" + "\n".join(f"- {k.upper()}: {v}" for k, v in r["regua"].items()))
        for av in r["avisos"]:
            print(f"[para o dono] {av}")
    else:
        r = avaliar(ler_resultados(a.resultados), ticket, a.margem)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
            return
        print(f"CPA máximo {brl(r['cpa_maximo'])} · alvo {brl(r['cpa_alvo'])}\n")
        for c in r["conjuntos"]:
            cpa = brl(c["cpa"]) if c["cpa"] else "sem venda"
            print(f"{c['decisao']:<9} {c['conjunto']}: gasto {brl(c['gasto'])}, {c['compras']} compras, CPA {cpa}, ROAS {c['roas']}")


if __name__ == "__main__":
    main()
