# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.widget import Widget

class HarmonicaWidget(ScrollView):
    origin = BooleanProperty(False)
    secondary = BooleanProperty(False)
    loading_widget = None

    def __init__(self, **kwargs):
        super(HarmonicaWidget, self).__init__(**kwargs)
        # Cache vocabulary items for validation
        self._vocabulary_items = []

    def init_data(self, item):
        self.loading_widget = item

    def on_kv_post(self, base_widget):
        self.load_data()

    def load_data(self):
        """Load vocabulary items using vocabulary service."""
        self.clear_widgets()

        layout = GridLayout(cols=1, size_hint_y='2dp', spacing=5)
        layout.bind(minimum_height=layout.setter('height'))

        if self.loading_widget and hasattr(self.loading_widget, 'status'):
            self.loading_widget.status = 0

        app = App.get_running_app()

        # Use app's vocabulary service instance (has loaded data)
        # Fall back to app.store if service not available
        if app._vocabulary_service:
            self._vocabulary_items = app._vocabulary_service.get_current_study_set()
        else:
            # Use app.store as fallback (contains VocabularyItem objects)
            self._vocabulary_items = app.store

        for item in self._vocabulary_items:
            self.add_row(layout, item.origin, item.translation)
            # TODO: Update loading status (not reflecting, just a freeze)
            if self.loading_widget and hasattr(self.loading_widget, 'status'):
                self.loading_widget.status += 1

        self.add_widget(layout)

    def add_row(self, layout, origin, trans):
        row = BoxLayout(orientation='horizontal', size_hint_min_y=30)

        if self.origin and self.secondary:
            row.add_widget(Label(text=origin))
            row.add_widget(Label(text=trans))

        elif self.origin and not self.secondary:
            row.add_widget(Label(text=origin))
            text_input = TextInput(text='', multiline=False)
            text_input.bind(on_text_validate=lambda instance: self.validate(instance, origin, False))
            row.add_widget(text_input)

        elif not self.origin and self.secondary:
            row.add_widget(Label(text=trans))
            text_input = TextInput(text='', multiline=False)
            text_input.bind(on_text_validate=lambda instance: self.validate(instance, trans, True))
            row.add_widget(text_input)

        row.add_widget(Widget(size_hint_x=None, width=10))
        layout.add_widget(row)

    def validate(self, instance, key, is_origin):
        """Validate user input and mark item as correct/incorrect."""
        app = App.get_running_app()

        # Use app's vocabulary service instance
        if not app._vocabulary_service:
            return

        # Find the matching vocabulary item
        item = None
        for vocab_item in self._vocabulary_items:
            if vocab_item.origin == key and not is_origin or is_origin and vocab_item.translation == key:
                item = vocab_item
                break

        if not item:
            return

        text = instance.text.strip()
        answer = item.origin if is_origin else item.translation
        parent = instance.parent
        parent.remove_widget(instance)

        if (answer == text):
            icon = Image(source='assets/images/success.png', size_hint=(None, None), size=(30, 30))
            parent.add_widget(icon)
            parent.add_widget(Label(text=answer))
            app._vocabulary_service.mark_item_correct(item)
        else:
            icon = Image(source='assets/images/error.png', size_hint=(None, None), size=(30, 30))
            parent.add_widget(icon)
            parent.add_widget(Label(text=f'[s]{text}[/s] {answer}', markup=True))
            app._vocabulary_service.mark_item_incorrect(item)
