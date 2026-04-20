# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for MediaService."""

import pytest
import os
from unittest.mock import Mock, patch

from application.services.media_service import MediaService


class TestMediaService:
    """Test media service."""

    @pytest.fixture
    def media_service(self, tmp_path):
        """Create a media service instance for testing."""
        audio_dir = str(tmp_path / "audio")
        os.makedirs(audio_dir, exist_ok=True)
        return MediaService('en', audio_dir)

    def test_set_language(self, media_service):
        """Test setting language."""
        media_service.set_language('es')
        assert media_service._lang == 'es'

    def test_set_audio_directory(self, media_service, tmp_path):
        """Test setting audio directory."""
        new_dir = str(tmp_path / "new_audio")
        media_service.set_audio_directory(new_dir)
        assert media_service._audio_dir == new_dir

    @patch('application.services.media_service.requests.post')
    def test_get_audio_file_generates_tts(self, mock_post, media_service):
        """Test that TTS is generated when file doesn't exist."""
        # Mock successful TTS response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "//OEtlc3Q="  # Base64 encoded "test"
        mock_post.return_value = mock_response

        result = media_service.get_audio_file("hello")

        # Should call TTS generation
        assert mock_post.called
        # Result should be a path
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
