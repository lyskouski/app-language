# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import json
import os
from typing import Dict, Optional

from infrastructure.persistence.sqlite_vocabulary_repository import SQLiteVocabularyRepository
from infrastructure.persistence.sqlite_config_repository import SQLiteConfigRepository
from domain.entities.vocabulary_item import VocabularyItem

EXPORT_FORMAT_VERSION = '1.0'


class LanguagePairIOService:
    """
    Application service for exporting and importing language pairs (categories + vocabulary).

    Export format (JSON):
    {
        "version": "1.0",
        "locale_from": "EN",
        "locale_to": "PL",
        "name": "EN-PL (English - Polish)",
        "logo_path": "",
        "categories": [
            {
                "name": "verbs",
                "vocabulary_source": "verbs",
                "icon_path": "",
                "display_order": 0
            }
        ],
        "vocabulary": [
            {
                "origin": "hello",
                "translation": "cześć",
                "sound_path": null,
                "image_path": null,
                "category": "verbs",
                "difficulty_level": 1
            }
        ]
    }
    """

    def __init__(
        self,
        vocab_repo: SQLiteVocabularyRepository,
        config_repo: SQLiteConfigRepository,
    ):
        self._vocab_repo = vocab_repo
        self._config_repo = config_repo

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_language_pair(self, locale_from: str, locale_to: str, file_path: str) -> int:
        """
        Export a language pair with all its categories and vocabulary to a JSON file.

        Args:
            locale_from: Source language locale (e.g. 'EN')
            locale_to:   Target language locale (e.g. 'PL')
            file_path:   Destination file path for the exported JSON

        Returns:
            Number of vocabulary items exported

        Raises:
            ValueError: If the language pair does not exist
            OSError: If the file cannot be written
        """
        pair = self._config_repo.get_language_pair(locale_from, locale_to)
        if pair is None:
            raise ValueError(f"Language pair {locale_from}-{locale_to} not found")

        categories_raw = self._config_repo.get_dictionaries_for_language_pair(locale_from, locale_to)
        categories = [
            {
                'name': cat['category_name'],
                'vocabulary_source': cat['vocabulary_source'],
                'icon_path': cat.get('logo', ''),
                'display_order': 0,
            }
            for cat in categories_raw
        ]

        vocabulary_items = self._vocab_repo.load_by_language_pair(locale_from, locale_to)
        vocabulary = [
            {
                'origin': item.origin,
                'translation': item.translation,
                'sound_path': item.sound,
                'image_path': item.image,
                'category': item.category,
                'difficulty_level': 1,
            }
            for item in vocabulary_items
        ]

        payload: Dict = {
            'version': EXPORT_FORMAT_VERSION,
            'locale_from': locale_from,
            'locale_to': locale_to,
            'name': pair.get('text', f'{locale_from}-{locale_to}'),
            'logo_path': pair.get('logo', ''),
            'categories': categories,
            'vocabulary': vocabulary,
        }

        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

        return len(vocabulary)

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def import_language_pair(self, file_path: str, merge: bool = False) -> Dict:
        """
        Import a language pair from a JSON file exported by this service.

        Args:
            file_path: Path to the JSON file
            merge:     If True, append vocabulary instead of replacing existing items.
                       Categories are always upserted.

        Returns:
            Dict with keys: locale_from, locale_to, categories_imported, vocabulary_imported

        Raises:
            ValueError: If the file format is invalid
            FileNotFoundError: If the file does not exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Import file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as fh:
            payload = json.load(fh)

        self._validate_payload(payload)

        locale_from = payload['locale_from'].strip().upper()
        locale_to = payload['locale_to'].strip().upper()
        name = payload.get('name', f'{locale_from}-{locale_to}')
        logo_path = payload.get('logo_path') or None

        # Ensure the language pair exists
        pair = self._config_repo.get_language_pair(locale_from, locale_to)
        if pair is None:
            self._config_repo.add_language_pair(locale_from, locale_to, name, logo_path)

        # Upsert categories
        categories = payload.get('categories', [])
        for cat in categories:
            self._upsert_category(locale_from, locale_to, cat)

        # Import vocabulary
        vocab_items = [
            VocabularyItem(
                origin=v['origin'],
                translation=v['translation'],
                sound=v.get('sound_path'),
                image=v.get('image_path'),
                category=v.get('category'),
            )
            for v in payload.get('vocabulary', [])
        ]

        if vocab_items:
            self._vocab_repo.save_vocabulary_items(
                locale_from,
                locale_to,
                vocab_items,
                replace=not merge,
            )

        return {
            'locale_from': locale_from,
            'locale_to': locale_to,
            'categories_imported': len(categories),
            'vocabulary_imported': len(vocab_items),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_payload(self, payload: Dict) -> None:
        required = {'locale_from', 'locale_to'}
        missing = required - set(payload.keys())
        if missing:
            raise ValueError(f"Invalid import file: missing fields {missing}")

    def _upsert_category(self, locale_from: str, locale_to: str, cat: Dict) -> None:
        """Insert category if it does not already exist for this language pair."""
        pair_row = self._config_repo._db.fetchone(
            "SELECT id FROM language_pairs WHERE locale_from = ? AND locale_to = ?",
            (locale_from, locale_to),
        )
        if pair_row is None:
            return
        pair_id = pair_row['id']

        existing = self._config_repo._db.fetchone(
            "SELECT id FROM game_categories WHERE language_pair_id = ? AND category_name = ?",
            (pair_id, cat['name']),
        )
        if existing:
            return

        self._config_repo._db.execute(
            """INSERT INTO game_categories
               (language_pair_id, category_name, vocabulary_source, icon_path, display_order, is_active)
               VALUES (?, ?, ?, ?, ?, 1)""",
            (
                pair_id,
                cat['name'],
                cat.get('vocabulary_source', cat['name']),
                cat.get('icon_path', '') or None,
                cat.get('display_order', 0),
            ),
        )
        self._config_repo._db.get_connection().commit()
