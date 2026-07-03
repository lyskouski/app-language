# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.behaviors import FocusBehavior, ButtonBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout


class SelectableRecycleBoxLayout(FocusBehavior, RecycleBoxLayout):
    """RecycleBoxLayout with selection support."""
    pass


# Register with Factory so KV can find it
Factory.register('SelectableRecycleBoxLayout', cls=SelectableRecycleBoxLayout)


class VocabularyItemWidget(ButtonBehavior, BoxLayout):
    """Widget for displaying a vocabulary item in RecycleView. ButtonBehavior enables touch events."""
    origin = StringProperty('')
    translation = StringProperty('')
    item_id = StringProperty('')
    item_index = NumericProperty(0)
    selected = BooleanProperty(False)  # Directly from data dict, not computed

    # Bind to selected property changes to redraw canvas
    def _redraw_background(self):
        """Redraw the background based on current selection state."""
        self.canvas.before.clear()
        with self.canvas.before:
            if self.selected:
                Color(0.2, 0.8, 0.2, 0.3)  # Light green
            else:
                Color(0.6, 0.6, 0.6, 0.2)  # Light grey
            Rectangle(pos=self.pos, size=self.size)
        # Also update the checkbox visual
        self._update_checkbox()

    def _update_checkbox(self):
        """Update the CheckBox widget visual state when selected changes."""
        try:
            from kivy.uix.checkbox import CheckBox
            # Find the CheckBox child widget by traversing children
            for child in self.children:
                if isinstance(child, CheckBox):
                    # Directly set the active state without triggering events
                    child.active = self.selected
                    return
                # Recursively check nested layouts (CheckBox is in last BoxLayout)
                if hasattr(child, 'children'):
                    for subchild in child.children:
                        if isinstance(subchild, CheckBox):
                            subchild.active = self.selected
                            return
        except Exception as e:
            pass

    def __init__(self, **kwargs):
        super(VocabularyItemWidget, self).__init__(**kwargs)
        # Bind to all relevant properties that affect the background
        self.bind(selected=lambda *args: self._redraw_background(),
                  pos=lambda *args: self._redraw_background(),
                  size=lambda *args: self._redraw_background())
        # Initial draw
        Clock.schedule_once(lambda dt: self._redraw_background(), 0)

    def on_release(self):
        """Handle widget click to toggle selection. Called by ButtonBehavior."""
        # Don't toggle if a child widget (like Delete button) was clicked
        if hasattr(self, '_button_clicked') and self._button_clicked:
            self._button_clicked = False
            return

        try:
            app = App.get_running_app()
            management_widget = app.root.get_screen('dictionary_management_screen').ids.management_widget
            management_widget.toggle_item_selection(self.item_id)
        except Exception as e:
            print(f"ERROR in VocabularyItemWidget.on_release: {e}")


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
    selected_indices = ListProperty([])  # Track selected indices, not item_ids

    def __init__(self, **kwargs):
        super(DictionaryManagementWidget, self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self._init_widget(), 0.1)

    def _init_widget(self):
        """Initialize widget after app is ready."""
        app = App.get_running_app()

    def load_vocabulary_items(self):
        """Load vocabulary items for the currently selected category."""
        try:
            app = App.get_running_app()
            self.data = []
            self.selected_indices = []  # Reset selection

            if hasattr(app, 'root') and app.root and 'main_screen' in app.root.screen_names:
                main_screen = app.root.get_screen('main_screen')
                if hasattr(main_screen, 'ids') and 'root_widget' in main_screen.ids:
                    root_widget = main_screen.ids.root_widget
                    path = root_widget.path

                    if path and path.startswith('category_'):
                        try:
                            category_id = int(path.split('_')[1])
                            config_repo = app._container.config_repository()
                            games = config_repo.get_games_for_category(category_id)

                            vocabulary_source = None
                            if games and len(games) > 0:
                                vocabulary_source = games[0].get('source', '')

                            if not vocabulary_source:
                                return

                            vocab_repo = app._container.vocabulary_repository()
                            all_vocab = vocab_repo.load_by_language_pair(app.locale_from, app.locale_to, vocabulary_source)

                            # Build data list with origin/translation
                            self.data = [
                                {
                                    'origin': item.origin,
                                    'translation': item.translation,
                                    'item_id': str(idx),
                                    'item_index': idx,
                                }
                                for idx, item in enumerate(all_vocab)
                            ]

                            # Populate selected_indices based on app.store
                            if app and app.store and len(app.store) > 0:
                                store_origins = {item.origin for item in app.store if hasattr(item, 'origin')}
                                self.selected_indices = [
                                    idx for idx, item in enumerate(self.data)
                                    if item.get('origin', '') in store_origins
                                ]

                            print(f"Loaded {len(self.data)} items, {len(self.selected_indices)} selected")
                        except (IndexError, ValueError) as e:
                            print(f"ERROR: Could not parse category from path '{path}': {e}")
                            import traceback
                            traceback.print_exc()
        except Exception as e:
            print(f"ERROR in load_vocabulary_items: {e}")
            import traceback
            traceback.print_exc()

    def populate_rv(self):
        """Populate the RecycleView with vocabulary item data."""
        if not hasattr(self, 'ids') or 'item_view' not in self.ids:
            Clock.schedule_once(lambda dt: self.populate_rv(), 0.2)
            return

        try:

            # Create data list with selection state stored in each dict
            # This ensures selection is updated ATOMICALLY with all other properties during RecycleView recycling
            data = [
                {
                    'origin': item['origin'],
                    'translation': item['translation'],
                    'item_id': str(idx),
                    'item_index': idx,
                    'selected': idx in self.selected_indices  # Store selected state in data dict
                }
                for idx, item in enumerate(self.data)
            ]

            # Set data which triggers RecycleView to rebind widgets
            self.ids.item_view.data = data
        except Exception as e:
            print(f"ERROR in populate_rv: {e}")
            import traceback
            traceback.print_exc()

    def toggle_item_selection(self, item_id):
        """Toggle selection of a vocabulary item by ID."""
        try:
            item_index = int(item_id)

            # Create new list instead of mutating to force ListProperty update
            if item_index in self.selected_indices:
                new_indices = [idx for idx in self.selected_indices if idx != item_index]
            else:
                new_indices = list(self.selected_indices) + [item_index]

            self.selected_indices = new_indices

            # Rebuild RecycleView data with correct selection states
            self.populate_rv()
        except Exception as e:
            print(f"ERROR in toggle_item_selection: {e}")
            import traceback
            traceback.print_exc()

    def delete_item(self, item_id):
        """Delete a vocabulary item from database and refresh list."""
        try:
            app = App.get_running_app()
            item_index = int(item_id)
            if item_index < 0 or item_index >= len(self.data):
                return

            item = self.data[item_index]
            origin = item.get('origin', '')
            translation = item.get('translation', '')

            vocab_repo = app._container.vocabulary_repository()
            if hasattr(vocab_repo, 'delete_vocabulary_item'):
                vocab_repo.delete_vocabulary_item(
                    app.locale_from,
                    app.locale_to,
                    origin,
                    translation=translation,
                )

            # Remove from data list
            del self.data[item_index]

            # Update selected_indices: remove deleted index, shift higher indices down
            updated_selected = []
            for idx in self.selected_indices:
                if idx == item_index:
                    continue  # Remove selection for deleted item
                elif idx > item_index:
                    updated_selected.append(idx - 1)  # Shift down
                else:
                    updated_selected.append(idx)
            self.selected_indices = updated_selected  # Replace entire list

            # Keep app.store in sync
            if app and hasattr(app, 'store'):
                app.store = [
                    s for s in app.store
                    if not (getattr(s, 'origin', None) == origin and getattr(s, 'translation', None) == translation)
                ]

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

            # Build selected items from indices
            selected_items = [
                VocabularyItem(
                    origin=self.data[idx]['origin'],
                    translation=self.data[idx]['translation'],
                    sound=self.data[idx].get('sound'),
                    image=self.data[idx].get('image'),
                    category=self.data[idx].get('category')
                )
                for idx in sorted(self.selected_indices)
                if idx < len(self.data)
            ]

            # Update app store
            app.store.clear()
            app.store.extend(selected_items)

            # Update vocabulary service if it exists
            if hasattr(app, '_vocabulary_service') and app._vocabulary_service:
                app._vocabulary_service._current_items = selected_items
                app._vocabulary_service.prepare_study_set(len(selected_items), force_shuffle=False)

            app._custom_selection_active = True
            self.go_back()
        except Exception as e:
            print(f"ERROR in apply_selection: {e}")
            import traceback
            traceback.print_exc()

    def go_back(self):
        """Navigate back to previous screen."""
        app = App.get_running_app()
        app.next_screen('main_screen')
