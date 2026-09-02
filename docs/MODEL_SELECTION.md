# Local component-model selection gate

Status date: 2026-09-02.

## Current decision

`Qwen/Qwen3-4B-GGUF:Q4_K_M` is **rejected** as the Procurement Runway component-proposal fallback candidate.
It fit the target CX33 resource envelope, but repeated empirical runs did not meet the frozen exact
evidence contract. The product must not weaken that contract after observing a candidate's failures.

`mistralai/Ministral-3-3B-Instruct-2512-GGUF:Q4_K_M` is now the selected **benchmark candidate**. It is
not production-approved. Production activation remains blocked until the exact pinned artifact passes
the target-host primary and holdout benchmark and an explicit governance decision changes its registry
status.

## Rejected candidate: Qwen3-4B Q4_K_M

Pinned artifact retained for provenance:

- repository: `Qwen/Qwen3-4B-GGUF`
- revision: `bc640142c66e1fdd12af0bd68f40445458f3869b`
- file: `Qwen3-4B-Q4_K_M.gguf`
- size: `2,497,280,256` bytes
- SHA-256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- licence: Apache-2.0
- registry status: `REJECTED`

Measured evidence on the pinned CX33 / llama.cpp host:

1. The earlier v5 benchmark produced only 2 exact true-positive component proposals from 10 positive
   cases and poor exact precision/recall.
2. Taxonomy guidance improved apparent category choice, but the v6 primary run produced **0 exact true
   positives from 10 positive cases** because every positive proposal still violated the frozen exact
   category+evidence requirement. The two negative cases were correctly abstained.
3. The v6 holdout then produced an out-of-range token reference, proving that constrained output can
   still be malformed and must be scored as a model failure rather than trusted or guessed into range.
4. Resource feasibility was not the blocker: observed peak RSS was about 4.9 GiB with zero swap on the
   8 GiB CX33 class.

The decision is therefore quality-driven, not resource-driven. No further paid tuning runs are planned
for this exact Qwen artifact against the already-observed primary corpus.

## Selected benchmark candidate: Ministral 3 3B Instruct Q4_K_M

Pinned artifact:

- repository: `mistralai/Ministral-3-3B-Instruct-2512-GGUF`
- revision: `eb599d408350ea2bb60452cb86be7c7b2fc28227`
- file: `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf`
- size: `2,147,023,008` bytes
- SHA-256: `9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8`
- licence: Apache-2.0
- runtime boundary: llama.cpp only
- registry status: `BENCHMARK_CANDIDATE`

Official model source:

`https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF/tree/eb599d408350ea2bb60452cb86be7c7b2fc28227`

Exact official artifact page:

`https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF/blob/eb599d408350ea2bb60452cb86be7c7b2fc28227/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf`

## Why this candidate

The artifact is published by Mistral AI in GGUF form, is licensed Apache-2.0, explicitly lists
Portuguese among its supported languages, and documents direct llama.cpp use. The Q4_K_M text-model
artifact is smaller than the rejected Qwen3-4B artifact, so it is reasonable to test on the same CX33
class without increasing the infrastructure envelope.

Those properties make it eligible for a benchmark, not approved for production. Its Portuguese
component-extraction quality and malformed-output rate are still unknown until measured against the
frozen primary and disjoint holdout corpora.

## Required benchmark before APPROVED

The exact pinned artifact must be tested on the intended production class while retaining:

1. pinned llama.cpp source commit and runtime SHA-256;
2. context size, thread count and deterministic inference settings;
3. exact model artifact SHA-256 and corpus SHA-256;
4. peak RSS and swap behavior;
5. median/max latency per synthetic unmatched scope span;
6. malformed-output / failed-case rate;
7. exact category + exact evidence precision/recall on the primary corpus;
8. the same exact metrics on the disjoint holdout corpus; and
9. rerun stability/cached-output behavior where relevant.

A malformed model response is a model failure. It must never be silently normalized into an invented
valid proposal, and a failed negative case must not be counted as a correct abstention.

Promotion to `APPROVED` requires an explicit registry change with benchmark evidence. A model upgrade,
new quantization or new artifact SHA-256 must repeat the gate.

## Download policy

The application contains no production model downloader. Benchmark provisioning obtains only the exact
pinned artifact and runs `verify_local_model_artifact()` before inference. Model weights remain outside
Git. A file with the wrong size or SHA-256 is rejected before it can become the configured model
identity.
