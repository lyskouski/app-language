import json
import os
import kivy
import kivy.resources

from kivy.app import App
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

    def load_breadcrumb(self, path):
        breadcrumbs = self.ids.breadcrumb_view.data
        cut_index = None
        for i, crumb in enumerate(breadcrumbs):
            if crumb.get('source') == path:
                cut_index = i
                break
        if cut_index is not None:
            self.ids.breadcrumb_view.data = breadcrumbs[:cut_index]
        self.load_data(path)
        self.populate_rv()

    def load_data(self, path = None):
        if not path:
            path = self.path
        source_path = kivy.resources.resource_find(path)
        if source_path and os.path.exists(source_path):
            with open(source_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = []

    def update_data(self, root):
        app = App.get_running_app()
        if (root.store_path != ''):
            app.init_store(root.store_path)
        if (root.locale != ''):
            app.update_locale(root.locale)
        if not self.ids.breadcrumb_view.data:
            self.ids.breadcrumb_view.data = []
            self.path = 'assets/source.json'
        self.ids.breadcrumb_view.data.append({'text': root.text, 'source': self.path})
        self.path = root.source
        self.load_data()
        self.populate_rv()

    def populate_rv(self):
        self.ids.recycle_view.data = self.data
