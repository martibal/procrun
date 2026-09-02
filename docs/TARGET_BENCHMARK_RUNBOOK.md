# Target benchmark runbook

Status date: 2026-09-02.

This runbook covers empirical local-model benchmarking on the target-class Hetzner host. The model
remains `BENCHMARK_CANDIDATE` before and after a run. No benchmark result automatically changes the
model registry.

## Frozen runtime inputs

- Hetzner target class: `CX33`.
- Expected class characteristics: 4 vCPU, 8 GB RAM, 80 GB local NVMe.
- Operating system: Ubuntu 24.04.
- llama.cpp release tag: `b10516`.
- llama.cpp commit:
  `b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9`.
- Model revision:
  `bc640142c66e1fdd12af0bd68f40445458f3869b`.
- Model file: `Qwen3-4B-Q4_K_M.gguf`.
- Model size: `2,497,280,256` bytes.
- Model SHA-256:
  `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`.

The llama.cpp revision is pinned to an exact upstream commit. The model download script uses the exact
Hugging Face revision and independently verifies size and SHA-256 before the file becomes usable.

## Evaluation inputs

One target-host session now runs two independently hashed corpora:

1. `tests/fixtures/component_benchmark_v1.json` — primary diagnostic/regression corpus.
2. `tests/fixtures/component_benchmark_holdout_v1.json` — disjoint holdout corpus.

Both use the same verified model and llama.cpp runtime. Category semantics are supplied through the
frozen model-facing `selection_rule` attached to each allowed taxonomy category.

The holdout is not a source of benchmark-specific prompt answers. If its expected answers are changed
after model output has been inspected, it must become a new holdout version.

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
2. creates the exact requested CX33 host with no SKU fallback;
3. waits for SSH and cloud-init;
4. uses `git archive HEAD`, so only committed repository content is transferred;
5. runs host bootstrap and the verified model download once;
6. runs both the primary and holdout corpora against the same runtime/model;
7. bundles all result artifacts and copies them to `data\exports\model-benchmark\` locally; and
8. deletes the billable server only after the result bundle exists locally.

If any remote step fails, the server is intentionally kept for diagnostics and the script prints the
explicit deletion command. Use `-KeepServer` only when a successful host must intentionally remain.

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

1. `component-benchmark-*.json` — primary exact quality/latency report.
2. `component-benchmark-*.time.txt` — primary GNU `time -v` resource report.
3. `component-benchmark-holdout-*.json` — holdout exact quality/latency report.
4. `component-benchmark-holdout-*.time.txt` — holdout GNU `time -v` resource report.
5. `component-benchmark-*.host.txt` — shared host, repository, llama.cpp and artifact provenance.

The adapter still enforces the 6 GiB Linux address-space ceiling. A model that needs more than that
fails closed rather than consuming the full 8 GB host.

## Interpretation gate

Do not change the registry status from `BENCHMARK_CANDIDATE` based on one headline metric or on an
improvement confined to the primary diagnostic corpus.

The next decision must inspect at least:

- every false-positive proposal in both corpora;
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

Do not leave a failed diagnostic host running after the required evidence has been collected.
