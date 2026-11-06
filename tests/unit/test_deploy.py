# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Publication/reload ordering, failure recovery and no-op behavior."""

import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "deploy", ROOT / "roles/run/files/acmesh-deploy.py"
)
DEPLOY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DEPLOY)


@pytest.fixture
def deployment(tmp_path, monkeypatch):
    # Only the root-owned path checks are replaced: publication and validation
    # use real files, permissions and OpenSSL in this isolated directory.
    tmp_path = tmp_path.resolve()
    stage = tmp_path / "stage"
    stage.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()
    state = tmp_path / "state"
    (state / "fixture").mkdir(parents=True)
    monkeypatch.setattr(DEPLOY, "STATE_DIR", str(state))
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "ec",
            "-pkeyopt",
            "ec_paramgen_curve:P-256",
            "-nodes",
            "-days",
            "2",
            "-subj",
            "/CN=fixture.test",
            "-addext",
            "subjectAltName=DNS:fixture.test",
            "-keyout",
            str(stage / "key"),
            "-out",
            str(stage / "cert"),
        ],
        check=True,
        capture_output=True,
    )
    manifest = {
        "version": 1,
        "certificate_id": "fixture",
        "domains": ["fixture.test"],
        "staging_dir": str(stage),
        "completion_artifact": "fullchain_file",
        "reload_service": "acmesh-reload-fixture.service",
        "artifacts": {
            key: {
                "staging": str(stage / name),
                "destination": str(dest / name),
                "uid": os.getuid(),
                "gid": os.getgid(),
                "mode": mode,
            }
            for key, name, mode in [
                ("fullchain_file", "cert", "0644"),
                ("key_file", "key", "0600"),
            ]
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    monkeypatch.setattr(
        DEPLOY,
        "open_locked_manifest",
        lambda _: (os.open(manifest_path, os.O_RDONLY), manifest),
    )
    monkeypatch.setattr(
        DEPLOY,
        "open_staging_dir",
        lambda _: os.open(stage, os.O_RDONLY | os.O_DIRECTORY),
    )
    calls = []
    real_run = subprocess.run

    def run(command, **kwargs):
        if command[0] == DEPLOY.SYSTEMCTL:
            # Reload may only see the complete, validated set.
            assert (dest / "cert").read_bytes() == (stage / "cert").read_bytes()
            assert (dest / "key").read_bytes() == (stage / "key").read_bytes()
            calls.append(command)
            return subprocess.CompletedProcess(command, 0)
        return real_run(command, check=kwargs.pop("check", False), **kwargs)

    monkeypatch.setattr(DEPLOY.subprocess, "run", run)
    return manifest, manifest_path, stage, dest, state / "fixture/reload-pending", calls


def test_publish_reload_metadata_and_noop(deployment):
    _manifest, path, _stage, dest, pending, calls = deployment
    assert DEPLOY.main(["--check", str(path)]) == DEPLOY.EXIT_DRIFT
    assert not calls and not pending.exists()
    assert DEPLOY.main([str(path)]) == 0
    assert len(calls) == 1 and not pending.exists()
    inode = (dest / "cert").stat().st_ino
    assert DEPLOY.main([str(path)]) == 0
    assert len(calls) == 1 and (dest / "cert").stat().st_ino == inode
    (dest / "key").chmod(0o400)
    assert DEPLOY.main([str(path)]) == 0
    assert len(calls) == 1 and (dest / "key").stat().st_mode & 0o777 == 0o600
    # Content changed outside the completion artifact still needs a reload.
    (dest / "key").write_bytes(b"old key")
    assert DEPLOY.main([str(path)]) == 0
    assert len(calls) == 2 and (dest / "cert").stat().st_ino == inode


def test_failed_reload_retries_without_republishing(deployment, monkeypatch):
    _manifest, path, _stage, dest, pending, calls = deployment
    run = DEPLOY.subprocess.run

    def fail(command, **kwargs):
        if command[0] == DEPLOY.SYSTEMCTL:
            return subprocess.CompletedProcess(command, 1)
        return run(command, **kwargs)

    monkeypatch.setattr(DEPLOY.subprocess, "run", fail)
    assert DEPLOY.main([str(path)]) == DEPLOY.EXIT_RELOAD
    inode = (dest / "cert").stat().st_ino
    assert pending.exists()
    assert DEPLOY.main(["--check", str(path)]) == DEPLOY.EXIT_DRIFT
    monkeypatch.setattr(DEPLOY.subprocess, "run", run)
    assert DEPLOY.main([str(path)]) == 0
    assert len(calls) == 1 and not pending.exists()
    assert (dest / "cert").stat().st_ino == inode


def test_validation_failure_never_reloads(deployment):
    _manifest, path, stage, dest, pending, calls = deployment
    (stage / "cert").write_bytes(b"invalid")
    assert DEPLOY.main([str(path)]) == DEPLOY.EXIT_VALIDATION
    assert not calls and not pending.exists() and not list(dest.iterdir())


def test_publish_failure_never_reloads(deployment, monkeypatch):
    _manifest, path, _stage, dest, _pending, calls = deployment
    write = DEPLOY.write_replacement

    def fail(entry, data):
        if entry["artifact"] == "fullchain_file":
            raise OSError("publish failed")
        write(entry, data)

    monkeypatch.setattr(DEPLOY, "write_replacement", fail)
    assert DEPLOY.main([str(path)]) == DEPLOY.EXIT_PUBLISH
    assert not calls and not list(dest.iterdir())


@pytest.mark.parametrize("mode", ["u=rw,g=r,o=", "0660", "0641", "4640", "0644"])
def test_helper_rejects_unsafe_or_unnormalized_key_modes(deployment, mode):
    manifest, *_rest = deployment
    manifest["artifacts"]["key_file"]["mode"] = mode
    with pytest.raises(DEPLOY.DeployError):
        DEPLOY.validate_manifest(manifest)


def test_helper_rejects_foreign_reload_service(deployment):
    manifest, *_rest = deployment
    manifest["reload_service"] = "unrelated.service"
    with pytest.raises(DEPLOY.DeployError):
        DEPLOY.validate_manifest(manifest)


@pytest.mark.parametrize("certificate_id", [".", "..", "../other"])
def test_helper_rejects_state_directory_traversal(deployment, certificate_id):
    manifest, *_rest = deployment
    manifest["certificate_id"] = certificate_id
    with pytest.raises(DEPLOY.DeployError):
        DEPLOY.validate_manifest(manifest)
