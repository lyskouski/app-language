# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

class StructureScreen(Screen):
    def __init__(self, **kwargs):
        super(StructureScreen, self).__init__(**kwargs)
        # Get services from DI container
        app = App.get_running_app()
        self._config_repo = app._container.config_repository()
        self._localization_service = app._container.localization_service()

        self.load_data()
        Clock.schedule_once(lambda dt: self.populate_rv())

    def get_new_item(self):
        app = App.get_running_app()
        return [{
            'text': self._localization_service.translate('item_new', app.locale),
            'source': '',
            'indent': None,
            'logo': '',
            'store_path': '',
            'route_path': '',
            'locale_from': '',
            'locale_to': '',
        }]

    def get_data(self, path):
        """Load data from SQLite database."""
        # Load language pairs from database
        data = self._config_repo.get_all_language_pairs()
        data += self.get_new_item()
        for item in data:
            if isinstance(item, dict):
                item['parent_source'] = path
                item['indent'] = None
                item['is_expanded'] = False
        return data

    def load_data(self):
        self.data = self.get_data('root')

    def populate_rv(self):
        self.ids.structure_view.data = self.data

class StructureWidget(BoxLayout):
    source = StringProperty('')
    parent_source = StringProperty('')
    indent = NumericProperty(0, allownone=True)
    text = StringProperty('')
    logo = StringProperty('')
    store_path = StringProperty('')
    route_path = StringProperty('')
    locale_from = StringProperty('')
    locale_to = StringProperty('')
    is_expanded = BooleanProperty(False)

    def expand(self):
        app = App.get_running_app()
        screen = app.root.get_screen('structure_screen')
        new_data = screen.get_data(self.source)
        new_indent = (self.indent or 0) + 0.1
        for item in new_data:
            if isinstance(item, dict):
                item['indent'] = new_indent
        insert_idx = None
        for idx, item in enumerate(screen.data):
            if isinstance(item, dict) and item.get('text') == self.text:
                insert_idx = idx
                screen.data[idx]['is_expanded'] = True
                break
        if insert_idx is not None:
            screen.data = screen.data[:insert_idx+1] + new_data + screen.data[insert_idx+1:]
        else:
            screen.data += new_data
        screen.populate_rv()

    def collapse(self):
        app = App.get_running_app()
        screen = app.root.get_screen('structure_screen')
        data = []
        indent = None
        for _, item in enumerate(screen.data):
            if isinstance(item, dict):
                curr_indent = item.get('indent', 0)
                if (curr_indent is None):
                    curr_indent = 0
                if indent is not None and indent >= curr_indent:
                    indent = None
                if item.get('text') == self.text:
                    indent = curr_indent
                    item['is_expanded'] = False
                if indent is not None and indent < curr_indent:
                    continue
                data += [item]
        screen.data = data
        screen.populate_rv()
