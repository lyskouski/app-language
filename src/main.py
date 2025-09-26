# Initialization:
# > python -m venv kivy_venv
# > source kivy_venv/Scripts/activate [OR] source kivy_venv/bin/activate
# > pip install -r requirements.txt
# > python ./src/main.py

# Dependencies:
# > choco install ffmpeg

import os
import kivy
import kivy.resources
import random
import sys

from component.main_screen import MainScreen
from component.dictionary_screen import DictionaryScreen
from component.phonetics_screen import PhoneticsScreen
from component.articulation_screen import ArticulationScreen
from component.store_update_screen import StoreUpdateScreen
from component.structure_screen import StructureScreen
from l18n.labels import labels

## Load all widgets (for distribution) to avoid:
# AttributeError: module 'component' has no attribute 'recorder_widget'
import component.harmonica_widget
import component.phonetics_widget
import component.recorder_widget

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform

from kivy.base import EventLoop
EventLoop.ensure_window()

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.RECORD_AUDIO, Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

class MainApp(App):
    kv_directory = StringProperty('template')
    is_mobile = BooleanProperty(False)
    store = ListProperty([])
    store_path = StringProperty('')
    locale = StringProperty('')
    locale_to = StringProperty('')

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        home_dir = self.get_home_dir()
        os.makedirs(home_dir, exist_ok=True)
        # FIXME: Priorities are not working for additional DIR...
        kivy.resources.resource_paths.insert(0, home_dir)
        kivy.resources.resource_add_path(os.getcwd())
        current_dir = os.path.dirname(os.path.abspath(__file__))
        kivy.resources.resource_add_path(current_dir)
        kivy.resources.resource_add_path(os.path.dirname(current_dir))
        if getattr(sys, 'frozen', False):
            kivy.resources.resource_add_path(sys._MEIPASS)

    def _(self, key, locale):
        return labels.get(locale, labels.get('EN', {})).get(key, '['+key+']')
    
    def update_locale(self, locale):
        self.locale = locale

    def find_resource(self, path):
        user_path = os.path.join(self.get_home_dir(), path)
        if os.path.exists(user_path):
            return user_path
        return kivy.resources.resource_find(path)

    def get_home_dir(self):
        return os.path.join(App.get_running_app().user_data_dir, ".terCAD", "app-language")
    
    def get_audio_dir(self):
        path = os.path.join(self.get_home_dir(), "assets", self.locale_to, "audio")
        os.makedirs(path, exist_ok=True)
        return path

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
            (StoreUpdateScreen, 'store_update_screen'),
        ]
        for cls, name in screens:
            path = kivy.resources.resource_find(f'template/{name}.kv')
            Builder.load_file(path)
            sm.add_widget(cls(name=name))
        sm.current = 'main_screen'
        return sm

    def next_screen(self, screen_name):
        self.root.current = screen_name
        self.refresh_widgets()

    def init_store(self, data_path):
        if not data_path:
            data_path = self.store_path
        try:
            self.store_path = data_path
            path = self.find_resource(data_path)
            lines = []
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            parsed_data = []
            for line in lines:
                if ";" in line:
                    parts = [p.strip() for p in line.strip().split(";")]
                    if len(parts) == 3:
                        origin, trans, sound = parts
                    elif len(parts) == 2:
                        origin, trans = parts
                        sound = ''
                    else:
                        continue
                    parsed_data.append((origin, trans, sound))

            random.shuffle(parsed_data)
            self.store = parsed_data[:25]

        except FileNotFoundError:
            self.store = []

    def refresh_widgets(self):
        if not self.root:
            return

        for widget in self.root.walk():
            if hasattr(widget, 'load_data'):
                widget.load_data()

if __name__ == '__main__':
    MainApp().run()
