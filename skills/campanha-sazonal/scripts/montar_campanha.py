#!/usr/bin/env python3
"""Monta a campanha 11.11 e Black Friday da Infinity Guard: ofertas de kit, calendário e mensagens.

Uso:
  python3 montar_campanha.py                                   (os dois eventos, desconto proposto de 10%)
  python3 montar_campanha.py --evento blackfriday --desconto 0.12 --cupom IGBLACK
  python3 montar_campanha.py --custos custos.json --margem-minima 0.25
  python3 montar_campanha.py --prova ok                        (só depois que a prova-da-loja passar)
  ... --json | --saida campanhas/2026.md

--desconto  desconto do kit sobre a soma dos preços ATUAIS (o Pix de 10% da loja vem por cima, se a Nuvemshop somar).
--cupom     código que você criou (ou vai criar) na Nuvemshop. Sem ele, usa o sugerido e avisa para criar.
--custos    JSON {"kit-cam-2": 210.00, ...} com o seu custo por produto; checa a margem de cada kit.
--prova     ok | pendente. Pendente = sem anúncio pago (CNPJ e garantia ainda não estão no site).
"""
import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
OFERTAS = AQUI / "references" / "ofertas.json"
CATALOGOS = [AQUI.parent / "atendente-infinity-guard" / "references" / "catalogo.json",
             AQUI / "references" / "catalogo.json"]
PARCELA_MINIMA = 30.0
DESCONTO_MAXIMO = 0.25  # acima disso o script recusa: margem e cara de preço maquiado
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_catalogo(caminho=None):
    cam = Path(caminho) if caminho else next((c for c in CATALOGOS if c.exists()), None)
    if not cam:
        raise SystemExit("catálogo não encontrado: instale a skill atendente-infinity-guard ao lado desta")
    dados = json.loads(cam.read_text(encoding="utf-8"))
    dados["por_id"] = {p["id"]: p for p in dados["produtos"]}
    return dados


def carregar_ofertas():
    return json.loads(OFERTAS.read_text(encoding="utf-8"))


