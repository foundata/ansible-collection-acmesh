================================================
foundata.acmesh Ansible collection Release Notes
================================================

.. contents:: Topics

v1.2.0
======

Release Summary
---------------

Release Date: 2025-11-02

Maintenance release.

Minor Changes
-------------

- Added a new fact ``__run_acmesh_is_installed`` to indicate whether acme.sh is installed as boolean.
- Molecule: Added Debian 13 (Trixie) as a test target platform.
- ``foundata.acmesh.run`` - Added Molecule verification tests to ensure hook configuration updates work correctly and validate the proper base64 encoding of hook commands in certificate config files.
- ``foundata.acmesh.run`` - Added automatic hook and reload command configuration updates for existing certificates. The role now detects when hook configurations (pre_hook, post_hook, renew_hook, reloadcmd) have changed in Ansible variables and automatically updates the corresponding base64-encoded values in acme.sh certificate config files without requiring certificate re-issuance. This is a workaround for upstream issue https://github.com/acmesh-official/acme.sh/issues/3936.
- ``foundata.acmesh.run``: Added Debian 13 (Trixie) as a supported platform.

Removed Features (previously deprecated)
----------------------------------------

- Molecule: Removed Debian 11 (Bullseye) as a test target platform.
- ``foundata.acmesh.run``: Removed Debian 11 (Bullseye) from the list of supported platforms. The role will continue to work on Debian 11 but will display a warning. To avoid this, either remain on or pin the previous version of the collection. Bugs and issues related to Debian 11 will no longer be fixed.

Bugfixes
--------

- Fixed `broken conditionals <https://docs.ansible.com/ansible/latest/porting_guides/porting_guide_core_2.19.html#broken-conditionals>`_. Ansible Core 2.19 / Ansible 12 introduced stricter behavior, e.g. non-boolean expressions in ``when:`` now raise errors by default.

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
