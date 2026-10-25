#!/bin/bash
# Gera o vídeo completo de uma pasta: narração -> tomadas 3D -> montagem final.
# Uso: anime3d/renderizar.sh <pasta-do-video> [--samples N]
# Tomadas já renderizadas são puladas; apague build/shots/<TOMADA> para refazer uma.
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
VIDEO="$(cd "$1" && pwd)"; shift
SAMPLES=10; [ "$1" = "--samples" ] && SAMPLES=$2
SHOTS="$VIDEO/build/shots"; mkdir -p "$SHOTS"

echo "== narração"
python3 "$AQUI/narracao.py" "$VIDEO"

echo "== tomadas 3D (cerca de 10 s por quadro no processador)"
python3 - "$VIDEO/shots3d.py" <<'PY' | while read -r NOME QUADROS; do
import ast, sys
tree = ast.parse(open(sys.argv[1]).read())
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "TOMADAS":
        for k, v in ast.literal_eval(node.value).items():
            print(k, max(1, round(v[0] * 12)))
PY
  FEITOS=$(ls "$SHOTS/$NOME" 2>/dev/null | wc -l)
  if [ "$FEITOS" -ge "$QUADROS" ]; then echo "   $NOME: pronta"; continue; fi
  echo "   $NOME: $QUADROS quadros..."
  "$AQUI/.venv-blender/bin/python" "$VIDEO/shots3d.py" "$NOME" --samples "$SAMPLES" --saida "$SHOTS" > "$VIDEO/build/log_$NOME.txt" 2>&1
done

echo "== montagem"
python3 "$VIDEO/montagem.py" video
