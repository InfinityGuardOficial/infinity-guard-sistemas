#!/usr/bin/env python3
"""Proposta comercial Infinity Guard para comércio, escritório, condomínio ou compra em quantidade.

Uso:
  python3 proposta.py --cliente "Padaria do Zé" --tipo comercio --itens kit-cam-2:2,alarme-ikerui:1
  python3 proposta.py ... --desconto 0.05 --validade 7 --contato "Zé (31) 9...." --saida propostas/padaria.md
  python3 proposta.py ... --custos custos.json --margem-minima 0.25
  python3 proposta.py --listar          (produtos ativos e ids)
  ... --json

--itens     id:quantidade separados por vírgula (ids do catalogo.json da atendente-infinity-guard).
--desconto  sobre o preço atual (padrão 0). Acima de 15% o script recusa. Sem --custos, avisa para conferir margem.
--validade  dias de validade da proposta (padrão 7: o catálogo muda).
"""
import argparse
import json
import math
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
CATALOGOS = [AQUI.parent / "atendente-infinity-guard" / "references" / "catalogo.json",
             AQUI / "references" / "catalogo.json"]
DESCONTO_MAXIMO = 0.15
PARCELA_MINIMA = 30.0
LIMITE_DONO = 3000.0  # acima disso o dono revisa antes de enviar (regra da atendente)
TIPOS = {"comercio": "seu comércio", "escritorio": "seu escritório", "condominio": "o condomínio",
         "home_office": "seu home office", "residencia": "sua casa"}


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_catalogo(caminho=None):
    cam = Path(caminho) if caminho else next((c for c in CATALOGOS if c.exists()), None)
    if not cam:
        raise SystemExit("catálogo não encontrado: instale a skill atendente-infinity-guard ao lado desta")
    dados = json.loads(cam.read_text(encoding="utf-8"))
    dados["por_id"] = {p["id"]: p for p in dados["produtos"]}
    return dados


def ler_itens(texto):
    itens = {}
    for parte in filter(None, (p.strip() for p in texto.split(","))):
        pid, _, qtd = parte.partition(":")
        itens[pid.strip()] = itens.get(pid.strip(), 0) + int(qtd or 1)
    return itens


def montar(cliente, tipo, itens, cat, desconto=0.0, validade=7, custos=None, margem_minima=None, hoje=None):
    if not 0 <= desconto <= DESCONTO_MAXIMO:
        raise ValueError(f"desconto fora do limite (0 a {DESCONTO_MAXIMO:.0%})")
    hoje = hoje or date.today()
    linhas, avisos, total_cheio, custo_total = [], [], 0.0, 0.0
    for pid, qtd in itens.items():
        p = cat["por_id"].get(pid)
        if not p:
            raise ValueError(f"produto '{pid}' não existe no catálogo")
        if not p["ativo"]:
            raise ValueError(f"produto '{pid}' está inativo (esgotado ou fora da loja)")
        if qtd < 1:
            raise ValueError(f"quantidade inválida para {pid}")
        sub = round(p["preco"] * qtd, 2)
        total_cheio += sub
        linhas.append({"id": pid, "nome": p["nome"], "qtd": qtd, "unitario": p["preco"], "subtotal": sub,
                       "url": p["url"]})
        if custos is not None:
            if pid not in custos:
                avisos.append(f"sem custo informado para {pid}: margem não conferida")
            else:
                custo_total += custos[pid] * qtd
    total_cheio = round(total_cheio, 2)
    total = round(total_cheio * (1 - desconto), 2)
    pix = round(total * (1 - cat["condicoes"]["desconto_pix"]), 2)
    parcelas = max(1, min(cat["condicoes"]["parcelas_max"], math.floor(total / PARCELA_MINIMA)))
    margem = None
    if custos is not None and custo_total:
        margem = round((total - custo_total) / total, 4)
        if margem_minima is not None and margem < margem_minima:
            avisos.append(f"margem de {margem:.1%} abaixo da mínima de {margem_minima:.0%}: reduza o desconto")
    if desconto and custos is None:
        avisos.append("desconto sem custos informados: confira a margem antes de enviar")
    if total > LIMITE_DONO:
        avisos.append(f"proposta acima de {brl(LIMITE_DONO)}: o dono revisa antes de enviar")
    idade = (hoje - date.fromisoformat(cat["atualizado_em"])).days
    if idade > 30:
        avisos.append(f"catálogo com {idade} dias: reconfira os preços no site antes de enviar")
    return {"cliente": cliente, "tipo": tipo, "data": hoje.isoformat(),
            "valida_ate": (hoje + timedelta(days=validade)).isoformat(), "itens": linhas,
            "total_cheio": total_cheio, "desconto": desconto, "total": total, "pix": pix,
            "parcelas": parcelas, "parcela_valor": round(total / parcelas, 2), "margem": margem,
            "avisos": avisos, "loja": cat["loja"], "whatsapp": cat["whatsapp"], "site": cat["site"],
            "condicoes": cat["condicoes"]}


