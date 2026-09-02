from pathlib import Path

from procrun.model_registry import SELECTED_COMPONENT_MODEL

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_target_benchmark_scripts_pin_registered_model() -> None:
    download = (REPO_ROOT / "scripts" / "download_benchmark_model.sh").read_text(
        encoding="utf-8"
    )
    run_script = (REPO_ROOT / "scripts" / "run_target_benchmark.sh").read_text(
        encoding="utf-8"
    )

    assert SELECTED_COMPONENT_MODEL.revision in download
    assert SELECTED_COMPONENT_MODEL.filename in download
    assert SELECTED_COMPONENT_MODEL.identity.artifact_sha256 in download
    assert str(SELECTED_COMPONENT_MODEL.size_bytes) in download
    assert SELECTED_COMPONENT_MODEL.filename in run_script
    assert "--service huggingface_model_download" in download


def test_target_benchmark_bootstrap_pins_llama_cpp_and_dependency_closure() -> None:
    bootstrap = (REPO_ROOT / "scripts" / "bootstrap_benchmark_host.sh").read_text(
        encoding="utf-8"
    )

    assert "b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9" in bootstrap
    assert "--service github_development" in bootstrap
    assert "--dependencies" in bootstrap
    assert "-c requirements-runtime.lock -e ." in bootstrap
    assert "-DLLAMA_BUILD_SERVER=OFF" in bootstrap
    assert '--target llama-completion -j "$(nproc)"' in bootstrap


def test_target_benchmark_bootstrap_uses_credential_free_commit_archive() -> None:
    bootstrap = (REPO_ROOT / "scripts" / "bootstrap_benchmark_host.sh").read_text(
        encoding="utf-8"
    )

    assert "git clone" not in bootstrap
    assert 'git -C "$LLAMA_SRC" fetch' not in bootstrap
    assert "codeload.github.com/ggml-org/llama.cpp/tar.gz/$LLAMA_CPP_COMMIT" in bootstrap
    assert "--retry-all-errors" in bootstrap
    assert 'tar -xzf "$LLAMA_ARCHIVE" --strip-components=1 -C "$LLAMA_SRC"' in bootstrap
    assert 'printf \'%s\\n\' "$LLAMA_CPP_COMMIT" > "$LLAMA_COMMIT_FILE"' in bootstrap


def test_target_benchmark_uses_non_interactive_completion_runtime() -> None:
    run_script = (REPO_ROOT / "scripts" / "run_target_benchmark.sh").read_text(
        encoding="utf-8"
    )

    assert 'LLAMA_RUNTIME="$RUNTIME_ROOT/llama.cpp/build/bin/llama-completion"' in run_script
    assert '--llama-cli "$LLAMA_RUNTIME"' in run_script
    assert "llama_runtime_sha256=" in run_script


def test_target_benchmark_host_report_uses_pinned_llama_commit_marker() -> None:
    run_script = (REPO_ROOT / "scripts" / "run_target_benchmark.sh").read_text(
        encoding="utf-8"
    )

    assert 'LLAMA_COMMIT_FILE="$RUNTIME_ROOT/llama.cpp/.procrun-llama-commit"' in run_script
    assert 'LLAMA_CPP_COMMIT="$(tr -d \'\\r\\n\' < "$LLAMA_COMMIT_FILE")"' in run_script
    assert "invalid llama.cpp source commit marker" in run_script
    assert "printf 'llama_cpp_commit=%s\\n' \"$LLAMA_CPP_COMMIT\"" in run_script
    assert 'git -C "$RUNTIME_ROOT/llama.cpp" rev-parse HEAD' not in run_script


def test_target_benchmark_runtime_stays_outside_repository() -> None:
    run_script = (REPO_ROOT / "scripts" / "run_target_benchmark.sh").read_text(
        encoding="utf-8"
    )
    download = (REPO_ROOT / "scripts" / "download_benchmark_model.sh").read_text(
        encoding="utf-8"
    )

    assert "$HOME/.local/share/procrun-benchmark" in run_script
    assert "$HOME/.local/share/procrun-benchmark" in download


def test_target_benchmark_accepts_explicit_archived_source_commit() -> None:
    run_script = (REPO_ROOT / "scripts" / "run_target_benchmark.sh").read_text(
        encoding="utf-8"
    )

    assert 'REPO_COMMIT="${PROCRUN_REPO_COMMIT:-}"' in run_script
    assert "missing benchmark prerequisite: PROCRUN_REPO_COMMIT" in run_script
    assert "printf 'repo_commit=%s\\n' \"$REPO_COMMIT\"" in run_script


def test_target_benchmark_surfaces_runtime_failure_diagnostics() -> None:
    run_script = (REPO_ROOT / "scripts" / "run_target_benchmark.sh").read_text(
        encoding="utf-8"
    )

    assert "set +e" in run_script
    assert "BENCHMARK_STATUS=$?" in run_script
    assert 'cat "$TIME_REPORT" >&2' in run_script
    assert 'cat "$HOST_REPORT" >&2' in run_script
    assert 'exit "$BENCHMARK_STATUS"' in run_script


def test_provisioning_checks_compliance_before_billable_server_create() -> None:
    provision = (REPO_ROOT / "scripts" / "provision_benchmark_server.ps1").read_text(
        encoding="utf-8"
    )

    gate = provision.index("--service hetzner_cloud")
    create = provision.index("hcloud server create")
    assert gate < create


def test_provisioning_retries_only_transient_capacity_without_fallback() -> None:
    provision = (REPO_ROOT / "scripts" / "provision_benchmark_server.ps1").read_text(
        encoding="utf-8"
    )

    assert '[int]$CreateAttempts = 6' in provision
    assert '[int]$RetryDelaySeconds = 15' in provision
    assert '$CreateMessage -notmatch "resource_unavailable"' in provision
    assert "Retrying the same approved target" in provision
    assert "No fallback server type or location is selected automatically" in provision
    assert "Start-Sleep -Seconds $RetryDelaySeconds" in provision
    assert "Refusing to retry or create a duplicate" in provision


def test_e2e_runner_transfers_only_committed_code_and_preserves_failures() -> None:
    runner = (REPO_ROOT / "scripts" / "run_hetzner_benchmark_e2e.ps1").read_text(
        encoding="utf-8"
    )

    assert "git -C $RepoRoot archive --format=zip" in runner
    assert "$RepoCommit = (& git -C $RepoRoot rev-parse HEAD).Trim()" in runner
    assert "-o $ArchivePath $RepoCommit" in runner
    assert "PROCRUN_REPO_COMMIT=__PROCRUN_REPO_COMMIT__" in runner
    assert "$BenchmarkSucceeded = $true" in runner
    assert "$ServerCreated -and $BenchmarkSucceeded -and -not $KeepServer" in runner
    assert "intentionally still running for diagnostics" in runner
    assert "data\\exports\\model-benchmark" in runner


def test_destroy_benchmark_server_is_idempotent_when_server_is_absent() -> None:
    destroy = (REPO_ROOT / "scripts" / "destroy_benchmark_server.ps1").read_text(
        encoding="utf-8"
    )

    assert "hcloud server describe" not in destroy
    assert "hcloud server list -o json" in destroy
    assert '$lookupExitCode = $LASTEXITCODE' in destroy
    assert "does not exist; nothing to delete" in destroy
    assert '$ErrorActionPreference = "Continue"' in destroy
