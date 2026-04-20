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

from component.card_screen import CardScreen
from component.loading_screen import LoadingScreen
from component.main_screen import MainScreen
from component.dictionary_screen import DictionaryScreen
from component.phonetics_screen import PhoneticsScreen
from component.articulation_screen import ArticulationScreen
from component.store_update_screen import StoreUpdateScreen
from component.structure_screen import StructureScreen
from component.structure_update_screen import StructureUpdateScreen
from component.language_screen import LanguageScreen

# Clean Architecture imports
from infrastructure.di.container import DependencyContainer

## Load all widgets (for distribution) to avoid:
# AttributeError: module 'component' has no attribute 'recorder_widget'
import component.harmonica_widget
import component.phonetics_widget
import component.recorder_widget
import component.card_layout_widget

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty, ListProperty
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

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

        # Initialize dependency injection container (Composition Root)
        self._container = DependencyContainer(self.user_data_dir)
        self._container.setup_kivy_resources()

        # Get services through dependency injection
        self._settings_service = self._container.settings_service()
        self._resource_service = self._container.resource_service()
        self._localization_service = self._container.localization_service()

        # Initialize vocabulary service (will be created when needed)
        self._vocabulary_service = None

        # Load settings
        settings = self._settings_service.load_settings()
        self.locale = settings.interface_locale
        self.locale_from = settings.locale_from
        self.locale_to = settings.locale_to

        print(f"Home directory: {self._resource_service.get_path_with_home('')}")

    def _(self, key, locale):
        """Translate a key to the specified locale."""
        return self._localization_service.translate(key, locale)

    def update_locale(self, locale):
        """Update the interface locale."""
        self.locale = locale
        self._settings_service.update_interface_locale(locale)

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
        sm = ScreenManager()
        screens = [
            (MainScreen, 'main_screen'),
            (DictionaryScreen, 'dictionary_screen'),
            (PhoneticsScreen, 'phonetics_screen'),
            (ArticulationScreen, 'articulation_screen'),
            (StructureScreen, 'structure_screen'),
            (StructureUpdateScreen, 'structure_update_screen'),
            (StoreUpdateScreen, 'store_update_screen'),
            (LoadingScreen, 'loading_screen'),
            (CardScreen, 'card_screen'),
            (LanguageScreen, 'language_screen')
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

    def init_store(self, data_path = None):
        """
        Initialize the vocabulary store.
        Uses dependency injection to create vocabulary service.
        """
        if data_path:
            # Create vocabulary service with profiler support
            self._vocabulary_service = self._container.vocabulary_service(data_path)

            # Find the actual file path and load vocabulary
            file_path = self._resource_service.find_resource(data_path)
            if file_path:
                self._vocabulary_service.load_vocabulary(file_path)

            # Prepare and get study set
            self._vocabulary_service.prepare_study_set(25)
            self.store = self._vocabulary_service.get_current_study_set()
        elif self._vocabulary_service:
            # Just shuffle if already loaded
            self._vocabulary_service.prepare_study_set(25)
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
