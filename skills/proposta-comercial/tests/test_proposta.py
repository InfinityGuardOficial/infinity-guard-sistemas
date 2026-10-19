import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import proposta as pr  # noqa: E402

HOJE = date(2026, 10, 19)


class Proposta(unittest.TestCase):
    def setUp(self):
        self.cat = pr.carregar_catalogo()

    def test_totais_do_catalogo(self):
        p = pr.montar("Padaria", "comercio", {"kit-cam-2": 2, "alarme-ikerui": 1}, self.cat, hoje=HOJE)
        self.assertAlmostEqual(p["total"], 392.35 * 2 + 875.50, places=2)
        self.assertAlmostEqual(p["pix"], round(p["total"] * 0.9, 2), places=2)
        self.assertLessEqual(p["parcelas"], 12)

    def test_desconto_limite(self):
        with self.assertRaises(ValueError):
            pr.montar("X", "comercio", {"kit-cam-2": 1}, self.cat, desconto=0.2, hoje=HOJE)

    def test_inativo_e_inexistente(self):
        with self.assertRaises(ValueError):
            pr.montar("X", "comercio", {"cartao-64": 1}, self.cat, hoje=HOJE)
        with self.assertRaises(ValueError):
            pr.montar("X", "comercio", {"camera-4g": 1}, self.cat, hoje=HOJE)

    def test_aviso_acima_de_3000_e_sem_custo(self):
        p = pr.montar("Cond", "condominio", {"fechadura-facial": 2}, self.cat, desconto=0.05, hoje=HOJE)
        self.assertTrue(any("dono revisa" in a for a in p["avisos"]))
        self.assertTrue(any("margem" in a for a in p["avisos"]))

    def test_margem_minima(self):
        custos = {"kit-cam-2": 380.0}
        p = pr.montar("X", "comercio", {"kit-cam-2": 1}, self.cat, 0.05, custos=custos, margem_minima=0.2, hoje=HOJE)
        self.assertTrue(any("abaixo da mínima" in a for a in p["avisos"]))

    def test_ler_itens(self):
        self.assertEqual(pr.ler_itens("kit-cam-2:2, alarme-ikerui, kit-cam-2:1"), {"kit-cam-2": 3, "alarme-ikerui": 1})

    def test_md_nao_promete_instalacao(self):
        md = pr.para_md(pr.montar("X", "comercio", {"kit-cam-2": 1}, self.cat, hoje=HOJE))
        self.assertIn("Instalação no local", md.split("## O que não está incluso")[1])


if __name__ == "__main__":
    unittest.main()
