================================================
foundata.acmesh Ansible collection Release Notes
================================================

.. contents:: Topics

v3.0.0
======

Release Summary
---------------

Release Date: 2026-07-30

Maintenance and feature release.

This release includes a *potentially* breaking change and therefore requires
a major version bump according to Semantic Versioning. Most installations are
expected to continue working without modification, but setups that rely on
root privileges during certificate issuance may require adjustments and fix
their permissions, e.g. to allow the acmesh service user to write into an
installation target.

Huge improvment: No more sudo or Polkit adjustment for reload cmds: The
per-certificate ``reloadcmd`` is no longer executed by ``acme.sh`` but by a
root-side systemd path unit (``acmesh-reload-<primary domain>.path``) watching
the installed certificate files.

The change aligns certificate issuance with automated renewal by running both
under the same unprivileged service user. This makes permission-related issues
visible during the Ansible run rather than weeks later during the first renewal.

See the following and the updated role README.md for details.

Minor Changes
-------------

- The Molecule ``default`` scenario now selects the test backend per platform via a ``type`` key: ``podman`` (container, the default when omitted) or ``libvirt`` (QEMU/KVM virtual machine from a vendor cloud image via a session libvirt daemon, without root privileges). VM platforms allow tests containers cannot cover; commented ``libvirt`` alternates for every platform are included in ``molecule.yml``. ``molecule login`` now works through a per-instance login command for both backends. See ``extensions/molecule/README.md`` for requirements and usage.
- ``run`` role - Certificates can now be removed declaratively. A ``run_acmesh_certs`` entry with ``state: absent`` removes all data of that certificate: the ``acme.sh`` data below ``run_acmesh_cfg_cert_home`` (which also stops its automated renewal), its ``acmesh-reload-*`` systemd units and the installed certificate files (their directories are kept, as they may be shared with other software; the certificate is not revoked at the ACME CA).
- ``run`` role - New ``run_acmesh_certs_delete_unmanaged`` option (default: ``false``). When enabled, certificate data below ``run_acmesh_cfg_cert_home`` that does not belong to any certificate listed in ``run_acmesh_certs`` gets removed (stopping its automated renewal), as do ``acmesh-reload-*`` units the current configuration does not define. Installed certificate files of unmanaged certificates are never touched, and nothing is removed while ``run_acmesh_certs`` is undefined. A full uninstall via ``run_acmesh_state: absent`` still preserves all certificate data.

Breaking Changes / Porting Guide
--------------------------------

- ``run`` role - All ``acme.sh`` operations during the Ansible run (account registration, certificate issuance and installation) now run as the unprivileged service user defined by ``run_acmesh_user`` instead of ``root``, matching the automated renewal (``acmesh-renewal.service``). Issuance and renewal now behave identically, so permission problems surface during the Ansible run instead of weeks later at the first renewal. Migration notes: with the ``webroot`` challenge, the service user now needs write access to the configured webroot directory (``acme.sh`` creates ``.well-known/acme-challenge`` below it); the ``pre_hook``, ``post_hook`` and ``renew_hook`` commands now also run as the service user during issuance (previously only during renewal) and must not require root privileges - use ``reloadcmd`` for service reloads, which runs as root. Certificates using the ``standalone`` or ``alpn`` challenge on a privileged port (below 1024) automatically get ``CAP_NET_BIND_SERVICE`` granted for issuance (via ``setpriv`` ambient capabilities), exactly as the renewal service unit already does.
- ``run`` role - The per-certificate ``reloadcmd`` is no longer executed by ``acme.sh`` but by a root-side systemd path unit (``acmesh-reload-<primary domain>.path``) watching the installed certificate files. Previously, the command ran as ``root`` only during the initial issuance and as the unprivileged service user during automated renewal, where privileged commands failed silently (``acme.sh`` tolerates reload errors during ``--cron``), leaving services on the old certificate. Now the command always runs as ``root`` whenever the installed files change, and a failing reload leaves the companion service unit in a failed state visible via ``systemctl --failed``. Migration notes: plain commands like ``systemctl reload nginx.service`` now work as-is; ``sudo -n`` prefixes are no longer needed (they keep working but should be removed along with the related sudoers rules). A certificate defining ``reloadcmd`` must now also define at least one install file path (``fullchain_file``, ``key_file``, ``ca_file`` or ``cert_file``), otherwise the role fails early. The reload happens asynchronously (typically within milliseconds) after the files were written, no longer synchronously within ``acme.sh``. Any ``Le_ReloadCmd`` stored in the ``acme.sh`` certificate configuration (by earlier versions of this role or manual runs) gets cleared.

