# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from component.harmonica_widget import HarmonicaWidget
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

class PhoneticsWidget(HarmonicaWidget):
    def __init__(self, **kwargs):
        super(PhoneticsWidget, self).__init__(**kwargs)
        # Get services from DI container
        app = App.get_running_app()
        self._localization_service = app._container.localization_service()

    def add_row(self, layout, origin, trans):
        app = App.get_running_app()
        # Use MediaService from container
        media_service = app._container.media_service(app.locale_to, app.get_audio_dir())
        row = BoxLayout(orientation='horizontal', size_hint_min_y=30)

        listen_button = Button(text=self._localization_service.translate('button_listen', app.locale), on_press=self.play_audio)
        listen_button.origin_value = origin
        listen_button.file_path = media_service.get_audio_file(origin)

        if self.origin and self.secondary:
            row.add_widget(Label(text=origin))
            row.add_widget(listen_button)
            row.add_widget(Label(text=trans))

        elif self.origin and not self.secondary:
            row.add_widget(listen_button)
            text_input = TextInput(text='', multiline=False)
            text_input.bind(on_text_validate=lambda instance: self.validate(instance, origin, False))
            row.add_widget(text_input)

        elif not self.origin and self.secondary:
            row.add_widget(listen_button)
            text_input = TextInput(text='', multiline=False)
            text_input.bind(on_text_validate=lambda instance: self.validate(instance, trans, True))
            row.add_widget(text_input)

        row.add_widget(Widget(size_hint_x=None, width=10))
        layout.add_widget(row)

    def play_audio(self, instance):
        app = App.get_running_app()
        media_service = app._container.media_service()
        media_service.play_audio(instance.file_path)
