import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from base import Sandbox  # noqa: E402
from tools import central  # noqa: E402

REPO = Path(__file__).resolve().parent.parent


class Central(Sandbox):
    def test_repositorio_com_links_que_existem(self):
        f = central.salvar(self.home / "docs" / "central.md")
        texto = f.read_text(encoding="utf-8")
        self.assertIn("23 funcionários em 7 squads", texto)
        self.assertIn("produtos ativos", texto)
        # todo link relativo aponta para um arquivo de verdade do repositório
        saida_no_repo = REPO / "docs" / "central-teste.md"
        try:
            saida_no_repo.write_text(central.gerar(REPO / "docs"), encoding="utf-8")
            for alvo in re.findall(r"\]\(([^)]+)\)", saida_no_repo.read_text(encoding="utf-8")):
                if not alvo.startswith("http"):
                    self.assertTrue((REPO / "docs" / alvo.replace("%20", " ")).exists(), alvo)
        finally:
            saida_no_repo.unlink(missing_ok=True)

    def test_com_orquestrador(self):
        (self.home / "logs").mkdir(exist_ok=True)
        (self.home / "logs" / "aprovacoes.json").write_text(json.dumps([
            {"agente": "lider-trafego", "acao": "Pausar o conjunto X", "status": "aguardando_max"},
            {"agente": "lider-trafego", "acao": "já decidido", "status": "recusado_por_max"}]), encoding="utf-8")
        texto = central.gerar(self.home / "logs", com_orquestrador=True)
        self.assertIn("1 pedido(s)", texto)
        self.assertIn("Pausar o conjunto X", texto)
        self.assertNotIn("já decidido", texto)

    def test_copia_do_projeto_usa_links_do_github(self):
        projeto = self.home / "projeto"
        (projeto / "infinity-guard" / "verificacao").mkdir(parents=True)
        (projeto / "infinity-guard" / "verificacao" / "2026-10-19-verificacao-geral.md").write_text("x", encoding="utf-8")
        central._github = True
        try:
            texto = central.gerar(projeto / "infinity-guard" / "central", projeto=projeto)
        finally:
            central._github = False
        self.assertIn(central.GITHUB + "README.md", texto)
        self.assertIn("../verificacao/2026-10-19-verificacao-geral.md", texto)
        self.assertNotIn("Relatório de Posicionamento", texto)  # só lista o que existe
