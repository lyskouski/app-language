# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Patch: Add Polish language support (2026-05-06).
Adds Polish (PL) to the languages table for existing installations.
"""

import sqlite3
from infrastructure.persistence.database_patches import DatabasePatches


@DatabasePatches.register("add_polish_language", version="1.0.0")
def patch_add_polish_language(conn: sqlite3.Connection) -> None:
    """
    Add Polish language to languages table for existing installations.

    This patch adds Polish (PL) to the languages table if it doesn't already exist.
    Applies only to databases that were created before Polish support was added.
    """
    cursor = conn.cursor()

    # Check if languages table exists and Polish is not present
    cursor.execute(
        "SELECT COUNT(*) FROM languages WHERE locale = 'PL'"
    )
    polish_exists = cursor.fetchone()[0] > 0

    if not polish_exists:
        # Get the current max display_order to insert Polish with the next order
        cursor.execute("SELECT MAX(display_order) FROM languages")
        max_order_result = cursor.fetchone()
        max_order = max_order_result[0] if max_order_result[0] is not None else 0
        next_order = max_order + 1

        # Insert Polish language
        cursor.execute(
            """
            INSERT INTO languages (locale, name, logo_path, is_active, display_order)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                'PL',
                'Polski',
                'assets/images/language/pl.png',
                1,
                next_order
            )
        )
        conn.commit()
