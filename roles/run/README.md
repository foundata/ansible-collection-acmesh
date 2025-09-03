# Ansible role: `foundata.acmesh.run`

The `foundata.acmesh.run` Ansible role (part if the `foundata.acmesh` Ansible collection). It provides automated management of ACME certificates using acme.sh.



## Table of contents<a id="toc"></a>

- [Features](#features)<!-- BEGIN ANSIBLE DOCSMITH TOC --><!-- END ANSIBLE DOCSMITH TOC -->
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

See [`defaults/main.yml`](./defaults/main.yml) for all available role parameters and their description. [`vars/main.yml`](./vars/main.yml) contains internal variables you should not override (but their description might be interesting).

Additionally, there are variables read from other roles and/or the global scope (for example, host or group vars) as follows:

- None right now.
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