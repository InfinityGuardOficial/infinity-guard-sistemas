#!/usr/bin/env python3
"""Painel de vendas da Infinity Guard: lê a exportação de pedidos da Nuvemshop e gera um HTML que abre em qualquer navegador.

Uso:
  python3 painel.py --pedidos vendas.csv [--conversas conversas.csv] --saida paineis/painel.html
  python3 painel.py --pedidos vendas.csv --json
  python3 painel.py --pedidos vendas.csv --mapear "total=Valor final" --mapear "data=Criado em"

--pedidos    CSV exportado na Nuvemshop (lista de vendas). Aceita ; ou , e valores 1.234,56 ou 1234.56.
--conversas  CSV opcional do atendimento: data;cliente;kit_indicado;resultado;canal
             resultado = venda | carrinho | recuperado | sem_resposta | em_aberto (modelo em references/).
--mapear     campo=Nome da coluna, se o cabeçalho da sua exportação tiver outro nome.
Os números saem só do arquivo. O painel não estima nem completa nada.
"""
import argparse
import csv
import html
import io
import json
import re
import sys
from collections import Counter, OrderedDict, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

META_VENDAS = 20  # o mapa de sistemas liga o painel nas primeiras 20 vendas
ALIASES = {
    "pedido": ["número do pedido", "numero do pedido", "nº do pedido", "pedido", "order", "número", "numero", "id do pedido"],
    "data": ["data", "data do pedido", "data de criação", "data de criacao", "criado em", "date"],
    "status": ["status do pagamento", "status de pagamento", "status", "situação", "situacao"],
    "total": ["total", "valor total", "total do pedido", "total (r$)", "valor"],
    "produto": ["nome do produto", "produto", "produtos", "item"],
    "qtd": ["quantidade comprada", "quantidade do produto", "quantidade", "qtd"],
    "pagamento": ["forma de pagamento", "meio de pagamento", "método de pagamento", "metodo de pagamento", "pagamento"],
    "cupom": ["cupom de desconto", "cupom", "código do cupom", "codigo do cupom"],
    "canal": ["canal", "canal de venda", "origem", "utm_source", "utm source"],
}
PAGO = re.compile(r"pago|aprovad|paid|confirmad|conclu", re.I)
CANCELADO = re.compile(r"cancel|recusad|estornad|devolvid|expirad", re.I)


def numero(s):
    s = str(s or "").strip().replace("R$", "").replace(" ", "")
    if not s:
        return 0.0
    if "," in s and (s.rfind(",") > s.rfind(".")):
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def data_de(s):
    s = str(s or "").strip()
    for f in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19], f).date()
        except ValueError:
            continue
    return None


def ler_csv(caminho):
    bruto = Path(caminho).read_bytes()
    for enc in ("utf-8-sig", "latin-1"):
        try:
            txt = bruto.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    sep = ";" if txt.split("\n", 1)[0].count(";") >= txt.split("\n", 1)[0].count(",") else ","
    return list(csv.DictReader(io.StringIO(txt), delimiter=sep))


def colunas(cabecalho, mapear=None):
    norm = {c.strip().lower(): c for c in cabecalho if c}
    achou = {}
    for campo, nomes in ALIASES.items():
        for n in nomes:
            if n in norm:
                achou[campo] = norm[n]
                break
    for m in mapear or []:
        campo, _, col = m.partition("=")
        if col not in cabecalho:
            raise ValueError(f"--mapear: coluna '{col}' não existe. Colunas do arquivo: {', '.join(cabecalho)}")
        achou[campo.strip()] = col
    faltam = [c for c in ("pedido", "data", "total") if c not in achou]
    if faltam:
        raise ValueError(f"faltam as colunas {faltam}. Colunas do arquivo: {', '.join(cabecalho)}. Use --mapear campo=Coluna.")
    return achou


def consolidar(linhas, col):
    """Uma linha por pedido (a Nuvemshop repete o pedido em cada produto)."""
    pedidos = OrderedDict()
    for l in linhas:
        g = lambda k: (l.get(col[k]) or "").strip() if k in col else ""
        num = g("pedido")
        if not num:
            continue
        p = pedidos.setdefault(num, {"pedido": num, "data": data_de(g("data")), "status": g("status"),
                                     "total": numero(g("total")), "pagamento": g("pagamento"), "cupom": g("cupom"),
                                     "canal": g("canal") or "loja", "itens": []})
        if not p["total"]:
            p["total"] = numero(g("total"))
        if g("produto"):
            p["itens"].append((g("produto"), int(numero(g("qtd")) or 1)))
    return list(pedidos.values())


