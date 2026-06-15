# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Patch: Drop legacy BY locale (2026-06-15).
Force-removes BY locale from languages table.
"""

import sqlite3
from infrastructure.persistence.database_patches import DatabasePatches


@DatabasePatches.register("drop_legacy_by_locale", version="1.0.0")
def patch_drop_legacy_by_locale(conn: sqlite3.Connection) -> None:
    """
    Drop legacy BY locale from languages table.

    This patch is intentionally separate from earlier BY->BE migration so it can
    run even when previous patch metadata is already marked as applied.
    """
    cursor = conn.cursor()
    # Intentionally limited to languages table cleanup only.
    cursor.execute("DELETE FROM languages WHERE locale = 'BY'")

    conn.commit()
