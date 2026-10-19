import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import diagnostico as dg  # noqa: E402


class Diagnostico(unittest.TestCase):
    def setUp(self):
        self.probs = dg.carregar()

    def test_offline(self):
        self.assertEqual(dg.diagnosticar("Minha câmera fica OFFLINE toda noite", self.probs)[0]["id"], "offline")

    def test_wifi_sem_acento(self):
        self.assertEqual(dg.diagnosticar("nao conecta no wifi", self.probs)[0]["id"], "nao-conecta-wifi")

    def test_categoria_filtra(self):
        ids = {p["id"] for p in dg.diagnosticar("a noite a imagem fica branca", self.probs, "fechadura")}
        self.assertNotIn("visao-noturna", ids)

    def test_nada(self):
        self.assertEqual(dg.diagnosticar("bom dia", self.probs), [])

    def test_mensagem_numerada(self):
        m = dg.mensagem_whatsapp(dg.diagnosticar("offline", self.probs)[0], "Ana")
        self.assertTrue(m.startswith("Ana,"))
        self.assertIn("1. ", m)
        self.assertNotIn("**", m)

    def test_ids_unicos(self):
        ids = [p["id"] for p in self.probs]
        self.assertEqual(len(ids), len(set(ids)))


class Troca(unittest.TestCase):
    def test_arrependimento(self):
        self.assertEqual(dg.caso_troca(date(2026, 10, 15), date(2026, 10, 22), False)["caso"], "arrependimento")

    def test_defeito_90(self):
        self.assertEqual(dg.caso_troca(date(2026, 8, 1), date(2026, 10, 19), True)["caso"], "defeito")

    def test_fora(self):
        self.assertEqual(dg.caso_troca(date(2026, 1, 1), date(2026, 10, 19), True)["caso"], "defeito-fora-do-prazo-legal")
        self.assertEqual(dg.caso_troca(date(2026, 10, 1), date(2026, 10, 19), False)["caso"], "fora-do-arrependimento")

    def test_sempre_dono_decide(self):
        self.assertEqual(dg.caso_troca(date(2026, 10, 18), date(2026, 10, 19), False)["decide"], "dono")


if __name__ == "__main__":
    unittest.main()