def para_md(p, contato=None):
    d = lambda s: date.fromisoformat(s).strftime("%d/%m/%Y")  # noqa: E731
    lugar = TIPOS.get(p["tipo"], "seu espaço")
    out = [f"# Proposta {p['loja']} para {p['cliente']}", "",
           f"**Segurança onde você estiver.** Proposta de {d(p['data'])}, válida até {d(p['valida_ate'])}."]
    if contato:
        out.append(f"Para: {contato}")
    out += ["", f"## O que vai proteger {lugar}", "", "| Produto | Qtd | Unitário | Subtotal |", "|---|---|---|---|"]
    out += [f"| [{i['nome']}]({i['url']}) | {i['qtd']} | {brl(i['unitario'])} | {brl(i['subtotal'])} |" for i in p["itens"]]
    out += ["", "## Investimento", ""]
    if p["desconto"]:
        out.append(f"- Total pelos preços da loja: {brl(p['total_cheio'])}")
        out.append(f"- Condição desta proposta ({p['desconto']:.0%} de desconto): **{brl(p['total'])}**")
    else:
        out.append(f"- Total: **{brl(p['total'])}**")
    out += [f"- No Pix: **{brl(p['pix'])}**", f"- Ou em até {p['parcelas']}x de {brl(p['parcela_valor'])} no cartão",
            "", "## O que está incluso", "",
            "- Guia de configuração segura (rede 2,4 GHz, troca da senha de fábrica, atualização).",
            "- Acompanhamento de 7 dias no WhatsApp depois da entrega e suporte que responde.",
            f"- Troca em 7 dias e {p['condicoes']['garantia'].split('(')[0].strip().lower()}.",
            "", "## O que não está incluso", "",
            "- Instalação no local (a loja envia o passo a passo e acompanha pelo WhatsApp).",
            "- Plano de nuvem do aplicativo e cartão de memória, se não estiverem na tabela.",
            "- Frete e prazo: calculados pelo CEP no site no momento do pedido.",
            "", "## Próximo passo", "",
            f"Responda \"aprovado\" no WhatsApp {p['whatsapp']} que a gente gera o link de pagamento. {p['site']}"]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cliente")
    ap.add_argument("--tipo", default="comercio", choices=list(TIPOS))
    ap.add_argument("--itens")
    ap.add_argument("--desconto", type=float, default=0.0)
    ap.add_argument("--validade", type=int, default=7)
    ap.add_argument("--contato")
    ap.add_argument("--custos")
    ap.add_argument("--margem-minima", type=float)
    ap.add_argument("--catalogo")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args()
    cat = carregar_catalogo(a.catalogo)
    if a.listar:
        for p in cat["produtos"]:
            if p["ativo"]:
                print(f"{p['id']:<18} {brl(p['preco']):>12}  {p['nome'][:70]}")
        return
    if not (a.cliente and a.itens):
        ap.error("informe --cliente e --itens (ou use --listar)")
    custos = json.loads(Path(a.custos).read_text(encoding="utf-8")) if a.custos else None
    p = montar(a.cliente, a.tipo, ler_itens(a.itens), cat, a.desconto, a.validade, custos, a.margem_minima)
    texto = json.dumps(p, ensure_ascii=False, indent=2) if a.json else para_md(p, a.contato)
    if a.saida:
        Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(a.saida).write_text(texto + "\n", encoding="utf-8")
        print(f"Proposta salva em {a.saida}")
    else:
        print(texto)
    for av in p["avisos"]:
        print(f"[para o dono] {av}")


if __name__ == "__main__":
    main()
