# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import threading

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

class MultilineLabel(Label):
    pass

class RecorderWidget(BoxLayout):
    loading_widget = None

    def __init__(self, **kwargs):
        super(RecorderWidget, self).__init__(**kwargs)
        # Get services from DI container
        app = App.get_running_app()
        self._recorder_service = app._container.recorder_service()
        self._localization_service = app._container.localization_service()

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
            choose_button = Button(text=self._localization_service.translate('button_choose', app.locale), size_hint_x=0.2)
            choose_button.file_path = file_name
            choose_button.bind(on_release=self.choose_sentence)
            row.add_widget(choose_button)
            list_layout.add_widget(row)

        scroll_view.add_widget(list_layout)
        main_layout.add_widget(scroll_view)

        control_layout = BoxLayout(size_hint_y=None, height=50)
        self.listen_button = Button(text=self._localization_service.translate('button_listen', app.locale), on_press=self.play_audio)
        self.listen_button.disabled = True
        self.status_label = Label(text=self._localization_service.translate('status_select_sentence', app.locale), size_hint_y='0.2dp')
        self.record_button = Button(text=self._localization_service.translate('button_record', app.locale), on_press=self.toggle_recording)
        self.play_button = Button(text=self._localization_service.translate('button_play', app.locale), on_press=self.play_audio, disabled=True)

        status = self._recorder_service.get_initial_status()
        self.record_button.disabled = not status

        control_layout.add_widget(self.listen_button)
        main_layout.add_widget(self.status_label)
        control_layout.add_widget(self.record_button)
        control_layout.add_widget(self.play_button)

        main_layout.add_widget(control_layout)
        self.clear_widgets()
        self.add_widget(main_layout)

    def load_audio_files(self):
        """Load audio files using vocabulary service."""
        app = App.get_running_app()
        media_service = app._container.media_service(app.locale_to, app.get_audio_dir())

        audio_files = {}
        # Use app's vocabulary service or fall back to app.store
        vocabulary_items = app._vocabulary_service.get_current_study_set() if app._vocabulary_service else app.store

        for item in vocabulary_items:
            key = item.sound if item.sound else item.origin + '.mp3'
            audio_files[media_service.get_audio_file(item.origin, key)] = item.origin
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
            self.status_label.text = self._localization_service.translate('status_recording', app.locale)
            self.record_button.text = self._localization_service.translate('button_stop_recording', app.locale)
            self.play_button.disabled = True

            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()
        else:
            self.recording = False
            self.status_label.text = self._localization_service.translate('status_saving', app.locale)
            self.record_button.text = self._localization_service.translate('button_processing', app.locale)
            self.record_button.disabled = True

            self.audio_thread = threading.Thread(target=self.stop_audio)
            self.audio_thread.start()

    def record_audio(self):
        path = self._recorder_service.start_recording()
        if path:
            self.play_button.file_path = path
            max_duration = 15
            Clock.schedule_once(lambda dt: self.stop_audio(), max_duration)
        else:
            app = App.get_running_app()
            self.record_button.text = self._localization_service.translate('button_record', app.locale)
            self.recording = False
            self.play_button.disabled = True

    def stop_audio(self):
        app = App.get_running_app()
        self.status_label.text = self._localization_service.translate('status_recording_stopped', app.locale)
        self._recorder_service.stop_recording()
        self.record_button.text = self._localization_service.translate('button_record', app.locale)
        self.record_button.disabled = False
        self.play_button.disabled = not bool(getattr(self.play_button, 'file_path', None))
        # print("Comparing:", self.listen_button.file_path, recorded_file_mp3)
        # result = AudioComparator().compare_audio(self.listen_button.file_path, recorded_file_mp3)
        # print("Comparison result:", result)

    def play_audio(self, instance):
        if not getattr(instance, 'file_path', None):
            app = App.get_running_app()
            self.status_label.text = self._localization_service.translate('status_select_sentence', app.locale)
            return
        # Use MediaService to play audio
        app = App.get_running_app()
        media_service = app._container.media_service()
        media_service.play_audio(instance.file_path)
