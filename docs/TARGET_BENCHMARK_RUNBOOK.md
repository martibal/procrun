# Target benchmark runbook

Status date: 2026-09-02.

This runbook covers empirical local-model benchmarking on the target-class Hetzner host. The selected
model remains `BENCHMARK_CANDIDATE` before and after a run. No benchmark result automatically changes
the model registry.

## Frozen runtime inputs

- Hetzner target class: `CX33`.
- Expected class characteristics: 4 vCPU, 8 GB RAM, 80 GB local NVMe.
- Operating system: Ubuntu 24.04.
- llama.cpp release tag: `b10516`.
- llama.cpp commit:
  `b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9`.
- Model repository: `mistralai/Ministral-3-3B-Instruct-2512-GGUF`.
- Model revision:
  `eb599d408350ea2bb60452cb86be7c7b2fc28227`.
- Model file: `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf`.
- Model size: `2,147,023,008` bytes.
- Model SHA-256:
  `9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8`.
- Registry status: `BENCHMARK_CANDIDATE`.

The previously measured Qwen3-4B Q4_K_M artifact is `INCONCLUSIVE`, not selected. The earlier
`REJECTED` conclusion was withdrawn because it depended materially on a minimal-phrase exact scoring
criterion that was stricter than the canonical fallback evidence acceptance rule. Qwen must still not
be substituted into this runbook without a new explicit governance decision.

The llama.cpp revision is pinned to an exact upstream commit. The model download script uses the exact
Hugging Face revision and independently verifies size and SHA-256 before the file becomes usable.

## Evaluation inputs

The 2026-09-02 target-host session ran two independently hashed corpora:

1. `tests/fixtures/component_benchmark_v1.json` — primary diagnostic/regression corpus.
2. `tests/fixtures/component_benchmark_holdout_v1.json` — disjoint holdout corpus.

Both used the same verified model and llama.cpp runtime. Category semantics are supplied through the
frozen model-facing `selection_rule` attached to each allowed taxonomy category.

The existing holdout is no longer eligible as independent production-approval evidence under report
v4 because the scoring interpretation was corrected after its outputs were observed. It remains valid
diagnostic evidence and must not be edited to improve the model's score.

## Scoring contract

The benchmark report schema is `component-benchmark-report-v4`.

Report v4 separates:

- **semantic scoring** — exact frozen `domain + category` equality, which measures the model's actual
  component-classification role; and
- **legacy exact scoring** — exact category plus byte-for-byte equality with the corpus's annotated
  minimal source phrase.

Legacy minimal-phrase exactness remains a strict diagnostic. It is not a product approval gate because
the canonical fallback validator accepts any exact source substring contained within a supplied
unmatched scope span, and the deterministic rule engine itself uses sentence-level supporting evidence.

This is not fuzzy matching. Semantic credit still requires the exact frozen category. Wrong, extra or
missing categories remain false positives/false negatives.

Evidence integrity remains a separate hard gate: the adapter must reconstruct exact source text from
valid token references inside the supplied unmatched scope span. Invalid token ranges, invented source
text, disallowed categories or out-of-scope evidence fail closed and cannot receive semantic credit.

## Local Windows provisioning

Prerequisites:

1. A Hetzner Cloud project.
2. A Hetzner API token exported only in the current shell as `HCLOUD_TOKEN`.
3. An SSH public key already registered in that project.
4. `hcloud` CLI.

The preferred one-command path from a clean Windows checkout is:

```powershell
.\scripts\run_hetzner_benchmark_e2e.ps1 -SshKey "<hetzner-ssh-key-name>"
```

Supply `-IdentityFile` when the private key is not available through the normal SSH agent/default key
locations.

The orchestration script:

