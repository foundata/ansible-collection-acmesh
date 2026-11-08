# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Execute acme.sh with environment data received through module stdin.

The role starts this helper after setpriv, as the service user. Secrets never
enter the SSH command or this helper's arguments. No credential file is created;
acme.sh's DNS plugins retain responsibility for renewal persistence.
"""

import json
import os
import re
import sys

MAX_INPUT = 1024 * 1024
INPUT_ERROR = 64  # acme.sh uses 2 for skipped issuance; helper errors must fail.


def read_environment(stream):
    """Validate input without exposing its contents in error messages."""
    data = stream.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT:
        raise ValueError
    values = json.loads(data)
    if not isinstance(values, dict):
        raise ValueError
    environment = {}
    for key, value in values.items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError
        if isinstance(value, (dict, list)):
            raise ValueError
        # Match Ansible's environment coercion for scalar YAML values.
        value = str(value)
        if "\0" in value:
            raise ValueError
        environment[key] = value
    return environment


def main():
    if len(sys.argv) < 2:
        print("acmesh-run: missing command", file=sys.stderr)
        return INPUT_ERROR
    try:
        environment = os.environ.copy()
        environment.update(read_environment(sys.stdin.buffer))
    except (ValueError, OSError, UnicodeError):
        print("acmesh-run: invalid environment input", file=sys.stderr)
        return INPUT_ERROR
    try:
        # The child must never receive the credential payload on stdin.
        with open(os.devnull, "rb") as empty:
            os.dup2(empty.fileno(), 0)
        os.execvpe(sys.argv[1], sys.argv[1:], environment)
    except OSError:
        print("acmesh-run: cannot execute command", file=sys.stderr)
        return 127


if __name__ == "__main__":
    sys.exit(main())
