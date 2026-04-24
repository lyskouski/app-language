# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from typing import List, Optional
from domain.entities.vocabulary_item import VocabularyItem
from domain.repositories.vocabulary_repository import IVocabularyRepository
from infrastructure.persistence.database_connection import DatabaseConnection


class SQLiteVocabularyRepository(IVocabularyRepository):
    """
    SQLite-based implementation of vocabulary repository.
    Replaces file-based storage with relational database.
    """

    def __init__(self, db_connection: DatabaseConnection):
        self._db = db_connection

    def _get_or_create_language_pair(self, locale_from: str, locale_to: str) -> int:
        """
        Get or create language pair ID.

        Args:
            locale_from: Source language locale
            locale_to: Target language locale

        Returns:
            Language pair ID
        """
        # Try to get existing
        row = self._db.fetchone(
            "SELECT id FROM language_pairs WHERE locale_from = ? AND locale_to = ?",
            (locale_from, locale_to)
        )

        if row:
            return row['id']

        # Create new
        cursor = self._db.execute(
            """INSERT INTO language_pairs (locale_from, locale_to, name)
               VALUES (?, ?, ?)""",
            (locale_from, locale_to, f"{locale_from}-{locale_to}")
        )
        self._db.get_connection().commit()
        return cursor.lastrowid

    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        """
        Load vocabulary items from file path.
        This extracts locale info from path and loads from database.

        Args:
            file_path: Path like 'assets/data/PL/EN/store.txt'

        Returns:
            List of vocabulary items
        """
        # Extract locale information from file path
        # e.g., "assets/data/PL/EN/store.txt" -> locale_to=PL, locale_from=EN
        locale_from, locale_to = self._extract_locales_from_path(file_path)

        if not locale_from or not locale_to:
            print(f"Warning: Could not extract locales from path: {file_path}")
            return []

        return self.load_by_language_pair(locale_from, locale_to)

    def _extract_locales_from_path(self, file_path: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract locale codes from file path.

        Args:
            file_path: Path like 'assets/data/PL/EN/store.txt'

        Returns:
            Tuple of (locale_from, locale_to)
        """
        try:
            parts = file_path.replace('\\', '/').split('/')
            if 'data' in parts:
                data_idx = parts.index('data')
                if len(parts) > data_idx + 2:
                    locale_to = parts[data_idx + 1]
                    locale_from = parts[data_idx + 2]
                    return (locale_from, locale_to)
        except Exception as e:
            print(f"Error extracting locales: {e}")

        return (None, None)

    def load_by_language_pair(self, locale_from: str, locale_to: str, category: Optional[str] = None) -> List[VocabularyItem]:
        """
        Load vocabulary items for a language pair, optionally filtered by category.

        Args:
            locale_from: Source language locale
            locale_to: Target language locale
            category: Optional category filter (verbs, articulation, dictionary, numbers)

        Returns:
            List of vocabulary items
        """
        if category:
            query = """
                SELECT v.id, v.origin, v.translation, v.sound_path, v.image_path, v.category
                FROM vocabulary_items v
                JOIN language_pairs lp ON v.language_pair_id = lp.id
                WHERE lp.locale_from = ? AND lp.locale_to = ? AND v.category = ?
                ORDER BY v.id
            """
            rows = self._db.fetchall(query, (locale_from, locale_to, category))
        else:
            query = """
                SELECT v.id, v.origin, v.translation, v.sound_path, v.image_path, v.category
                FROM vocabulary_items v
                JOIN language_pairs lp ON v.language_pair_id = lp.id
                WHERE lp.locale_from = ? AND lp.locale_to = ?
                ORDER BY v.id
            """
            rows = self._db.fetchall(query, (locale_from, locale_to))

        items = []
        for row in rows:
            try:
                item = VocabularyItem(
                    origin=row['origin'],
                    translation=row['translation'],
                    sound=row['sound_path'],
                    image=row['image_path'],
                    category=row['category'] if 'category' in row.keys() else None
                )
                items.append(item)
            except ValueError as e:
                print(f"Warning: Skipping invalid item: {e}")

        return items

    def save_to_file(self, file_path: str, items: List[VocabularyItem]) -> None:
        """
        Save vocabulary items to database.
        File path is used to determine language pair.

        Args:
            file_path: Path containing locale information
            items: List of vocabulary items to save
        """
        locale_from, locale_to = self._extract_locales_from_path(file_path)

        if not locale_from or not locale_to:
            print(f"Warning: Could not extract locales from path: {file_path}")
            return

        self.save_vocabulary_items(locale_from, locale_to, items)

    def save_vocabulary_items(
        self,
        locale_from: str,
        locale_to: str,
        items: List[VocabularyItem],
        replace: bool = True
    ) -> None:
        """
        Save vocabulary items for a language pair.

        Args:
            locale_from: Source language locale
            locale_to: Target language locale
            items: List of vocabulary items
            replace: If True, replace existing items; if False, append
        """
        try:
            with self._db.transaction() as conn:
                # Get or create language pair
                language_pair_id = self._get_or_create_language_pair(locale_from, locale_to)

                if replace:
                    # Delete existing items for this language pair
                    conn.execute(
                        "DELETE FROM vocabulary_items WHERE language_pair_id = ?",
                        (language_pair_id,)
                    )

                # Insert new items
                for item in items:
                    conn.execute(
                        """INSERT INTO vocabulary_items
                           (language_pair_id, origin, translation, sound_path, image_path, category)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            language_pair_id,
                            item.origin,
                            item.translation,
                            item.sound,
                            item.image,
                            item.category
                        )
                    )
        except Exception as e:
            print(f"Error saving vocabulary: {e}")
            raise

    def get_vocabulary_item_id(self, locale_from: str, locale_to: str, origin: str) -> Optional[int]:
        """
        Get vocabulary item ID by origin word.

        Args:
            locale_from: Source language locale
            locale_to: Target language locale
            origin: Origin word to search for

        Returns:
            Vocabulary item ID or None
        """
        query = """
            SELECT v.id
            FROM vocabulary_items v
            JOIN language_pairs lp ON v.language_pair_id = lp.id
            WHERE lp.locale_from = ? AND lp.locale_to = ? AND v.origin = ?
        """

        row = self._db.fetchone(query, (locale_from, locale_to, origin))
        return row['id'] if row else None
