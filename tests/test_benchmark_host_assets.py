from pathlib import Path

from procrun.model_registry import QWEN3_4B_Q4_K_M

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_target_benchmark_scripts_pin_registered_model() -> None:
    download = (REPO_ROOT / "scripts" / "download_benchmark_model.sh").read_text(
        encoding="utf-8"
    )

    assert QWEN3_4B_Q4_K_M.revision in download
    assert QWEN3_4B_Q4_K_M.filename in download
    assert QWEN3_4B_Q4_K_M.identity.artifact_sha256 in download
    assert str(QWEN3_4B_Q4_K_M.size_bytes) in download
    assert "--service huggingface_model_download" in download


def test_target_benchmark_bootstrap_pins_llama_cpp_and_dependency_closure() -> None:
    bootstrap = (REPO_ROOT / "scripts" / "bootstrap_benchmark_host.sh").read_text(
        encoding="utf-8"
    )

    assert "b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9" in bootstrap
    assert "git -C \"$LLAMA_SRC\" checkout --detach FETCH_HEAD" in bootstrap
    assert "--service github_development" in bootstrap
    assert "--dependencies" in bootstrap
    assert "-c requirements-runtime.lock -e ." in bootstrap
    assert "-DLLAMA_BUILD_SERVER=OFF" in bootstrap
    assert '--target llama-completion -j "$(nproc)"' in bootstrap


def test_target_benchmark_uses_non_interactive_completion_runtime() -> None:
    run_script = (REPO_ROOT / "scripts" / "run_target_benchmark.sh").read_text(
        encoding="utf-8"
    )

    assert 'LLAMA_RUNTIME="$RUNTIME_ROOT/llama.cpp/build/bin/llama-completion"' in run_script
    assert '--llama-cli "$LLAMA_RUNTIME"' in run_script
    assert "llama_runtime_sha256=" in run_script


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
