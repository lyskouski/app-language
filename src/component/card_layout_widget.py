# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout


class CardWidget(Button):
    text_init = StringProperty('')
    text_flip = StringProperty('')

class CardLayoutWidget(StackLayout):
    flip = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CardLayoutWidget, self).__init__(**kwargs)
        # Get services from DI container
        app = App.get_running_app()
        self._resource_service = app._container.resource_service()

    def load_data(self):
        """Load vocabulary items using vocabulary service."""
        app = App.get_running_app()

        self.clear_widgets()
        # Use app's vocabulary service or fall back to app.store
        vocabulary_items = app._vocabulary_service.get_current_study_set() if app._vocabulary_service else app.store

        for item in vocabulary_items:
            button = CardWidget()
            button.text_init = item.translation if self.flip else item.origin
            button.text_flip = item.origin if self.flip else item.translation
            path = app.get_image_dir()
            image = self._resource_service.find_resource(f"{path}/{item.image}" if item.image else 'assets/images/error.png')
            button.background_normal = image if image else self._resource_service.find_resource('assets/images/error.png')
            button.background_down = self._resource_service.find_resource('assets/images/success.png')
            self.add_widget(button)
