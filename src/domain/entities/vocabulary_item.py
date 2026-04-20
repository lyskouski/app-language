# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VocabularyItem:
    """
    Domain Entity representing a vocabulary item.
    Immutable and contains only business logic, no framework dependencies.
    """
    origin: str
    translation: str
    sound: Optional[str] = None
    image: Optional[str] = None

    def __post_init__(self):
        if not self.origin or not self.translation:
            raise ValueError("Origin and translation are required")

    def __str__(self) -> str:
        return f"{self.origin} → {self.translation}"

    def has_audio(self) -> bool:
        """Check if this item has audio support."""
        return self.sound is not None

    def has_image(self) -> bool:
        """Check if this item has image support."""
        return self.image is not None
