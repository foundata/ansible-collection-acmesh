# Ansible collection: `foundata.acmesh`

This repository contains the `foundata.acmesh` Ansible Collection.

It provides resources to manage and use [acme.sh](https://acme.sh/), as shell-based [Automatic Certificate Management Environment (ACME)](https://en.wikipedia.org/wiki/Automatic_Certificate_Management_Environment) client. It allows the issuance and maintenance of X.509 certificates, commonly used for securing HTTPS/TLS/SSL services on web servers.


<div align="center" id="project-readme-header">
<br>
<br>

**⭐ Found this useful? Support open-source and star this project:**

[![GitHub repository](https://img.shields.io/github/stars/foundata/ansible-collection-acmesh.svg)](https://github.com/foundata/ansible-collection-acmesh)

<br>
</div>



## Table of contents<a id="toc"></a>

- [Included content](#content)
- [Dependencies](#dependencies)
- [Licensing, copyright](#licensing-copyright)
- [Author information](#author-information)



## Included content<a id="content"></a>

### Role: `foundata.acmesh.run`

The primary role in this collection for issuing and managing certificates. [Its `README.md`](./roles/run/README.md) covers configuration, usage examples, and more:

<!-- ANSIBLE DOCSMITH TOC-FULL run START -->
- [Ansible role: `foundata.acmesh.run`](roles/run/README.md#ansible-role-foundataacmeshrun)
  - [Table of contents](roles/run/README.md#toc)
  - [Features](roles/run/README.md#features)
  - [Example playbooks, using this role](roles/run/README.md#examples)
    - [Webroot challenge (single domain)](roles/run/README.md#examples-webroot)
    - [DNS challenge (multiple domains and certificates)](roles/run/README.md#examples-dns)
    - [Certificate file access for other services](roles/run/README.md#examples-cert-access)
    - [Service reloads after certificate changes (reloadcmd)](roles/run/README.md#examples-reload-permissions)
    - [dns-persist-01 challenge (long-lived TXT record)](roles/run/README.md#examples-dns-persist)
    - [Removing certificates](roles/run/README.md#examples-remove)
    - [Uninstall](roles/run/README.md#examples-uninstall)
    - [Pre-seeding certificate files](roles/run/README.md#examples-preseed)
  - [Supported tags](roles/run/README.md#tags)
  - [Role variables](roles/run/README.md#variables)
    - [`run_acmesh_state`](roles/run/README.md#variable-run_acmesh_state)
    - [`run_acmesh_autoupgrade`](roles/run/README.md#variable-run_acmesh_autoupgrade)
    - [`run_acmesh_autorenewal`](roles/run/README.md#variable-run_acmesh_autorenewal)
    - [`run_acmesh_environment`](roles/run/README.md#variable-run_acmesh_environment)
    - [`run_acmesh_git_url`](roles/run/README.md#variable-run_acmesh_git_url)
    - [`run_acmesh_git_fallback_version_branch`](roles/run/README.md#variable-run_acmesh_git_fallback_version_branch)
    - [`run_acmesh_git_version`](roles/run/README.md#variable-run_acmesh_git_version)
    - [`run_acmesh_certs`](roles/run/README.md#variable-run_acmesh_certs)
      - [`run_acmesh_certs['domains']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains)
        - [`run_acmesh_certs['domains']['name']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-name)
        - [`run_acmesh_certs['domains']['challenge']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge)
          - [`run_acmesh_certs['domains']['challenge']['type']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-type)
          - [`run_acmesh_certs['domains']['challenge']['dns_provider']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_provider)
          - [`run_acmesh_certs['domains']['challenge']['challenge_alias']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-challenge_alias)
          - [`run_acmesh_certs['domains']['challenge']['domain_alias']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-domain_alias)
          - [`run_acmesh_certs['domains']['challenge']['webroot']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-webroot)
          - [`run_acmesh_certs['domains']['challenge']['httpport']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-httpport)
          - [`run_acmesh_certs['domains']['challenge']['tlsport']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-tlsport)
          - [`run_acmesh_certs['domains']['challenge']['dns_persist_wildcard']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_persist_wildcard)
          - [`run_acmesh_certs['domains']['challenge']['dns_persist_ca_name']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_persist_ca_name)
          - [`run_acmesh_certs['domains']['challenge']['dns_persist_days']`](roles/run/README.md#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_persist_days)
      - [`run_acmesh_certs['install']`](roles/run/README.md#variable-run_acmesh_certs-sub-install)
        - [`run_acmesh_certs['install']['ca_file']`](roles/run/README.md#variable-run_acmesh_certs-sub-install-sub-ca_file)
        - [`run_acmesh_certs['install']['cert_file']`](roles/run/README.md#variable-run_acmesh_certs-sub-install-sub-cert_file)
        - [`run_acmesh_certs['install']['fullchain_file']`](roles/run/README.md#variable-run_acmesh_certs-sub-install-sub-fullchain_file)
        - [`run_acmesh_certs['install']['fullcain_file']`](roles/run/README.md#variable-run_acmesh_certs-sub-install-sub-fullcain_file)
        - [`run_acmesh_certs['install']['key_file']`](roles/run/README.md#variable-run_acmesh_certs-sub-install-sub-key_file)
        - [`run_acmesh_certs['install']['reloadcmd']`](roles/run/README.md#variable-run_acmesh_certs-sub-install-sub-reloadcmd)
      - [`run_acmesh_certs['server']`](roles/run/README.md#variable-run_acmesh_certs-sub-server)
      - [`run_acmesh_certs['force']`](roles/run/README.md#variable-run_acmesh_certs-sub-force)
      - [`run_acmesh_certs['debug']`](roles/run/README.md#variable-run_acmesh_certs-sub-debug)
      - [`run_acmesh_certs['dnssleep']`](roles/run/README.md#variable-run_acmesh_certs-sub-dnssleep)
      - [`run_acmesh_certs['pre_hook']`](roles/run/README.md#variable-run_acmesh_certs-sub-pre_hook)
      - [`run_acmesh_certs['post_hook']`](roles/run/README.md#variable-run_acmesh_certs-sub-post_hook)
      - [`run_acmesh_certs['renew_hook']`](roles/run/README.md#variable-run_acmesh_certs-sub-renew_hook)
      - [`run_acmesh_certs['extra_flags']`](roles/run/README.md#variable-run_acmesh_certs-sub-extra_flags)
      - [`run_acmesh_certs['environment']`](roles/run/README.md#variable-run_acmesh_certs-sub-environment)
      - [`run_acmesh_certs['state']`](roles/run/README.md#variable-run_acmesh_certs-sub-state)
    - [`run_acmesh_certs_delete_unmanaged`](roles/run/README.md#variable-run_acmesh_certs_delete_unmanaged)
    - [`run_acmesh_user`](roles/run/README.md#variable-run_acmesh_user)
    - [`run_acmesh_group`](roles/run/README.md#variable-run_acmesh_group)
    - [`run_acmesh_cfg_accountemail`](roles/run/README.md#variable-run_acmesh_cfg_accountemail)
    - [`run_acmesh_cfg_home`](roles/run/README.md#variable-run_acmesh_cfg_home)
    - [`run_acmesh_cfg_config_home`](roles/run/README.md#variable-run_acmesh_cfg_config_home)
    - [`run_acmesh_cfg_cert_home`](roles/run/README.md#variable-run_acmesh_cfg_cert_home)
    - [`run_acmesh_cfg_logfile`](roles/run/README.md#variable-run_acmesh_cfg_logfile)
    - [`run_acmesh_cfg_log_level`](roles/run/README.md#variable-run_acmesh_cfg_log_level)
    - [`run_acmesh_cfg_syslog`](roles/run/README.md#variable-run_acmesh_cfg_syslog)
    - [`run_acmesh_cfg_ca_bundle`](roles/run/README.md#variable-run_acmesh_cfg_ca_bundle)
    - [`run_acmesh_cfg_ca_path`](roles/run/README.md#variable-run_acmesh_cfg_ca_path)
    - [`run_acmesh_cfg_account_keys`](roles/run/README.md#variable-run_acmesh_cfg_account_keys)
      - [`run_acmesh_cfg_account_keys['server']`](roles/run/README.md#variable-run_acmesh_cfg_account_keys-sub-server)
      - [`run_acmesh_cfg_account_keys['account_key']`](roles/run/README.md#variable-run_acmesh_cfg_account_keys-sub-account_key)
    - [`run_acmesh_dns_persist_pause`](roles/run/README.md#variable-run_acmesh_dns_persist_pause)
  - [Dependencies](roles/run/README.md#dependencies)
  - [Compatibility](roles/run/README.md#compatibility)
  - [External requirements](roles/run/README.md#requirements)
<!-- ANSIBLE DOCSMITH TOC-FULL run END -->



## Dependencies<a id="dependencies"></a>

See `dependencies` in [`galaxy.yml`](./galaxy.yml).



## Licensing, copyright<a id="licensing-copyright"></a>

<!--REUSE-IgnoreStart-->
Copyright (c) 2025, 2026 [foundata GmbH](https://foundata.com/) (https://foundata.com)

This project is licensed under the GNU General Public License v3.0 or later (SPDX-License-Identifier: `GPL-3.0-or-later`), see [`LICENSES/GPL-3.0-or-later.txt`](LICENSES/GPL-3.0-or-later.txt) for the full text.

The [`REUSE.toml`](REUSE.toml) file provides detailed licensing and copyright information in a human- and machine-readable format. This includes parts that may be subject to different licensing or usage terms, such as third-party components. The repository conforms to the [REUSE specification](https://reuse.software/spec/). You can use [`reuse spdx`](https://reuse.readthedocs.io/en/latest/readme.html#cli) to create a [SPDX software bill of materials (SBOM)](https://en.wikipedia.org/wiki/Software_Package_Data_Exchange).
<!--REUSE-IgnoreEnd-->

[![REUSE status](https://api.reuse.software/badge/github.com/foundata/ansible-collection-acmesh)](https://api.reuse.software/info/github.com/foundata/ansible-collection-acmesh)



## Author information<a id="author-information"></a>

This [project](https://foundata.com/en/projects/) was created and is maintained by [foundata](https://foundata.com/).

Initially based on an [Ansible skeleton](https://foundata.com/en/projects/ansible-skeletons/) developed by [foundata](https://foundata.com/).
