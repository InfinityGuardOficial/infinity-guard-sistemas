import copy
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import catalogo as cg  # noqa: E402

HOJE = date(2026, 10, 19)


class Catalogo(unittest.TestCase):
    def setUp(self):
        self.cat = cg.carregar(cg.caminho_catalogo())

    def test_catalogo_atual_valido(self):
        r = cg.validar(self.cat, HOJE)
        self.assertTrue(r["ok"], r["erros"])

    def test_detecta_pix_errado(self):
        c = copy.deepcopy(self.cat)
        c["produtos"][0]["pix"] = 1.0
        self.assertFalse(cg.validar(c, HOJE)["ok"])

    def test_parcelas_max_por_produto(self):
        c = copy.deepcopy(self.cat)
        p = next(x for x in c["produtos"] if x["id"] == "kit-cam-2")
        p.update({"parcelas_max": 7, "preco": 392.35, "pix": 353.12, "parcelas": 7, "parcela_valor": 56.05})
        self.assertTrue(cg.validar(c, HOJE)["ok"])
        p["parcelas"], p["parcela_valor"] = 12, 32.70
        self.assertFalse(cg.validar(c, HOJE)["ok"])

    def test_atualizar_recalcula(self):
        c = copy.deepcopy(self.cat)
        next(x for x in c["produtos"] if x["id"] == "kit-cam-2").pop("parcelas_max", None)  # regra geral (até 12x, mínimo R$ 30)
        mud = cg.atualizar(c, "kit-cam-2", preco=300.0, hoje=HOJE)
        p = next(x for x in c["produtos"] if x["id"] == "kit-cam-2")
        self.assertEqual(p["pix"], 270.0)
        self.assertEqual(p["parcelas"], 10)
        self.assertEqual(p["parcela_valor"], 30.0)
        self.assertIn("preco", mud)
        self.assertEqual(c["atualizado_em"], "2026-10-19")
        self.assertTrue(cg.validar(c, HOJE)["ok"])

    def test_preco_de_menor_recusado(self):
        with self.assertRaises(ValueError):
            cg.atualizar(copy.deepcopy(self.cat), "kit-cam-2", preco=500.0, preco_de=450.0)

    def test_margem(self):
        r = cg.margens(self.cat, {"kit-cam-2": 200.0}, taxa=0.05, minima=0.5)
        pix = next(x for x in r["linhas"] if x["forma"] == "pix")
        self.assertAlmostEqual(pix["lucro"], 353.12 * 0.95 - 200, places=2)
        self.assertTrue(pix["abaixo"])
        self.assertIn("alarme-ikerui", r["sem_custo"])

    def test_estoque(self):
        r = {x["id"]: x["acao"] for x in cg.estoque_baixo(self.cat, {"kit-cam-2": 0, "alarme-ikerui": 2, "cartao-64": 10})}
        self.assertIn("desativar", r["kit-cam-2"])
        self.assertIn("repor", r["alarme-ikerui"])
        self.assertIn("reativar", r["cartao-64"])


if __name__ == "__main__":
    unittest.main()
