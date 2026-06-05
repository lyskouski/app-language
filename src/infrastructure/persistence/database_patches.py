# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Database patch registry and application system.
Provides the core patch management infrastructure.
"""

import sqlite3
from typing import Callable, Dict


class PatchMetadata:
    """Metadata for a database patch."""

    def __init__(self, name: str, func: Callable, version: str = "1.0.0"):
        self.name = name
        self.func = func
        self.version = version
        self.description = func.__doc__ or ""

    def __repr__(self) -> str:
        return f"PatchMetadata(name={self.name}, version={self.version})"


class DatabasePatches:
    """
    Universal patch registry and application system for database updates.

    This system allows patches to be registered via decorator and applied
    in order to existing installations. Tracks which patches have been applied
    to avoid re-execution.
    """

    _registry: Dict[str, PatchMetadata] = {}

    @classmethod
    def register(cls, name: str, version: str = "1.0.0") -> Callable:
        """
        Decorator to register a database patch.

        Args:
            name: Unique identifier for the patch
            version: Semantic version of the patch (default: "1.0.0")

        Returns:
            Decorator function

        Example:
            @DatabasePatches.register("add_polish_language", version="1.0.0")
            def patch_add_polish_language(conn: sqlite3.Connection) -> None:
                '''Add Polish language support.'''
                cursor = conn.cursor()
                # Apply patch
                conn.commit()
        """
        def decorator(func: Callable) -> Callable:
            cls._registry[name] = PatchMetadata(name, func, version)
            return func
        return decorator

    @classmethod
    def get_registry(cls) -> Dict[str, PatchMetadata]:
        """Get all registered patches."""
        return cls._registry.copy()

    @classmethod
    def _ensure_patches_table(cls, conn: sqlite3.Connection) -> None:
        """Ensure the patches tracking table exists."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_patches_applied (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patch_name TEXT UNIQUE NOT NULL,
                patch_version TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    @classmethod
    def _is_patch_applied(cls, conn: sqlite3.Connection, patch_name: str) -> bool:
        """Check if a patch has already been applied."""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM db_patches_applied WHERE patch_name = ?",
            (patch_name,)
        )
        return cursor.fetchone()[0] > 0

    @classmethod
    def _record_patch_applied(
        cls, conn: sqlite3.Connection, patch_name: str, version: str
    ) -> None:
        """Record that a patch has been applied."""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO db_patches_applied (patch_name, patch_version)
            VALUES (?, ?)
            """,
            (patch_name, version)
        )
        conn.commit()

    @classmethod
    def apply_all(cls, conn: sqlite3.Connection) -> None:
        """
        Apply all pending patches to the database.

        Patches are applied in registration order. Only patches that haven't
        been applied yet will be executed.

        Args:
            conn: SQLite database connection
        """
        # Ensure patches tracking table exists
        cls._ensure_patches_table(conn)

        # Get all registered patches in insertion order
        patches = cls._registry

        if not patches:
            return

        print(f"Checking {len(patches)} registered patches...")

        applied_count = 0
        for patch_name, patch_meta in patches.items():
            # Check if patch already applied
            if cls._is_patch_applied(conn, patch_name):
                print(f"  ⊘ Skipped (already applied): {patch_name} v{patch_meta.version}")
                continue

            try:
                # Apply the patch
                patch_meta.func(conn)
                # Record that it was applied
                cls._record_patch_applied(conn, patch_name, patch_meta.version)
                applied_count += 1
                print(f"  ✓ Applied: {patch_name} v{patch_meta.version}")
            except Exception as e:
                print(f"  ✗ Failed: {patch_name} - {e}")

        if applied_count > 0:
            print(f"Successfully applied {applied_count} patch(es)")
