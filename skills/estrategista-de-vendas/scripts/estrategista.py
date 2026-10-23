#!/usr/bin/env python3
"""Estrategista de vendas da Infinity Guard: o método das marcas de luxo, adaptado a uma loja online honesta.

Uso:
  python3 estrategista.py precos                       (preço que não cai: riscados, Pix e escada de valor)
  python3 estrategista.py dossie --nome Ana --imovel casa --interesse camera [--orcamento 500]
  python3 estrategista.py calendario --nome Ana --produto kit-cam-2 --entrega 2026-10-30
  python3 estrategista.py escassez --produto alarme-ikerui --estoque 3 [--conferido 2026-10-23]
  python3 estrategista.py escassez --fim 2026-11-29     (prazo real de uma campanha)
  ... --json

Preço, Pix e parcela saem do catalogo.json da atendente-infinity-guard. Todo texto que pode ir para o
cliente passa pelo revisar.py do revisor-de-promessas e sai com o veredito. Nada é enviado: quem envia é o dono.
"""
import argparse
import importlib.util
import json
import sys
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
CATALOGOS = [AQUI.parent / "atendente-infinity-guard" / "references" / "catalogo.json",
             AQUI / "references" / "catalogo.json"]
REVISOR = AQUI.parent / "revisor-de-promessas" / "scripts" / "revisar.py"
SEGURANCA = ("camera", "alarme", "fechadura", "complemento")
RISCADO_MINIMO = 0.10   # abaixo disso o "de" parece maquiagem: melhor tirar e mostrar só o preço
ESTOQUE_REAL = 5        # só fala de estoque baixo com número conferido até este limite
DEGRAUS = [(150, "entrada"), (500, "essencial"), (1000, "completo"), (float("inf"), "assinatura")]
# Escolha curada: uma indicação principal e uma alternativa, como o vendedor de boutique (não o catálogo inteiro).
CURADORIA = {
    ("camera", "casa"): ("kit-cam-2", "cam-asecam-ptz"),
    ("camera", "apartamento"): ("cam-asecam-ptz", "kit-cam-2"),
    ("camera", "comercio"): ("kit-cam-2", "cam-asecam-ptz"),
    ("alarme", "casa"): ("alarme-ikerui", "sensor-presenca"),
    ("alarme", "apartamento"): ("alarme-ikerui", "kit-cam-2"),
    ("alarme", "comercio"): ("alarme-ikerui", "kit-cam-2"),
    ("fechadura", "casa"): ("fechadura-bio", "fechadura-facial"),
    ("fechadura", "apartamento"): ("fechadura-bio", "fechadura-facial"),
    ("fechadura", "comercio"): ("fechadura-facial", "fechadura-bio"),
}
POR_QUE = {
    "kit-cam-2": "duas câmeras para ver frente e fundo de casa pelo celular, com visão noturna",
    "cam-asecam-ptz": "uma câmera que gira e acompanha o movimento, boa para um cômodo ou uma sala grande",
    "alarme-ikerui": "sensores nas portas e janelas e aviso no celular, funcionando com Wi-Fi ou chip",
    "sensor-presenca": "acende a luz sozinho quando alguém se aproxima, um complemento simples",
    "fechadura-bio": "abre com a digital ou pelo app, sem chave para perder",
    "fechadura-facial": "abre pelo rosto, pela digital ou pelo app, a mais completa da loja",
}
IMOVEL = {"casa": "sua casa", "apartamento": "seu apartamento", "comercio": "seu comércio"}
NOME_CURTO = {"kit-cam-2": "Kit com 2 Câmeras Wi-Fi", "cam-asecam-ptz": "Câmera ASECAM que gira",
              "alarme-ikerui": "Alarme IKerui", "fechadura-bio": "Fechadura com digital",
              "fechadura-facial": "Fechadura facial 3D", "sensor-presenca": "Sensor de presença"}
PERGUNTAS = {
    "camera": "tem Wi-Fi e tomada perto de onde a câmera vai ficar? Quais lugares você quer ver? "
              "E você quer só olhar pelo celular ou também gravar?",
    "alarme": "quantas portas e janelas dão para fora? No lugar tem Wi-Fi, ou prefere usar um chip de celular? "
              "E quem vai receber os avisos no celular?",
    "fechadura": "a porta é de madeira ou de metal, e qual a espessura dela? Quantas pessoas vão usar? "
                 "E você prefere abrir com a digital, pelo rosto ou pelo app?",
}


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def curto(p):
    return NOME_CURTO.get(p["id"], p["nome"].split(" — ")[0])


