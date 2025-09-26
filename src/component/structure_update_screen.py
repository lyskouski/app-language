
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen

class StructureUpdateScreen(Screen):
    source = StringProperty('')
    parent_source = StringProperty('')
    text = StringProperty('')
    logo = StringProperty('')
    store_path = StringProperty('')
    route_path = StringProperty('')
    locale = StringProperty('')
    locale_to = StringProperty('')

    def init_data(self, widget = None):
        if widget is not None:
            self.source = widget.source
            self.parent_source = widget.parent_source
            self.text = widget.text
            self.logo = widget.logo
            self.store_path = widget.store_path
            self.route_path = widget.route_path
            self.locale = widget.locale
            self.locale_to = widget.locale_to
