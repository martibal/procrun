#!/usr/bin/env bash
set -euo pipefail

RUNTIME_ROOT="${PROCRUN_BENCHMARK_ROOT:-$HOME/.local/share/procrun-benchmark}"
LLAMA_CLI="$RUNTIME_ROOT/llama.cpp/build/bin/llama-cli"
MODEL="$RUNTIME_ROOT/models/Qwen3-4B-Q4_K_M.gguf"
CORPUS="tests/fixtures/component_benchmark_v1.json"
OUTPUT_DIR="$RUNTIME_ROOT/results"
CACHE_DIR="$RUNTIME_ROOT/cache"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="$OUTPUT_DIR/component-benchmark-$STAMP.json"
TIME_REPORT="$OUTPUT_DIR/component-benchmark-$STAMP.time.txt"
HOST_REPORT="$OUTPUT_DIR/component-benchmark-$STAMP.host.txt"
REPO_COMMIT="${PROCRUN_REPO_COMMIT:-}"

if [[ -z "$REPO_COMMIT" ]]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    REPO_COMMIT="$(git rev-parse HEAD)"
  else
    echo "missing benchmark prerequisite: PROCRUN_REPO_COMMIT" >&2
    exit 2
  fi
fi
if [[ ! "$REPO_COMMIT" =~ ^[0-9a-f]{40}$ ]]; then
  echo "invalid benchmark source commit: $REPO_COMMIT" >&2
  exit 2
fi

mkdir -p "$OUTPUT_DIR" "$CACHE_DIR"

for required in "$LLAMA_CLI" "$MODEL" "$CORPUS" ".venv/bin/procrun-model-benchmark"; do
  if [[ ! -e "$required" ]]; then
    echo "missing benchmark prerequisite: $required" >&2
    exit 2
  fi
done

{
  printf 'utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'kernel=%s\n' "$(uname -a)"
  printf 'cpu_count=%s\n' "$(nproc)"
  printf 'memory_kib=%s\n' "$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
  printf 'root_free_bytes=%s\n' "$(df -B1 --output=avail / | tail -1 | tr -d ' ')"
  printf 'llama_cli_sha256=%s\n' "$(sha256sum "$LLAMA_CLI" | awk '{print $1}')"
  printf 'model_sha256=%s\n' "$(sha256sum "$MODEL" | awk '{print $1}')"
  printf 'repo_commit=%s\n' "$REPO_COMMIT"
  printf 'llama_cpp_commit=%s\n' "$(git -C "$RUNTIME_ROOT/llama.cpp" rev-parse HEAD)"
} > "$HOST_REPORT"

/usr/bin/time -v \
  .venv/bin/procrun-model-benchmark \
    --corpus "$CORPUS" \
    --llama-cli "$LLAMA_CLI" \
    --model "$MODEL" \
    --output "$REPORT" \
    --cache-dir "$CACHE_DIR" \
  2> "$TIME_REPORT"

printf '%s\n' "benchmark report: $REPORT"
printf '%s\n' "resource report:  $TIME_REPORT"
printf '%s\n' "host report:      $HOST_REPORT"
