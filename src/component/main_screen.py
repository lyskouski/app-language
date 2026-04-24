# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

class MainScreen(Screen):
    pass

class RootWidget(BoxLayout):
    data = ObjectProperty([])
    path = StringProperty('root')  # Changed from JSON path to navigation state

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        # Defer initialization until app is fully ready
        Clock.schedule_once(lambda dt: self._init_widget(), 0.1)

    def _init_widget(self):
        """Initialize widget after app is ready."""
        try:
            # Get services from DI container
            app = App.get_running_app()
            if not app or not hasattr(app, '_container'):
                print("ERROR: App not ready or missing container!")
                return

            self._config_repo = app._container.config_repository()

            self.load_data()
            Clock.schedule_once(lambda dt: self.populate_rv(), 0.1)
        except Exception as e:
            print(f"ERROR in MainScreen._init_widget: {e}")
            import traceback
            traceback.print_exc()

    def load_breadcrumb(self, path):
        breadcrumbs = self.ids.breadcrumb_view.data
        cut_index = None
        for i, crumb in enumerate(breadcrumbs):
            if crumb.get('source') == path:
                cut_index = i
                break
        if cut_index is not None:
            self.path = path
            self.ids.breadcrumb_view.data = breadcrumbs[:cut_index]
        self.load_data(path)
        self.populate_rv()

    def load_data(self, path = None):
        """Load data from SQLite database."""
        self.data = []
        if not path:
            path = self.path

        # Load language pairs from database
        self.data = self._config_repo.get_all_language_pairs()
        print(f"DEBUG: MainScreen loaded {len(self.data)} language pairs")

    def update_data(self, info):
        app = App.get_running_app()
        if (info.store_path != ''):
            app.init_store(info.store_path)
        if (info.locale_from != ''):
            app.locale_from = info.locale_from
        if (info.locale_to != ''):
            app.locale_to = info.locale_to
        if not self.ids.breadcrumb_view.data:
            self.ids.breadcrumb_view.data = []
            self.path = 'root'
        self.ids.breadcrumb_view.data.append({'text': info.text, 'source': self.path})
        self.path = info.source
        self.load_data()
        self.populate_rv()

    def populate_rv(self):
        """Populate the RecycleView with data."""
        try:
            if not hasattr(self, 'ids') or 'recycle_view' not in self.ids:
                print("ERROR: recycle_view not found in ids, retrying...")
                Clock.schedule_once(lambda dt: self.populate_rv(), 0.2)
                return

            print(f"DEBUG: MainScreen populating RecycleView with {len(self.data)} items")
            self.ids.recycle_view.data = self.data
            print("DEBUG: MainScreen RecycleView data set successfully")
        except Exception as e:
            print(f"ERROR in populate_rv: {e}")
            import traceback
            traceback.print_exc()
