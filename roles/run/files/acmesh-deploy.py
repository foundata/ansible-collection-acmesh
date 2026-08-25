#!/usr/bin/env python3
"""Publish staged acme.sh certificate files to their final destinations.

Managed by Ansible (foundata.acmesh.run role); local changes will be
overwritten. Executed as root by the acmesh-deploy-* systemd service units
(and by the role itself with --check to detect deployment drift). Python
standard library only (3.9+), certificate parsing via fixed calls to the
openssl binary; no shell is ever invoked.

Trust model: the unprivileged acme.sh service account controls only the
*content* of the staging files. Destinations, ownership, modes and helper
arguments come exclusively from a root-owned JSON manifest below
/etc/acmesh-deploy.d. All staged input is validated (size limits, PEM
parsing, private key/certificate match, certificate domain coverage) before
anything is written. The artifact acme.sh writes last (the manifest's
"completion_artifact") is published last, so path units watching the
destination only fire after a complete deployment; metadata-only fixes use
chown/chmod on the existing inode and do not fire them at all.

Limitation: publishing uses per-file atomic renames plus rollback when a
later publish operation fails. A hard system crash in the middle of
publishing files that live on different filesystems can still leave a mixed
set; a fully atomic transaction across filesystems is not possible.

Usage:
  acmesh-deploy [--check] /etc/acmesh-deploy.d/<certificate-id>.json

Exit codes:
  0  success (deployed, already in sync, or --check found no drift)
  1  usage error or unexpected failure
  2  manifest error (untrusted, malformed, unknown keys, invalid paths)
  3  drift detected (--check only)
  4  staged input validation error (previous deployment left untouched)
  5  publish error (rollback attempted)
"""

import argparse
import fcntl
import json
import os
import re
import stat
import subprocess
import sys
import time

# Keep in sync with __run_acmesh_deploy_manifest_dir_path in the role's
# vars/main.yml. Only manifests directly below this root-owned directory are
# accepted, so a manipulated path argument cannot point the helper at an
# attacker-supplied manifest.
MANIFEST_DIR = "/etc/acmesh-deploy.d"

OPENSSL = "/usr/bin/openssl"

# Conservative input limits: certificates, chains and keys are a few KiB.
MAX_ARTIFACT_SIZE = 1024 * 1024
MAX_MANIFEST_SIZE = 1024 * 1024

# Waiting instead of failing immediately lets an Ansible-triggered and a
# path-unit-triggered deployment of the same certificate coexist.
LOCK_TIMEOUT_SECONDS = 60

ARTIFACT_KEYS = ("ca_file", "cert_file", "fullchain_file", "key_file")
ARTIFACT_SPEC_KEYS = {"staging", "destination", "uid", "gid", "mode"}
MANIFEST_KEYS = {
    "version",
    "certificate_id",
    "domains",
    "staging_dir",
    "completion_artifact",
    "artifacts",
}

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_MANIFEST = 2
EXIT_DRIFT = 3
EXIT_VALIDATION = 4
EXIT_PUBLISH = 5

PEM_CERT_RE = re.compile(
    b"-----BEGIN CERTIFICATE-----.+?-----END CERTIFICATE-----", re.DOTALL
)


