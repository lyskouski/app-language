# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

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
        # Defer initialization until app is fully ready
        Clock.schedule_once(lambda dt: self._init_widget(), 0.1)

    def _init_widget(self):
        """Initialize widget after app is ready."""
        try:
            # Get services from DI container
            app = App.get_running_app()
            if not app:
                print("ERROR: No running app found!")
                return

            if not hasattr(app, '_container'):
                print("ERROR: App has no _container attribute!")
                return

            self._config_repo = app._container.config_repository()
            self._settings_service = app._container.settings_service()

            self.load_languages()
            Clock.schedule_once(lambda dt: self.populate_languages(), 0.1)
        except Exception as e:
            print(f"ERROR in _init_widget: {e}")
            import traceback
            traceback.print_exc()

    def load_languages(self):
        """Load available languages from SQLite database."""
        self.data = self._config_repo.get_all_languages()
        print(f"DEBUG: Loaded {len(self.data)} languages")

    def populate_languages(self):
        """Populate the RecycleView with language data."""
        try:
            if not hasattr(self, 'ids') or 'language_view' not in self.ids:
                print("ERROR: language_view not found in ids, retrying...")
                Clock.schedule_once(lambda dt: self.populate_languages(), 0.2)
                return

            data_for_rv = [{
                'text': item.get('text', ''),
                'logo': item.get('logo', ''),
                'locale': item.get('locale', '')
            } for item in self.data]
            print(f"DEBUG: Populating RecycleView with {len(data_for_rv)} items")
            self.ids.language_view.data = data_for_rv
            print("DEBUG: RecycleView data set successfully")
        except Exception as e:
            print(f"ERROR in populate_languages: {e}")
            import traceback
            traceback.print_exc()

    def select_language(self, locale):
        """Select language using settings service."""
        app = App.get_running_app()
        # Use settings service to update locale
        self._settings_service.update_interface_locale(locale)
        # Update app property for backward compatibility
        app.locale = locale
        app.next_screen('main_screen')
