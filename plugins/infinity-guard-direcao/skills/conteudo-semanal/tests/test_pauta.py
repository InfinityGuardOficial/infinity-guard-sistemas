import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import pauta_semana as ps  # noqa: E402


class Pauta(unittest.TestCase):
    def test_tres_roteiros_formatos_diferentes(self):
        p = ps.pauta(date(2026, 10, 19), historico={})
        self.assertEqual(len(p["roteiros"]), 3)
        self.assertEqual(len({r["formato"] for r in p["roteiros"]}), 3)
        self.assertEqual([r["dia"] for r in p["roteiros"]], ["segunda", "quarta", "sexta"])

    def test_nao_repete_em_2_semanas(self):
        hist = {}
        s = date(2026, 10, 19)
        for i in range(8):
            semana = s + timedelta(weeks=i)
            ids = [r["tema"] for r in ps.pauta(semana, historico=hist)["roteiros"]]
            for k, antigos in hist.items():
                if (semana - date.fromisoformat(k)).days <= 14:
                    repetidos = set(ids) & set(antigos) - {"black-friday-olhar"}  # tema de campanha volta de propósito
                    self.assertFalse(repetidos, (semana, k))
            hist[semana.isoformat()] = ids

    def test_semana_da_black_friday_comeca_pela_campanha(self):
        p = ps.pauta(date(2026, 11, 26), historico={})
        self.assertEqual(p["semana"], "2026-11-23")
        self.assertEqual(p["campanha"], "blackfriday")
        self.assertEqual(p["roteiros"][0]["tema"], "black-friday-olhar")

    def test_tema_de_black_friday_fora_da_janela(self):
        p = ps.pauta(date(2026, 12, 14), historico={})
        self.assertNotIn("black-friday-olhar", [r["tema"] for r in p["roteiros"]])

    def test_anatel_so_com_codigo_publicado(self):
        for i in range(12):
            s = date(2026, 10, 19) + timedelta(weeks=i)
            self.assertNotIn("anatel", [r["tema"] for r in ps.pauta(s, historico={})["roteiros"]])

    def test_legenda_tem_cta_whatsapp(self):
        md = ps.para_md(ps.pauta(date(2026, 10, 19), historico={}))
        self.assertIn("98667-9178", md)
        self.assertIn("Gancho", md)

    def test_proxima_segunda(self):
        self.assertEqual(ps.proxima_segunda(date(2026, 10, 18)), date(2026, 10, 19))
        self.assertEqual(ps.proxima_segunda(date(2026, 10, 19)), date(2026, 10, 26))


if __name__ == "__main__":
    unittest.main()