def metricas(pedidos, conversas=None, hoje=None):
    hoje = hoje or date.today()
    pagos = [p for p in pedidos if not CANCELADO.search(p["status"]) and (not p["status"] or PAGO.search(p["status"]))]
    cancelados = [p for p in pedidos if CANCELADO.search(p["status"])]
    pendentes = [p for p in pedidos if p not in pagos and p not in cancelados]
    fat = round(sum(p["total"] for p in pagos), 2)
    pix = [p for p in pagos if "pix" in p["pagamento"].lower()]
    semanas = defaultdict(float)
    for p in pagos:
        if p["data"]:
            semanas[(p["data"] - timedelta(days=p["data"].weekday())).isoformat()] += p["total"]
    produtos = Counter()
    for p in pagos:
        for nome, q in p["itens"]:
            produtos[nome.split(" — ")[0][:60]] += q
    canais = Counter(p["canal"] for p in pagos)
    cupons = Counter(p["cupom"].upper() for p in pagos if p["cupom"])
    m = {"gerado_em": hoje.isoformat(),
         "periodo": [min((p["data"] for p in pedidos if p["data"]), default=None),
                     max((p["data"] for p in pedidos if p["data"]), default=None)],
         "pedidos_pagos": len(pagos), "pendentes": len(pendentes), "cancelados": len(cancelados),
         "faturamento": fat, "ticket_medio": round(fat / len(pagos), 2) if pagos else 0.0,
         "pix_pct": round(len(pix) / len(pagos), 3) if pagos else 0.0,
         "meta_vendas": META_VENDAS, "por_semana": dict(sorted(semanas.items())),
         "top_produtos": produtos.most_common(8), "canais": canais.most_common(), "cupons": cupons.most_common()}
    m["periodo"] = [d.isoformat() if d else None for d in m["periodo"]]
    if conversas is not None:
        res = Counter((c.get("resultado") or "").strip().lower() for c in conversas)
        kits = Counter((c.get("kit_indicado") or "").strip() for c in conversas if (c.get("kit_indicado") or "").strip())
        total = len(conversas)
        vendas = res["venda"] + res["recuperado"]
        m["conversas"] = {"total": total, "vendas": vendas, "conversao": round(vendas / total, 3) if total else 0.0,
                          "carrinhos": res["carrinho"] + res["recuperado"], "recuperados": res["recuperado"],
                          "sem_resposta": res["sem_resposta"], "kits": kits.most_common(6)}
    return m


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def barras(pares, fmt=str, largura=560, alto=26):
    """Barras horizontais em SVG (uma série, um tom), com tooltip nativo."""
    if not pares:
        return '<p class="vazio">Sem dados ainda.</p>'
    mx = max(v for _, v in pares) or 1
    rot = 170
    h = alto * len(pares)
    out = [f'<svg viewBox="0 0 {largura} {h}" role="img" class="bars">']
    for i, (k, v) in enumerate(pares):
        w = max(4, (largura - rot - 90) * v / mx)
        y = i * alto
        bruto = str(k)
        nome = html.escape(bruto)
        curto = html.escape(bruto if len(bruto) <= 24 else bruto[:23] + "…")
        out.append(f'<g><title>{nome}: {html.escape(fmt(v))}</title>'
                   f'<rect x="0" y="{y}" width="{largura}" height="{alto}" fill="transparent"/>'
                   f'<text x="{rot - 8}" y="{y + alto / 2 + 4}" text-anchor="end" class="lbl">{curto}</text>'
                   f'<rect x="{rot}" y="{y + 5}" width="{w:.1f}" height="{alto - 10}" rx="4" class="bar"/>'
                   f'<text x="{rot + w + 6:.1f}" y="{y + alto / 2 + 4}" class="val">{html.escape(fmt(v))}</text></g>')
    out.append("</svg>")
    return "".join(out)


def tabela(pares, cab, fmt=str):
    linhas = "".join(f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(fmt(v))}</td></tr>" for k, v in pares)
    return f'<table><thead><tr><th>{cab[0]}</th><th>{cab[1]}</th></tr></thead><tbody>{linhas}</tbody></table>'


