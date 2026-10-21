import json
import subprocess
import sys
import unittest
from pathlib import Path

SERVIDOR = Path(__file__).resolve().parent.parent / "infinity_guard_mcp.py"


def conversa(*mensagens):
    entrada = "".join(json.dumps(m) + "\n" for m in mensagens)
    r = subprocess.run([sys.executable, str(SERVIDOR)], input=entrada, capture_output=True, text=True, timeout=120)
    return [json.loads(l) for l in r.stdout.splitlines() if l.strip()]


class MCP(unittest.TestCase):
    def test_aperto_de_mao_e_lista(self):
        r = conversa({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "teste", "version": "1"}}},
                     {"jsonrpc": "2.0", "method": "notifications/initialized"},
                     {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(len(r), 2)  # a notificação não tem resposta
        self.assertEqual(r[0]["result"]["protocolVersion"], "2025-06-18")
        nomes = {t["name"] for t in r[1]["result"]["tools"]}
        self.assertIn("revisar_texto", nomes)
        self.assertEqual(len(nomes), 9)

    def test_ferramentas_reais(self):
        r = conversa({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "revisar_texto", "arguments": {"texto": "Câmera 100% segura com instalação grátis"}}},
                     {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "plano_de_midia", "arguments": {"ticket": 620, "margem": 0.3, "meta_vendas": 16}}},
                     {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "recomendar_kit", "arguments": {"imovel": "apartamento", "wifi": "sim"}}})
        self.assertIn("BLOQUEADO", r[0]["result"]["content"][0]["text"])
        self.assertFalse(r[0]["result"]["isError"])
        self.assertIn("CPA máximo", r[1]["result"]["content"][0]["text"])
        self.assertIn("R$", r[2]["result"]["content"][0]["text"])

    def test_erros(self):
        r = conversa({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "nao_existe"}},
                     {"jsonrpc": "2.0", "id": 2, "method": "metodo/estranho"},
                     {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "revisar_texto", "arguments": {}}})
        self.assertEqual(r[0]["error"]["code"], -32602)
        self.assertEqual(r[1]["error"]["code"], -32601)
        self.assertTrue(r[2]["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
