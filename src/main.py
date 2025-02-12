# Initialization:
# > python -m venv kivy_venv
# > source kivy_venv/Scripts/activate [OR] source kivy_venv/bin/activate
# > pip install -r requirements.txt
# > python ./src/main.py

import kivy
import random
import sys
import kivy.resources

# hack to avoid "not found"-exception after tlum.spec usage
import component.harmonica_widget
import component.recorder_widget

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

from kivy.base import EventLoop
EventLoop.ensure_window()

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.RECORD_AUDIO, Permission.WRITE_EXTERNAL_STORAGE])

if getattr(sys, 'frozen', False):
    kivy.resources.resource_add_path(sys._MEIPASS)

class RootWidget(BoxLayout):
    container = ObjectProperty(None)

class MainApp(App):
    kv_directory = StringProperty('template')
    is_mobile = BooleanProperty(False)
    data = ListProperty([])

    def build(self):
        if platform in ['android', 'ios']:
            self.is_mobile = True
        self.load_and_shuffle_data()
        kvPath = kivy.resources.resource_find(self.kv_directory + '/main.kv')
        return Builder.load_file(kvPath)

    def next_screen(self, screen):
        kvPath = kivy.resources.resource_find(self.kv_directory + '/' + screen + '.kv')
        Builder.unload_file(kvPath)
        self.root.container.clear_widgets()
        screen = Builder.load_file(kvPath)
        self.root.container.add_widget(screen)

    def load_and_shuffle_data(self):
        data_file = "assets/data/dictionary.txt"
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            parsed_data = []
            for line in lines:
                if ":" in line:
                    origin, trans = line.strip().split(":", 1)
                    origin, trans = origin.strip(), trans.strip()
                    parsed_data.append((origin, trans))

            random.shuffle(parsed_data)
            self.data = parsed_data[:25]

        except FileNotFoundError:
            self.data = []

        Clock.schedule_once(lambda dt: self.refresh_widgets())

    def refresh_widgets(self):
        if not self.root:
            return

        for widget in self.root.walk():
            if hasattr(widget, 'load_data'):
                widget.load_data()

if __name__ == '__main__':
    MainApp().run()
