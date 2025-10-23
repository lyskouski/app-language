# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from typing import Optional

class StoreItem:
    def __init__(self, origin: str, translation: str, sound: Optional[str] = None, image: Optional[str] = None):
        self.origin = origin
        self.translation = translation
        self.sound = sound
        self.image = image

    def __str__(self) -> str:
        return f"{self.origin} → {self.translation}"

    def __repr__(self) -> str:
        return f"StoreItem('{self.origin}', '{self.translation}', sound={self.sound}, image={self.image})"