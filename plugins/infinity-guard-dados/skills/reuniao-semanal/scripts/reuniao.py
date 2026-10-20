#!/usr/bin/env python3
"""Reunião semanal da Infinity Guard: lê o estado de todas as skills instaladas ao lado e monta a pauta
da semana por squad, com as prioridades em ordem.

Uso:
  python3 reuniao.py                           (pauta da semana de hoje)
  python3 reuniao.py --hoje 2026-11-02         (simular outra data)
  python3 reuniao.py --saida reunioes/$(date +%F).md
  ... --json

Nada aqui inventa número: cada linha diz de qual arquivo saiu. O que o script não consegue ler
(vendas da semana, conversas) entra como "trazer para a reunião".
"""
import argparse
import json
import re
from datetime import date
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent.parent
SQUADS = ["Direção", "Vendas", "Sucesso do Cliente", "Marketing e Conteúdo", "Tráfego Pago", "Operações e Loja",
          "Dados e Inteligência"]


def ler_json(caminho):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def arquivos_datados(pasta, padrao=r"(\d{4}-\d{2}-\d{2})"):
    datas = []
    for f in Path(pasta).glob("*") if Path(pasta).exists() else []:
        m = re.search(padrao, f.name)
        if m:
            datas.append((date.fromisoformat(m.group(1)), f))
    return sorted(datas)


