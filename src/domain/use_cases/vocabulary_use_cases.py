# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import random
from typing import List
from domain.entities.vocabulary_item import VocabularyItem
from domain.repositories.vocabulary_repository import IVocabularyRepository


class LoadVocabularyUseCase:
    """
    Use Case: Load vocabulary items from a data source.
    Single Responsibility: Only handles loading vocabulary.
    """

    def __init__(self, repository: IVocabularyRepository):
        self._repository = repository

    def execute(self, file_path: str) -> List[VocabularyItem]:
        """Load and return vocabulary items from the specified file."""
        return self._repository.load_from_file(file_path)


class ShuffleVocabularyUseCase:
    """
    Use Case: Shuffle vocabulary items and apply a limit.
    Single Responsibility: Only handles vocabulary shuffling logic.
    """

    def execute(self, items: List[VocabularyItem], limit: int = 25) -> List[VocabularyItem]:
        """Shuffle items and return up to the specified limit."""
        shuffled = items.copy()
        random.shuffle(shuffled)
        return shuffled[:limit]
