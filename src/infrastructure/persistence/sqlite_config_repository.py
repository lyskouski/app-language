# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Static configuration repository for languages, games, and learning paths.
Replaces JSON file-based configuration with SQLite storage.
"""

from typing import List, Dict, Optional
from infrastructure.persistence.database_connection import DatabaseConnection


class SQLiteConfigRepository:
    """
    Repository for static application configuration.
    Handles languages, language pairs, and game configurations.
    """

    def __init__(self, db_connection: DatabaseConnection):
        self._db = db_connection

    # ===== Language Management =====

    def get_all_languages(self) -> List[Dict]:
        """
        Get all available languages.

        Returns:
            List of language dictionaries
        """
        rows = self._db.fetchall(
            """SELECT locale, name, logo_path, is_active, display_order
               FROM languages
               WHERE is_active = 1
               ORDER BY display_order, name"""
        )

        return [
            {
                'locale': row['locale'],
                'text': row['name'],
                'logo': row['logo_path']
            }
            for row in rows
        ]

    def add_language(self, locale: str, name: str, logo_path: str, display_order: int = 0) -> None:
        """
        Add a new language.

        Args:
            locale: Language locale code (e.g., 'EN', 'PL')
            name: Display name
            logo_path: Path to language logo image
            display_order: Sort order for display
        """
        try:
            self._db.execute(
                """INSERT OR REPLACE INTO languages
                   (locale, name, logo_path, display_order, is_active)
                   VALUES (?, ?, ?, ?, 1)""",
                (locale, name, logo_path, display_order)
            )
            self._db.get_connection().commit()
        except Exception as e:
            print(f"Error adding language: {e}")

    # ===== Language Pair Management =====

    def get_all_language_pairs(self) -> List[Dict]:
        """
        Get all available language pairs.

        Returns:
            List of language pair dictionaries
        """
        rows = self._db.fetchall(
            """SELECT id, locale_from, locale_to, name, logo_path
               FROM language_pairs
               ORDER BY name"""
        )

        return [
            {
                'locale_from': row['locale_from'],
                'locale_to': row['locale_to'],
                'text': row['name'],
                'logo': row['logo_path'],
                'source': f"assets/data/{row['locale_to']}/{row['locale_from']}/source.json",
                'store_path': '',
                'route_path': ''
            }
            for row in rows
        ]

    def get_language_pair(self, locale_from: str, locale_to: str) -> Optional[Dict]:
        """
        Get a specific language pair.

        Args:
            locale_from: Source language locale
            locale_to: Target language locale

        Returns:
            Language pair dictionary or None
        """
        row = self._db.fetchone(
            """SELECT id, locale_from, locale_to, name, logo_path
               FROM language_pairs
               WHERE locale_from = ? AND locale_to = ?""",
            (locale_from, locale_to)
        )

        if not row:
            return None

        return {
            'locale_from': row['locale_from'],
            'locale_to': row['locale_to'],
            'text': row['name'],
            'logo': row['logo_path'],
            'source': f"assets/data/{row['locale_to']}/{row['locale_from']}/source.json"
        }

    def add_language_pair(
        self,
        locale_from: str,
        locale_to: str,
        name: str,
        logo_path: Optional[str] = None
    ) -> int:
        """
        Add a new language pair.

        Args:
            locale_from: Source language locale
            locale_to: Target language locale
            name: Display name (e.g., "EN-PL (English - Polish)")
            logo_path: Optional path to logo image

        Returns:
            Language pair ID
        """
        try:
            cursor = self._db.execute(
                """INSERT OR REPLACE INTO language_pairs
                   (locale_from, locale_to, name, logo_path)
                   VALUES (?, ?, ?, ?)""",
                (locale_from, locale_to, name, logo_path)
            )
            self._db.get_connection().commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding language pair: {e}")
            raise

    # ===== Game Configuration Management =====

    def get_dictionaries_for_language_pair(self, locale_from: str, locale_to: str) -> List[Dict]:
        """
        Get all dictionaries/categories for a language pair.
        This is the second navigation level (after selecting a language pair).

        Args:
            locale_from: Source language locale
            locale_to: Target language locale

        Returns:
            List of dictionary/category dictionaries
        """
        query = """
            SELECT gc.id, gc.category_name, gc.icon_path, gc.display_order
            FROM game_categories gc
            JOIN language_pairs lp ON gc.language_pair_id = lp.id
            WHERE lp.locale_from = ? AND lp.locale_to = ? AND gc.is_active = 1
            ORDER BY gc.display_order, gc.category_name
        """

        rows = self._db.fetchall(query, (locale_from, locale_to))

        return [
            {
                'id': row['id'],
                'text': row['category_name'],
                'logo': row['icon_path'] or '',
                'source': f"category_{row['id']}",  # Used for navigation
                'store_path': '',
                'route_path': '',
                'locale_from': locale_from,
                'locale_to': locale_to,
                'category_id': str(row['id']),  # For Add button
                'category_name': row['category_name']  # For pre-filling form
            }
            for row in rows
        ]

    def get_games_for_category(self, category_id: int) -> List[Dict]:
        """
        Get all game modes for a specific dictionary/category.
        This is the third navigation level (after selecting a dictionary).

        Args:
            category_id: Category ID

        Returns:
            List of game configuration dictionaries
        """
        query = """
            SELECT g.id, g.game_name, g.description, g.vocabulary_source,
                   g.icon_path, g.route_screen, gc.category_name
            FROM games g
            JOIN game_categories gc ON g.category_id = gc.id
            WHERE g.category_id = ? AND g.is_active = 1
            ORDER BY g.display_order, g.game_name
        """

        rows = self._db.fetchall(query, (category_id,))

        return [
            {
                'text': row['game_name'],
                'description': row['description'],
                'source': row['vocabulary_source'] or '',
                'logo': row['icon_path'] or '',
                'store_path': row['vocabulary_source'] or 'all',  # For vocabulary loading
                'route_path': row['route_screen'] or 'card_screen',  # Screen to navigate to
                'vocab_filter': row['vocabulary_source'] or 'all'
            }
            for row in rows
        ]

    def get_games_for_language_pair(self, locale_from: str, locale_to: str) -> List[Dict]:
        """
        Get all games for a language pair.

        Args:
            locale_from: Source language locale
            locale_to: Target language locale

        Returns:
            List of game configuration dictionaries
        """
        query = """
            SELECT g.id, g.game_name, g.description, g.vocabulary_source,
                   g.icon_path, gc.category_name
            FROM games g
            JOIN game_categories gc ON g.category_id = gc.id
            JOIN language_pairs lp ON gc.language_pair_id = lp.id
            WHERE lp.locale_from = ? AND lp.locale_to = ? AND g.is_active = 1
            ORDER BY gc.display_order, g.display_order
        """

        rows = self._db.fetchall(query, (locale_from, locale_to))

        return [
            {
                'name': row['game_name'],
                'description': row['description'],
                'source': row['vocabulary_source'],
                'icon': row['icon_path'],
                'category': row['category_name']
            }
            for row in rows
        ]

    def add_game_category(
        self,
        locale_from: str,
        locale_to: str,
        category_name: str,
        icon_path: Optional[str] = None,
        display_order: int = 0
    ) -> int:
        """
        Add a game category for a language pair.

        Args:
            locale_from: Source language locale
            locale_to: Target language locale
            category_name: Category name
            icon_path: Optional icon path
            display_order: Display order

        Returns:
            Category ID
        """
        # Get language pair ID
        row = self._db.fetchone(
            "SELECT id FROM language_pairs WHERE locale_from = ? AND locale_to = ?",
            (locale_from, locale_to)
        )

        if not row:
            raise ValueError(f"Language pair not found: {locale_from}-{locale_to}")

        language_pair_id = row['id']

        try:
            cursor = self._db.execute(
                """INSERT INTO game_categories
                   (language_pair_id, category_name, icon_path, display_order)
                   VALUES (?, ?, ?, ?)""",
                (language_pair_id, category_name, icon_path, display_order)
            )
            self._db.get_connection().commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding game category: {e}")
            raise

    def add_game(
        self,
        category_id: int,
        game_name: str,
        vocabulary_source: str,
        description: Optional[str] = None,
        icon_path: Optional[str] = None,
        display_order: int = 0
    ) -> int:
        """
        Add a game to a category.

        Args:
            category_id: Game category ID
            game_name: Game name
            vocabulary_source: Path to vocabulary data
            description: Optional description
            icon_path: Optional icon path
            display_order: Display order

        Returns:
            Game ID
        """
        try:
            cursor = self._db.execute(
                """INSERT INTO games
                   (category_id, game_name, description, vocabulary_source,
                    icon_path, display_order)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (category_id, game_name, description, vocabulary_source,
                 icon_path, display_order)
            )
            self._db.get_connection().commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding game: {e}")
            raise
