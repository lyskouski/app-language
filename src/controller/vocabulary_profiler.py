# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import json
import numpy as np
import pickle
import time
from pathlib import Path
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from model.store_item import StoreItem

class VocabularyProfiler:
    """
    Lightweight machine learning model for vocabulary proficiency tracking.
    Uses a distilled embedding approach to learn user patterns and optimize vocabulary ordering.
    """

    def __init__(self, user_profile_path: str = "user_profile.json", model_path: str = "vocab_model.pkl"):
        self.user_profile_path = user_profile_path
        self.model_path = model_path

        # User interaction tracking
        self.user_history: Dict[str, Dict] = {}
        self.word_embeddings: Dict[str, np.ndarray] = {}

        # Model parameters
        self.embedding_dim = 32  # Small embedding size for efficiency
        self.learning_rate = 0.01
        self.decay_factor = 0.95  # For forgetting old patterns

        # Difficulty scoring weights
        self.difficulty_weights = {
            'length': 0.2,          # Word length
            'frequency': 0.3,       # How often word appears
            'similarity': 0.25,     # Similarity to known words
            'user_history': 0.25    # Personal performance history
        }

        # Load existing data
        self._load_user_profile()
        self._load_model()

    def _load_user_profile(self):
        """Load user interaction history from file."""
        try:
            if Path(self.user_profile_path).exists():
                with open(self.user_profile_path, 'r', encoding='utf-8') as f:
                    self.user_history = json.load(f)
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

    def _create_word_embedding(self, word: str) -> np.ndarray:
        """Create a simple character-based embedding for a word."""
        if word in self.word_embeddings:
            return self.word_embeddings[word]

        # Create embedding based on character features
        embedding = np.zeros(self.embedding_dim)

        # Character frequency features (first 26 dimensions)
        for i, char in enumerate(word.lower()[:26]):
            if 'a' <= char <= 'z':
                embedding[ord(char) - ord('a')] += 1

        # Normalize character frequencies
        if np.sum(embedding[:26]) > 0:
            embedding[:26] /= len(word)

        # Additional features (remaining dimensions)
        if self.embedding_dim > 26:
            embedding[26] = len(word) / 20.0  # Normalized word length
            embedding[27] = len(set(word)) / len(word) if len(word) > 0 else 0  # Character diversity
            if self.embedding_dim > 28:
                embedding[28] = word.count(' ') / max(1, len(word) - 1)  # Space ratio
            if self.embedding_dim > 29:
                # Vowel ratio
                vowels = sum(1 for c in word.lower() if c in 'aeiou')
                embedding[29] = vowels / max(1, len(word))
            if self.embedding_dim > 30:
                # Consonant clusters (difficulty indicator)
                consonant_clusters = 0
                consonants = 'bcdfghjklmnpqrstvwxyz'
                for i in range(len(word) - 1):
                    if word[i].lower() in consonants and word[i+1].lower() in consonants:
                        consonant_clusters += 1
                embedding[30] = consonant_clusters / max(1, len(word) - 1)
            if self.embedding_dim > 31:
                # Repetitive patterns (easier to remember)
                unique_chars = len(set(word.lower()))
                embedding[31] = (len(word) - unique_chars) / max(1, len(word))

        self.word_embeddings[word] = embedding
        return embedding

    def _calculate_word_difficulty(self, item: "StoreItem") -> float:
        """Calculate difficulty score for a vocabulary item."""
        word = item.origin

        # Length-based difficulty
        length_score = min(len(word) / 15.0, 1.0)  # Normalize to 0-1

        # Frequency-based difficulty (assume common words are easier)
        # This could be enhanced with actual frequency data
        frequency_score = 0.5  # Default neutral score

        # Similarity to known words (using embeddings)
        similarity_score = 0.5  # Default neutral score
        if len(self.word_embeddings) > 1:
            word_emb = self._create_word_embedding(word)
            similarities = []
            for other_word, other_emb in self.word_embeddings.items():
                if other_word != word:
                    # Cosine similarity
                    dot_product = np.dot(word_emb, other_emb)
                    norm_product = np.linalg.norm(word_emb) * np.linalg.norm(other_emb)
                    if norm_product > 0:
                        similarities.append(dot_product / norm_product)

            if similarities:
                similarity_score = 1.0 - max(similarities)  # Less similar = more difficult

        # User history-based difficulty
        history_score = 0.5  # Default neutral score
        if word in self.user_history:
            user_data = self.user_history[word]
            correct = user_data.get('correct', 0)
            total = user_data.get('total', 0)
            if total > 0:
                accuracy = correct / total
                history_score = 1.0 - accuracy  # Lower accuracy = higher difficulty

                # Apply temporal decay (recent performance matters more)
                last_seen = user_data.get('last_seen', 0)
                time_decay = np.exp(-(time.time() - last_seen) / (7 * 24 * 3600))  # 7-day decay
                history_score = history_score * time_decay + 0.5 * (1 - time_decay)

        # Weighted combination
        difficulty = (
            self.difficulty_weights['length'] * length_score +
            self.difficulty_weights['frequency'] * frequency_score +
            self.difficulty_weights['similarity'] * similarity_score +
            self.difficulty_weights['user_history'] * history_score
        )

        return difficulty

    def _update_user_history(self, item: "StoreItem", is_correct: bool):
        """Update user interaction history."""
        word = item.origin

        if word not in self.user_history:
            self.user_history[word] = {
                'correct': 0,
                'total': 0,
                'first_seen': time.time(),
                'last_seen': time.time(),
                'consecutive_correct': 0,
                'consecutive_incorrect': 0
            }

        user_data = self.user_history[word]
        user_data['total'] += 1
        user_data['last_seen'] = time.time()

        if is_correct:
            user_data['correct'] += 1
            user_data['consecutive_correct'] += 1
            user_data['consecutive_incorrect'] = 0
        else:
            user_data['consecutive_correct'] = 0
            user_data['consecutive_incorrect'] += 1

        # Update word embedding based on performance (reinforcement learning)
        word_emb = self._create_word_embedding(word)

        # Adjust embedding based on performance
        if is_correct:
            # Slightly reduce difficulty indicators
            adjustment = -self.learning_rate * np.random.normal(0, 0.1, self.embedding_dim)
        else:
            # Slightly increase difficulty indicators
            adjustment = self.learning_rate * np.random.normal(0, 0.1, self.embedding_dim)

        # Apply adjustment with bounds
        self.word_embeddings[word] = np.clip(word_emb + adjustment, -2.0, 2.0)

    def mark_positive(self, item: "StoreItem"):
        """Mark an item as correctly answered (positive feedback)."""
        self._update_user_history(item, True)
        self._save_user_profile()
        self._save_model()

    def mark_negative(self, item: "StoreItem"):
        """Mark an item as incorrectly answered (negative feedback)."""
        self._update_user_history(item, False)
        self._save_user_profile()
        self._save_model()

    def get_prioritized_items(self, items: List["StoreItem"], size: int = 25) -> List["StoreItem"]:
        """
        Get prioritized list of vocabulary items based on ML model.
        Returns items ordered by learning priority (difficult/forgotten items first).
        """
        if not items:
            return []

        # Ensure size is a valid integer
        try:
            size = int(size) if not isinstance(size, int) else size
            size = max(1, min(size, len(items)))  # Clamp size to valid range
        except (TypeError, ValueError):
            size = min(25, len(items))  # Default fallback

        # Calculate priority scores for all items
        item_scores = []
        for item in items:
            difficulty = self._calculate_word_difficulty(item)

            # Additional priority factors
            word = item.origin
            priority_boost = 0.0

            if word in self.user_history:
                user_data = self.user_history[word]

                # Boost priority for recently incorrect answers
                if user_data.get('consecutive_incorrect', 0) > 0:
                    priority_boost += 0.3 * user_data['consecutive_incorrect']

                # Boost priority for words not seen recently
                days_since_seen = (time.time() - user_data.get('last_seen', 0)) / (24 * 3600)
                if days_since_seen > 1:
                    priority_boost += min(0.2 * days_since_seen, 0.5)

                # Reduce priority for recently mastered words
                if user_data.get('consecutive_correct', 0) >= 3:
                    priority_boost -= 0.4
            else:
                # New words get medium priority
                priority_boost += 0.1

            total_score = difficulty + priority_boost
            item_scores.append((item, total_score))

        # Sort by priority score (highest first)
        item_scores.sort(key=lambda x: x[1], reverse=True)

        # Add some randomization to avoid predictable patterns
        selected_items = []
        remaining_items = [item for item, _ in item_scores]

        # Take top 70% by priority, 30% with some randomization
        priority_count = int(size * 0.7)
        random_count = size - priority_count

        # Add high-priority items
        selected_items.extend(remaining_items[:priority_count])

        # Add some randomized items from the rest
        if len(remaining_items) > priority_count and random_count > 0:
            import random
            random_pool = remaining_items[priority_count:]
            random.shuffle(random_pool)
            selected_items.extend(random_pool[:random_count])

        # If we don't have enough items, fill with remaining
        while len(selected_items) < size and len(selected_items) < len(items):
            for item in remaining_items:
                if item not in selected_items:
                    selected_items.append(item)
                    break

        return selected_items[:size]

    def get_user_stats(self) -> Dict:
        """Get user learning statistics."""
        if not self.user_history:
            return {
                'total_words_studied': 0,
                'overall_accuracy': 0.0,
                'words_mastered': 0,
                'words_struggling': 0,
                'study_streak': 0
            }

        total_correct = sum(data.get('correct', 0) for data in self.user_history.values())
        total_attempts = sum(data.get('total', 0) for data in self.user_history.values())
        overall_accuracy = total_correct / total_attempts if total_attempts > 0 else 0.0

        words_mastered = sum(1 for data in self.user_history.values()
                           if data.get('consecutive_correct', 0) >= 3)

        words_struggling = sum(1 for data in self.user_history.values()
                             if data.get('consecutive_incorrect', 0) >= 2)

        # Calculate study streak (days with activity)
        current_time = time.time()
        study_days = set()
        for data in self.user_history.values():
            last_seen = data.get('last_seen', 0)
            days_ago = int((current_time - last_seen) / (24 * 3600))
            if days_ago < 30:  # Consider last 30 days
                study_days.add(days_ago)

        study_streak = len(study_days)

        return {
            'total_words_studied': len(self.user_history),
            'overall_accuracy': overall_accuracy,
            'words_mastered': words_mastered,
            'words_struggling': words_struggling,
            'study_streak': study_streak,
            'total_attempts': total_attempts
        }
