# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import json
import numpy as np
import pickle
import time
from pathlib import Path
from typing import Dict, List
from domain.entities.vocabulary_item import VocabularyItem
from domain.services import IVocabularyProfiler


class MLVocabularyProfiler(IVocabularyProfiler):
    """
    Machine Learning-based vocabulary profiler implementation.
    Uses embeddings and user history to prioritize vocabulary items.

    This is an infrastructure implementation of the domain interface.
    """

    def __init__(self, user_profile_path: str, model_path: str):
        self.user_profile_path = user_profile_path
        self.model_path = model_path

        # User interaction tracking
        self.user_history: Dict[str, Dict] = {}
        self.word_embeddings: Dict[str, np.ndarray] = {}

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

        # Load existing data
        self._load_user_profile()
        self._load_model()

    def mark_positive(self, item: VocabularyItem) -> None:
        """Mark a vocabulary item as correctly answered."""
        word = item.origin
        if word not in self.user_history:
            self.user_history[word] = {
                'correct': 0,
                'incorrect': 0,
                'last_seen': time.time()
            }

        self.user_history[word]['correct'] += 1
        self.user_history[word]['last_seen'] = time.time()
        self._save_user_profile()

    def mark_negative(self, item: VocabularyItem) -> None:
        """Mark a vocabulary item as incorrectly answered."""
        word = item.origin
        if word not in self.user_history:
            self.user_history[word] = {
                'correct': 0,
                'incorrect': 0,
                'last_seen': time.time()
            }

        self.user_history[word]['incorrect'] += 1
        self.user_history[word]['last_seen'] = time.time()
        self._save_user_profile()

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
        """Calculate difficulty score for a vocabulary item."""
        word = item.origin

        # Length-based difficulty
        length_score = min(len(word) / 15.0, 1.0)

        # Frequency score (default neutral)
        frequency_score = 0.5

        # Similarity score
        similarity_score = 0.5
        if len(self.word_embeddings) > 1:
            word_emb = self._create_word_embedding(word)
            similarities = []
            for other_word, other_emb in self.word_embeddings.items():
                if other_word != word:
                    dot_product = np.dot(word_emb, other_emb)
                    norm_product = np.linalg.norm(word_emb) * np.linalg.norm(other_emb)
                    if norm_product > 0:
                        similarity = dot_product / norm_product
                        similarities.append(similarity)
            if similarities:
                similarity_score = 1.0 - max(similarities)

        # User history score
        history_score = 0.5
        if word in self.user_history:
            history = self.user_history[word]
            # Safely get values with defaults in case keys are missing
            correct = history.get('correct', 0)
            incorrect = history.get('incorrect', 0)
            total = correct + incorrect
            if total > 0:
                accuracy = correct / total
                history_score = 1.0 - accuracy

        # Weighted combination
        difficulty = (
            self.difficulty_weights['length'] * length_score +
            self.difficulty_weights['frequency'] * frequency_score +
            self.difficulty_weights['similarity'] * similarity_score +
            self.difficulty_weights['user_history'] * history_score
        )

        return difficulty

    def _create_word_embedding(self, word: str) -> np.ndarray:
        """Create a simple character-based embedding for a word."""
        if word in self.word_embeddings:
            return self.word_embeddings[word]

        embedding = np.zeros(self.embedding_dim)

        # Character frequency features
        for char in word.lower()[:26]:
            if 'a' <= char <= 'z':
                embedding[ord(char) - ord('a')] += 1

        # Normalize
        if np.sum(embedding[:26]) > 0:
            embedding[:26] /= len(word)

        # Additional features
        if self.embedding_dim > 26:
            embedding[26] = len(word) / 20.0
            embedding[27] = len(set(word)) / len(word) if len(word) > 0 else 0
            if self.embedding_dim > 28:
                embedding[28] = word.count(' ') / max(1, len(word) - 1)
            if self.embedding_dim > 29:
                vowels = sum(1 for c in word.lower() if c in 'aeiou')
                embedding[29] = vowels / max(1, len(word))

        self.word_embeddings[word] = embedding
        return embedding

    def _load_user_profile(self):
        """Load user interaction history from file."""
        try:
            if Path(self.user_profile_path).exists():
                with open(self.user_profile_path, 'r', encoding='utf-8') as f:
                    loaded_history = json.load(f)
                    # Normalize loaded data to ensure all required keys exist
                    self.user_history = {}
                    for word, history in loaded_history.items():
                        self.user_history[word] = {
                            'correct': history.get('correct', 0),
                            'incorrect': history.get('incorrect', 0),
                            'last_seen': history.get('last_seen', time.time())
                        }
        except Exception as e:
            print(f"Warning: Could not load user profile: {e}")
            self.user_history = {}

    def _save_user_profile(self):
        """Save user interaction history to file."""
        try:
            with open(self.user_profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save user profile: {e}")

    def _load_model(self):
        """Load word embeddings and model state."""
        try:
            if Path(self.model_path).exists():
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.word_embeddings = data.get('embeddings', {})
        except Exception as e:
            print(f"Warning: Could not load model: {e}")
            self.word_embeddings = {}

    def _save_model(self):
        """Save word embeddings and model state."""
        try:
            data = {
                'embeddings': self.word_embeddings,
                'timestamp': time.time()
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not save model: {e}")
