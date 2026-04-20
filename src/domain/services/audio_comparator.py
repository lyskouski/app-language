# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IAudioComparator(ABC):
    """
    Domain interface for audio comparison service.
    Responsible for comparing recorded audio with reference audio.
    """

    @abstractmethod
    def compare_audio(
        self,
        original_path: str,
        recorded_path: str
    ) -> List[Dict[str, Any]]:
        """
        Compare two audio files and return similarity analysis.

        Args:
            original_path: Path to the reference audio file
            recorded_path: Path to the user's recorded audio file

        Returns:
            List of comparison results with scores and feedback
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if audio comparison functionality is available."""
        pass
