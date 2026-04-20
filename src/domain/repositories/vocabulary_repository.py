# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from abc import ABC, abstractmethod
from typing import List
from domain.entities.vocabulary_item import VocabularyItem


class IVocabularyRepository(ABC):
    """
    Repository interface for vocabulary data access.
    Follows Dependency Inversion Principle - domain defines the interface.
    """

    @abstractmethod
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        """Load vocabulary items from a file."""
        pass

    @abstractmethod
    def save_to_file(self, file_path: str, items: List[VocabularyItem]) -> None:
        """Save vocabulary items to a file."""
        pass
