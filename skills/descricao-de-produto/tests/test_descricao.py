import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import descrever as ds  # noqa: E402


class Descricao(unittest.TestCase):
    def setUp(self):
        self.cat = ds.carregar_catalogo()
        self.cats = ds.json.loads(ds.CATEGORIAS.read_text(encoding="utf-8"))

    def gerar(self, pid, **kw):
        return ds.descrever(self.cat["por_id"][pid], self.cat, self.cats, **kw)

    def test_limites_seo(self):
        for p in self.cat["produtos"]:
            d = ds.descrever(p, self.cat, self.cats)
            self.assertLessEqual(len(d["titulo_seo"]), ds.TITULO_MAX, p["id"])
            self.assertLessEqual(len(d["meta_description"]), ds.META_MAX, p["id"])

    def test_sem_anatel_nao_cita_codigo_e_pede_pendencia(self):
        d = self.gerar("kit-cam-2")
        self.assertNotIn("Anatel", d["html"])
        self.assertTrue(any("Anatel" in x for x in d["pendencias"]))

    def test_com_anatel_valido(self):
        d = self.gerar("alarme-ikerui", anatel="12345-21-01234", garantia="12 meses")
        self.assertIn("12345-21-01234", d["html"])
        self.assertIn("Garantia de 12 meses", d["html"])
        self.assertEqual(d["pendencias"], [])

    def test_anatel_invalido(self):
        with self.assertRaises(ValueError):
            self.gerar("kit-cam-2", anatel="123")

    def test_preco_do_catalogo(self):
        self.assertIn("R$ 353,12", self.gerar("kit-cam-2")["descricao_curta"])

    def test_nao_promete_instalacao(self):
        for p in self.cat["produtos"]:
            self.assertNotIn("instalação", ds.descrever(p, self.cat, self.cats)["html"].lower())


if __name__ == "__main__":
    unittest.main()
