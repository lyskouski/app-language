# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for RecorderService."""

import pytest
from unittest.mock import Mock

from application.services.recorder_service import RecorderService


class TestRecorderService:
    """Test recorder service."""

    @pytest.fixture
    def mock_controller(self):
        """Create a mock recorder controller."""
        controller = Mock()
        controller.get_initial_status.return_value = "Ready"
        controller.start_recording.return_value = "Recording..."
        controller.stop_recording.return_value = "/path/to/recording.mp3"
        return controller

    @pytest.fixture
    def recorder_service(self, mock_controller):
        """Create a recorder service instance for testing."""
        return RecorderService(mock_controller)

    def test_get_initial_status(self, recorder_service, mock_controller):
        """Test getting initial status."""
        result = recorder_service.get_initial_status()

        assert result == "Ready"
        mock_controller.get_initial_status.assert_called_once()

    def test_start_recording(self, recorder_service, mock_controller):
        """Test starting recording."""
        result = recorder_service.start_recording()

        assert result == "Recording..."
        assert recorder_service.is_recording() is True
        mock_controller.start_recording.assert_called_once()

    def test_stop_recording(self, recorder_service, mock_controller):
        """Test stopping recording."""
        recorder_service.start_recording()
        result = recorder_service.stop_recording()

        assert result == "/path/to/recording.mp3"
        assert recorder_service.is_recording() is False
        mock_controller.stop_recording.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
