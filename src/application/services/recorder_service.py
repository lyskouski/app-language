# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from abc import ABC, abstractmethod
from typing import Optional


class IRecorderController(ABC):
    """Interface for audio recording controllers."""

    @abstractmethod
    def get_initial_status(self, status_label: str) -> str:
        """Get the initial recording status message."""
        pass

    @abstractmethod
    def start_recording(self, status_label: str) -> str:
        """Start recording and return status message."""
        pass

    @abstractmethod
    def stop_recording(self, status_label: str) -> str:
        """Stop recording and return status message with file path."""
        pass


class RecorderService:
    """
    Application service for audio recording.
    Single Responsibility: Coordinate audio recording operations.
    """

    def __init__(self, recorder_controller: IRecorderController):
        self._recorder = recorder_controller
        self._is_recording = False

    def get_initial_status(self, status_label: str = "Ready to record") -> str:
        """Get the initial status message."""
        return self._recorder.get_initial_status(status_label)

    def start_recording(self, status_label: str = "Recording...") -> str:
        """
        Start recording audio.

        Returns:
            Status message
        """
        self._is_recording = True
        return self._recorder.start_recording(status_label)

    def stop_recording(self, status_label: str = "Processing...") -> str:
        """
        Stop recording audio.

        Returns:
            Status message with file path
        """
        self._is_recording = False
        return self._recorder.stop_recording(status_label)

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording
