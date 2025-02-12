import os

from kivy.app import App
from kivy.core.audio.audio_sdl2 import MusicSDL2
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
import sounddevice as sd
import soundfile as sf
import threading

class RecorderWidget(BoxLayout):
    def on_kv_post(self, base_widget):
        self.recording = False
        self.audio_files = self.load_audio_files()

        self.spinner = Spinner(text='Select Audio', values=list(self.audio_files.keys()))
        self.spinner.bind(text=self.on_audio_selected)
        self.listen_button = Button(text="Listen", on_press=self.play_audio)
        self.listen_button.file_path = "assets/audio/skoregorkowa_001.mp3"
        self.status_label = Label(text="Press 'Record' to start")
        self.record_button = Button(text="Record", on_press=self.toggle_recording)
        self.play_button = Button(text="Play", on_press=self.play_audio, disabled=True)
        self.play_button.file_path = os.path.join(App.get_running_app().user_data_dir, "recorded_audio.wav")

        self.add_widget(self.spinner)
        self.add_widget(self.listen_button)
        self.add_widget(self.status_label)
        self.add_widget(self.record_button)
        self.add_widget(self.play_button)

    def load_audio_files(self):
        audio_dict = {}
        try:
            with open("assets/audio/parrot.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        filename, text = line.strip().split(":", 1)
                        audio_dict[filename.strip()] = text.strip()
        except FileNotFoundError:
            print("Error: parrot.txt not found!")
        return audio_dict

    def on_audio_selected(self, spinner, text):
        self.listen_button.file_path = f"assets/audio/{text}"

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
            self.status_label.text = "Recording stopped"
            self.record_button.text = "Record"
            self.play_button.disabled = False

    def record_audio(self):
        fs = 44100
        duration = 15
        self.audio_data = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        sf.write(self.play_button.file_path, self.audio_data, fs)

    def play_audio(self, instance):
        if os.path.exists(instance.file_path):
            music = MusicSDL2(source=instance.file_path)
            music.play()
            #sound = SoundLoader.load(instance.file_path)
            #if sound:
            #    sound.play()
        else:
            self.status_label.text = "Error: No recorded file found"