def para_html(m):
    def bloco(titulo, pares, fmt=str, cab=("Item", "Valor")):
        return (f'<section class="card"><h2>{titulo}</h2>{barras(pares, fmt)}'
                f'<details><summary>Ver tabela</summary>{tabela(pares, cab, fmt)}</details></section>')
    semanas = [(datetime.fromisoformat(k).strftime("sem. %d/%m"), v) for k, v in m["por_semana"].items()]
    prog = min(100, round(100 * m["pedidos_pagos"] / m["meta_vendas"]))
    per = " a ".join(datetime.fromisoformat(d).strftime("%d/%m/%Y") for d in m["periodo"] if d) or "sem datas"
    tiles = [("Faturamento pago", brl(m["faturamento"])), ("Pedidos pagos", str(m["pedidos_pagos"])),
             ("Ticket médio", brl(m["ticket_medio"])), ("Pagos no Pix", f"{m['pix_pct']:.0%}")]
    conv = ""
    if "conversas" in m:
        c = m["conversas"]
        conv = ('<section class="card"><h2>Atendimento no WhatsApp</h2><div class="tiles">'
                + "".join(f'<div class="tile"><span>{a}</span><b>{b}</b></div>' for a, b in [
                    ("Conversas", c["total"]), ("Viraram venda", f"{c['vendas']} ({c['conversao']:.0%})"),
                    ("Carrinhos recuperados", f"{c['recuperados']} de {c['carrinhos']}"), ("Sem resposta", c["sem_resposta"])])
                + "</div>" + ("<h3>Kits mais indicados</h3>" + barras(c["kits"]) if c["kits"] else "") + "</section>")
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Painel de Vendas</title>
<style>
:root{{--bg:#f4f4f2;--surface:#fcfcfb;--text:#0b0b0b;--text2:#52514e;--line:#e2e1dc;--bar:#2a78d6;--good:#0ca30c}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111110;--surface:#1a1a19;--text:#f0efec;--text2:#c3c2b7;--line:#383835;--bar:#3987e5}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:960px;margin:0 auto;padding:24px 16px 48px}}h1{{font-size:22px;margin:0 0 4px}}.sub{{color:var(--text2);margin:0 0 20px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:16px}}
.tile{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px}}.tile span{{color:var(--text2);font-size:13px;display:block}}
.tile b{{font-size:24px;font-variant-numeric:tabular-nums}}.card{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:16px}}
.card h2{{font-size:16px;margin:0 0 12px}}.card h3{{font-size:14px;color:var(--text2)}}.bars{{width:100%;height:auto}}.bar{{fill:var(--bar)}}
.lbl,.val{{fill:var(--text2);font-size:12px}}.val{{fill:var(--text);font-variant-numeric:tabular-nums}}g:hover .bar{{opacity:.8}}
.meta{{height:10px;background:var(--line);border-radius:5px;overflow:hidden}}.meta i{{display:block;height:100%;background:var(--good)}}
details{{margin-top:8px;color:var(--text2)}}table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:13px}}
td,th{{text-align:left;padding:4px 6px;border-bottom:1px solid var(--line)}}.vazio{{color:var(--text2)}}
</style></head><body><main>
<h1>Painel de Vendas · Infinity Guard</h1>
<p class="sub">Pedidos de {per} · gerado em {datetime.fromisoformat(m['gerado_em']).strftime('%d/%m/%Y')} · {m['pendentes']} pendentes e {m['cancelados']} cancelados fora da conta</p>
<div class="tiles">{''.join(f'<div class="tile"><span>{a}</span><b>{b}</b></div>' for a, b in tiles)}</div>
<section class="card"><h2>Meta das primeiras {m['meta_vendas']} vendas: {m['pedidos_pagos']} de {m['meta_vendas']}</h2>
<div class="meta" role="progressbar" aria-valuenow="{prog}" aria-valuemin="0" aria-valuemax="100"><i style="width:{prog}%"></i></div></section>
{bloco("Faturamento pago por semana", semanas, brl, ("Semana", "Faturamento"))}
{bloco("Produtos mais vendidos (unidades)", m["top_produtos"], str, ("Produto", "Unidades"))}
{bloco("Vendas por canal (pedidos)", m["canais"], str, ("Canal", "Pedidos"))}
{bloco("Cupons usados (pedidos)", m["cupons"], str, ("Cupom", "Pedidos")) if m["cupons"] else ""}
{conv}
</main></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pedidos", required=True)
    ap.add_argument("--conversas")
    ap.add_argument("--mapear", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args()
    linhas = ler_csv(a.pedidos)
    try:
        col = colunas(list(linhas[0].keys()) if linhas else [], a.mapear)
    except ValueError as e:
        sys.exit(f"erro: {e}")
    conv = ler_csv(a.conversas) if a.conversas else None
    m = metricas(consolidar(linhas, col), conv)
    out = json.dumps(m, ensure_ascii=False, indent=2) if a.json else para_html(m)
    if a.saida:
        Path(a.saida).write_text(out, encoding="utf-8")
        print(f"painel salvo em {a.saida}: {m['pedidos_pagos']} pedidos pagos, {brl(m['faturamento'])}")
    else:
        print(out)


if __name__ == "__main__":
    main()
