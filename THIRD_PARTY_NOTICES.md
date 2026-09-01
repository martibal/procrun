# Third-party notices and reviewed licences

Status date: 2026-09-01.

This file records software/model components intentionally used by Procurement Runway. It is not a replacement for each upstream licence; exact upstream licence text and requirements remain authoritative.

## Direct runtime dependencies

### httpx 0.28.1

- Licence: BSD-3-Clause
- Upstream: https://github.com/encode/httpx
- Use: bounded HTTP client for approved public-source collectors.
- Distribution note: preserve applicable copyright/licence notices if ProcRun software is later distributed rather than provided only as a hosted service.

### Psycopg 3.3.5

- Licence: LGPL-3.0-only
- Upstream: https://www.psycopg.org/psycopg3/
- Use: PostgreSQL client.
- Current mode: server-side SaaS.
- Distribution note: re-review LGPL obligations before any on-premise/binary distribution or modification of Psycopg itself.

### Pydantic 2.13.5

- Licence: MIT
- Upstream: https://github.com/pydantic/pydantic
- Use: strict canonical/source/model validation.
- Distribution note: preserve applicable copyright/licence notices if software is distributed.

## Frozen runtime transitive closure

`requirements-runtime.lock` freezes the reviewed Python 3.12/Linux runtime closure observed in the green 2026-09-01 CI baseline. In addition to the direct packages above, it contains:

- annotated-types 0.8.0 — MIT
- AnyIO 4.14.2 — MIT
- certifi 2026.7.22 — MPL-2.0
- h11 0.16.0 — MIT
- httpcore 1.0.9 — BSD-3-Clause
- idna 3.19 — BSD-3-Clause
- psycopg-binary 3.3.5 — LGPL-3.0-only
- pydantic-core 2.46.5 — MIT
- typing-inspection 0.4.4 — MIT
- typing-extensions 4.16.0 — PSF-2.0

The lock is a reproducibility/compliance constraint, not a substitute for retaining upstream licence text when distribution obligations apply.

## Local inference components

### Qwen3-4B-GGUF / Q4_K_M

- Licence reviewed: Apache-2.0
- Repository: https://huggingface.co/Qwen/Qwen3-4B-GGUF
- Frozen revision: `bc640142c66e1fdd12af0bd68f40445458f3869b`
- Frozen file: `Qwen3-4B-Q4_K_M.gguf`
- Frozen SHA-256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- Use: local benchmark candidate for component proposal only.
- No hosted Hugging Face inference is approved.
- Model weights are not committed to this repository.

### llama.cpp

- Licence: MIT
- Upstream: https://github.com/ggml-org/llama.cpp
- Benchmark commit: `b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9`
- Use: local/offline CPU inference runtime.

## PostgreSQL

- Licence: PostgreSQL License (permissive)
- Upstream: https://www.postgresql.org/about/licence/
- Use: canonical append-only production ledger.

## Provisioning tooling

### Hetzner Cloud CLI (`hcloud`)

- Licence: MIT
- Upstream: https://github.com/hetznercloud/cli
- Use: local creation/deletion of the ephemeral benchmark host.
- The CLI itself is not part of the customer service runtime.

## FastAPI

FastAPI is part of the locked intended web/API architecture but is **not yet a direct runtime dependency in `pyproject.toml`** at this development stage.

- Licence: MIT
- Upstream: https://github.com/fastapi/fastapi

Its exact version must be pinned and added to `src/procrun/compliance.py` before it becomes a production dependency.

## Build/development dependencies

The repository also uses development/build tooling such as Hatchling, pytest, pytest-cov, Ruff and mypy. They are not part of the current customer-delivered runtime surface. Before a commercial deployment is frozen, the build process must produce an exact dependency snapshot/SBOM including transitive packages and retain the relevant notices required for any distributed artefacts.

## Repository licence

This is a private proprietary repository. The presence of third-party open-source components does not grant a licence to the Procurement Runway source code itself. No project-wide open-source licence should be added without an explicit business/legal decision.

## Review cadence

Runtime dependency/model compliance metadata is executable in `src/procrun/compliance.py` and `src/procrun/model_registry.py`. The current review expires on 2026-11-30 and CI is intentionally designed to fail after expiry until the review is renewed from then-current upstream terms.