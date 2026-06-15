# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

# Initialization:
# > python -m venv kivy_venv
# > source kivy_venv/Scripts/activate [OR] source kivy_venv/bin/activate
# > pip install -r requirements.txt
# > python ./src/main.py

# Initialization for Android/iOS (with Buildozer):
# NOTE: Android target is not available on Windows-native Buildozer.
#       Use Linux (recommended: WSL2 on Windows) to build Android APK/AAB.
# > python3 -m pip install --user -U buildozer
# > buildozer -v android debug

# Dependencies:
# > choco install ffmpeg

import os
import kivy
import kivy.resources
import sys
from pathlib import Path
from kivy.config import Config

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_BOOTSTRAP_ICON = _PROJECT_ROOT / 'assets' / 'images' / 'logo_44.png'
Config.set('kivy', 'window_icon', str(_BOOTSTRAP_ICON))

from component.card_screen import CardScreen
from component.loading_screen import LoadingScreen
from component.main_screen import MainScreen
from component.dictionary_screen import DictionaryScreen
from component.dictionary_management_screen import DictionaryManagementScreen
from component.phonetics_screen import PhoneticsScreen
from component.articulation_screen import ArticulationScreen
from component.store_update_screen import StoreUpdateScreen
from component.structure_screen import StructureScreen
from component.structure_update_screen import StructureUpdateScreen
from component.language_screen import LanguageScreen
from component.vocabulary_add_screen import VocabularyAddScreen
from component.category_add_screen import CategoryAddScreen
from component.language_pair_add_screen import LanguagePairAddScreen

# Clean Architecture imports
from infrastructure.di.container import DependencyContainer

## Load all widgets (for distribution) to avoid:
# AttributeError: module 'component' has no attribute 'recorder_widget'
import component.harmonica_widget
import component.phonetics_widget
import component.recorder_widget
import component.card_layout_widget

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform

from kivy.base import EventLoop
EventLoop.ensure_window()

