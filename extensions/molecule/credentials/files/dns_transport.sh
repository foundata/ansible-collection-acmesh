#!/usr/bin/env sh
# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# Synthetic provider for the disposable Pebble DNS server only.

dns_transport_add() {
  TRANSPORT_TOKEN="${TRANSPORT_TOKEN:-$(_readaccountconf_mutable TRANSPORT_TOKEN)}"
  TRANSPORT_GLOBAL="${TRANSPORT_GLOBAL:-$(_readaccountconf_mutable TRANSPORT_GLOBAL)}"
  TRANSPORT_HASH="${TRANSPORT_HASH:-$(_readaccountconf_mutable TRANSPORT_HASH)}"
  TRANSPORT_GLOBAL_HASH="${TRANSPORT_GLOBAL_HASH:-$(_readaccountconf_mutable TRANSPORT_GLOBAL_HASH)}"
  TRANSPORT_NUMBER="${TRANSPORT_NUMBER:-$(_readaccountconf_mutable TRANSPORT_NUMBER)}"
  if [ "$(printf '%s' "$TRANSPORT_TOKEN" | sha256sum | cut -d ' ' -f 1)" != "$TRANSPORT_HASH" ] ||
     [ "$(printf '%s' "$TRANSPORT_GLOBAL" | sha256sum | cut -d ' ' -f 1)" != "$TRANSPORT_GLOBAL_HASH" ] ||
     [ "$TRANSPORT_NUMBER" != "17" ]; then
    return 1
  fi
  if [ "${TRANSPORT_FAIL:-}" = "1" ]; then
    # Deliberately hostile process output: Ansible must censor both streams.
    printf '%s\n' "$TRANSPORT_TOKEN"
    printf '%s\n' "$TRANSPORT_GLOBAL" >&2
    printf '%s' "$TRANSPORT_TOKEN" | base64 >&2
    return 1
  fi
  _saveaccountconf_mutable TRANSPORT_TOKEN "$TRANSPORT_TOKEN" 1
  _saveaccountconf_mutable TRANSPORT_GLOBAL "$TRANSPORT_GLOBAL" 1
  _saveaccountconf_mutable TRANSPORT_HASH "$TRANSPORT_HASH"
  _saveaccountconf_mutable TRANSPORT_GLOBAL_HASH "$TRANSPORT_GLOBAL_HASH"
  _saveaccountconf_mutable TRANSPORT_NUMBER "$TRANSPORT_NUMBER"
  curl --fail --silent --show-error --data "{\"host\":\"$1.\",\"value\":\"$2\"}" \
    http://127.0.0.1:8055/set-txt
}

dns_transport_rm() {
  curl --fail --silent --show-error --data "{\"host\":\"$1.\"}" \
    http://127.0.0.1:8055/clear-txt
}
