#!/usr/bin/env python3
"""Vigia da gestão: lê os dados do app Rota do Milhão e lista o que saiu errado, por funcionário responsável.

Entrada (uma das duas):
  --backup arquivo.json   backup exportado no app (Gestão → Integrações → Backup completo)
  --pasta  pasta/         pasta salva pelo ArtifactData (out_dir) com data/users/me/estado/...

Uso:
  python3 monitor.py --backup rota-do-milhao-backup-2026-10-20.json
  python3 monitor.py --backup backup.json --json        # saída em JSON
  python3 monitor.py --backup backup.json --hoje 2026-10-25
Sai com código 2 se houver alerta crítico, 1 se houver alto, 0 se só médio ou nada.
"""
import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

REGRAS = Path(__file__).resolve().parent.parent / "references" / "alertas.json"
ORDEM = {"critico": 0, "alto": 1, "medio": 2}
VALIDOS_FORA = {"cancelado", "novo"}


def carregar_regras(caminho=REGRAS):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    return dados["limites"], {r["id"]: r for r in dados["regras"]}


def carregar_backup(caminho):
    b = json.loads(Path(caminho).read_text(encoding="utf-8"))
    if b.get("app") != "rota-do-milhao":
        raise ValueError("não é um backup do Rota do Milhão")
    return b


def carregar_pasta(pasta):
    base = Path(pasta)
    est = next(base.glob("**/estado"), None) if not (base / "estado").is_dir() else base / "estado"
    if est is None or not est.is_dir():
        raise ValueError("pasta sem data/users/me/estado")
    def col(nome):
        d = est / nome
        return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in d.glob("*.json")} if d.is_dir() else {}
    cat = est / "extra" / "catalogo.json"
    return {"catalogo": json.loads(cat.read_text(encoding="utf-8")) if cat.exists() else {"produtos": []},
            "pedidos": col("pedidos"), "clientes": col("clientes"), "fornecedores": col("fornecedores"),
            "lancamentos": col("lancamentos")}


def _d(s):
    try:
        return date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


def _prazo_max(texto):
    n = [int(x) for x in re.findall(r"\d+", str(texto or ""))]
    return max(n) if n else None


