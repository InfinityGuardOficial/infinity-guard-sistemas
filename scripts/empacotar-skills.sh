#!/usr/bin/env bash
# Roda os testes de todas as skills e refaz os .zip (para enviar no claude.ai).
# Uso: bash scripts/empacotar-skills.sh
set -euo pipefail
cd "$(dirname "$0")/../skills"
falhou=0
for d in */; do
  s="${d%/}"
  if [ -d "$s/tests" ]; then
    (cd "$s" && python3 -m unittest discover -s tests -q) || { echo "testes falharam: $s"; falhou=1; }
  fi
done
[ "$falhou" = 0 ] || { echo "Nada foi empacotado: corrija os testes primeiro."; exit 1; }
for d in */; do
  s="${d%/}"
  rm -f "$s.zip"
  zip -qr "$s.zip" "$s" -x "*/__pycache__/*" "*.pyc" "*/custos.json" "*/estoque.json"
  echo "ok: $s.zip"
done
