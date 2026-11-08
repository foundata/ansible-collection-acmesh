# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise real SSH logging against a disposable, prepared Molecule target.

The target must already have passed default prepare/converge. Use an isolated
collection installation. Logs stay private; secret input files are always
removed. A failed scan reports filenames only, never matching content.
"""

import argparse
import base64
import json
import os
import secrets
import subprocess
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "extensions/molecule/credentials"


def markers(values):
    """Recognize plaintext/escaped tokens and base64 at all byte alignments."""
    result = set()
    for value in values:
        # The random ASCII core survives shell, JSON and URL escaping. Checking
        # it also catches partially printed values, without relying on suffixes.
        core = value.split(" ", 1)[0].encode()
        result.add(core)
        for offset in range(3):
            encoded = base64.b64encode(b"x" * offset + core)
            # Drop groups affected by prefix/suffix bytes in a larger payload.
            result.add(encoded[4:-4])
    return result


def scan(paths, needles):
    leaking = []
    for path in paths:
        content = path.read_bytes()
        if any(needle in content for needle in needles):
            leaking.append(path.name)
    return leaking


def execute(playbook, inventory, variables, directory, verbosity, pipelining):
    directory.mkdir(mode=0o700)
    variables = {
        **variables,
        "transport_remote_tmp": f"/var/tmp/acmesh-transport-{variables['transport_domain']}",
    }
    inputs = directory / "inputs.json"
    output = directory / "console.log"
    log = directory / "ansible.log"
    inputs.write_text(json.dumps(variables), encoding="utf-8")
    inputs.chmod(0o600)
    command = [
        "ansible-playbook",
        "-i",
        inventory,
        str(FIXTURES / playbook),
        "--extra-vars",
        f"@{inputs}",
        "--diff",
    ]
    if verbosity:
        command.append("-" + "v" * verbosity)
    env = {
        **os.environ,
        "ANSIBLE_DEBUG": "false",
        "ANSIBLE_VERBOSITY": str(verbosity),
        "ANSIBLE_PIPELINING": str(pipelining).lower(),
        "ANSIBLE_LOG_PATH": str(log),
        "ANSIBLE_DISPLAY_ARGS_TO_STDOUT": "true",
        "ANSIBLE_REMOTE_TEMP": variables["transport_remote_tmp"],
        "ANSIBLE_KEEP_REMOTE_FILES": "false",
    }
    try:
        with output.open("wb") as stream:
            completed = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=stream,
                stderr=subprocess.STDOUT,
                env=env,
                timeout=1800,
                check=False,
            )
        return completed.returncode, [output, log]
    finally:
        inputs.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True)
    parser.add_argument(
        "--work-dir", required=True, type=Path, help="New private directory"
    )
    parser.add_argument("--verbosity", type=int, choices=(0, 1, 3, 4), action="append")
    parser.add_argument("--pipelining", choices=("on", "off"), action="append")
    args = parser.parse_args()
    os.umask(0o077)
    args.work_dir.mkdir(mode=0o700)
    all_needles = set()
    run_id = secrets.token_hex(4)
    for verbosity in args.verbosity or (0, 1, 3, 4):
        for pipeline in args.pipelining or ("off", "on"):
            name = f"v{verbosity}-{pipeline}"
            domain = f"transport-{run_id}-{name}.test"
            values = {
                key: f"ACMECANARY{secrets.token_hex(24)} ' \" \\ $HOME\nü"
                for key in ("token", "global", "overridden")
            }
            all_needles.update(markers(values.values()))
            status, logs = execute(
                "verify.yml",
                args.inventory,
                {"transport_domain": domain, "transport_secrets": values},
                args.work_dir / name,
                verbosity,
                pipeline == "on",
            )
            leaks = scan(logs, all_needles)
            print(f"{name}: exit={status}, leaking logs={leaks}", flush=True)
            if status or leaks:
                return 1
            # A separate process receives no secrets: renewal must use the DNS
            # provider's native persistence. Remove this certificate afterwards
            # so subsequent cases cannot reuse another case's saved credentials.
            status, logs = execute(
                "renewal.yml",
                args.inventory,
                {"transport_domain": domain},
                args.work_dir / f"{name}-renewal",
                verbosity,
                pipeline == "on",
            )
            leaks = scan(logs, all_needles)
            print(f"{name} renewal: exit={status}, leaking logs={leaks}", flush=True)
            if status or leaks:
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
