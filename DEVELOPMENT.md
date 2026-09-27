# Developing foundata.acmesh

This guide is the entry point for changing and testing the `foundata.acmesh`
collection. Role usage and supported platforms are documented in
[`README.md`](./README.md) and the role READMEs under [`roles/`](./roles/).

## Prerequisites

Use an Ansible version matching [`meta/runtime.yml`](./meta/runtime.yml).
Collection dependencies are declared in [`galaxy.yml`](./galaxy.yml).

For integration testing, follow the
[Molecule requirements](./extensions/molecule/README.md#requirements). The
selected platforms determine whether you need Podman or a libvirt/QEMU
environment. The execution-environment scenario has additional requirements
documented there.

## Getting started

Clone a repository listed on the
[source page](https://foundata.com/en/projects/ansible-collection-acmesh/#source);
the commands below use GitHub as an example. Work from the repository root:

```sh
git clone https://github.com/foundata/ansible-collection-acmesh.git
cd ansible-collection-acmesh
```

Read the affected role's README before changing its tasks, defaults, or argument
specifications. The [Molecule guide](./extensions/molecule/README.md) covers
test environment setup and how to add verification tasks.

## Testing

After setting up the required test tools, run the collection's Molecule scenario
from the repository root:

```sh
export MOLECULE_GLOB="./{extensions/molecule,molecule}/*/molecule.yml"
molecule test
```

Review the platform selection in
[`extensions/molecule/default/molecule.yml`](./extensions/molecule/default/molecule.yml)
before running tests. Use the
[testing instructions](./extensions/molecule/README.md#usage-testing) for
individual platforms, the execution-environment scenario, and retaining
instances for debugging. Tests create and remove containers or virtual machines.

Check changed Markdown files with the repository's
[rumdl configuration](./.rumdl.toml). For the contributor documents:

```sh
rumdl fmt --config .rumdl.toml --deny-config-warnings CONTRIBUTING.md DEVELOPMENT.md SECURITY.md
rumdl check --config .rumdl.toml --deny-config-warnings CONTRIBUTING.md DEVELOPMENT.md SECURITY.md
git diff --check
```

## Changelog and releases

Write user-visible changes as YAML fragments under
[`changelogs/fragments/`](./changelogs/fragments/). Start from the
[fragment template](./changelogs/fragments/00-fragment-template.txt), keep the
applicable categories, and use reStructuredText in entry text.

Antsibull owns [`CHANGELOG.rst`](./CHANGELOG.rst); its configuration is in
[`changelogs/config.yaml`](./changelogs/config.yaml). Release metadata comes
from [`galaxy.yml`](./galaxy.yml) and [`releasing.toml`](./releasing.toml).

Maintainers use foundata's
[Ansible collection release procedure](https://github.com/foundata/releasing/blob/main/docs/ansible-collections.md).
It covers release preparation, building from the committed revision, publication
to Ansible Galaxy, and verification. Publishing requires the maintainer's Galaxy
and GitHub credentials.

## Troubleshooting

See the [Molecule troubleshooting guide](./extensions/molecule/README.md#faq)
for role-path detection, air-gapped environments, container limits, and VM
networking.
