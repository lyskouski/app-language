# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from typing import List, Optional
from domain.entities.vocabulary_item import VocabularyItem
from domain.services import IVocabularyProfiler
from domain.use_cases.vocabulary_use_cases import LoadVocabularyUseCase, ShuffleVocabularyUseCase


class VocabularyService:
    """
    Application Service coordinating vocabulary-related use cases.
    Follows Single Responsibility Principle - only coordinates vocabulary operations.
    """

    def __init__(
        self,
        load_use_case: LoadVocabularyUseCase,
        shuffle_use_case: ShuffleVocabularyUseCase,
        profiler: Optional[IVocabularyProfiler] = None
    ):
        self._load_use_case = load_use_case
        self._shuffle_use_case = shuffle_use_case
        self._profiler = profiler
        self._current_items: List[VocabularyItem] = []
        self._shuffled_items: List[VocabularyItem] = []

    def load_vocabulary(self, file_path: str) -> None:
        """Load vocabulary from a file."""
        self._current_items = self._load_use_case.execute(file_path)

    def prepare_study_set(self, limit: int = 25, force_shuffle: bool = False) -> List[VocabularyItem]:
        """Prepare a shuffled study set with the specified limit.

        Args:
            limit: Maximum number of items to return
            force_shuffle: If True, always use random shuffle even when profiler exists
        """
        if self._profiler and not force_shuffle:
            # Use ML-based prioritization if available
            prioritized_items = self._profiler.get_prioritized_items(
                self._current_items, limit
            )
            # Shuffle the prioritized items to add variety
            self._shuffled_items = self._shuffle_use_case.execute(prioritized_items, limit)
        else:
            self._shuffled_items = self._shuffle_use_case.execute(self._current_items, limit)
        return self._shuffled_items

    def get_current_study_set(self) -> List[VocabularyItem]:
        """Get the current study set."""
        return self._shuffled_items

    def mark_item_correct(self, item: VocabularyItem) -> None:
        """Mark an item as correctly answered (for profiling)."""
        if self._profiler:
            self._profiler.mark_positive(item)

    def mark_item_incorrect(self, item: VocabularyItem) -> None:
        """Mark an item as incorrectly answered (for profiling)."""
        if self._profiler:
            self._profiler.mark_negative(item)
