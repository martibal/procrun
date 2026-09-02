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

The previously measured Qwen3-4B Q4_K_M artifact is `REJECTED` and must not be substituted back into
this runbook without a new explicit governance decision.

The llama.cpp revision is pinned to an exact upstream commit. The model download script uses the exact
Hugging Face revision and independently verifies size and SHA-256 before the file becomes usable.

## Evaluation inputs

One target-host session runs two independently hashed corpora:

1. `tests/fixtures/component_benchmark_v1.json` — primary diagnostic/regression corpus.
2. `tests/fixtures/component_benchmark_holdout_v1.json` — disjoint holdout corpus.

Both use the same verified model and llama.cpp runtime. Category semantics are supplied through the
frozen model-facing `selection_rule` attached to each allowed taxonomy category.

The holdout is not a source of benchmark-specific prompt answers. If its expected answers are changed
after model output has been inspected, it must become a new holdout version.

The exact scoring contract is frozen: category and evidence span must both match exactly. Do not add
fuzzy span credit or candidate-specific post-processing after seeing model outputs.

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

The benchmark report schema is `component-benchmark-report-v3`.

A fail-closed `LlamaAdapterError` from one synthetic case is recorded in that case's `inference_error`
and the corpus continues. The case is scored as failed, not silently repaired:

- a failed positive case contributes its missing expected proposal(s) as false negatives;
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

1. `component-benchmark-*.json` — primary exact quality/latency/failure report.
2. `component-benchmark-*.time.txt` — primary GNU `time -v` resource report.
3. `component-benchmark-holdout-*.json` — holdout exact quality/latency/failure report.
4. `component-benchmark-holdout-*.time.txt` — holdout GNU `time -v` resource report.
5. `component-benchmark-*.host.txt` — shared host, repository, llama.cpp and artifact provenance.

The adapter enforces the 6 GiB Linux address-space ceiling. A model that needs more than that fails
closed rather than consuming the full 8 GB host.

## Interpretation gate

Do not change the registry status from `BENCHMARK_CANDIDATE` based on one headline metric or on an
improvement confined to the primary diagnostic corpus.

The next decision must inspect at least:

- every false-positive proposal in both corpora;
- every failed/malformed case and its `inference_error`;
- every negative/abstention case in both corpora;
- exact precision, recall, F1 and whole-case match rate for both corpora;
- whether category errors remain concentrated at taxonomy boundaries;
- unresolved/empty-proposal behavior;
- median and worst measured case latency for both runs;
- peak resident-set size and remaining host headroom from both resource reports; and
- repository, model, corpus and llama.cpp provenance/hashes.

No numeric production threshold is invented in this runbook. A threshold must be frozen explicitly
before it can be used as a production approval rule.

## Cost cleanup

The end-to-end PowerShell runner deletes a successful ephemeral server automatically after the result
bundle has been copied home. If a failed run leaves a server for diagnostics, delete it explicitly:

```powershell
.\scripts\destroy_benchmark_server.ps1 -ServerName procrun-benchmark
```

The destroy command is idempotent; an already-absent server is a successful no-op. Do not leave a
failed diagnostic host running after the required evidence has been collected.
