# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Patch: Add German and French language support (2026-09-11).
Adds DE and FR to the languages table for existing installations.
"""

import sqlite3
from infrastructure.persistence.database_patches import DatabasePatches


@DatabasePatches.register("add_german_and_french_languages", version="1.0.0")
def patch_add_german_and_french_languages(conn: sqlite3.Connection) -> None:
    """Add German and French locale entries for installations created before those languages were introduced."""
    cursor = conn.cursor()

    for locale, name, logo in (
        ('DE', 'Deutsch', 'assets/images/language/de.png'),
        ('FR', 'Français', 'assets/images/language/fr.png'),
    ):
        cursor.execute("SELECT COUNT(*) FROM languages WHERE locale = ?", (locale,))
        exists = cursor.fetchone()[0] > 0
        if exists:
            continue

        cursor.execute(
            "SELECT MAX(display_order) FROM languages"
        )
        max_order_result = cursor.fetchone()
        max_order = max_order_result[0] if max_order_result and max_order_result[0] is not None else 0

        cursor.execute(
            """
            INSERT INTO languages (locale, name, logo_path, is_active, display_order)
            VALUES (?, ?, ?, ?, ?)
            """,
            (locale, name, logo, 1, max_order + 1)
        )

    conn.commit()
