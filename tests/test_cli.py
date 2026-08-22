"""CLI subprocess smoke: synth -> freeze -> run all --dev-limit -> verdict, đúng đường
người dùng thật sự gõ. Bắt các lỗi chỉ xảy ra ở tầng CLI (vd. serialize state cho lệnh
`verdict`) mà test gọi thẳng pipeline.py không thấy được.
"""
import json
import subprocess
import sys

import pytest


@pytest.fixture(scope="module")
def cli_env(tmp_path_factory):
    root = tmp_path_factory.mktemp("cli")
    return root / "raw", root / "results"


def _run(*args, raw, out):
    return subprocess.run(
        [sys.executable, "-m", "eth_dca_os.cli", "--raw-dir", str(raw), "--out-dir", str(out),
         *args],
        capture_output=True, text=True, timeout=590)


def test_cli_full_flow(cli_env):
    raw, out = cli_env
    r = _run("synth", "--start", "2018-01-01", "--end", "2021-06-30", raw=raw, out=out)
    assert r.returncode == 0, r.stderr

    r = _run("freeze", raw=raw, out=out)
    assert r.returncode == 0, r.stderr
    meta = json.loads(r.stdout)
    assert meta["gate2"]["denominator"] == 219
    assert meta["gate3"]["size"] == 114

    r = _run("run", "all", "--dev-limit", "2", raw=raw, out=out)
    assert r.returncode == 0, r.stderr   # regression: _strip() từng crash trên key không phải str
    assert '"verdict"' in r.stdout
    assert (out / "pipeline_state.json").exists()
    state = json.loads((out / "pipeline_state.json").read_text())
    assert "gate1" in state and "gate2" in state and "gate3" in state and "controls" in state
    assert "verdict" in state and state["verdict"]["verdict"]["verdict"] in (
        "BUILD", "BUILD_WITH_MODIFICATIONS", "INCONCLUSIVE", "DO_NOT_BUILD")

    r = _run("verdict", raw=raw, out=out)
    assert r.returncode == 0, r.stderr
    payload, _ = json.JSONDecoder().raw_decode(r.stdout)
    assert payload["verdict"] in (
        "BUILD", "BUILD_WITH_MODIFICATIONS", "INCONCLUSIVE", "DO_NOT_BUILD")
    assert "reasons" in payload
