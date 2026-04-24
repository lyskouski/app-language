#!/usr/bin/env python3
"""Verify SQLite database migration."""

import sqlite3

conn = sqlite3.connect('tlum.db')
c = conn.cursor()

print("=" * 60)
print("SQLite Database Migration Verification")
print("=" * 60)

# Count records
languages = c.execute('SELECT COUNT(*) FROM languages').fetchone()[0]
pairs = c.execute('SELECT COUNT(*) FROM language_pairs').fetchone()[0]
vocab = c.execute('SELECT COUNT(*) FROM vocabulary_items').fetchone()[0]

print(f"\n✓ Languages: {languages}")
print(f"✓ Language pairs: {pairs}")
print(f"✓ Vocabulary items: {vocab}")

# Show language pairs
print("\n📊 Language Pairs:")
for row in c.execute('''
    SELECT locale_from, locale_to, name 
    FROM language_pairs 
    ORDER BY name
''').fetchall():
    locale_from, locale_to, name = row
    count = c.execute('''
        SELECT COUNT(*) 
        FROM vocabulary_items 
        WHERE language_pair_id = (
            SELECT id FROM language_pairs 
            WHERE locale_from = ? AND locale_to = ?
        )
    ''', (locale_from, locale_to)).fetchone()[0]
    print(f"  {locale_from} -> {locale_to} ({name}): {count} items")

# Sample vocabulary
print("\n📖 Sample Vocabulary:")
for row in c.execute('''
    SELECT v.origin, v.translation, lp.locale_from, lp.locale_to
    FROM vocabulary_items v 
    JOIN language_pairs lp ON v.language_pair_id = lp.id 
    LIMIT 10
''').fetchall():
    origin, translation, locale_from, locale_to = row
    print(f"  {locale_from}->{locale_to}: {origin} → {translation}")

# Media statistics
print("\n🎵 Media Statistics:")
total = c.execute('SELECT COUNT(*) FROM vocabulary_items').fetchone()[0]
with_sound = c.execute('SELECT COUNT(*) FROM vocabulary_items WHERE sound_path IS NOT NULL AND sound_path != ""').fetchone()[0]
with_image = c.execute('SELECT COUNT(*) FROM vocabulary_items WHERE image_path IS NOT NULL AND image_path != ""').fetchone()[0]
print(f"  Total items: {total}")
print(f"  Items with sound: {with_sound}")
print(f"  Items with images: {with_image}")

# Sample items with media
print("\n🎬 Sample Items with Media:")
for row in c.execute('''
    SELECT origin, translation, sound_path, image_path 
    FROM vocabulary_items 
    WHERE sound_path IS NOT NULL AND sound_path != ""
    LIMIT 5
''').fetchall():
    origin, translation, sound, image = row
    print(f"  {origin} → {translation}")
    print(f"    🔊 {sound}")
    print(f"    🖼️ {image}")

print("\n" + "=" * 60)
print("✅ Verification complete!")
print("=" * 60)

conn.close()
