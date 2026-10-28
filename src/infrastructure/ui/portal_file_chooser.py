# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
import secrets
import threading
from urllib.parse import unquote, urlparse

FLATPAK_INFO = '/.flatpak-info'


def is_available() -> bool:
    """Flatpak sandbox has no access to user files: they are picked via org.freedesktop.portal.FileChooser."""
    return os.path.exists(FLATPAK_INFO)


def open_file(title: str, callback, patterns=('*.json',)):
    """Ask for an existing file; callback receives its path or None (runs in a background thread)."""
    filters = ('a(sa(us))', [(', '.join(patterns), [(0, pattern) for pattern in patterns])])
    _request('OpenFile', title, {'filters': filters}, callback)


def save_file(title: str, current_name: str, callback):
    """Ask for a target file; callback receives its path or None (runs in a background thread)."""
    _request('SaveFile', title, {'current_name': ('s', current_name)}, callback)


def _request(method: str, title: str, options: dict, callback):
    threading.Thread(target=_run, args=(method, title, options, callback), daemon=True).start()


def _run(method: str, title: str, options: dict, callback):
    path = None
    try:
        from jeepney import DBusAddress, MatchRule, message_bus, new_method_call
        from jeepney.io.blocking import Proxy, open_dbus_connection
        from jeepney.wrappers import unwrap_msg

        with open_dbus_connection(bus='SESSION') as conn:
            # Subscribe to the Response signal before the call to not miss a quick answer
            token = f'tlum{secrets.token_hex(8)}'
            sender = conn.unique_name[1:].replace('.', '_')
            rule = MatchRule(
                type='signal',
                interface='org.freedesktop.portal.Request',
                member='Response',
                path=f'/org/freedesktop/portal/desktop/request/{sender}/{token}',
            )
            Proxy(message_bus, conn).AddMatch(rule)
            portal = DBusAddress(
                '/org/freedesktop/portal/desktop',
                bus_name='org.freedesktop.portal.Desktop',
                interface='org.freedesktop.portal.FileChooser',
            )
            with conn.filter(rule) as responses:
                options = {**options, 'handle_token': ('s', token)}
                unwrap_msg(conn.send_and_get_reply(new_method_call(portal, method, 'ssa{sv}', ('', title, options))))
                code, results = conn.recv_until_filtered(responses).body
            # 0: success, 1: cancelled by user, 2: other error
            if code == 0 and results.get('uris'):
                path = unquote(urlparse(results['uris'][1][0]).path)
    except Exception as e:
        print(f"Warning: File chooser portal is not available: {e}")
    callback(path)
