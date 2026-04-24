# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import Screen


class LanguagePairAddScreen(Screen):
    """
    Screen for adding new language pairs to the database.
    Follows Clean Architecture principles with dependency injection.
    """
    locale_from_text = StringProperty('')
    locale_to_text = StringProperty('')
    name_text = StringProperty('')
    logo_path_text = StringProperty('')

    # Available languages for dropdowns
    available_languages = ListProperty([])

    def __init__(self, **kwargs):
        super(LanguagePairAddScreen, self).__init__(**kwargs)

    def on_enter(self):
        """Load available languages when screen is entered."""
        app = App.get_running_app()
        try:
            config_repo = app._container.config_repository()
            languages = config_repo.get_all_languages()
            self.available_languages = [(lang['locale'], lang['text']) for lang in languages]
        except Exception as e:
            print(f"ERROR loading languages: {e}")
            import traceback
            traceback.print_exc()

    def clear_form(self):
        """Clear all form fields."""
        self.locale_from_text = ''
        self.locale_to_text = ''
        self.name_text = ''
        self.logo_path_text = ''

    def update_name_automatically(self):
        """
        Auto-generate name from selected languages.
        Called when locale_from or locale_to changes.
        """
        if self.locale_from_text and self.locale_to_text:
            # Find language names
            from_name = next((name for locale, name in self.available_languages if locale == self.locale_from_text), self.locale_from_text)
            to_name = next((name for locale, name in self.available_languages if locale == self.locale_to_text), self.locale_to_text)
            self.name_text = f"{self.locale_from_text}-{self.locale_to_text} ({from_name} - {to_name})"

    def save_language_pair(self):
        """
        Save a new language pair to the database.
        Uses dependency injection to get repository from container.
        """
        app = App.get_running_app()

        # Validate required fields
        if not self.locale_from_text:
            print("ERROR: Source language is required")
            return

        if not self.locale_to_text:
            print("ERROR: Target language is required")
            return

        if not self.name_text:
            print("ERROR: Name is required")
            return

        if self.locale_from_text == self.locale_to_text:
            print("ERROR: Source and target languages must be different")
            return

        try:
            # Get repository from DI container
            config_repo = app._container.config_repository()

            # Add language pair to database
            pair_id = config_repo.add_language_pair(
                self.locale_from_text,
                self.locale_to_text,
                self.name_text.strip(),
                self.logo_path_text.strip() if self.logo_path_text else ''
            )

            print(f"✓ Language pair created: {self.name_text} (ID: {pair_id})")

            # Clear form and return to main screen
            self.clear_form()
            app.next_screen('main_screen')

        except Exception as e:
            print(f"ERROR saving language pair: {e}")
            import traceback
            traceback.print_exc()

    def cancel(self):
        """Cancel and return to main screen."""
        app = App.get_running_app()
        self.clear_form()
        app.next_screen('main_screen')
