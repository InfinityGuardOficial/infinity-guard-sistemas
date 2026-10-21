import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
from auditar import auditar, cnpj_valido, relatorio_md, texto_de  # noqa: E402

FIX = AQUI / "fixtures"


def pagina(nome):
    return {"url": nome, "html": (FIX / nome).read_text(encoding="utf-8")}


def status(r, chave, i=0):
    return next(it["status"] for it in r["paginas"][i]["itens"] if it["chave"] == chave)


class Cnpj(unittest.TestCase):
    def test_digito(self):
        self.assertTrue(cnpj_valido("11.222.333/0001-81"))
        self.assertTrue(cnpj_valido("11222333000181"))
        self.assertFalse(cnpj_valido("11.222.333/0001-82"))
        self.assertFalse(cnpj_valido("11.111.111/1111-11"))


class LojaHoje(unittest.TestCase):
    def setUp(self):
        self.r = auditar([pagina("produto_hoje.html")])

    def test_acha_o_que_falta(self):
        self.assertEqual(status(self.r, "cnpj"), "falta")  # CNPJ só dentro de <script> não conta
        self.assertEqual(status(self.r, "garantia"), "aviso")
        self.assertEqual(status(self.r, "avaliacoes"), "falta")
        self.assertEqual(status(self.r, "troca"), "ok")
        self.assertEqual(status(self.r, "contato"), "aviso")

    def test_rastros_de_fornecedor(self):
        it = next(i for i in self.r["paginas"][0]["itens"] if i["chave"] == "rastros")
        self.assertIn("plugue da UE", it["achado"])
        self.assertIn("placeholder", it["achado"])

    def test_ordem_da_correcao(self):
        self.assertEqual([c["chave"] for c in self.r["correcoes"]][:3], ["cnpj", "garantia", "avaliacoes"])

    def test_relatorio_nao_inventa(self):
        md = relatorio_md(self.r)
        self.assertIn("Lista de correção", md)
        self.assertNotRegex(md, r"\d{5}-\d{2}-\d{5}")  # nenhum código Anatel inventado
        self.assertNotRegex(md, r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")  # nenhum CNPJ inventado


class LojaCorrigida(unittest.TestCase):
    def test_tudo_ok(self):
        r = auditar([pagina("produto_corrigido.html")])
        self.assertEqual(r["correcoes"], [])
        self.assertEqual(r["nota"], 100)

    def test_cnpj_do_rodape_vale_para_o_site(self):
        r = auditar([pagina("produto_hoje.html"), pagina("produto_corrigido.html")])
        self.assertNotIn("cnpj", [c["chave"] for c in r["correcoes"]])
        self.assertIn("garantia", [c["chave"] for c in r["correcoes"]])


class Anatel(unittest.TestCase):
    """Dropshipping: o código Anatel não é cobrado; citar Anatel sem conferir vira aviso."""

    def test_nao_cobra_anatel(self):
        r = auditar([pagina("produto_hoje.html")])
        self.assertNotIn("anatel", [it["chave"] for it in r["paginas"][0]["itens"]])
        self.assertNotIn("Anatel", relatorio_md(r).split("## Conferir à mão")[1])

    def test_avisa_quando_a_pagina_cita_anatel(self):
        r = auditar([{"url": "p", "html": "<p>Câmera homologada pela Anatel: 12345-24-06789</p>"}])
        self.assertEqual(status(r, "anatel"), "aviso")


class Texto(unittest.TestCase):
    def test_tira_script_e_tags(self):
        self.assertEqual(texto_de("<p>Oi&nbsp;<b>Ana</b></p><script>x=1</script>"), "Oi Ana")


if __name__ == "__main__":
    unittest.main()
