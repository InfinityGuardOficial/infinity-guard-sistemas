import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from base import Sandbox  # noqa: E402
from core import config, daemon_orchestrator as d, regras  # noqa: E402
from core.event_queue import EventQueue  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
TERCA_9H = datetime(2026, 10, 20, 9, 0)
SEGUNDA_9H = datetime(2026, 10, 19, 9, 0)


def falso(chamadas, aprovacoes=0, ok=True):
    def rodar(agente, tarefa, evento, **k):
        chamadas.append((evento, agente))
        return {"ok": ok, "arquivo": f"{evento}.md", "aprovacoes": aprovacoes, "simulacao": False}
    return rodar


class Regras(Sandbox):
    def test_sem_dados_so_avisa(self):
        eventos, avisos, _ = regras.avaliar({"vendas": {"ok": False, "motivo": "x"}, "meta": {"ok": False, "motivo": "y"}},
                                            {}, config.carregar(), TERCA_9H)
        self.assertEqual(eventos, [])
        self.assertEqual(len(avisos), 2)

    def test_reuniao_na_segunda(self):
        eventos, _, estado = regras.avaliar({"vendas": {"ok": False}, "meta": {"ok": False}}, {}, config.carregar(), SEGUNDA_9H)
        self.assertEqual([e["type"] for e in eventos], ["reuniao_semanal"])
        self.assertEqual(eventos[0]["details"]["agente"], "diretor-geral")
        again, _, _ = regras.avaliar({"vendas": {"ok": False}, "meta": {"ok": False}}, estado, config.carregar(), SEGUNDA_9H)
        self.assertEqual(again, [])

    def test_config_local_sobrepoe(self):
        (self.home / "config").mkdir()
        (self.home / "config" / "orquestrador.local.json").write_text('{"intervalo_minutos": 5}', encoding="utf-8")
        cfg = config.carregar()
        self.assertEqual(cfg["intervalo_minutos"], 5)
        self.assertEqual(cfg["margem_bruta"], 0.35)


class Ciclo(Sandbox):
    def test_ciclo_completo(self):
        self.com_vendas(conversas=True)
        self.com_meta()
        chamadas = []
        r = d.ciclo(rotinas_fn={}, rodar=falso(chamadas, aprovacoes=1), agora=TERCA_9H)
        tipos = [e["type"] for e in r["eventos"]]
        self.assertIn("relatorio_diario", tipos)
        self.assertIn("revisar_conjuntos", tipos)
        self.assertNotIn("novas_vendas", tipos)  # primeiro ciclo só registra quantos pedidos já existem
        self.assertEqual(sorted(chamadas), sorted((e["type"], e["details"]["agente"]) for e in r["eventos"]))
        self.assertEqual(EventQueue.snapshot()["pending_tasks"], [])
        self.assertEqual({h["status"] for h in EventQueue.snapshot()["history"]}, {"aguardando_aprovacao"})
        self.assertTrue((self.home / "logs" / "metrics.json").exists())

        # segundo ciclo no mesmo dia, sem mudança: nada novo
        chamadas.clear()
        r2 = d.ciclo(rotinas_fn={}, rodar=falso(chamadas), agora=TERCA_9H)
        self.assertEqual(r2["eventos"], [])
        self.assertEqual(chamadas, [])

    def test_venda_nova_chama_pos_venda(self):
        self.com_vendas()
        regras.gravar_estado({"pedidos_pagos": 1, "ultimo_relatorio": TERCA_9H.date().isoformat()})
        chamadas = []
        r = d.ciclo(rotinas_fn={}, rodar=falso(chamadas), agora=TERCA_9H)
        self.assertEqual(chamadas, [("novas_vendas", "guardiao-pos-venda")])
        self.assertGreater(r["eventos"][0]["details"]["novos"], 0)

    def test_agente_que_quebra_nao_derruba_o_ciclo(self):
        self.com_vendas()

        def explode(*a, **k):
            raise RuntimeError("claude fora do ar")
        r = d.ciclo(rotinas_fn={}, rodar=explode, agora=TERCA_9H)
        self.assertEqual([t["status"] for t in r["tarefas"]], ["erro"])
        self.assertIn("claude fora do ar", EventQueue.snapshot()["history"][-1]["saida"])

    def test_rodar_agentes_desligado(self):
        self.com_vendas()
        cfg = config.carregar()
        cfg["rodar_agentes"] = False
        chamadas = []
        d.ciclo(cfg, rotinas_fn={}, rodar=falso(chamadas), agora=TERCA_9H)
        self.assertEqual(chamadas, [])
        self.assertEqual(EventQueue.snapshot()["history"][-1]["status"], "pulada")


class Linha_de_comando(Sandbox):
    def _rodar(self, *args):
        import os
        return subprocess.run([sys.executable, str(REPO / "core" / "daemon_orchestrator.py"), *args],
                              capture_output=True, text=True, encoding="utf-8", env=os.environ.copy(), timeout=60)

    def test_uma_vez_status_parar(self):
        self.com_vendas()
        (self.home / "config").mkdir()
        (self.home / "config" / "orquestrador.local.json").write_text(  # sem internet no teste
            '{"rotinas": {"auditoria": {"ativa": false}}}', encoding="utf-8")
        r = self._rodar("uma-vez")
        self.assertEqual(r.returncode, 0, r.stderr)
        saida = json.loads(r.stdout)
        self.assertTrue(all(t["status"] in ("ok", "aguardando_aprovacao") for t in saida["tarefas"]))
        s = self._rodar("status")
        self.assertEqual(s.returncode, 0, s.stderr)
        self.assertIn("Fila: 0 pendente(s)", s.stdout)
        self.assertIn("system.log", [p.name for p in (self.home / "logs").iterdir()])
        p = self._rodar("parar")
        self.assertEqual(p.returncode, 0)
        self.assertTrue((self.home / "logs" / "PARAR").exists())

    def test_loop_encerra_com_parar(self):
        import os
        import time
        (self.home / "config").mkdir()
        (self.home / "config" / "orquestrador.local.json").write_text('{"intervalo_minutos": 1}', encoding="utf-8")
        proc = subprocess.Popen([sys.executable, str(REPO / "core" / "daemon_orchestrator.py")], env=os.environ.copy(),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                if (self.home / "logs" / "daemon.heartbeat").exists():
                    break
                time.sleep(0.1)
            self.assertTrue((self.home / "logs" / "daemon.pid").exists())
            segundo = self._rodar()
            self.assertEqual(segundo.returncode, 1)
            self.assertIn("Já há um daemon", segundo.stdout)
            self._rodar("parar")
            self.assertEqual(proc.wait(timeout=20), 0)
            self.assertFalse((self.home / "logs" / "daemon.pid").exists())
        finally:
            proc.kill()
