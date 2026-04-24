# SQLite Migration - Implementation Status

## 📋 Overview

This document tracks the migration from file-based storage (JSON/CSV/text files) to SQLite database for the Tlum vocabulary learning application.

## ✅ Completed Components

### 1. Database Infrastructure ✓

**Files Created:**
- `src/infrastructure/persistence/database_schema.sql` - Complete SQLite schema with tables for:
  - `language_pairs` - Language pair configurations
  - `vocabulary_items` - Vocabulary data with foreign keys
  - `learning_progress` - User study history and difficulty scores
  - `ml_embeddings` - Character embeddings cache
  - `languages` - Available languages
  - `game_categories` & `games` - Game configurations
  - `db_metadata` - Database versioning

- `src/infrastructure/persistence/database_connection.py` - Thread-safe connection manager with:
  - Singleton pattern per thread
  - Transaction context manager
  - Auto-initialization of schema
  - WAL mode for concurrency
  - Foreign key enforcement

### 2. Repository Implementations ✓

**Vocabulary Repository:**
- `src/infrastructure/persistence/sqlite_vocabulary_repository.py`
  - Implements `IVocabularyRepository` interface
  - Replaces `FileVocabularyRepository`
  - Methods:
    - `load_from_file()` - Extracts locales from path, loads from DB
    - `load_by_language_pair()` - Direct DB query by locales
    - `save_vocabulary_items()` - Batch insert with transaction
    - `get_vocabulary_item_id()` - Helper for profiler

**ML Profiler:**
- `src/infrastructure/ml/sqlite_ml_vocabulary_profiler.py`
  - Implements `IVocabularyProfiler` interface
  - Replaces `MLVocabularyProfiler` (JSON/pickle)
  - Stores:
    - Learning progress in `learning_progress` table
    - Character embeddings in `ml_embeddings` table
  - Methods:
    - `mark_positive()` / `mark_negative()` - Update progress
    - `get_prioritized_items()` - ML-based prioritization
    - `_calculate_word_difficulty()` - Difficulty scoring

**Config Repository:**
- `src/infrastructure/persistence/sqlite_config_repository.py`
  - New repository for static configuration
  - Methods:
    - `get_all_languages()` - Language list
    - `get_all_language_pairs()` - Language pair configs
    - `get_games_for_language_pair()` - Game configs
    - Add methods for seeding data

### 3. Data Migration Script ✓

**Migration Tool:**
- `src/infrastructure/persistence/migrate_to_sqlite.py`
  - Command-line migration tool
  - Migrates:
    - Languages from `assets/languages.json`
    - Language pairs from `assets/source.json`
    - Vocabulary from `assets/data/*/.*txt` files
    - Game configs from `assets/data/.../games.json`
  - Usage: `python -m src.infrastructure.persistence.migrate_to_sqlite`

### 4. Dependency Injection Container ✓

**Updated:**
- `src/infrastructure/di/container.py`
  - Added `database()` method returning DatabaseConnection
  - Changed `vocabulary_repository()` to use SQLiteVocabularyRepository
  - Changed `vocabulary_profiler()` to use SQLiteMLVocabularyProfiler
  - Added `config_repository()` method

## 🚧 Remaining Work

### 1. Component Updates (High Priority)

**Files to Update:**

1. **language_screen.py** - Partially updated
   - ✅ `load_languages()` - Use config_repository instead of JSON
   - ⚠️ Still references JSON loading in some methods

2. **main_screen.py** - Needs update
   - Current: Loads from `assets/source.json`
   - Target: Use `config_repository.get_all_language_pairs()`

3. **structure_screen.py** - Needs update
   - Current: Loads from `assets/source.json`
   - Target: Use config repository

### 2. Test Updates (High Priority)

**Vocabulary Repository Tests:**
- `tests/unit/test_infrastructure_vocabulary_repository.py`
  - Update to use SQLite repository
  - Add `tmp_path` fixture for test database
  - Update assertions for DB behavior

**ML Profiler Tests:**
- `tests/unit/test_infrastructure_ml_profiler.py`
  - Update to use SQLite profiler
  - Mock database connection or use in-memory DB
  - Test progress tracking

**New Tests Needed:**
- `test_infrastructure_database_connection.py`
- `test_infrastructure_sqlite_config_repository.py`

### 3. Data Migration Execution (Critical)

