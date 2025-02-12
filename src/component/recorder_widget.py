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
    def on_kv_post(self, base_widget):
        self.recording = False
        self.selected_file = None
        self.audio_files = self.load_audio_files()
        
        self.main_layout = BoxLayout(orientation='vertical')

        self.scroll_view = ScrollView()
        self.list_layout = GridLayout(cols=1, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        for file_name, sentence in self.audio_files.items():
            row = BoxLayout(orientation='horizontal')
            row.add_widget(Label(text=sentence, size_hint_x=0.8))
            choose_button = Button(text="Choose", size_hint_x=0.2)
            choose_button.file_path = file_name
            choose_button.bind(on_release=self.choose_sentence)
            row.add_widget(choose_button)
            self.list_layout.add_widget(row)
        
        self.scroll_view.add_widget(self.list_layout)
        self.main_layout.add_widget(self.scroll_view)

        self.control_layout = BoxLayout(size_hint_y=None, height=50)
        self.listen_button = Button(text="Listen", on_press=self.play_audio)
        self.listen_button.disabled = True
        self.status_label = Label(text="Select a sentence")
        self.record_button = Button(text="Record", on_press=self.toggle_recording)
        self.play_button = Button(text="Play", on_press=self.play_audio, disabled=True)

        self.control_layout.add_widget(self.listen_button)
        self.main_layout.add_widget(self.status_label)
        self.control_layout.add_widget(self.record_button)
        self.control_layout.add_widget(self.play_button)

        self.main_layout.add_widget(self.control_layout)
        self.add_widget(self.main_layout)
    
    def load_audio_files(self):
        audio_path = "assets/audio/parrot.txt"
        audio_files = {}
        try:
            with open(audio_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if ":" in line:
                        file_name, sentence = line.strip().split(":", 1)
                        audio_files[file_name.strip()] = sentence.strip()
        except FileNotFoundError:
            print("Error: parrot.txt not found!")
        return audio_files
    
    def choose_sentence(self, instance):
        self.listen_button.disabled = False
        self.listen_button.file_path = f"assets/audio/{instance.file_path}"
        self.status_label.text = f"Selected: {self.audio_files.get(instance.file_path, '')}"
    
    def toggle_recording(self, instance):
        if not self.recording:
            self.recording = True
            self.status_label.text = "Recording..."
            self.record_button.text = "Stop Recording"
            self.play_button.disabled = True

            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()
        else:
            self.recording = False
            self.status_label.text = "Saving..."
            self.record_button.text = "Processing"
            self.record_button.disabled = True
    
    def record_audio(self):       
        fs = 44100
        max_duration = 15
        recorded_file = os.path.join(App.get_running_app().user_data_dir, "recorded_audio.wav")
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
        self.status_label.text = "Recording stopped"
        self.record_button.text = "Record"
    
    def play_audio(self, instance):
        if os.path.exists(instance.file_path):
            music = MusicSDL2(source=instance.file_path)
            music.play()
        else:
            self.status_label.text = "Error: No recorded file found"
