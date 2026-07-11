# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for SQLiteConfigRepository validations."""

import pytest

from infrastructure.persistence.database_connection import DatabaseConnection
from infrastructure.persistence.sqlite_config_repository import SQLiteConfigRepository


class TestSQLiteConfigRepository:
    """Test SQLite-based config repository."""

    @pytest.fixture
    def db_connection(self, tmp_path):
        """Create a temporary database connection for testing."""
        db_path = str(tmp_path / "test_tlum.db")
        return DatabaseConnection(db_path)

    @pytest.fixture
    def repository(self, db_connection):
        """Create a repository instance for testing."""
        return SQLiteConfigRepository(db_connection)

    def test_add_language_pair_rejects_duplicate(self, repository):
        """Test adding the same language pair twice is rejected."""
        repository.add_language_pair("EN", "PL", "EN-PL")

        with pytest.raises(ValueError, match="Language pair already exists"):
            repository.add_language_pair("en", "pl", "EN-PL duplicate")

    def test_add_game_category_rejects_duplicate_name_for_same_pair(self, repository):
        """Test category name uniqueness is enforced per language pair."""
        repository.add_language_pair("EN", "PL", "EN-PL")
        repository.add_game_category("EN", "PL", "Verbs", "verbs")

        with pytest.raises(ValueError, match="Category already exists"):
            repository.add_game_category("EN", "PL", "  verbs  ", "verbs")
