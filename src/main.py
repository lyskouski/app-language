# Initialization:
# > python -m venv kivy_venv
# > source kivy_venv/Scripts/activate
# > pip install -r requirements.txt

import kivy
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

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

    def next_screen(self, screen):
        filepath = self.kv_directory + '/' + screen + '.kv'
        Builder.unload_file(filepath)
        self.root.container.clear_widgets()
        screen = Builder.load_file(filepath)
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
        for widget in self.root.walk():
            if hasattr(widget, 'load_data'):
                widget.load_data()

if __name__ == '__main__':
    MainApp().run()
