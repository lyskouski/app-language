# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen


class DictionaryManagementScreen(Screen):
    """Screen for managing vocabulary items in the current study set."""

    def on_enter(self):
        """Reload data when screen becomes visible."""
        if hasattr(self, 'ids') and 'management_widget' in self.ids:
            widget = self.ids.management_widget
            widget.load_vocabulary_items()
            Clock.schedule_once(lambda dt: widget.populate_rv(), 0.1)


class DictionaryManagementWidget(BoxLayout):
    data = ObjectProperty([])
    selected_items = ListProperty([])
    _populating = False  # Guard against recursive calls

    def __init__(self, **kwargs):
        super(DictionaryManagementWidget, self).__init__(**kwargs)
        # Defer initialization until app is fully ready
        Clock.schedule_once(lambda dt: self._init_widget(), 0.1)

    def _init_widget(self):
        """Initialize widget after app is ready."""
        try:
            app = App.get_running_app()
            if not app:
                print("ERROR: No running app found!")
                return

            # Get main screen context to know which category/path we're on
            if hasattr(app, 'root') and app.root and 'main_screen' in app.root.screen_names:
                main_screen = app.root.get_screen('main_screen')
                if hasattr(main_screen, 'ids') and 'root_widget' in main_screen.ids:
                    root_widget = main_screen.ids.root_widget
                    # Store reference to root widget for context
                    self._root_widget = root_widget

            self.load_vocabulary_items()
            Clock.schedule_once(lambda dt: self.populate_rv(), 0.1)
        except Exception as e:
            print(f"ERROR in DictionaryManagementWidget._init_widget: {e}")
            import traceback
            traceback.print_exc()

    def load_vocabulary_items(self):
        """Load vocabulary items for the currently selected category."""
        try:
            app = App.get_running_app()
            self.data = []

            # Get main screen context to extract category ID
            if hasattr(app, 'root') and app.root and 'main_screen' in app.root.screen_names:
                main_screen = app.root.get_screen('main_screen')
                if hasattr(main_screen, 'ids') and 'root_widget' in main_screen.ids:
                    root_widget = main_screen.ids.root_widget
                    path = root_widget.path

                    # Extract category ID from path like "category_5"
                    if path and path.startswith('category_'):
                        try:
                            category_id = int(path.split('_')[1])

                            # Get config repository to find category info
                            config_repo = app._container.config_repository()

                            # Load all vocabulary for this language pair first
                            vocab_repo = app._container.vocabulary_repository()
                            all_vocab = vocab_repo.load_by_language_pair(app.locale_from, app.locale_to)

                            # Convert to dicts and keep track
                            vocab_dicts = []
                            for item in all_vocab:
                                vocab_dicts.append({
                                    'origin': item.origin,
                                    'translation': item.translation,
                                    'sound': getattr(item, 'sound', ''),
                                    'image': getattr(item, 'image', ''),
                                    'category': getattr(item, 'category', '')
                                })

                            # For now, use all vocabulary items from the language pair
                            # In a real scenario, vocabulary_items table should have category_id foreign key
                            self.data = vocab_dicts
                            print(f"DEBUG: Loaded {len(self.data)} vocabulary items for language pair {app.locale_from}-{app.locale_to}")
                        except (IndexError, ValueError) as e:
                            print(f"ERROR: Could not parse category from path '{path}': {e}")

            # Initialize selected items (all items are selected by default)
            self.selected_items = [str(i) for i in range(len(self.data))]
            print(f"DEBUG: Total vocabulary items: {len(self.data)}")
        except Exception as e:
            print(f"ERROR in load_vocabulary_items: {e}")
            import traceback
            traceback.print_exc()

    def populate_rv(self):
        """Populate the RecycleView with vocabulary item data."""
        if self._populating:
            return

        self._populating = True
        try:
            if not hasattr(self, 'ids') or 'item_view' not in self.ids:
                print("ERROR: item_view not found in ids, retrying...")
                Clock.schedule_once(lambda dt: self.populate_rv(), 0.2)
                return

            # Prepare data for RecycleView
            item_data = []
            for idx, item in enumerate(self.data):
                item_id = str(idx)
                if isinstance(item, dict):
                    origin = item.get('origin', '')
                    translation = item.get('translation', '')
                else:
                    origin = str(item)
                    translation = ''

                item_data.append({
                    'origin': origin,
                    'translation': translation,
                    'item_id': item_id,
                    'item_index': idx,
                    'selected': item_id in self.selected_items
                })

            self.ids.item_view.data = item_data
        except Exception as e:
            print(f"ERROR in populate_rv: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._populating = False

    def toggle_item_selection(self, item_id):
        """Toggle selection state of a vocabulary item."""
        if item_id in self.selected_items:
            self.selected_items.remove(item_id)
        else:
            self.selected_items.append(item_id)

        # Update only the specific item in the RecycleView without full refresh
        try:
            if hasattr(self, 'ids') and 'item_view' in self.ids:
                current_data = list(self.ids.item_view.data)
                item_index = int(item_id)
                if 0 <= item_index < len(current_data):
                    current_data[item_index]['selected'] = item_id in self.selected_items
                    # Use list slice to trigger update without infinite loop
                    self.ids.item_view.data = current_data[:]
        except Exception as e:
            print(f"ERROR in toggle_item_selection: {e}")

    def apply_selection(self):
        """Apply the selected items to the app store."""
        try:
            app = App.get_running_app()

            # Filter data based on selected items
            selected_indices = sorted([int(item_id) for item_id in self.selected_items])
            filtered_data = [self.data[i] for i in selected_indices if i < len(self.data)]

            # Update app store with selected items
            app.store = filtered_data

            # If vocabulary service exists, update it too
            if hasattr(app, '_vocabulary_service') and app._vocabulary_service:
                app._vocabulary_service._current_items = filtered_data

            self.go_back()
        except Exception as e:
            print(f"ERROR in apply_selection: {e}")
            import traceback
            traceback.print_exc()

    def go_back(self):
        """Navigate back to previous screen."""
        try:
            app = App.get_running_app()
            app.next_screen('main_screen')
        except Exception as e:
            print(f"ERROR in go_back: {e}")
            import traceback
            traceback.print_exc()

