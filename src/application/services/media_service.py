# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
import re
import requests
import json
import base64
import threading
import platform
from typing import Optional

if platform.system() == 'Windows':
    from kivy.core.audio.audio_sdl2 import MusicSDL2
else:
    from kivy.core.audio import SoundLoader
from kivy.clock import Clock


class MediaService:
    """
    Application service for media playback and text-to-speech.
    Single Responsibility: Handle audio playback and TTS generation.
    """

    def __init__(self, default_lang: str = 'en', audio_dir: str = 'assets/data/EN/audio/'):
        self._lang = default_lang.lower()
        self._audio_dir = audio_dir

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

        if not os.path.exists(filepath):
            self._generate_tts_audio(word, filepath)

        return filepath if os.path.exists(filepath) else None

    def play_audio(self, path: str) -> None:
        """
        Play an audio file.

        Args:
            path: Path to the audio file
        """
        if not os.path.exists(path):
            print(f"[MediaService] File not found: {path}")
            return

        def _play():
            try:
                if platform.system() == 'Windows':
                    sound = MusicSDL2(source=path)
                else:
                    sound = SoundLoader.load(path)

                if sound:
                    Clock.schedule_once(lambda dt: sound.play(), 0)
                else:
                    print(f"[MediaService] Cannot load audio: {path}")
            except Exception as e:
                print(f"[MediaService] Error playing audio: {e}")

        threading.Thread(target=_play, daemon=True).start()

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
