# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Patch: Add international interface languages (2026-10-21).
Adds PT-PT, PT-BR, ES, IT, NL, CS, RO, TR, AZ, UZ, ID, ZH-CN, ZH-TW, JA, KO, HI, FA, AR and KA
to the languages table for existing installations.
"""

import sqlite3
from infrastructure.persistence.database_patches import DatabasePatches

LANGUAGES = (
    ('PT-PT', 'Português (Portugal)', 'assets/images/language/pt_pt.png'),
    ('PT-BR', 'Português (Brasil)', 'assets/images/language/pt_br.png'),
    ('ES', 'Español', 'assets/images/language/es.png'),
    ('IT', 'Italiano', 'assets/images/language/it.png'),
    ('NL', 'Nederlands', 'assets/images/language/nl.png'),
    ('CS', 'Čeština', 'assets/images/language/cs.png'),
    ('RO', 'Română', 'assets/images/language/ro.png'),
    ('TR', 'Türkçe', 'assets/images/language/tr.png'),
    ('AZ', 'Azərbaycan dili', 'assets/images/language/az.png'),
    ('UZ', 'Oʻzbekcha', 'assets/images/language/uz.png'),
    ('ID', 'Bahasa Indonesia', 'assets/images/language/id.png'),
    ('ZH-CN', '简体中文', 'assets/images/language/zh_cn.png'),
    ('ZH-TW', '繁體中文', 'assets/images/language/zh_tw.png'),
    ('JA', '日本語', 'assets/images/language/ja.png'),
    ('KO', '한국어', 'assets/images/language/ko.png'),
    ('HI', 'हिन्दी', 'assets/images/language/hi.png'),
    ('FA', 'فارسی', 'assets/images/language/fa.png'),
    ('AR', 'العربية', 'assets/images/language/ar.png'),
    ('KA', 'ქართული', 'assets/images/language/ka.png'),
)


@DatabasePatches.register("add_international_languages", version="1.0.0")
def patch_add_international_languages(conn: sqlite3.Connection) -> None:
    """Add locale entries for installations created before those languages were introduced."""
    cursor = conn.cursor()

    for locale, name, logo in LANGUAGES:
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