def avaliar(dados, hoje=None, regras=None):
    hoje = hoje or date.today()
    limites, R = regras or carregar_regras()
    cat = dados.get("catalogo") or {"produtos": []}
    produtos = {p["id"]: p for p in cat.get("produtos", [])}
    ativos = [p for p in produtos.values() if p.get("ativo")]
    pedidos = list((dados.get("pedidos") or {}).values())
    clientes = list((dados.get("clientes") or {}).values())
    forns = dados.get("fornecedores") or {}
    lancs = list((dados.get("lancamentos") or {}).values())
    achados = {}

    def add(rid, item, resp=None):
        achados.setdefault((rid, resp or R[rid]["responsavel"]), []).append(item)

    def custo(p):
        if p.get("custo") is not None:
            return float(p["custo"])
        return sum((float(produtos.get(i.get("id"), {}).get("custo") or 0) + float(produtos.get(i.get("id"), {}).get("frete") or 0)) * float(i.get("qtd") or 1) for i in p.get("itens", []))

    def previsao(p):
        e = p.get("envio") or {}
        if e.get("previsao"):
            return _d(e["previsao"])
        base = _d(e.get("enviadoEm") or p.get("dataPago") or p.get("data"))
        if not base:
            return None
        dias = (forns.get(p.get("fornecedorId")) or {}).get("prazoMax")
        if not dias:
            ds = [_prazo_max(produtos.get(i.get("id"), {}).get("prazo") or cat.get("prazo_padrao")) for i in p.get("itens", [])]
            ds = [x for x in ds if x]
            dias = max(ds) if ds else None
        return base + timedelta(days=int(dias)) if dias else None

    for p in pedidos:
        st, pid = p.get("status"), p.get("id")
        nome = (p.get("cliente") or {}).get("nome") or ""
        pv = previsao(p)
        if st in ("pago", "fornecedor", "transito") and pv and pv < hoje:
            add("tms-atraso", f"{pid} de {nome}: previsão {pv.strftime('%d/%m')}")
        if st == "pago":
            dp = _d(p.get("dataPago") or p.get("data"))
            if dp and (hoje - dp).days > limites["dias_para_repassar"]:
                add("erp-nao-repassado", f"{pid} pago em {dp.strftime('%d/%m')}")
        if st == "fornecedor" and not (p.get("envio") or {}).get("rastreio"):
            dr = _d((p.get("envio") or {}).get("repassadoEm") or p.get("dataPago") or p.get("data"))
            if dr and (hoje - dr).days > limites["dias_sem_rastreio"]:
                add("tms-sem-rastreio", f"{pid} repassado em {dr.strftime('%d/%m')}")
        if st not in VALIDOS_FORA:
            c = custo(p)
            if c > 0 and float(p.get("total") or 0) - c - float(p.get("taxa") or 0) < 0:
                add("erp-margem-negativa", f"{pid}: total {float(p.get('total') or 0):.2f}, custo {c:.2f}")
        if st == "troca":
            add("sac-troca-aberta", f"{pid} de {nome}")

    mes = hoje.isoformat()[:7]
    ped_mes = [p for p in pedidos if p.get("status") not in VALIDOS_FORA and str(p.get("data", ""))[:7] == mes]
    receita = sum(float(p.get("total") or 0) for p in ped_mes)
    margem = receita - sum(custo(p) for p in ped_mes) - sum(float(p.get("taxa") or 0) for p in ped_mes)
    l_mes = [l for l in lancs if str(l.get("data", ""))[:7] == mes]
    desp = sum(float(l.get("valor") or 0) for l in l_mes if l.get("tipo") != "receita")
    extra = sum(float(l.get("valor") or 0) for l in l_mes if l.get("tipo") == "receita")
    if (receita or desp) and margem + extra - desp < 0:
        add("fin-resultado-negativo", f"resultado de {mes}: {margem + extra - desp:.2f}")
    anuncios = sum(float(l.get("valor") or 0) for l in l_mes if l.get("categoria") == "anuncios" and l.get("tipo") != "receita")
    if receita and anuncios / receita * 100 > limites["anuncio_max_pct_receita"]:
        add("fin-anuncio-alto", f"anúncios {anuncios:.2f} = {anuncios / receita * 100:.0f}% da receita de {mes}")

    for c in clientes:
        prox = c.get("proxima") or {}
        etapa = c.get("etapa")
        if etapa == "perdido":
            continue
        dp = _d(prox.get("data"))
        if dp and (hoje - dp).days > limites["dias_followup_atrasado"]:
            resp = {"orcamento": "recuperador-de-carrinho", "pos": "guardiao-pos-venda"}.get(etapa)
            add("crm-followup-atrasado", f"{c.get('nome')}: {prox.get('acao') or 'follow-up'} ({dp.strftime('%d/%m')})", resp)
        if etapa == "orcamento" and not dp:
            add("crm-orcamento-sem-acao", c.get("nome") or c.get("id"))

    for p in ativos:
        ef, ep = p.get("estoqueFornecedor"), float(p.get("estoqueProprio") or 0)
        est = None if ef in (None, "") else float(ef) + ep
        if est is None and ep:
            est = ep
        nome = p.get("nome", p["id"])[:50]
        if est is not None and est <= 0:
            add("wms-esgotado", nome)
        elif est is not None and p.get("minimo") and est <= float(p["minimo"]):
            add("wms-baixo", f"{nome}: {est:.0f} un. (mínimo {float(p['minimo']):.0f})")
        if p.get("fornecedorId"):
            conf = _d(p.get("conferidoEm"))
            if not conf or (hoje - conf).days > limites["dias_sem_conferir_estoque"]:
                add("wms-sem-conferencia", f"{nome}: {'nunca conferido' if not conf else 'conferido em ' + conf.strftime('%d/%m')}")
        else:
            add("vmi-sem-fornecedor", nome)
        if not float(p.get("custo") or 0):
            add("erp-sem-custo", nome)

    for fid, f in forns.items():
        ent = [p for p in pedidos if p.get("fornecedorId") == fid and p.get("status") == "entregue" and (p.get("envio") or {}).get("entregueEm")]
        if len(ent) >= limites["entregas_minimas_para_avaliar"]:
            ok = sum(1 for p in ent if not previsao(p) or _d(p["envio"]["entregueEm"]) <= previsao(p))
            pct = ok / len(ent) * 100
            if pct < limites["pontualidade_minima_pct"]:
                add("vmi-pontualidade", f"{f.get('nome')}: {pct:.0f}% no prazo em {len(ent)} entregas")

    saida = []
    for (rid, resp), itens in achados.items():
        r = R[rid]
        quando = r["quando"].format(**limites)
        saida.append({"regra": rid, "sistema": r["sistema"], "nivel": r["nivel"], "responsavel": resp, "qtd": len(itens),
                      "itens": itens, "quando": quando, "acao": r["acao"]})
    saida.sort(key=lambda a: (ORDEM[a["nivel"]], a["sistema"], a["regra"]))
    return saida


def para_texto(alertas):
    if not alertas:
        return "Sem alertas na gestão. Tudo em dia."
    linhas = []
    nomes = {"critico": "CRÍTICO", "alto": "ALTO", "medio": "MÉDIO"}
    for a in alertas:
        linhas.append(f"[{nomes[a['nivel']]}] {a['sistema']} · {a['responsavel']}: {a['quando']} ({a['qtd']})")
        for i in a["itens"][:5]:
            linhas.append(f"   - {i}")
        if a["qtd"] > 5:
            linhas.append(f"   - e mais {a['qtd'] - 5}")
        linhas.append(f"   O que fazer: {a['acao']}")
    return "\n".join(linhas)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--backup")
    g.add_argument("--pasta")
    ap.add_argument("--hoje", help="AAAA-MM-DD (padrão: hoje)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    dados = carregar_backup(a.backup) if a.backup else carregar_pasta(a.pasta)
    alertas = avaliar(dados, date.fromisoformat(a.hoje) if a.hoje else None)
    print(json.dumps(alertas, ensure_ascii=False, indent=2) if a.json else para_texto(alertas))
    sys.exit(2 if any(x["nivel"] == "critico" for x in alertas) else 1 if any(x["nivel"] == "alto" for x in alertas) else 0)


if __name__ == "__main__":
    main()
