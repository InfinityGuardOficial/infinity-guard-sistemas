import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import carrinho  # noqa: E402
import exportar_prompt  # noqa: E402
from recomendar_kit import brl, carregar_catalogo, mensagem, recomendar  # noqa: E402


def ids(v):
    return {i["id"]: i["qtd"] for i in v["itens"]}


class Catalogo(unittest.TestCase):
    def test_pix_e_10_por_cento(self):
        for p in carregar_catalogo()["produtos"]:
            self.assertAlmostEqual(p["pix"], p["preco"] * 0.9, delta=0.011, msg=p["id"])

    def test_parcelas_batem_com_vitrine(self):
        for p in carregar_catalogo()["produtos"]:
            self.assertAlmostEqual(p["parcela_valor"] * p["parcelas"], p["preco"], delta=0.07, msg=p["id"])


class Recomendacao(unittest.TestCase):
    def test_apartamento_basico(self):
        r = recomendar("apartamento")
        self.assertEqual(ids(r["ideal"]), {"kit-cam-2": 1})
        self.assertEqual(r["ideal"]["pix"], 353.12)
        self.assertEqual(r["ideal"]["parcelas"], 12)

    def test_casa_grande_viaja_com_porta(self):
        r = recomendar("casa", pontos=5, viaja=True, porta="digital")
        self.assertEqual(ids(r["ideal"]), {"cam-asecam-ptz": 1, "kit-cam-2": 2, "alarme-ikerui": 1,
                                           "fechadura-bio": 1, "sensor-presenca": 1})
        esperado = 407.17 + 2 * 392.35 + 875.50 + 1218.54 + 71.98
        self.assertAlmostEqual(r["ideal"]["total"], esperado, places=2)

    def test_sitio_sem_wifi_nao_vende_camera(self):
        r = recomendar("sitio", wifi=False)
        self.assertNotIn("kit-cam-2", ids(r["ideal"]))
        self.assertIn("alarme-ikerui", ids(r["ideal"]))
        self.assertTrue(any("Wi-Fi" in a for a in r["avisos"]))

    def test_nunca_oferece_esgotado(self):
        for im in ("apartamento", "casa", "sitio", "comercio", "home_office"):
            self.assertNotIn("cartao-64", ids(recomendar(im, pontos=6, viaja=True, porta="facial")["ideal"]))

    def test_orcamento_corta_ate_caber(self):
        r = recomendar("casa", pontos=4, viaja=True, porta="facial", orcamento=1300)
        vo = r["versao_orcamento"]
        self.assertTrue(vo["cabe"])
        self.assertLessEqual(vo["pix"], 1300)
        self.assertIn("kit-cam-2", ids(vo))
        self.assertTrue(vo["cortes"])

    def test_orcamento_impossivel(self):
        r = recomendar("apartamento", orcamento=100)
        self.assertFalse(r["versao_orcamento"]["cabe"])
        self.assertIn("parcelar", mensagem(r))

    def test_sem_orcamento_nao_gera_versao(self):
        self.assertIsNone(recomendar("casa", orcamento=99999)["versao_orcamento"])

    def test_mensagem_tem_link_preco_e_promessa(self):
        m = mensagem(recomendar("casa", nome="Ana"))
        self.assertIn("Ana,", m)
        self.assertIn("https://infinityguard.com.br/produtos/", m)
        self.assertIn("no Pix", m)
        self.assertIn("7 dias", m)

    def test_entrada_invalida(self):
        with self.assertRaises(ValueError):
            recomendar("castelo")

    def test_brl(self):
        self.assertEqual(brl(2173.27), "R$ 2.173,27")


class Carrinho(unittest.TestCase):
    def test_tres_mensagens_e_cupom(self):
        s = carrinho.sequencia("Ana", "alarme-ikerui", cupom="VOLTEI5")
        self.assertEqual(len(s["mensagens"]), 3)
        self.assertIn("R$ 787,95", s["mensagens"][1]["texto"])
        self.assertIn("VOLTEI5", s["mensagens"][2]["texto"])
        self.assertIn("paro por aqui", s["mensagens"][2]["texto"])

    def test_sem_cupom_nao_inventa(self):
        s = carrinho.sequencia("Ana", "kit-cam-2")
        self.assertNotIn("cupom", s["mensagens"][2]["texto"].lower())


class Exportar(unittest.TestCase):
    def test_prompt_completo(self):
        p = exportar_prompt.montar()
        self.assertIn("ESGOTADO", p)
        self.assertIn("Nunca", p)
        self.assertIn("2,4 GHz", p)
        self.assertNotIn("scripts/recomendar_kit.py", p)


if __name__ == "__main__":
    unittest.main()
