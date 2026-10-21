#!/usr/bin/env python3
"""Daemon do orquestrador da Infinity Guard.

A cada ciclo (intervalo_minutos do config): coleta as métricas (Nuvemshop CSV + Meta só leitura), aplica as
regras de core/regras.py, enfileira os eventos em logs/queue.json e dispara o funcionário de cada evento.
O que o funcionário recomendar que gaste dinheiro, mexa em anúncio, preço, loja ou fale com cliente vai para
logs/aprovacoes.json: o daemon nunca executa isso.

Uso:
  python3 core/daemon_orchestrator.py            # roda sem parar (Ctrl+C ou o comando parar encerram)
  python3 core/daemon_orchestrator.py uma-vez    # um ciclo só (bom para testar)
  python3 core/daemon_orchestrator.py status     # fila, últimas tarefas e aprovações pendentes
  python3 core/daemon_orchestrator.py parar      # pede para o daemon em segundo plano encerrar
  python3 core/daemon_orchestrator.py aprovacoes # pedidos esperando o seu "pode", com o link de onde fazer
  python3 core/daemon_orchestrator.py aprovar 3 [nota]   /   recusar 3 [nota]
Funciona igual no Windows, Linux e Mac. Logs em logs/system.log e logs/errors.log.
"""
import json
import logging
import os
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import aprovacoes, caminhos, config, regras, resumo, rotinas  # noqa: E402
from core.event_queue import EventQueue  # noqa: E402
from tools import central, coletar_metricas, run_claude_agent  # noqa: E402

log = logging.getLogger("infinity-guard")
log.addHandler(logging.NullHandler())


