#!/bin/bash
# Instala o que o gerador de vídeos animados precisa (uma vez por máquina/sessão). Tudo gratuito.
set -e
cd "$(dirname "$0")"
# bibliotecas de sistema para o Blender rodar sem tela
(apt-get install -y -q libegl1 libgl1-mesa-dri libegl-mesa0 >/dev/null 2>&1 \
  || (apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libegl1 libgl1-mesa-dri libegl-mesa0 >/dev/null)) || true
command -v ffmpeg >/dev/null || apt-get install -y -q ffmpeg >/dev/null
# Blender como módulo Python (bpy 5.x pede Python 3.13)
PY=$(command -v python3.13 || command -v python3)
[ -x .venv-blender/bin/python ] || "$PY" -m venv .venv-blender
.venv-blender/bin/pip install -q bpy
# voz, desenho 2D e áudio
pip install -q kokoro-onnx soundfile skia-python numpy pillow 2>/dev/null || pip install -q --break-system-packages kokoro-onnx soundfile skia-python numpy pillow
# modelo de voz Kokoro (pt-BR), ~350 MB, baixado do GitHub
mkdir -p modelos
URL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s modelos/kokoro-v1.0.onnx ] || curl -sSL -o modelos/kokoro-v1.0.onnx $URL/kokoro-v1.0.onnx
[ -s modelos/voices-v1.0.bin ] || curl -sSL -o modelos/voices-v1.0.bin $URL/voices-v1.0.bin
echo "Pronto."
