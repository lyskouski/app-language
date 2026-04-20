# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

class StoreUpdateScreen(Screen):
    data = StringProperty('original ; translation ; sound path')
    store_path = StringProperty('')

    def __init__(self, **kwargs):
        super(StoreUpdateScreen, self).__init__(**kwargs)
        # Get services from DI container
        app = App.get_running_app()
        self._resource_service = app._container.resource_service()

    def init_data(self, widget):
        """Initialize data using resource service."""
        self.store_path = widget.store_path
        path = self._resource_service.find_resource(self.store_path)
        lines = []
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.data = ''.join(lines)

    def save_data(self):
        """Save data using resource service."""
        path = self._resource_service.get_path_with_home(self.store_path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.data)
