import os
import numpy as np
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
import sounddevice as sd
import soundfile as sf
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
        app = App.get_running_app()
        fs = 44100
        max_duration = 15
        recorded_file = os.path.join(app.get_home_dir(), f'tmp_{int(time.time())}.wav')
        self.play_button.file_path = recorded_file

        buffer = []
        with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
            for _ in range(int(fs * max_duration / 1024)):
                if not self.recording:
                    break
                data, __ = stream.read(1024)
                buffer.append(data)
        if buffer:
            self.audio_data = np.concatenate(buffer, axis=0)
            if hasattr(self, 'music') and self.music:
                try:
                    self.music.stop()
                except Exception:
                    pass
                self.music = None
            for _ in range(5):
                try:
                    if os.path.exists(recorded_file):
                        os.remove(recorded_file)
                    break
                except PermissionError:
                    time.sleep(0.2)
            sf.write(recorded_file, self.audio_data, fs)

        self.play_button.disabled = False
        self.record_button.disabled = False
        self.status_label.text = app._('status_recording_stopped', app.locale)
        self.record_button.text = app._('button_record', app.locale)
        print("Comparing:", self.listen_button.file_path, recorded_file)
        result = AudioComparator().compare_audio(self.listen_button.file_path, recorded_file)
        print("Comparison result:", result)

    def play_audio(self, instance):
        MediaController.play_sound(instance.file_path)
