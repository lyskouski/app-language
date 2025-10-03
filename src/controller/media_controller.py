# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
import re
import requests
import json
import base64
import threading
import platform

if platform.system() == 'Windows':
    from kivy.core.audio.audio_sdl2 import MusicSDL2
else:
    from kivy.core.audio import SoundLoader
from kivy.clock import Clock

class MediaController:
    lang = 'en'

    def __init__(self, lang='en', path='assets/data/EN/audio/'):
        self.lang = lang.lower()
        self.path = path

    def get(self, word, name=None):
        if not name or not name.strip():
            name = f"{word}.mp3"
        filename = f"{self.path}/{name}"
        if not os.path.exists(filename):
            self.save_sound(word, filename)
        return filename if os.path.exists(filename) else None

    def save_sound(self, word, filename):
        data = {
            'f.req': json.dumps([
                [
                    [
                        'jQ1olc',
                        json.dumps([
                            word,
                            self.lang,
                            None,
                            json.dumps(None),
                        ]),
                        None,
                        'generic',
                    ]
                ]
            ]),
        }

        response = requests.post('https://translate.google.com/_/TranslateWebserverUi/data/batchexecute', data=data)

        if response.status_code == 200:
            match = re.search(r'//OE[^\\]+', response.text)
            if match:
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(match.group(0)))
            else:
                print(f"Error: No match for '{word}'")
        else:
            print(f"HTTP error: {response.status_code} for '{word}'")

    @staticmethod
    def play_sound(path):
        if not os.path.exists(path):
            print(f"[AudioPlayer] File not found: {path}")
            return

        def _play():
            if platform.system() == 'Windows':
                sound = MusicSDL2(source=path)
            else:
                sound = SoundLoader.load(path)

            if sound:
                Clock.schedule_once(lambda dt: sound.play(), 0)
            else:
                print(f"[AudioPlayer] Cannot load audio: {path}")

        threading.Thread(target=_play, daemon=True).start()
