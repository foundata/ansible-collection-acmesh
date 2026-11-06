# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Permission normalization and the deployment manifest's safety boundary."""

import importlib

import pytest
from ansible.errors import AnsibleError, AnsibleFilterError, AnsibleUndefinedVariable
from ansible.plugins.loader import init_plugin_loader
from jinja2 import StrictUndefined, UndefinedError

init_plugin_loader()
PLUGIN = importlib.import_module(
    "ansible_collections.foundata.acmesh.plugins.filter.permission_mode"
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("u=rw,g=r,o=", "0640"),
        ("o=,g=rxs,u=rwx", "2750"),
        ("a=r", "0444"),
        ("a=,u=rw,g=r", "0640"),
        ("ug=r,o=", "0440"),
        ("u=rwxs,g=rxs,o=rxt", "7755"),
        ("640", "0640"),
        ("2750", "2750"),
        ("u=,g=,o=", "0000"),
    ],
)
def test_normalize(value, expected):
    assert PLUGIN.permission_mode(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        640,
        "",
        "u=rw",
        "u+rw,g=r,o=",
        "u=rw,g=r,o=X",
        "u=g,g=r,o=",
        "u=rw,g=r,o=r\n",
        "u=rw,g=r,o=☃",
        "u=rw,g=r,o=s",
        "a=s",
        "u=t,g=,o=",
        "888",
        [],
        {},
    ],
)
def test_invalid_mode(value):
    with pytest.raises(AnsibleFilterError):
        PLUGIN.permission_mode(value)


def test_undefined_propagates():
    with pytest.raises((UndefinedError, AnsibleUndefinedVariable)):
        PLUGIN.permission_mode(StrictUndefined(name="missing"))


def test_ansible_templating():
    from ansible.template import Templar, trust_as_template

    templar = Templar(variables={"mode": "u=rw,g=r,o="})
    assert (
        templar.template(
            trust_as_template("{{ mode | foundata.acmesh.permission_mode }}")
        )
        == "0640"
    )
    for value in [None, "", "u=rw", "u=rw,g=r,o=☃"]:
        templar.available_variables = {"mode": value}
        with pytest.raises(AnsibleError, match=r"(?i)permission|symbolic"):
            templar.template(
                trust_as_template("{{ mode | foundata.acmesh.permission_mode }}")
            )
    with pytest.raises(AnsibleUndefinedVariable):
        templar.template(
            trust_as_template("{{ absent | foundata.acmesh.permission_mode }}")
        )
