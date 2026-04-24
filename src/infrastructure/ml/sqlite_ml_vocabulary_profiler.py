# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import numpy as np
import pickle
from typing import Dict, List, Optional
from domain.entities.vocabulary_item import VocabularyItem
from domain.services import IVocabularyProfiler
from infrastructure.persistence.database_connection import DatabaseConnection


class SQLiteMLVocabularyProfiler(IVocabularyProfiler):
    """
    SQLite-backed Machine Learning vocabulary profiler.
    Stores user learning progress and character embeddings in database.

    Replaces JSON/pickle file storage with relational database.
    """

    def __init__(self, db_connection: DatabaseConnection, locale_from: str, locale_to: str):
        self._db = db_connection
        self.locale_from = locale_from
        self.locale_to = locale_to

        # Model parameters
        self.embedding_dim = 32
        self.learning_rate = 0.01
        self.decay_factor = 0.95

        # Difficulty scoring weights
        self.difficulty_weights = {
            'length': 0.2,
            'frequency': 0.3,
            'similarity': 0.25,
            'user_history': 0.25
        }

        # Cache for embeddings (loaded on demand)
        self._embedding_cache: Dict[str, np.ndarray] = {}

    def mark_positive(self, item: VocabularyItem) -> None:
        """Mark a vocabulary item as correctly answered."""
        self._update_progress(item, correct=True)

    def mark_negative(self, item: VocabularyItem) -> None:
        """Mark a vocabulary item as incorrectly answered."""
        self._update_progress(item, correct=False)

    def _update_progress(self, item: VocabularyItem, correct: bool) -> None:
        """
        Update learning progress for an item.

        Args:
            item: Vocabulary item
            correct: Whether answer was correct
        """
        try:
            # Get vocabulary item ID
            vocab_id = self._get_vocabulary_item_id(item.origin)
            if not vocab_id:
                print(f"Warning: Could not find vocabulary item: {item.origin}")
                return

            with self._db.transaction() as conn:
                # Check if progress record exists
                row = conn.execute(
                    """SELECT id, correct_count, incorrect_count, study_count
                       FROM learning_progress
                       WHERE vocabulary_item_id = ? AND user_id = 'default'""",
                    (vocab_id,)
                ).fetchone()

                if row:
                    # Update existing record
                    correct_count = row['correct_count'] + (1 if correct else 0)
                    incorrect_count = row['incorrect_count'] + (0 if correct else 1)
                    study_count = row['study_count'] + 1
                    total = correct_count + incorrect_count
                    difficulty_score = 1.0 - (correct_count / total) if total > 0 else 0.5

                    conn.execute(
                        """UPDATE learning_progress
                           SET correct_count = ?,
                               incorrect_count = ?,
                               study_count = ?,
                               difficulty_score = ?,
                               last_studied_at = datetime('now'),
                               updated_at = datetime('now')
                           WHERE id = ?""",
                        (correct_count, incorrect_count, study_count, difficulty_score, row['id'])
                    )
                else:
                    # Create new record
                    correct_count = 1 if correct else 0
                    incorrect_count = 0 if correct else 1
                    difficulty_score = 0.0 if correct else 1.0

                    conn.execute(
                        """INSERT INTO learning_progress
                           (vocabulary_item_id, correct_count, incorrect_count,
                            difficulty_score, last_studied_at, study_count)
                           VALUES (?, ?, ?, ?, datetime('now'), 1)""",
                        (vocab_id, correct_count, incorrect_count, difficulty_score)
                    )
        except Exception as e:
            print(f"Error updating progress: {e}")

    def get_prioritized_items(
        self,
        items: List[VocabularyItem],
        limit: int
    ) -> List[VocabularyItem]:
        """Get vocabulary items prioritized by difficulty and user performance."""
        if not items:
            return []

        # Calculate difficulty scores for all items
        scored_items = []
        for item in items:
            difficulty = self._calculate_word_difficulty(item)
            scored_items.append((item, difficulty))

        # Sort by difficulty (higher = harder, should be shown more)
        scored_items.sort(key=lambda x: x[1], reverse=True)

        # Return top items up to limit
        return [item for item, _ in scored_items[:limit]]

    def _calculate_word_difficulty(self, item: VocabularyItem) -> float:
        """
        Calculate difficulty score for a vocabulary item.

        Args:
            item: Vocabulary item

        Returns:
            Difficulty score (0.0 - 1.0, higher = harder)
        """
        word = item.origin

        # Length-based difficulty
        length_score = min(len(word) / 15.0, 1.0)

        # Frequency score (default neutral)
        frequency_score = 0.5

        # Similarity score (simplified for now)
        similarity_score = 0.5

        # User history score from database
        history_score = self._get_history_score(word)

        # Weighted combination
        difficulty = (
            self.difficulty_weights['length'] * length_score +
            self.difficulty_weights['frequency'] * frequency_score +
            self.difficulty_weights['similarity'] * similarity_score +
            self.difficulty_weights['user_history'] * history_score
        )

        return difficulty

    def _get_history_score(self, origin: str) -> float:
        """
        Get difficulty score based on user history.

        Args:
            origin: Origin word

        Returns:
            History-based difficulty score (0.0 - 1.0)
        """
        try:
            vocab_id = self._get_vocabulary_item_id(origin)
            if not vocab_id:
                return 0.5  # Neutral score for unknown items

            row = self._db.fetchone(
                """SELECT correct_count, incorrect_count
                   FROM learning_progress
                   WHERE vocabulary_item_id = ? AND user_id = 'default'""",
                (vocab_id,)
            )

            if row:
                correct = row['correct_count']
                incorrect = row['incorrect_count']
                total = correct + incorrect
                if total > 0:
                    accuracy = correct / total
                    return 1.0 - accuracy  # Low accuracy = high difficulty

            return 0.5  # Neutral score for new items
        except Exception as e:
            print(f"Error getting history score: {e}")
            return 0.5

    def _get_vocabulary_item_id(self, origin: str) -> Optional[int]:
        """
        Get vocabulary item ID by origin word.

        Args:
            origin: Origin word

        Returns:
            Vocabulary item ID or None
        """
        query = """
            SELECT v.id
            FROM vocabulary_items v
            JOIN language_pairs lp ON v.language_pair_id = lp.id
            WHERE lp.locale_from = ? AND lp.locale_to = ? AND v.origin = ?
        """

        row = self._db.fetchone(query, (self.locale_from, self.locale_to, origin))
        return row['id'] if row else None

    def _get_or_create_embedding(self, character: str) -> np.ndarray:
        """
        Get or create character embedding.

        Args:
            character: Single character

        Returns:
            Embedding vector
        """
        # Check cache first
        if character in self._embedding_cache:
            return self._embedding_cache[character]

        # Check database
        row = self._db.fetchone(
            "SELECT embedding_vector FROM ml_embeddings WHERE character = ?",
            (character,)
        )

        if row:
            embedding = pickle.loads(row['embedding_vector'])
            self._embedding_cache[character] = embedding
            return embedding

        # Create new embedding
        embedding = np.random.randn(self.embedding_dim) * 0.1

        # Save to database
        try:
            self._db.execute(
                "INSERT INTO ml_embeddings (character, embedding_vector) VALUES (?, ?)",
                (character, pickle.dumps(embedding))
            )
            self._db.get_connection().commit()
        except Exception as e:
            print(f"Error saving embedding: {e}")

        self._embedding_cache[character] = embedding
        return embedding
