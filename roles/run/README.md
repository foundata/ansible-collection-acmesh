# Ansible role: `foundata.acmesh.run`

The `foundata.acmesh.run` Ansible role (part if the `foundata.acmesh` Ansible collection). It provides automated management of ACME certificates using acme.sh.



## Table of contents<a id="toc"></a>

- [Features](#features)<!-- BEGIN ANSIBLE DOCSMITH TOC -->
- [Role variables](#variables)
  - [`run_acmesh_state`](#variable-run_acmesh_state)
  - [`run_acmesh_autoupgrade`](#variable-run_acmesh_autoupgrade)
  - [`run_acmesh_autorenewal`](#variable-run_acmesh_autorenewal)
  - [`run_acmesh_environment`](#variable-run_acmesh_environment)
  - [`run_acmesh_certs`](#variable-run_acmesh_certs)
    - [`domains`](#variable-run_acmesh_certs-sub-domains)
      - [`name`](#variable-run_acmesh_certs-sub-domains-sub-name)
      - [`challenge`](#variable-run_acmesh_certs-sub-domains-sub-challenge)
        - [`type`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-type)
        - [`dns_provider`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_provider)
        - [`challenge_alias`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-challenge_alias)
        - [`domain_alias`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-domain_alias)
        - [`httpport`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-httpport)
        - [`tlsport`](#variable-run_acmesh_certs-sub-domains-sub-challenge-sub-tlsport)
    - [`install`](#variable-run_acmesh_certs-sub-install)
      - [`ca_file`](#variable-run_acmesh_certs-sub-install-sub-ca_file)
      - [`cert_file`](#variable-run_acmesh_certs-sub-install-sub-cert_file)
      - [`fullcain_file`](#variable-run_acmesh_certs-sub-install-sub-fullcain_file)
      - [`key_file`](#variable-run_acmesh_certs-sub-install-sub-key_file)
      - [`reloadcmd`](#variable-run_acmesh_certs-sub-install-sub-reloadcmd)
    - [`server`](#variable-run_acmesh_certs-sub-server)
    - [`force`](#variable-run_acmesh_certs-sub-force)
    - [`debug`](#variable-run_acmesh_certs-sub-debug)
    - [`dnssleep`](#variable-run_acmesh_certs-sub-dnssleep)
    - [`pre_hook`](#variable-run_acmesh_certs-sub-pre_hook)
    - [`post_hook`](#variable-run_acmesh_certs-sub-post_hook)
    - [`renew_hook`](#variable-run_acmesh_certs-sub-renew_hook)
    - [`extra_flags`](#variable-run_acmesh_certs-sub-extra_flags)
  - [`run_acmesh_user`](#variable-run_acmesh_user)
  - [`run_acmesh_group`](#variable-run_acmesh_group)
  - [`run_acmesh_cfg_accountemail`](#variable-run_acmesh_cfg_accountemail)
  - [`run_acmesh_cfg_home`](#variable-run_acmesh_cfg_home)
  - [`run_acmesh_cfg_config_home`](#variable-run_acmesh_cfg_config_home)
  - [`run_acmesh_cfg_cert_home`](#variable-run_acmesh_cfg_cert_home)
  - [`run_acmesh_cfg_logfile`](#variable-run_acmesh_cfg_logfile)
  - [`run_acmesh_cfg_log_level`](#variable-run_acmesh_cfg_log_level)
  - [`run_acmesh_cfg_syslog`](#variable-run_acmesh_cfg_syslog)
<!-- END ANSIBLE DOCSMITH TOC -->
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)
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


<!-- BEGIN ANSIBLE DOCSMITH MAIN -->

## Role variables<a id="variables"></a>

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `run_acmesh_state` | `str` | Yes | `"present"` | Determines whether the managed resources should be `present` or `absent`.<br><br>`present` ensures that required components, such as software packages, are installed and configured.<br><br>`absent` reverts changes as much as possible, such as […](#variable-run_acmesh_state) |
| `run_acmesh_autoupgrade` | `bool` | Yes | `false` | If set to true, all managed packages will be upgraded during each Ansible run (e.g., when the package provider detects a newer version than the currently installed one). |
| `run_acmesh_autorenewal` | `bool` | Yes | `true` | Enables daily automatic certificate renewal via systemd timer (this role is not using acme.sh's cronjob function). |
| `run_acmesh_environment` | `dict` | Yes | `{}` | Defines environment variables required for ACME DNS challenges.<br><br>This is typically needed for DNS challenge plugins, such as those requiring DNS API credentials (e.g., `HETZNER_Token`, `INWX_User`, `INWX_Password`). Multiple variables can be […](#variable-run_acmesh_environment) |
| `run_acmesh_certs` | `list` | Yes | `[]` | Defines certificates to be requested, their associated domains, challenge methods, and installation details. Each item in the list is a dictionary with suboptions / keys.<br><br>Example:<br><br>``` run_acmesh_certs: # first certificate: "example.org" […](#variable-run_acmesh_certs) |
| `run_acmesh_user` | `str` | Yes | `"acmesh"` | Specifies the service user account that runs acme.sh and owns relevant files and directories. |
| `run_acmesh_group` | `str` | Yes | `"acmesh"` | Specifies the group associated with the service user for managing acme.sh and its file permissions. |
| `run_acmesh_cfg_accountemail` | `str` | Yes | `""` | Specifies the email address to be associated with the ACME account. This email is used for expiration notices and recovery purposes. Some ACME providers might refuse to issue certificates if not set. |
| `run_acmesh_cfg_home` | `str` | Yes | `"/opt/acme.sh"` | Specifies the installation directory for the acme.sh software (relates to acme.sh option --home). Will also be used as home directory of the service user defined (see `run_acmesh_user``). |
| `run_acmesh_cfg_config_home` | `str` | Yes | `"/etc/acme.sh"` | Defines where configuration files are stored (relates to acme.sh option --config-home). |
| `run_acmesh_cfg_cert_home` | `str` | Yes | `"/var/opt/acme.sh"` | Specifies the directory where certificates are maintained by acme.sh (relates to acme.sh option --certhome). ⚠️ Do not rely on the files in this directory directly. Instead, copy the certificates where needed using the "install" key of […](#variable-run_acmesh_cfg_cert_home) |
| `run_acmesh_cfg_logfile` | `str` | Yes | `"/var/log/acme.sh.log"` | Path to the log file where acme.sh logs its operations (relates to acme.sh option --log). |
| `run_acmesh_cfg_log_level` | `int` | Yes | `1` | Specifies the log level (relates to acme.sh option --log-level). Possible values are 1 (less logging) and 2 (more logging). |
| `run_acmesh_cfg_syslog` | `int` | Yes | `3` | Specifies what to log (relates to acme.sh option --syslog). Possible values are 0 (disable syslog), 3 (errors), 6 (info) and 7 (debug) |

### `run_acmesh_state`<a id="variable-run_acmesh_state"></a>

Determines whether the managed resources should be `present` or `absent`.

`present` ensures that required components, such as software packages, are
installed and configured.

`absent` reverts changes as much as possible, such as removing packages,
deleting created users, stopping services, restoring modified settings, …

- **Type**: `str`
- **Required**: Yes
- **Default**: `"present"`
- **Choices**: `present`, `absent`



### `run_acmesh_autoupgrade`<a id="variable-run_acmesh_autoupgrade"></a>

If set to true, all managed packages will be upgraded during each Ansible
run (e.g., when the package provider detects a newer version than the
currently installed one).

- **Type**: `bool`
- **Required**: Yes
- **Default**: `false`



### `run_acmesh_autorenewal`<a id="variable-run_acmesh_autorenewal"></a>

Enables daily automatic certificate renewal via systemd timer (this role
is not using acme.sh's cronjob function).

- **Type**: `bool`
- **Required**: Yes
- **Default**: `true`



### `run_acmesh_environment`<a id="variable-run_acmesh_environment"></a>

Defines environment variables required for ACME DNS challenges.

This is typically needed for DNS challenge plugins, such as those requiring
DNS API credentials (e.g., `HETZNER_Token`, `INWX_User`, `INWX_Password`).
Multiple variables can be defined in parallel to support different providers
for different domains on the same server. For more details on acme.sh's
DNS API support see https://github.com/acmesh-official/acme.sh/wiki/dnsapi

Example:

```
run_acmesh_environment:
  "HETZNER_Token": "{{ lookup('ansible.builtin.unvault', '...') | string | trim }}"
```

- **Type**: `dict`
- **Required**: Yes
- **Default**: `{}`



### `run_acmesh_certs`<a id="variable-run_acmesh_certs"></a>

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
      fullcain_file: "/etc/pki/tls/certs/example.org/fullchain.cer"
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
      fullcain_file: "/etc/pki/tls/certs/foo.example.com/fullchain.cer"
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
  HETZNER_Token: "{{ lookup('ansible.builtin.unvault', '...') | string | trim }}"
  INWX_User: "exampleuser"
  INWX_Password: "{{ lookup('ansible.builtin.unvault', '...') | string | trim }}"
```

- **Type**: `list`
- **Required**: Yes
- **Default**: `[]`
- **List Elements**: `dict`

#### `domains`<a id="variable-run_acmesh_certs-sub-domains"></a>

List of dictionaries specifying the domains to be included in the
certificate request, along with their challenge configurations. If multiple
domains are defined, they will be included in the same certificate as
Subject Alternative Names (SANs).

- **Type**: `list`
- **Required**: No
- **List Elements**: `dict`

##### `name`<a id="variable-run_acmesh_certs-sub-domains-sub-name"></a>

The domain name to request a certificate for.

- **Type**: `str`
- **Required**: No

##### `challenge`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge"></a>

Dictionary defining the ACME challenge parameters. The required
parameters depend on the challenge type

- **Type**: `dict`
- **Required**: No

###### `type`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-type"></a>

Challenge method. See https://github.com/acmesh-official/acme.sh/wiki/How-to-issue-a-cert
for details.

- **Type**: `str`
- **Required**: No
- **Choices**: `alpn`, `dns`, `standalone`, `webroot`

###### `dns_provider`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-dns_provider"></a>

Optional. Required for "dns" challenges. Specifies
the DNS provider for API-based verification. See
https://github.com/acmesh-official/acme.sh/wiki/dnsapi for supported
providers and their name. You usually have to provide credentials for
their APIs via the "run_acmesh_environment" variable.

- **Type**: `str`
- **Required**: No

###### `challenge_alias`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-challenge_alias"></a>

Optional. Used with "dns" challenges when using CNAME delegation. Requires
a CNAME record such as:
`_acme-challenge.example.com` -> `_acme-challenge.example.com.example.net`
See https://github.com/acmesh-official/acme.sh/wiki/DNS-alias-mode for
details.

- **Type**: `str`
- **Required**: No

###### `domain_alias`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-domain_alias"></a>

Optional. Required for "webroot" challenges. Specifies
the directory where the ACME challenge response should be placed.
See https://github.com/acmesh-official/acme.sh/wiki/How-to-issue-a-cert
for details.

- **Type**: `str`
- **Required**: No

###### `httpport`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-httpport"></a>

Optional. Used with "httpport" challenges. Specifies
a non-standard port for acme.sh's internal HTTP webserver to listen,
might be needed behind a reverse proxy or load balancer.

- **Type**: `int`
- **Required**: No

###### `tlsport`<a id="variable-run_acmesh_certs-sub-domains-sub-challenge-sub-tlsport"></a>

Optional. Used with "alpn" challenges. Specifies a non-standard port for
acme.sh's internal HTTPS webserver to listen, might be needed behind a
reverse proxy or load balancer.

- **Type**: `int`
- **Required**: No



#### `install`<a id="variable-run_acmesh_certs-sub-install"></a>

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

##### `ca_file`<a id="variable-run_acmesh_certs-sub-install-sub-ca_file"></a>



- **Type**: `str`
- **Required**: No

##### `cert_file`<a id="variable-run_acmesh_certs-sub-install-sub-cert_file"></a>



- **Type**: `str`
- **Required**: No

##### `fullcain_file`<a id="variable-run_acmesh_certs-sub-install-sub-fullcain_file"></a>



- **Type**: `str`
- **Required**: No

##### `key_file`<a id="variable-run_acmesh_certs-sub-install-sub-key_file"></a>



- **Type**: `str`
- **Required**: No

##### `reloadcmd`<a id="variable-run_acmesh_certs-sub-install-sub-reloadcmd"></a>



- **Type**: `str`
- **Required**: No


#### `server`<a id="variable-run_acmesh_certs-sub-server"></a>

Optional. Specifies the ACME CA server to use. Defaults
to `letsencrypt`. Other options include:
- "letsencrypt_test", "buypass_test", "google_test" for staging environments.
- Custom CA URLs can also be used. See
  https://github.com/acmesh-official/acme.sh/wiki/Server for a full list
  and details.

- **Type**: `str`
- **Required**: No
- **Default**: `"letsencrypt"`

#### `force`<a id="variable-run_acmesh_certs-sub-force"></a>

Optional. If true, forces certificate issuance even if
the current certificate is still valid. Defaults to false.

- **Type**: `bool`
- **Required**: No

#### `debug`<a id="variable-run_acmesh_certs-sub-debug"></a>



- **Type**: `bool`
- **Required**: No

#### `dnssleep`<a id="variable-run_acmesh_certs-sub-dnssleep"></a>



- **Type**: `int`
- **Required**: No

#### `pre_hook`<a id="variable-run_acmesh_certs-sub-pre_hook"></a>

Optional. Command to execute before attempting certificate
issuance or renewal. See
https://github.com/acmesh-official/acme.sh/wiki/Using-pre-hook-post-hook-renew-hook-reloadcmd
for details.

- **Type**: `str`
- **Required**: No

#### `post_hook`<a id="variable-run_acmesh_certs-sub-post_hook"></a>

Optional. Command to execute after a successful certificate issuance or renewal. See
https://github.com/acmesh-official/acme.sh/wiki/Using-pre-hook-post-hook-renew-hook-reloadcmd
for details.

- **Type**: `str`
- **Required**: No

#### `renew_hook`<a id="variable-run_acmesh_certs-sub-renew_hook"></a>

Optional. Command to execute after renewing the certificate. See
https://github.com/acmesh-official/acme.sh/wiki/Using-pre-hook-post-hook-renew-hook-reloadcmd
for details.

- **Type**: `str`
- **Required**: No

#### `extra_flags`<a id="variable-run_acmesh_certs-sub-extra_flags"></a>

Optional. Additional CLI flags for edge cases. Useful for passing custom parameters during
certificate issuance wich are not natively supported by this role, just pass them as
"--foo --bar 'baz'".

- **Type**: `str`
- **Required**: No



### `run_acmesh_user`<a id="variable-run_acmesh_user"></a>

Specifies the service user account that runs acme.sh and owns relevant
files and directories.

- **Type**: `str`
- **Required**: Yes
- **Default**: `"acmesh"`



### `run_acmesh_group`<a id="variable-run_acmesh_group"></a>

Specifies the group associated with the service user for managing
acme.sh and its file permissions.

- **Type**: `str`
- **Required**: Yes
- **Default**: `"acmesh"`



### `run_acmesh_cfg_accountemail`<a id="variable-run_acmesh_cfg_accountemail"></a>

Specifies the email address to be associated with the ACME account.
This email is used for expiration notices and recovery purposes.
Some ACME providers might refuse to issue certificates if not set.

- **Type**: `str`
- **Required**: Yes
- **Default**: `""`



### `run_acmesh_cfg_home`<a id="variable-run_acmesh_cfg_home"></a>

Specifies the installation directory for the acme.sh software  (relates
to acme.sh option --home). Will also  be used as home directory of the
service user defined (see `run_acmesh_user``).

- **Type**: `str`
- **Required**: Yes
- **Default**: `"/opt/acme.sh"`



### `run_acmesh_cfg_config_home`<a id="variable-run_acmesh_cfg_config_home"></a>

Defines where configuration files are stored (relates to acme.sh option
--config-home).

- **Type**: `str`
- **Required**: Yes
- **Default**: `"/etc/acme.sh"`



### `run_acmesh_cfg_cert_home`<a id="variable-run_acmesh_cfg_cert_home"></a>

Specifies the directory where certificates are maintained by
acme.sh (relates to acme.sh option --certhome).
⚠️ Do not rely on the files in this directory directly. Instead, copy
the certificates where needed using the "install" key of `run_acmesh_certs`
(relates to acme.sh option --install-cert). This ensures that the
certificates are properly maintained and automatically reinstalled
upon renewal. See the following for more information:
https://github.com/acmesh-official/acme.sh/issues/2350#issuecomment-1449235599

- **Type**: `str`
- **Required**: Yes
- **Default**: `"/var/opt/acme.sh"`



### `run_acmesh_cfg_logfile`<a id="variable-run_acmesh_cfg_logfile"></a>

Path to the log file where acme.sh logs its operations (relates to acme.sh
option --log).

- **Type**: `str`
- **Required**: Yes
- **Default**: `"/var/log/acme.sh.log"`



### `run_acmesh_cfg_log_level`<a id="variable-run_acmesh_cfg_log_level"></a>

Specifies the log level (relates to acme.sh option --log-level).
Possible values are 1 (less logging) and 2 (more logging).

- **Type**: `int`
- **Required**: Yes
- **Default**: `1`
- **Choices**: `1`, `2`



### `run_acmesh_cfg_syslog`<a id="variable-run_acmesh_cfg_syslog"></a>

Specifies what to log (relates to acme.sh option --syslog).
Possible values are 0 (disable syslog), 3 (errors), 6 (info) and 7
(debug)

- **Type**: `int`
- **Required**: Yes
- **Default**: `3`
- **Choices**: `0`, `3`, `6`, `7`




<!-- END ANSIBLE DOCSMITH MAIN -->


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
              fullcain_file: "/etc/pki/tls/certs/example.org/fullchain.cer"
              key_file: "/etc/pki/tls/certs/example.org/cert.key"
              reloadcmd: "/bin/systemctl reload apache2.service"
            server: "letsencrypt_test" # optional, CA alias or URL, defaults to "letsencrypt" see https://github.com/acmesh-official/acme.sh/wiki/Server for details.
```


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
              fullcain_file: "/etc/pki/tls/certs/example.org/fullchain.cer"
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
              fullcain_file: "/etc/pki/tls/certs/foo.example.com/fullchain.cer"
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
          HETZNER_Token: "{{ lookup('ansible.builtin.unvault', '...') | string | trim }}"
          INWX_User: "exampleuser"
          INWX_Password: "{{ lookup('ansible.builtin.unvault', '...') | string | trim }}"
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



## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__run_acmesh_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

* **GitHub API access:** The role needs to be able to connect to GitHub API endpoint to fetch the latest acme.sh release information for upgrades (see `__run_acmesh_githubapi_release_latest_url` in [`vars/main.yml`](./vars/main.yml) for details).
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