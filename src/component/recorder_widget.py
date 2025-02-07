import os

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import sounddevice as sd
import soundfile as sf
import threading

class RecorderWidget(BoxLayout):
    def on_kv_post(self, base_widget):
        self.recording = False

        self.listen_button = Button(text="Listen", on_press=self.play_audio)
        self.listen_button.file_path = "assets/audio/skoregorkowa_001.mp3"
        #self.listen_button.file_path = "assets/audio/skoregorkowa_002.ogg"
        self.status_label = Label(text="Press 'Record' to start")
        self.record_button = Button(text="Record", on_press=self.toggle_recording)
        self.play_button = Button(text="Play", on_press=self.play_audio, disabled=True)
        self.play_button.file_path = os.path.join(App.get_running_app().user_data_dir, "recorded_audio.wav")

        self.add_widget(self.listen_button)
        self.add_widget(self.status_label)
        self.add_widget(self.record_button)
        self.add_widget(self.play_button)

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
            sound = SoundLoader.load(instance.file_path)
            if sound:
                sound.play()
        else:
            self.status_label.text = "Error: No recorded file found"
