# Running the frozen local-model benchmark

The benchmark runner is intentionally separate from the production pipeline. It verifies the pinned
model bytes and local `llama-completion`, executes every frozen Portuguese case, scores both frozen
category semantics and legacy minimal-phrase exactness, and writes one provenance-bound JSON report.

No model is downloaded by this command.

## Command

```bash
procrun-model-benchmark \
  --corpus tests/fixtures/component_benchmark_v1.json \
  --llama-cli /opt/llama.cpp/llama-completion \
  --model /var/lib/procrun/models/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf \
  --output /var/lib/procrun/benchmarks/ministral3-3b-q4km.json \
  --cache-dir /var/lib/procrun/cache/model-benchmark
```

The runner uses the registered `BENCHMARK_CANDIDATE` and the benchmark adapter's frozen resource and
determinism settings. A model file with the wrong size or SHA-256 fails before inference. A different
or non-executable local runtime fails before the corpus starts.

The v4 output report records the exact corpus hash, model ID/hash and `llama-completion` hash together
with two distinct quality views:

- `semantic_*` metrics score exact frozen `domain + category` pairs. These are the product-aligned
  model-quality diagnostics.
- `exact_*` metrics retain the historical byte-for-byte minimal phrase comparison. They are stricter
  than the canonical fallback evidence acceptance rule and are diagnostic only.

Evidence integrity is still fail-closed outside those semantic metrics: accepted model evidence must be
exact source text contained in a supplied unmatched scope span. Semantic credit cannot convert invalid
or hallucinated evidence into an accepted proposal.

The report also retains abstention behavior, failed-case counts/errors, cache counts and measured
inference times. A fail-closed model-output error is retained for that case and the remaining synthetic
cases continue; failed negative cases are not counted as correct abstentions. The report does not emit
a production approval verdict.

The report path is written atomically: a failed write cannot leave a truncated report masquerading as
a completed benchmark.