Security Fixes
--------------

- ``run`` role - The certificate settings shown at ``-vvv`` verbosity no longer include each certificate's ``environment`` mapping, which holds DNS provider API credentials. The debug output now uses the credential-free views of the certificate list.
- ``run`` role - ``run_acmesh_cfg_account_keys[].account_key`` is now marked ``no_log`` in the argument specification, so a failing argument validation can no longer expose the PEM-encoded account private key.

Bugfixes
--------

- ``run`` role - Certificate identities are validated early now: ``run_acmesh_certs[]['domains']`` and each domain's ``name`` are required and must be non-empty, primary domains must be unique and must stay unique after unit-name normalization (lowercase, every character outside ``a-z0-9.-`` becomes ``-``). Such entries previously failed midway with an unhelpful templating error, were silently skipped by the ``state: absent`` cleanup, or collided in the shared ``acme.sh`` storage directory and ``acmesh-reload-*`` unit names (last writer wins).
- ``run`` role - Platform-specific task files are now guaranteed to run before the shared default tasks. The former single include loop did not preserve that order with several platforms in one play: Ansible batches the includes across hosts and the insertion order depends on when results arrive (non-deterministic), so default tasks could run before platform-specific ones. The includes are now two sequential tasks, which is a hard ordering barrier.

v2.0.2
======

Release Summary
---------------

Release Date: 2026-07-24

Bugfix release.

Minor Changes
-------------

- ``run`` role - The ``run_acmesh_user`` documentation now states that it must be a dedicated account fully owned by the role and that, when user management is enabled, the role fully manages and removes it regardless of who created it.

Security Fixes
--------------

- ``run`` role - DNS API credentials passed through ``run_acmesh_environment`` and the per-certificate ``environment`` mapping could appear in task output. The certificate issue and install tasks set them as the task environment and also carried the per-certificate values in their loop items, so a normal run (and especially ``--diff`` or a task failure) printed them. Both tasks are now ``no_log``, both variables are marked ``no_log`` in the argument specification, and the remaining tasks that iterate over the certificates but do not need the credentials loop over a credential-free view of the list. Note that a ``-vvv`` run still exposes the environment in the connection plugin's ``EXEC`` line; this is an Ansible limitation that ``no_log`` does not cover.
- ``run`` role - The role now refuses to run when ``run_acmesh_user`` resolves to ``root``, a UID 0 account, or the account Ansible connects with. The role fully owns that account: installation rewrites its password, shell, home directory and supplementary groups, and ``run_acmesh_state: absent`` deletes it together with its home directory. Because the role does not track whether it originally created the account, pointing ``run_acmesh_user`` at a shared, pre-existing or privileged account could previously damage or delete it. The guard runs in the always-included init tasks, so it protects both the install and the uninstall path.

Bugfixes
--------

