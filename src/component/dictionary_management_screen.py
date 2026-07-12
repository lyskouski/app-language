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
    management_widget = ObjectProperty(None, allownone=True)
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
        self._update_checkbox()

    def _update_checkbox(self):
        """Update the CheckBox widget visual state when selected changes."""
        try:
            from kivy.uix.checkbox import CheckBox
        except Exception:
            return

        for child in self.children:
            if isinstance(child, CheckBox):
                child.active = self.selected
                return

            for subchild in getattr(child, 'children', []):
                if isinstance(subchild, CheckBox):
                    subchild.active = self.selected
                    return

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
            if self.management_widget:
                self.management_widget.toggle_item_selection(self.item_id)
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
    data = ListProperty([])
    selected_indices = ListProperty([])  # Track selected indices, not item_ids

    def __init__(self, **kwargs):
        super(DictionaryManagementWidget, self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self._init_widget(), 0.1)

    def _init_widget(self):
        """Initialize widget after app is ready."""
        App.get_running_app()

    def _get_app(self):
        return App.get_running_app()

    def _get_main_screen(self):
        app = self._get_app()
        if not app or not hasattr(app, 'root') or not app.root:
            return None

        if 'main_screen' not in app.root.screen_names:
            return None

        return app.root.get_screen('main_screen')

    def _get_category_id(self):
        main_screen = self._get_main_screen()
        if not main_screen or not hasattr(main_screen, 'ids') or 'root_widget' not in main_screen.ids:
            return None

        path = main_screen.ids.root_widget.path
        if not path or not path.startswith('category_'):
            return None

        try:
            return int(path.split('_')[1])
        except (IndexError, ValueError):
            return None

    def _get_vocabulary_source(self, category_id):
        app = self._get_app()
        config_repo = app._container.config_repository()
        games = config_repo.get_games_for_category(category_id)

        if not games:
            return None

        return games[0].get('source', '')

    def _build_data_rows(self, all_vocab):
        return [
            {
                'origin': item.origin,
                'translation': item.translation,
                'category': item.category,
                'item_id': str(idx),
                'item_index': idx,
            }
            for idx, item in enumerate(all_vocab)
        ]

    def _selected_origin_set(self):
        app = self._get_app()
        if not app or not app.store:
            return set()

        return {
            item.origin
            for item in app.store
            if hasattr(item, 'origin')
        }

    def _sync_selection_from_store(self):
        store_origins = self._selected_origin_set()
        self.selected_indices = [
            idx for idx, item in enumerate(self.data)
            if item.get('origin', '') in store_origins
        ]

    def _build_recycleview_data(self):
        return [
            {
                'origin': item['origin'],
                'translation': item['translation'],
                'category': item.get('category'),
                'item_id': str(idx),
                'item_index': idx,
                'selected': idx in self.selected_indices,
                'management_widget': self,
            }
            for idx, item in enumerate(self.data)
        ]

    def _shift_selected_indices_after_delete(self, deleted_index):
        updated_selected = []
        for idx in self.selected_indices:
            if idx == deleted_index:
                continue
            if idx > deleted_index:
                updated_selected.append(idx - 1)
            else:
                updated_selected.append(idx)
        return updated_selected

    def _remove_item_from_store(self, origin, translation, category):
        app = self._get_app()
        if not app or not hasattr(app, 'store'):
            return

        app.store = [
            item for item in app.store
            if not (
                getattr(item, 'origin', None) == origin and
                getattr(item, 'translation', None) == translation and
                getattr(item, 'category', None) == category
            )
        ]

    def _build_selected_items(self):
        from domain.entities.vocabulary_item import VocabularyItem

        return [
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

    def load_vocabulary_items(self):
        """Load vocabulary items for the currently selected category."""
        try:
            self.data = []
            self.selected_indices = []

            category_id = self._get_category_id()
            if category_id is None:
                return

            app = self._get_app()
            vocabulary_source = self._get_vocabulary_source(category_id)
            if not vocabulary_source:
                return

            vocab_repo = app._container.vocabulary_repository()
            all_vocab = vocab_repo.load_by_language_pair(app.locale_from, app.locale_to, vocabulary_source)

            self.data = self._build_data_rows(all_vocab)
            self._sync_selection_from_store()

            print(f"Loaded {len(self.data)} items, {len(self.selected_indices)} selected")
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
            self.ids.item_view.data = self._build_recycleview_data()
        except Exception as e:
            print(f"ERROR in populate_rv: {e}")
            import traceback
            traceback.print_exc()

    def toggle_item_selection(self, item_id):
        """Toggle selection of a vocabulary item by ID."""
        try:
            item_index = int(item_id)
            if item_index in self.selected_indices:
                self.selected_indices = [idx for idx in self.selected_indices if idx != item_index]
            else:
                self.selected_indices = list(self.selected_indices) + [item_index]

            self.populate_rv()
        except Exception as e:
            print(f"ERROR in toggle_item_selection: {e}")
            import traceback
            traceback.print_exc()

    def delete_item(self, item_id):
        """Delete a vocabulary item from database and refresh list."""
        try:
            item_index = int(item_id)
            if item_index < 0 or item_index >= len(self.data):
                return

            item = self.data[item_index]
            origin = item.get('origin', '')
            translation = item.get('translation', '')
            category = item.get('category')

            app = self._get_app()
            vocab_repo = app._container.vocabulary_repository()
            if hasattr(vocab_repo, 'delete_vocabulary_item'):
                vocab_repo.delete_vocabulary_item(
                    app.locale_from,
                    app.locale_to,
                    origin,
                    translation=translation,
                    category=category,
                )

            del self.data[item_index]
            self.selected_indices = self._shift_selected_indices_after_delete(item_index)
            self._remove_item_from_store(origin, translation, category)

            self.populate_rv()
        except Exception as e:
            print(f"ERROR in delete_item: {e}")
            import traceback
            traceback.print_exc()

    def apply_selection(self):
        """Apply the selected items to the app store."""
        try:
            app = App.get_running_app()
            selected_items = self._build_selected_items()

            app.store.clear()
            app.store.extend(selected_items)

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
