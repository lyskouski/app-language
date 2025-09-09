import os
import numpy as np

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

class RecorderWidget(BoxLayout):
    def load_data(self):
        app = App.get_running_app()
        self.recording = False
        self.selected_file = None
        self.audio_files = self.load_audio_files()
        
        self.main_layout = BoxLayout(orientation='vertical')

        self.scroll_view = ScrollView()
        self.list_layout = GridLayout(cols=1, size_hint_y='1dp', minimum_height='0.8dp', spacing=5)
        
        for file_name, sentence in self.audio_files.items():
            row = BoxLayout(orientation='horizontal', size_hint_min_y=30)
            row.add_widget(Label(text=sentence.replace('\\n', '\n'), size_hint_x=0.8, halign='left'))
            choose_button = Button(text=app._('button_choose', app.locale), size_hint_x=0.2)
            choose_button.file_path = file_name
            choose_button.bind(on_release=self.choose_sentence)
            row.add_widget(choose_button)
            self.list_layout.add_widget(row)
        
        self.scroll_view.add_widget(self.list_layout)
        self.main_layout.add_widget(self.scroll_view)

        self.control_layout = BoxLayout(size_hint_y=None, height=50)
        self.listen_button = Button(text=app._('button_listen', app.locale), on_press=self.play_audio)
        self.listen_button.disabled = True
        self.status_label = Label(text=app._('status_select_sentence', app.locale), size_hint_y='0.2dp')
        self.record_button = Button(text=app._('button_record', app.locale), on_press=self.toggle_recording)
        self.play_button = Button(text=app._('button_play', app.locale), on_press=self.play_audio, disabled=True)

        self.control_layout.add_widget(self.listen_button)
        self.main_layout.add_widget(self.status_label)
        self.control_layout.add_widget(self.record_button)
        self.control_layout.add_widget(self.play_button)

        self.main_layout.add_widget(self.control_layout)
        self.add_widget(self.main_layout)
    
    def load_audio_files(self):
        app = App.get_running_app()
        audio_files = {}
        for line in app.store:
            key = line[2] if line[2] != '' else line[0] + '.mp3'
            audio_files[key] = line[0]
        return audio_files
    
    def choose_sentence(self, instance):
        self.listen_button.disabled = False
        self.listen_button.file_path = f"assets/data/PL/audio/{instance.file_path}"
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
        recorded_file = os.path.join(app.get_user_data_dir(), 'recorded_audio.wav')
        self.play_button.file_path = recorded_file

        buffer = []
        with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
            for _ in range(int(fs * max_duration / 1024)):
                if not self.recording:
                    break
                data, overflowed = stream.read(1024)
                buffer.append(data)
        if buffer:
            self.audio_data = np.concatenate(buffer, axis=0)
            sf.write(recorded_file, self.audio_data, fs)

        self.play_button.disabled = False
        self.record_button.disabled = False
        self.status_label.text = app._('status_recording_stopped', app.locale)
        self.record_button.text = app._('button_record', app.locale)

    def play_audio(self, instance):
        app = App.get_running_app()
        if os.path.exists(instance.file_path):
            music = MusicSDL2(source=instance.file_path)
            music.play()
        else:
            self.status_label.text = app._('error_not_found', app.locale)
