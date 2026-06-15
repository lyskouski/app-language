# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Patch: Replace Belarusian locale BY with BE (2026-06-15).
Migrates existing databases from legacy locale code BY to BE.
"""

import sqlite3
from infrastructure.persistence.database_patches import DatabasePatches


@DatabasePatches.register("replace_belarusian_locale_by_to_be", version="1.0.0")
def patch_replace_belarusian_locale_by_to_be(conn: sqlite3.Connection) -> None:
    """
    Replace legacy Belarusian locale BY with BE.

    This patch updates:
    - languages.locale (BY -> BE)
    - language_pairs.locale_from / locale_to (BY -> BE)

    The patch is idempotent and safely handles duplicate BY/BE language pairs
    by merging linked content into the BE pair before removing the BY pair.
    """
    cursor = conn.cursor()

    # Ensure BE language exists or convert BY language row to BE.
    cursor.execute("SELECT id, is_active, display_order FROM languages WHERE locale = 'BE'")
    be_row = cursor.fetchone()

    cursor.execute("SELECT id, name, logo_path, is_active, display_order FROM languages WHERE locale = 'BY'")
    by_row = cursor.fetchone()

    if by_row:
        by_id, by_name, _by_logo, by_active, by_order = by_row

        if be_row:
            be_id, be_active, be_order = be_row

            merged_active = 1 if (be_active or by_active) else 0
            merged_order = min(
                be_order if be_order is not None else by_order,
                by_order if by_order is not None else be_order,
            )

            cursor.execute(
                """
                UPDATE languages
                SET name = ?, logo_path = ?, is_active = ?, display_order = ?
                WHERE id = ?
                """,
                (
                    by_name or "Беларуская",
                    "assets/images/language/be.png",
                    merged_active,
                    merged_order if merged_order is not None else 0,
                    be_id,
                ),
            )
            cursor.execute("DELETE FROM languages WHERE id = ?", (by_id,))
        else:
            cursor.execute(
                """
                UPDATE languages
                SET locale = 'BE', logo_path = ?
                WHERE id = ?
                """,
                ("assets/images/language/be.png", by_id),
            )

    # Merge pairs where both BY and BE versions exist.
    cursor.execute(
        """
        SELECT old_lp.id AS old_id, new_lp.id AS new_id
        FROM language_pairs old_lp
        JOIN language_pairs new_lp
          ON (
            (old_lp.locale_from = 'BY' AND new_lp.locale_from = 'BE' AND old_lp.locale_to = new_lp.locale_to)
            OR
            (old_lp.locale_to = 'BY' AND new_lp.locale_to = 'BE' AND old_lp.locale_from = new_lp.locale_from)
          )
        """
    )
    pair_remaps = cursor.fetchall()

    for old_id, new_id in pair_remaps:
        # Move vocabulary rows to BE pair.
        cursor.execute(
            """
            UPDATE vocabulary_items
            SET language_pair_id = ?
            WHERE language_pair_id = ?
            """,
            (new_id, old_id),
        )

        # Merge game categories without violating unique(language_pair_id, category_name).
        cursor.execute(
            """
            INSERT OR IGNORE INTO game_categories (
                language_pair_id,
                category_name,
                vocabulary_source,
                icon_path,
                display_order,
                is_active
            )
            SELECT ?, category_name, vocabulary_source, icon_path, display_order, is_active
            FROM game_categories
            WHERE language_pair_id = ?
            """,
            (new_id, old_id),
        )
        cursor.execute(
            "DELETE FROM game_categories WHERE language_pair_id = ?",
            (old_id,),
        )

        cursor.execute("DELETE FROM language_pairs WHERE id = ?", (old_id,))

    # Convert any remaining BY pair references directly.
    cursor.execute(
        """
        UPDATE language_pairs
        SET locale_from = 'BE'
        WHERE locale_from = 'BY'
          AND NOT EXISTS (
            SELECT 1
            FROM language_pairs lp2
            WHERE lp2.locale_from = 'BE' AND lp2.locale_to = language_pairs.locale_to
          )
        """
    )
    cursor.execute(
        """
        UPDATE language_pairs
        SET locale_to = 'BE'
        WHERE locale_to = 'BY'
          AND NOT EXISTS (
            SELECT 1
            FROM language_pairs lp2
            WHERE lp2.locale_to = 'BE' AND lp2.locale_from = language_pairs.locale_from
          )
        """
    )

    conn.commit()
