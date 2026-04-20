# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

class LanguageScreen(Screen):
    pass

class LanguageWidget(BoxLayout):
    data = ObjectProperty([])

    def __init__(self, **kwargs):
        super(LanguageWidget, self).__init__(**kwargs)
        # Get services from DI container
        app = App.get_running_app()
        self._resource_service = app._container.resource_service()
        self._settings_service = app._container.settings_service()

        self.load_languages()
        Clock.schedule_once(lambda dt: self.populate_languages())

    def load_languages(self):
        """Load available languages using resource service."""
        self.data = []
        source_path = self._resource_service.find_resource('assets/languages.json')
        if source_path and os.path.exists(source_path):
            with open(source_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def populate_languages(self):
        self.ids.language_view.data = [{
            'text': item.get('text', ''),
            'logo': item.get('logo', ''),
            'locale': item.get('locale', '')
        } for item in self.data]

    def select_language(self, locale):
        """Select language using settings service."""
        app = App.get_running_app()
        # Use settings service to update locale
        self._settings_service.update_interface_locale(locale)
        # Update app property for backward compatibility
        app.locale = locale
        app.next_screen('main_screen')
