import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from base import Sandbox  # noqa: E402
from tools import coletar_metricas, metricas_meta, metricas_vendas  # noqa: E402


class Vendas(Sandbox):
    def test_sem_csv_nao_inventa(self):
        r = metricas_vendas.coletar()
        self.assertFalse(r["ok"])
        self.assertIn("nenhum CSV", r["motivo"])

    def test_le_csv_da_nuvemshop(self):
        self.com_vendas(conversas=True)
        r = metricas_vendas.coletar()
        self.assertTrue(r["ok"])
        self.assertEqual(r["arquivo"], "vendas.csv")
        self.assertEqual(r["arquivo_conversas"], "conversas.csv")
        self.assertGreater(r["pedidos_pagos"], 0)
        self.assertGreater(r["faturamento"], 0)
        self.assertIn("conversao", r["conversas"])


class Meta(Sandbox):
    def test_sem_fonte(self):
        self.assertFalse(metricas_meta.coletar()["ok"])

    def test_csv_do_gerenciador(self):
        self.com_meta()
        r = metricas_meta.coletar()
        self.assertEqual(r["fonte"], "meta_csv")
        self.assertEqual(r["gasto"], 570.0)
        self.assertEqual(r["compras"], 5)
        self.assertEqual(r["receita"], 1750.0)
        self.assertEqual(r["roas"], 3.07)
        self.assertEqual(r["cpa"], 114.0)

    def test_api_so_faz_get(self):
        pedidos = []

        class Resp(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def abrir(req, timeout):
            pedidos.append(req)
            return Resp(json.dumps({"data": [{"adset_name": "Quente", "adset_id": "1", "spend": "100.5",
                                              "actions": [{"action_type": "purchase", "value": "2"},
                                                          {"action_type": "link_click", "value": "40"}],
                                              "action_values": [{"action_type": "purchase", "value": "700"}]}]}).encode())

        api = metricas_meta.MetaAdsLeitura("tok", "123", abrir=abrir)
        r = metricas_meta.coletar(api=api)
        self.assertEqual(r["fonte"], "meta_api")
        self.assertEqual(r["conjuntos"][0], {"conjunto": "Quente", "id": "1", "gasto": 100.5, "compras": 2, "receita": 700.0})
        self.assertEqual([p.get_method() for p in pedidos], ["GET"])
        self.assertIn("/act_123/insights", pedidos[0].full_url)
        publicos = [m for m in dir(metricas_meta.MetaAdsLeitura) if not m.startswith("_")]
        self.assertEqual(sorted(publicos), ["conjuntos", "do_ambiente"])


class Coleta(Sandbox):
    def test_grava_metrics_json_sem_numero_inventado(self):
        m = coletar_metricas.coletar()
        self.assertIsNone(m["current_roas"])
        self.assertIsNone(m["conversion_rate"])
        salvo = json.loads((self.home / "logs" / "metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(salvo["gerado_em"], m["gerado_em"])

    def test_com_as_duas_fontes(self):
        self.com_vendas(conversas=True)
        self.com_meta()
        m = coletar_metricas.coletar()
        self.assertEqual(m["current_roas"], 3.07)
        self.assertIsNotNone(m["conversion_rate"])

    def test_fonte_quebrada_nao_derruba_a_outra(self):
        self.com_meta()
        (self.home / "dados" / "nuvemshop" / "vendas.csv").write_text("coluna_errada\nx\n", encoding="utf-8")
        m = coletar_metricas.coletar()
        self.assertFalse(m["vendas"]["ok"])
        self.assertTrue(m["meta"]["ok"])
