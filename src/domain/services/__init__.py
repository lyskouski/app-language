# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from abc import ABC, abstractmethod
from typing import List
from domain.entities.vocabulary_item import VocabularyItem


class IVocabularyProfiler(ABC):
    """
    Domain interface for vocabulary profiling service.
    Responsible for tracking user performance and prioritizing vocabulary items.
    """

    @abstractmethod
    def mark_positive(self, item: VocabularyItem) -> None:
        """Mark a vocabulary item as correctly answered."""
        pass

    @abstractmethod
    def mark_negative(self, item: VocabularyItem) -> None:
        """Mark a vocabulary item as incorrectly answered."""
        pass

    @abstractmethod
    def get_prioritized_items(
        self,
        items: List[VocabularyItem],
        limit: int
    ) -> List[VocabularyItem]:
        """
        Get vocabulary items prioritized by difficulty and user performance.

        Args:
            items: All available vocabulary items
            limit: Maximum number of items to return

        Returns:
            List of prioritized vocabulary items
        """
        pass