def precificar(kit, cat, desconto, custos=None, margem_minima=None):
    pid = cat["por_id"]
    curtos = carregar_ofertas().get("nomes_curtos", {})
    avisos = []
    itens = []
    for i, q in kit["itens"].items():
        p = pid.get(i)
        if not p:
            raise ValueError(f"{kit['id']}: produto {i} não está no catálogo")
        if not p.get("ativo"):
            avisos.append(f"{p['nome'].split(' — ')[0]} está esgotado: kit fora da campanha")
        itens.append((p, q))
    de = round(sum(p["preco"] * q for p, q in itens), 2)  # preço atual, nunca preco_de
    por = round(de * (1 - desconto), 2)
    pix = round(por * (1 - cat["condicoes"]["desconto_pix"]), 2)
    parcelas = min(cat["condicoes"]["parcelas_max"], max(1, int(por // PARCELA_MINIMA)))
    r = {"id": kit["id"], "nome": kit["nome"], "para": kit["para"], "gancho": kit["gancho"],
         "itens": [{"id": p["id"], "nome": curtos.get(p["id"], p["nome"].split(" — ")[0]), "qtd": q, "preco": p["preco"], "url": p["url"]}
                   for p, q in itens],
         "de": de, "por": por, "economia": round(de - por, 2), "pix": pix,
         "parcelas": parcelas, "parcela_valor": round(por / parcelas, 2), "ativo": not avisos, "avisos": avisos}
    if custos is not None:
        faltam = [p["id"] for p, _ in itens if p["id"] not in custos]
        if faltam:
            r["avisos"].append("sem custo para " + ", ".join(faltam) + ": margem não checada")
        else:
            custo = sum(custos[p["id"]] * q for p, q in itens)
            r["margem_pix"] = round((pix - custo) / pix, 3)
            if margem_minima is not None and r["margem_pix"] < margem_minima:
                r["avisos"].append(f"margem no Pix de {r['margem_pix']:.0%} abaixo do mínimo de {margem_minima:.0%}")
                r["ativo"] = False
    return r


def ofertas(cat, desconto, custos=None, margem_minima=None):
    if not 0 <= desconto <= DESCONTO_MAXIMO:
        raise ValueError(f"desconto deve ficar entre 0 e {DESCONTO_MAXIMO:.0%}")
    return [precificar(k, cat, desconto, custos, margem_minima) for k in carregar_ofertas()["kits"]]


def d(s):
    return date.fromisoformat(s)


def fmt(dia):
    return f"{dia:%d/%m} ({DIAS[dia.weekday()]})"


def mensagens(kits, cupom, nome_evento, link, artigo="o"):
    no, do = ("no", "do") if artigo == "o" else ("na", "da")
    ativos = [k for k in kits if k["ativo"]]
    principal = next((k for k in ativos if k["id"] == "kit-casa-vigiada"), ativos[0] if ativos else None)
    if not principal:
        return {}
    lista = "\n".join(f"• {k['nome']}: {brl(k['por'])} ou {brl(k['pix'])} no Pix ({k['parcelas']}x de {brl(k['parcela_valor'])})"
                      for k in ativos)
    c = f" com o cupom {cupom}" if cupom else ""
    sair = "Se não quiser mais receber, responda SAIR."
    return {
        "vip": ("Oi {nome}! Aqui é da Infinity Guard. " + no.capitalize() + " " + nome_evento + " vou separar kits montados pra cada tipo de casa, "
                "com preço especial e configuração segura acompanhada no WhatsApp. Quer entrar na lista e receber antes de todo mundo? "
                "É só responder SIM."),
        "abertura": (f"{{nome}}, começou {artigo} {nome_evento} da Infinity Guard{c}:\n{lista}\n"
                     f"Todos vão com o passo a passo de configuração segura e suporte aqui no WhatsApp. "
                     f"Quer que eu te ajude a ver qual serve pra sua casa? {link}\n{sair}"),
        "lembrete": (f"{{nome}}, pra casa que fica vazia durante o dia eu indico o {principal['nome']} ({principal['gancho']}): "
                     f"{brl(principal['pix'])} no Pix{c}. Me fala como é sua casa que eu confirmo se é o certo. {sair}"),
        "ultima": (f"{{nome}}, hoje é o último dia {do} {nome_evento}{c}. Depois de hoje os kits voltam ao preço normal. "
                   f"Se ficou alguma dúvida, me chama aqui. {link}\n{sair}"),
    }


def calendario(evento, ev, prova_ok):
    ini, fim = d(ev["inicio"]), d(ev["fim"])
    pago = "Anúncio pago (Máquina de Anúncios)" if prova_ok else "Só orgânico: anúncio pago bloqueado até a prova da loja passar"
    passos = []
    if evento == "1111":
        passos += [
            (date(2026, 10, 21), "Loja", "Prazo da auditoria da prova-da-loja (CNPJ, garantia com prazo, troca e prazo de entrega no site)"),
            (date(2026, 10, 28), "Loja", "Criar o cupom na Nuvemshop e congelar os preços atuais até 29/11 (sem subir preço antes da promoção)"),
            (date(2026, 11, 2), "Reels", "Reels de aquecimento: câmera invadida por senha de fábrica (Máquina de Reels, tema quente)"),
            (date(2026, 11, 4), "WhatsApp", "Mensagem VIP para quem já conversou com a loja (texto 'vip'); só manda o resto para quem disser SIM"),
            (date(2026, 11, 9), "Reels + Stories", "Mostrar os 4 kits e para que casa serve cada um; caixa de perguntas"),
            (date(2026, 11, 10), "WhatsApp", "Aviso à lista VIP: amanhã às 8h"),
        ]
    else:
        passos += [
            (date(2026, 11, 12), "WhatsApp", "Quem deixou carrinho no 11.11: sequência de carrinho da skill atendente"),
            (date(2026, 11, 16), "Reels", "Reels: o que olhar antes de comprar câmera na Black Friday (prazo de entrega, garantia, suporte)"),
            (date(2026, 11, 20), "WhatsApp", "Mensagem VIP de Black Friday (texto 'vip') para a base que respondeu no 11.11"),
            (date(2026, 11, 24), "Stories", "Esquenta: contagem regressiva e caixa de perguntas"),
        ]
    dia, n = ini, 0
    while dia <= fim:
        if dia == ini:
            passos += [(dia, "WhatsApp", "8h: texto 'abertura' para a lista VIP"),
                       (dia, "Site", "Banner do evento na home e cupom ativo; conferir preço dos kits no carrinho"),
                       (dia, "Reels + Stories", "Post de abertura com os kits"),
                       (dia, "Anúncio", pago)]
        elif dia == fim:
            passos += [(dia, "WhatsApp", "18h: texto 'ultima' para a lista VIP que ainda não comprou"),
                       (dia, "Stories", "Últimas horas")]
        else:
            passos += [(dia, "WhatsApp", "12h: texto 'lembrete' para quem respondeu e não comprou"),
                       (dia, "Stories", "Prova: unboxing e configuração segura na prática")]
        if ini == fim:
            passos += [(dia, "WhatsApp", "18h: texto 'ultima' só para quem respondeu a abertura e ainda não comprou")]
        dia += timedelta(days=1)
        n += 1
    passos.append((fim + timedelta(days=1), "WhatsApp", "Pós-venda dia 1 para cada compra (skill atendente, modo pós-venda); desativar cupom"))
    return [{"data": x.isoformat(), "quando": fmt(x), "canal": c, "acao": a} for x, c, a in sorted(passos, key=lambda p: p[0])]


def montar(eventos=("1111", "blackfriday"), desconto=0.10, cupom=None, custos=None, margem_minima=None,
           prova_ok=False, catalogo=None):
    cat = carregar_catalogo(catalogo)
    of = carregar_ofertas()
    kits = ofertas(cat, desconto, custos, margem_minima)
    avisos = []
    idade = (date.today() - d(cat["atualizado_em"])).days
    if idade > 30:
        avisos.append(f"catálogo com {idade} dias: reconfira os preços no site antes de lançar")
    if custos is None:
        avisos.append("sem custos informados: confirme a margem de cada kit antes de criar o cupom")
    if not prova_ok:
        avisos.append("prova da loja pendente (CNPJ, garantia): campanha só orgânica e WhatsApp; nada de anúncio pago")
    avisos.append("o cupom vale para o carrinho todo, não só para o kit: o kit é a forma de apresentar a oferta")
    avisos.append("confirme na Nuvemshop se o cupom soma com o desconto de 10% no Pix; se não somar, use o valor 'por' na comunicação")
    saida = {"gerado_em": date.today().isoformat(), "desconto": desconto, "prova_ok": prova_ok,
             "kits": kits, "eventos": [], "avisos": avisos + [a for k in kits for a in k["avisos"]]}
    for e in eventos:
        ev = of["eventos"][e]
        cod = cupom or ev["cupom_sugerido"]
        saida["eventos"].append({
            "id": e, "nome": ev["nome"], "inicio": ev["inicio"], "fim": ev["fim"], "fonte": ev["fonte"],
            "cupom": cod, "cupom_criado": bool(cupom),
            "calendario": calendario(e, ev, prova_ok),
            "mensagens": mensagens(kits, cod, ev["nome"], cat["site"], ev.get("artigo", "o")),
        })
    return saida


def para_md(c):
    L = [f"# Campanha 11.11 e Black Friday · Infinity Guard", "",
         f"Gerado em {c['gerado_em']} com os preços do catálogo. Desconto do kit: {c['desconto']:.0%} sobre a soma dos preços atuais.", ""]
    L += ["## Antes de lançar", ""] + [f"- ⚠️ {a}" for a in c["avisos"]] + [""]
    L += ["## Ofertas", "", "| Kit | Para quem | Itens | De (preço atual) | Por | Pix | Parcelas |", "|---|---|---|---|---|---|---|"]
    for k in c["kits"]:
        itens = " + ".join(f"{i['qtd']}× {i['nome']}" for i in k["itens"])
        st = "" if k["ativo"] else " (fora)"
        L.append(f"| {k['nome']}{st} | {k['para']} | {itens} | {brl(k['de'])} | {brl(k['por'])} | {brl(k['pix'])} | "
                 f"{k['parcelas']}x {brl(k['parcela_valor'])} |")
    L += ["", "Promessa de todos os kits: passo a passo de configuração segura e acompanhamento de 7 dias no WhatsApp. "
          "Sem instalação no local.", ""]
    for e in c["eventos"]:
        L += [f"## {e['nome']} · {e['inicio'][8:10]}/{e['inicio'][5:7]}" + (f" a {e['fim'][8:10]}/{e['fim'][5:7]}" if e["fim"] != e["inicio"] else ""), "",
              f"Fonte do tamanho do evento: {e['fonte']}.", "",
              f"Cupom: **{e['cupom']}**" + ("" if e["cupom_criado"] else " (sugestão: crie na Nuvemshop antes de mandar qualquer mensagem)"), "",
              "### Calendário", "", "| Quando | Canal | O que fazer |", "|---|---|---|"]
        L += [f"| {p['quando']} | {p['canal']} | {p['acao']} |" for p in e["calendario"]]
        L += ["", "### Mensagens de WhatsApp (troque {nome})", ""]
        for nome, txt in e["mensagens"].items():
            L += [f"**{nome}**", "```", txt, "```", ""]
    L += ["## Regras de envio", "",
          "- WhatsApp só para quem já conversou com a loja ou respondeu SIM. Mensagem em massa: no máximo 1 por dia por pessoa, nunca entre 21h e 8h. Responder quem puxou conversa não conta.",
          "- Quem responder SAIR sai da lista na hora (LGPD).",
          "- Não suba preço antes da campanha: o 'de' é o preço atual. Preço maquiado vira reclamação no Procon e no Reclame Aqui.",
          "- Anúncios e Reels: passe a tabela de ofertas para a Máquina de Anúncios e a Máquina de Reels."]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--evento", choices=["1111", "blackfriday", "ambos"], default="ambos")
    ap.add_argument("--desconto", type=float, default=0.10)
    ap.add_argument("--cupom")
    ap.add_argument("--custos")
    ap.add_argument("--margem-minima", type=float)
    ap.add_argument("--prova", choices=["ok", "pendente"], default="pendente")
    ap.add_argument("--catalogo")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args()
    evs = ("1111", "blackfriday") if a.evento == "ambos" else (a.evento,)
    custos = json.loads(Path(a.custos).read_text(encoding="utf-8")) if a.custos else None
    try:
        c = montar(evs, a.desconto, a.cupom, custos, a.margem_minima, a.prova == "ok", a.catalogo)
    except ValueError as e:
        sys.exit(f"erro: {e}")
    out = json.dumps(c, ensure_ascii=False, indent=2) if a.json else para_md(c)
    if a.saida:
        Path(a.saida).write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
