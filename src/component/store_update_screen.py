# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from domain.entities.vocabulary_item import VocabularyItem

class StoreUpdateScreen(Screen):
    """Screen for editing vocabulary items for a category from the database."""
    data = StringProperty('origin ; translation ; sound path')
    store_path = StringProperty('')  # Category/vocabulary_source name

    def __init__(self, **kwargs):
        super(StoreUpdateScreen, self).__init__(**kwargs)
        app = App.get_running_app()
        self._vocab_repo = app._container.vocabulary_repository()

    def init_data(self, widget):
        """Load vocabulary items from database for the given category."""
        app = App.get_running_app()
        self.store_path = widget.store_path  # This is the vocabulary_source (category name)

        # Load vocabulary items from database for current language pair and category
        if app.locale_from and app.locale_to and self.store_path:
            items = self._vocab_repo.load_by_language_pair(
                app.locale_from,
                app.locale_to,
                self.store_path
            )
            # Format as semicolon-separated lines
            lines = []
            for item in items:
                parts = [item.origin, item.translation]
                if item.sound:
                    parts.append(item.sound)
                if item.image:
                    parts.append(item.image)
                lines.append(';'.join(parts))
            self.data = '\n'.join(lines)
        else:
            self.data = ''

    def save_data(self):
        """Parse edited content and save vocabulary items to database."""
        app = App.get_running_app()
        if not (app.locale_from and app.locale_to and self.store_path):
            print('ERROR: Missing locale or category information')
            return

        # Parse the edited text
        new_items = []
        for line in self.data.strip().split('\n'):
            line = line.strip()
            if not line or ';' not in line:
                continue

            parts = [p.strip() for p in line.split(';')]
            if len(parts) >= 2:
                origin = parts[0]
                translation = parts[1]
                sound = parts[2] if len(parts) > 2 else None
                image = parts[3] if len(parts) > 3 else None

                try:
                    item = VocabularyItem(
                        origin=origin,
                        translation=translation,
                        sound=sound,
                        image=image,
                        category=self.store_path
                    )
                    new_items.append(item)
                except ValueError as e:
                    print(f"Warning: Skipping invalid item: {e}")

        # Load existing items for other categories and merge
        all_items = self._vocab_repo.load_by_language_pair(app.locale_from, app.locale_to)
        # Keep items from other categories, replace items for this category
        merged_items = [item for item in all_items if item.category != self.store_path]
        merged_items.extend(new_items)

        # Save all items to database (replace all for language pair)
        if hasattr(self._vocab_repo, 'save_vocabulary_items'):
            self._vocab_repo.save_vocabulary_items(
                app.locale_from,
                app.locale_to,
                merged_items,
                replace=True
            )
            print(f"Saved {len(new_items)} vocabulary items for {app.locale_from}-{app.locale_to} ({self.store_path})")

            # Refresh app.store with updated vocabulary so games see new items
            app.store.clear()
            app.store.extend(merged_items)

            # If vocabulary service exists, update its study set too
            if hasattr(app, '_vocabulary_service') and app._vocabulary_service:
                app._vocabulary_service._current_items = merged_items
                app._vocabulary_service.prepare_study_set(len(merged_items), force_shuffle=False)
        else:
            print('ERROR: Repository does not support save_vocabulary_items')
