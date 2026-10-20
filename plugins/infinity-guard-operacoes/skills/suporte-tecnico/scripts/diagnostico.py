#!/usr/bin/env python3
"""Suporte técnico Infinity Guard: acha o problema pela fala do cliente e devolve o passo a passo para o WhatsApp.

Uso:
  python3 diagnostico.py --mensagem "minha câmera fica offline toda noite" --nome Ana
  python3 diagnostico.py --mensagem "..." --categoria camera     (camera | alarme | fechadura)
  python3 diagnostico.py --listar                               (todos os problemas da base)
  python3 diagnostico.py --troca --recebido 2026-10-15 [--hoje 2026-10-19] [--defeito]
  ... --json

O modo --troca diz em qual caso do CDC o cliente está (arrependimento em 7 dias, defeito em 90 dias)
e monta o resumo para o dono decidir. Ele não aprova nem nega troca sozinho.
"""
import argparse
import json
import unicodedata
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "references" / "problemas.json"
PRAZO_ARREPENDIMENTO = 7   # CDC art. 49
PRAZO_DEFEITO = 90         # CDC art. 26, II (produto durável)
PRAZO_CONSERTO = 30        # CDC art. 18, §1º


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def carregar(caminho=BASE):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))["problemas"]


def diagnosticar(mensagem, problemas, categoria=None):
    msg = sem_acento(mensagem)
    pontos = []
    for p in problemas:
        if categoria and categoria not in p["produtos"]:
            continue
        acertos = sorted({sem_acento(w) for w in p["palavras"] if sem_acento(w) in msg})
        if acertos:
            pontos.append((len(acertos), p, acertos))
    pontos.sort(key=lambda t: -t[0])
    return [{"id": p["id"], "titulo": p["titulo"], "acertos": a, "passos": p["passos"], "escalar_se": p["escalar_se"]}
            for _, p, a in pontos]


def mensagem_whatsapp(prob, nome=None):
    oi = f"{nome}, " if nome else ""
    linhas = [f"{oi}vamos resolver juntos. Faz assim, um passo de cada vez, e me fala em qual deu certo:"]
    linhas += [f"{i}. {passo.replace('**', '*')}" for i, passo in enumerate(prob["passos"], 1)]
    linhas.append("Se não resolver, me manda um vídeo curto mostrando o que acontece que eu sigo daqui.")
    return "\n".join(linhas)


def caso_troca(recebido, hoje, defeito):
    dias = (hoje - recebido).days
    if dias < 0:
        raise ValueError("data de recebimento no futuro")
    if dias <= PRAZO_ARREPENDIMENTO:
        caso = ("arrependimento", f"Dentro dos {PRAZO_ARREPENDIMENTO} dias do CDC art. 49: devolução do valor total, "
                "frete incluso, sem precisar de motivo.")
    elif defeito and dias <= PRAZO_DEFEITO:
        caso = ("defeito", f"Dentro da garantia legal de {PRAZO_DEFEITO} dias (CDC art. 26): a loja tem até "
                f"{PRAZO_CONSERTO} dias para resolver; senão o cliente escolhe troca, dinheiro de volta ou abatimento.")
    elif defeito:
        caso = ("defeito-fora-do-prazo-legal", "Passou dos 90 dias da entrega. Se o defeito apareceu agora (vício oculto), "
                "o prazo conta de quando apareceu. Garantia contratual da loja ainda não documentada: o dono decide.")
    else:
        caso = ("fora-do-arrependimento", "Passou dos 7 dias e não é defeito: a troca é cortesia, o dono decide.")
    return {"dias_desde_entrega": dias, "caso": caso[0], "explicacao": caso[1],
            "pedir": ["número do pedido", "foto ou vídeo do problema", "foto da caixa (se for devolução)"],
            "decide": "dono"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mensagem")
    ap.add_argument("--nome")
    ap.add_argument("--categoria", choices=["camera", "alarme", "fechadura"])
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--troca", action="store_true")
    ap.add_argument("--recebido")
    ap.add_argument("--hoje")
    ap.add_argument("--defeito", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    probs = carregar()

    if a.listar:
        for p in probs:
            print(f"{p['id']:<18} {p['titulo']}  ({', '.join(p['produtos'])})")
        return
    if a.troca:
        if not a.recebido:
            ap.error("--troca precisa de --recebido AAAA-MM-DD")
        hoje = date.fromisoformat(a.hoje) if a.hoje else date.today()
        r = caso_troca(date.fromisoformat(a.recebido), hoje, a.defeito)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            print(f"Caso: {r['caso']} ({r['dias_desde_entrega']} dias desde a entrega)\n{r['explicacao']}\n"
                  f"Peça ao cliente: {', '.join(r['pedir'])}.\nQuem decide: o dono.")
        return
    if not a.mensagem:
        ap.error("use --mensagem, --listar ou --troca")
    achados = diagnosticar(a.mensagem, probs, a.categoria)
    if a.json:
        print(json.dumps({"achados": achados, "mensagem": mensagem_whatsapp(achados[0], a.nome) if achados else None},
                         ensure_ascii=False, indent=2))
        return
    if not achados:
        print("Não reconheci o problema. Pergunte ao cliente: qual aparelho, o que aparece na tela do app "
              "e desde quando. Rode de novo com a resposta.")
        return
    p = achados[0]
    print(f"Problema provável: {p['titulo']} [{p['id']}]")
    if len(achados) > 1:
        print("Outras possibilidades: " + ", ".join(x["titulo"] for x in achados[1:3]))
    print("\n--- mensagem para o cliente ---\n" + mensagem_whatsapp(p, a.nome))
    print(f"\n--- para o dono ---\nEscalar se: {p['escalar_se']}")


if __name__ == "__main__":
    main()
