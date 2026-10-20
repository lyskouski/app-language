# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

class SettingsScreen(Screen):
    pass

class SettingsWidget(BoxLayout):
    data = ListProperty([])
    language_options = ListProperty([])
    language_text = StringProperty('')

    def __init__(self, **kwargs):
        super(SettingsWidget, self).__init__(**kwargs)
        # Defer initialization until app is fully ready
        Clock.schedule_once(lambda dt: self._init_widget(), 0.1)

    def _get_app(self):
        return App.get_running_app()

    def _init_widget(self):
        """Initialize widget after app is ready."""
        try:
            # Get services from DI container
            app = self._get_app()
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

    def populate_languages(self):
        """Fill the language selector, showing the current interface language."""
        try:
            if not hasattr(self, 'ids') or 'language_selector' not in self.ids:
                print("ERROR: language_selector not found in ids, retrying...")
                Clock.schedule_once(lambda dt: self.populate_languages(), 0.2)
                return

            app = self._get_app()
            self.language_options = [item.get('text', '') for item in self.data]
            self.language_text = next(
                (item.get('text', '') for item in self.data if item.get('locale') == app.locale),
                ''
            )
        except Exception as e:
            print(f"ERROR in populate_languages: {e}")
            import traceback
            traceback.print_exc()

    def select_language(self, name):
        """Select language by its display name using settings service."""
        locale = next((item.get('locale', '') for item in self.data if item.get('text') == name), '')
        app = self._get_app()
        if not locale or locale == app.locale:
            return
        is_first_choice = not app.locale
        self.language_text = name
        # Use settings service to update locale
        self._settings_service.update_interface_locale(locale)
        # Update app property for backward compatibility
        app.locale = locale
        # First launch: continue to the main screen as soon as a language is chosen
        if is_first_choice:
            app.next_screen('main_screen')

    def go_back(self):
        """Return to the main screen once an interface language is chosen."""
        app = self._get_app()
        if app.locale:
            app.next_screen('main_screen')