def coletar(hoje, base=SKILLS):
    itens = []  # (prioridade 1-3, squad, texto, fonte)
    add = lambda pr, sq, tx, fo: itens.append({"prioridade": pr, "squad": sq, "texto": tx, "fonte": fo})  # noqa: E731

    cat = ler_json(base / "atendente-infinity-guard" / "references" / "catalogo.json")
    if not cat:
        add(1, "Operações e Loja", "Catálogo não encontrado: instalar a skill atendente-infinity-guard.", "-")
    else:
        idade = (hoje - date.fromisoformat(cat["atualizado_em"])).days
        if idade > 30:
            add(1, "Operações e Loja", f"Catálogo com {idade} dias: reconferir preços no site (catalogo-e-precos validar).",
                "catalogo.json")
        cond = cat.get("condicoes", {})
        if "NÃO informar código" in cond.get("anatel", ""):
            add(1, "Operações e Loja", "Código Anatel ainda não publicado: cobrar do fornecedor e conferir no portal.",
                "catalogo.json → condicoes.anatel")
        if "NÃO prometer prazo" in cond.get("garantia", ""):
            add(1, "Operações e Loja", "Prazo de garantia sem documento do fornecedor: pedir por escrito.",
                "catalogo.json → condicoes.garantia")

    ofertas = ler_json(base / "campanha-sazonal" / "references" / "ofertas.json")
    for ev in (ofertas or {}).get("eventos", {}).values():
        ini, fim = date.fromisoformat(ev["inicio"]), date.fromisoformat(ev["fim"])
        faltam = (ini - hoje).days
        if 0 <= faltam <= 30:
            pr = 1 if faltam <= 14 else 2
            add(pr, "Marketing e Conteúdo", f"{ev['nome']} em {faltam} dias ({ini:%d/%m}): campanha montada, cupom "
                f"{ev.get('cupom_sugerido', '')} criado na Nuvemshop e lista VIP avisada?", "ofertas.json")
            add(pr, "Tráfego Pago", f"{ev['nome']} em {faltam} dias: plano de mídia com margem e portão de prova.",
                "ofertas.json")
        elif ini <= hoje <= fim:
            add(1, "Vendas", f"{ev['nome']} acontecendo agora: atendente no WhatsApp em minutos, carrinho com cupom.",
                "ofertas.json")
        elif 0 < (hoje - fim).days <= 10:
            add(2, "Sucesso do Cliente", f"Depois do {ev['nome']}: pós-venda de 7 dias e pedido de avaliação dos compradores.",
                "ofertas.json")

    auds = arquivos_datados(base / "prova-da-loja" / "auditorias")
    if not auds:
        add(1, "Operações e Loja", "Nenhuma auditoria de prova da loja: rodar prova-da-loja.", "auditorias/")
    else:
        d, f = auds[-1]
        txt = f.read_text(encoding="utf-8")
        m = re.search(r"Nota de prova: (\d+) de (\d+)", txt)
        nota = f" (nota {m.group(1)} de {m.group(2)})" if m else ""
        if (hoje - d).days > 14:
            add(2, "Operações e Loja", f"Última auditoria em {d:%d/%m}{nota}: refazer e comparar.", f.name)
        elif m and int(m.group(1)) < int(m.group(2)):
            add(2, "Operações e Loja", f"Auditoria de {d:%d/%m}{nota}: seguir a lista de correção em ordem.", f.name)
        if m and int(m.group(1)) < 4:
            add(1, "Tráfego Pago", f"Prova da loja {m.group(1)} de {m.group(2)}: sem público frio até CNPJ, Anatel e garantia.",
                f.name)

    hist = ler_json(base / "conteudo-semanal" / "pautas" / "historico.json") or {}
    ultima = max((date.fromisoformat(k) for k in hist), default=None)
    if not ultima or (hoje - ultima).days >= 7:
        add(2, "Marketing e Conteúdo", "Pauta da semana não registrada: rodar conteudo-semanal --registrar.",
            "pautas/historico.json")
    temas = ler_json(base / "conteudo-semanal" / "references" / "temas.json")
    if temas and (hoje - date.fromisoformat(temas["atualizado_em"])).days > 45:
        add(3, "Dados e Inteligência", "Banco de temas com mais de 45 dias: rodar o Detetive de Nicho e renovar.",
            "temas.json")

    radar = ler_json(base / "radar-de-concorrentes" / "references" / "concorrentes.json")
    if radar:
        velhas = sum((hoje - date.fromisoformat(l["data"])).days > 30 for l in radar["leituras"])
        if velhas:
            add(3, "Dados e Inteligência", f"{velhas} leituras de concorrente com mais de 30 dias: refazer o radar.",
                "concorrentes.json")

    paineis = arquivos_datados(base / "painel-de-vendas" / "paineis")
    if not paineis or (hoje - paineis[-1][0]).days > 7:
        add(2, "Dados e Inteligência", "Painel da semana: exportar o CSV de pedidos da Nuvemshop e rodar painel-de-vendas.",
            "paineis/")

    add(2, "Vendas", "Trazer: conversas da semana, kits indicados, carrinhos recuperados (conversas.csv).", "-")
    add(3, "Sucesso do Cliente", "Trazer: chamados de suporte e trocas da semana; problema novo vira entrada em problemas.json.", "-")
    add(3, "Direção", "Decidir as 3 prioridades da semana e quem (qual funcionário) cuida de cada uma.", "-")
    itens.sort(key=lambda i: (i["prioridade"], SQUADS.index(i["squad"])))
    return itens


def para_md(itens, hoje):
    out = [f"# Reunião semanal Infinity Guard · {hoje:%d/%m/%Y}", "",
           "## Top 3 da semana", ""]
    out += [f"{n}. **{i['squad']}:** {i['texto']}" for n, i in enumerate(itens[:3], 1)]
    for sq in SQUADS:
        do_squad = [i for i in itens if i["squad"] == sq]
        if do_squad:
            out += ["", f"## {sq}", ""]
            out += [f"- [{'P' + str(i['prioridade'])}] {i['texto']} _(fonte: {i['fonte']})_" for i in do_squad]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hoje")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args()
    hoje = date.fromisoformat(a.hoje) if a.hoje else date.today()
    itens = coletar(hoje)
    texto = json.dumps(itens, ensure_ascii=False, indent=2) if a.json else para_md(itens, hoje)
    if a.saida:
        Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(a.saida).write_text(texto + "\n", encoding="utf-8")
        print(f"Pauta salva em {a.saida}")
    else:
        print(texto)


if __name__ == "__main__":
    main()
