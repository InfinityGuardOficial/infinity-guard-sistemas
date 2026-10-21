"""Regra de suporte (21/10/2026): a loja tira dúvidas, não configura o produto por WhatsApp nem por vídeo.

Varre o material da equipe (agentes, skills, docs, app, orquestrador) com a regra `configuracao-pela-loja`
do revisor de promessas: nenhum texto pode prometer configuração pela loja.
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "skills" / "revisor-de-promessas" / "scripts"))
import revisar as rv  # noqa: E402

PASTAS = ["agents", "skills", "docs", "app", "core", "tools", "mcp_servers", "plugins"]
SOLTOS = ["CLAUDE.md", ".claude/CLAUDE.md", "README.md"]
EXTENSOES = {".md", ".json", ".py", ".txt", ".html"}
# Onde a promessa aparece de propósito: a própria regra e os casos de teste do revisor.
IGNORAR = {"regras.json", "test_revisor.py"}


def arquivos():
    for nome in SOLTOS:
        yield REPO / nome
    for pasta in PASTAS:
        for f in sorted((REPO / pasta).rglob("*")):
            if f.is_file() and f.suffix in EXTENSOES and f.name not in IGNORAR and "__pycache__" not in f.parts:
                yield f


class RegraDeSuporte(unittest.TestCase):
    def test_nenhum_material_promete_configurar_por_whatsapp_ou_video(self):
        regras = [r for r in rv.carregar_regras() if r["id"] == "configuracao-pela-loja"]
        self.assertEqual(len(regras), 1)
        achados = []
        for f in arquivos():
            for a in rv.revisar(f.read_text(encoding="utf-8"), regras)["achados"]:
                if a["gravidade"] == "bloqueia":
                    achados.append(f"{f.relative_to(REPO)}:{a['linha']}: {a['trecho']}")
        self.assertEqual(achados, [], "\n".join(achados))

    def test_regras_da_casa_explicam_o_que_a_loja_faz(self):
        for nome in ("CLAUDE.md", ".claude/CLAUDE.md"):
            texto = (REPO / nome).read_text(encoding="utf-8")
            self.assertIn("manual de instruções acompanha o produto", texto, nome)
        for f in sorted((REPO / "agents").glob("*.md")):
            self.assertIn("Nunca prometa configurar o produto para o cliente", f.read_text(encoding="utf-8"), f.name)


if __name__ == "__main__":
    unittest.main()
