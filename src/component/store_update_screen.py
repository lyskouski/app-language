import os
import kivy

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

class StoreUpdateScreen(Screen):
    data = StringProperty('original ; translation ; sound path')

    def load_data(self):
        app = App.get_running_app()
        path = kivy.resources.resource_find(app.store_path)
        lines = []
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.data = ''.join(lines)

    def save_data(self):
        app = App.get_running_app()
        path = os.path.join(app.get_home_dir(), app.store_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.data)
        app.init_store(app.store_path)
