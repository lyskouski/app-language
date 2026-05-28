# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import threading
from statistics import mean

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
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
        self._audio_comparator = app._container.audio_comparator()

    def init_data(self, item):
        self.loading_widget = item

    def load_data(self):
        app = App.get_running_app()
        self.recording = False
        self.selected_file = None
        self.selected_sentence = ''
        self.comparison_result = []
        self._comparison_animation_event = None
        self._comparison_animation_direction = 1
        self.audio_files = self.load_audio_files()

        main_layout = BoxLayout(orientation='vertical')
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True)
        list_layout = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=[0, 0, 0, 5])
        list_layout.bind(minimum_height=list_layout.setter('height'))

        for file_name, sentence in self.audio_files.items():
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=36)
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

        comparison_header = Label(
            text=self._localization_service.translate('status_comparison_result', app.locale),
            size_hint_y=None,
            height=28
        )
        self.comparison_progress = ProgressBar(max=100, value=0, size_hint_y=None, height=8)
        self.comparison_scroll = ScrollView(size_hint_y=None, height=160)
        self.comparison_panel = GridLayout(cols=1, size_hint_y=None, spacing=4, padding=[4, 4, 4, 4])
        self.comparison_panel.bind(minimum_height=self.comparison_panel.setter('height'))
        self.comparison_scroll.add_widget(self.comparison_panel)

        main_layout.add_widget(control_layout)
        main_layout.add_widget(comparison_header)
        main_layout.add_widget(self.comparison_progress)
        main_layout.add_widget(self.comparison_scroll)
        self.clear_widgets()
        self.add_widget(main_layout)
        self._render_comparison_rows([])

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
        self.selected_sentence = self.audio_files.get(instance.file_path, '')
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
            self.recording = False
            self._set_recording_failed_ui(app.locale)

    def stop_audio(self):
        app = App.get_running_app()
        self._set_status(self._localization_service.translate('status_recording_stopped', app.locale))
        self._recorder_service.stop_recording()
        self._set_post_recording_controls()

        selected_file_path = getattr(self.listen_button, 'file_path', None)
        recorded_file_path = getattr(self.play_button, 'file_path', None)
        if not recorded_file_path:
            self._set_status(self._localization_service.translate('error_not_found', app.locale))
            return

        if not selected_file_path:
            self._set_status(self._localization_service.translate('status_comparison_missing_reference', app.locale))
            return

        self._set_status(self._localization_service.translate('status_comparing_audio', app.locale))
        self._compare_audio(selected_file_path, recorded_file_path)

    def _compare_audio(self, original_path, recorded_path):
        app = App.get_running_app()
        self._set_comparison_progress(0, 'status_comparison_preparing')
        if not self._audio_comparator or not self._audio_comparator.is_available():
            self._set_status(self._localization_service.translate('status_comparison_unavailable', app.locale))
            self._stop_comparison_animation(completed=False)
            self._render_comparison_rows([])
            return

        try:
            self._start_comparison_animation('status_comparison_processing')
            self.comparison_result = self._audio_comparator.compare_audio(
                original_path,
                recorded_path,
                getattr(self, 'selected_sentence', '')
            )
            score_values = [
                item.get('score', self._deviation_to_score(item.get('deviation', 100.0)))
                for item in self.comparison_result
                if isinstance(item, dict)
            ]

            if not score_values:
                self._set_status(self._localization_service.translate('status_comparison_error', app.locale))
                self._stop_comparison_animation(completed=False)
                self._render_comparison_rows([])
                return

            self._set_status(self._localization_service.translate('status_comparison_finalizing', app.locale))
            self._stop_comparison_animation(completed=True)
            overall_score = mean(score_values)
            details = ', '.join([f"W{idx + 1}: {score:.0f}%" for idx, score in enumerate(score_values[:3])])
            score_label = self._localization_service.translate('status_comparison_result', app.locale)
            self._set_status(f"{score_label}: {overall_score:.1f}% ({details})")
            self._render_comparison_rows(self.comparison_result)
        except Exception as exc:
            print(f"Error running audio comparison: {exc}")
            self._set_status(self._localization_service.translate('status_comparison_error', app.locale))
            self._stop_comparison_animation(completed=False)
            self._render_comparison_rows([])

    def _set_status(self, text):
        """Set status text on the main UI thread."""
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text), 0)

    def _set_recording_failed_ui(self, locale):
        """Reset controls when recording could not be started."""
        def update_ui(dt):
            self.record_button.text = self._localization_service.translate('button_record', locale)
            self.play_button.disabled = True

        Clock.schedule_once(update_ui, 0)

    def _set_post_recording_controls(self):
        """Restore controls after recording stops."""
        def update_ui(dt):
            app = App.get_running_app()
            self.record_button.text = self._localization_service.translate('button_record', app.locale)
            self.record_button.disabled = False
            self.play_button.disabled = not bool(getattr(self.play_button, 'file_path', None))

        Clock.schedule_once(update_ui, 0)

    def _set_comparison_progress(self, value, status_key=None):
        """Update comparison progress bar and optional status on the main UI thread."""
        app = App.get_running_app()
        progress_value = max(0, min(100, int(value)))

        def update_ui(dt):
            self.comparison_progress.value = progress_value
            if status_key:
                self.status_label.text = self._localization_service.translate(status_key, app.locale)

        Clock.schedule_once(update_ui, 0)

    def _start_comparison_animation(self, status_key=None):
        """Start indeterminate progress animation while comparison is running."""
        app = App.get_running_app()

        def start_ui(dt):
            if self._comparison_animation_event is not None:
                self._comparison_animation_event.cancel()
            self._comparison_animation_direction = 1
            self.comparison_progress.value = 12
            if status_key:
                self.status_label.text = self._localization_service.translate(status_key, app.locale)
            self._comparison_animation_event = Clock.schedule_interval(self._animate_comparison_progress, 0.08)

        Clock.schedule_once(start_ui, 0)

    def _stop_comparison_animation(self, completed):
        """Stop progress animation and set terminal bar value."""
        target = 100 if completed else 0

        def stop_ui(dt):
            if self._comparison_animation_event is not None:
                self._comparison_animation_event.cancel()
                self._comparison_animation_event = None
            self.comparison_progress.value = target

        Clock.schedule_once(stop_ui, 0)

    def _animate_comparison_progress(self, dt):
        """Animate progress bar back-and-forth in a bounded range."""
        next_value = self.comparison_progress.value + (self._comparison_animation_direction * 4)
        if next_value >= 90:
            next_value = 90
            self._comparison_animation_direction = -1
        elif next_value <= 12:
            next_value = 12
            self._comparison_animation_direction = 1
        self.comparison_progress.value = next_value

    def _render_comparison_rows(self, results):
        def update_ui(dt):
            app = App.get_running_app()
            self.comparison_panel.clear_widgets()

            if not results:
                self.comparison_panel.add_widget(Label(
                    text=self._localization_service.translate('status_comparison_no_segments', app.locale),
                    size_hint_y=None,
                    height=28
                ))
                return

            for item in results:
                if not isinstance(item, dict):
                    continue

                segment_no = int(item.get('word_index', item.get('second', 0)))
                score = float(item.get('score', self._deviation_to_score(item.get('deviation', 100.0))))
                feedback = item.get('feedback', '')
                word_value = item.get('word', '')
                if word_value:
                    row_text = f"{self._localization_service.translate('label_word_short', app.locale)} {segment_no} ({word_value}): {score:.1f}% - {feedback}"
                else:
                    row_text = f"{self._localization_service.translate('label_segment_short', app.locale)} {segment_no}: {score:.1f}% - {feedback}"
                self.comparison_panel.add_widget(Label(
                    text=row_text,
                    size_hint_y=None,
                    height=28,
                    halign='left',
                    text_size=(self.width - 20, None)
                ))

        Clock.schedule_once(update_ui, 0)

    def _deviation_to_score(self, deviation):
        """Convert MFCC distance value to 0-100 pronunciation score."""
        try:
            distance = max(float(deviation), 0.0)
        except (TypeError, ValueError):
            distance = 100.0
        return max(0.0, min(100.0, 100.0 / (1.0 + (distance / 25.0))))

    def play_audio(self, instance):
        if not getattr(instance, 'file_path', None):
            app = App.get_running_app()
            self.status_label.text = self._localization_service.translate('status_select_sentence', app.locale)
            return
        # Use MediaService to play audio
        app = App.get_running_app()
        media_service = app._container.media_service()
        media_service.play_audio(instance.file_path)
