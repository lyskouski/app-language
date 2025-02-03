from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty, StringProperty

class HarmonicaWidget(ScrollView):
    origin = BooleanProperty(False)
    secondary = BooleanProperty(False)
    data_file = StringProperty("assets/data/harmonica.txt")

    def on_kv_post(self, base_widget):
        self.load_data()

    def load_data(self):
        self.clear_widgets()

        layout = GridLayout(cols=1, size_hint_y='2dp', spacing=5)
        layout.bind(minimum_height=layout.setter("height"))

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                if ":" in line:
                    origin, trans = line.strip().split(":", 1)
                    origin, trans = origin.strip(), trans.strip()

                    self.add_row(layout, origin, trans)
        except FileNotFoundError:
            layout.add_widget(Label(text="Error: File not found!"))

        self.add_widget(layout)

    def add_row(self, layout, origin, trans):
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

        layout.add_widget(row)
