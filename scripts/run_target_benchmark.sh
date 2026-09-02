#!/usr/bin/env bash
set -euo pipefail

RUNTIME_ROOT="${PROCRUN_BENCHMARK_ROOT:-$HOME/.local/share/procrun-benchmark}"
LLAMA_RUNTIME="$RUNTIME_ROOT/llama.cpp/build/bin/llama-completion"
LLAMA_COMMIT_FILE="$RUNTIME_ROOT/llama.cpp/.procrun-llama-commit"
MODEL="$RUNTIME_ROOT/models/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"
PRIMARY_CORPUS="tests/fixtures/component_benchmark_v1.json"
HOLDOUT_CORPUS="tests/fixtures/component_benchmark_holdout_v1.json"
OUTPUT_DIR="$RUNTIME_ROOT/results"
CACHE_DIR="$RUNTIME_ROOT/cache"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PRIMARY_REPORT="$OUTPUT_DIR/component-benchmark-$STAMP.json"
PRIMARY_TIME_REPORT="$OUTPUT_DIR/component-benchmark-$STAMP.time.txt"
HOLDOUT_REPORT="$OUTPUT_DIR/component-benchmark-holdout-$STAMP.json"
HOLDOUT_TIME_REPORT="$OUTPUT_DIR/component-benchmark-holdout-$STAMP.time.txt"
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

for required in \
  "$LLAMA_RUNTIME" \
  "$LLAMA_COMMIT_FILE" \
  "$MODEL" \
  "$PRIMARY_CORPUS" \
  "$HOLDOUT_CORPUS" \
  ".venv/bin/procrun-model-benchmark"; do
  if [[ ! -e "$required" ]]; then
    echo "missing benchmark prerequisite: $required" >&2
    exit 2
  fi
done

LLAMA_CPP_COMMIT="$(tr -d '\r\n' < "$LLAMA_COMMIT_FILE")"
if [[ ! "$LLAMA_CPP_COMMIT" =~ ^[0-9a-f]{40}$ ]]; then
  echo "invalid llama.cpp source commit marker: $LLAMA_CPP_COMMIT" >&2
  exit 2
fi

{
  printf 'utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'kernel=%s\n' "$(uname -a)"
  printf 'cpu_count=%s\n' "$(nproc)"
  printf 'memory_kib=%s\n' "$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
  printf 'root_free_bytes=%s\n' "$(df -B1 --output=avail / | tail -1 | tr -d ' ')"
  printf 'llama_runtime_sha256=%s\n' "$(sha256sum "$LLAMA_RUNTIME" | awk '{print $1}')"
  printf 'model_sha256=%s\n' "$(sha256sum "$MODEL" | awk '{print $1}')"
  printf 'repo_commit=%s\n' "$REPO_COMMIT"
  printf 'llama_cpp_commit=%s\n' "$LLAMA_CPP_COMMIT"
} > "$HOST_REPORT"

run_benchmark() {
  local label="$1"
  local corpus="$2"
  local report="$3"
  TIME_REPORT="$4"

  set +e
  /usr/bin/time -v \
    .venv/bin/procrun-model-benchmark \
      --corpus "$corpus" \
      --llama-cli "$LLAMA_RUNTIME" \
      --model "$MODEL" \
      --output "$report" \
      --cache-dir "$CACHE_DIR" \
    2> "$TIME_REPORT"
  BENCHMARK_STATUS=$?
  set -e

  if [[ "$BENCHMARK_STATUS" -ne 0 ]]; then
    echo "$label benchmark command failed with exit code $BENCHMARK_STATUS" >&2
    if [[ -f "$TIME_REPORT" ]]; then
      echo "---- benchmark stderr/resource report ----" >&2
      cat "$TIME_REPORT" >&2
      echo "---- end benchmark stderr/resource report ----" >&2
    fi
    if [[ -f "$HOST_REPORT" ]]; then
      echo "---- benchmark host report ----" >&2
      cat "$HOST_REPORT" >&2
      echo "---- end benchmark host report ----" >&2
    fi
    exit "$BENCHMARK_STATUS"
  fi
}

run_benchmark "primary" "$PRIMARY_CORPUS" "$PRIMARY_REPORT" "$PRIMARY_TIME_REPORT"
run_benchmark "holdout" "$HOLDOUT_CORPUS" "$HOLDOUT_REPORT" "$HOLDOUT_TIME_REPORT"

printf '%s\n' "primary benchmark report: $PRIMARY_REPORT"
printf '%s\n' "primary resource report:  $PRIMARY_TIME_REPORT"
printf '%s\n' "holdout benchmark report: $HOLDOUT_REPORT"
printf '%s\n' "holdout resource report:  $HOLDOUT_TIME_REPORT"
printf '%s\n' "host report:              $HOST_REPORT"
