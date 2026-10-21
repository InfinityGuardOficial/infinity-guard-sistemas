"""Fila de eventos em JSON (logs/queue.json), segura para o daemon e o terminal usarem ao mesmo tempo.

Mesma ideia da EventQueue do roteiro original, com três correções:
- trava de arquivo (logs/queue.lock) para duas escritas não se atropelarem;
- gravação atômica (arquivo temporário + os.replace), então uma queda no meio não corrompe a fila;
- histórico limitado (HISTORICO_MAX) para o arquivo não crescer para sempre.
"""
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime

from core import caminhos

HISTORICO_MAX = 500
TRAVA_VELHA = 60  # segundos: trava mais velha que isso foi deixada por um processo que caiu


def _arquivo():
    return caminhos.logs() / "queue.json"


@contextmanager
def _trava(espera=10.0):
    trava = caminhos.logs() / "queue.lock"
    limite = time.monotonic() + espera
    while True:
        try:
            fd = os.open(trava, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            break
        except (FileExistsError, PermissionError):
            # no Windows, uma trava que está sendo apagada dá PermissionError em vez de FileExistsError
            try:
                if time.time() - trava.stat().st_mtime > TRAVA_VELHA:
                    trava.unlink()
                    continue
            except FileNotFoundError:
                continue
            except PermissionError:
                pass
            if time.monotonic() > limite:
                raise TimeoutError(f"fila travada por outro processo ({trava})")
            time.sleep(0.05)
    try:
        yield
    finally:
        for _ in range(50):
            try:
                trava.unlink()
                break
            except FileNotFoundError:
                break
            except PermissionError:  # Windows: antivírus ou indexador segurando o arquivo por um instante
                time.sleep(0.02)


def _ler():
    f = _arquivo()
    if not f.exists() or f.stat().st_size == 0:
        return {"pending_tasks": [], "history": []}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # guarda o arquivo estragado para análise e recomeça a fila
        f.replace(f.with_suffix(f".corrompido-{int(time.time())}.json"))
        return {"pending_tasks": [], "history": []}


def _gravar(data):
    f = _arquivo()
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, f)


class EventQueue:
    @staticmethod
    def initialize():
        with _trava():
            f = _arquivo()
            if not f.exists() or f.stat().st_size == 0:
                _gravar({"pending_tasks": [], "history": []})

    @staticmethod
    def add_event(trigger_type, details):
        """Enfileira um evento. Devolve False se já há um pendente do mesmo tipo (não duplica)."""
        EventQueue.initialize()
        with _trava():
            data = _ler()
            if any(t["type"] == trigger_type for t in data["pending_tasks"]):
                return False
            data["pending_tasks"].append({"type": trigger_type, "details": details,
                                          "created_at": datetime.now().isoformat(timespec="seconds")})
            _gravar(data)
            return True

    @staticmethod
    def pop_task():
        EventQueue.initialize()
        with _trava():
            data = _ler()
            if not data["pending_tasks"]:
                return None
            task = data["pending_tasks"].pop(0)
            task["started_at"] = datetime.now().isoformat(timespec="seconds")
            data["history"] = (data["history"] + [task])[-HISTORICO_MAX:]
            _gravar(data)
            return task

    @staticmethod
    def finish_task(task, status, saida=None):
        """Marca no histórico como a tarefa terminou (ok, erro, aguardando_aprovacao...)."""
        with _trava():
            data = _ler()
            for t in reversed(data["history"]):
                if t["type"] == task["type"] and t.get("created_at") == task.get("created_at"):
                    t["status"] = status
                    t["finished_at"] = datetime.now().isoformat(timespec="seconds")
                    if saida:
                        t["saida"] = str(saida)
                    break
            _gravar(data)

    @staticmethod
    def snapshot():
        EventQueue.initialize()
        with _trava():
            return _ler()
