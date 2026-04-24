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
    icon_path_text = StringProperty('')
    display_order_text = StringProperty('0')

    def __init__(self, **kwargs):
        super(CategoryAddScreen, self).__init__(**kwargs)

    def clear_form(self):
        """Clear all form fields."""
        self.category_name_text = ''
        self.icon_path_text = ''
        self.display_order_text = '0'

    def save_category(self):
        """
        Save a new category to the database.
        Uses dependency injection to get repository from container.
        """
        app = App.get_running_app()

        # Validate required fields
        if not self.category_name_text:
            print("ERROR: Category name is required")
            return

        if not app.locale_from or not app.locale_to:
            print("ERROR: Please select a language pair first")
            return

        try:
            # Get repository from DI container
            config_repo = app._container.config_repository()

            print(f"→ Saving category '{self.category_name_text}' for {app.locale_from}→{app.locale_to}")

            # Add category to database
            category_id = config_repo.add_game_category(
                app.locale_from,
                app.locale_to,
                self.category_name_text.strip(),
                self.icon_path_text.strip() if self.icon_path_text else None,
                int(self.display_order_text) if self.display_order_text else 0
            )

            print(f"✓ Added category: {self.category_name_text} (ID: {category_id}) for {app.locale_from}→{app.locale_to}")

            # Clear form and return to main screen
            self.clear_form()
            app.next_screen('main_screen')

        except Exception as e:
            print(f"ERROR saving category: {e}")
            import traceback
            traceback.print_exc()

    def cancel(self):
        """Cancel and return to main screen."""
        app = App.get_running_app()
        self.clear_form()
        app.next_screen('main_screen')