**Steps:**
1. Backup existing user data (`~/.kivy/tlum/*.json`, `*.pkl`, `*.ini`)
2. Run migration script:
   ```bash
   cd c:\Apps\Git\tlum
   python -m src.infrastructure.persistence.migrate_to_sqlite --db tlum.db --assets assets
   ```
3. Verify database contents:
   ```bash
   sqlite3 tlum.db "SELECT COUNT(*) FROM vocabulary_items;"
   sqlite3 tlum.db "SELECT * FROM languages;"
   ```

### 4. Backward Compatibility (Optional)

**Options:**
- Keep old file-based repositories as fallback
- Add migration flag to DI container
- Allow runtime switching between implementations

### 5. Component Method Updates

**Required Changes:**

```python
# OLD: main_screen.py
source_path = self._resource_service.find_resource('assets/source.json')
with open(source_path, 'r') as f:
    self.data = json.load(f)

# NEW: main_screen.py
config_repo = app._container.config_repository()
self.data = config_repo.get_all_language_pairs()
```

```python
# OLD: structure_screen.py
self.data = self.get_data('assets/source.json')

# NEW: structure_screen.py
config_repo = app._container.config_repository()
self.data = config_repo.get_all_language_pairs()
```

## 📦 Files Modified

### Created (11 files):
1. `src/infrastructure/persistence/database_schema.sql`
2. `src/infrastructure/persistence/database_connection.py`
3. `src/infrastructure/persistence/sqlite_vocabulary_repository.py`
4. `src/infrastructure/persistence/sqlite_config_repository.py`
5. `src/infrastructure/ml/sqlite_ml_vocabulary_profiler.py`
6. `src/infrastructure/persistence/migrate_to_sqlite.py`

### Modified (2 files):
1. `src/infrastructure/di/container.py` - Updated to use SQLite repositories
2. `src/component/language_screen.py` - Partially updated

### To Modify (6+ files):
1. `src/component/main_screen.py`
2. `src/component/structure_screen.py`
3. `tests/unit/test_infrastructure_vocabulary_repository.py`
4. `tests/unit/test_infrastructure_ml_profiler.py`
5. `tests/unit/test_infrastructure_di_container.py`
6. Other component files loading JSON configs

## 🎯 Next Steps (Priority Order)

1. **Run Migration Script**
   ```bash
   python -m src.infrastructure.persistence.migrate_to_sqlite
   ```

2. **Update Component Files**
   - Update `main_screen.py` to use config_repository
   - Update `structure_screen.py` to use config_repository
   - Search for all JSON loads and replace with DB queries

3. **Update Tests**
   - Modify vocabulary repository tests for SQLite
   - Modify ML profiler tests for SQLite
   - Add new database connection tests
   - Run full test suite: `pytest tests/unit/ -v`

4. **Verify Functionality**
   - Run application: `python src/main.py`
   - Test vocabulary loading
   - Test learning progress tracking
   - Test language selection
   - Test game loading

5. **Performance Testing**
   - Compare load times: File vs SQLite
   - Verify no regressions
   - Optimize queries if needed (add indexes)

6. **Documentation**
   - Update README.md with database info
   - Document schema migrations
   - Add developer setup guide

## 🔄 Migration Benefits

### Advantages:
- ✅ **Data Integrity**: Foreign keys, transactions, ACID compliance
- ✅ **Performance**: Indexed queries faster than file parsing
- ✅ **Scalability**: Better for growing vocabulary sets
- ✅ **Querying**: Complex queries (filter by difficulty, category, etc.)
- ✅ **Consistency**: Single source of truth
- ✅ **Analytics**: User progress tracking and analytics

### Considerations:
- ⚠️ **Initial Migration**: One-time cost to migrate existing data
- ⚠️ **Testing**: Need to update all tests
- ⚠️ **Complexity**: More complex than file I/O
- ⚠️ **Dependencies**: Requires sqlite3 (built into Python)

## 🐛 Known Issues

1. **Language screen**: Partial update complete, needs testing
2. **Test suite**: Will fail until all tests updated for SQLite
3. **Migration script**: Needs testing with actual data
4. **Game loading**: Not yet implemented in components

## 📚 References

- SQLite Documentation: https://www.sqlite.org/docs.html
- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- Database Schema: `src/infrastructure/persistence/database_schema.sql`

---

**Status**: 🟨 **70% Complete** - Core infrastructure done, integration work remaining

**Last Updated**: April 24, 2026
