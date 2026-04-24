# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

class MainScreen(Screen):
    pass

class RootWidget(BoxLayout):
    data = ObjectProperty([])
    path = StringProperty('root')  # Changed from JSON path to navigation state

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        # Defer initialization until app is fully ready
        Clock.schedule_once(lambda dt: self._init_widget(), 0.1)

    def _init_widget(self):
        """Initialize widget after app is ready."""
        try:
            # Get services from DI container
            app = App.get_running_app()
            if not app or not hasattr(app, '_container'):
                print("ERROR: App not ready or missing container!")
                return

            self._config_repo = app._container.config_repository()

            self.load_data()
            Clock.schedule_once(lambda dt: self.populate_rv(), 0.1)
        except Exception as e:
            print(f"ERROR in MainScreen._init_widget: {e}")
            import traceback
            traceback.print_exc()

    def load_breadcrumb(self, path):
        """Navigate back using breadcrumb."""
        breadcrumbs = self.ids.breadcrumb_view.data
        cut_index = None
        for i, crumb in enumerate(breadcrumbs):
            if crumb.get('source') == path:
                cut_index = i
                break
        if cut_index is not None:
            self.path = path
            self.ids.breadcrumb_view.data = breadcrumbs[:cut_index]
        else:
            # If no matching breadcrumb found, go to root
            self.path = 'root'
            self.ids.breadcrumb_view.data = []

        self.load_data(path)
        self.populate_rv()

    def load_data(self, path = None):
        """Load data from SQLite database."""
        self.data = []
        if not path:
            path = self.path

        app = App.get_running_app()

        # Root level: show language pairs
        if path == 'root':
            self.data = self._config_repo.get_all_language_pairs()
            print(f"DEBUG: MainScreen loaded {len(self.data)} language pairs")

        # Level 2: Language pair selected → show dictionaries/categories
        elif path.startswith('assets/data/'):
            # This is a language pair path like "assets/data/PL/EN/source.json"
            if app.locale_from and app.locale_to:
                dictionaries = self._config_repo.get_dictionaries_for_language_pair(app.locale_from, app.locale_to)
                print(f"DEBUG: MainScreen loaded {len(dictionaries)} dictionaries for {app.locale_from}-{app.locale_to}")
                self.data = dictionaries
            else:
                print("ERROR: locale_from or locale_to not set!")
                self.data = []

        # Level 3: Dictionary/category selected → show game modes
        elif path.startswith('category_'):
            # Extract category ID from path like "category_5"
            try:
                category_id = int(path.split('_')[1])
                games = self._config_repo.get_games_for_category(category_id)
                print(f"DEBUG: MainScreen loaded {len(games)} games for category {category_id}")

                # Add locale info to each game
                for game in games:
                    game['locale_from'] = app.locale_from
                    game['locale_to'] = app.locale_to

                self.data = games
            except (IndexError, ValueError) as e:
                print(f"ERROR: Invalid category path: {path} - {e}")
                self.data = []

        else:
            print(f"DEBUG: Unknown path: {path}")
            self.data = []

    def update_data(self, info):
        """Handle navigation when a language pair, dictionary, or game is clicked."""
        try:
            print("DEBUG: update_data called")
            print(f"DEBUG: info.text = {info.text}")
            print(f"DEBUG: info.store_path = {info.store_path}")
            print(f"DEBUG: info.route_path = {info.route_path}")
            print(f"DEBUG: info.source = {info.source}")

            app = App.get_running_app()

            # Update locale settings
            if (info.locale_from != ''):
                app.locale_from = info.locale_from
                print(f"DEBUG: Set app.locale_from = {app.locale_from}")
            if (info.locale_to != ''):
                app.locale_to = info.locale_to
                print(f"DEBUG: Set app.locale_to = {app.locale_to}")

            # Check if this is a game (has route_path) - Level 3 → Game screen
            if (info.route_path != ''):
                print(f"DEBUG: Navigating to game screen: {info.route_path}")
                # Load vocabulary for the game
                if info.store_path and info.store_path != '':
                    print(f"DEBUG: Loading vocabulary with filter: {info.store_path}")
                    app.init_store(info.store_path)
                else:
                    print("DEBUG: Loading all vocabulary")
                    app.init_store('all')

                # Navigate to the specific game screen
                app.next_screen('loading_screen')
                Clock.schedule_once(
                    lambda dt: app.next_screen(info.route_path, app.root.get_screen('loading_screen')),
                    1
                )
                return

            # Otherwise, navigate to next level
            print("DEBUG: Navigating to next level")
            if not self.ids.breadcrumb_view.data:
                self.ids.breadcrumb_view.data = []
                self.path = 'root'
            self.ids.breadcrumb_view.data.append({'text': info.text, 'source': self.path})
            self.path = info.source
            print(f"DEBUG: New path = {self.path}")
            self.load_data()
            self.populate_rv()
        except Exception as e:
            print(f"ERROR in update_data: {e}")
            import traceback
            traceback.print_exc()

    def play_game(self, info):
        """Load vocabulary and navigate to a game screen."""
        try:
            print("DEBUG: play_game called")
            print(f"DEBUG: info.text = {info.text}")
            print(f"DEBUG: info.store_path = {info.store_path}")
            print(f"DEBUG: info.route_path = {info.route_path}")

            app = App.get_running_app()

            # Load vocabulary for the game
            if info.store_path and info.store_path != '':
                print(f"DEBUG: Loading vocabulary with filter: {info.store_path}")
                app.init_store(info.store_path)
            else:
                print("DEBUG: Loading all vocabulary")
                app.init_store('all')

            # Navigate to the loading screen, then to the game screen
            app.next_screen('loading_screen')
            Clock.schedule_once(
                lambda dt: app.next_screen(info.route_path, app.root.get_screen('loading_screen')),
                1
            )
        except Exception as e:
            print(f"ERROR in play_game: {e}")
            import traceback
            traceback.print_exc()

    def populate_rv(self):
        """Populate the RecycleView with data."""
        try:
            if not hasattr(self, 'ids') or 'recycle_view' not in self.ids:
                print("ERROR: recycle_view not found in ids, retrying...")
                Clock.schedule_once(lambda dt: self.populate_rv(), 0.2)
                return

            print(f"DEBUG: MainScreen populating RecycleView with {len(self.data)} items")
            self.ids.recycle_view.data = self.data
            print("DEBUG: MainScreen RecycleView data set successfully")
        except Exception as e:
            print(f"ERROR in populate_rv: {e}")
            import traceback
            traceback.print_exc()
