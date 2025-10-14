# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
import time
try:
    from pydub import AudioSegment
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    HAS_DESKTOP_AUDIO = True
except ImportError:
    print("Warning: Desktop audio libraries not available")
    HAS_DESKTOP_AUDIO = False
    AudioSegment = None
    sd = None
    sf = None
    np = None

from kivy.app import App

class RecorderControllerDesktop:
    def get_initial_status(self, status_label):
        if not HAS_DESKTOP_AUDIO:
            status_label.text = "[!] Desktop audio recording libraries are not available"
            return False
        return True

    def start_recording(self, status_label):
        self.recording = True
        app = App.get_running_app()
        fs = 44100
        recorded_file_wav = os.path.join(app.get_home_dir(), f'tmp_{int(time.time())}.wav')
        recorded_file_mp3 = os.path.join(app.get_home_dir(), f'tmp_{int(time.time())}.mp3')
        max_duration = 15  # seconds
        buffer = []

        with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
            for _ in range(int(fs * max_duration / 1024)):
                if not self.recording:
                    break
                data, __ = stream.read(1024)
                buffer.append(data)

        if buffer:
            self.audio_data = np.concatenate(buffer, axis=0)
            # Save as WAV first
            for _ in range(5):
                try:
                    if os.path.exists(recorded_file_wav):
                        os.remove(recorded_file_wav)
                    break
                except PermissionError:
                    time.sleep(0.2)

            sf.write(recorded_file_wav, self.audio_data, fs)
            # Convert mono WAV to stereo MP3 using pydub
            audio = AudioSegment.from_wav(recorded_file_wav)
            if audio.channels == 1:
                audio = audio.set_channels(2)
            audio.export(recorded_file_mp3, format="mp3")
            # Optionally remove the temp wav file
            try:
                os.remove(recorded_file_wav)
            except Exception:
                pass
        return recorded_file_mp3

    def stop_recording(self, status_label):
        self.recording = False
