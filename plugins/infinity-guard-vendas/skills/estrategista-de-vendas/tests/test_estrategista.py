import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import estrategista as es  # noqa: E402


class Estrategista(unittest.TestCase):
    def setUp(self):
        self.cat = es.carregar_catalogo()

    def test_precos_do_catalogo_e_riscados(self):
        d = es.diagnostico_precos(self.cat)
        por_id = {i["id"]: i for i in d["itens"]}
        self.assertEqual(por_id["kit-cam-2"]["preco"], 392.35)
        self.assertIn("tirar o riscado", por_id["kit-cam-2"]["leitura"])  # 5%: maquiagem
        self.assertIn("praticado", por_id["alarme-ikerui"]["leitura"])    # 15%: precisa de prova
        self.assertNotIn("hub-7em1", por_id)                              # home office fica fora
        self.assertNotIn("cartao-64", por_id)                             # inativo fica fora
        self.assertEqual(por_id["fechadura-facial"]["degrau"], "assinatura")

    def test_dossie_curado_com_preco_do_catalogo_e_liberado(self):
        d = es.dossie("Ana", "casa", "camera", self.cat)
        self.assertEqual(d["ficha"]["indicado"], "kit-cam-2")
        texto = "\n".join(t for _, t in d["etapas"])
        self.assertIn("R$ 392,35", texto)
        self.assertIn("R$ 353,12", texto)
        self.assertIn("manual de instruções acompanha o produto", texto)
        self.assertEqual(d["revisao"]["veredito"], "LIBERADO")

    def test_dossie_respeita_orcamento(self):
        d = es.dossie("Rui", "comercio", "fechadura", self.cat, orcamento=1500)
        self.assertEqual(d["ficha"]["indicado"], "fechadura-bio")

    def test_todos_os_dossies_passam_no_revisor(self):
        for interesse, imovel in es.CURADORIA:
            d = es.dossie("Bia", imovel, interesse, self.cat)
            self.assertEqual(d["revisao"]["veredito"], "LIBERADO", (interesse, imovel, d["revisao"]["achados"]))

    def test_calendario_datas_e_revisor(self):
        c = es.calendario("Ana", "alarme-ikerui", self.cat, entrega="2026-10-30")
        datas = {i["dia"]: i["data"] for i in c["itens"]}
        self.assertEqual(datas[6], "2026-11-05")
        self.assertEqual(datas[80], "2027-01-18")
        self.assertEqual(c["revisao"]["veredito"], "LIBERADO")
        with self.assertRaises(ValueError):
            es.calendario("Ana", "camera-4g", self.cat)

    def test_escassez_so_com_dado_real(self):
        self.assertFalse(es.escassez(self.cat)["permitido"])
        self.assertFalse(es.escassez(self.cat, "alarme-ikerui", 3)["permitido"])          # sem data
        self.assertFalse(es.escassez(self.cat, "alarme-ikerui", 40, "2026-10-23")["permitido"])  # não é baixo
        r = es.escassez(self.cat, "alarme-ikerui", 3, "2026-10-23")
        self.assertTrue(r["permitido"])
        self.assertIn("23/10", r["frase"])
        self.assertNotEqual(r["revisao"]["veredito"], "BLOQUEADO")
        self.assertEqual(es.escassez(self.cat, fim="2026-11-29")["frase"], "Condição válida até 29/11.")

    def test_referencias_passam_no_revisor(self):
        refs = Path(__file__).resolve().parent.parent / "references"
        for f in refs.glob("*.md"):
            r = es.revisar(f.read_text(encoding="utf-8"))
            self.assertEqual(r.get("bloqueia", 0), 0, (f.name, r["achados"]))


if __name__ == "__main__":
    unittest.main()
