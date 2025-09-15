from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.widget import Widget

class HarmonicaWidget(ScrollView):
    origin = BooleanProperty(False)
    secondary = BooleanProperty(False)

    def on_kv_post(self, base_widget):
        self.load_data()

    def load_data(self):
        self.clear_widgets()

        layout = GridLayout(cols=1, size_hint_y='2dp', spacing=5)
        layout.bind(minimum_height=layout.setter('height'))

        app = App.get_running_app()
        for origin, trans, _ in app.store:
            self.add_row(layout, origin, trans)

        self.add_widget(layout)

    def add_row(self, layout, origin, trans):
        row = BoxLayout(orientation='horizontal', size_hint_min_y=30)

        if self.origin and self.secondary:
            row.add_widget(Label(text=origin))
            row.add_widget(Label(text=trans))

        elif self.origin and not self.secondary:
            row.add_widget(Label(text=origin))
            text_input = TextInput(text='', multiline=False)
            text_input.bind(on_text_validate=self.validate_trans)
            row.add_widget(text_input)

        elif not self.origin and self.secondary:
            row.add_widget(Label(text=trans))
            text_input = TextInput(text='', multiline=False)
            text_input.bind(on_text_validate=self.validate_origin)
            row.add_widget(text_input)

        row.add_widget(Widget(size_hint_x=None, width=10))
        layout.add_widget(row)

    def __get_pair(self, instance, is_origin):
        key = instance.parent.children[2].text.strip()
        app = App.get_running_app()
        for origin, trans, _ in app.store:
            if origin == key or trans == key:
                return origin if is_origin else trans
            
    def __validate(self, instance, is_origin):
        text = instance.text.strip()
        pair = self.__get_pair(instance, is_origin)
        parent = instance.parent
        parent.remove_widget(instance)
        if (pair == text):
            icon = Image(source='assets/images/success.png', size_hint=(None, None), size=(30, 30))
            parent.add_widget(icon)
            parent.add_widget(Label(text=pair))
        else:
            icon = Image(source='assets/images/error.png', size_hint=(None, None), size=(30, 30))
            parent.add_widget(icon)
            parent.add_widget(Label(text=f'[s]{text}[/s] {pair}', markup=True))

    def validate_origin(self, instance):
        self.__validate(instance, True)

    def validate_trans(self, instance):
        self.__validate(instance, False)
