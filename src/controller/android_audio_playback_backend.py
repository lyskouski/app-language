# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from application.services.media_service import IAudioPlaybackBackend


class AndroidAudioPlaybackBackend(IAudioPlaybackBackend):
    """Android native audio playback backend using MediaPlayer."""

    def __init__(self):
        self._player = None
        self._media_player_class = None
        try:
            from jnius import autoclass
            self._media_player_class = autoclass('android.media.MediaPlayer')
        except Exception:
            self._media_player_class = None

    def is_available(self) -> bool:
        return self._media_player_class is not None

    def play_audio(self, path: str) -> bool:
        if not self._media_player_class:
            return False

        self.stop_audio()

        try:
            player = self._media_player_class()
            player.setDataSource(path)
            player.prepare()
            player.start()
            self._player = player
            return True
        except Exception as e:
            print(f"[AndroidAudioPlaybackBackend] Playback failed: {e}")
            self.stop_audio()
            return False

    def stop_audio(self) -> None:
        if not self._player:
            return

        try:
            self._player.stop()
        except Exception:
            pass

        try:
            self._player.reset()
        except Exception:
            pass

        try:
            self._player.release()
        except Exception:
            pass

        self._player = None
