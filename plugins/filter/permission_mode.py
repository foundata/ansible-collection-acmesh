# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Normalize deterministic permission assignments for deployment manifests."""

from __future__ import annotations

import re

from ansible.errors import AnsibleFilterError

DOCUMENTATION = r"""
name: permission_mode
short_description: Normalize complete permission assignments to octal
version_added: "4.2.0"
description:
  - Convert a quoted octal mode or complete symbolic assignments to four octal digits.
  - Symbolic modes must explicitly assign all of C(u), C(g) and C(o), or C(a).
  - Relative operations, conditional execute and copied permissions are rejected.
  - This normalizes syntax only. The role and deploy helper enforce certificate safety limits.
options:
  _input:
    description: Quoted octal mode or complete symbolic assignments.
    type: str
    required: true
author:
  - foundata GmbH (@foundata)
"""

EXAMPLES = r"""
# Both expressions return "0640".
mode: "{{ 'u=rw,g=r,o=' | foundata.acmesh.permission_mode }}"
legacy_mode: "{{ '640' | foundata.acmesh.permission_mode }}"
"""

RETURN = r"""
_value:
  description: Normalized four-digit octal mode.
  type: str
"""


def permission_mode(value: str) -> str:
    """Return a mode independent of the previous permissions and the umask."""
    # Coercion lets Ansible/Jinja propagate undefined values before validation.
    text = str(value)
    if not isinstance(value, str):
        raise AnsibleFilterError("Permission modes must be strings")
    if re.fullmatch(r"[0-7]{3,4}", text):
        return format(int(text, 8), "04o")
    assigned = set()
    mode = 0
    for clause in text.split(","):
        match = re.fullmatch(r"([ugoa]+)=([rwxst]*)", clause)
        if not match:
            raise AnsibleFilterError(
                "Use quoted octal or complete symbolic assignments"
            )
        who, permissions = match.groups()
        classes = set("ugo" if "a" in who else who)
        if ("s" in permissions and "o" in classes) or (
            "t" in permissions and classes != {"o"}
        ):
            raise AnsibleFilterError(
                "Special permission bits require explicit u/g or o assignments"
            )
        bits = sum(
            bit
            for letter, bit in (("r", 4), ("w", 2), ("x", 1))
            if letter in permissions
        )
        for identity, shift, special in (
            ("u", 6, 0o4000),
            ("g", 3, 0o2000),
            ("o", 0, 0o1000),
        ):
            if identity in classes:
                mode &= ~((7 << shift) | special)
                mode |= bits << shift
                if (identity in "ug" and "s" in permissions) or (
                    identity == "o" and "t" in permissions
                ):
                    mode |= special
        assigned.update(classes)
    if assigned != set("ugo"):
        raise AnsibleFilterError("Symbolic modes must assign u, g and o explicitly")
    return format(mode, "04o")


class FilterModule:
    """Expose permission normalization to the role."""

    def filters(self) -> dict:
        return {"permission_mode": permission_mode}
