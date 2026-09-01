# Running the frozen local-model benchmark

The benchmark runner is intentionally separate from the production pipeline. It verifies the pinned
model bytes and local `llama-cli`, executes every frozen Portuguese case, scores exact evidence spans,
and writes one provenance-bound JSON report.

No model is downloaded by this command.

## Command

```bash
procrun-model-benchmark \
  --corpus tests/fixtures/component_benchmark_v1.json \
  --llama-cli /opt/llama.cpp/llama-cli \
  --model /var/lib/procrun/models/Qwen3-4B-Q4_K_M.gguf \
  --output /var/lib/procrun/benchmarks/qwen3-4b-q4km.json \
  --cache-dir /var/lib/procrun/cache/model-benchmark
```

The runner uses the registered `BENCHMARK_CANDIDATE` and the benchmark adapter's frozen resource and
determinism settings. A model file with the wrong size or SHA-256 fails before inference. A different
or non-executable local runtime fails before the corpus starts.

The output report records the exact corpus hash, model ID/hash, `llama-cli` hash, exact-match quality
metrics, abstention behavior, cache counts and measured inference times. It does not emit a production
approval verdict.

The report path is written atomically: a failed write cannot leave a truncated report masquerading as
a completed benchmark.
