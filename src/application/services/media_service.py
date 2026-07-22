# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
import re
import requests
import json
import base64
import platform
from abc import ABC, abstractmethod
from typing import Optional

if platform.system() == 'Windows':
    from kivy.core.audio.audio_sdl2 import MusicSDL2
else:
    from kivy.core.audio import SoundLoader

from kivy.clock import Clock


class IAudioPlaybackBackend(ABC):
    """Abstraction for platform-specific audio playback backends."""

    @abstractmethod
    def play_audio(self, path: str) -> bool:
        """Play audio at the provided path; return True on success."""
        pass

    @abstractmethod
    def stop_audio(self) -> None:
        """Stop and release any active playback resources."""
        pass


class KivyAudioPlaybackBackend(IAudioPlaybackBackend):
    """Default Kivy-based audio backend used on desktop and as fallback."""

    def __init__(self):
        self._current_sound = None

    def play_audio(self, path: str) -> bool:
        self.stop_audio()

        if platform.system() == 'Windows':
            self._current_sound = MusicSDL2(source=path)
        else:
            self._current_sound = SoundLoader.load(path)

        if not self._current_sound:
            return False

        self._current_sound.play()
        return True

    def stop_audio(self) -> None:
        if not self._current_sound:
            return

        try:
            self._current_sound.stop()
        except Exception:
            pass
        finally:
            self._current_sound = None


class MediaService:
    """
    Application service for media playback and text-to-speech.
    Single Responsibility: Handle audio playback and TTS generation.
    """

    def __init__(
        self,
        default_lang: str = 'en',
        audio_dir: str = 'assets/data/EN/audio/',
        audio_playback_backend: Optional[IAudioPlaybackBackend] = None
    ):
        self._lang = default_lang.lower()
        self._audio_dir = audio_dir
        self._audio_playback_backend = audio_playback_backend or KivyAudioPlaybackBackend()

    def set_language(self, lang: str) -> None:
        """Set the language for TTS."""
        self._lang = lang.lower()

    def set_audio_directory(self, audio_dir: str) -> None:
        """Set the audio directory for storing TTS files."""
        self._audio_dir = audio_dir

    def get_audio_file(self, word: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Get or generate audio file for a word.

        Args:
            word: The word to get audio for
            filename: Optional custom filename

        Returns:
            Path to the audio file or None if failed
        """
        if not filename or not filename.strip():
            filename = f"{word}.mp3"

        filepath = os.path.join(self._audio_dir, filename)

        # Regenerate when file is missing or empty/corrupted.
        if (not os.path.exists(filepath)) or os.path.getsize(filepath) == 0:
            self._generate_tts_audio(word, filepath)

        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return filepath
        return None

    def play_audio(self, path: str) -> None:
        """
        Play an audio file.

        Args:
            path: Path to the audio file
        """
        if not path:
            print('[MediaService] Empty audio path')
            return

        if (not os.path.exists(path)) or os.path.getsize(path) == 0:
            print(f"[MediaService] File not found: {path}")
            return

        def _play(dt):
            try:
                if not self._audio_playback_backend.play_audio(path):
                    print(f"[MediaService] Cannot load audio: {path}")
            except Exception as e:
                print(f"[MediaService] Error playing audio: {e}")

        Clock.schedule_once(_play, 0)

    def _generate_tts_audio(self, word: str, filepath: str) -> None:
        """
        Generate TTS audio using Google Translate API.

        Args:
            word: The word to generate audio for
            filepath: Path to save the audio file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            data = {
                'f.req': json.dumps([
                    [
                        [
                            'jQ1olc',
                            json.dumps([
                                word,
                                self._lang,
                                None,
                                json.dumps(None),
                            ]),
                            None,
                            'generic',
                        ]
                    ]
                ]),
            }

            response = requests.post(
                'https://translate.google.com/_/TranslateWebserverUi/data/batchexecute',
                data=data,
                timeout=10
            )

            if response.status_code == 200:
                match = re.search(r'//OE[^\\]+', response.text)
                if match:
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(match.group(0)))
                else:
                    print(f"[MediaService] No audio data found for '{word}'")
            else:
                print(f"[MediaService] HTTP error {response.status_code} for '{word}'")
        except Exception as e:
            print(f"[MediaService] Error generating TTS: {e}")
