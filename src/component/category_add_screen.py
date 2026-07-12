# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

class CategoryAddScreen(Screen):
    """
    Screen for adding new categories to the database.
    Follows Clean Architecture principles with dependency injection.
    """
    category_name_text = StringProperty('')
    status_text = StringProperty('')

    def __init__(self, **kwargs):
        super(CategoryAddScreen, self).__init__(**kwargs)

    def _get_app(self):
        return App.get_running_app()

    def clear_form(self):
        """Clear all form fields."""
        self.category_name_text = ''
        self.status_text = ''

    def save_category(self):
        """
        Save a new category to the database.
        Uses dependency injection to get repository from container.
        """
        app = self._get_app()
        category_name = self.category_name_text.strip()

        # Validate required fields
        if not category_name:
            self.status_text = "Category name is required"
            return

        if not app.locale_from or not app.locale_to:
            self.status_text = "Please select a language pair first"
            return

        try:
            # Get repository from DI container
            config_repo = app._container.config_repository()

            # Add category to database (use category_name as vocabulary filter)
            config_repo.add_game_category(
                app.locale_from,
                app.locale_to,
                category_name,
                category_name
            )
            self.status_text = ''

            # Clear form and return to main screen
            self.clear_form()
            app.next_screen('main_screen')

        except ValueError as e:
            self.status_text = str(e)
            print(f"ERROR: {e}")
        except Exception as e:
            self.status_text = f"Failed to save category: {e}"
            print(f"ERROR saving category: {e}")
            import traceback
            traceback.print_exc()

    def cancel(self):
        """Cancel and return to main screen."""
        app = self._get_app()
        self.clear_form()
        app.next_screen('main_screen')
