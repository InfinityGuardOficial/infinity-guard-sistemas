#!/usr/bin/env python3
"""Radar de concorrentes da Infinity Guard: registra preços do mercado e compara com o nosso catálogo.

Uso:
  python3 radar.py comparar                      (nossa posição de preço por produto, com a leitura mais recente de cada concorrente)
  python3 radar.py registrar --concorrente Intelbras --produto "iM4 C" --equivale cam-asecam-ptz \
      --preco 579.90 --fonte "Extra" [--pix] [--oferta] [--garantia "1 ano"] [--anatel sim|nao] [--data 2026-10-20]
  python3 radar.py velhas [--dias 30]            (leituras que precisam ser refeitas)
  ... --json

Toda leitura precisa de fonte. Preço sem fonte não entra.
"""
import argparse
import json
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
BASE = AQUI / "references" / "concorrentes.json"
CATALOGOS = [AQUI.parent / "atendente-infinity-guard" / "references" / "catalogo.json"]


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar(caminho=BASE):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def catalogo():
    cam = next((c for c in CATALOGOS if c.exists()), None)
    if not cam:
        raise SystemExit("catálogo não encontrado: instale a skill atendente-infinity-guard ao lado desta")
    return {p["id"]: p for p in json.loads(cam.read_text(encoding="utf-8"))["produtos"]}


def mais_recentes(leituras):
    ult = {}
    for l in sorted(leituras, key=lambda x: x["data"]):
        ult[(l["concorrente"], l["produto"])] = l
    return list(ult.values())


def comparar(leituras, nossos):
    saida = []
    for pid, p in nossos.items():
        rivais = [l for l in mais_recentes(leituras) if l["equivale"] == pid]
        if not rivais or not p["ativo"]:
            continue
        precos = sorted(l["preco"] for l in rivais)
        mediana = precos[len(precos) // 2] if len(precos) % 2 else round((precos[len(precos) // 2 - 1] + precos[len(precos) // 2]) / 2, 2)
        dif = round((p["preco"] - mediana) / mediana, 4)
        if dif > 0.25:
            leitura = "acima do mercado: precisa de prova e serviço visíveis (garantia, prazo de entrega, suporte) ou revisar preço"
        elif dif < -0.15:
            leitura = "abaixo do mercado: espaço para margem ou para destacar o preço"
        else:
            leitura = "na faixa do mercado"
        if len(rivais) < 3:
            leitura = f"poucas leituras ({len(rivais)}), compare com cada uma; pela mediana: {leitura}"
        vantagens = [f"{l['concorrente']} {l['produto']}: {', '.join(x for x in (('garantia ' + l['garantia']) if l.get('garantia') else '', 'Anatel na página' if l.get('anatel') else '') if x)}"
                     for l in rivais if l.get("garantia") or l.get("anatel")]
        saida.append({"id": pid, "nosso": p["preco"], "nosso_pix": p["pix"], "mediana": mediana, "minimo": precos[0],
                      "maximo": precos[-1], "diferenca": dif,
                      "vs_mais_barato": round((p["preco"] - precos[0]) / precos[0], 4), "leitura": leitura, "rivais": rivais,
                      "o_que_eles_mostram": vantagens})
    return saida


def registrar(base, leitura):
    for campo in ("concorrente", "produto", "equivale", "preco", "fonte", "data"):
        if not leitura.get(campo):
            raise ValueError(f"campo obrigatório: {campo}")
    if leitura["preco"] <= 0:
        raise ValueError("preço inválido")
    base["leituras"].append(leitura)
    return base


def velhas(leituras, dias=30, hoje=None):
    hoje = hoje or date.today()
    return [l for l in mais_recentes(leituras) if (hoje - date.fromisoformat(l["data"])).days > dias]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="modo", required=True)
    sub.add_parser("comparar")
    r = sub.add_parser("registrar")
    for c in ("concorrente", "produto", "equivale", "fonte"):
        r.add_argument(f"--{c}", required=True)
    r.add_argument("--preco", type=float, required=True)
    r.add_argument("--pix", action="store_true")
    r.add_argument("--oferta", action="store_true")
    r.add_argument("--garantia")
    r.add_argument("--anatel", choices=["sim", "nao"])
    r.add_argument("--instalacao")
    r.add_argument("--data")
    v = sub.add_parser("velhas")
    v.add_argument("--dias", type=int, default=30)
    a = ap.parse_args()
    base = carregar()

    if a.modo == "comparar":
        res = comparar(base["leituras"], catalogo())
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
            return
        for x in res:
            print(f"\n{x['id']}: nosso {brl(x['nosso'])} (Pix {brl(x['nosso_pix'])}) · mercado {brl(x['minimo'])} a "
                  f"{brl(x['maximo'])}, mediana {brl(x['mediana'])} → {x['diferenca']:+.0%} da mediana, "
                  f"{x['vs_mais_barato']:+.0%} do mais barato; {x['leitura']}")
            for o in x["o_que_eles_mostram"]:
                print(f"   eles mostram: {o}")
    elif a.modo == "registrar":
        nossos = catalogo()
        if a.equivale not in nossos:
            raise SystemExit(f"'{a.equivale}' não é id do catálogo")
        leitura = {"data": a.data or date.today().isoformat(), "concorrente": a.concorrente, "produto": a.produto,
                   "equivale": a.equivale, "preco": a.preco, "pix": a.pix, "oferta": a.oferta, "fonte": a.fonte,
                   "garantia": a.garantia, "anatel": None if a.anatel is None else a.anatel == "sim",
                   "instalacao": a.instalacao}
        BASE.write_text(json.dumps(registrar(base, leitura), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Registrado: {a.concorrente} {a.produto} {brl(a.preco)} ({a.fonte})")
    else:
        res = velhas(base["leituras"], a.dias)
        print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else
              "\n".join(f"{l['data']} {l['concorrente']} {l['produto']} ({l['fonte']})" for l in res) or "Tudo em dia.")


if __name__ == "__main__":
    main()
