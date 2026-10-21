import json
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from base import Sandbox  # noqa: E402
from core import event_queue  # noqa: E402
from core.event_queue import EventQueue  # noqa: E402


class Fila(Sandbox):
    def test_inicializa_vazia(self):
        EventQueue.initialize()
        data = json.loads((self.home / "logs" / "queue.json").read_text(encoding="utf-8"))
        self.assertEqual(data, {"pending_tasks": [], "history": []})

    def test_fifo_e_historico(self):
        self.assertTrue(EventQueue.add_event("a", {"n": 1}))
        self.assertTrue(EventQueue.add_event("b", {"n": 2}))
        self.assertEqual(EventQueue.pop_task()["type"], "a")
        t = EventQueue.pop_task()
        self.assertEqual(t["type"], "b")
        self.assertIsNone(EventQueue.pop_task())
        EventQueue.finish_task(t, "ok", "saida.md")
        hist = EventQueue.snapshot()["history"]
        self.assertEqual([h["type"] for h in hist], ["a", "b"])
        self.assertEqual(hist[-1]["status"], "ok")

    def test_nao_duplica_pendente(self):
        self.assertTrue(EventQueue.add_event("relatorio", {}))
        self.assertFalse(EventQueue.add_event("relatorio", {}))
        self.assertEqual(len(EventQueue.snapshot()["pending_tasks"]), 1)

    def test_arquivo_vazio_ou_corrompido(self):
        f = self.home / "logs" / "queue.json"
        f.parent.mkdir(exist_ok=True)
        f.write_text("", encoding="utf-8")
        self.assertIsNone(EventQueue.pop_task())
        f.write_text("{quebrado", encoding="utf-8")
        self.assertTrue(EventQueue.add_event("x", {}))
        self.assertTrue(list((self.home / "logs").glob("queue.corrompido-*.json")))

    def test_concorrencia_sem_perder_evento(self):
        ts = [threading.Thread(target=EventQueue.add_event, args=(f"t{i}", {})) for i in range(20)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(len(EventQueue.snapshot()["pending_tasks"]), 20)

    def test_trava_velha_e_liberada(self):
        trava = self.home / "logs" / "queue.lock"
        trava.parent.mkdir(exist_ok=True)
        trava.write_text("999999")
        import os
        import time
        velho = time.time() - event_queue.TRAVA_VELHA - 5
        os.utime(trava, (velho, velho))
        self.assertTrue(EventQueue.add_event("depois_da_queda", {}))

    def test_historico_limitado(self):
        antes = event_queue.HISTORICO_MAX
        event_queue.HISTORICO_MAX = 3
        try:
            for i in range(5):
                EventQueue.add_event(f"e{i}", {})
                EventQueue.pop_task()
            self.assertEqual([h["type"] for h in EventQueue.snapshot()["history"]], ["e2", "e3", "e4"])
        finally:
            event_queue.HISTORICO_MAX = antes
