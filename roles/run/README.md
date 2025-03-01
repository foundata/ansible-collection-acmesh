# Ansible role: `foundata.acmesh.run`

The `foundata.acmesh.run` Ansible role (part if the `foundata.acmesh` Ansible collection).

Main features:

- Installation, configuration, and certificate files are stored in dedicated, configurable locations.
- Usage of a dedicated service user and group to own relevant resources.
- Supports multiple [challenge types](https://github.com/acmesh-official/acme.sh/wiki/How-to-issue-a-cert):
  - `alpn`, `dns` (including alias mode), `standalone`, and `webroot`.
- Global `acme.sh` shell alias for easy access.
- Automatic certificate renewal via cronjob.
- Supports uploading pre-seeded certificate files before issuing new ones, which helps prevent hitting CA rate limits when frequently reinstalling target systems during development.

Currently not supported:

- Apache and NGINX modes (however, you can use `extra_flags` to pass `--nginx` or `--apache` if necessary).
- The [notify feature](https://github.com/acmesh-official/acme.sh/wiki/notify).
- systemd timer instead of a cronjob (planned for a future release).



## Table of contents<a id="toc"></a>

- [Role variables](#variables)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Role variables<a id="variables"></a>

See [`defaults/main.yml`](./defaults/main.yml) for all available role parameters and their description. [`vars/main.yml`](./vars/main.yml) contains internal variables you should not override (but their description might be interesting).

Additionally, there are variables read from other roles and/or the global scope (for example, host or group vars) as follows:

- None right now.



## Example playbooks, using this role<a id="examples"></a>

Using only one domain per certificate an the webroot challenge:

```yaml
---

- name: "Initialize the foundata.acmesh.run role"
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
              reloadcmd: "systemctl reload apache2.service;"
            server: "zerossl" # optional, CA alias or URL, defaults to "letsencrypt" see https://github.com/acmesh-official/acme.sh/wiki/Server for details.

```

Multiple domains per certificate with DNS challenge and challenge alias:


```yaml
---

- name: "Initialize the foundata.acmesh.run role"
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
            server: "letsencrypt_test"
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

- name: "Initialize the foundata.acmesh.run role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.acmesh.run role"
      ansible.builtin.include_role:
        name: "foundata.acmesh.run"
      vars:
        run_acmesh_state: "absent"
```

This role can upload backed-up acme.sh certificate folders from the Ansible control node to target systems before issuing new certificates if the files do not already exist on the target (this prevents overwriting up-to-date certificates with old ones). This helps prevent CA rate limits, especially when frequently reinstalling target systems during development.<br>To use this feature, simply back up a directory such as `www.example.com_ecc` or `example.org_rsa` from acme.sh’s certificate home (defined by `run_acmesh_cfg_cert_home`, defaulting to `/var/opt/acme.sh`). Then, place the backup under `files/acme.sh/certhome` in your playbook directory on the control node.



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

The role needs to be able to connect to GitHub API endpoint to fetch the latest acme.sh release information (see `__run_acmesh_githubapi_release_latest_url` in [`vars/main.yml`](./vars/main.yml) for details).

Beside that, there are no special requirements not covered by Ansible itself.
