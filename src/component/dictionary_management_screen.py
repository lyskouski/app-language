# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

class VocabularyItemWidget(BoxLayout):
    """Widget for displaying a vocabulary item with checkbox in RecycleView."""
    origin = StringProperty('')
    translation = StringProperty('')
    item_id = StringProperty('')
    item_index = NumericProperty(0)
    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(VocabularyItemWidget, self).__init__(**kwargs)
        # Create canvas instructions that we'll update
        with self.canvas.before:
            self._bg_color = Color(0.9, 0.9, 0.9, 0.1)  # Initial light gray
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

        # Bind selected property to canvas update for visual change
        self.bind(selected=self._on_selected_changed, pos=self._on_pos_changed, size=self._on_size_changed)

    def _on_selected_changed(self, instance, value):
        """Called when selected property changes - update background color."""
        print(f"DEBUG: VocabularyItemWidget {self.item_id} selected changed to {value}")
        self._update_background_color()

    def _on_pos_changed(self, instance, value):
        """Called when position changes - update rectangle position."""
        if hasattr(self, '_bg_rect'):
            self._bg_rect.pos = self.pos

    def _on_size_changed(self, instance, value):
        """Called when size changes - update rectangle size."""
        if hasattr(self, '_bg_rect'):
            self._bg_rect.size = self.size

    def _update_background_color(self):
        """Update background color based on selected state."""
        if hasattr(self, '_bg_color'):
            if self.selected:
                self._bg_color.rgba = (0.2, 0.8, 0.2, 0.2)  # Green for selected
            else:
                self._bg_color.rgba = (0.9, 0.9, 0.9, 0.1)  # Light gray for not selected

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
    _updating_checkbox = False  # Guard against circular checkbox binding

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

            # Don't load data here - app.store is empty during initialization
            # Data will be loaded in on_enter() when the screen is actually shown
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

                            # Get config repository to find category vocabulary_source
                            config_repo = app._container.config_repository()

                            # Query the database to get vocabulary_source for this category_id
                            # This is the actual category name used in vocabulary_items table
                            games = config_repo.get_games_for_category(category_id)

                            # Extract vocabulary_source from category info
                            vocabulary_source = None
                            if games and len(games) > 0:
                                # games is a list, extract source from first game
                                vocabulary_source = games[0].get('source', '')

                            if not vocabulary_source:
                                print(f"ERROR: Could not find vocabulary_source for category_id {category_id}")
                                return

                            # Load vocabulary filtered by category
                            vocab_repo = app._container.vocabulary_repository()
                            all_vocab = vocab_repo.load_by_language_pair(app.locale_from, app.locale_to, vocabulary_source)

                            # Convert to dicts
                            vocab_dicts = []
                            for item in all_vocab:
                                vocab_dicts.append({
                                    'origin': item.origin,
                                    'translation': item.translation,
                                    'sound': getattr(item, 'sound', ''),
                                    'image': getattr(item, 'image', ''),
                                    'category': getattr(item, 'category', '')
                                })

                            self.data = vocab_dicts
                            print(f"DEBUG: Loaded {len(self.data)} vocabulary items for category '{vocabulary_source}' ({app.locale_from}-{app.locale_to})")
                        except (IndexError, ValueError) as e:
                            print(f"ERROR: Could not parse category from path '{path}': {e}")
                            import traceback
                            traceback.print_exc()

            # Initialize selected items based on what's in app.store
            # app.store contains VocabularyItem objects (domain entities)
            # self.data contains dictionaries loaded from the database
            # We match these against the full category vocabulary list
            self.selected_items = []

            if app and app.store and len(app.store) > 0:
                # Build a set of origins from app.store for quick lookup
                store_origins = set()
                for store_item in app.store:
                    # app.store contains VocabularyItem domain entities
                    origin = store_item.origin if hasattr(store_item, 'origin') else str(store_item)
                    store_origins.add(origin)

                # Find indices in self.data that match store origins
                for idx, item in enumerate(self.data):
                    item_origin = item.get('origin', '') if isinstance(item, dict) else str(item)
                    if item_origin in store_origins:
                        self.selected_items.append(str(idx))
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

    def toggle_item_selection(self, item_id, checkbox_active):
        """Toggle selection state of a vocabulary item."""
        # Guard against circular checkbox binding updates
        if self._updating_checkbox:
            return

        # The checkbox state is passed from the on_active binding
        if checkbox_active:
            if item_id not in self.selected_items:
                self.selected_items.append(item_id)
        else:
            if item_id in self.selected_items:
                self.selected_items.remove(item_id)

        # Update the RecycleView data for this specific item without triggering on_active
        try:
            if hasattr(self, 'ids') and 'item_view' in self.ids:
                current_data = list(self.ids.item_view.data)
                item_index = int(item_id)
                if 0 <= item_index < len(current_data):
                    # Update the selected state based on current selected_items
                    current_data[item_index]['selected'] = item_id in self.selected_items
                    # Set flag to prevent on_active from firing when we update the checkbox
                    self._updating_checkbox = True
                    self.ids.item_view.data = current_data
                    self._updating_checkbox = False
        except Exception as e:
            print(f"ERROR in toggle_item_selection: {e}")
            self._updating_checkbox = False

    def delete_item(self, item_id):
        """Delete a vocabulary item from database and refresh management list."""
        try:
            app = App.get_running_app()
            item_index = int(item_id)
            if item_index < 0 or item_index >= len(self.data):
                return

            item = self.data[item_index]
            origin = item.get('origin', '') if isinstance(item, dict) else ''
            translation = item.get('translation', '') if isinstance(item, dict) else ''
            category = item.get('category') if isinstance(item, dict) else None

            vocab_repo = app._container.vocabulary_repository()
            if hasattr(vocab_repo, 'delete_vocabulary_item'):
                vocab_repo.delete_vocabulary_item(
                    app.locale_from,
                    app.locale_to,
                    origin,
                    translation=translation,
                    category=category,
                )

            # Remove from current list and update selection indices.
            del self.data[item_index]

            updated_selected = []
            for selected_id in self.selected_items:
                selected_index = int(selected_id)
                if selected_index == item_index:
                    continue
                if selected_index > item_index:
                    updated_selected.append(str(selected_index - 1))
                else:
                    updated_selected.append(selected_id)
            self.selected_items = updated_selected

            # Keep app.store in sync.
            if app and hasattr(app, 'store'):
                filtered_store = [
                    store_item for store_item in app.store
                    if not (
                        getattr(store_item, 'origin', None) == origin
                        and getattr(store_item, 'translation', None) == translation
                        and getattr(store_item, 'category', None) == category
                    )
                ]
                app.store.clear()
                app.store.extend(filtered_store)

            self.populate_rv()
        except Exception as e:
            print(f"ERROR in delete_item: {e}")
            import traceback
            traceback.print_exc()

    def apply_selection(self):
        """Apply the selected items to the app store."""
        try:
            from domain.entities.vocabulary_item import VocabularyItem
            app = App.get_running_app()

            # Filter data based on selected items
            selected_indices = sorted([int(item_id) for item_id in self.selected_items])
            selected_dicts = [self.data[i] for i in selected_indices if i < len(self.data)]

            # Convert back to VocabularyItem objects to match app.store format
            selected_items = [
                VocabularyItem(
                    origin=item['origin'],
                    translation=item['translation'],
                    sound=item.get('sound'),
                    image=item.get('image'),
                    category=item.get('category')
                )
                for item in selected_dicts
            ]

            # Update app store with selected items (must be VocabularyItem objects, not dicts)
            app.store.clear()
            app.store.extend(selected_items)

            # If vocabulary service exists, update its study set too
            if hasattr(app, '_vocabulary_service') and app._vocabulary_service:
                app._vocabulary_service._current_items = selected_items
                app._vocabulary_service.prepare_study_set(len(selected_items), force_shuffle=False)

            # Mark that custom selection is now active - prevents reinitializing when game is played
            app._custom_selection_active = True
            print(f"DEBUG: Custom selection active - app.store will be preserved during gameplay")

            print(f"DEBUG: Saved {len(selected_items)} selected items to app.store")
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
