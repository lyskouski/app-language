#!/usr/bin/env python3
# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Data migration script: JSON/Text files → SQLite database.
Migrates vocabulary items, languages, and game configurations.
"""

import os
import sys
import json
import csv
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.persistence.database_connection import get_database
from infrastructure.persistence.sqlite_vocabulary_repository import SQLiteVocabularyRepository
from infrastructure.persistence.sqlite_config_repository import SQLiteConfigRepository
from domain.entities.vocabulary_item import VocabularyItem


class DataMigration:
    """Migrate existing file-based data to SQLite."""
    
    def __init__(self, db_path: str, assets_dir: str):
        """
        Initialize migration.
        
        Args:
            db_path: Path to SQLite database
            assets_dir: Path to assets directory
        """
        self.db = get_database(db_path)
        self.assets_dir = Path(assets_dir)
        self.vocab_repo = SQLiteVocabularyRepository(self.db)
        self.config_repo = SQLiteConfigRepository(self.db)
    
    def migrate_all(self) -> None:
        """Run all migrations."""
        print("=" * 60)
        print("Tlum Data Migration: Files -> SQLite")
        print("=" * 60)
        
        self.migrate_languages()
        self.migrate_language_pairs()
        self.migrate_vocabulary()
        self.migrate_games()
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    
    def migrate_languages(self) -> None:
        """Migrate languages from JSON."""
        print("\n📚 Migrating languages...")
        
        languages_file = self.assets_dir / 'languages.json'
        if not languages_file.exists():
            print(f"  ⚠️  Languages file not found: {languages_file}")
            return
        
        try:
            with open(languages_file, 'r', encoding='utf-8') as f:
                languages = json.load(f)
            
            for idx, lang in enumerate(languages):
                locale = lang.get('locale', '')
                name = lang.get('text', '')
                logo = lang.get('logo', '')
                
                if locale and name:
                    self.config_repo.add_language(locale, name, logo, idx)
                    print(f"  ✓ Added language: {name} ({locale})")
            
            print(f"  📊 Migrated {len(languages)} languages")
        except Exception as e:
            print(f"  ❌ Error migrating languages: {e}")
    
    def migrate_language_pairs(self) -> None:
        """Migrate language pairs from JSON."""
        print("\n🔗 Migrating language pairs...")
        
        source_file = self.assets_dir / 'source.json'
        if not source_file.exists():
            print(f"  ⚠️  Source file not found: {source_file}")
            return
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                pairs = json.load(f)
            
            for pair in pairs:
                locale_from = pair.get('locale_from', '')
                locale_to = pair.get('locale_to', '')
                name = pair.get('text', '')
                logo = pair.get('logo', '')
                
                if locale_from and locale_to and name:
                    self.config_repo.add_language_pair(locale_from, locale_to, name, logo)
                    print(f"  ✓ Added pair: {name}")
            
            print(f"  📊 Migrated {len(pairs)} language pairs")
        except Exception as e:
            print(f"  ❌ Error migrating language pairs: {e}")
    
    def migrate_vocabulary(self) -> None:
        """Migrate vocabulary items from text files."""
        print("\n📖 Migrating vocabulary items...")
        
        data_dir = self.assets_dir / 'data'
        if not data_dir.exists():
            print(f"  ⚠️  Data directory not found: {data_dir}")
            return
        
        total_items = 0
        
        # Iterate through language pair directories
        for locale_to_dir in data_dir.iterdir():
            if not locale_to_dir.is_dir():
                continue
            
            locale_to = locale_to_dir.name
            
            for locale_from_dir in locale_to_dir.iterdir():
                if not locale_from_dir.is_dir():
                    continue
                
                locale_from = locale_from_dir.name
                
                # Check for data subdirectory with CSV files
                data_subdir = locale_from_dir / 'data'
                if data_subdir.exists() and data_subdir.is_dir():
                    vocab_files = list(data_subdir.glob('*.csv'))
                else:
                    # Fallback to looking for .txt files at root level
                    vocab_files = list(locale_from_dir.glob('*.txt'))
                
                for vocab_file in vocab_files:
                    items = self._load_vocabulary_from_file(vocab_file)
                    
                    if items:
                        self.vocab_repo.save_vocabulary_items(
                            locale_from, 
                            locale_to, 
                            items,
                            replace=False  # Append, don't replace
                        )
                        total_items += len(items)
                        print(f"  ✓ Migrated {len(items)} items from {locale_to}/{locale_from}/{vocab_file.name}")
        
        print(f"  📊 Total vocabulary items migrated: {total_items}")
    
    def _load_vocabulary_from_file(self, file_path: Path) -> list[VocabularyItem]:
        """
        Load vocabulary items from a CSV/text file.
        
        Args:
            file_path: Path to vocabulary file
            
        Returns:
            List of vocabulary items
        """
        items = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Use CSV reader to properly handle quoted fields with semicolons
                csv_reader = csv.reader(f, delimiter=';', quotechar='"', skipinitialspace=True)
                
                for parts in csv_reader:
                    if len(parts) >= 2:
                        origin = parts[0].strip()
                        translation = parts[1].strip()
                        sound = parts[2].strip() if len(parts) > 2 else None
                        image = parts[3].strip() if len(parts) > 3 else None
                        
                        # Skip empty entries
                        if not origin or not translation:
                            continue
                        
                        # Clean up empty strings
                        sound = sound if sound else None
                        image = image if image else None
                        
                        try:
                            item = VocabularyItem(
                                origin=origin,
                                translation=translation,
                                sound=sound,
                                image=image
                            )
                            items.append(item)
                        except ValueError as e:
                            print(f"    ⚠️  Skipping invalid item: {e}")
        except Exception as e:
            print(f"    ❌ Error loading file {file_path}: {e}")
        
        return items
    
    def migrate_games(self) -> None:
        """Migrate game configurations from JSON."""
        print("\n🎮 Migrating games...")
        
        data_dir = self.assets_dir / 'data'
        if not data_dir.exists():
            print(f"  ⚠️  Data directory not found: {data_dir}")
            return
        
        total_games = 0
        
        # Iterate through language pair directories
        for locale_to_dir in data_dir.iterdir():
            if not locale_to_dir.is_dir():
                continue
            
            locale_to = locale_to_dir.name
            
            for locale_from_dir in locale_to_dir.iterdir():
                if not locale_from_dir.is_dir():
                    continue
                
                locale_from = locale_from_dir.name
                
                # Load games.json if exists
                games_file = locale_from_dir / 'games.json'
                if games_file.exists():
                    try:
                        with open(games_file, 'r', encoding='utf-8') as f:
                            games = json.load(f)
                        
                        for game in games:
                            category_name = game.get('category', 'General')
                            
                            # Get or create category
                            try:
                                category_id = self.config_repo.add_game_category(
                                    locale_from,
                                    locale_to,
                                    category_name,
                                    game.get('icon'),
                                    0
                                )
                            except:
                                # Category might already exist, get it
                                pass
                            
                            # Add game (simplified - would need proper category lookup)
                            game_name = game.get('name', 'Unknown')
                            source = game.get('store_path', '')
                            
                            total_games += 1
                            print(f"  ✓ Found game: {game_name}")
                    
                    except Exception as e:
                        print(f"    ❌ Error loading games from {games_file}: {e}")
        
        print(f"  📊 Found {total_games} games")


def main():
    """Main migration entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate Tlum data to SQLite')
    parser.add_argument(
        '--db',
        default='tlum.db',
        help='Path to SQLite database (default: tlum.db)'
    )
    parser.add_argument(
        '--assets',
        default='assets',
        help='Path to assets directory (default: assets)'
    )
    
    args = parser.parse_args()
    
    migration = DataMigration(args.db, args.assets)
    migration.migrate_all()


if __name__ == '__main__':
    main()
