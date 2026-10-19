import copy
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import radar as rd  # noqa: E402


class Radar(unittest.TestCase):
    def setUp(self):
        self.base = rd.carregar()
        self.nossos = rd.catalogo()

    def test_toda_leitura_tem_fonte_e_id_valido(self):
        for l in self.base["leituras"]:
            self.assertTrue(l["fonte"])
            self.assertIn(l["equivale"], self.nossos)

    def test_kit_cam_acima_do_mercado(self):
        res = {x["id"]: x for x in rd.comparar(self.base["leituras"], self.nossos)}
        self.assertGreater(res["kit-cam-2"]["diferenca"], 0.25)
        self.assertIn("acima", res["kit-cam-2"]["leitura"])

    def test_mais_recente_vence(self):
        ls = copy.deepcopy(self.base["leituras"])
        ls.append({**ls[0], "data": "2026-11-01", "preco": 100.0})
        rec = [l for l in rd.mais_recentes(ls) if l["produto"] == ls[0]["produto"]]
        self.assertEqual(len(rec), 1)
        self.assertEqual(rec[0]["preco"], 100.0)

    def test_registrar_exige_fonte(self):
        with self.assertRaises(ValueError):
            rd.registrar(copy.deepcopy(self.base), {"concorrente": "X", "produto": "Y", "equivale": "kit-cam-2",
                                                    "preco": 10.0, "fonte": "", "data": "2026-10-19"})

    def test_velhas(self):
        self.assertEqual(len(rd.velhas(self.base["leituras"], 30, date(2026, 10, 19))), 0)
        self.assertGreater(len(rd.velhas(self.base["leituras"], 30, date(2026, 12, 31))), 0)


if __name__ == "__main__":
    unittest.main()