class MainApp(App):
    """
    Main Application class following SOLID principles.

    Responsibilities (following Single Responsibility Principle):
    - App lifecycle management
    - Screen management
    - Coordination between services and UI

    Dependencies are injected through the DependencyContainer (Dependency Inversion Principle).
    """
    kv_directory = StringProperty('template')
    is_mobile = BooleanProperty(False)
    store = ListProperty([])
    locale = StringProperty('')
    locale_from = StringProperty('')
    locale_to = StringProperty('')
    theme_mode = StringProperty('light')
    theme = ObjectProperty(None)
    theme_version = NumericProperty(0)
    title = 'Tlum'

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

        # Initialize dependency injection container (Composition Root)
        self._container = DependencyContainer(self.user_data_dir)
        self._container.setup_kivy_resources()

        # Get services through dependency injection
        self._settings_service = self._container.settings_service()
        self._config_repo = self._container.config_repository()
        self._resource_service = self._container.resource_service()
        self._localization_service = self._container.localization_service()
        self._theme_service = self._container.theme_service()

        # Load persisted theme mode from database.
        saved_theme_mode = self._config_repo.get_app_setting('theme_mode', 'light')
        self.theme_mode = 'dark' if saved_theme_mode == 'dark' else 'light'
        self._theme_service.set_mode(self.theme_mode)
        self.theme = self._theme_service.get_theme()

        # Initialize vocabulary service (will be created when needed)
        self._vocabulary_service = None

        # Track whether custom dictionary selection is active
        self._custom_selection_active = False

        # Load settings
        settings = self._settings_service.load_settings()
        self.locale = settings.interface_locale
        self.locale_from = settings.locale_from
        self.locale_to = settings.locale_to

    def _(self, key, locale):
        """Translate a key to the specified locale."""
        return self._localization_service.translate(key, locale)

    def update_locale(self, locale):
        """Update the interface locale."""
        self.locale = locale
        self._settings_service.update_interface_locale(locale)

    def theme_color(self, token_name: str, _theme_version: float = 0):
        """Get a theme token value.

        `_theme_version` is an explicit dependency used by KV bindings
        to force live theme re-evaluation when mode changes.
        """
        return getattr(self.theme, token_name)

    def toggle_theme_mode(self, dark_enabled: bool):
        """Switch between light and dark theme and persist choice in database."""
        new_mode = 'dark' if dark_enabled else 'light'
        if self.theme_mode == new_mode:
            return

        self.theme_mode = new_mode
        self._theme_service.set_mode(new_mode)
        self.theme = self._theme_service.get_theme()
        self.theme_version += 1
        Window.clearcolor = self.theme.md3_background
        self._config_repo.set_app_setting('theme_mode', new_mode)

        if self.root:
            self.root.canvas.ask_update()
            for widget in self.root.walk():
                if hasattr(widget, 'canvas') and widget.canvas:
                    widget.canvas.ask_update()

    def find_resource(self, path):
        """Find a resource by path."""
        return self._resource_service.find_resource(path)

    def get_home_dir(self):
        """Get the application home directory."""
        return self._resource_service._repository.get_home_dir()

    def get_with_home_dir(self, file_path):
        """Get a path relative to home directory."""
        return self._resource_service.get_path_with_home(file_path)

    def get_audio_dir(self):
        """Get the audio directory for current locale."""
        return self._resource_service.get_audio_directory(self.locale_to)

    def get_image_dir(self):
        """Get the image directory for current locale."""
        return self._resource_service.get_image_directory(self.locale_to)

    def build(self):
        if platform in ['android', 'ios']:
            self.is_mobile = True

        app_icon = kivy.resources.resource_find('assets/images/logo_44.png')
        if app_icon:
            self.icon = app_icon
            try:
                Window.set_icon(app_icon)
            except Exception:
                # Some platforms/backends may not support the chosen icon format.
                pass

        # Use themed clear color so transition gaps never expose default black.
        Window.clearcolor = self.theme.md3_background

        # Load shared Material 3 styling rules first so all subsequent widgets inherit them.
        theme_path = kivy.resources.resource_find('template/theme.kv')
        if theme_path:
            Builder.load_file(theme_path)

        sm = ScreenManager()
        screens = [
            (MainScreen, 'main_screen'),
            (DictionaryScreen, 'dictionary_screen'),
            (DictionaryManagementScreen, 'dictionary_management_screen'),
            (PhoneticsScreen, 'phonetics_screen'),
            (ArticulationScreen, 'articulation_screen'),
            (StructureScreen, 'structure_screen'),
            (StructureUpdateScreen, 'structure_update_screen'),
            (StoreUpdateScreen, 'store_update_screen'),
            (LoadingScreen, 'loading_screen'),
            (CardScreen, 'card_screen'),
            (LanguageScreen, 'language_screen'),
            (VocabularyAddScreen, 'vocabulary_add_screen'),
            (CategoryAddScreen, 'category_add_screen'),
            (LanguagePairAddScreen, 'language_pair_add_screen')
        ]
        for cls, name in screens:
            path = kivy.resources.resource_find(f'template/{name}.kv')
            Builder.load_file(path)
            sm.add_widget(cls(name=name))
        sm.current = 'language_screen' if not self.locale else 'main_screen'
        return sm

    def next_screen(self, screen_name, widget = None):
        self.root.current = screen_name
        self.refresh_widgets(widget)

    def init_store(self, data_path = None, force_shuffle: bool = False):
        """
        Initialize the vocabulary store.
        Uses dependency injection to create vocabulary service.

        Args:
            data_path: Path to vocabulary file, 'db'/'all' to load from database, or category filter. If None, reshuffles current vocabulary.
            force_shuffle: If True, uses random shuffle instead of ML prioritization.
        """
        if data_path:
            # Check if we should load from database
            # If data_path is not a file path (no extension or assets/ prefix), treat it as database request
            is_file_path = (data_path.startswith('assets/') or '.' in data_path.split('/')[-1])

            if not is_file_path or data_path == 'db' or data_path == 'all':
                # Load vocabulary directly from database using current locale settings
                if self.locale_from and self.locale_to:
                    # Determine category filter
                    category_filter = None
                    if data_path not in ('db', 'all'):
                        category_filter = data_path

                    # Get repository directly from container
                    vocab_repo = self._container.vocabulary_repository()
                    items = vocab_repo.load_by_language_pair(self.locale_from, self.locale_to, category_filter)

                    # Create vocabulary service for this language pair
                    self._vocabulary_service = self._container.vocabulary_service(f"db_{self.locale_from}_{self.locale_to}")

                    # Set items directly (bypass file loading)
                    self._vocabulary_service._current_items = items

                    # Prepare and get study set
                    self._vocabulary_service.prepare_study_set(25, force_shuffle)
                    self.store = self._vocabulary_service.get_current_study_set()
                else:
                    print("ERROR: locale_from and locale_to must be set to load from database")
            else:
                # Legacy file-based loading
                self._vocabulary_service = self._container.vocabulary_service(data_path)

                # Find the actual file path and load vocabulary
                file_path = self._resource_service.find_resource(data_path)
                if file_path:
                    self._vocabulary_service.load_vocabulary(file_path)
                else:
                    print(f"ERROR: File not found: {data_path}")
                    return

                # Prepare and get study set
                self._vocabulary_service.prepare_study_set(25, force_shuffle)
                self.store = self._vocabulary_service.get_current_study_set()
        elif self._vocabulary_service:
            # Just shuffle if already loaded
            self._vocabulary_service.prepare_study_set(25, force_shuffle)
            self.store = self._vocabulary_service.get_current_study_set()
            self.store = self._vocabulary_service.get_current_study_set()

    def refresh_widgets(self, item = None):
        if not self.root:
            return

        for widget in self.root.walk():
            if item is not None and hasattr(widget, 'init_data'):
                widget.init_data(item)
            if hasattr(widget, 'load_data'):
                widget.load_data()

if __name__ == '__main__':
    MainApp().run()
