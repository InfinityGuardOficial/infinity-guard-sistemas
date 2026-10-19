import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import montar_campanha as mc  # noqa: E402


class Ofertas(unittest.TestCase):
    def setUp(self):
        self.cat = mc.carregar_catalogo()
        self.kits = {k["id"]: k for k in mc.ofertas(self.cat, 0.10)}

    def test_de_e_preco_atual_nunca_preco_de(self):
        k = self.kits["kit-casa-vigiada"]
        self.assertAlmostEqual(k["de"], 392.35 + 875.50, places=2)
        self.assertAlmostEqual(k["por"], round((392.35 + 875.50) * 0.9, 2), places=2)
        self.assertAlmostEqual(k["pix"], round(k["por"] * 0.9, 2), places=2)

    def test_parcela_minima(self):
        for k in self.kits.values():
            self.assertGreaterEqual(k["parcela_valor"], mc.PARCELA_MINIMA - 0.01, k["id"])
            self.assertLessEqual(k["parcelas"], 12)

    def test_so_produtos_ativos(self):
        for k in self.kits.values():
            for i in k["itens"]:
                self.assertTrue(self.cat["por_id"][i["id"]]["ativo"], i["id"])

    def test_desconto_alto_recusado(self):
        with self.assertRaises(ValueError):
            mc.ofertas(self.cat, 0.40)

    def test_margem_baixa_tira_kit(self):
        custos = {p["id"]: p["preco"] * 0.85 for p in self.cat["produtos"]}
        ks = mc.ofertas(self.cat, 0.10, custos, margem_minima=0.20)
        self.assertTrue(all(not k["ativo"] for k in ks))
        self.assertTrue(any("margem" in a for a in ks[0]["avisos"]))


class Campanha(unittest.TestCase):
    def test_datas_dos_eventos(self):
        c = mc.montar()
        ev = {e["id"]: e for e in c["eventos"]}
        self.assertEqual(date.fromisoformat(ev["1111"]["inicio"]).weekday(), 2)  # 11/11/2026 é quarta
        datas = [p["data"] for p in ev["blackfriday"]["calendario"]]
        for dia in ("2026-11-26", "2026-11-27", "2026-11-28", "2026-11-29"):
            self.assertIn(dia, datas)
        self.assertEqual(datas, sorted(datas))

    def test_prova_pendente_bloqueia_anuncio(self):
        c = mc.montar(prova_ok=False)
        acoes = [p["acao"] for e in c["eventos"] for p in e["calendario"] if p["canal"] == "Anúncio"]
        self.assertTrue(acoes and all("bloqueado" in a for a in acoes))
        acoes_ok = [p["acao"] for e in mc.montar(prova_ok=True)["eventos"] for p in e["calendario"] if p["canal"] == "Anúncio"]
        self.assertTrue(all("bloqueado" not in a for a in acoes_ok))

    def test_mensagens_com_saida_e_precos_do_script(self):
        c = mc.montar(eventos=("blackfriday",), cupom="IGBLACK")
        m = c["eventos"][0]["mensagens"]
        self.assertIn("SAIR", m["abertura"])
        self.assertIn("IGBLACK", m["abertura"])
        self.assertIn(mc.brl(next(k for k in c["kits"] if k["id"] == "kit-casa-vigiada")["pix"]), m["lembrete"])
        self.assertTrue(c["eventos"][0]["cupom_criado"])

    def test_cupom_sugerido_avisa_para_criar(self):
        md = mc.para_md(mc.montar(eventos=("1111",)))
        self.assertIn("crie na Nuvemshop", md)
        self.assertNotIn("instalação inclusa", md.lower())


if __name__ == "__main__":
    unittest.main()
