# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import json
import os

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

class StructureUpdateScreen(Screen):
    source = StringProperty('')
    parent_source = StringProperty('')
    text = StringProperty('')
    text_initial = StringProperty('')
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
            self.text_initial = widget.text
            self.logo = widget.logo
            self.store_path = widget.store_path
            self.route_path = widget.route_path
            self.locale = widget.locale
            self.locale_to = widget.locale_to

    def update_data(self):
        app = App.get_running_app()
        if self.source != '':
            os.makedirs(os.path.join(app.get_home_dir(), os.path.dirname(self.source)), exist_ok=True)
        if self.store_path != '':
            store_full_path = os.path.join(app.get_home_dir(), self.store_path)
            os.makedirs(os.path.dirname(store_full_path), exist_ok=True)
            if not os.path.exists(store_full_path):
                with open(store_full_path, 'w', encoding='utf-8') as f:
                    f.write('original ; translation ; audio file name with extension (.mp3)\n')
        data = []
        initial_path = app.find_resource(self.parent_source)
        if initial_path is not None and os.path.exists(initial_path):
            with open(initial_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

        insert_idx = None
        new_data = [{
            'text': self.text,
            'source': self.source,
            'logo': self.logo,
            'store_path': self.store_path,
            'route_path': self.route_path,
            'locale': self.locale,
            'locale_to': self.locale_to,
        }]
        for idx, item in enumerate(data):
            if isinstance(item, dict) and item.get('text') == self.text_initial:
                insert_idx = idx
                break
        if insert_idx is not None:
            data = data[:insert_idx] + new_data + data[insert_idx+1:]
        else:
            data += new_data

        source_path = os.path.join(app.get_home_dir(), self.parent_source)
        os.makedirs(os.path.dirname(source_path), exist_ok=True)
        with open(source_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
