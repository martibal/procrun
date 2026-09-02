#!/usr/bin/env bash
set -euo pipefail

MODEL_REVISION="eb599d408350ea2bb60452cb86be7c7b2fc28227"
MODEL_FILENAME="Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"
MODEL_SHA256="9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8"
MODEL_SIZE_BYTES="2147023008"
RUNTIME_ROOT="${PROCRUN_BENCHMARK_ROOT:-$HOME/.local/share/procrun-benchmark}"
MODEL_DIR="$RUNTIME_ROOT/models"
MODEL_PATH="$MODEL_DIR/$MODEL_FILENAME"
MODEL_URL="https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF/resolve/$MODEL_REVISION/$MODEL_FILENAME?download=true"

python3 scripts/check_compliance_gate.py --service huggingface_model_download

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
