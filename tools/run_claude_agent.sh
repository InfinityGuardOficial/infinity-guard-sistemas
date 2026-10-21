#!/usr/bin/env bash
# Dispara um funcionário da Infinity Guard pelo Claude Code (Linux, Mac ou Git Bash no Windows).
# Uso: tools/run_claude_agent.sh <agente> "<tarefa>" [evento]
# Exemplo: tools/run_claude_agent.sh analista-de-vendas "Resuma as vendas desta semana"
# No PowerShell: python tools\run_claude_agent.py --agente <agente> --tarefa "<tarefa>"
set -euo pipefail
[ $# -ge 2 ] || { sed -n '2,5p' "$0"; exit 2; }
cd "$(dirname "$0")/.."
# no Windows, "python3" pode ser o atalho da Microsoft Store que não roda: testa antes de usar
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "Python não encontrado"; exit 1; }
exec "$PY" tools/run_claude_agent.py --agente "$1" --tarefa "$2" --evento "${3:-manual}"
