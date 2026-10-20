import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import reuniao as rn  # noqa: E402


class Reuniao(unittest.TestCase):
    def test_anatel_e_prova_em_outubro(self):
        itens = rn.coletar(date(2026, 10, 19))
        textos = " ".join(i["texto"] for i in itens)
        self.assertIn("Anatel", textos)
        self.assertIn("sem público frio", textos)
        self.assertEqual(itens[0]["prioridade"], 1)

    def test_black_friday_perto(self):
        textos = " ".join(i["texto"] for i in rn.coletar(date(2026, 11, 16)))
        self.assertIn("Black Friday em 10 dias", textos)

    def test_durante_e_depois(self):
        self.assertIn("acontecendo agora", " ".join(i["texto"] for i in rn.coletar(date(2026, 11, 27))))
        self.assertIn("pós-venda", " ".join(i["texto"] for i in rn.coletar(date(2026, 12, 3))))

    def test_catalogo_velho(self):
        self.assertIn("Catálogo com", " ".join(i["texto"] for i in rn.coletar(date(2026, 12, 31))))

    def test_md_tem_todos_os_squads_com_item(self):
        hoje = date(2026, 10, 19)
        md = rn.para_md(rn.coletar(hoje), hoje)
        self.assertIn("## Top 3 da semana", md)
        for sq in ("Operações e Loja", "Tráfego Pago", "Direção"):
            self.assertIn(f"## {sq}", md)

    def test_toda_linha_tem_fonte(self):
        for i in rn.coletar(date(2026, 10, 19)):
            self.assertTrue(i["fonte"])
            self.assertIn(i["squad"], rn.SQUADS)


if __name__ == "__main__":
    unittest.main()