class DeployError(Exception):
    """Deployment failure with a dedicated exit code."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def log(message):
    """Write a concise message to stderr (journal via SyslogIdentifier)."""
    print("acmesh-deploy: {0}".format(message), file=sys.stderr, flush=True)


def run_openssl(arguments, data):
    """Run a fixed openssl subcommand with input via stdin, without a shell.

    Passing the (already read) bytes via stdin guarantees validation and
    publishing use the same data and keeps file paths out of the command.
    """
    try:
        return subprocess.run(
            [OPENSSL] + arguments,
            input=data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            check=False,
        )
    except OSError as exc:
        raise DeployError(
            EXIT_ERROR, "cannot execute {0}: {1}".format(OPENSSL, exc)
        ) from exc


def check_no_traversal(code, label, path):
    """Reject relative, empty, non-normalized or traversing paths."""
    if not isinstance(path, str) or not path:
        raise DeployError(code, "{0}: path must be a non-empty string".format(label))
    if not path.startswith("/"):
        raise DeployError(code, "{0}: path is not absolute: {1}".format(label, path))
    if path != os.path.normpath(path):
        raise DeployError(
            code, "{0}: path is not normalized: {1}".format(label, path)
        )
    if ".." in path.split("/"):
        raise DeployError(
            code, "{0}: path contains traversal: {1}".format(label, path)
        )


def open_locked_manifest(path):
    """Open, verify and lock the manifest; return (fd, parsed manifest).

    The manifest must be a root-owned regular file directly below
    MANIFEST_DIR and must not be writable by group or others. The exclusive
    flock on it is the per-certificate deployment lock; it is held until the
    process exits.
    """
    absolute = os.path.abspath(path)
    if os.path.dirname(absolute) != MANIFEST_DIR:
        raise DeployError(
            EXIT_MANIFEST,
            "manifest must reside directly below {0}: {1}".format(
                MANIFEST_DIR, absolute
            ),
        )
    try:
        fd = os.open(absolute, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        raise DeployError(
            EXIT_MANIFEST, "cannot open manifest {0}: {1}".format(absolute, exc)
        ) from exc
    file_stat = os.fstat(fd)
    if not stat.S_ISREG(file_stat.st_mode):
        os.close(fd)
        raise DeployError(
            EXIT_MANIFEST, "manifest is not a regular file: {0}".format(absolute)
        )
    if file_stat.st_uid != 0:
        os.close(fd)
        raise DeployError(
            EXIT_MANIFEST, "manifest is not owned by root: {0}".format(absolute)
        )
    if file_stat.st_mode & 0o022:
        os.close(fd)
        raise DeployError(
            EXIT_MANIFEST,
            "manifest is group- or world-writable: {0}".format(absolute),
        )
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except OSError:
            if time.monotonic() >= deadline:
                os.close(fd)
                raise DeployError(
                    EXIT_ERROR,
                    "timeout waiting for the deployment lock on {0}".format(
                        absolute
                    ),
                )
            time.sleep(0.5)
    if file_stat.st_size > MAX_MANIFEST_SIZE:
        raise DeployError(
            EXIT_MANIFEST, "manifest exceeds size limit: {0}".format(absolute)
        )
    raw = b""
    while True:
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        raw += chunk
        if len(raw) > MAX_MANIFEST_SIZE:
            raise DeployError(
                EXIT_MANIFEST, "manifest exceeds size limit: {0}".format(absolute)
            )
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise DeployError(
            EXIT_MANIFEST, "manifest is not valid JSON: {0}".format(exc)
        ) from exc
    return fd, manifest


def validate_manifest(manifest):
    """Strictly validate the manifest structure; reject unknown keys."""
    if not isinstance(manifest, dict):
        raise DeployError(EXIT_MANIFEST, "manifest root must be an object")
    unknown = set(manifest) - MANIFEST_KEYS
    if unknown:
        raise DeployError(
            EXIT_MANIFEST,
            "manifest contains unknown key(s): {0}".format(", ".join(sorted(unknown))),
        )
    missing = MANIFEST_KEYS - set(manifest)
    if missing:
        raise DeployError(
            EXIT_MANIFEST,
            "manifest misses key(s): {0}".format(", ".join(sorted(missing))),
        )
    if manifest["version"] != 1:
        raise DeployError(
            EXIT_MANIFEST,
            "unsupported manifest version: {0!r}".format(manifest["version"]),
        )
    certificate_id = manifest["certificate_id"]
    if (
        not isinstance(certificate_id, str)
        or not re.fullmatch(r"[a-z0-9.-]{1,200}", certificate_id)
    ):
        raise DeployError(EXIT_MANIFEST, "invalid certificate_id")
    domains = manifest["domains"]
    if (
        not isinstance(domains, list)
        or not domains
        or not all(isinstance(d, str) and d for d in domains)
    ):
        raise DeployError(
            EXIT_MANIFEST, "domains must be a non-empty list of non-empty strings"
        )
    staging_dir = manifest["staging_dir"]
    check_no_traversal(EXIT_MANIFEST, "staging_dir", staging_dir)
    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, dict) or not artifacts:
        raise DeployError(EXIT_MANIFEST, "artifacts must be a non-empty object")
    unknown = set(artifacts) - set(ARTIFACT_KEYS)
    if unknown:
        raise DeployError(
            EXIT_MANIFEST,
            "unknown artifact key(s): {0}".format(", ".join(sorted(unknown))),
        )
    if manifest["completion_artifact"] not in artifacts:
        raise DeployError(
            EXIT_MANIFEST, "completion_artifact is not a configured artifact"
        )
    destinations = set()
    for artifact, spec in artifacts.items():
        label = "artifacts.{0}".format(artifact)
        if not isinstance(spec, dict):
            raise DeployError(EXIT_MANIFEST, "{0} must be an object".format(label))
        if set(spec) != ARTIFACT_SPEC_KEYS:
            raise DeployError(
                EXIT_MANIFEST,
                "{0} must have exactly the keys: {1}".format(
                    label, ", ".join(sorted(ARTIFACT_SPEC_KEYS))
                ),
            )
        staging = spec["staging"]
        check_no_traversal(EXIT_MANIFEST, label + ".staging", staging)
        if os.path.dirname(staging) != staging_dir or not os.path.basename(staging):
            raise DeployError(
                EXIT_MANIFEST,
                "{0}.staging must reside directly below staging_dir".format(label),
            )
        destination = spec["destination"]
        check_no_traversal(EXIT_MANIFEST, label + ".destination", destination)
        if destination == staging_dir or destination.startswith(staging_dir + "/"):
            raise DeployError(
                EXIT_MANIFEST,
                "{0}.destination must not reside below staging_dir".format(label),
            )
        if not os.path.dirname(destination) or not os.path.basename(destination):
            raise DeployError(
                EXIT_MANIFEST, "{0}.destination is invalid".format(label)
            )
        if destination in destinations:
            raise DeployError(
                EXIT_MANIFEST,
                "duplicate destination: {0}".format(destination),
            )
        destinations.add(destination)
        for id_key in ("uid", "gid"):
            value = spec[id_key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise DeployError(
                    EXIT_MANIFEST,
                    "{0}.{1} must be a non-negative integer".format(label, id_key),
                )
        mode = spec["mode"]
        if not isinstance(mode, str) or not re.fullmatch(r"[0-7]{3,4}", mode):
            raise DeployError(
                EXIT_MANIFEST,
                "{0}.mode must be an octal string such as \"0640\"".format(label),
            )
        mode_int = int(mode, 8)
        if mode_int & 0o7111:
            raise DeployError(
                EXIT_MANIFEST,
                "{0}.mode must not contain execute or setuid/setgid/sticky "
                "bits".format(label),
            )
        if mode_int & 0o022:
            raise DeployError(
                EXIT_MANIFEST,
                "{0}.mode must not be group- or world-writable".format(label),
            )
        if artifact == "key_file" and mode_int & 0o007:
            raise DeployError(
                EXIT_MANIFEST,
                "{0}.mode must not grant world access to a private key".format(label),
            )


def open_staging_dir(staging_dir):
    """Open the staging directory via a symlink-free, trusted path walk.

    Every component is opened with O_NOFOLLOW | O_DIRECTORY relative to the
    previous one, so no component may be a symlink. All components except the
    final one (the per-certificate staging directory, owned by the service
    user) must be root-owned and not group- or world-writable. This is
    defense in depth: with the default layout the whole chain up to the
    staging base is root-owned anyway.
    """
    parts = [part for part in staging_dir.split("/") if part]
    walked = "/"
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for index, part in enumerate(parts):
            try:
                next_fd = os.open(
                    part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd
                )
            except OSError as exc:
                raise DeployError(
                    EXIT_VALIDATION,
                    "cannot open staging path component {0!r} below {1}: "
                    "{2}".format(part, walked, exc),
                ) from exc
            os.close(fd)
            fd = next_fd
            walked = os.path.join(walked, part)
            dir_stat = os.fstat(fd)
            if index < len(parts) - 1:
                if dir_stat.st_uid != 0 or dir_stat.st_mode & 0o022:
                    raise DeployError(
                        EXIT_VALIDATION,
                        "untrusted staging path component (must be root-owned "
                        "and not group/world-writable): {0}".format(walked),
                    )
            elif dir_stat.st_mode & 0o002:
                raise DeployError(
                    EXIT_VALIDATION,
                    "staging directory is world-writable: {0}".format(walked),
                )
        return fd
    except DeployError:
        os.close(fd)
        raise


def read_staging_file(staging_dir_fd, staging_path):
    """Read one staged artifact exactly once, with strict input checks."""
    name = os.path.basename(staging_path)
    try:
        # O_NONBLOCK prevents blocking on a planted FIFO; the fstat below
        # rejects everything that is not a regular file.
        fd = os.open(
            name,
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
            dir_fd=staging_dir_fd,
        )
    except OSError as exc:
        raise DeployError(
            EXIT_VALIDATION,
            "cannot open staged file {0}: {1}".format(staging_path, exc),
        ) from exc
    try:
        file_stat = os.fstat(fd)
        if not stat.S_ISREG(file_stat.st_mode):
            raise DeployError(
                EXIT_VALIDATION,
                "staged file is not a regular file: {0}".format(staging_path),
            )
        if file_stat.st_size > MAX_ARTIFACT_SIZE:
            raise DeployError(
                EXIT_VALIDATION,
                "staged file exceeds the size limit: {0}".format(staging_path),
            )
        os.set_blocking(fd, True)
        data = b""
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            data += chunk
            if len(data) > MAX_ARTIFACT_SIZE:
                raise DeployError(
                    EXIT_VALIDATION,
                    "staged file exceeds the size limit: {0}".format(staging_path),
                )
        if not data:
            raise DeployError(
                EXIT_VALIDATION, "staged file is empty: {0}".format(staging_path)
            )
        return data
    finally:
        os.close(fd)


def certificate_names(data):
    """Return the lowercased DNS SAN entries (plus subject CN) of a leaf."""
    names = set()
    result = run_openssl(["x509", "-noout", "-ext", "subjectAltName"], data)
    if result.returncode == 0:
        for match in re.finditer(
            r"DNS:([^\s,]+)", result.stdout.decode("utf-8", "replace")
        ):
            names.add(match.group(1).lower())
    result = run_openssl(
        ["x509", "-noout", "-subject", "-nameopt", "RFC2253"], data
    )
    if result.returncode == 0:
        match = re.search(
            r"CN=([^,\n]+)", result.stdout.decode("utf-8", "replace")
        )
        if match:
            names.add(match.group(1).strip().lower())
    return names


def validate_staged(manifest, staged):
    """Parse every artifact, verify key/leaf match and domain coverage."""
    for artifact, data in staged.items():
        if artifact == "key_file":
            result = run_openssl(["pkey", "-noout"], data)
            if result.returncode != 0:
                raise DeployError(
                    EXIT_VALIDATION, "staged private key does not parse"
                )
        else:
            blocks = PEM_CERT_RE.findall(data)
            if not blocks:
                raise DeployError(
                    EXIT_VALIDATION,
                    "staged {0} contains no PEM certificate".format(artifact),
                )
            for block in blocks:
                result = run_openssl(["x509", "-noout"], block)
                if result.returncode != 0:
                    raise DeployError(
                        EXIT_VALIDATION,
                        "staged {0} contains an invalid certificate".format(
                            artifact
                        ),
                    )
    # The leaf certificate is the cert_file and/or the first certificate of
    # the fullchain_file. Both (if configured) must cover the certificate's
    # domains and match the staged private key.
    leaves = []
    if "cert_file" in staged:
        leaves.append(("cert_file", PEM_CERT_RE.findall(staged["cert_file"])[0]))
    if "fullchain_file" in staged:
        leaves.append(
            ("fullchain_file", PEM_CERT_RE.findall(staged["fullchain_file"])[0])
        )
    key_pubkey = None
    if "key_file" in staged:
        result = run_openssl(["pkey", "-pubout"], staged["key_file"])
        if result.returncode != 0:
            raise DeployError(
                EXIT_VALIDATION, "cannot derive the staged key's public key"
            )
        key_pubkey = result.stdout
    for artifact, leaf in leaves:
        names = certificate_names(leaf)
        for domain in manifest["domains"]:
            if domain.lower() not in names:
                raise DeployError(
                    EXIT_VALIDATION,
                    "staged {0} does not cover the configured domain "
                    "{1}".format(artifact, domain),
                )
        if key_pubkey is not None:
            result = run_openssl(["x509", "-noout", "-pubkey"], leaf)
            if result.returncode != 0:
                raise DeployError(
                    EXIT_VALIDATION,
                    "cannot derive the public key of the staged {0}".format(
                        artifact
                    ),
                )
            if result.stdout != key_pubkey:
                raise DeployError(
                    EXIT_VALIDATION,
                    "the staged private key does not match the staged "
                    "{0}".format(artifact),
                )


def examine_destination(artifact, spec):
    """Inspect one destination; return its publish plan entry.

    The destination's parent directory is opened as a directory (ancestors
    are root-configured via the manifest, symlinked ancestors are therefore
    acceptable); the leaf itself is handled with O_NOFOLLOW and symlink or
    non-regular leaves are rejected.
    """
    destination = spec["destination"]
    directory = os.path.dirname(destination)
    name = os.path.basename(destination)
    try:
        dir_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    except OSError as exc:
        raise DeployError(
            EXIT_VALIDATION,
            "cannot open destination directory {0}: {1} (the Ansible role "
            "creates and manages it)".format(directory, exc),
        ) from exc
    entry = {
        "artifact": artifact,
        "spec": spec,
        "dir_fd": dir_fd,
        "name": name,
        "exists": False,
        "old_data": None,
        "old_stat": None,
        "state": "missing",
    }
    try:
        leaf_stat = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except FileNotFoundError:
        return entry
    if stat.S_ISLNK(leaf_stat.st_mode):
        raise DeployError(
            EXIT_VALIDATION,
            "destination is a symlink: {0}".format(destination),
        )
    if not stat.S_ISREG(leaf_stat.st_mode):
        raise DeployError(
            EXIT_VALIDATION,
            "destination is not a regular file: {0}".format(destination),
        )
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dir_fd)
    try:
        old_data = b""
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            old_data += chunk
            if len(old_data) > MAX_ARTIFACT_SIZE:
                # Unexpectedly large existing file: treat as content drift,
                # do not keep reading.
                old_data = None
                break
        entry["old_stat"] = os.fstat(fd)
    finally:
        os.close(fd)
    entry["exists"] = True
    entry["old_data"] = old_data
    return entry


def plan_state(entry, new_data):
    """Classify one destination: in_sync, metadata or content drift."""
    if not entry["exists"] or entry["old_data"] != new_data:
        return "content"
    spec = entry["spec"]
    old_stat = entry["old_stat"]
    if (
        old_stat.st_uid != spec["uid"]
        or old_stat.st_gid != spec["gid"]
        or stat.S_IMODE(old_stat.st_mode) != int(spec["mode"], 8)
    ):
        return "metadata"
    return "in_sync"


def write_replacement(entry, data):
    """Write data as a temporary file next to the destination and rename it.

    Ownership and mode are applied and flushed before the rename publishes
    the file; the directory is flushed afterwards.
    """
    spec = entry["spec"]
    dir_fd = entry["dir_fd"]
    temp_name = ".{0}.acmesh-deploy.tmp".format(entry["name"])
    try:
        os.unlink(temp_name, dir_fd=dir_fd)
    except FileNotFoundError:
        pass
    fd = os.open(
        temp_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600,
        dir_fd=dir_fd,
    )
    try:
        offset = 0
        while offset < len(data):
            offset += os.write(fd, data[offset:])
        os.fchown(fd, spec["uid"], spec["gid"])
        os.fchmod(fd, int(spec["mode"], 8))
        os.fsync(fd)
    except OSError:
        os.close(fd)
        try:
            os.unlink(temp_name, dir_fd=dir_fd)
        except OSError:
            pass
        raise
    os.close(fd)
    try:
        os.rename(temp_name, entry["name"], src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
    except OSError:
        try:
            os.unlink(temp_name, dir_fd=dir_fd)
        except OSError:
            pass
        raise
    os.fsync(dir_fd)


def apply_metadata(entry):
    """Fix ownership/mode on the existing inode (no rename, no path events)."""
    spec = entry["spec"]
    fd = os.open(
        entry["name"], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=entry["dir_fd"]
    )
    try:
        os.fchown(fd, spec["uid"], spec["gid"])
        os.fchmod(fd, int(spec["mode"], 8))
    finally:
        os.close(fd)


def rollback(published):
    """Best-effort restoration of artifacts already published in this run."""
    for entry in reversed(published):
        destination = entry["spec"]["destination"]
        try:
            if entry["exists"] and entry["old_data"] is not None:
                restore = {
                    "artifact": entry["artifact"],
                    "name": entry["name"],
                    "dir_fd": entry["dir_fd"],
                    "spec": {
                        "destination": destination,
                        "uid": entry["old_stat"].st_uid,
                        "gid": entry["old_stat"].st_gid,
                        "mode": format(stat.S_IMODE(entry["old_stat"].st_mode), "04o"),
                    },
                }
                write_replacement(restore, entry["old_data"])
                log("rollback: restored {0}".format(destination))
            else:
                os.unlink(entry["name"], dir_fd=entry["dir_fd"])
                log("rollback: removed {0}".format(destination))
        except OSError as exc:
            log(
                "rollback of {0} failed: {1} (manual intervention may be "
                "required)".format(destination, exc)
            )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="acmesh-deploy",
        description=(
            "Validate staged acme.sh certificate files and publish them to "
            "their final destinations (foundata.acmesh.run role)."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate and report drift without writing anything",
    )
    parser.add_argument("manifest", help="root-owned deployment manifest (JSON)")
    args = parser.parse_args(argv)

    manifest_fd = None
    staging_fd = None
    entries = []
    try:
        manifest_fd, manifest = open_locked_manifest(args.manifest)
        validate_manifest(manifest)
        certificate_id = manifest["certificate_id"]
        artifacts = manifest["artifacts"]

        staging_fd = open_staging_dir(manifest["staging_dir"])
        staged = {}
        for artifact in ARTIFACT_KEYS:
            if artifact in artifacts:
                staged[artifact] = read_staging_file(
                    staging_fd, artifacts[artifact]["staging"]
                )
        validate_staged(manifest, staged)

        # Deterministic publish order with the completion artifact last: the
        # acmesh-reload-* path unit watching it only fires once every other
        # artifact has been published.
        completion = manifest["completion_artifact"]
        order = [
            artifact
            for artifact in ARTIFACT_KEYS
            if artifact in artifacts and artifact != completion
        ] + [completion]

        drift = {}
        for artifact in order:
            entry = examine_destination(artifact, artifacts[artifact])
            entry["state"] = plan_state(entry, staged[artifact])
            entries.append(entry)
            if entry["state"] != "in_sync":
                drift[artifact] = entry["state"]

        if args.check:
            if drift:
                for artifact, state in drift.items():
                    log(
                        "check {0}: {1} drift on {2}".format(
                            certificate_id, state, artifact
                        )
                    )
                return EXIT_DRIFT
            log("check {0}: in sync".format(certificate_id))
            return EXIT_OK

        if not drift:
            log("{0}: already in sync, nothing to do".format(certificate_id))
            return EXIT_OK

        published = []
        try:
            for entry in entries:
                if entry["state"] == "content":
                    write_replacement(entry, staged[entry["artifact"]])
                    published.append(entry)
                    log(
                        "{0}: published {1} to {2}".format(
                            certificate_id,
                            entry["artifact"],
                            entry["spec"]["destination"],
                        )
                    )
                elif entry["state"] == "metadata":
                    apply_metadata(entry)
                    log(
                        "{0}: reconciled ownership/mode of {1}".format(
                            certificate_id, entry["spec"]["destination"]
                        )
                    )
        except OSError as exc:
            log("{0}: publishing failed: {1}".format(certificate_id, exc))
            rollback(published)
            raise DeployError(
                EXIT_PUBLISH,
                "incomplete deployment of {0}, previous state restored as far "
                "as possible".format(certificate_id),
            ) from exc

        log("{0}: deployment complete".format(certificate_id))
        return EXIT_OK
    except DeployError as exc:
        log(str(exc))
        return exc.code
    except Exception as exc:  # pylint: disable=broad-except
        log("unexpected error: {0!r}".format(exc))
        return EXIT_ERROR
    finally:
        for entry in entries:
            try:
                os.close(entry["dir_fd"])
            except OSError:
                pass
        if staging_fd is not None:
            try:
                os.close(staging_fd)
            except OSError:
                pass
        if manifest_fd is not None:
            try:
                os.close(manifest_fd)
            except OSError:
                pass


if __name__ == "__main__":
    sys.exit(main())
