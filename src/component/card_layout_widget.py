# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout


class CardWidget(Button):
    text_init = StringProperty('')
    text_flip = StringProperty('')

class CardLayoutWidget(StackLayout):
    flip = BooleanProperty(False)

    def load_data(self):
        app = App.get_running_app()
        self.clear_widgets()
        for item in app.store:
            button = CardWidget()
            button.text_init = item[1 if self.flip else 0]
            button.text_flip = item[0 if self.flip else 1]
            path = app.get_image_dir()
            image = app.find_resource(f"{path}/{item[3]}" if item[3] else 'assets/images/error.png')
            button.background_normal = image if image else app.find_resource('assets/images/error.png')
            button.background_down = app.find_resource('assets/images/success.png')
            self.add_widget(button)
