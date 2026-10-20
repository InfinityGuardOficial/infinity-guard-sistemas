#!/usr/bin/env python3
"""Monta o kit Infinity Guard certo para a casa do cliente, sempre com os preços do catálogo.

Uso:
  python3 recomendar_kit.py --imovel casa --pontos 3 --wifi sim --viaja sim --porta digital --orcamento 1500 --nome Ana
  python3 recomendar_kit.py ... --json        (saída em JSON, para robôs e planilhas)

--imovel   apartamento | casa | sitio | comercio | home_office
--pontos   quantos lugares quer ver (portão, garagem, sala, quintal...). Padrão por tipo de imóvel.
--wifi     sim | nao       (tem Wi-Fi chegando nos pontos?)
--viaja    sim | nao       (a casa fica vazia por dias / trabalha fora o dia todo?)
--porta    nao | digital | facial   (quer fechadura inteligente?)
--orcamento  valor em reais que o cliente quer gastar (opcional; comparado com o total no Pix)
"""
import argparse
import json
import math
from pathlib import Path

CATALOGO = Path(__file__).resolve().parent.parent / "references" / "catalogo.json"
PARCELA_MINIMA = 30.0  # regra observada na vitrine em 18/10/2026
ROTULO = {"apartamento": "o seu apartamento", "casa": "a sua casa", "sitio": "o seu sítio",
          "comercio": "o seu comércio", "home_office": "o seu home office"}
PONTOS_PADRAO = {"apartamento": 2, "casa": 2, "sitio": 3, "comercio": 2, "home_office": 1}


def carregar_catalogo(caminho=CATALOGO):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    dados["por_id"] = {p["id"]: p for p in dados["produtos"]}
    return dados


