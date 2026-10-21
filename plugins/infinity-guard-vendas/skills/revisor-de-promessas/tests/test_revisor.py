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
        self.assertIn("dados-sensiveis", self.ids("qual é a senha do wifi?"))
        self.assertNotIn("dados-sensiveis", self.ids("Troque a senha do Wi-Fi se ela for a de fábrica"))

    def test_dropshipping(self):
        self.assertIn("produto-ja-configurado", self.ids("Sua câmera sai daqui configurada"))
        self.assertIn("produto-ja-configurado", self.ids("Já vem configurada, é só ligar"))
        self.assertIn("prazo-de-entrega", self.ids("Entrega em 24h para todo o Brasil"))
        self.assertNotIn("produto-ja-configurado", self.ids("O manual de instruções acompanha o produto"))

    def test_loja_nao_configura_por_whatsapp_nem_video(self):
        for texto in ("Quando chegar, a gente configura junto com você por vídeo no WhatsApp",
                      "Eu configuro com você por vídeo (rede Wi-Fi 2,4 GHz, senha trocada)",
                      "Kits com configuração segura acompanhada no WhatsApp",
                      "Configuração guiada por vídeo em 15 minutos",
                      "Te ajudo a configurar pelo WhatsApp",
                      "Me chama que eu te passo a configuração por vídeo",
                      "Chamada de vídeo pra configurar a fechadura"):
            self.assertIn("configuracao-pela-loja", self.ids(texto), msg=texto)
            self.assertEqual(rv.revisar(texto, self.regras)["veredito"], "BLOQUEADO", msg=texto)
        for texto in ("O manual de instruções acompanha o produto. Ficou com dúvida? Chama no WhatsApp que a gente responde.",
                      "No app: configurações do aparelho, atualização.",
                      "Deixe o aparelho a até 3 metros do roteador só para configurar.",
                      "Siga o manual para configurar a câmera no app."):
            self.assertNotIn("configuracao-pela-loja", self.ids(texto), msg=texto)
        self.assertEqual(rv.revisar("A loja não configura por WhatsApp nem por vídeo.", self.regras)["bloqueia"], 0)

    def test_ajustar_nao_bloqueia(self):
        r = rv.revisar("A melhor câmera do Brasil, últimas 3 unidades!", self.regras)
        self.assertEqual(r["veredito"], "AJUSTAR")
        self.assertEqual(r["bloqueia"], 0)

    def test_variantes_de_promessa_absoluta(self):
        for texto in ("Câmera 100% inviolável", "Segurança total para sua casa", "Fechadura impossível de hackear",
                      "Invulnerável a ladrão"):
            self.assertIn("seguranca-absoluta", self.ids(texto), msg=texto)
        self.assertIn("superlativo-sem-prova", self.ids("A melhor do Brasil"))
        self.assertNotIn("superlativo-sem-prova", self.ids("Melhor custo-benefício para apartamento"))

    def test_liberar_regra_resolvida(self):
        regras = rv.carregar_regras(liberar=["anatel-sem-codigo"])
        self.assertEqual(rv.revisar("Código Anatel 12345-21-01234", regras)["veredito"], "LIBERADO")

    def test_negacao_vira_ajustar(self):
        r = rv.revisar("Sem instalação no local.\n## O que não está incluso\n- Instalação no local", self.regras)
        self.assertEqual(r["bloqueia"], 0)
        self.assertEqual(r["veredito"], "AJUSTAR")
        self.assertEqual(rv.revisar("Instalação grátis para você!", self.regras)["veredito"], "BLOQUEADO")
        self.assertEqual(rv.revisar('**"Essa câmera é homologada pela Anatel?"**', self.regras)["bloqueia"], 0)

    def test_linha_certa(self):
        a = rv.revisar("ok\nok\ninstalação grátis", self.regras)["achados"][0]
        self.assertEqual(a["linha"], 3)


if __name__ == "__main__":
    unittest.main()
