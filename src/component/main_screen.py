import json
import os
import kivy
import kivy.resources

from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

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
