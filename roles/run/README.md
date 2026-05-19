# Ansible role: `foundata.acmesh.run`

The `foundata.acmesh.run` Ansible role (part of the `foundata.acmesh` Ansible collection). It provides automated management of ACME certificates using acme.sh.



## Table of contents<a id="toc"></a>

- [Features](#features)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)<!-- ANSIBLE DOCSMITH TOC START -->
- [Role variables](#variables)
  - [`run_acmesh_state`](#variable-run_acmesh_state)
  - [`run_acmesh_autoupgrade`](#variable-run_acmesh_autoupgrade)
  - [`run_acmesh_autorenewal`](#variable-run_acmesh_autorenewal)
  - [`run_acmesh_environment`](#variable-run_acmesh_environment)
  - [`run_acmesh_git_url`](#variable-run_acmesh_git_url)
  - [`run_acmesh_git_fallback_version_branch`](#variable-run_acmesh_git_fallback_version_branch)
  - [`run_acmesh_git_version`](#variable-run_acmesh_git_version)
  - [`run_acmesh_certs`](#variable-run_acmesh_certs)
    - [`run_acmesh_certs['domains']`](#variable-run_acmesh_certs-sub-domains)
      - [`run_acmesh_certs['domains']['name']`](#variable-run_acmesh_certs-sub-domains-sub-name)
      - [`run_acmesh_certs['domains']['challenge']`](#variable-run_acmesh_certs-sub-domains-sub-challenge)
        - [`run_acmesh_certs['domains']['challenge']['type']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-type)
        - [`run_acmesh_certs['domains']['challenge']['dns_provider']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_provider)
        - [`run_acmesh_certs['domains']['challenge']['challenge_alias']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-challenge_alias)
        - [`run_acmesh_certs['domains']['challenge']['domain_alias']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-domain_alias)
        - [`run_acmesh_certs['domains']['challenge']['webroot']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-webroot)
        - [`run_acmesh_certs['domains']['challenge']['httpport']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-httpport)
        - [`run_acmesh_certs['domains']['challenge']['tlsport']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-tlsport)
        - [`run_acmesh_certs['domains']['challenge']['dns_persist_wildcard']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_persist_wildcard)
        - [`run_acmesh_certs['domains']['challenge']['dns_persist_ca_name']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_persist_ca_name)
        - [`run_acmesh_certs['domains']['challenge']['dns_persist_days']`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_persist_days)
    - [`run_acmesh_certs['install']`](#variable-run_acmesh_certs-sub-install)
      - [`run_acmesh_certs['install']['ca_file']`](#variable-run_acmesh_certs-sub-install-sub-ca_file)
      - [`run_acmesh_certs['install']['cert_file']`](#variable-run_acmesh_certs-sub-install-sub-cert_file)
      - [`run_acmesh_certs['install']['fullchain_file']`](#variable-run_acmesh_certs-sub-install-sub-fullchain_file)
      - [`run_acmesh_certs['install']['key_file']`](#variable-run_acmesh_certs-sub-install-sub-key_file)
      - [`run_acmesh_certs['install']['reloadcmd']`](#variable-run_acmesh_certs-sub-install-sub-reloadcmd)
    - [`run_acmesh_certs['server']`](#variable-run_acmesh_certs-sub-server)
    - [`run_acmesh_certs['force']`](#variable-run_acmesh_certs-sub-force)
    - [`run_acmesh_certs['debug']`](#variable-run_acmesh_certs-sub-debug)
    - [`run_acmesh_certs['dnssleep']`](#variable-run_acmesh_certs-sub-dnssleep)
    - [`run_acmesh_certs['pre_hook']`](#variable-run_acmesh_certs-sub-pre_hook)
    - [`run_acmesh_certs['post_hook']`](#variable-run_acmesh_certs-sub-post_hook)
    - [`run_acmesh_certs['renew_hook']`](#variable-run_acmesh_certs-sub-renew_hook)
    - [`run_acmesh_certs['extra_flags']`](#variable-run_acmesh_certs-sub-extra_flags)
    - [`run_acmesh_certs['environment']`](#variable-run_acmesh_certs-sub-environment)
  - [`run_acmesh_user`](#variable-run_acmesh_user)
  - [`run_acmesh_group`](#variable-run_acmesh_group)
  - [`run_acmesh_cfg_accountemail`](#variable-run_acmesh_cfg_accountemail)
  - [`run_acmesh_cfg_home`](#variable-run_acmesh_cfg_home)
  - [`run_acmesh_cfg_config_home`](#variable-run_acmesh_cfg_config_home)
  - [`run_acmesh_cfg_cert_home`](#variable-run_acmesh_cfg_cert_home)
  - [`run_acmesh_cfg_logfile`](#variable-run_acmesh_cfg_logfile)
  - [`run_acmesh_cfg_log_level`](#variable-run_acmesh_cfg_log_level)
  - [`run_acmesh_cfg_syslog`](#variable-run_acmesh_cfg_syslog)
  - [`run_acmesh_cfg_ca_bundle`](#variable-run_acmesh_cfg_ca_bundle)
  - [`run_acmesh_cfg_ca_path`](#variable-run_acmesh_cfg_ca_path)
  - [`run_acmesh_cfg_account_keys`](#variable-run_acmesh_cfg_account_keys)
    - [`run_acmesh_cfg_account_keys['server']`](#variable-run_acmesh_cfg_account_keys-sub-server)
    - [`run_acmesh_cfg_account_keys['account_key']`](#variable-run_acmesh_cfg_account_keys-sub-account_key)
  - [`run_acmesh_dns_persist_pause`](#variable-run_acmesh_dns_persist_pause)
<!-- ANSIBLE DOCSMITH TOC END -->
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Features<a id="features"></a>

Main features:

- **Dedicated, configurable storage locations** for installation, configuration, and certificate files.
- **Dedicated, configurable service user and group (non-root, rootless)** for improved security, controlled via the `run_acmesh_user` and `run_acmesh_group` variables:
  - By default, other users cannot read certificates managed by `acme.sh`. See the [usage examples](#examples) for ways to grant access if needed.
  - By default, the service user defined by `run_acmesh_user` does not have permission to restart/reload privileged services. This may be required for [hooks](https://github.com/acmesh-official/acme.sh/wiki/Using-pre-hook-post-hook-renew-hook-reloadcmd) to function properly. See the [usage examples](#examples) for ways to allow service management if needed.
- **Automatic certificate renewal via systemd timer.**
- Support for multiple [ACME challenge types](https://github.com/acmesh-official/acme.sh/wiki/How-to-issue-a-cert): `alpn`, `dns` (including alias mode), `standalone`, and `webroot`
- Global `acme.sh` shell alias for easy execution.
- **Uploading of pre-seeded certificate files before issuing new ones**: Helps to prevent hitting CA rate limits, especially when frequently reinstalling target systems during development.


Currently not supported:

- The [acme.sh notify functionality](https://github.com/acmesh-official/acme.sh/wiki/notify).
- Native handling of the Apache and NGINX modes (but you can use `extra_flags` to pass `--nginx` or `--apache` if really necessary).



## Example playbooks, using this role<a id="examples"></a>

Using only one domain per certificate an the webroot challenge:

```yaml
---

- name: "Demo of the foundata.acmesh.run role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.acmesh.run role"
      ansible.builtin.include_role:
        name: "foundata.acmesh.run"
      vars:
        run_acmesh_autoupgrade: true
        run_acmesh_cfg_accountemail: "hostmaster@example.org"
        run_acmesh_certs:
          - domains:
              - name: "example.org"
                challenge:  # parameters depend on type
                  type: "webroot"
                  webroot: "/var/www/example.org"
            install:
              ca_file: "/etc/pki/tls/certs/example.org/ca.cer"
              cert_file: "/etc/pki/tls/certs/example.org/cert.cer"
              fullchain_file: "/etc/pki/tls/certs/example.org/fullchain.cer"
              key_file: "/etc/pki/tls/certs/example.org/cert.key"
              reloadcmd: "/bin/systemctl reload apache2.service"
            server: "letsencrypt_test" # optional, CA alias or URL, defaults to "letsencrypt" see https://github.com/acmesh-official/acme.sh/wiki/Server for details.
```

The role clones acme.sh from GitHub by default. Use the [`run_acmesh_git_url`](#variable-run_acmesh_git_url) parameter to point it at an internal Git mirror instead (e.g. for air-gapped environments).

By default, other users and groups cannot read the certificate files managed by `acme.sh`. To allow access, add specific service users (e.g., `www-data` or `nginx`) to the group defined by `run_acmesh_group` (defaults to `acmesh`). [`ansible.builtin.user`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/user_module.html) can help you with that:

```yaml
- name: "Grant the webserver's service user read access to certs by adding it to the acmesh group"
  ansible.builtin.user:
    name: "www-data"
    groups:
      - "acmesh" # the groupname get set via run_acmesh_group role variable, defaults to "acmesh"
    append: true # do not remove existing group memberships
```


Additionally you may need to allow the service user defined by `run_acmesh_user` (defaults to `acmesh`) to reload/restart services for [hooks](https://github.com/acmesh-official/acme.sh/wiki/Using-pre-hook-post-hook-renew-hook-reloadcmd) to function. [`community.general.sudoers`](https://docs.ansible.com/ansible/latest/collections/community/general/sudoers_module.html) can help you with that:

```yaml
- name: "Allow the acme.sh service user to reload / restart services with managed certificates"
  community.general.sudoers:
    name: "acmesh-service"
    user: "acmesh" # the username get set via run_acmesh_user role variable, defaults to "acmesh"
    commands:
      - "/bin/systemctl reload apache2.service"
      - "/bin/systemctl reload nginx.service"
      - "/bin/systemctl restart postfix.service"
    nopassword: true
```


Multiple domains per certificate with DNS challenge and challenge alias:

```yaml
---

- name: "Demo of the foundata.acmesh.run role (multiple domains, DNS challenge)"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.acmesh.run role"
      ansible.builtin.include_role:
        name: "foundata.acmesh.run"
      vars:
        run_acmesh_autoupgrade: true
        run_acmesh_cfg_accountemail: "hostmaster@example.org"
        run_acmesh_certs:
          # first certificate: "example.org"
          - domains:
              - name: "example.org"
                challenge:
                  type: "webroot"
                  webroot: "/var/www/example.org"
            install:
              ca_file: "/etc/pki/tls/certs/example.org/ca.cer"
              cert_file: "/etc/pki/tls/certs/example.org/cert.cer"
              fullchain_file: "/etc/pki/tls/certs/example.org/fullchain.cer"
              key_file: "/etc/pki/tls/certs/example.org/cert.key"
              reloadcmd: "systemctl reload apache2.service;"
            # optional, CA alias or URL, defaults to "letsencrypt" see
            # https://github.com/acmesh-official/acme.sh/wiki/Server
            server: "zerossl"

          # second certificate: "foo.example.com" with an additional "bar.example.com" SAN
          - domains:
              - name: "foo.example.com"
                challenge:  # parameters depend on type
                  type: "dns"
                  dns_provider: "dns_hetzner"
                  # CNAME _acme-challenge.foo.example.com => _acme-challenge.foo.example.com.example.net
                  challenge_alias: "foo.example.com.example.net"
              - name: "bar.example.com"
                challenge:
                  type: "dns"
                  dns_provider: "dns_inwx"
                  # CNAME _acme-challenge.bar.example.com => _acme-challenge.example.net
                  challenge_alias: example.net"
            install:
              ca_file: "/etc/pki/tls/certs/foo.example.com/ca.cer"
              cert_file: "/etc/pki/tls/certs/foo.example.com/cert.cer"
              fullchain_file: "/etc/pki/tls/certs/foo.example.com/fullchain.cer"
              key_file: "/etc/pki/tls/certs/foo.example.com/cert.key"
              reloadcmd: "systemctl reload nginx.service; systemctl restart postfix.service"
            # "{letsencrypt,buypass,google}_test" for staging, see
            # https://github.com/acmesh-official/acme.sh/wiki/Server
            server: "letsencrypt"
            force: false  # optional
            debug: false # optional
            post_hook: ""  # optional
            renew_hook: "" # optional
            extra_flags: "" # optional (workaround for edge cases, put --whatever here)

        # Environment variables needed for the DNS API authentication for
        # type: "dns" and dns_provider: "dns_hetzner" /  dns_provider: "dns_inwx"
        run_acmesh_environment:
          HETZNER_Token: "{{ lookup('ansible.builtin.unvault', '...') | ansible.builtin.string | ansible.builtin.trim }}"
          INWX_User: "exampleuser"
          INWX_Password: "{{ lookup('ansible.builtin.unvault', '...') | ansible.builtin.string | ansible.builtin.trim }}"
```

Uninstall (certificate files, if present, will be preserved):

```yaml
---

- name: "Demo of the foundata.acmesh.run role (removal, uninstall)"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.acmesh.run role"
      ansible.builtin.include_role:
        name: "foundata.acmesh.run"
      vars:
        run_acmesh_state: "absent"
```

This role supports **uploading backed-up acme.sh certificate folders from the Ansible control node to target systems** before issuing new certificates. Files are only transferred if they do not already exist on the target, preventing the accidental overwrite of up-to-date certificates. This feature helps avoid CA rate limits, especially when frequently reinstalling target systems during development.

**Usage:**

1. Back up a certificate directory such as `www.example.com_ecc` or `example.org_rsa` from acme.sh's certificate home (`run_acmesh_cfg_cert_home`, default: `/var/opt/acme.sh`).
2. Place the backup under `files/acme.sh/certhome` in your playbook directory on the control node.



## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `run_acmesh_setup`: Manage basic resources, such as packages or service users.
- `run_acmesh_config`: Manage settings, such as adapting or creating configuration files.
- `run_acmesh_cert`: Manage and issue certificates.

There are also tags usually not meant to be called directly but listed for the sake of completeness** and edge cases:

- `run_acmesh_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `run_acmesh_state` | `str` | No | `"present"` | Determines whether the managed resources should be `present` or `absent`.<br><br>`present` ensures that required components, such as software packages, are installed and configured.<br><br>`absent` reverts changes as much as possible, such as […](#variable-run_acmesh_state) |
| `run_acmesh_autoupgrade` | `bool` | No | `false` | If set to `true`, all managed packages will be upgraded during each Ansible run (e.g., when the package provider detects a newer version than the currently installed one). |
| `run_acmesh_autorenewal` | `bool` | No | `true` | Enables daily automatic certificate renewal via systemd timer (this role is not using acme.sh's cronjob function). |
| `run_acmesh_environment` | `dict` | No | `{}` | Defines environment variables required for ACME DNS challenges.<br><br>This is typically needed for DNS challenge plugins, such as those requiring DNS API credentials (e.g., `HETZNER_Token`, `INWX_User`, `INWX_Password`). Multiple variables can be […](#variable-run_acmesh_environment) |
| `run_acmesh_git_url` | `str` | No | `"https://github.com/acmesh-official/acme.sh.git"` | The Git repository URL for acme.sh. The role uses this URL to clone the source code during installation or updates and to query available version tags via `git ls-remote`.<br><br>Can be set to an internal Git mirror for air-gapped environments or to […](#variable-run_acmesh_git_url) |
| `run_acmesh_git_fallback_version_branch` | `str` | No | `"master"` | The Git branch to clone when no version tag could be determined from the remote repository (e.g. because `git ls-remote` failed or returned no matching tags).<br><br>See https://github.com/acmesh-official/acme.sh/issues/1162 for why acme.sh uses […](#variable-run_acmesh_git_fallback_version_branch) |
| `run_acmesh_git_version` | `str` | No | `""` | Overrides the automatically detected acme.sh version with a specific Git ref (tag, branch, or commit hash). When set (non-empty string), the role skips the upstream version tag detection via `git ls-remote` and uses this value directly for the `git […](#variable-run_acmesh_git_version) |
| `run_acmesh_certs` | `list` | No | `[]` | Defines certificates to be requested, their associated domains, challenge methods, and installation details. Each item in the list is a dictionary with suboptions / keys.<br><br>Example:<br><br>``` run_acmesh_certs: # first certificate: "example.org" […](#variable-run_acmesh_certs) |
| `run_acmesh_user` | `str` | No | `"acmesh"` | Specifies the service user account that runs acme.sh and owns relevant files and directories. |
| `run_acmesh_group` | `str` | No | `"acmesh"` | Specifies the group associated with the service user for managing acme.sh and the corresponding file permissions. |
| `run_acmesh_cfg_accountemail` | `str` | No | `""` | Specifies the email address to be associated with the ACME account. This email is used for expiration notices and recovery purposes. Some ACME providers might refuse to issue certificates if not set. |
| `run_acmesh_cfg_home` | `str` | No | `"/opt/acme.sh"` | Specifies the installation directory for the acme.sh software (relates to acme.sh option --home). Will also be used as home directory of the service user defined (see `run_acmesh_user`). |
| `run_acmesh_cfg_config_home` | `str` | No | `"/etc/acme.sh"` | Defines where configuration files are stored (relates to acme.sh option --config-home). |
| `run_acmesh_cfg_cert_home` | `str` | No | `"/var/opt/acme.sh"` | Specifies the directory where certificates are maintained by acme.sh (relates to acme.sh option --certhome). ⚠️ Do not rely on the files in this directory directly. Instead, copy the certificates where needed using the "install" key of […](#variable-run_acmesh_cfg_cert_home) |
| `run_acmesh_cfg_logfile` | `str` | No | `"/var/log/acme.sh.log"` | Path to the log file where acme.sh logs its operations (relates to acme.sh option --log). |
| `run_acmesh_cfg_log_level` | `int` | No | `1` | Specifies the log level (relates to acme.sh option --log-level). Possible values are 1 (less logging) and 2 (more logging). |
| `run_acmesh_cfg_syslog` | `int` | No | `3` | Specifies what to log (relates to acme.sh option --syslog). Possible values are 0 (disable syslog), 3 (errors), 6 (info) and 7 (debug) |
| `run_acmesh_cfg_ca_bundle` | `str` | No | `""` | Path to a custom CA certificate bundle file on the remote host. Passed as `--ca-bundle` to all acme.sh commands that make HTTPS requests (issue, register-account). Needed when the ACME server uses a certificate signed by a private or non-standard CA […](#variable-run_acmesh_cfg_ca_bundle) |
| `run_acmesh_cfg_ca_path` | `str` | No | `""` | Path to a directory of CA certificates in PEM format on the remote host. Passed as `--ca-path` to all acme.sh commands that make HTTPS requests. Alternative to `run_acmesh_cfg_ca_bundle` when the HTTP client (curl/wget) requires a directory of […](#variable-run_acmesh_cfg_ca_path) |
| `run_acmesh_cfg_account_keys` | `list` | No | `[]` | List of ACME account keys to pre-seed. This is useful for `dns-persist-01` challenges where the TXT record is bound to a specific account key, and you want to reuse the same key across multiple servers or after re-installations.<br><br>Each item must […](#variable-run_acmesh_cfg_account_keys) |
| `run_acmesh_dns_persist_pause` | `int` | No | `600` | Controls the pause duration (in seconds) after displaying dns-persist-01 TXT record instructions. Set to `0` to disable the pause (useful for CI/CD pipelines or environments where TXT records are guaranteed to already be published).<br><br>If the […](#variable-run_acmesh_dns_persist_pause) |

### `run_acmesh_state`<a id="variable-run_acmesh_state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Determines whether the managed resources should be `present` or `absent`.

`present` ensures that required components, such as software packages, are
installed and configured.

`absent` reverts changes as much as possible, such as removing packages,
deleting created users, stopping services, restoring modified settings, …

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`



### `run_acmesh_autoupgrade`<a id="variable-run_acmesh_autoupgrade"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, all managed packages will be upgraded during each Ansible
run (e.g., when the package provider detects a newer version than the
currently installed one).

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `run_acmesh_autorenewal`<a id="variable-run_acmesh_autorenewal"></a>

[*⇑ Back to ToC ⇑*](#toc)

Enables daily automatic certificate renewal via systemd timer (this role
is not using acme.sh's cronjob function).

- **Type**: `bool`
- **Required**: No
- **Default**: `true`



### `run_acmesh_environment`<a id="variable-run_acmesh_environment"></a>

[*⇑ Back to ToC ⇑*](#toc)

Defines environment variables required for ACME DNS challenges.

This is typically needed for DNS challenge plugins, such as those requiring
DNS API credentials (e.g., `HETZNER_Token`, `INWX_User`, `INWX_Password`).
Multiple variables can be defined in parallel to support different providers
for different domains on the same server. For more details on acme.sh's
DNS API support see https://github.com/acmesh-official/acme.sh/wiki/dnsapi

Example:

```
run_acmesh_environment:
  "HETZNER_Token": "\{\{ lookup('ansible.builtin.unvault', '...') | ansible.builtin.string | ansible.builtin.trim \}\}"
```

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`



### `run_acmesh_git_url`<a id="variable-run_acmesh_git_url"></a>

[*⇑ Back to ToC ⇑*](#toc)

The Git repository URL for acme.sh. The role uses this URL to clone the
source code during installation or updates and to query available version
tags via `git ls-remote`.

Can be set to an internal Git mirror for air-gapped environments or to
avoid GitHub API rate limits.

- **Type**: `str`
- **Required**: No
- **Default**: `"https://github.com/acmesh-official/acme.sh.git"`



### `run_acmesh_git_fallback_version_branch`<a id="variable-run_acmesh_git_fallback_version_branch"></a>

[*⇑ Back to ToC ⇑*](#toc)

The Git branch to clone when no version tag could be determined from the
remote repository (e.g. because `git ls-remote` failed or returned no
matching tags).

See https://github.com/acmesh-official/acme.sh/issues/1162 for why
acme.sh uses `master` as the branch for the latest release.

- **Type**: `str`
- **Required**: No
- **Default**: `"master"`



### `run_acmesh_git_version`<a id="variable-run_acmesh_git_version"></a>

[*⇑ Back to ToC ⇑*](#toc)

Overrides the automatically detected acme.sh version with a specific
Git ref (tag, branch, or commit hash). When set (non-empty string),
the role skips the upstream version tag detection via `git ls-remote`
and uses this value directly for the `git clone` operation.

This is useful when the latest tagged release does not yet include a
feature you need (setting to `master` is usually safe as acme.sh aims
for a production-ready `master` branch by default), or when you want
to pin a specific version for reproducibility.

When set, the upgrade task also respects this value and skips the
normal semver comparison that gates upgrades.

- **Type**: `str`
- **Required**: No
- **Default**: `""`



### `run_acmesh_certs`<a id="variable-run_acmesh_certs"></a>

[*⇑ Back to ToC ⇑*](#toc)

Defines certificates to be requested, their associated domains,
challenge methods, and installation details. Each item in the list is a
dictionary with suboptions / keys.

Example:

```
run_acmesh_certs:
  # first certificate: "example.org"
  - domains:
      - name: "example.org"
        challenge: # parameters depend on type
          type: "webroot"
          webroot: "/var/www/example.org"
    install:
      ca_file: "/etc/pki/tls/certs/example.org/ca.cer"
      cert_file: "/etc/pki/tls/certs/example.org/cert.cer"
      fullchain_file: "/etc/pki/tls/certs/example.org/fullchain.cer"
      key_file: "/etc/pki/tls/certs/example.org/cert.key"
      reloadcmd: "systemctl reload apache2.service;"
  # second certificate: "foo.example.com" with an additional "bar.example.com" SAN
  - domains:
      - name: "foo.example.com"
        challenge: # parameters depend on type
          type: "dns"
          dns_provider: "dns_hetzner"
          challenge_alias: "foo.example.com.example.net"
      - name: "bar.example.com"
        challenge:
          type: "dns"
          dns_provider: "dns_inwx"
          challenge_alias: "bar.example.com.example.net"
    install:
      ca_file: "/etc/pki/tls/certs/foo.example.com/ca.cer"
      cert_file: "/etc/pki/tls/certs/foo.example.com/cert.cer"
      fullchain_file: "/etc/pki/tls/certs/foo.example.com/fullchain.cer"
      key_file: "/etc/pki/tls/certs/foo.example.com/cert.key"
      reloadcmd: "systemctl reload nginx.service; systemctl restart postfix.service"
    # optional, CA alias or URL, defaults to "letsencrypt". "{letsencrypt,buypass,google}_test"
    # for staging, see https://github.com/acmesh-official/acme.sh/wiki/Server for details.
    server: "zerossl"
    force: false  # optional
    debug: false # optional
    post_hook: ""  # optional
    renew_hook: "" # optional
    extra_flags: "" # optional (workaround for edge cases, put --whatever in here, used during issuing a cert")

# Environment variables needed for the DNS API authentication for
# type: "dns" and dns_provider: "dns_hetzner" /  dns_provider: "dns_inwx"
run_acmesh_environment:
  HETZNER_Token: "\{\{ lookup('ansible.builtin.unvault', '...') | ansible.builtin.string | ansible.builtin.trim \}\}"
  INWX_User: "exampleuser"
  INWX_Password: "\{\{ lookup('ansible.builtin.unvault', '...') | ansible.builtin.string | ansible.builtin.trim \}\}"
```

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `dict`

#### `run_acmesh_certs['domains']`<a id="variable-run_acmesh_certs-sub-domains"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of dictionaries specifying the domains to be included in the
certificate request, along with their challenge configurations. If multiple
domains are defined, they will be included in the same certificate as
Subject Alternative Names (SANs).

- **Type**: `list`
- **Required**: No
- **List Elements**: `dict`

##### `run_acmesh_certs['domains']['name']`<a id="variable-run_acmesh_certs-sub-domains-sub-name"></a>

[*⇑ Back to ToC ⇑*](#toc)

The domain name to request a certificate for.

- **Type**: `str`
- **Required**: No

##### `run_acmesh_certs['domains']['challenge']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge"></a>

[*⇑ Back to ToC ⇑*](#toc)

Dictionary defining the ACME challenge parameters. The required
parameters depend on the challenge type

- **Type**: `dict`
- **Required**: No

###### `run_acmesh_certs['domains']['challenge']['type']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-type"></a>

[*⇑ Back to ToC ⇑*](#toc)

Challenge method. See https://github.com/acmesh-official/acme.sh/wiki/How-to-issue-a-cert
for details.

- **Type**: `str`
- **Required**: No
- **Choices**: `alpn`, `dns`, `dns_persist`, `standalone`, `webroot`

###### `run_acmesh_certs['domains']['challenge']['dns_provider']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_provider"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Required for "dns" challenges. Specifies
the DNS provider for API-based verification. See
https://github.com/acmesh-official/acme.sh/wiki/dnsapi for supported
providers and their name. You usually have to provide credentials for
their APIs via the global `run_acmesh_environment` variable or the
per-certificate `environment` key.

- **Type**: `str`
- **Required**: No

###### `run_acmesh_certs['domains']['challenge']['challenge_alias']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-challenge_alias"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Used with "dns" challenges when using CNAME delegation. Requires
a CNAME record such as:
`_acme-challenge.example.com` -> `_acme-challenge.example.com.example.net`
See https://github.com/acmesh-official/acme.sh/wiki/DNS-alias-mode for
details.

- **Type**: `str`
- **Required**: No

###### `run_acmesh_certs['domains']['challenge']['domain_alias']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-domain_alias"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Used with "dns" challenges as an alternative to
`challenge_alias`. Instead of CNAME delegation, the alias domain is
set directly as the domain to use for the DNS challenge validation.
See https://github.com/acmesh-official/acme.sh/wiki/DNS-alias-mode
for details.

- **Type**: `str`
- **Required**: No

###### `run_acmesh_certs['domains']['challenge']['webroot']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-webroot"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Required for "webroot" challenges. Specifies
the directory where the ACME challenge response should be placed
(e.g. the document root of the web server serving the domain).
See https://github.com/acmesh-official/acme.sh/wiki/How-to-issue-a-cert
for details.

- **Type**: `str`
- **Required**: No

###### `run_acmesh_certs['domains']['challenge']['httpport']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-httpport"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Used with "httpport" challenges. Specifies
a non-standard port for acme.sh's internal HTTP webserver to listen,
might be needed behind a reverse proxy or load balancer.

- **Type**: `int`
- **Required**: No

###### `run_acmesh_certs['domains']['challenge']['tlsport']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-tlsport"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Used with "alpn" challenges. Specifies a non-standard port for
acme.sh's internal HTTPS webserver to listen, might be needed behind a
reverse proxy or load balancer.

- **Type**: `int`
- **Required**: No

###### `run_acmesh_certs['domains']['challenge']['dns_persist_wildcard']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_persist_wildcard"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Used with "dns_persist" challenges. If true, the persistent
TXT record will also authorize wildcard certificates and matching
subdomains for this domain. Corresponds to acme.sh --dns-persist-wildcard.
See https://github.com/acmesh-official/acme.sh/wiki/DNS-persist-mode
for details.

- **Type**: `bool`
- **Required**: No

###### `run_acmesh_certs['domains']['challenge']['dns_persist_ca_name']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_persist_ca_name"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Used with "dns_persist" challenges. Specifies a custom CA
identity domain name for the TXT record value (instead of deriving it
from the server URL). Corresponds to acme.sh --dns-persist-ca-name.
See https://github.com/acmesh-official/acme.sh/wiki/DNS-persist-mode
for details.

- **Type**: `str`
- **Required**: No

###### `run_acmesh_certs['domains']['challenge']['dns_persist_days']`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_persist_days"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Used with "dns_persist" challenges. Specifies the number of
days the TXT record should be considered valid (adds a persistUntil
field to the record). Corresponds to acme.sh --dns-persist-days.
See https://github.com/acmesh-official/acme.sh/wiki/DNS-persist-mode
for details.

- **Type**: `int`
- **Required**: No



#### `run_acmesh_certs['install']`<a id="variable-run_acmesh_certs-sub-install"></a>

[*⇑ Back to ToC ⇑*](#toc)

Dictionary defining where to install the issued certificates.
The following keys specify file paths and a reload command:
- ca_file: String. Path to the certificate authority (CA) file.
- cert_file: String. Path to the certificate file.
- fullchain_file: String. Path to the full certificate chain file.
- key_file: String. Path to the private key file.
- reloadcmd: String. Command to reload or restart services after certificate
  renewal (e.g., web server or mail server).

- **Type**: `dict`
- **Required**: No

##### `run_acmesh_certs['install']['ca_file']`<a id="variable-run_acmesh_certs-sub-install-sub-ca_file"></a>

[*⇑ Back to ToC ⇑*](#toc)



- **Type**: `str`
- **Required**: No

##### `run_acmesh_certs['install']['cert_file']`<a id="variable-run_acmesh_certs-sub-install-sub-cert_file"></a>

[*⇑ Back to ToC ⇑*](#toc)



- **Type**: `str`
- **Required**: No

##### `run_acmesh_certs['install']['fullchain_file']`<a id="variable-run_acmesh_certs-sub-install-sub-fullchain_file"></a>

[*⇑ Back to ToC ⇑*](#toc)



- **Type**: `str`
- **Required**: No

##### `run_acmesh_certs['install']['key_file']`<a id="variable-run_acmesh_certs-sub-install-sub-key_file"></a>

[*⇑ Back to ToC ⇑*](#toc)



- **Type**: `str`
- **Required**: No

##### `run_acmesh_certs['install']['reloadcmd']`<a id="variable-run_acmesh_certs-sub-install-sub-reloadcmd"></a>

[*⇑ Back to ToC ⇑*](#toc)



- **Type**: `str`
- **Required**: No


#### `run_acmesh_certs['server']`<a id="variable-run_acmesh_certs-sub-server"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Specifies the ACME CA server to use. Defaults
to `letsencrypt`. Other options include:
- "letsencrypt_test", "buypass_test", "google_test" for staging environments.
- Custom CA URLs can also be used. See
  https://github.com/acmesh-official/acme.sh/wiki/Server for a full list
  and details.

- **Type**: `str`
- **Required**: No
- **Default**: `"letsencrypt"`

#### `run_acmesh_certs['force']`<a id="variable-run_acmesh_certs-sub-force"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. If true, forces certificate issuance even if
the current certificate is still valid. Defaults to `false`.

- **Type**: `bool`
- **Required**: No

#### `run_acmesh_certs['debug']`<a id="variable-run_acmesh_certs-sub-debug"></a>

[*⇑ Back to ToC ⇑*](#toc)



- **Type**: `bool`
- **Required**: No

#### `run_acmesh_certs['dnssleep']`<a id="variable-run_acmesh_certs-sub-dnssleep"></a>

[*⇑ Back to ToC ⇑*](#toc)



- **Type**: `int`
- **Required**: No

#### `run_acmesh_certs['pre_hook']`<a id="variable-run_acmesh_certs-sub-pre_hook"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Command to execute before attempting certificate
issuance or renewal. See
https://github.com/acmesh-official/acme.sh/wiki/Using-pre-hook-post-hook-renew-hook-reloadcmd
for details.

- **Type**: `str`
- **Required**: No

#### `run_acmesh_certs['post_hook']`<a id="variable-run_acmesh_certs-sub-post_hook"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Command to execute after a successful certificate issuance or renewal. See
https://github.com/acmesh-official/acme.sh/wiki/Using-pre-hook-post-hook-renew-hook-reloadcmd
for details.

- **Type**: `str`
- **Required**: No

#### `run_acmesh_certs['renew_hook']`<a id="variable-run_acmesh_certs-sub-renew_hook"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Command to execute after renewing the certificate. See
https://github.com/acmesh-official/acme.sh/wiki/Using-pre-hook-post-hook-renew-hook-reloadcmd
for details.

- **Type**: `str`
- **Required**: No

#### `run_acmesh_certs['extra_flags']`<a id="variable-run_acmesh_certs-sub-extra_flags"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Additional CLI flags for edge cases. Useful for passing custom parameters during
certificate issuance wich are not natively supported by this role, just pass them as
"--foo --bar 'baz'".

- **Type**: `str`
- **Required**: No

#### `run_acmesh_certs['environment']`<a id="variable-run_acmesh_certs-sub-environment"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional. Dictionary of environment variables specific to this certificate.
Setting environment variables per certificate can improve readability, as
it clearly shows which certificate  or domain is using which credentials
in setups that involve multiple DNS provider credentials.

These are merged with the  global`run_acmesh_environment`, with
per-certificate values taking precedence on key conflicts.

Please note that acme.sh DNS API plugins usually persist credentials per
provider (not per certificate) in `account.conf`, so using different
credentials for the same DNS provider across certificates will result in
only the last-written set being saved for automatic renewals.

- **Type**: `dict`
- **Required**: No



### `run_acmesh_user`<a id="variable-run_acmesh_user"></a>

[*⇑ Back to ToC ⇑*](#toc)

Specifies the service user account that runs acme.sh and owns relevant
files and directories.

- **Type**: `str`
- **Required**: No
- **Default**: `"acmesh"`



### `run_acmesh_group`<a id="variable-run_acmesh_group"></a>

[*⇑ Back to ToC ⇑*](#toc)

Specifies the group associated with the service user for managing
acme.sh and the corresponding file permissions.

- **Type**: `str`
- **Required**: No
- **Default**: `"acmesh"`



### `run_acmesh_cfg_accountemail`<a id="variable-run_acmesh_cfg_accountemail"></a>

[*⇑ Back to ToC ⇑*](#toc)

Specifies the email address to be associated with the ACME account.
This email is used for expiration notices and recovery purposes.
Some ACME providers might refuse to issue certificates if not set.

- **Type**: `str`
- **Required**: No
- **Default**: `""`



### `run_acmesh_cfg_home`<a id="variable-run_acmesh_cfg_home"></a>

[*⇑ Back to ToC ⇑*](#toc)

Specifies the installation directory for the acme.sh software  (relates
to acme.sh option --home). Will also  be used as home directory of the
service user defined (see `run_acmesh_user`).

- **Type**: `str`
- **Required**: No
- **Default**: `"/opt/acme.sh"`



### `run_acmesh_cfg_config_home`<a id="variable-run_acmesh_cfg_config_home"></a>

[*⇑ Back to ToC ⇑*](#toc)

Defines where configuration files are stored (relates to acme.sh option
--config-home).

- **Type**: `str`
- **Required**: No
- **Default**: `"/etc/acme.sh"`



### `run_acmesh_cfg_cert_home`<a id="variable-run_acmesh_cfg_cert_home"></a>

[*⇑ Back to ToC ⇑*](#toc)

Specifies the directory where certificates are maintained by
acme.sh (relates to acme.sh option --certhome).
⚠️ Do not rely on the files in this directory directly. Instead, copy
the certificates where needed using the "install" key of `run_acmesh_certs`
(relates to acme.sh option --install-cert). This ensures that the
certificates are properly maintained and automatically reinstalled
upon renewal. See the following for more information:
https://github.com/acmesh-official/acme.sh/issues/2350#issuecomment-1449235599

- **Type**: `str`
- **Required**: No
- **Default**: `"/var/opt/acme.sh"`



### `run_acmesh_cfg_logfile`<a id="variable-run_acmesh_cfg_logfile"></a>

[*⇑ Back to ToC ⇑*](#toc)

Path to the log file where acme.sh logs its operations (relates to acme.sh
option --log).

- **Type**: `str`
- **Required**: No
- **Default**: `"/var/log/acme.sh.log"`



### `run_acmesh_cfg_log_level`<a id="variable-run_acmesh_cfg_log_level"></a>

[*⇑ Back to ToC ⇑*](#toc)

Specifies the log level (relates to acme.sh option --log-level).
Possible values are 1 (less logging) and 2 (more logging).

- **Type**: `int`
- **Required**: No
- **Default**: `1`
- **Choices**: `1`, `2`



### `run_acmesh_cfg_syslog`<a id="variable-run_acmesh_cfg_syslog"></a>

[*⇑ Back to ToC ⇑*](#toc)

Specifies what to log (relates to acme.sh option --syslog).
Possible values are 0 (disable syslog), 3 (errors), 6 (info) and 7
(debug)

- **Type**: `int`
- **Required**: No
- **Default**: `3`
- **Choices**: `0`, `3`, `6`, `7`



### `run_acmesh_cfg_ca_bundle`<a id="variable-run_acmesh_cfg_ca_bundle"></a>

[*⇑ Back to ToC ⇑*](#toc)

Path to a custom CA certificate bundle file on the remote host. Passed
as `--ca-bundle` to all acme.sh commands that make HTTPS requests (issue,
register-account). Needed when the ACME server uses a certificate signed
by a private or non-standard CA (e.g., a local pebble test server).

This is a global acme.sh setting -- acme.sh persists it to its
`account.conf` and applies it to all operations including cron renewals.

- **Type**: `str`
- **Required**: No
- **Default**: `""`



### `run_acmesh_cfg_ca_path`<a id="variable-run_acmesh_cfg_ca_path"></a>

[*⇑ Back to ToC ⇑*](#toc)

Path to a directory of CA certificates in PEM format on the remote host.
Passed as `--ca-path` to all acme.sh commands that make HTTPS requests.
Alternative to `run_acmesh_cfg_ca_bundle` when the HTTP client (curl/wget)
requires a directory of individual CA certificate files.

This is a global acme.sh setting -- acme.sh persists it to its
`account.conf` and applies it to all operations including cron renewals.

- **Type**: `str`
- **Required**: No
- **Default**: `""`



### `run_acmesh_cfg_account_keys`<a id="variable-run_acmesh_cfg_account_keys"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of ACME account keys to pre-seed. This is useful for `dns-persist-01`
challenges where the TXT record is bound to a specific account key, and
you want to reuse the same key across multiple servers or after
re-installations.

Each item must specify a `server` (CA alias or URL, same value used in
`run_acmesh_certs[].server`) and `account_key` (PEM-encoded private key
content). The role seeds the key and then runs `acme.sh --register-account`
which confirms the account with the CA and may generate the `account.json`
metadata automatically if needed (per RFC 8555 section 7.3.1, the CA
identifies accounts by their public key).

Example:

```
run_acmesh_cfg_account_keys:
  - server: "letsencrypt"
    account_key: "\{\{ lookup('ansible.builtin.unvault', 'files/acmesh_account_key_letsencrypt.pem') \}\}"
```

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `dict`

#### `run_acmesh_cfg_account_keys['server']`<a id="variable-run_acmesh_cfg_account_keys-sub-server"></a>

[*⇑ Back to ToC ⇑*](#toc)

The CA alias or full ACME directory URL. Must match the value used in
`run_acmesh_certs[].server` (e.g., "letsencrypt", "zerossl", or a URL).

- **Type**: `str`
- **Required**: Yes

#### `run_acmesh_cfg_account_keys['account_key']`<a id="variable-run_acmesh_cfg_account_keys-sub-account_key"></a>

[*⇑ Back to ToC ⇑*](#toc)

PEM-encoded ACME account private key content. Sensitive - use
`ansible.builtin.unvault` or similar secret management to supply this
value.

- **Type**: `str`
- **Required**: Yes



### `run_acmesh_dns_persist_pause`<a id="variable-run_acmesh_dns_persist_pause"></a>

[*⇑ Back to ToC ⇑*](#toc)

Controls the pause duration (in seconds) after displaying dns-persist-01
TXT record instructions. Set to `0` to disable the pause (useful for
CI/CD pipelines or environments where TXT records are guaranteed to
already be published).

If the pause expires without user confirmation, the play continues.

- **Type**: `int`
- **Required**: No
- **Default**: `600`




<!-- ANSIBLE DOCSMITH MAIN END -->


## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__run_acmesh_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

* **Git repository access:** The role uses `git ls-remote` to query available version tags from the configured git repository. This works with any git remote (GitHub, GitLab, local mirrors), making it suitable for air-gapped environments with internal mirrors (see [`run_acmesh_git_url`](#variable-run_acmesh_git_url) parameter).
* **SELinux**: This role does not handle SELinux configurations. Please add additional tasks before or after this role to accommodate these changes (e.g. `cert_t` might be needed as context). The following Ansible modules may help with SELinux configuration:
  - [`ansible.posix.selinux`](https://docs.ansible.com/ansible/latest/collections/ansible/posix/selinux_module.html)
  - [`community.general.sefcontext_module`](https://docs.ansible.com/ansible/latest/collections/community/general/sefcontext_module.html)
  - [`community.general.seport_module`](https://docs.ansible.com/ansible/latest/collections/community/general/seport_module.html)
* **Permissions to restart services for the service user:** Additionally you may need to allow the service user defined by `run_acmesh_user` (defaults to `acmesh`) to reload/restart services for [hooks](https://github.com/acmesh-official/acme.sh/wiki/Using-pre-hook-post-hook-renew-hook-reloadcmd) to function. Using `sudo` in the hook and [`community.general.sudoers`](https://docs.ansible.com/ansible/latest/collections/community/general/sudoers_module.html) can help you with that:
  ```yaml
  - name: "Allow the acme.sh service user to reload / restart services with managed certificates"
    community.general.sudoers:
      name: "acmesh-service"
      user: "acmesh" # the username get set via run_acmesh_user role variable, defaults to "acmesh"
      commands:
        - "/bin/systemctl reload apache2.service"
        - "/bin/systemctl reload nginx.service"
        - "/bin/systemctl restart postfix.service"
      nopassword: true
  ```

Beside that, there are no special requirements not covered by the role or Ansible itself.