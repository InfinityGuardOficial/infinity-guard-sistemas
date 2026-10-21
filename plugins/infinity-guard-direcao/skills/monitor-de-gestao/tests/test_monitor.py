import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import monitor as mn  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "backup.json"


class Monitor(unittest.TestCase):
    def setUp(self):
        self.alertas = mn.avaliar(mn.carregar_backup(FIX), date(2026, 10, 20))
        self.por = {(a["regra"], a["responsavel"]): a for a in self.alertas}
        self.ids = {a["regra"] for a in self.alertas}

    def test_prazo_em_dias_uteis_vira_corridos(self):
        self.assertEqual(mn._prazo_max("8 a 15 dias úteis"), 21)
        self.assertEqual(mn._prazo_max("7 a 15 dias"), 15)
        self.assertIsNone(mn._prazo_max(""))

    def test_criticos_primeiro(self):
        self.assertEqual(self.alertas[0]["nivel"], "critico")
        self.assertIn("tms-atraso", self.ids)
        self.assertIn("wms-esgotado", self.ids)

    def test_operacao(self):
        self.assertEqual(self.por[("erp-nao-repassado", "lider-operacoes")]["itens"][0].split()[0], "P2")
        self.assertIn("tms-sem-rastreio", self.ids)
        self.assertIn("sac-troca-aberta", self.ids)
        self.assertIn("erp-margem-negativa", self.ids)  # P2: 150 de total, 205 de custo

    def test_financeiro(self):
        self.assertIn("fin-resultado-negativo", self.ids)
        self.assertIn("fin-anuncio-alto", self.ids)

    def test_crm_responsavel_por_etapa(self):
        self.assertIn(("crm-followup-atrasado", "recuperador-de-carrinho"), self.por)
        self.assertNotIn(("crm-followup-atrasado", "consultor-whatsapp"), self.por)  # Gil vence hoje: ainda não está atrasado
        self.assertIn("crm-orcamento-sem-acao", self.ids)
        itens = " ".join(i for a in self.alertas for i in a["itens"])
        self.assertNotIn("Fábio", itens)  # perdido não gera alerta

    def test_estoque_e_cadastro(self):
        self.assertIn("wms-baixo", self.ids)
        self.assertIn("erp-sem-custo", self.ids)
        self.assertIn("vmi-sem-fornecedor", self.ids)
        self.assertNotIn("Pasta", " ".join(i for a in self.alertas for i in a["itens"]))  # inativo fica fora

    def test_sem_dados_sem_alerta(self):
        self.assertEqual(mn.avaliar({"app": "rota-do-milhao"}, date(2026, 10, 20)), [])
        self.assertIn("Sem alertas", mn.para_texto([]))


if __name__ == "__main__":
    unittest.main()
