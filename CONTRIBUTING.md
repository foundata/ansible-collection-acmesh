# Contributing

Report problems with `foundata.acmesh` through the
[issue tracker](https://github.com/foundata/ansible-collection-acmesh/issues),
or submit a
[pull request](https://github.com/foundata/ansible-collection-acmesh/pulls) with
a change. Follow the [code of conduct](./CODE_OF_CONDUCT.md) when participating.

Report vulnerabilities privately as described in [`SECURITY.md`](./SECURITY.md).

## Issues

Search existing issues before opening a report. Include the collection and
Ansible versions, the managed system's operating system and version, and the
affected role. Provide a minimal playbook and the relevant variables, the
expected result, and the actual result or error. Remove credentials and other
private data from examples and logs.

For a proposed feature, explain the task you need to accomplish and how the
current behavior limits it.

## Pull requests

Use [`DEVELOPMENT.md`](./DEVELOPMENT.md) to set up the collection and find its
checks. Keep each change focused, update the affected role documentation, and
include the test results and tested platforms in the pull request.

For user-visible changes, add a YAML fragment under
[`changelogs/fragments/`](./changelogs/fragments/) using the
[fragment template](./changelogs/fragments/00-fragment-template.txt). Antsibull
generates [`CHANGELOG.rst`](./CHANGELOG.rst) from these fragments.

Contributions must be compatible with the licensing recorded in
[`REUSE.toml`](./REUSE.toml). Write scoped commit messages following the
[foundata commit guide](https://github.com/foundata/guidelines/blob/main/git-commits.md).
