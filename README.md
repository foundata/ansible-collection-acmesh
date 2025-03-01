# Ansible collection: `foundata.acmesh`

This repository contains the `foundata.acmesh` Ansible Collection.

It provides resources to manage and use [acme.sh](https://acme.sh/), as shell-based [Automatic Certificate Management Environment (ACME)](https://en.wikipedia.org/wiki/Automatic_Certificate_Management_Environment) client. It allows the issuance and maintenance of X.509 certificates, commonly used for securing HTTPS/TLS/SSL services on web servers.



## Table of contents<a id="toc"></a>

- [Included content](#content)
- [Dependencies](#dependencies)
- [Licensing, copyright](#licensing-copyright)
- [Author information](#author-information)



## Included content<a id="content"></a>

### Role: `foundata.acmesh.run`

The main resource of the collection to issue and manage certificates. See the [role's `README.md`](./roles/run/README.md) for more information and usage examples.



## Dependencies<a id="dependencies"></a>

See `dependencies` in [`galaxy.yml`](./galaxy.yml).



## Licensing, copyright<a id="licensing-copyright"></a>

<!--REUSE-IgnoreStart-->
Copyright (c) 2025 foundata GmbH (https://foundata.com)

This project is licensed under the GNU General Public License v3.0 or later (SPDX-License-Identifier: `GPL-3.0-or-later`), see [`LICENSES/GPL-3.0-or-later.txt`](LICENSES/GPL-3.0-or-later.txt) for the full text.

The [`REUSE.toml`](REUSE.toml) file provides detailed licensing and copyright information in a human- and machine-readable format. This includes parts that may be subject to different licensing or usage terms, such as third-party components. The repository conforms to the [REUSE specification](https://reuse.software/spec/). You can use [`reuse spdx`](https://reuse.readthedocs.io/en/latest/readme.html#cli) to create a [SPDX software bill of materials (SBOM)](https://en.wikipedia.org/wiki/Software_Package_Data_Exchange).
<!--REUSE-IgnoreEnd-->



## Author information<a id="author-information"></a>

This project was created and is maintained by foundata GmbH (https://foundata.com).

The collection was initiated using an [Ansible skeleton](https://github.com/foundata/ansible-skeletons).