def brl(valor):
    s = f"{valor:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def totais(itens, desconto_pix):
    total = round(sum(p["preco"] * q for p, q in itens), 2)
    if len(itens) == 1 and itens[0][1] == 1:
        pix = itens[0][0]["pix"]
    else:
        pix = math.floor(total * (1 - desconto_pix) * 100 + 0.5) / 100
    parcelas = max(1, min(12, int(total // PARCELA_MINIMA)))
    return {"total": total, "pix": pix, "parcelas": parcelas, "parcela_valor": round(total / parcelas, 2)}


def montar_ideal(cat, imovel, pontos, wifi, viaja, porta):
    p = cat["por_id"]
    itens, motivos, avisos = [], [], []

    if wifi:
        resto = pontos
        if pontos >= 3 and imovel in ("casa", "sitio", "comercio"):
            itens.append((p["cam-asecam-ptz"], 1))
            motivos.append("Câmera ASECAM com rastreamento para a área aberta (quintal, garagem ou pátio): ela gira e segue o movimento.")
            resto -= 1
        kits = max(1, math.ceil(resto / 2))
        itens.append((p["kit-cam-2"], kits))
        qtd = "1 kit" if kits == 1 else f"{kits} kits"
        motivos.append(f"{qtd} com 2 câmeras dupla lente para {kits * 2} pontos: entradas e áreas internas, com visão noturna.")
    else:
        avisos.append("As câmeras da loja precisam de Wi-Fi no local. Sem Wi-Fi, o alarme com chip GSM é a proteção que funciona.")

    if viaja or imovel == "sitio" or not wifi or (imovel == "casa" and pontos >= 3):
        itens.append((p["alarme-ikerui"], 1))
        motivos.append("Alarme IKerui com sensores: avisa no celular na hora que alguém abre porta ou janela, mesmo com a casa vazia (funciona com Wi-Fi ou chip).")

    if porta == "facial":
        itens.append((p["fechadura-facial"], 1))
        motivos.append("Fechadura facial 3D: abre com o rosto, sem chave para perder ou copiar.")
    elif porta == "digital":
        itens.append((p["fechadura-bio"], 1))
        motivos.append("Fechadura com digital e app: cada pessoa da casa entra com o dedo, e você libera visita pelo celular.")
    if porta in ("facial", "digital"):
        avisos.append("Fechadura: confirmar a espessura e o tipo da porta antes de fechar o pedido.")

    if imovel in ("casa", "sitio"):
        itens.append((p["sensor-presenca"], 1))
        motivos.append("Sensor de presença: acende a luz da frente sozinho quando alguém chega. Ladrão não gosta de luz.")

    avisos.append("Cartão de memória está esgotado; não oferecer até voltar ao estoque.")
    return itens, motivos, avisos


def caber_no_orcamento(cat, itens, orcamento):
    """Corta itens na ordem de menor impacto na segurança até o total no Pix caber no orçamento."""
    p = cat["por_id"]
    d = cat["condicoes"]["desconto_pix"]
    atual = [list(x) for x in itens]
    cortes = []

    def ids():
        return [x[0]["id"] for x in atual]

    def tirar(pid, frase):
        nonlocal atual
        if pid in ids():
            atual = [x for x in atual if x[0]["id"] != pid]
            cortes.append(frase)

    passos = [
        lambda: _trocar(atual, "fechadura-facial", p["fechadura-bio"], cortes,
                        "Troquei a fechadura facial pela de digital, que custa menos."),
        lambda: tirar("sensor-presenca", "Tirei o sensor de presença."),
        lambda: tirar("fechadura-bio", "Deixei a fechadura para uma segunda compra."),
        lambda: tirar("cam-asecam-ptz", "Tirei a câmera com rastreamento; o kit de 2 cobre o principal."),
        lambda: _reduzir_kits(atual, cortes),
        lambda: tirar("alarme-ikerui", "Deixei o alarme para uma segunda compra.") if "kit-cam-2" in ids() else None,
    ]
    for passo in passos:
        if totais([tuple(x) for x in atual], d)["pix"] <= orcamento or not atual:
            break
        passo()
    final = [tuple(x) for x in atual]
    cabe = bool(final) and totais(final, d)["pix"] <= orcamento
    return final, cortes, cabe


def _trocar(atual, de_id, para, cortes, frase):
    for x in atual:
        if x[0]["id"] == de_id:
            x[0] = para
            cortes.append(frase)
            return


def _reduzir_kits(atual, cortes):
    for x in atual:
        if x[0]["id"] == "kit-cam-2" and x[1] > 1:
            x[1] = 1
            cortes.append("Reduzi para 1 kit de 2 câmeras, nos pontos mais importantes.")
            return


def recomendar(imovel, pontos=None, wifi=True, viaja=False, porta="nao", orcamento=None, nome=None, catalogo=CATALOGO):
    cat = carregar_catalogo(catalogo)
    if imovel not in PONTOS_PADRAO:
        raise ValueError(f"imovel deve ser um de {sorted(PONTOS_PADRAO)}")
    if porta not in ("nao", "digital", "facial"):
        raise ValueError("porta deve ser nao, digital ou facial")
    pontos = pontos or PONTOS_PADRAO[imovel]
    d = cat["condicoes"]["desconto_pix"]
    itens, motivos, avisos = montar_ideal(cat, imovel, pontos, wifi, viaja, porta)
    res = {
        "nome": nome, "imovel": imovel, "pontos": pontos, "wifi": wifi, "viaja": viaja, "porta": porta,
        "ideal": {"itens": [_item(p, q) for p, q in itens], **totais(itens, d)},
        "motivos": motivos, "avisos": avisos, "orcamento": orcamento, "versao_orcamento": None,
        "catalogo_atualizado_em": cat["atualizado_em"],
    }
    if orcamento is not None and res["ideal"]["pix"] > orcamento:
        final, cortes, cabe = caber_no_orcamento(cat, itens, orcamento)
        res["versao_orcamento"] = {"itens": [_item(p, q) for p, q in final], **(totais(final, d) if final else {}),
                                   "cortes": cortes, "cabe": cabe}
    return res


def _item(p, q):
    return {"id": p["id"], "nome": p["nome"], "qtd": q, "preco_unit": p["preco"], "url": p["url"]}


def _bloco(titulo, versao):
    linhas = [f"*{titulo}*"]
    for it in versao["itens"]:
        q = f"{it['qtd']}x " if it["qtd"] > 1 else ""
        linhas.append(f"• {q}{it['nome']} ({brl(it['preco_unit'])})\n  {it['url']}")
    linhas.append(f"Total: {brl(versao['total'])} ou *{brl(versao['pix'])} no Pix* "
                  f"ou {versao['parcelas']}x de {brl(versao['parcela_valor'])} sem juros")
    return "\n".join(linhas)


def mensagem(res):
    nome = res["nome"] or ""
    abre = f"{nome}, " if nome else ""
    partes = [f"{abre}com o que você me contou, montei a proteção certa para {ROTULO[res['imovel']]}:"]
    partes.append(_bloco("Kit indicado", res["ideal"]))
    partes.append("Por que cada item:\n" + "\n".join(f"- {m}" for m in res["motivos"]))
    vo = res["versao_orcamento"]
    if vo:
        if vo["cabe"]:
            partes.append(_bloco(f"Versão que cabe nos {brl(res['orcamento'])}", vo))
            partes.append("O que ajustei: " + " ".join(vo["cortes"]))
        else:
            partes.append(f"Com {brl(res['orcamento'])} no Pix ainda não fecha nem o essencial. "
                          "Dá para parcelar sem juros, ou começar por um item só e completar depois.")
    if not res["wifi"]:
        partes.append(res["avisos"][0])
    tem_camera = any(i["id"].startswith(("kit-cam", "cam-")) for i in res["ideal"]["itens"])
    if tem_camera:
        partes.append("E aqui tem uma diferença: quando a câmera chegar, eu configuro com você por vídeo no WhatsApp, "
                      "trocando a senha de fábrica e deixando tudo seguro, e te acompanho nos primeiros 7 dias.")
    else:
        partes.append("E você não fica sozinho: quando chegar, eu te passo a configuração por vídeo no WhatsApp "
                      "e te acompanho nos primeiros 7 dias.")
    partes.append("Quer que eu separe esse kit para você?")
    return "\n\n".join(partes)


def _simnao(v):
    return str(v).strip().lower() in ("sim", "s", "yes", "y", "1", "true")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--imovel", required=True)
    ap.add_argument("--pontos", type=int)
    ap.add_argument("--wifi", default="sim")
    ap.add_argument("--viaja", default="nao")
    ap.add_argument("--porta", default="nao")
    ap.add_argument("--orcamento", type=float)
    ap.add_argument("--nome")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = recomendar(a.imovel, a.pontos, _simnao(a.wifi), _simnao(a.viaja), a.porta, a.orcamento, a.nome)
    print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else mensagem(res))


if __name__ == "__main__":
    main()
