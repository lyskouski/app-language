# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    print("Warning: numpy not available, some features may be limited")
    HAS_NUMPY = False
    np = None
import time

from controller.audio_comparator import AudioComparator
from controller.media_controller import MediaController
from kivy.app import App
from kivy.core.audio.audio_sdl2 import MusicSDL2
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
from kivy.clock import Clock

# Import Android audio recorder
try:
    from controller.android_audio import AndroidAudioRecorder
    android_recorder = AndroidAudioRecorder()
except ImportError:
    android_recorder = None

# Desktop audio libraries (optional)
if platform not in ['android', 'ios']:
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
else:
    HAS_DESKTOP_AUDIO = False
    AudioSegment = None
    sd = None
    sf = None
    # We still need numpy on Android for other functionality
    try:
        import numpy as np
    except ImportError:
        np = None

import threading

class MultilineLabel(Label):
    pass

class RecorderWidget(BoxLayout):
    loading_widget = None

    def init_data(self, item):
        self.loading_widget = item

    def load_data(self):
        app = App.get_running_app()
        self.recording = False
        self.selected_file = None
        self.audio_files = self.load_audio_files()

        main_layout = BoxLayout(orientation='vertical')

        if platform == 'android':
            if android_recorder and android_recorder.is_available():
                if android_recorder.has_recording_permission():
                    info_label = Label(
                        text="Android audio recording ready",
                        size_hint_y=None,
                        height=30,
                        color=(0, 1, 0, 1)  # Green color
                    )
                else:
                    info_label = Label(
                        text="Tap record to request audio permission",
                        size_hint_y=None,
                        height=30,
                        color=(1, 1, 0, 1)  # Yellow color
                    )
            else:
                info_label = Label(
                    text="Android audio recording not available",
                    size_hint_y=None,
                    height=30,
                    color=(1, 0, 0, 1)  # Red color
                )
            main_layout.add_widget(info_label)
        elif platform == 'ios':
            info_label = Label(
                text="iOS audio recording not yet implemented",
                size_hint_y=None,
                height=30,
                color=(1, 0.5, 0, 1)  # Orange color
            )
            main_layout.add_widget(info_label)
        elif not HAS_DESKTOP_AUDIO:
            info_label = Label(
                text="Desktop audio libraries not available",
                size_hint_y=None,
                height=30,
                color=(1, 0.5, 0, 1)  # Orange color
            )
            main_layout.add_widget(info_label)

        scroll_view = ScrollView()
        list_layout = GridLayout(cols=1, size_hint_y='1dp', minimum_height='0.8dp', spacing=5)

        for file_name, sentence in self.audio_files.items():
            row = BoxLayout(orientation='horizontal', size_hint_min_y=30)
            row.add_widget(MultilineLabel(text=sentence))
            choose_button = Button(text=app._('button_choose', app.locale), size_hint_x=0.2)
            choose_button.file_path = file_name
            choose_button.bind(on_release=self.choose_sentence)
            row.add_widget(choose_button)
            list_layout.add_widget(row)

        scroll_view.add_widget(list_layout)
        main_layout.add_widget(scroll_view)

        control_layout = BoxLayout(size_hint_y=None, height=50)
        self.listen_button = Button(text=app._('button_listen', app.locale), on_press=self.play_audio)
        self.listen_button.disabled = True
        self.status_label = Label(text=app._('status_select_sentence', app.locale), size_hint_y='0.2dp')
        self.record_button = Button(text=app._('button_record', app.locale), on_press=self.toggle_recording)
        self.play_button = Button(text=app._('button_play', app.locale), on_press=self.play_audio, disabled=True)

        control_layout.add_widget(self.listen_button)
        main_layout.add_widget(self.status_label)
        control_layout.add_widget(self.record_button)
        control_layout.add_widget(self.play_button)

        main_layout.add_widget(control_layout)
        self.clear_widgets()
        self.add_widget(main_layout)

    def load_audio_files(self):
        app = App.get_running_app()
        media_controller = MediaController(app.locale_to, app.get_audio_dir())
        audio_files = {}
        for line in app.store:
            key = line[2] if line[2] != '' else line[0] + '.mp3'
            audio_files[media_controller.get(line[0], key)] = line[0]
            # TODO: Update loading status (not reflecting, just a freeze)
            if (self.loading_widget and hasattr(self.loading_widget, 'status')):
                self.loading_widget.status += 1
        return audio_files

    def choose_sentence(self, instance):
        self.listen_button.disabled = False
        self.listen_button.file_path = instance.file_path
        self.status_label.text = f"Selected: {self.audio_files.get(instance.file_path, '')}"

    def toggle_recording(self, instance):
        app = App.get_running_app()
        if not self.recording:
            self.recording = True
            self.status_label.text = app._('status_recording', app.locale)
            self.record_button.text = app._('button_stop_recording', app.locale)
            self.play_button.disabled = True

            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()
        else:
            self.recording = False
            self.status_label.text = app._('status_saving', app.locale)
            self.record_button.text = app._('button_processing', app.locale)
            self.record_button.disabled = True

    def record_audio(self):
        max_duration = 15

        if platform == 'android' and android_recorder and android_recorder.is_available():
            self.start_android_recording(max_duration)
        elif platform not in ['android', 'ios'] and HAS_DESKTOP_AUDIO:
            self.start_desktop_recording(max_duration)
        else:
            print("Warning: Audio recording not available on this platform")
            self.recording = False
            return

    def start_android_recording(self, max_duration):
        try:
            app = App.get_running_app()
            # Use 3gp format for Android compatibility
            recorded_file = os.path.join(app.get_home_dir(), f'tmp_{int(time.time())}.3gp')
            self.play_button.file_path = recorded_file

            # Callback to handle recording start result
            def recording_callback(success, message):
                if success:
                    print(f"Recording started: {message}")
                    # Schedule stop after max_duration
                    Clock.schedule_once(lambda dt: self.stop_android_recording(), max_duration)
                else:
                    print(f"Recording failed: {message}")
                    self.recording = False
                    # Update UI to show error
                    if hasattr(self, 'status_label'):
                        self.status_label.text = f"Recording failed: {message}"

            # Start recording with callback
            android_recorder.start_recording(recorded_file, max_duration, recording_callback)

        except Exception as e:
            print(f"Android recording error: {e}")
            self.recording = False

    def stop_android_recording(self):
        try:
            if android_recorder:
                def stop_callback(success, message):
                    if success:
                        print(f"Recording stopped: {message}")
                        if hasattr(self, 'status_label'):
                            self.status_label.text = "Recording completed"
                    else:
                        print(f"Stop recording failed: {message}")
                        if hasattr(self, 'status_label'):
                            self.status_label.text = f"Stop failed: {message}"
                    self.recording = False

                android_recorder.stop_recording(stop_callback)
            else:
                self.recording = False
        except Exception as e:
            print(f"Error stopping Android recording: {e}")
            self.recording = False

    def start_desktop_recording(self, max_duration):
        app = App.get_running_app()
        fs = 44100
        recorded_file_wav = os.path.join(app.get_home_dir(), f'tmp_{int(time.time())}.wav')
        recorded_file_mp3 = os.path.join(app.get_home_dir(), f'tmp_{int(time.time())}.mp3')
        self.play_button.file_path = recorded_file_mp3

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

        self.play_button.disabled = False
        self.record_button.disabled = False
        self.status_label.text = app._('status_recording_stopped', app.locale)
        self.record_button.text = app._('button_record', app.locale)
        # print("Comparing:", self.listen_button.file_path, recorded_file_mp3)
        # result = AudioComparator().compare_audio(self.listen_button.file_path, recorded_file_mp3)
        # print("Comparison result:", result)

    def play_audio(self, instance):
        MediaController.play_sound(instance.file_path)
