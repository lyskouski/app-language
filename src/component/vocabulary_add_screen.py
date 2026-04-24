# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import Screen
from domain.entities.vocabulary_item import VocabularyItem


class VocabularyAddScreen(Screen):
    """
    Screen for adding new vocabulary items to the database.
    Follows Clean Architecture principles with dependency injection.
    """
    origin_text = StringProperty('')
    translation_text = StringProperty('')
    sound_path_text = StringProperty('')
    image_path_text = StringProperty('')
    category_text = StringProperty('dictionary')
    difficulty_text = StringProperty('0')
    
    categories = ListProperty(['dictionary', 'verbs', 'numbers', 'articulation'])

    def __init__(self, **kwargs):
        super(VocabularyAddScreen, self).__init__(**kwargs)

    def clear_form(self):
        """Clear all form fields."""
        self.origin_text = ''
        self.translation_text = ''
        self.sound_path_text = ''
        self.image_path_text = ''
        self.category_text = 'dictionary'
        self.difficulty_text = '0'

    def save_vocabulary_item(self):
        """
        Save a new vocabulary item to the database.
        Uses dependency injection to get repository from container.
        """
        app = App.get_running_app()

        # Validate required fields
        if not self.origin_text or not self.translation_text:
            print("ERROR: Origin and Translation are required fields")
            return

        if not app.locale_from or not app.locale_to:
            print("ERROR: Please select a language pair first")
            return

        try:
            # Get repository from DI container
            vocab_repo = app._container.vocabulary_repository()

            # Create vocabulary item entity
            new_item = VocabularyItem(
                origin=self.origin_text.strip(),
                translation=self.translation_text.strip(),
                sound=self.sound_path_text.strip() if self.sound_path_text else None,
                image=self.image_path_text.strip() if self.image_path_text else None
            )

            # Save to database
            vocab_repo.save_vocabulary_items(
                app.locale_from,
                app.locale_to,
                [new_item],
                replace=False  # Append, don't replace existing items
            )

            print(f"✓ Added vocabulary item: {new_item.origin} → {new_item.translation}")

            # Clear form and return to main screen
            self.clear_form()
            app.next_screen('main_screen')

        except Exception as e:
            print(f"ERROR saving vocabulary item: {e}")
            import traceback
            traceback.print_exc()

    def cancel(self):
        """Cancel and return to main screen."""
        app = App.get_running_app()
        self.clear_form()
        app.next_screen('main_screen')
