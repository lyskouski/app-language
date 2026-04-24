-- Tlum Application Database Schema
-- SQLite database for vocabulary learning app

-- Language pairs and learning paths
CREATE TABLE IF NOT EXISTS language_pairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    locale_from TEXT NOT NULL,
    locale_to TEXT NOT NULL,
    name TEXT NOT NULL,
    logo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(locale_from, locale_to)
);

-- Vocabulary items for each language pair
CREATE TABLE IF NOT EXISTS vocabulary_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_pair_id INTEGER NOT NULL,
    origin TEXT NOT NULL,
    translation TEXT NOT NULL,
    sound_path TEXT,
    image_path TEXT,
    category TEXT,
    difficulty_level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (language_pair_id) REFERENCES language_pairs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_vocab_language_pair ON vocabulary_items(language_pair_id);
CREATE INDEX IF NOT EXISTS idx_vocab_origin ON vocabulary_items(origin);

-- User learning progress for each vocabulary item
CREATE TABLE IF NOT EXISTS learning_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vocabulary_item_id INTEGER NOT NULL,
    user_id TEXT DEFAULT 'default',  -- For future multi-user support
    correct_count INTEGER DEFAULT 0,
    incorrect_count INTEGER DEFAULT 0,
    difficulty_score REAL DEFAULT 0.5,  -- 0.0 (easy) to 1.0 (hard)
    last_studied_at TIMESTAMP,
    study_count INTEGER DEFAULT 0,
    mastery_level INTEGER DEFAULT 0,  -- 0-5 scale
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vocabulary_item_id) REFERENCES vocabulary_items(id) ON DELETE CASCADE,
    UNIQUE(vocabulary_item_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_progress_vocab ON learning_progress(vocabulary_item_id);
CREATE INDEX IF NOT EXISTS idx_progress_difficulty ON learning_progress(difficulty_score);
CREATE INDEX IF NOT EXISTS idx_progress_last_studied ON learning_progress(last_studied_at);

-- ML character embeddings cache (for vocabulary profiler)
CREATE TABLE IF NOT EXISTS ml_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character TEXT UNIQUE NOT NULL,
    embedding_vector BLOB NOT NULL,  -- Serialized numpy array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Available languages
CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    locale TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    logo_path TEXT,
    is_active INTEGER DEFAULT 1,
    display_order INTEGER DEFAULT 0
);

-- Game configurations
CREATE TABLE IF NOT EXISTS game_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_pair_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    vocabulary_source TEXT NOT NULL,  -- Vocabulary category for games (e.g., 'verbs', 'dictionary', 'numbers', 'articulation')
    icon_path TEXT,
    display_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (language_pair_id) REFERENCES language_pairs(id) ON DELETE CASCADE,
    UNIQUE(language_pair_id, category_name)
);


-- Database metadata and versioning
CREATE TABLE IF NOT EXISTS db_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial metadata
INSERT OR REPLACE INTO db_metadata (key, value) VALUES ('schema_version', '1.0');
INSERT OR REPLACE INTO db_metadata (key, value) VALUES ('created_at', datetime('now'));