def configurar_logs():
    if any(not isinstance(h, logging.NullHandler) for h in log.handlers):
        return
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    for nome, nivel in (("system.log", logging.INFO), ("errors.log", logging.ERROR)):
        h = RotatingFileHandler(caminhos.logs() / nome, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        h.setLevel(nivel)
        h.setFormatter(fmt)
        log.addHandler(h)
    if sys.stdout and sys.stdout.isatty():
        s = logging.StreamHandler()
        s.setFormatter(fmt)
        log.addHandler(s)


def processar_fila(cfg, rodar=run_claude_agent.rodar):
    feitas = []
    while (task := EventQueue.pop_task()) is not None:
        d = task["details"]
        if not cfg.get("rodar_agentes", True):
            EventQueue.finish_task(task, "pulada", "rodar_agentes=false no config")
            log.info("evento %s pulado (rodar_agentes=false)", task["type"])
            continue
        log.info("evento %s → %s", task["type"], d["agente"])
        try:
            r = rodar(d["agente"], d["tarefa"], evento=task["type"],
                      timeout_min=cfg["agente_timeout_minutos"], max_turnos=cfg["agente_max_turnos"])
            status = "aguardando_aprovacao" if r["aprovacoes"] else ("ok" if r["ok"] else "erro")
            EventQueue.finish_task(task, status, r["arquivo"])
            (log.info if r["ok"] else log.error)("evento %s: %s (%s, %d aprovação(ões))",
                                                 task["type"], status, r["arquivo"], r["aprovacoes"])
            feitas.append({**task, "status": status, "resultado": r})
        except Exception as e:
            EventQueue.finish_task(task, "erro", f"{type(e).__name__}: {e}")
            log.exception("evento %s falhou", task["type"])
            feitas.append({**task, "status": "erro"})
    return feitas


def ciclo(cfg=None, rodar=run_claude_agent.rodar, agora=None, api_meta=None, rotinas_fn=None):
    cfg = cfg or config.carregar()
    agora_ = agora or datetime.now()
    m = coletar_metricas.coletar(api_meta=api_meta)
    eventos, avisos, estado = regras.avaliar(m, regras.ler_estado(), cfg, agora_)
    feitas, ev_rotinas, estado = rotinas.rodar(cfg, estado, agora_, rotinas_fn)
    for r in feitas:
        (log.info if r["ok"] else log.error)("rotina %s: %s", r["rotina"], r["resumo"])
    eventos += ev_rotinas
    estado["ultimas_rotinas"] = [r for r in estado.get("ultimas_rotinas", []) if r.get("data") == agora_.date().isoformat()] \
        + [{**r, "data": agora_.date().isoformat()} for r in feitas]
    for a in avisos:
        log.warning(a)
    for e in eventos:
        if EventQueue.add_event(e["type"], e["details"]):
            log.info("enfileirado: %s", e["type"])
    regras.gravar_estado(estado)
    (caminhos.logs() / "daemon.heartbeat").write_text(m["gerado_em"], encoding="utf-8")
    tarefas = processar_fila(cfg, rodar)
    arquivo_resumo = resumo.gerar(m, agora_)
    try:
        central.salvar(caminhos.logs() / "central.md", com_orquestrador=True, agora=agora_)
    except Exception:
        log.exception("central não foi atualizada")
    return {"metricas": m, "eventos": eventos, "avisos": avisos, "rotinas": feitas, "tarefas": tarefas,
            "resumo": str(arquivo_resumo)}


def _ja_rodando(cfg):
    hb = caminhos.logs() / "daemon.heartbeat"
    return hb.exists() and time.time() - hb.stat().st_mtime < cfg["intervalo_minutos"] * 60 * 2 \
        and (caminhos.logs() / "daemon.pid").exists()


def loop():
    cfg = config.carregar()
    parar = caminhos.logs() / "PARAR"
    if _ja_rodando(cfg):
        print("Já há um daemon rodando (logs/daemon.pid). Use 'parar' antes de iniciar outro.")
        return 1
    parar.unlink(missing_ok=True)
    (caminhos.logs() / "daemon.pid").write_text(str(os.getpid()), encoding="utf-8")
    log.info("daemon iniciado (pid %s, ciclo de %s min)", os.getpid(), cfg["intervalo_minutos"])
    try:
        while not parar.exists():
            try:
                ciclo(config.carregar())
            except Exception:
                log.exception("ciclo falhou; tento de novo no próximo")
            fim = time.monotonic() + cfg["intervalo_minutos"] * 60
            while time.monotonic() < fim and not parar.exists():
                time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        parar.unlink(missing_ok=True)
        (caminhos.logs() / "daemon.pid").unlink(missing_ok=True)
        log.info("daemon encerrado")
    return 0


def status():
    q = EventQueue.snapshot()
    f = caminhos.logs() / "aprovacoes.json"
    aprov = [a for a in (json.loads(f.read_text(encoding="utf-8")) if f.exists() else []) if a["status"] == "aguardando_max"]
    hb = caminhos.logs() / "daemon.heartbeat"
    print(f"Daemon: {'rodando' if _ja_rodando(config.carregar()) else 'parado'}"
          + (f" (último ciclo {hb.read_text(encoding='utf-8')})" if hb.exists() else ""))
    print(f"Fila: {len(q['pending_tasks'])} pendente(s)")
    for t in q["history"][-5:]:
        print(f"  {t.get('started_at', '')} {t['type']} → {t['details'].get('agente')}: {t.get('status', 'rodando')}")
    print(f"Aprovações aguardando você: {len(aprov)} (detalhes: comando aprovacoes)")
    hoje = caminhos.logs() / "resumo" / f"{datetime.now():%Y-%m-%d}.md"
    if hoje.exists():
        print(f"Resumo do dia: {hoje}")
    return 0


def main(argv):
    caminhos.terminal_utf8()
    configurar_logs()
    cmd = argv[1] if len(argv) > 1 else "rodar"
    if cmd == "rodar":
        return loop()
    if cmd == "uma-vez":
        r = ciclo()
        print(json.dumps({"eventos": [e["type"] for e in r["eventos"]], "avisos": r["avisos"],
                          "rotinas": [{"rotina": x["rotina"], "ok": x["ok"], "resumo": x["resumo"]} for x in r["rotinas"]],
                          "tarefas": [{"tipo": t["type"], "status": t["status"]} for t in r["tarefas"]],
                          "resumo": r["resumo"]},
                         indent=2, ensure_ascii=False))
        return 0
    if cmd == "status":
        return status()
    if cmd == "aprovacoes":
        print(aprovacoes.texto_lista())
        return 0
    if cmd in ("aprovar", "recusar"):
        if len(argv) < 3 or not argv[2].isdigit():
            print(f"Uso: {cmd} <número> [nota]. Veja os números com: aprovacoes")
            return 2
        try:
            p = aprovacoes.decidir(int(argv[2]), cmd == "aprovar", " ".join(argv[3:]))
        except ValueError as e:
            print(e)
            return 1
        print(f"Pedido {argv[2]} {'aprovado' if cmd == 'aprovar' else 'recusado'}: {p['acao']}")
        if cmd == "aprovar" and aprovacoes.link(p):
            print(f"Agora é com você: {aprovacoes.link(p)}")
        return 0
    if cmd == "parar":
        (caminhos.logs() / "PARAR").write_text("parar", encoding="utf-8")
        print("Pedido de parada enviado: o daemon encerra em até 5 segundos (ou ao fim do agente em andamento).")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
