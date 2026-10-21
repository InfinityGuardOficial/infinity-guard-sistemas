import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from base import FIXTURES, Sandbox  # noqa: E402
from core import aprovacoes, config, daemon_orchestrator as d  # noqa: E402
from tools import coletar_metricas, fontes_externas, metricas_meta, metricas_vendas  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
LINK = "https://docs.google.com/spreadsheets/d/AbC-123_x/edit#gid=42"


def servidor(respostas, pedidos=None):
    """Imita urllib.request.urlopen: devolve o texto de cada URL (ou levanta o erro)."""
    @contextmanager
    def abrir(req, timeout=None):
        url = req.full_url
        if pedidos is not None:
            pedidos.append(url)
        r = respostas[url]
        if isinstance(r, Exception):
            raise r
        yield io.BytesIO(r.encode("utf-8"))
    return abrir


class Fontes(Sandbox):
    def config_local(self, fontes):
        (self.home / "config").mkdir(exist_ok=True)
        (self.home / "config" / "orquestrador.local.json").write_text(json.dumps({"fontes": fontes}), encoding="utf-8")

    def test_link_da_planilha_vira_csv(self):
        self.assertEqual(fontes_externas.url_csv(LINK),
                         "https://docs.google.com/spreadsheets/d/AbC-123_x/export?format=csv&gid=42")
        self.assertEqual(fontes_externas.url_csv("https://docs.google.com/spreadsheets/d/AbC/edit"),
                         "https://docs.google.com/spreadsheets/d/AbC/export?format=csv")
        publicado = "https://docs.google.com/spreadsheets/d/e/2PACX-1/pub?output=csv"
        self.assertEqual(fontes_externas.url_csv(publicado), publicado)

    def test_sem_config_nao_baixa_nada(self):
        self.assertEqual(fontes_externas.sincronizar(abrir=servidor({})), [])

    def test_planilhas_alimentam_vendas_e_meta(self):
        self.config_local({"planilhas": {"nuvemshop": LINK, "conversas": None,
                                         "meta": "https://docs.google.com/spreadsheets/d/M/pub?output=csv"}})
        abrir = servidor({fontes_externas.url_csv(LINK): (FIXTURES / "vendas_exemplo.csv").read_text(encoding="utf-8"),
                          "https://docs.google.com/spreadsheets/d/M/pub?output=csv":
                              (FIXTURES / "meta_resultados.csv").read_text(encoding="utf-8")})
        m = coletar_metricas.coletar(gravar=False, abrir=abrir)
        self.assertEqual([p["ok"] for p in m["planilhas"]], [True, True])
        self.assertTrue(m["vendas"]["ok"])
        self.assertEqual(m["vendas"]["arquivo"], "planilha-pedidos.csv")
        self.assertEqual(m["meta"]["arquivo"], "planilha-meta.csv")
        self.assertEqual(m["meta"]["gasto"], 570.0)

    def test_planilha_fechada_nao_apaga_a_anterior(self):
        self.config_local({"planilhas": {"meta": LINK}})
        destino = self.home / "dados" / "meta" / "planilha-meta.csv"
        destino.write_text("conjunto;gasto;compras;receita\nA;10;1;50\n", encoding="utf-8")
        r = fontes_externas.sincronizar(abrir=servidor({fontes_externas.url_csv(LINK): "<html>login</html>"}))
        self.assertFalse(r[0]["ok"])
        self.assertIn("Qualquer pessoa com o link", r[0]["motivo"])
        self.assertIn("A;10", destino.read_text(encoding="utf-8"))
        r = fontes_externas.sincronizar(abrir=servidor({fontes_externas.url_csv(LINK): OSError("sem internet")}))
        self.assertFalse(r[0]["ok"])
        self.assertTrue(metricas_meta.coletar()["ok"])

    def test_pasta_do_drive(self):
        drive = Path(tempfile.mkdtemp(prefix="ig-drive-"))
        self.addCleanup(shutil.rmtree, drive, True)
        (drive / "nuvemshop").mkdir()
        (drive / "meta").mkdir()
        shutil.copy(FIXTURES / "vendas_exemplo.csv", drive / "nuvemshop" / "vendas-drive.csv")
        shutil.copy(FIXTURES / "meta_resultados.csv", drive / "meta" / "meta-drive.csv")
        self.config_local({"pasta_drive": str(drive)})
        self.assertEqual(metricas_vendas.coletar()["arquivo"], "vendas-drive.csv")
        self.assertEqual(metricas_meta.coletar()["arquivo"], "meta-drive.csv")
        self.assertEqual(len(fontes_externas.pastas("app")), 1)  # sem subpasta app/ no Drive, só dados/app

    def test_config_padrao_tem_as_chaves(self):
        f = config.carregar()["fontes"]
        self.assertIsNone(f["pasta_drive"])
        self.assertEqual(set(f["planilhas"]), {"nuvemshop", "conversas", "meta"})


