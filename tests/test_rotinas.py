import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from base import Sandbox  # noqa: E402
from core import aprovacoes, config, resumo, rotinas  # noqa: E402
from core import daemon_orchestrator as d  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SEGUNDA_9H = datetime(2026, 10, 19, 9, 0)
TERCA_9H = datetime(2026, 10, 20, 9, 0)
QUINTA_9H = datetime(2026, 10, 22, 9, 0)
HOJE_9H = datetime.now().replace(hour=9, minute=0)  # o histórico da fila usa a hora real


class Agenda(Sandbox):
    def test_diarias_e_semanais(self):
        cfg = config.carregar()
        self.assertEqual(rotinas.devidas(cfg, {}, TERCA_9H), ["catalogo", "gestao"])
        self.assertEqual(rotinas.devidas(cfg, {}, SEGUNDA_9H), ["catalogo", "gestao", "conteudo"])
        self.assertIn("auditoria", rotinas.devidas(cfg, {}, QUINTA_9H))
        self.assertEqual(rotinas.devidas(cfg, {}, datetime(2026, 10, 20, 6, 0)), [])  # antes da hora do relatório

    def test_nao_repete_no_dia_e_falha_nao_derruba(self):
        def quebra(hoje):
            raise RuntimeError("sem internet")
        cfg = config.carregar()
        res, ev, estado = rotinas.rodar(cfg, {}, TERCA_9H, {"catalogo": lambda h: ("ok", None), "gestao": quebra})
        self.assertEqual([(r["rotina"], r["ok"]) for r in res], [("catalogo", True), ("gestao", False)])
        self.assertIn("sem internet", res[1]["resumo"])
        res2, _, _ = rotinas.rodar(cfg, estado, TERCA_9H, {"catalogo": lambda h: ("ok", None), "gestao": quebra})
        self.assertEqual(res2, [])

    def test_rotina_desligada_no_config(self):
        (self.home / "config").mkdir()
        (self.home / "config" / "orquestrador.local.json").write_text('{"rotinas": {"gestao": {"ativa": false}}}',
                                                                      encoding="utf-8")
        self.assertEqual(rotinas.devidas(config.carregar(), {}, TERCA_9H), ["catalogo"])


class Scripts_de_verdade(Sandbox):
    def test_catalogo(self):
        resumo_, evento = rotinas.catalogo("2026-10-21")
        self.assertIn("produtos ativos", resumo_)
        self.assertTrue((self.home / "logs" / "rotinas" / "catalogo" / "2026-10-21.json").exists())
        if evento:
            self.assertEqual(evento["details"]["agente"], "gestor-de-catalogo")

    def test_gestao_sem_backup(self):
        resumo_, evento = rotinas.gestao("2026-10-21")
        self.assertIn("sem backup", resumo_)
        self.assertIsNone(evento)

    def test_gestao_com_backup(self):
        (self.home / "dados" / "app").mkdir()
        shutil.copy(REPO / "skills" / "monitor-de-gestao" / "tests" / "fixtures" / "backup.json",
                    self.home / "dados" / "app" / "backup.json")
        resumo_, evento = rotinas.gestao("2026-10-21")
        self.assertIn("alerta(s)", resumo_)
        self.assertIsNotNone(evento)
        self.assertEqual(evento["details"]["agente"], "lider-operacoes")

    def test_conteudo_gera_pauta_sem_registrar(self):
        historico = REPO / "skills" / "conteudo-semanal" / "pautas" / "historico.json"
        antes = historico.read_text(encoding="utf-8")
        resumo_, evento = rotinas.conteudo("2026-10-19")
        self.assertTrue((self.home / "logs" / "rotinas" / "conteudo" / "pauta-2026-10-19.md").exists())
        self.assertEqual(evento["details"]["agente"], "roteirista-de-reels")
        self.assertEqual(historico.read_text(encoding="utf-8"), antes)

    def test_radar(self):
        resumo_, evento = rotinas.radar("2026-10-21")
        self.assertTrue((self.home / "logs" / "rotinas" / "radar" / "2026-10-21.json").exists())
        if evento:
            self.assertEqual(evento["details"]["agente"], "detetive-de-mercado")

    def test_auditoria_com_resposta_gravada(self):
        pagina = {"url": "https://exemplo", "itens": [{"chave": "cnpj", "status": "falta"}, {"chave": "troca", "status": "ok"}]}
        antes = rotinas._script
        rotinas._script = lambda *a, **k: (0, json.dumps({"data": "2026-10-22", "paginas": [pagina], "falhas": []}), "")
        try:
            resumo_, evento = rotinas.auditoria("2026-10-22")
        finally:
            rotinas._script = antes
        self.assertIn("faltando: cnpj", resumo_)
        self.assertEqual(evento["details"]["agente"], "auditor-da-loja")