- The comment written into neutralized distribution config files contained a stray double quote in the Debian hint (``dpkg -S '<file>'"``), so the suggested command could not be copied and pasted as-is. The quote is removed.
- ``run`` role - Automatic renewal of certificates issued with the ``standalone`` (HTTP-01) or ``alpn`` (TLS-ALPN-01) challenge failed because ``acmesh-renewal.service`` runs unprivileged (as ``run_acmesh_user``) and acme.sh could not bind the privileged port (80 or 443) it opens for those challenges. The renewal service now gets ``AmbientCapabilities=CAP_NET_BIND_SERVICE`` when, and only when, a configured certificate uses ``standalone`` or ``alpn`` on a privileged port (below 1024). Certificates using ``dns``, ``dns_persist`` or ``webroot`` (or ``standalone`` / ``alpn`` pinned to a high port) get a renewal service without any extra capability. Thanks to @Menchen13 for reporting this and presenting a proposed solution.
- ``run`` role - The documented ``reloadcmd`` values and the suggested sudoers rule did not work together: a sudoers rule is only applied when the command actually invokes ``sudo``, so the plain ``systemctl reload ...`` examples were denied during automated renewal (which runs as the unprivileged service user) while ``acme.sh`` tolerates such reload errors, silently leaving services on the old certificate. All ``reloadcmd`` examples now invoke ``sudo -n`` with absolute command paths, the sudoers examples use the matching ``/usr/bin/systemctl`` paths, and the README gained a dedicated "Reload permissions" section covering ``sudo`` (``community.general.sudoers`` or ``foundata.linux.sudo``) as well as a polkit rule as an alternative for plain ``systemctl`` commands.

v2.0.1
======

Release Summary
---------------

Release Date: 2026-06-01

Bugfix release (kind of).

Minor Changes
-------------

- ``foundata.acmesh.run`` - Handle deprecated ``fullcain_file`` alias gracefully. The deprecated ``run_acmesh_certs[]['install']['fullcain_file']`` typo alias now emits a timed warning instead of failing immediately, then normalizes the value to ``fullchain_file`` and removes the deprecated key before later tasks run. Please update your playbooks accordingly by replacing all occurrences of ``fullcain_file`` with ``fullchain_file``.

v2.0.0
======

Release Summary
---------------

Release Date: 2026-05-21

Feature and bugfix release.

Major Changes
-------------

- ``foundata.acmesh.run`` - Added support for the ``dns-persist-01`` ACME challenge type (https://github.com/foundata/ansible-collection-acmesh/issues/17). This challenge uses a static TXT record at ``_validation-persist.<domain>`` bound to the ACME account key, eliminating the need for DNS API credentials during certificate issuance and renewal. New challenge sub-options: ``dns_persist_wildcard``, ``dns_persist_ca_name``, and ``dns_persist_days``. New parameters: ``run_acmesh_cfg_account_keys``, and ``run_acmesh_dns_persist_pause``. The ACME registration metadata (account.json) may get automatically regenerated by ``acme.sh --register-account`` using the seeded account key (per RFC 8555 7.3.1, the CA identifies accounts by their public key) if needed. Please note that you might need to set ``run_acmesh_git_version: "master"`` since acme.sh 3.1.4 is not yet released as of 2026-05-21 and earlier versions lack support for ``dns-persist-01``.
- ``foundata.acmesh.run`` - The role now automatically registers ACME accounts, generates dns-persist TXT record values via ``acme.sh --make-dns-persist-value``, and displays human-readable instructions for DNS record publication when certificates use the ``dns_persist`` challenge type.

Minor Changes
-------------

- ``foundata.acmesh.run`` - Added ``run_acmesh_cfg_ca_bundle`` and ``run_acmesh_cfg_ca_path`` parameters to specify a custom CA certificate bundle or directory for all acme.sh HTTPS requests (issue, register-account). This is needed when the ACME server uses a non-standard CA. These are global acme.sh settings, matching the upstream behavior where ``CA_BUNDLE`` / ``CA_PATH`` are persisted to ``account.conf``. Until now, one had to use ``run_acmesh_certs['extra_flags']`` for this. As these settings are quite common,	role level variables make sense.
- ``foundata.acmesh.run`` - Added ``run_acmesh_git_version`` parameter to override the automatically detected acme.sh version with a specific Git ref (tag, branch, or commit hash). Setting it to ``master`` installs the latest code, which is usually safe as acme.sh aims for a production-ready ``master`` branch by default. This may be needed for features not yet included in a tagged release (example as of 2026-05-19: ``--make-dns-persist-value`` for dns-persist-01 support which is in `master` but not in the latest tagged version 3.1.3) or when you want to pin a specific version for reproducibility.

Breaking Changes / Porting Guide
--------------------------------

- ``foundata.acmesh.run`` - Renamed the ``run_acmesh_certs[]['install']\`` sub-key ``fullcain_file`` to ``fullchain_file`` (typo fix, "cain" instead of "chain"). Update your playbooks and inventory accordingly by replacing all occurrences of ``fullcain_file`` with ``fullchain_file``.

v1.6.1
======

Release Summary
---------------

Release Date: 2026-05-12

Bugfix release.

Bugfixes
--------

- ``foundata.acmesh.run`` - Fixed ``acmesh-renewal.timer`` not being started after installation. The systemd timer was only enabled (scheduled for future boots) but never started, so automatic certificate renewal would not begin until the next reboot. The timer is now started immediately when enabled and stopped when disabled or uninstalled (`#16 <https://github.com/foundata/ansible-collection-acmesh/issues/16>`__).

v1.6.0
======

Release Summary
---------------

Release Date: 2026-05-11

Maintenance release.

Minor Changes
-------------

- Added Fedora 44 as supported platform for all collection roles and Molecule test scenarios.
- Added Ubuntu 26.04 LTS (Resolute Raccoon) as supported platform for all collection roles and Molecule test scenarios.

Removed Features (previously deprecated)
----------------------------------------

- Removed Fedora 42 support (End of Life, EOL) from collection roles and Molecule scenarios. The collection may still work on Fedora 42, but no testing or bugfixes will be provided. A warning will be displayed when used on unsupported platforms.

v1.5.1
======

Release Summary
---------------

Release Date: 2026-05-10

Bugfix release.

Minor Changes
-------------

- Added Molecule tests for webroot (HTTP-01) challenge certificate issuance using `pebble <https://github.com/letsencrypt/pebble>`__ (Let's Encrypt test ACME server). The tests run unconditionally on all platforms (no external credentials required) with a switchable web server backend (nginx or apache, controlled via the ``TEST_ACMESH_WEBROOT_BACKEND`` environment variable, defaulting to nginx).

Bugfixes
--------

- ``foundata.acmesh.run`` - The ``webroot`` challenge parameter was missing from the role's argument spec (``meta/argument_specs.yml``), causing validation failures when using ``type: webroot`` in ``run_acmesh_certs[].domains[].challenge``. The ``domain_alias`` description was also corrected to accurately describe DNS alias mode (see `#15 <https://github.com/foundata/ansible-collection-acmesh/issues/15>`__).

v1.5.0
======

Release Summary
---------------

Release Date: 2026-02-21

Feature and bugfix release.

Minor Changes
-------------

- ``foundata.acmesh.run`` - Added optional per-certificate ``environment`` key in ``run_acmesh_certs`` items. Setting environment variables per certificate can improve readability, as it clearly shows which certificate or domain is using which credentials in setups that involve multiple DNS provider credentials.
  Per-certificate environment variables are merged with the global ``run_acmesh_environment``, with per-certificate values taking precedence on key conflicts.
  Please note that acme.sh DNS API plugins usually persist credentials per provider (not per certificate) in ``account.conf``, so using different credentials for the same DNS provider across certificates will result in only the last-written set being saved for automatic renewals.
- ``foundata.acmesh.run`` - The uninstall tasks now check ``run_acmesh_group`` membership and delete the supplementary group if no other members remain.

Bugfixes
--------

- ``foundata.acmesh.run`` - Fixed handler failure during uninstall by skipping the ownership and permissions handler when ``run_acmesh_cfg_home`` no longer exists.
- ``foundata.acmesh.run`` - Fixed incorrect group ownership on renewed certificate files by setting the SGID bit (``2750``) on certificate directories. Without it, files created by acme.sh during automatic renewal via the systemd timer were owned by the service user's primary group instead of ``run_acmesh_group``, which could not be corrected without an additional Ansible run.

v1.4.0
======

Release Summary
---------------

Release Date: 2026-02-20

Feature release.

Minor Changes
-------------

- Molecule: Added openSUSE Leap 16.0 as a test target platform.
- ``foundata.acmesh.run`` - Added ``run_acmesh_git_fallback_version_branch`` parameter to configure the Git branch used as a fallback when no version tag can be determined from the remote repository.
- ``foundata.acmesh.run`` - Added ``run_acmesh_git_url`` parameter to override the Git repository URL used for cloning acme.sh and querying upstream version tags. This allows pointing the role at an internal Git mirror, making it suitable for air-gapped environments and avoiding GitHub API rate limits.
- ``foundata.acmesh.run`` - Replaced the GitHub API-based version detection with ``git ls-remote --tags --refs``. This approach works with any Git remote and no longer requires access to the GitHub API.
- ``foundata.acmesh.run``: Added openSUSE Leap 16.0 as a supported platform.

Removed Features (previously deprecated)
----------------------------------------

- Molecule: Removed openSUSE Leap 15.6 as a test target platform.
- ``foundata.acmesh.run``: Removed openSUSE Leap 15.6 from the list of supported platforms. The role will continue to work on openSUSE Leap 15.6 but will display a warning. To avoid this, either remain on or pin the previous version of the collection. Bugs and issues related to openSUSE Leap 15.6 will no longer be fixed.

v1.3.0
======

Release Summary
---------------

Release Date: 2025-12-26

Maintenance release.

Minor Changes
-------------

- Added Fedora 43 as supported platform for all collection roles and Molecule test scenarios

Removed Features (previously deprecated)
----------------------------------------

- Removed Fedora 41 support (End of Life, EOL) from collection roles and Molecule scenarios. The collection may still work on Fedora 41, but no testing or bugfixes will be provided. A warning will be displayed when used on unsupported platforms.

v1.2.1
======

Release Summary
---------------

Release Date: 2025-12-03

Bugfix release.

Bugfixes
--------

- Files created by ``Cert | Default | Install certificate(s)`` / ``acme.sh --install-cert`` were ignored by the handler to set ownership and permissions of files and directories (restrict to service user and/or group).

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
