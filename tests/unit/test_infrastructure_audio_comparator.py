# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for LibrosaAudioComparator."""

import pytest
from unittest.mock import patch

from domain.services.audio_comparator import IAudioComparator
from infrastructure.audio.librosa_audio_comparator import LibrosaAudioComparator


class TestLibrosaAudioComparator:
    """Test audio comparator implementation."""

    @pytest.fixture
    def comparator(self):
        """Create a comparator instance for testing."""
        return LibrosaAudioComparator()

    def test_implements_interface(self, comparator):
        """Test that comparator implements IAudioComparator."""
        assert isinstance(comparator, IAudioComparator)

    def test_is_available(self, comparator):
        """Test availability check."""
        # Should return bool based on dependencies
        result = comparator.is_available()
        assert isinstance(result, bool)

    def test_compare_audio_without_dependencies(self, comparator):
        """Test audio comparison when dependencies are unavailable."""
        with patch('infrastructure.audio.librosa_audio_comparator.HAS_NUMPY', False):
            comparator_no_deps = comparator
            result = comparator_no_deps.compare_audio("fake1.mp3", "fake2.mp3")

            assert isinstance(result, list)
            assert len(result) > 0
            assert "feedback" in result[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
