from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen

class LoadingScreen(Screen):
    status = NumericProperty(0)
