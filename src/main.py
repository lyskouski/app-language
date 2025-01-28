# Initialization:
# > python -m venv kivy_venv
# > source kivy_venv/Scripts/activate
# > pip install -r requirements.txt

import kivy

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

class RootWidget(BoxLayout):
    container = ObjectProperty(None)

class MainApp(App):
    kv_directory = 'template'

    def next_screen(self, screen):
        filepath = self.kv_directory + '/' + screen + '.kv'
        Builder.unload_file(filepath)
        self.root.container.clear_widgets()
        screen = Builder.load_file(filepath)
        self.root.container.add_widget(screen)

if __name__ == '__main__':
    MainApp().run()
