"""Regras que transformam as métricas em eventos para a fila. Cada evento diz qual funcionário chamar e o que pedir.

Estado entre ciclos fica em logs/estado.json (último relatório, pedidos já vistos, última avaliação dos conjuntos),
para o mesmo evento não ser criado a cada 30 minutos.
"""
import json
from datetime import datetime

from core import caminhos
from tools import _skills


def ler_estado():
    f = caminhos.logs() / "estado.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def gravar_estado(estado):
    f = caminhos.logs() / "estado.json"
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(f)


def _evento(tipo, agente, tarefa, **extra):
    return {"type": tipo, "details": {"agente": agente, "tarefa": tarefa, **extra}}


def avaliar(metricas, estado, cfg, agora=None):
    """Devolve (eventos, avisos, novo_estado). Não grava nada."""
    agora = agora or datetime.now()
    hoje = agora.date().isoformat()
    estado = dict(estado)
    eventos, avisos = [], []
    vendas, meta = metricas.get("vendas", {}), metricas.get("meta", {})
    arq_metricas = caminhos.logs() / "metrics.json"
    arq_vendas = caminhos.dados() / "nuvemshop" / str(vendas.get("arquivo"))

    if not vendas.get("ok"):
        avisos.append(f"vendas: {vendas.get('motivo')}")
    if not meta.get("ok"):
        avisos.append(f"meta: {meta.get('motivo')}")

    if vendas.get("ok"):
        (caminhos.logs() / "paineis").mkdir(exist_ok=True)
        if agora.hour >= cfg["hora_relatorio_diario"] and estado.get("ultimo_relatorio") != hoje:
            eventos.append(_evento(
                "relatorio_diario", "analista-de-vendas",
                f"Leia {arq_metricas} (gerado em {metricas['gerado_em']}) e o CSV {arq_vendas}. "
                f"Gere o painel com a skill painel-de-vendas (--saida {caminhos.logs() / 'paineis' / (hoje + '.html')}; a pasta já existe, não rode mkdir) "
                "e resuma em 3 números e uma ação para hoje."))
            estado["ultimo_relatorio"] = hoje
        vistos = estado.get("pedidos_pagos")
        if vistos is not None and vendas["pedidos_pagos"] > vistos:
            novos = vendas["pedidos_pagos"] - vistos
            eventos.append(_evento(
                "novas_vendas", "guardiao-pos-venda",
                f"Entraram {novos} pedido(s) pago(s) novo(s) no CSV {arq_vendas}. "
                "Prepare o rascunho da mensagem de pós-venda do dia 0 para cada um (não envie).", novos=novos))
        estado["pedidos_pagos"] = vendas["pedidos_pagos"]

    if meta.get("ok") and meta.get("conjuntos"):
        ticket = cfg.get("ticket_referencia") or (vendas.get("ticket_medio") if vendas.get("ok") else None)
        if not ticket:
            avisos.append("meta: sem ticket (ticket_referencia no config ou vendas no CSV) para aplicar a régua.")
        else:
            midia = _skills.carregar("plano-de-midia", "midia")
            r = midia.avaliar(meta["conjuntos"], ticket, cfg["margem_bruta"])
            decisoes = {c["conjunto"]: c["decisao"] for c in r["conjuntos"]}
            mexer = {k: v for k, v in decisoes.items() if v in ("PAUSAR", "ESCALAR")}
            if mexer and mexer != estado.get("decisoes_conjuntos"):
                linhas = "; ".join(f"{k}: {v}" for k, v in mexer.items())
                eventos.append(_evento(
                    "revisar_conjuntos", "analista-de-midia",
                    f"A régua do plano-de-midia (ticket {ticket}, margem {cfg['margem_bruta']}) indica: {linhas}. "
                    f"Confira com os números de {arq_metricas}, explique cada decisão em uma linha e liste o que "
                    "o dono deve fazer.", decisoes=mexer))
            estado["decisoes_conjuntos"] = mexer
            roas, equilibrio = meta.get("roas"), round(1 / cfg["margem_bruta"], 2)
            if roas is not None and roas < equilibrio and estado.get("alerta_roas") != hoje:
                eventos.append(_evento(
                    "roas_abaixo_do_equilibrio", "lider-trafego",
                    f"O ROAS geral está em {roas}, abaixo do equilíbrio {equilibrio} (margem {cfg['margem_bruta']}). "
                    f"Diga a causa mais provável pelos números de {arq_metricas} e o plano dos próximos 3 dias.",
                    roas=roas, equilibrio=equilibrio))
                estado["alerta_roas"] = hoje

    if agora.weekday() == cfg["dia_reuniao_semanal"] and agora.hour >= cfg["hora_relatorio_diario"] \
            and estado.get("ultima_reuniao") != hoje:
        eventos.append(_evento(
            "reuniao_semanal", "diretor-geral",
            f"Monte a pauta da reunião semanal com a skill reuniao-semanal, usando {arq_metricas} e os relatórios "
            f"da semana em {caminhos.logs() / 'agentes'}. Termine com as 3 prioridades da semana."))
        estado["ultima_reuniao"] = hoje

    return eventos, avisos, estado
