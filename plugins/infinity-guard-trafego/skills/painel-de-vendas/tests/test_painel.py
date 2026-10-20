import sys
import unittest
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
import painel  # noqa: E402

FIX = AQUI / "fixtures"


def carregar(conversas=False):
    linhas = painel.ler_csv(FIX / "vendas_exemplo.csv")
    col = painel.colunas(list(linhas[0].keys()))
    conv = painel.ler_csv(FIX / "conversas_exemplo.csv") if conversas else None
    return painel.metricas(painel.consolidar(linhas, col), conv, hoje=date(2026, 11, 30))


class Painel(unittest.TestCase):
    def test_um_pedido_por_numero_e_so_pagos(self):
        m = carregar()
        self.assertEqual(m["pedidos_pagos"], 3)
        self.assertEqual(m["pendentes"], 1)
        self.assertEqual(m["cancelados"], 1)
        self.assertAlmostEqual(m["faturamento"], 353.12 + 1141.07 + 1026.96, places=2)

    def test_pix_cupom_canal(self):
        m = carregar()
        self.assertAlmostEqual(m["pix_pct"], 0.667, places=3)
        self.assertEqual(dict(m["cupons"]), {"IG1111": 1, "IGBLACK": 1})
        self.assertEqual(dict(m["canais"])["whatsapp"], 2)
        self.assertEqual(dict(m["top_produtos"])["Câmera Wi-Fi Infinity Guard"], 3)

    def test_semana_comeca_na_segunda(self):
        self.assertIn("2026-11-09", carregar()["por_semana"])

    def test_conversas(self):
        c = carregar(conversas=True)["conversas"]
        self.assertEqual(c["total"], 4)
        self.assertEqual(c["vendas"], 2)
        self.assertEqual(c["recuperados"], 1)

    def test_numero_brasileiro(self):
        self.assertEqual(painel.numero("1.234,56"), 1234.56)
        self.assertEqual(painel.numero("R$ 1234.56"), 1234.56)
        self.assertEqual(painel.numero(""), 0.0)

    def test_coluna_faltando_explica(self):
        with self.assertRaises(ValueError) as e:
            painel.colunas(["Cliente", "Valor final"])
        self.assertIn("--mapear", str(e.exception))
        col = painel.colunas(["Pedido", "Criado em", "Valor final"], ["data=Criado em", "total=Valor final"])
        self.assertEqual(col["total"], "Valor final")

    def test_html(self):
        h = painel.para_html(carregar(conversas=True))
        self.assertIn("Painel de Vendas", h)
        self.assertIn("prefers-color-scheme:dark", h)
        self.assertIn("3 de 20", h)
        self.assertNotIn("http", h.split("<body>")[1])  # sem recursos externos


if __name__ == "__main__":
    unittest.main()
