# Local component-model selection gate

Status date: 2026-09-02.

## Current decision

`mistralai/Ministral-3-3B-Instruct-2512-GGUF:Q4_K_M` remains the selected **benchmark candidate**. It is
not production-approved.

The completed 2026-09-02 target-host run exposed an error in the benchmark interpretation rather than
a reason to weaken the product contract: the frozen corpus annotated minimal component phrases, while
the canonical fallback contract accepts any exact source substring contained inside one supplied
unmatched scope span. The deterministic rule engine itself stores sentence-level supporting evidence.
Therefore minimal-phrase equality is stricter than the production evidence invariant.

Benchmark report v4 keeps the old exact-span metrics as a strict diagnostic for historical continuity,
but adds product-aligned semantic scoring on the frozen `domain + category` pair. Evidence integrity is
still enforced separately by the adapter and canonical proposal validator; semantic scoring does not
permit invented, rewritten or out-of-scope source text.

No model is promoted based on the reinterpreted synthetic results. A fresh evaluation set is required
before production approval because the scoring interpretation was corrected after the current primary
and holdout outputs had been observed.

## Historical candidate: Qwen3-4B Q4_K_M

Pinned artifact retained for provenance:

- repository: `Qwen/Qwen3-4B-GGUF`
- revision: `bc640142c66e1fdd12af0bd68f40445458f3869b`
- file: `Qwen3-4B-Q4_K_M.gguf`
- size: `2,497,280,256` bytes
- SHA-256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- licence: Apache-2.0
- registry status: `INCONCLUSIVE`

Qwen's earlier target-host measurements remain valid evidence about runtime behavior and generated
outputs, including an out-of-range token reference on holdout. The prior `REJECTED` verdict is withdrawn
because it relied materially on minimal-phrase exact-match scoring that was stricter than the actual
canonical fallback acceptance rule. This does **not** make Qwen selected or approved; it only records
that the previous product-level rejection was not supported by the correct scoring contract.

No additional paid Qwen run is planned at this stage.

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

## Completed diagnostic evidence

The exact pinned Ministral artifact completed both 12-case corpora on the pinned target-host runtime
without adapter failures.

Re-scoring the already-generated proposals on the product-relevant frozen `domain + category` pair
produces the following **diagnostic-only** result:

| Corpus | Positive category TP | Category FP | Category FN | Semantic precision | Semantic recall | Correct negative abstention |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Primary | 5 | 1 | 5 | 83.3% | 50.0% | 2/2 |
| Holdout | 7 | 1 | 3 | 87.5% | 70.0% | 2/2 |

The corresponding legacy minimal-phrase exact scores were much lower because many semantically correct
proposals cited a broader or narrower exact substring than the corpus annotation. That difference is
now reported explicitly instead of being conflated with wrong taxonomy classification.

Observed median per-case latency was about 41.8 seconds on primary and 42.8 seconds on holdout; maximum
case latency was about 47.0 and 48.7 seconds respectively. The result bundle also contains the separate
GNU `time -v` resource reports and host provenance.

These numbers are not an approval gate. The current primary corpus informed earlier prompt/category
guidance, and the semantic scoring interpretation was corrected after the completed holdout had been
observed. They are useful diagnostics only.

## Required evidence before APPROVED

Production approval now requires a fresh, frozen evaluation whose scoring contract is fixed before the
model sees it. At minimum retain:

1. pinned llama.cpp source commit and runtime SHA-256;
2. exact model artifact SHA-256 and evaluation-set SHA-256;
3. deterministic inference settings and resource bounds;
4. semantic precision/recall/F1 on frozen `domain + category` expectations;
5. negative-case abstention and false-positive behavior;
6. malformed-output / failed-case rate;
7. evidence-integrity validation proving every accepted proposal cites exact bytes inside a supplied
   unmatched scope span;
8. peak RSS, swap behavior and latency on the intended host; and
9. an explicit registry/governance change.

The legacy minimal-phrase exact metric may remain in reports for diagnosis, but it is not a production
quality gate unless the canonical product contract is separately changed to require minimal phrases.

A malformed model response remains a hard model failure. It must never be silently normalized into an
invented proposal, and a failed negative case must not count as a correct abstention.

## Cost decision

Do not provision another paid benchmark host merely to rerun the same synthetic primary/holdout under
report v4. The existing outputs are sufficient to diagnose the scoring mismatch. The next paid run
should occur only after a fresh evaluation set is frozen or after real PII-safe shadow-run scope text
is available for a materially more representative gate.

## Download policy

The application contains no production model downloader. Benchmark provisioning obtains only the exact
pinned selected artifact and runs `verify_local_model_artifact()` before inference. Model weights remain
outside Git. A file with the wrong size or SHA-256 is rejected before it can become the configured model
identity.
