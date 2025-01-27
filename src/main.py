# Initialization:
# > python -m venv kivy_venv
# > source kivy_venv/Scripts/activate
# > pip install -r requirements.txt

import kivy

from kivy.app import App

class MainApp(App):
  kv_directory = 'template'


if __name__ == '__main__':
    MainApp().run()
