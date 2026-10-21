"""Resumo do dia em um arquivo só: logs/resumo/AAAA-MM-DD.md (refeito a cada ciclo)."""
import json
from datetime import datetime

from core import aprovacoes, caminhos
from core.event_queue import EventQueue


def _brl(v):
    return "—" if v is None else "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar(metricas, agora=None):
    agora = agora or datetime.now()
    hoje = agora.date().isoformat()
    v, m = metricas.get("vendas", {}), metricas.get("meta", {})
    linhas = [f"# Resumo do dia · {agora:%d/%m/%Y}", f"_Atualizado às {agora:%H:%M}._", "", "## Números"]
    if v.get("ok"):
        linhas.append(f"- Vendas ({v['arquivo']}, {v['periodo'][0]} a {v['periodo'][1]}): {v['pedidos_pagos']} pedido(s) pago(s), "
                      f"{_brl(v['faturamento'])}, ticket {_brl(v['ticket_medio'])}, meta das primeiras {v['meta_vendas']}.")
    else:
        linhas.append(f"- Vendas: sem dados ({v.get('motivo')})")
    if m.get("ok"):
        linhas.append(f"- Anúncios ({m['fonte']}): gasto {_brl(m['gasto'])}, {m['compras']} compra(s), ROAS {m['roas'] or '—'}, "
                      f"CPA {_brl(m['cpa'])}.")
    else:
        linhas.append(f"- Anúncios: sem dados ({m.get('motivo')})")

    estado_f = caminhos.logs() / "estado.json"
    estado = json.loads(estado_f.read_text(encoding="utf-8")) if estado_f.exists() else {}
    rot = [r for r in estado.get("ultimas_rotinas", []) if r.get("data") == hoje]
    linhas += ["", "## Rotinas de hoje"] + ([f"- {r['rotina']}: {'ok' if r['ok'] else 'ERRO'} · {r['resumo']}" for r in rot]
                                          or ["- nenhuma rodou ainda"])

    hist = [t for t in EventQueue.snapshot()["history"] if str(t.get("started_at", "")).startswith(hoje)]
    linhas += ["", "## Funcionários chamados hoje"] + (
        [f"- {t['details'].get('agente')} ({t['type']}): {t.get('status', 'rodando')} · {t.get('saida', '')}" for t in hist]
        or ["- nenhum"])

    pend = aprovacoes.pendentes()
    linhas += ["", f"## Esperando o seu \"pode\" ({len(pend)})"] + (
        [f"- {n}. [{p['agente']}] {p['acao']}" for n, p in pend] or ["- nada"])
    linhas += ["", "Comandos: `python core/daemon_orchestrator.py aprovacoes` · `aprovar <n>` · `recusar <n>` · `status`"]

    pasta = caminhos.logs() / "resumo"
    pasta.mkdir(exist_ok=True)
    f = pasta / f"{hoje}.md"
    f.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return f
