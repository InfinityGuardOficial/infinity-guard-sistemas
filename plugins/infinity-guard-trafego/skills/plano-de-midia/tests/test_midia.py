import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import midia as md  # noqa: E402


class Plano(unittest.TestCase):
    def test_cpa_e_roas(self):
        p = md.plano(1000, 0.4, meta_vendas=10, dias=20, prova_ok=True)
        self.assertEqual(p["cpa_maximo"], 400)
        self.assertEqual(p["cpa_alvo"], 240)
        self.assertEqual(p["roas_equilibrio"], 2.5)
        self.assertEqual(p["orcamento_total"], 2400)
        self.assertEqual(p["orcamento_dia"], 120)

    def test_sem_prova_sem_frio(self):
        p = md.plano(1000, 0.4, meta_vendas=10)
        self.assertNotIn("frio", p["por_funil_dia"])
        self.assertTrue(any("prova da loja" in a for a in p["avisos"]))

    def test_orcamento_define_vendas(self):
        p = md.plano(1000, 0.4, orcamento_dia=24, dias=30, prova_ok=True)
        self.assertEqual(p["vendas_esperadas"], 3)

    def test_margem_invalida(self):
        with self.assertRaises(ValueError):
            md.plano(1000, 35)

    def test_ticket_do_kit_soma_catalogo(self):
        self.assertAlmostEqual(md.ticket_do_kit("kit-casa-vigiada"), 392.35 + 875.50, places=2)


class Avaliar(unittest.TestCase):
    def test_regua(self):
        csv = "conjunto;gasto;compras;receita\nA;100,00;5;5.000,00\nB;900,00;0;0\nC;50;0;0\nD;2.000,00;4;4.000\nE;1.200;4;4.000\n"
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv)
        r = {c["conjunto"]: c["decisao"] for c in md.avaliar(md.ler_resultados(f.name), 1000, 0.4)["conjuntos"]}
        # CPA máx 400, alvo 240
        self.assertEqual(r, {"A": "ESCALAR", "B": "PAUSAR", "C": "OBSERVAR", "D": "PAUSAR", "E": "MANTER"})


if __name__ == "__main__":
    unittest.main()