class AprovacaoRapida(Sandbox):
    def _pedidos(self, n=3):
        (self.home / "logs").mkdir(exist_ok=True)
        (self.home / "logs" / "aprovacoes.json").write_text(json.dumps([
            {"agente": "analista-de-vendas", "evento": "relatorio_diario", "acao": f"Cobrar o boleto <{i}>",
             "relatorio": f"r{i}.md", "status": "aguardando_max"} for i in range(1, n + 1)]), encoding="utf-8")

    def test_pagina(self):
        self._pedidos()
        html = aprovacoes.salvar_pagina(datetime(2026, 10, 21, 9, 0)).read_text(encoding="utf-8")
        self.assertIn("3 esperando você", html)
        self.assertIn("Cobrar o boleto &lt;2&gt;", html)
        self.assertIn("agentes/r1.md", html)
        self.assertIn("nuvemshop.com.br", html)
        self.assertIn("aprovar 1 2 3", html)
        aprovacoes.decidir_varios([1, 2, 3], False)
        self.assertIn("Nenhum pedido esperando você", (self.home / "logs" / "aprovacoes.html").read_text(encoding="utf-8"))

    def test_varios_pela_linha_de_comando(self):
        self._pedidos()
        run = lambda *a: subprocess.run([sys.executable, str(REPO / "core" / "daemon_orchestrator.py"), *a],  # noqa: E731
                                        capture_output=True, text=True, encoding="utf-8", env=os.environ.copy())
        r = run("aprovar", "1", "3", "feito", "no", "celular")
        self.assertEqual(r.returncode, 0, r.stderr)
        lista = aprovacoes.carregar()
        self.assertEqual([p["status"] for p in lista], ["aprovado_por_max", "aguardando_max", "aprovado_por_max"])
        self.assertEqual(lista[2]["nota"], "feito no celular")
        r = run("recusar", "2", "9")
        self.assertEqual(r.returncode, 1)
        self.assertIn("não existe o pedido 9", r.stdout)
        self.assertEqual(aprovacoes.carregar()[1]["status"], "recusado_por_max")

    def test_aviso(self):
        self.assertIsNone(aprovacoes.avisar(0, {}))
        self.assertIn("2 pedido(s) novo(s)", aprovacoes.avisar(2, {"avisar_no_windows": True}))

    def test_ciclo_avisa_e_gera_pagina(self):
        def rodar(agente, tarefa, evento, **k):
            lista = aprovacoes.carregar() + [{"agente": agente, "evento": evento, "acao": "Responder o cliente",
                                              "status": "aguardando_max"}]
            (self.home / "logs" / "aprovacoes.json").write_text(json.dumps(lista), encoding="utf-8")
            return {"ok": True, "arquivo": "x.md", "aprovacoes": 1}
        self.com_vendas()
        r = d.ciclo(rodar=rodar, agora=datetime(2026, 10, 20, 9, 0), rotinas_fn={})
        self.assertIn("pedido(s) novo(s)", r["aviso_aprovacoes"])
        self.assertIn("Responder o cliente", (self.home / "logs" / "aprovacoes.html").read_text(encoding="utf-8"))
