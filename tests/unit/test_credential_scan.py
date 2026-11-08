# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""The transport regression must detect encoded as well as plain leaks."""

import base64
import importlib.util
import json
import shlex
from pathlib import Path
from urllib.parse import quote

import pytest

SPEC = importlib.util.spec_from_file_location(
    "credential_transport",
    Path(__file__).resolve().parents[1] / "credential_transport.py",
)
SCANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCANNER)
SECRET = "ACMECANARY0123456789abcdef0123456789abcdef0123456789abcdef '\"\\\nü"


@pytest.mark.parametrize(
    "encoded",
    [
        SECRET.encode(),
        json.dumps(SECRET).encode(),
        shlex.quote(SECRET).encode(),
        quote(SECRET).encode(),
        *[base64.b64encode(b"x" * n + SECRET.encode() + b"suffix") for n in range(3)],
    ],
)
def test_detects_leak(tmp_path, encoded):
    output = tmp_path / "console.log"
    output.write_bytes(b"diagnostic: " + encoded)
    assert SCANNER.scan([output], SCANNER.markers([SECRET])) == ["console.log"]


def test_clean_log(tmp_path):
    output = tmp_path / "console.log"
    output.write_text('{"censored": "no_log: true"}')
    assert SCANNER.scan([output], SCANNER.markers([SECRET])) == []
