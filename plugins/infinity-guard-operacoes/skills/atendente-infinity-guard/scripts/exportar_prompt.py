#!/usr/bin/env python3
"""Gera o prompt de sistema do atendente para colar num robô de WhatsApp com IA
(app de WhatsApp da Nuvemshop, OmniChat, ou qualquer plataforma que aceite instruções em texto).

Uso:
  python3 exportar_prompt.py > prompt-atendente.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recomendar_kit import brl, carregar_catalogo  # noqa: E402

REF = Path(__file__).resolve().parent.parent / "references"


def tabela_produtos(cat):
    linhas = []
    for p in cat["produtos"]:
        if not p["ativo"]:
            linhas.append(f"- [ESGOTADO, não oferecer] {p['nome']}")
            continue
        linhas.append(f"- {p['nome']}: {brl(p['preco'])} | Pix {brl(p['pix'])} | "
                      f"até {p['parcelas']}x de {brl(p['parcela_valor'])} | {p['url']}")
    return "\n".join(linhas)


def regras_kit():
    return """Como montar o kit (siga sempre, não calcule de outro jeito):
- Câmeras só se houver Wi-Fi no local. Kit de 2 câmeras cobre 2 pontos; use quantos kits forem precisos.
- Casa, sítio ou comércio com 3 pontos ou mais: 1 câmera ASECAM com rastreamento para a área aberta e kits de 2 para o resto.
- Alarme IKerui quando a casa fica vazia (trabalho/viagem), em sítio, sem Wi-Fi (funciona com chip) ou em casa com 3+ pontos.
- Fechadura só se o cliente quiser: digital (mais barata) ou facial 3D. Confirmar espessura e tipo da porta.
- Casa ou sítio: oferecer o sensor de presença para a luz da frente.
- Itens de home office só como complemento quando o cliente trabalha em casa.
- Pix = preço com 10% de desconto. Parcelas sem juros com parcela mínima de cerca de R$ 30, até 12x; confirmar no checkout.
- Se passar do orçamento: troque fechadura facial pela digital, depois tire sensor, fechadura, câmera com rastreamento, reduza para 1 kit e por último o alarme."""


def montar(cat=None):
    cat = cat or carregar_catalogo()
    c = cat["condicoes"]
    partes = [
        f"Você é o atendente de vendas da {cat['loja']} no WhatsApp. Slogan: \"{cat['slogan']}\". Site: {cat['site']}.",
        "Seu papel: o consultor da casa certa. Você descobre como é a casa do cliente e indica a proteção certa, "
        "com clareza e sem alarmismo. Você vende tranquilidade e suporte que responde, não preço de oferta.",
        "CONDIÇÕES DA LOJA\n" + "\n".join(f"- {k}: {v}" for k, v in c.items() if k != "desconto_pix")
        + f"\n- desconto Pix: {int(c['desconto_pix'] * 100)}%",
        f"PRODUTOS (preços de {cat['atualizado_em']})\n" + tabela_produtos(cat),
        regras_kit(),
        (REF / "roteiro.md").read_text(encoding="utf-8"),
        (REF / "objecoes.md").read_text(encoding="utf-8"),
        (REF / "pos-venda-7-dias.md").read_text(encoding="utf-8"),
    ]
    return "\n\n".join(partes).replace("Rode `scripts/recomendar_kit.py` com as respostas e use a mensagem que ele gera. Nunca calcule preço de cabeça.",
                                      "Monte o kit pelas regras acima e use só os preços da lista de produtos.")


if __name__ == "__main__":
    print(montar())
