import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from base import Sandbox  # noqa: E402
from tools import run_claude_agent as rca  # noqa: E402

RESPOSTA = """Resumo: 3 vendas.

## Pedidos de aprovação
- Pausar o conjunto WhatsApp quente (gastou 300 sem venda)
- Subir 20% no Remarketing 7 dias

## Observação
nada mais
"""


def _bash():
    """No Windows, "bash" no PATH costuma ser o do WSL; o script é para o Git Bash, que fica ao lado do git."""
    if os.name == "nt" and shutil.which("git"):
        git_bash = Path(shutil.which("git")).resolve().parent.parent / "bin" / "bash.exe"
        if git_bash.exists():
            return str(git_bash)
    return "bash"


class Agente(Sandbox):
    def test_comando_em_modo_leitura(self):
        cmd, prompt = rca.comando("analista-de-vendas", "resuma")
        self.assertIn("-p", cmd)
        self.assertIn("--plugin-dir", cmd)
        permitidas = cmd[cmd.index("--allowedTools") + 1:cmd.index("--disallowedTools")]
        proibidas = cmd[cmd.index("--disallowedTools") + 1:]
        self.assertNotIn("Write", permitidas)
        self.assertNotIn("Edit", permitidas)
        self.assertFalse(any(p.startswith("mcp__") for p in permitidas))
        self.assertIn("mcp__Meta", proibidas)
        self.assertIn("infinity-guard:analista-de-vendas", prompt)
        self.assertIn("Não gaste dinheiro", prompt)
        self.assertFalse(any("\n" in c for c in cmd))  # prompt vai pela entrada padrão

    def test_agente_inexistente(self):
        with self.assertRaises(ValueError):
            rca.comando("estagiario", "x")

    def test_todos_os_23_agentes(self):
        self.assertEqual(len(rca.AGENTES), 23)

    def test_extrai_pedidos_de_aprovacao(self):
        self.assertEqual(rca.pedidos_de_aprovacao(RESPOSTA),
                         ["Pausar o conjunto WhatsApp quente (gastou 300 sem venda)", "Subir 20% no Remarketing 7 dias"])
        self.assertEqual(rca.pedidos_de_aprovacao("sem seção"), [])
        self.assertEqual(rca.pedidos_de_aprovacao("## Pedidos de aprovação\n- Nenhuma ação recomendada.\n"), [])

    def test_simulacao_nao_chama_claude(self):
        r = rca.rodar("analista-de-vendas", "resuma", evento="teste",
                      executar=lambda *a, **k: self.fail("não devia chamar o Claude"))
        self.assertTrue(r["simulacao"])
        self.assertIn("simulação", Path(r["arquivo"]).read_text(encoding="utf-8"))

    def test_resposta_vira_aprovacao_pendente(self):
        os.environ["IG_DRY_RUN"] = "0"
        os.environ["IG_CLAUDE_BIN"] = "claude-falso"
        try:
            r = rca.rodar("analista-de-midia", "avalie", evento="revisar_conjuntos",
                          executar=lambda cmd, **k: (self.assertIn("analista-de-midia", k["input"]),
                                                     subprocess.CompletedProcess(cmd, 0, RESPOSTA, ""))[1])
        finally:
            os.environ.pop("IG_CLAUDE_BIN")
        self.assertEqual(r["aprovacoes"], 2)
        lista = json.loads((self.home / "logs" / "aprovacoes.json").read_text(encoding="utf-8"))
        self.assertEqual({a["status"] for a in lista}, {"aguardando_max"})
        self.assertEqual(lista[0]["agente"], "analista-de-midia")

    def test_script_sh_valida_argumentos(self):
        sh = Path(__file__).resolve().parent.parent / "tools" / "run_claude_agent.sh"
        bash = _bash()
        r = subprocess.run([bash, str(sh)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 2)
        r = subprocess.run([bash, str(sh), "analista-de-vendas", "resuma", "teste_sh"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)["simulacao"])
