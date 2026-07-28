#!/bin/sh
# Checks a captured Molecule / Ansible log for the canary credential planted
# in the converge fixtures (see tasks/converge/role-run.yml, CANARY_LEAK_TEST).
#
# The per-certificate "environment" mapping holds DNS API credentials. Task
# callbacks (normal, --diff and -vvv output) run on the controller, so no
# in-scenario assertion can observe them - this check works on the captured
# log instead. Usage:
#
#   ANSIBLE_VERBOSITY=3 ANSIBLE_DIFF_ALWAYS=true molecule test > molecule.log 2>&1
#   extensions/molecule/check-no-secret-leaks.sh molecule.log
#
# The check is only meaningful for credential-bearing runs (TEST_ACMESH_*
# environment variables set): without them the certificate fixtures are
# inert and the canary never enters the play.

set -u

LOG="${1:?Usage: $0 <molecule-log-file>}"
CANARY="molecule-canary-cred-do-not-print-1f9e"

if [ ! -r "${LOG}" ]; then
    printf 'ERROR: cannot read log file "%s"\n' "${LOG}" >&2
    exit 2
fi

if grep -q -- "${CANARY}" "${LOG}"; then
    printf 'FAIL: the canary credential appears in "%s":\n' "${LOG}" >&2
    grep -n -- "${CANARY}" "${LOG}" | head -n 20 >&2
    exit 1
fi

printf 'OK: no canary credential in "%s".\n' "${LOG}"
printf 'Note: only meaningful for credential-bearing runs at -vvv with --diff.\n'
exit 0
