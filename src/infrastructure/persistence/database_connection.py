# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Database connection and management module.
Provides SQLite database connection with proper resource management.
"""

import sqlite3
import os
from typing import Optional
from contextlib import contextmanager
import threading


class DatabaseConnection:
    """
    Singleton database connection manager.
    Ensures single connection per thread and proper resource cleanup.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnection, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str):
        if self._initialized:
            return

        self.db_path = db_path
        self._local = threading.local()
        self._initialized = True

        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)

        # Initialize database schema
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema if not exists."""
        schema_path = os.path.join(os.path.dirname(__file__), 'database_schema.sql')

        with self.get_connection() as conn:
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                    conn.executescript(schema_sql)
            else:
                print(f"Warning: Database schema file not found: {schema_path}")

    def get_connection(self) -> sqlite3.Connection:
        """
        Get thread-local database connection.

        Returns:
            SQLite connection with row factory enabled
        """
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10.0
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            # Enable WAL mode for better concurrency
            self._local.connection.execute("PRAGMA journal_mode = WAL")

        return self._local.connection

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Usage:
            with db.transaction() as conn:
                conn.execute("INSERT ...")
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def execute(self, query: str, params=None) -> sqlite3.Cursor:
        """
        Execute a single query.

        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)

        Returns:
            Cursor with results
        """
        conn = self.get_connection()
        if params:
            return conn.execute(query, params)
        return conn.execute(query)

    def fetchone(self, query: str, params=None) -> Optional[sqlite3.Row]:
        """
        Fetch single row.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Single row or None
        """
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params=None) -> list:
        """
        Fetch all rows.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of rows
        """
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def close(self) -> None:
        """Close database connection."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')

    def __del__(self):
        """Cleanup on deletion."""
        self.close()


def get_database(db_path: Optional[str] = None) -> DatabaseConnection:
    """
    Factory function to get database instance.

    Args:
        db_path: Path to SQLite database file. If None, uses default.

    Returns:
        DatabaseConnection instance
    """
    if db_path is None:
        from kivy.app import App
        app = App.get_running_app()
        if app:
            db_path = os.path.join(app.user_data_dir, 'tlum.db')
        else:
            db_path = 'tlum.db'

    return DatabaseConnection(db_path)
