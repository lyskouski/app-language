# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import Screen

from l18n.world_languages import WORLD_LANGUAGES


class LanguagePairAddScreen(Screen):
    """
    Screen for adding new language pairs to the database.
    Follows Clean Architecture principles with dependency injection.
    """
    from_language_text = StringProperty('')
    to_language_text = StringProperty('')
    locale_from_text = StringProperty('')
    locale_to_text = StringProperty('')
    name_text = StringProperty('')
    logo_path_text = StringProperty('')
    status_text = StringProperty('')

    # Available languages for dropdowns
    available_languages = ListProperty([])
    language_options = ListProperty([])

    def __init__(self, **kwargs):
        super(LanguagePairAddScreen, self).__init__(**kwargs)

    def _get_app(self):
        return App.get_running_app()

    def _build_language_catalog(self):
        """Return the canonical worldwide language list as locale/name tuples."""
        return [(locale, name, '') for locale, name in sorted(WORLD_LANGUAGES.items())]

    def _display_name_for(self, locale):
        """Return a selector label in the format 'CODE - Language name'."""
        name = next((name for code, name, _ in self.available_languages if code == locale), locale)
        return f"{locale} - {name}"

    def on_enter(self):
        """Load the full worldwide language list when the screen is entered."""
        try:
            self.available_languages = self._build_language_catalog()
            self.language_options = [self._display_name_for(locale) for locale, _, _ in self.available_languages]
        except Exception as e:
            print(f"ERROR loading languages: {e}")
            import traceback
            traceback.print_exc()

    def _resolve_locale_from_display(self, display_value):
        """Map a selector label back to the raw locale code."""
        if not display_value or ' - ' not in display_value:
            return display_value
        return display_value.split(' - ', 1)[0].strip()

    def select_from_language(self, locale):
        """Select source language."""
        value = self._resolve_locale_from_display(locale)
        self.from_language_text = value
        self.locale_from_text = value
        self.update_name_automatically()

    def select_to_language(self, locale):
        """Select target language."""
        value = self._resolve_locale_from_display(locale)
        self.to_language_text = value
        self.locale_to_text = value
        self.update_name_automatically()

    def clear_form(self):
        """Clear all form fields."""
        self.from_language_text = ''
        self.to_language_text = ''
        self.locale_from_text = ''
        self.locale_to_text = ''
        self.name_text = ''
        self.logo_path_text = ''
        self.status_text = ''

    def update_name_automatically(self):
        """
        Auto-generate name from selected languages.
        Called when locale_from or locale_to changes.
        """
        if self.locale_from_text and self.locale_to_text:
            # Find language names
            from_name = next((name for locale, name, logo in self.available_languages if locale == self.locale_from_text), self.locale_from_text)
            to_name = next((name for locale, name, logo in self.available_languages if locale == self.locale_to_text), self.locale_to_text)
            self.name_text = f"{self.locale_from_text}-{self.locale_to_text} ({from_name} - {to_name})"

    def save_language_pair(self):
        """
        Save a new language pair to the database.
        Uses dependency injection to get repository from container.
        """
        app = self._get_app()

        locale_from = self.locale_from_text.strip().upper()
        locale_to = self.locale_to_text.strip().upper()
        name = self.name_text.strip()

        # Validate required fields
        if not locale_from:
            self.status_text = "Source language is required"
            return

        if not locale_to:
            self.status_text = "Target language is required"
            return

        if not name:
            self.status_text = "Name is required"
            return

        if locale_from == locale_to:
            self.status_text = "Source and target languages must be different"
            return

        try:
            # Get repository from DI container
            config_repo = app._container.config_repository()

            if config_repo.get_language_pair(locale_from, locale_to) is not None:
                self.status_text = f"Language pair already exists: {locale_from}-{locale_to}"
                return

            # Add language pair to database
            pair_id = config_repo.add_language_pair(
                locale_from,
                locale_to,
                name,
                self.logo_path_text.strip() if self.logo_path_text else ''
            )

            print(f"✓ Language pair created: {name} (ID: {pair_id})")
            self.status_text = ""

            # Clear form and return to main screen
            self.clear_form()
            app.next_screen('main_screen')

        except ValueError as e:
            self.status_text = str(e)
            print(f"ERROR: {e}")
        except Exception as e:
            self.status_text = f"Failed to save language pair: {e}"
            print(f"ERROR saving language pair: {e}")
            import traceback
            traceback.print_exc()

    def cancel(self):
        """Cancel and return to main screen."""
        app = self._get_app()
        self.clear_form()
        app.next_screen('main_screen')
