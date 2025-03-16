# Ansible Molecule: Testing this collections

This directory provides resources for testing the collection and its roles with [Molecule](https://ansible.readthedocs.io/projects/molecule/).


## Table of contents

- [Requirements](#requirements)
  - [Scenario `default`](#requirements-scenario-default)
- [Usage](#usage)
  - [Run tests](#usage-testing)
  - [Access instance terminal](#usage-instance-access)
  - [Write tests](#usage-add-tests)
- [FAQ, troubleshooting](#faq)
  - [Molecule role path detection issues](#faq-role-path-detection)
  - [Container: `inotify_init1(): Too many open files`](#faq-inotify)



## Requirements<a id="requirements"></a>

 See the official documentation on how to [install Molecule](https://ansible.readthedocs.io/projects/molecule/installation/#pip).

A typical Molecule scenario requires:

1. Access to container registries (quay.io, docker.io).
2. Standard OS package repositories.

If your environment does not provide internet access:

* Adjust the `platforms:` key in a scenario's `molecule.yml` to use alternative container registries.
* Add platform-specific preparation tasks in `resources/tasks/prepare/<platform-name|all>.yml` for adding tasks to adapt the testing infrastructure molecule creates, eg. add custom repositories.


### Scenario `default`<a id="requirements-scenario-default"></a>

1. [Podman](https://podman.io/docs/installation).
2. The Molecule [plugin](https://github.com/ansible-community/molecule-plugins) `podman`:
   ```bash
   pip install molecule[podman]
   ```


## Usage<a id="usage"></a>

### Run tests<a id="usage-testing"></a>

```bash
cd /path/to/collection/extensions
molecule test
molecule test --platform-name="molecule-debian12"  # Test single platform
molecule test --destroy=never  # Keep instances after testing
```



### Access instance terminal<a id="usage-instance-access"></a>

```bash
cd /path/to/collection
molecule list
molecule login --host <name>
```



### Write tests<a id="usage-add-tests"></a>

To add tests specific to your collection:

1. **Converge Tests** - Place task files in `./tasks/converge/`
   - Primarily role includes happen here to demonstrate functionality.
   - This step provides verification through Ansible's declarative approach and their failures on execution.
2. **Verification Tests** - Place task files in `./tasks/verify/`
   - Usually contains `ansible.builtin.assert` tasks for validating outcomes wich are not covered by task fails.
   - Focuses on confirming expected states and behaviors.

This file structure allows you to update your collection's `extensions/molecule` directory with the latest content from a [rendered `collection_default` skeleton](https://github.com/foundata/ansible-skeletons) without losing your collection-specific tests.


## FAQ, troubleshooting, FAQ<a id="faq"></a>

### Molecule role path detection issues<a id="faq-role-path-detection"></a>

If the roles of this collection are not found by Molecule, try the following"

1. Change into the collection's `extensions` directory.
2. Try to run molecule with an adjusted search pattern:
   ```bash
   MOLECULE_GLOB="./molecule/*/molecule.yml" molecule test
   ```

Further reading:

* https://github.com/ansible/molecule/issues/4015
* https://github.com/ansible/molecule/issues/4040
* https://github.com/ansible/molecule/issues/4061
* https://github.com/ansible/molecule/pull/4177



### Container: `inotify_init1(): Too many open files`<a id="faq-inotify"></a>

If you are not able to start all containers, you might need to increase `fs.inotify.max_user_instances` or do not run all containers in parallel (using `--platform-name=` parameter):

```bash
# inspect
sysctl fs.inotify

# adapt / test (runtime only)
echo 512 | sudo tee /proc/sys/fs/inotify/max_user_instances
echo 524288 | sudo tee /proc/sys/fs/inotify/max_user_watches

# adapt (persistent)
echo "fs.inotify.max_user_instances=512" | sudo tee -a /etc/sysctl.conf
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

It may help during debugging to manually start a container while you hit limits and inspect its logs:

```bash
# trigger resource limit
molecule test --destroy=never

# inspect
podman image
podman start <imageid> --log-level debug 2>&1 | grep -i -E "not|warn|err|deny|denie"
```
