#!/usr/bin/env bash
set -euo pipefail

MODEL_REVISION="bc640142c66e1fdd12af0bd68f40445458f3869b"
MODEL_FILENAME="Qwen3-4B-Q4_K_M.gguf"
MODEL_SHA256="7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5"
MODEL_SIZE_BYTES="2497280256"
RUNTIME_ROOT="${PROCRUN_BENCHMARK_ROOT:-$HOME/.local/share/procrun-benchmark}"
MODEL_DIR="$RUNTIME_ROOT/models"
MODEL_PATH="$MODEL_DIR/$MODEL_FILENAME"
MODEL_URL="https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/$MODEL_REVISION/$MODEL_FILENAME?download=true"

mkdir -p "$MODEL_DIR"

if [[ -f "$MODEL_PATH" ]]; then
  actual_size="$(stat -c '%s' "$MODEL_PATH")"
  actual_sha="$(sha256sum "$MODEL_PATH" | awk '{print $1}')"
  if [[ "$actual_size" == "$MODEL_SIZE_BYTES" && "$actual_sha" == "$MODEL_SHA256" ]]; then
    echo "model already present and verified: $MODEL_PATH"
    exit 0
  fi
  echo "existing model file failed verification; refusing to overwrite it" >&2
  exit 3
fi

partial="$MODEL_PATH.partial"

curl \
  --fail \
  --location \
  --retry 4 \
  --retry-all-errors \
  --connect-timeout 20 \
  --continue-at - \
  --output "$partial" \
  "$MODEL_URL"

actual_size="$(stat -c '%s' "$partial")"
if [[ "$actual_size" != "$MODEL_SIZE_BYTES" ]]; then
  echo "model size mismatch: expected $MODEL_SIZE_BYTES, got $actual_size" >&2
  exit 4
fi

actual_sha="$(sha256sum "$partial" | awk '{print $1}')"
if [[ "$actual_sha" != "$MODEL_SHA256" ]]; then
  echo "model SHA-256 mismatch" >&2
  exit 5
fi

mv "$partial" "$MODEL_PATH"
echo "model verified: $MODEL_PATH"
