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


def test_target_benchmark_bootstrap_pins_llama_cpp_commit() -> None:
    bootstrap = (REPO_ROOT / "scripts" / "bootstrap_benchmark_host.sh").read_text(
        encoding="utf-8"
    )

    assert "b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9" in bootstrap
    assert "git -C \"$LLAMA_SRC\" checkout --detach FETCH_HEAD" in bootstrap


def test_target_benchmark_runtime_stays_outside_repository() -> None:
    run_script = (REPO_ROOT / "scripts" / "run_target_benchmark.sh").read_text(
        encoding="utf-8"
    )
    download = (REPO_ROOT / "scripts" / "download_benchmark_model.sh").read_text(
        encoding="utf-8"
    )

    assert "$HOME/.local/share/procrun-benchmark" in run_script
    assert "$HOME/.local/share/procrun-benchmark" in download


def test_e2e_runner_transfers_only_committed_code_and_preserves_failures() -> None:
    runner = (REPO_ROOT / "scripts" / "run_hetzner_benchmark_e2e.ps1").read_text(
        encoding="utf-8"
    )

    assert "git -C $RepoRoot archive --format=zip" in runner
    assert "$BenchmarkSucceeded = $true" in runner
    assert "$ServerCreated -and $BenchmarkSucceeded -and -not $KeepServer" in runner
    assert "intentionally still running for diagnostics" in runner
    assert "data\\exports\\model-benchmark" in runner
