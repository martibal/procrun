# Target benchmark runbook

Status date: 2026-09-01.

This runbook covers the first empirical local-model benchmark on the target-class Hetzner host.
The model remains `BENCHMARK_CANDIDATE` before and after this run. No benchmark result automatically
changes the model registry.

## Frozen runtime inputs

- Hetzner target class: `CX33`.
- Expected class characteristics verified before this run: 4 vCPU, 8 GB RAM, 80 GB local NVMe.
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

The llama.cpp revision is pinned to an exact upstream commit rather than a moving branch. The model
download script uses the exact Hugging Face revision and independently verifies size and SHA-256
before the file becomes usable.

## Local Windows provisioning

The repository includes an optional PowerShell helper for the billable server-creation step.

Prerequisites:

1. A Hetzner Cloud project.
2. A Hetzner API token exported only in the current shell as `HCLOUD_TOKEN`.
3. An SSH public key already registered in that project.
4. `hcloud` CLI. On Windows it can be installed with:
   `winget install --id HetznerCloud.CLI -e`.

Create the ephemeral benchmark host:

```powershell
$env:HCLOUD_TOKEN = "<temporary-token>"
.\scripts\provision_benchmark_server.ps1 -SshKey "<hetzner-ssh-key-name>"
```

The helper refuses to create a second server with the same name. It does not enable backups or
deletion protection because the benchmark host is intended to be short-lived.

### One-command end-to-end run

Once `HCLOUD_TOKEN` is set and the named SSH key exists in the Hetzner project, the preferred path
from a clean Windows checkout is:

```powershell
.\scripts\run_hetzner_benchmark_e2e.ps1 -SshKey "<hetzner-ssh-key-name>"
```

This orchestration script:

1. creates the exact requested CX33 host with no SKU fallback;
2. waits for SSH and cloud-init;
3. uses `git archive HEAD`, so only committed repository content is transferred;
4. runs host bootstrap, the verified model download and the frozen benchmark remotely;
5. bundles the three result artifacts and copies them to
   `data\exports\model-benchmark\` locally; and
6. deletes the billable server only after the result bundle exists locally.

If any remote step fails, the server is intentionally kept for diagnostics and the script prints the
explicit deletion command. Use `-KeepServer` to keep a successful host as well. An optional
`-IdentityFile` can be supplied when the private key is not available through the normal SSH agent
or default key locations.

## Host setup

Connect to the new Ubuntu host. Clone this private repository using the user's normal GitHub
authentication method, then run from the repository root:

```bash
bash scripts/bootstrap_benchmark_host.sh
bash scripts/download_benchmark_model.sh
bash scripts/run_target_benchmark.sh
```

The bootstrap:

- installs only the build/runtime packages required for the CPU benchmark;
- fetches the exact pinned llama.cpp commit;
- builds only the local `llama-cli` path needed by the adapter;
- creates a repository-local Python virtual environment; and
- installs ProcRun from the checked-out repository.

The model download is deliberately separate from bootstrap because it is the large network transfer.
An existing incorrect model file is never overwritten silently.

## Generated evidence

`run_target_benchmark.sh` writes three timestamped files below:

`~/.local/share/procrun-benchmark/results/`

1. `component-benchmark-*.json` — exact quality/latency report from the frozen corpus.
2. `component-benchmark-*.time.txt` — GNU `time -v`, including peak resident-set size.
3. `component-benchmark-*.host.txt` — host, disk, repository, llama.cpp and artifact hashes.

The adapter itself still enforces the 6 GiB Linux address-space ceiling. Therefore a model that needs
more than that fails closed rather than consuming the full 8 GB host.

## Interpretation gate

Do not change the registry status from `BENCHMARK_CANDIDATE` based on one headline metric.

The next decision must inspect at least:

- every false-positive proposal;
- both abstention cases;
- exact-span precision and recall;
- unresolved behavior;
- median and worst measured case latency;
- peak resident-set size and remaining host headroom; and
- reproducibility of the report hashes.

No numeric production threshold is invented in this runbook. Thresholds must be frozen explicitly
after the first empirical report is available.

## Cost cleanup

After copying the three result files off the ephemeral server, delete it from the Windows machine:

```powershell
.\scripts\destroy_benchmark_server.ps1
```

The deletion helper is intentionally separate from the benchmark command so a failed benchmark cannot
silently delete the only diagnostic evidence before it has been inspected.
