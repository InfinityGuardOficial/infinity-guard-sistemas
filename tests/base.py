"""Base dos testes: cada teste roda numa pasta temporária (IG_HOME), sem tocar em logs/ e dados/ do repositório."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="ig-sandbox-"))
        (self.home / "dados" / "nuvemshop").mkdir(parents=True)
        (self.home / "dados" / "meta").mkdir(parents=True)
        self._antes = {k: os.environ.get(k) for k in ("IG_HOME", "IG_DRY_RUN", "META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID")}
        os.environ["IG_HOME"] = str(self.home)
        os.environ["IG_DRY_RUN"] = "1"
        os.environ.pop("META_ACCESS_TOKEN", None)
        os.environ.pop("META_AD_ACCOUNT_ID", None)

    def tearDown(self):
        for k, v in self._antes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.home, ignore_errors=True)

    def com_vendas(self, conversas=False):
        shutil.copy(FIXTURES / "vendas_exemplo.csv", self.home / "dados" / "nuvemshop" / "vendas.csv")
        if conversas:
            shutil.copy(FIXTURES / "conversas_exemplo.csv", self.home / "dados" / "nuvemshop" / "conversas.csv")

    def com_meta(self):
        shutil.copy(FIXTURES / "meta_resultados.csv", self.home / "dados" / "meta" / "resultados.csv")
