# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from typing import List
from domain.entities.vocabulary_item import VocabularyItem
from domain.repositories.vocabulary_repository import IVocabularyRepository


class FileVocabularyRepository(IVocabularyRepository):
    """
    File-based implementation of vocabulary repository.
    Depends on abstraction (IVocabularyRepository), not the other way around.
    """

    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        """
        Load vocabulary items from a semicolon-separated file.
        Format: origin;translation[;sound[;image]]
        """
        items = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                if ";" in line:
                    parts = [p.strip() for p in line.strip().split(";")]
                    if len(parts) >= 2:
                        origin = parts[0]
                        translation = parts[1]
                        sound = parts[2] if len(parts) > 2 else None
                        image = parts[3] if len(parts) > 3 else None

                        try:
                            item = VocabularyItem(
                                origin=origin,
                                translation=translation,
                                sound=sound,
                                image=image
                            )
                            items.append(item)
                        except ValueError as e:
                            print(f"Warning: Skipping invalid item: {e}")
        except FileNotFoundError:
            print(f"Warning: Vocabulary file not found: {file_path}")
        except Exception as e:
            print(f"Error loading vocabulary: {e}")

        return items

    def save_to_file(self, file_path: str, items: List[VocabularyItem]) -> None:
        """Save vocabulary items to a file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for item in items:
                    parts = [item.origin, item.translation]
                    if item.sound:
                        parts.append(item.sound)
                        if item.image:
                            parts.append(item.image)
                    elif item.image:
                        parts.extend(['', item.image])

                    f.write(";".join(parts) + "\n")
        except Exception as e:
            print(f"Error saving vocabulary: {e}")
