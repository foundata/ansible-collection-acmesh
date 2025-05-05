================================================
foundata.acmesh Ansible collection Release Notes
================================================

.. contents:: Topics

v1.1.0
======

Release Summary
---------------

Release Date: 2025-05-05

Mostly a maintenance release, shipping official Fedora 42 support.

Minor Changes
-------------

- Added Fedora 42 as supported platform for all collection roles and Molecule test scenarios
- Exclude ``extensions/molecule`` from build artifacts. This reduces the size of the resulting artifact. The Ansible Molecule directory is intended for developer testing and not needed in production artifacts, where environment-specific testing can be performed independently.
- Improved inline script quoting. Ensure safer handling of input by adding ``ansible.builtin.quote`` where appropriate. Even if inputs are user-controlled or derived from internal variables, it's better to be safe and prevent potential issues with shell parsing.

Removed Features (previously deprecated)
----------------------------------------

- Removed Fedora 40 support (End of Life, EOL) from collection roles and Molecule scenarios. The collection may still work on Fedora 40, but no testing or bugfixes will be provided. A warning will be displayed when used on unsupported platforms.

v1.0.0
======

Release Summary
---------------

Release Date: 2025-04-17

First public release, providing all functionality and files
