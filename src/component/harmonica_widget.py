from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty, StringProperty

class HarmonicaWidget(BoxLayout):
    origin = BooleanProperty(False)
    secondary = BooleanProperty(False)
    data_file = StringProperty("assets/data/harmonica.txt")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

    def on_kv_post(self, base_widget):
        self.load_data()

    def load_data(self):
        self.clear_widgets()
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                if ":" in line:
                    origin, trans = line.strip().split(":", 1)
                    origin, trans = origin.strip(), trans.strip()

                    self.add_row(origin, trans)
        except FileNotFoundError:
            self.add_widget(Label(text="Error: File not found!"))

    def add_row(self, origin, trans):
        row = BoxLayout(orientation='horizontal')

        if self.origin and self.secondary:
            row.add_widget(Label(text=origin))
            row.add_widget(Label(text=trans))

        elif self.origin and not self.secondary:
            row.add_widget(Label(text=origin))
            row.add_widget(TextInput(text=trans))

        elif not self.origin and self.secondary:
            row.add_widget(Label(text=trans))
            row.add_widget(TextInput(text=origin))

        self.add_widget(row)