1. refuses dirty/uncommitted repository state;
2. creates the exact requested CX33 host with no SKU/location fallback;
3. retries only transient Hetzner `resource_unavailable` placement failures against that same target;
4. waits for SSH and cloud-init;
5. uses `git archive HEAD`, so only committed repository content is transferred;
6. runs host bootstrap and the verified model download once;
7. runs both the primary and holdout corpora against the same runtime/model;
8. bundles all result artifacts and copies them to `data\exports\model-benchmark\` locally; and
9. deletes the billable server only after the result bundle exists locally.

If any remote infrastructure/programming step fails, the server is intentionally kept for diagnostics
and the script prints the explicit deletion command. Use `-KeepServer` only when a successful host must
intentionally remain.

## Per-case model failures

A fail-closed `LlamaAdapterError` from one synthetic case is recorded in that case's `inference_error`
and the corpus continues. The case is scored as failed, not silently repaired:

- a failed positive case contributes its missing expected category/proposal as a false negative;
- a failed negative case is not a correct abstention;
- the model-selected invalid token range is never clamped or guessed into range; and
- failed outputs are not cached as valid model batches.

Programming errors, invalid corpus fixtures, artifact verification failures and mixed provenance are
not case-quality observations and still abort the run.

This behavior exists so a paid target-host session returns as much valid diagnostic evidence as
possible without weakening fail-closed semantics.

## Manual host path

For diagnostics or a manually retained host, run from the repository root on Ubuntu:

```bash
bash scripts/bootstrap_benchmark_host.sh
bash scripts/download_benchmark_model.sh
bash scripts/run_target_benchmark.sh
```

The bootstrap installs only the required build/runtime packages, fetches the exact pinned llama.cpp
commit archive, builds the local completion runtime, creates the Python virtual environment and
installs the pinned ProcRun dependency closure.

## Generated evidence

`run_target_benchmark.sh` writes five timestamped files below:

`~/.local/share/procrun-benchmark/results/`

1. `component-benchmark-*.json` — primary semantic/exact quality, latency and failure report.
2. `component-benchmark-*.time.txt` — primary GNU `time -v` resource report.
3. `component-benchmark-holdout-*.json` — holdout semantic/exact quality, latency and failure report.
4. `component-benchmark-holdout-*.time.txt` — holdout GNU `time -v` resource report.
5. `component-benchmark-*.host.txt` — shared host, repository, llama.cpp and artifact provenance.

The adapter enforces the 6 GiB Linux address-space ceiling. A model that needs more than that fails
closed rather than consuming the full 8 GB host.

## Completed Ministral diagnostic run

The 2026-09-02 Ministral run completed all 12 primary and all 12 holdout cases with zero adapter-failed
cases. Re-scoring the already-generated proposals on the frozen semantic category key gives:

| Corpus | Semantic TP | Semantic FP | Semantic FN | Precision | Recall | Negative abstention |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Primary | 5 | 1 | 5 | 83.3% | 50.0% | 2/2 |
| Holdout | 7 | 1 | 3 | 87.5% | 70.0% | 2/2 |

Median case latency was about 41.8 seconds on primary and 42.8 seconds on holdout; maximum case latency
was about 47.0 and 48.7 seconds respectively.

These results are diagnostic only. Do not spend another paid host run simply to regenerate the same
synthetic corpora under report v4.

## Interpretation gate for the next paid run

The next paid benchmark should occur only after a **fresh evaluation set** is frozen before inference,
or after representative PII-safe shadow-run scope text is available.

The production decision must inspect at least:

- semantic precision, recall, F1 and whole-case match rate;
- every semantic false-positive proposal;
- every failed/malformed case and its `inference_error`;
- every negative/abstention case;
- evidence-integrity failures from adapter/canonical validation;
- unresolved/empty-proposal behavior;
- median and worst measured case latency;
- peak resident-set size and remaining host headroom from resource reports; and
- repository, model, evaluation-set and llama.cpp provenance/hashes.

A numeric production threshold must be frozen before that fresh evaluation is run. Do not choose the
threshold after seeing the new results.

## Cost cleanup

The end-to-end PowerShell runner deletes a successful ephemeral server automatically after the result
bundle has been copied home. If a failed run leaves a server for diagnostics, delete it explicitly:

```powershell
.\scripts\destroy_benchmark_server.ps1 -ServerName procrun-benchmark
```

The destroy command is idempotent; an already-absent server is a successful no-op. Do not leave a
failed diagnostic host running after the required evidence has been collected.
