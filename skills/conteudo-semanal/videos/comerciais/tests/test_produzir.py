import copy, json, os, shutil, sys, tempfile, unittest
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import produzir

EP15 = os.path.join(AQUI, "..", "ep15-quem-deixou-isso-na-porta")


class Validar(unittest.TestCase):
    def setUp(self):
        produzir.MAX_IDADE_CATALOGO = 10 ** 6  # a idade do catálogo é checada à parte, na produção
    def episodio(self, mudar):
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        for f in ("episodio.json", "shots3d.py"): shutil.copy(os.path.join(EP15, f), tmp)
        d = json.load(open(os.path.join(tmp, "episodio.json"))); mudar(d)
        json.dump(d, open(os.path.join(tmp, "episodio.json"), "w"), ensure_ascii=False)
        return produzir.validar(tmp, quieto=True)[0]

    def test_ep15_passa(self):
        self.assertEqual(produzir.validar(EP15, quieto=True)[0], [])

    def test_barra_funcao_nao_confirmada(self):
        for frase in ("A câmera grava tudo.", "Manda alerta no aplicativo.", "Imagem em 2K.", "Tem áudio."):
            erros = self.episodio(lambda d: d["segmentos"][2]["falas"][0].update(texto=frase))
            self.assertTrue(erros, frase)

    def test_barra_preco_promocao_e_identificacao(self):
        for frase in ("Por R$ 299!", "Só hoje, sem juros.", "A câmera identificou o entregador.", "Zoom de 8x."):
            self.assertTrue(self.episodio(lambda d: d["segmentos"][3]["falas"][1].update(texto=frase)), frase)

    def test_barra_produto_inativo(self):
        self.assertTrue(any("inativo" in e for e in self.episodio(lambda d: d.update(produto="cartao-64"))))

    def test_barra_roteiro_com_buraco(self):
        self.assertTrue(self.episodio(lambda d: d["segmentos"][1].update(fim=13)))


if __name__ == "__main__":
    unittest.main()


class Precos(unittest.TestCase):
    def test_por_extenso(self):
        self.assertEqual(produzir.reais_falado(1218.54), "mil duzentos e dezoito reais e cinquenta e quatro")
        self.assertEqual(produzir.reais_falado(1096.69), "mil e noventa e seis reais e sessenta e nove")
        self.assertEqual(produzir.reais_falado(100), "cem reais")
        self.assertEqual(produzir.brl(1218.54), "R$ 1.218,54")

    def test_preencher_usa_o_catalogo(self):
        prod = {"preco": 1218.54, "pix": 1096.69, "parcelas": 12, "parcela_valor": 101.55}
        self.assertEqual(produzir.preencher("{preco} ou {pix} no Pix, {parcelas}x de {parcela}", prod),
                         "R$ 1.218,54 ou R$ 1.096,69 no Pix, 12x de R$ 101,55")


EP17 = os.path.join(AQUI, "..", "ep17-o-presente-que-ninguem-esperava")


class RecursosInformados(unittest.TestCase):
    def setUp(self):
        produzir.MAX_IDADE_CATALOGO = 10 ** 6

    def episodio(self, mudar):
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        for f in ("episodio.json", "shots3d.py"): shutil.copy(os.path.join(EP17, f), tmp)
        d = json.load(open(os.path.join(tmp, "episodio.json"))); mudar(d)
        json.dump(d, open(os.path.join(tmp, "episodio.json"), "w"), ensure_ascii=False)
        return produzir.validar(tmp, quieto=True)

    def test_ep17_passa_com_avisos(self):
        erros, avisos = produzir.validar(EP17, quieto=True)
        self.assertEqual(erros, [])
        self.assertTrue(any("cartão" in a for a in avisos))

    def test_sem_informar_cartao_bloqueia(self):
        self.assertTrue(self.episodio(lambda d: d.update(recursos_informados=[]))[0])

    def test_wifi_e_campo_desconhecido_bloqueiam(self):
        self.assertTrue(self.episodio(lambda d: d["segmentos"][2]["falas"][1].update(texto="Abre pelo Wi-Fi de qualquer lugar."))[0])
        self.assertTrue(self.episodio(lambda d: d["segmentos"][4]["falas"][0].update(texto="Por {desconto}."))[0])
