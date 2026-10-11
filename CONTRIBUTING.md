# Contributing

<!--
SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
SPDX-License-Identifier: GPL-3.0-or-later
-->

Thank you for your interest in contributing. Use these channels:

- Open an issue to report a problem or request a feature.
- Submit code through a pull request (PR) or merge request (MR).
- Send an email to the maintainer if you have something to discuss (no support
  requests).

Development takes place on our internal repository hosting platform. You can
report issues and submit changes through any of our public repositories on
platforms such as GitHub, GitLab or Codeberg. We coordinate the work internally
and follow up on the platform where you contributed.

Follow the [code of conduct](./CODE_OF_CONDUCT.md) when participating.

Report vulnerabilities privately as described in [`SECURITY.md`](./SECURITY.md).


## Issues<a id="issues"></a>

If you spot a problem, have an idea or want to request a feature, use the issue
tracker where this project's repository is hosted, such as GitHub, GitLab or
Codeberg. Search the existing issues there before opening a new one.

You only need to report an issue once, on one platform. If you know of a related
issue on another platform, include its full URL so we can connect the reports.

We don't assign issues automatically. Leave a comment if you'd like to work on
an issue or have already started. You can also ask us to assign it to you.

Include the collection and Ansible versions, the managed system's operating
system and version, and the affected role. Provide a minimal playbook and the
relevant variables, the expected result, and the actual result or error. Remove
credentials and other private data from examples and logs.

For a proposed feature, explain the task you need to accomplish and how the
current behavior limits it.


## Discussions<a id="discussions"></a>

If you have something to discuss or comment about the project, feel free to send
an email to Andreas Haerter <ah@foundata.com> (no support requests, all
resources are provided "as is").


## Submitting changes<a id="submitting-changes"></a>

The following requirements apply to both pull requests and merge requests:

Use [`DEVELOPMENT.md`](./DEVELOPMENT.md) to set up the collection and find its
checks. Keep each change focused, update the affected role documentation, and
include the test results and tested platforms in your submission.

For user-visible changes, add a YAML fragment under
[`changelogs/fragments/`](./changelogs/fragments/) using the
[fragment template](./changelogs/fragments/00-fragment-template.txt). Antsibull
generates [`CHANGELOG.rst`](./CHANGELOG.rst) from these fragments.

Contributions must be compatible with the licensing recorded in
[`REUSE.toml`](./REUSE.toml). Write scoped commit messages following the
[foundata commit guide](https://foundata.com/en/guidelines/git-commits/).

Working on a branch in your own fork lets you make changes without affecting the
original project until we merge them. For help with forks, branches and
submitting changes, use the documentation for the platform hosting the
repository:

| Platform |  Submission type   | Help |
| -------- | ------------------ | ---- |
| GitHub   | Pull request (PR)  | [Quickstart for pull requests](https://docs.github.com/en/pull-requests/get-started/pull-request-quickstart) |
| GitLab   | Merge request (MR) | [Create merge requests](https://docs.gitlab.com/user/project/merge_requests/creating_merge_requests/) |
| Forgejo  | Pull request (PR)  | [Pull requests and Git flow](https://forgejo.org/docs/latest/user/collaboration/pull-requests-and-git-flow/) |
