# Local component-model selection gate

Status date: 2026-09-01.

## Current decision

`Qwen/Qwen3-4B-GGUF:Q4_K_M` is pinned as the first **benchmark candidate**, not as a production-approved
model. Production activation remains blocked until the exact artifact passes the target-host resource
benchmark and the Procurement Runway component-proposal regression set.

Pinned artifact:

- repository: `Qwen/Qwen3-4B-GGUF`
- revision: `bc640142c66e1fdd12af0bd68f40445458f3869b`
- file: `Qwen3-4B-Q4_K_M.gguf`
- size: `2,497,280,256` bytes (~2.5 GB)
- SHA-256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- license: Apache-2.0
- runtime boundary: llama.cpp only
- registry status: `BENCHMARK_CANDIDATE`

Official model source:

`https://huggingface.co/Qwen/Qwen3-4B-GGUF/tree/bc640142c66e1fdd12af0bd68f40445458f3869b`

Exact official artifact page:

`https://huggingface.co/Qwen/Qwen3-4B-GGUF/blob/bc640142c66e1fdd12af0bd68f40445458f3869b/Qwen3-4B-Q4_K_M.gguf`

## Why this candidate

The artifact is published by the Qwen organisation as an official GGUF and its model page documents
direct llama.cpp use. Qwen3 is a multilingual model family trained across 119 languages; Qwen's
published Qwen3 language-support material includes Portuguese. Apache-2.0 is substantially simpler for
commercial deployment than a custom model license.

The 2.5 GB quantized file is small enough to justify a real benchmark on the planned 8 GB VPS class,
but file size alone is not a RAM-capacity proof. KV cache, context length, llama.cpp runtime overhead,
concurrency and operating-system/PostgreSQL memory all compete for the same host memory. The registry
therefore deliberately does not mark the model `APPROVED` yet.

## Required benchmark before APPROVED

The exact pinned artifact must be tested on a machine matching the intended production class. Freeze:

1. llama.cpp version/build hash;
2. context size;
3. thread count;
4. batch size;
5. inference mode/prompt template;
6. peak RSS with PostgreSQL and normal worker services present;
7. p50/p95 latency per unmatched scope span;
8. malformed-output rate;
9. exact-span validity rate;
10. taxonomy precision/recall on the frozen Phase-0/curated Portuguese component fixture set; and
11. rerun stability/cached-output behavior.

Promotion to `APPROVED` requires an explicit registry change with benchmark evidence. A model upgrade or
new quantization is a new artifact with a new SHA-256 and must repeat the gate.

## Download policy

The application contains no automatic model downloader. Model weights remain outside Git. Provisioning
must obtain the pinned artifact separately and run `verify_local_model_artifact()` before inference.
A file with the wrong size or SHA-256 is rejected before it can become the configured model identity.