def carregar_catalogo(caminho=None):
    cam = Path(caminho) if caminho else next((c for c in CATALOGOS if c.exists()), None)
    if not cam:
        raise SystemExit("catálogo não encontrado: instale a skill atendente-infinity-guard ao lado desta")
    dados = json.loads(cam.read_text(encoding="utf-8"))
    dados["por_id"] = {p["id"]: p for p in dados["produtos"]}
    return dados


def _revisor():
    if not REVISOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("ig_revisar", REVISOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def revisar(texto):
    """Veredito do revisor-de-promessas para um texto que pode ir ao cliente."""
    rv = _revisor()
    if not rv:
        return {"veredito": "SEM REVISOR", "achados": []}
    return rv.revisar(texto, rv.carregar_regras())


def degrau(preco):
    return next(nome for limite, nome in DEGRAUS if preco < limite)


# ---------- 1. Preço que não cai ----------

def diagnostico_precos(cat):
    itens, acoes = [], []
    for p in cat["produtos"]:
        if p["categoria"] not in SEGURANCA or not p.get("ativo"):
            continue
        de = p.get("preco_de")
        corte = round(1 - p["preco"] / de, 3) if de else 0.0
        if not de:
            leitura = "ok: preço limpo, sem riscado"
        elif corte < RISCADO_MINIMO:
            leitura = f"tirar o riscado: {corte:.0%} de diferença parece maquiagem e ensina o cliente a esperar desconto"
            acoes.append(f"{p['id']}: mostrar só {brl(p['preco'])} (Pix {brl(p['pix'])}); tirar o 'de' {brl(de)}")
        else:
            leitura = f"riscado de {corte:.0%}: só mantenha se {brl(de)} foi o preço praticado de verdade antes"
            acoes.append(f"{p['id']}: confirmar com o histórico da Nuvemshop que {brl(de)} foi praticado; sem prova, tirar")
        itens.append({"id": p["id"], "nome": p["nome"], "preco": p["preco"], "preco_de": de, "corte": corte,
                      "pix": p["pix"], "parcelas": p["parcelas"], "parcela_valor": p["parcela_valor"],
                      "degrau": degrau(p["preco"]), "leitura": leitura})
    itens.sort(key=lambda i: i["preco"])
    regras = [
        "O preço não cai no meio do ano. A única condição fixa é o Pix com "
        f"{cat['condicoes']['desconto_pix']:.0%} (é forma de pagamento, não liquidação).",
        "Campanha (11.11, Black Friday) dá mais valor, não preço menor: kit montado, brinde de complemento "
        "ou acesso antecipado para a lista Primeira Fila. O 'de' da campanha é a soma dos preços atuais (campanha-sazonal).",
        "Reajuste é anunciado antes, com data: quem comprou antes fica feliz, e quem esperou entende que esperar não compensa.",
    ]
    return {"atualizado_em": cat.get("atualizado_em"), "itens": itens, "acoes": acoes, "regras": regras}


def precos_md(d):
    L = [f"# Preço que não cai · catálogo de {d['atualizado_em']}", "",
         "| Degrau | Produto | Preço | Pix | Parcelas | Leitura |", "|---|---|---|---|---|---|"]
    for i in d["itens"]:
        L.append(f"| {i['degrau']} | {i['id']} | {brl(i['preco'])} | {brl(i['pix'])} | "
                 f"{i['parcelas']}x {brl(i['parcela_valor'])} | {i['leitura']} |")
    L += ["", "## O que fazer (o dono decide e muda na Nuvemshop)"] + [f"- {a}" for a in d["acoes"] or ["Nada a mudar."]]
    L += ["", "## Regras do preço"] + [f"- {r}" for r in d["regras"]]
    return "\n".join(L)


# ---------- 2. Dossiê de atendimento (clienteling) ----------

def dossie(nome, imovel, interesse, cat, orcamento=None):
    if (interesse, imovel) not in CURADORIA:
        raise ValueError(f"combinação não prevista: interesse={interesse}, imovel={imovel}")
    principal, alternativa = (cat["por_id"][i] for i in CURADORIA[(interesse, imovel)])
    if not principal.get("ativo") or not alternativa.get("ativo"):
        raise ValueError("produto da curadoria inativo no catálogo: confira com o gestor-de-catalogo")
    if orcamento and principal["preco"] > orcamento and alternativa["preco"] <= orcamento:
        principal, alternativa = alternativa, principal
    lugar = IMOVEL[imovel]
    c = cat["condicoes"]

    def oferta(p):
        return (f"{curto(p)}: {POR_QUE.get(p['id'], ', '.join(p['destaques']))}. "
                f"{brl(p['preco'])} em até {p['parcelas']}x de {brl(p['parcela_valor'])}, ou {brl(p['pix'])} no Pix.")

    etapas = [
        ("Acolhida", f"Oi, {nome}! Aqui é da Infinity Guard. Que bom falar com você. "
                     f"Me conta um pouco sobre {lugar}: o que você quer ver ou proteger primeiro?"),
        ("Diagnóstico", "Para eu indicar certo, só três perguntas: " + PERGUNTAS[interesse]),
        ("Indicação curada", f"Pelo que você contou, eu indicaria uma coisa só: {oferta(principal)}"),
        ("Alternativa", f"Se fizer mais sentido para você, tem também: {oferta(alternativa)}"),
        ("Transparência", f"O manual de instruções acompanha o produto, e a gente tira suas dúvidas aqui no WhatsApp. "
                          f"O prazo é de {cat['prazo_padrao']} e o rastreio vai por e-mail. "
                          "Se não gostar, você tem 7 dias depois de receber para devolver, com o valor de volta."),
        ("Fechamento sem pressão", "Quer que eu te mande o link do produto para você ver com calma? "
                                   "Fico por aqui se surgir qualquer dúvida."),
    ]
    texto = "\n".join(t for _, t in etapas)
    ficha = {"nome": nome, "imovel": imovel, "interesse": interesse, "indicado": principal["id"],
             "alternativa": alternativa["id"], "orcamento": orcamento, "proximo_passo": "mandar o link e anotar a data"}
    return {"etapas": etapas, "ficha": ficha, "revisao": revisar(texto),
            "links": [principal["url"], alternativa["url"]], "prazo": c["prazo_entrega"]}


def dossie_md(d):
    f = d["ficha"]
    L = [f"# Dossiê de atendimento · {f['nome']}", "",
         f"Imóvel: {f['imovel']} · Interesse: {f['interesse']} · Indicado: `{f['indicado']}` · Alternativa: `{f['alternativa']}`", ""]
    for i, (etapa, txt) in enumerate(d["etapas"], 1):
        L += [f"**{i}. {etapa}**", "", f"> {txt}", ""]
    L += ["Links: " + " · ".join(d["links"]), "",
          f"Revisor de promessas: **{d['revisao']['veredito']}**",
          "", "[para o dono] Mande uma etapa por vez e espere a resposta. Anote a ficha no livro de clientes."]
    return "\n".join(L)


# ---------- 3. Calendário de relacionamento (pós-venda e comunidade) ----------

def calendario(nome, produto_id, cat, entrega=None):
    p = cat["por_id"].get(produto_id)
    if not p:
        raise ValueError(f"produto '{produto_id}' não existe no catálogo")
    nome_p = curto(p)
    complemento = "sensor-presenca" if p["categoria"] != "complemento" else None
    extra = cat["por_id"].get(complemento) if complemento else None
    passos = [
        (0, "Boas-vindas", f"Oi, {nome}! Seu pedido chegou. Que bom ter você com a gente. O manual de instruções está "
                           "na caixa; se surgir alguma dúvida, é só me chamar aqui."),
        (2, "Primeiros dias", f"{nome}, tudo certo com a sua compra ({nome_p})? Se tiver alguma dúvida de uso, estou por aqui."),
        (6, "Antes do fim dos 7 dias", f"{nome}, passando para saber se está tudo como você esperava. "
                                       "Se algo não estiver bom, me conta: você ainda está no prazo de 7 dias para trocar ou devolver."),
        (30, "Um mês", f"{nome}, um mês desde a sua compra ({nome_p})! Uma dica: revise de vez em quando quem tem acesso ao app "
                       "e mantenha o aplicativo atualizado. Se puder, conte como foi sua experiência na avaliação da loja."),
        (80, "Garantia legal", f"{nome}, um lembrete: a garantia legal (CDC) vale até 90 dias depois da entrega. "
                               "Se notou qualquer defeito, me avisa antes disso."),
        (180, "Seis meses", f"{nome}, seis meses desde a sua compra ({nome_p})! Você entrou na lista Primeira Fila: "
                            "nas próximas campanhas, você fica sabendo antes de todo mundo."
                            + (f" Se quiser completar, o {curto(extra)} sai por {brl(extra['preco'])}."
                               if extra and extra.get("ativo") else "")),
        (365, "Um ano", f"{nome}, faz um ano que você está com a gente. Obrigado pela confiança. "
                        "Se alguém da família ou um amigo precisar, pode passar meu contato."),
    ]
    base = date.fromisoformat(entrega) if entrega else None
    itens = [{"dia": d, "data": (base + timedelta(days=d)).isoformat() if base else f"entrega + {d} dias",
              "etapa": e, "mensagem": m} for d, e, m in passos]
    return {"nome": nome, "produto": produto_id, "itens": itens,
            "revisao": revisar("\n".join(i["mensagem"] for i in itens))}


def calendario_md(c):
    L = [f"# Calendário de relacionamento · {c['nome']} ({c['produto']})", "", "| Data | Etapa | Mensagem |", "|---|---|---|"]
    L += [f"| {i['data']} | {i['etapa']} | {i['mensagem']} |" for i in c["itens"]]
    L += ["", f"Revisor de promessas: **{c['revisao']['veredito']}**",
          "", "[para o dono] Quem envia é você. Pare a sequência se o cliente pedir, e nunca mande mais de uma por semana."]
    return "\n".join(L)


# ---------- 4. Escassez honesta ----------

def escassez(cat, produto_id=None, estoque=None, conferido=None, fim=None):
    """Só devolve frase de escassez quando o dado é real (estoque conferido ou data de campanha)."""
    if fim:
        d = date.fromisoformat(fim)
        frase = f"Condição válida até {d.strftime('%d/%m')}."
        return {"permitido": True, "frase": frase, "motivo": "prazo real de campanha", "revisao": revisar(frase)}
    if produto_id and estoque is not None:
        p = cat["por_id"].get(produto_id)
        if not p:
            raise ValueError(f"produto '{produto_id}' não existe no catálogo")
        if 0 < estoque <= ESTOQUE_REAL and conferido:
            dia = date.fromisoformat(conferido).strftime("%d/%m")
            frase = f"Restam {estoque} unidades deste lote do {curto(p)} (estoque conferido em {dia})."
            return {"permitido": True, "frase": frase, "motivo": "estoque real conferido", "revisao": revisar(frase)}
        motivo = "sem data de conferência do estoque" if not conferido else f"estoque {estoque} não é baixo"
        return {"permitido": False, "frase": None, "motivo": motivo,
                "alternativa": "Use exclusividade de acesso, não escassez: 'quem está na lista Primeira Fila fica "
                               "sabendo das campanhas antes'."}
    return {"permitido": False, "frase": None, "motivo": "sem estoque conferido nem prazo de campanha",
            "alternativa": "Venda pela escolha certa e pela tranquilidade, não pela pressa."}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modo", choices=["precos", "dossie", "calendario", "escassez"])
    ap.add_argument("--nome", default="cliente")
    ap.add_argument("--imovel", choices=sorted(IMOVEL), default="casa")
    ap.add_argument("--interesse", choices=["camera", "alarme", "fechadura"], default="camera")
    ap.add_argument("--orcamento", type=float)
    ap.add_argument("--produto")
    ap.add_argument("--entrega", help="data em que o pedido foi entregue (AAAA-MM-DD)")
    ap.add_argument("--estoque", type=int)
    ap.add_argument("--conferido", help="data em que o estoque foi conferido com o fornecedor (AAAA-MM-DD)")
    ap.add_argument("--fim", help="último dia real da campanha (AAAA-MM-DD)")
    ap.add_argument("--catalogo")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cat = carregar_catalogo(a.catalogo)
    try:
        if a.modo == "precos":
            r = diagnostico_precos(cat)
            md = precos_md(r)
        elif a.modo == "dossie":
            r = dossie(a.nome, a.imovel, a.interesse, cat, a.orcamento)
            md = dossie_md(r)
        elif a.modo == "calendario":
            r = calendario(a.nome, a.produto or "kit-cam-2", cat, a.entrega)
            md = calendario_md(r)
        else:
            r = escassez(cat, a.produto, a.estoque, a.conferido, a.fim)
            md = (f"Pode usar: \"{r['frase']}\" ({r['motivo']})" if r["permitido"]
                  else f"Não use escassez: {r['motivo']}. {r['alternativa']}")
    except ValueError as e:
        raise SystemExit(str(e))
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str) if a.json else md)


if __name__ == "__main__":
    main()
