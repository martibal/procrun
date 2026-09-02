#!/usr/bin/env bash
set -euo pipefail

LLAMA_CPP_COMMIT="${LLAMA_CPP_COMMIT:-b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9}"
RUNTIME_ROOT="${PROCRUN_BENCHMARK_ROOT:-$HOME/.local/share/procrun-benchmark}"
LLAMA_SRC="$RUNTIME_ROOT/llama.cpp"
LLAMA_BUILD="$LLAMA_SRC/build"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "benchmark host bootstrap requires Linux" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required from cloud-init before benchmark bootstrap" >&2
  exit 2
fi

python3 scripts/check_compliance_gate.py --service github_development
python3 scripts/check_compliance_gate.py --dependencies

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required" >&2
  exit 2
fi

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  build-essential \
  ca-certificates \
  cmake \
  curl \
  git \
  ninja-build \
  python3 \
  python3-pip \
  python3-venv \
  time

mkdir -p "$RUNTIME_ROOT"

if [[ ! -d "$LLAMA_SRC/.git" ]]; then
  mkdir -p "$LLAMA_SRC"
  git -C "$LLAMA_SRC" init -q
  git -C "$LLAMA_SRC" remote add origin https://github.com/ggml-org/llama.cpp.git
fi

# Fetch the exact pinned commit as a normal shallow repository. Do not use a
# partial/promisor clone: a missing blob would otherwise trigger a second
# network fetch during checkout and make the benchmark bootstrap less robust.
git -C "$LLAMA_SRC" config --unset-all remote.origin.promisor >/dev/null 2>&1 || true
git -C "$LLAMA_SRC" config --unset-all remote.origin.partialclonefilter >/dev/null 2>&1 || true
GIT_TERMINAL_PROMPT=0 git -C "$LLAMA_SRC" fetch --depth=1 --no-tags origin "$LLAMA_CPP_COMMIT"
git -C "$LLAMA_SRC" checkout --detach FETCH_HEAD

cmake -S "$LLAMA_SRC" -B "$LLAMA_BUILD" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_BUILD_COMMON=ON \
  -DLLAMA_BUILD_TOOLS=ON \
  -DLLAMA_BUILD_TESTS=OFF \
  -DLLAMA_BUILD_SERVER=OFF \
  -DLLAMA_BUILD_EXAMPLES=OFF \
  -DLLAMA_BUILD_APP=OFF \
  -DLLAMA_BUILD_UI=OFF \
  -DLLAMA_OPENSSL=OFF

cmake --build "$LLAMA_BUILD" --target llama-completion -j "$(nproc)"

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -c requirements-runtime.lock -e .

printf '%s\n' "llama.cpp commit: $(git -C "$LLAMA_SRC" rev-parse HEAD)"
printf '%s\n' "llama-completion: $LLAMA_BUILD/bin/llama-completion"
printf '%s\n' "venv: $(pwd)/.venv"
