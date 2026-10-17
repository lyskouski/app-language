# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

class CardWidget(Button):
    text_init = StringProperty('')
    text_flip = StringProperty('')
    fallback_background_color = ListProperty([1.0, 1.0, 1.0, 1.0])

class CardLayoutWidget(StackLayout):
    flip = BooleanProperty(False)
    # Side length of a (square) card, recalculated on resize and rotation
    card_side = NumericProperty(dp(150))

    def __init__(self, **kwargs):
        super(CardLayoutWidget, self).__init__(**kwargs)
        # Get services from DI container
        app = App.get_running_app()
        self._resource_service = app._container.resource_service()
        self.bind(size=self._update_card_side, spacing=self._update_card_side)
        app.bind(is_portrait=self._update_card_side)

    def _update_card_side(self, *_):
        if App.get_running_app().is_portrait:
            # Fill the narrow width with 2+ even columns instead of leaving a ragged gap
            columns = max(2, int(self.width // dp(200)))
            self.card_side = max(dp(100), (self.width - self.spacing[0] * (columns - 1)) / columns - 1)
        else:
            self.card_side = max(dp(150), min(self.width * 0.24, self.height * 0.24))

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
            image = self._resource_service.find_resource(f"{path}/{item.image}") if item.image else None
            if image:
                button.background_normal = image
                button.background_down = image
            else:
                button.background_normal = ''
                button.background_down = ''
            self.add_widget(button)
