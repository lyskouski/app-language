# Initialization:
# > python -m venv kivy_venv
# > source kivy_venv/Scripts/activate [OR] source kivy_venv/bin/activate
# > pip install -r requirements.txt
# > python ./src/main.py

import json
import os
import kivy
import kivy.resources
import random
import sys

from component.dictionary_screen import DictionaryScreen
from component.phonetics_screen import PhoneticsScreen
from component.articulation_screen import ArticulationScreen
from component.store_update_screen import StoreUpdateScreen
from l18n.labels import labels

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform

from kivy.base import EventLoop
EventLoop.ensure_window()

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.RECORD_AUDIO, Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

class MainScreen(Screen):
    pass

class RootWidget(BoxLayout):
    data = ObjectProperty([])
    path = StringProperty('assets/source.json')

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.load_data()
        Clock.schedule_once(lambda dt: self.populate_rv())

    def load_data(self):
        source_path = kivy.resources.resource_find(self.path)
        if source_path and os.path.exists(source_path):
            with open(source_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = []

    def populate_rv(self):
        self.ids.recycle_view.data = self.data

class MainApp(App):
    kv_directory = StringProperty('template')
    is_mobile = BooleanProperty(False)
    store = ListProperty([])
    store_path = StringProperty('')
    locale = StringProperty('')

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        home_dir = self.get_home_dir()
        os.makedirs(home_dir, exist_ok=True)
        kivy.resources.resource_add_path(home_dir)
        kivy.resources.resource_add_path(os.getcwd())
        current_dir = os.path.dirname(os.path.abspath(__file__))
        kivy.resources.resource_add_path(current_dir)
        kivy.resources.resource_add_path(os.path.dirname(current_dir))
        if getattr(sys, 'frozen', False):
            kivy.resources.resource_add_path(sys._MEIPASS)

    def _(self, key, locale):
        return labels.get(locale, labels.get('en', {})).get(key, '['+key+']')
    
    def update_locale(self, locale):
        self.locale = locale

    def get_home_dir(self):
        return os.path.join(App.get_running_app().user_data_dir, ".terCAD", "app-language")

    def build(self):
        if platform in ['android', 'ios']:
            self.is_mobile = True
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        Builder.load_file('template/dictionary_screen.kv')
        sm.add_widget(DictionaryScreen(name='dictionary_screen'))
        Builder.load_file('template/phonetics_screen.kv')
        sm.add_widget(PhoneticsScreen(name='phonetics_screen'))
        Builder.load_file('template/articulation_screen.kv')
        sm.add_widget(ArticulationScreen(name='articulation_screen'))
        Builder.load_file('template/store_update_screen.kv')
        sm.add_widget(StoreUpdateScreen(name='store_update_screen'))
        sm.current = 'main'
        return sm

    def next_screen(self, screen_name):
        self.root.current = screen_name
        self.refresh_widgets()

    def init_store(self, data_path):
        if not data_path:
            data_path = self.store_path
        try:
            self.store_path = data_path
            path = kivy.resources.resource_find(data_path)
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
