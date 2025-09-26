import json
import os
import kivy
import kivy.resources

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

class StructureScreen(Screen):
    def __init__(self, **kwargs):
        super(StructureScreen, self).__init__(**kwargs)
        self.load_data()
        Clock.schedule_once(lambda dt: self.populate_rv())

    def get_data(self, path):
        source_path = kivy.resources.resource_find(path)
        if source_path and os.path.exists(source_path):
            with open(source_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def load_data(self):
        self.data = self.get_data('assets/source.json')

    def populate_rv(self):
        self.ids.structure_view.data = self.data

class StructureWidget(BoxLayout):
    source = StringProperty('')
    indent = NumericProperty(0, allownone=True)

    def expand(self):
        app = App.get_running_app()
        screen = app.root.get_screen('structure_screen')
        new_data = screen.get_data(self.source)
        new_indent = (self.indent or 0) + 0.1
        for item in new_data:
            if isinstance(item, dict):
                item['indent'] = new_indent
        insert_idx = None
        for idx, item in enumerate(screen.data):
            if isinstance(item, dict) and item.get('text') == self.text:
                insert_idx = idx
                break
        if insert_idx is not None:
            screen.data = screen.data[:insert_idx+1] + new_data + screen.data[insert_idx+1:]
        else:
            screen.data += new_data
        screen.populate_rv()