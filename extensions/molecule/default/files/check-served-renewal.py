# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise real ACME renewal, atomic publication and NGINX's served TLS serial."""

import os
import socket
import ssl
import subprocess
import sys
import time
from pathlib import Path


def command(*args, **kwargs):
    try:
        return subprocess.run(
            args, check=True, capture_output=True, timeout=120, **kwargs
        ).stdout
    except subprocess.CalledProcessError as error:
        print(error.stdout.decode(errors="replace"))
        print(error.stderr.decode(errors="replace"))
        raise


def served():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with socket.create_connection(("127.0.0.1", 8443), timeout=5) as connection:
        with context.wrap_socket(
            connection, server_hostname="acmesh-webroot.test"
        ) as tls:
            cert = tls.getpeercert(binary_form=True)
    return command(
        "openssl", "x509", "-inform", "DER", "-serial", "-noout", input=cert
    ).strip()


def reload_stamp():
    # The configured command writes this marker on every invocation. systemd
    # may unload an inactive oneshot and discard its execution timestamp.
    return Path("/var/tmp/acmesh-reload-webroot-marker").stat().st_mtime_ns


def main():
    home, config, cert_home, user = sys.argv[1:]
    cert = Path("/etc/pki/tls/certs/acmesh-webroot.test/fullchain.cer")
    before = served()
    inode = cert.stat().st_ino
    print("Served before renewal:", before.decode())
    command(
        "runuser",
        "-u",
        user,
        "--",
        str(Path(home) / "acme.sh"),
        "--renew",
        "--force",
        "--ecc",
        "--domain",
        "acmesh-webroot.test",
        "--config-home",
        config,
        "--certhome",
        cert_home,
        # Pebble may reject ARI replacement IDs on repeated forced renewals.
        env={**os.environ, "HOME": home, "NO_ARI": "1"},
        cwd=home,
    )
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        after = served()
        disk = command("openssl", "x509", "-in", str(cert), "-serial", "-noout").strip()
        if after != before and after == disk:
            break
        time.sleep(0.5)
    else:
        raise AssertionError("NGINX did not serve the renewed certificate")
    assert cert.stat().st_ino != inode, "Publication did not replace the inode"
    print("Served after renewal:", after.decode())
    # Starting the service waits for any path-triggered publication to complete.
    unit = "acmesh-deploy-acmesh-webroot.test.service"
    command("systemctl", "start", unit)
    stamp = reload_stamp()
    cert.chmod(0o600)
    command("systemctl", "start", unit)
    assert cert.stat().st_mode & 0o777 == 0o644
    assert reload_stamp() == stamp, "Metadata-only deployment reloaded NGINX"
    command("systemctl", "start", unit)
    assert reload_stamp() == stamp, "No-op deployment reloaded NGINX"
    assert served() == after
    print("Metadata-only and no-op deployments preserved the reload timestamp")

    # The preceding rapid starts must not consume the fault test's start limit.
    command("systemctl", "reset-failed", unit)
    # Fault injection stays in a dedicated drop-in and is always removed.
    dropin_dir = Path("/etc/systemd/system/acmesh-reload-acmesh-webroot.test.service.d")
    dropin_dir.mkdir(exist_ok=True)
    dropin = dropin_dir / "99-molecule-failure.conf"
    pending = Path("/var/lib/acmesh-deploy/acmesh-webroot.test/reload-pending")
    try:
        dropin.write_text("[Service]\nExecStart=\nExecStart=/bin/false\n")
        command("systemctl", "daemon-reload")
        cert.write_bytes(cert.read_bytes() + b"\n")
        failed = subprocess.run(
            ["systemctl", "start", unit], check=False, capture_output=True, timeout=120
        )
        assert failed.returncode != 0 and pending.exists()
        assert b"Result=exit-code" in command(
            "systemctl", "show", unit, "--property=Result"
        )
        published_inode = cert.stat().st_ino
    finally:
        dropin.unlink()
        dropin_dir.rmdir()
        command("systemctl", "daemon-reload")
    command("systemctl", "start", unit)
    assert not pending.exists() and cert.stat().st_ino == published_inode
    assert reload_stamp() != stamp and served() == after
    print("Failed reload remained visible and retried without republishing")


if __name__ == "__main__":
    main()
