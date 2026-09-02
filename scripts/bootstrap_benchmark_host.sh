#!/usr/bin/env bash
set -euo pipefail

LLAMA_CPP_COMMIT="${LLAMA_CPP_COMMIT:-b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9}"
RUNTIME_ROOT="${PROCRUN_BENCHMARK_ROOT:-$HOME/.local/share/procrun-benchmark}"
LLAMA_SRC="$RUNTIME_ROOT/llama.cpp"
LLAMA_BUILD="$LLAMA_SRC/build"
LLAMA_ARCHIVE="$RUNTIME_ROOT/llama.cpp-$LLAMA_CPP_COMMIT.tar.gz"
LLAMA_COMMIT_FILE="$LLAMA_SRC/.procrun-llama-commit"

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

# Download an archive addressed by the exact immutable commit rather than using
# Git's smart-HTTP transport. Anonymous git fetches from fresh benchmark hosts
# have intermittently received an authentication challenge, while codeload is
# a plain HTTPS artifact fetch and therefore cannot fall back to a credential
# prompt. The commit marker is carried into the host report below.
rm -rf "$LLAMA_SRC"
rm -f "$LLAMA_ARCHIVE"
mkdir -p "$LLAMA_SRC"
curl \
  --fail \
  --location \
  --silent \
  --show-error \
  --retry 5 \
  --retry-delay 2 \
  --retry-all-errors \
  --connect-timeout 15 \
  --output "$LLAMA_ARCHIVE" \
  "https://codeload.github.com/ggml-org/llama.cpp/tar.gz/$LLAMA_CPP_COMMIT"
tar -xzf "$LLAMA_ARCHIVE" --strip-components=1 -C "$LLAMA_SRC"
rm -f "$LLAMA_ARCHIVE"
printf '%s\n' "$LLAMA_CPP_COMMIT" > "$LLAMA_COMMIT_FILE"

if [[ ! -f "$LLAMA_SRC/CMakeLists.txt" ]]; then
  echo "pinned llama.cpp archive did not contain CMakeLists.txt" >&2
  exit 2
fi
if [[ "$(tr -d '\r\n' < "$LLAMA_COMMIT_FILE")" != "$LLAMA_CPP_COMMIT" ]]; then
  echo "pinned llama.cpp source marker mismatch" >&2
  exit 2
fi

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

printf '%s\n' "llama.cpp commit: $(tr -d '\r\n' < "$LLAMA_COMMIT_FILE")"
printf '%s\n' "llama-completion: $LLAMA_BUILD/bin/llama-completion"
printf '%s\n' "venv: $(pwd)/.venv"
