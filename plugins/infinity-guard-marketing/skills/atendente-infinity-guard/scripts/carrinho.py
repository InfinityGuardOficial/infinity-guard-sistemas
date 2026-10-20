#!/usr/bin/env python3
"""Gera a sequência de recuperação de carrinho abandonado (D0, D1, D3) para WhatsApp.

Uso:
  python3 carrinho.py --nome Ana --produto kit-cam-2 --link https://infinityguard.com.br/checkout/...
  python3 carrinho.py --nome Ana --produto alarme-ikerui --cupom VOLTEI5 --json

--produto  id do catálogo (references/catalogo.json). Sem --link, usa a página do produto.
--cupom    opcional; só use cupom que já existe na Nuvemshop.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recomendar_kit import brl, carregar_catalogo  # noqa: E402

DOR = {
    "camera": "ver quem chega, de qualquer lugar",
    "alarme": "saber na hora se alguém entrar na sua casa",
    "fechadura": "nunca mais se preocupar com chave perdida ou copiada",
    "complemento": "deixar a frente da casa sempre iluminada",
    "home_office": "deixar seu espaço de trabalho do jeito certo",
}


def sequencia(nome, produto_id, link=None, cupom=None):
    cat = carregar_catalogo()
    p = cat["por_id"].get(produto_id)
    if not p:
        raise ValueError(f"produto desconhecido: {produto_id}")
    link = link or p["url"]
    dor = DOR.get(p["categoria"], "ficar mais tranquilo")
    curto = p["nome"].split(" — ")[0]
    msgs = [
        {"quando": "30 a 60 minutos depois",
         "texto": f"Oi {nome}, aqui é da Infinity Guard. Vi que você separou o pedido ({curto}) e não finalizou. "
                  f"Ficou alguma dúvida? Posso te ajudar a ver se serve pra sua casa. "
                  f"Seu carrinho está aqui: {link}"},
        {"quando": "no dia seguinte",
         "texto": f"{nome}, {curto} sai por {brl(p['preco'])} ou {brl(p['pix'])} no Pix, "
                  f"em até {p['parcelas']}x sem juros e com frete grátis. "
                  f"E vai com o passo a passo pra configurar com segurança, com a gente te respondendo no WhatsApp. "
                  f"Quer que eu tire alguma dúvida antes? {link}"},
        {"quando": "3 dias depois (última)",
         "texto": (f"{nome}, última mensagem pra não te incomodar. "
                   + (f"Consegui o cupom {cupom} pra você finalizar hoje. " if cupom else "")
                   + f"Se ainda faz sentido {dor}, é só clicar: {link}. "
                   "Se mudou de ideia, tudo bem, é só me dizer que eu paro por aqui.")},
    ]
    return {"nome": nome, "produto": p["id"], "link": link, "mensagens": msgs,
            "regras": ["Só envie para quem deu o WhatsApp no checkout ou já conversou com a loja.",
                       "Pare a sequência se o cliente comprar, responder 'não' ou pedir para sair.",
                       "Não envie entre 21h e 8h."]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nome", required=True)
    ap.add_argument("--produto", required=True)
    ap.add_argument("--link")
    ap.add_argument("--cupom")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    s = sequencia(a.nome, a.produto, a.link, a.cupom)
    if a.json:
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return
    for i, m in enumerate(s["mensagens"], 1):
        print(f"Mensagem {i} ({m['quando']}):\n{m['texto']}\n")
    print("Regras: " + " ".join(s["regras"]))


if __name__ == "__main__":
    main()
