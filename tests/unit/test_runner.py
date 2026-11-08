# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Credential handoff, diagnostic suppression and child process behavior."""

import json
import os
import signal
import subprocess
import sys
from pathlib import Path

import pytest

RUNNER = Path(__file__).resolve().parents[2] / "roles/run/files/acmesh-run.py"


def invoke(data, *command, **kwargs):
    return subprocess.run(
        [sys.executable, str(RUNNER), *command],
        input=data,
        capture_output=True,
        check=False,
        timeout=10,
        **kwargs,
    )


def test_environment_and_empty_stdin(tmp_path):
    values = {"TOKEN": "synthetic '\" $HOME \\ \n ü", "NUMBER": 17, "FLAG": False}
    result = invoke(
        json.dumps(values).encode(),
        sys.executable,
        "-c",
        "import json,os,sys; assert sys.stdin.read()==''; "
        "print(json.dumps({k:os.environ[k] for k in ('TOKEN','NUMBER','FLAG','KEPT')}))",
        env={**os.environ, "KEPT": "inherited", "TOKEN": "old"},
        cwd=tmp_path,
    )
    assert result.returncode == 0 and not result.stderr
    assert json.loads(result.stdout) == {
        **{k: str(v) for k, v in values.items()},
        "KEPT": "inherited",
    }
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "data",
    [
        b"malformed-secret",
        b'{"TOKEN": "unterminated-secret',
        b"[]",
        b"null",
        b'{"BAD=NAME": "synthetic-secret"}',
        b'{"TOKEN": "synthetic-secret\\u0000"}',
        b'{"TOKEN": ["synthetic-secret"]}',
        b'{"TOKEN": {"secret": "synthetic-secret"}}',
        b'{"TOKEN": "\xff"}',
        pytest.param(b"synthetic-secret" * 75000, id="oversized"),
    ],
)
def test_invalid_input_is_never_printed(data):
    result = invoke(data, sys.executable, "-c", "raise AssertionError")
    assert result.returncode == 64
    assert result.stdout == b""
    assert result.stderr == b"acmesh-run: invalid environment input\n"


@pytest.mark.parametrize("status", [0, 1, 2, 23])
def test_child_exit_status(status):
    result = invoke(b"{}", sys.executable, "-c", f"raise SystemExit({status})")
    assert result.returncode == status


def test_child_signal():
    result = invoke(
        b"{}",
        sys.executable,
        "-c",
        "import os,signal; os.kill(os.getpid(),signal.SIGTERM)",
    )
    assert result.returncode == -signal.SIGTERM


def test_exec_failure_is_generic():
    result = invoke(b'{"TOKEN":"synthetic-secret"}', "/missing/synthetic-secret")
    assert result.returncode == 127
    assert result.stderr == b"acmesh-run: cannot execute command\n"


def test_missing_command_cannot_look_like_skipped_issuance():
    result = invoke(b'{"TOKEN":"synthetic-secret"}')
    assert result.returncode == 64
    assert result.stdout == b""
    assert result.stderr == b"acmesh-run: missing command\n"
