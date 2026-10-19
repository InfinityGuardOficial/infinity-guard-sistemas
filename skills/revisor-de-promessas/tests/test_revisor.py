import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import revisar as rv  # noqa: E402


class Revisor(unittest.TestCase):
    def setUp(self):
        self.regras = rv.carregar_regras()

    def ids(self, texto):
        return {a["regra"] for a in rv.revisar(texto, self.regras)["achados"]}

    def test_texto_limpo_liberado(self):
        r = rv.revisar("Veja sua casa de onde estiver. Kit montado para a sua casa, com suporte no WhatsApp.", self.regras)
        self.assertEqual(r["veredito"], "LIBERADO")

    def test_promessas_que_bloqueiam(self):
        texto = "Câmera 100% segura com instalação grátis e garantia de 2 anos. Homologada pela Anatel."
        self.assertTrue({"seguranca-absoluta", "instalacao", "garantia-sem-prazo-documentado",
                         "anatel-sem-codigo"} <= self.ids(texto))
        self.assertEqual(rv.revisar(texto, self.regras)["veredito"], "BLOQUEADO")

    def test_4g_e_cartao(self):
        self.assertIn("4g-sem-wifi", self.ids("Funciona sem Wi-Fi"))
        self.assertIn("dados-sensiveis", self.ids("me passa o número do cartão"))

    def test_ajustar_nao_bloqueia(self):
        r = rv.revisar("A melhor câmera do Brasil, últimas 3 unidades!", self.regras)
        self.assertEqual(r["veredito"], "AJUSTAR")
        self.assertEqual(r["bloqueia"], 0)

    def test_liberar_regra_resolvida(self):
        regras = rv.carregar_regras(liberar=["anatel-sem-codigo"])
        self.assertEqual(rv.revisar("Código Anatel 12345-21-01234", regras)["veredito"], "LIBERADO")

    def test_linha_certa(self):
        a = rv.revisar("ok\nok\ninstalação grátis", self.regras)["achados"][0]
        self.assertEqual(a["linha"], 3)


if __name__ == "__main__":
    unittest.main()