class Aprovacoes(Sandbox):
    def _pedidos(self):
        (self.home / "logs").mkdir(exist_ok=True)
        (self.home / "logs" / "aprovacoes.json").write_text(json.dumps([
            {"agente": "analista-de-midia", "evento": "revisar_conjuntos", "acao": "Pausar o conjunto X",
             "relatorio": "r.md", "status": "aguardando_max"},
            {"agente": "analista-de-vendas", "evento": "relatorio_diario", "acao": "Cobrar o boleto do pedido 1003",
             "relatorio": "s.md", "status": "aguardando_max"}]), encoding="utf-8")

    def test_listar_aprovar_recusar(self):
        self._pedidos()
        texto = aprovacoes.texto_lista()
        self.assertIn("2 pedido(s)", texto)
        self.assertIn("adsmanager.facebook.com", texto)
        self.assertIn("nuvemshop", texto)
        aprovacoes.decidir(1, True, "feito no celular")
        aprovacoes.decidir(2, False)
        lista = aprovacoes.carregar()
        self.assertEqual([p["status"] for p in lista], ["aprovado_por_max", "recusado_por_max"])
        self.assertEqual(lista[0]["nota"], "feito no celular")
        self.assertEqual(aprovacoes.texto_lista(), "Nenhum pedido esperando você.")
        with self.assertRaises(ValueError):
            aprovacoes.decidir(1, True)
        with self.assertRaises(ValueError):
            aprovacoes.decidir(9, True)

    def test_linha_de_comando(self):
        import os
        import subprocess
        self._pedidos()
        run = lambda *a: subprocess.run([sys.executable, str(REPO / "core" / "daemon_orchestrator.py"), *a],  # noqa: E731
                                        capture_output=True, text=True, encoding="utf-8", env=os.environ.copy())
        self.assertIn("1. [analista-de-midia]", run("aprovacoes").stdout)
        r = run("aprovar", "1", "ok")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Agora é com você", r.stdout)
        self.assertEqual(run("recusar", "1").returncode, 1)
        self.assertEqual(run("aprovar").returncode, 2)


class Resumo(Sandbox):
    def test_resumo_do_dia(self):
        self.com_vendas()
        self.com_meta()
        chamadas = []
        r = d.ciclo(rodar=lambda a, t, evento, **k: chamadas.append(a) or {"ok": True, "arquivo": "x.md", "aprovacoes": 0},
                    agora=HOJE_9H, rotinas_fn={"catalogo": lambda h: ("15 produtos", None)})
        texto = Path(r["resumo"]).read_text(encoding="utf-8")
        self.assertIn(f"Resumo do dia · {HOJE_9H:%d/%m/%Y}", texto)
        self.assertIn("pedido(s) pago(s)", texto)
        self.assertIn("ROAS 3.07", texto)
        self.assertIn("catalogo: ok · 15 produtos", texto)
        self.assertIn("analista-de-vendas", texto)

    def test_resumo_sem_dados(self):
        f = resumo.gerar({"vendas": {"ok": False, "motivo": "sem CSV"}, "meta": {"ok": False, "motivo": "sem token"}}, TERCA_9H)
        texto = f.read_text(encoding="utf-8")
        self.assertIn("Vendas: sem dados (sem CSV)", texto)
        self.assertIn("nada", texto)
