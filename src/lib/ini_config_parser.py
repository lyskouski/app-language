# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os

from kivy.config import ConfigParser

class IniConfigParser():
    INTERFACE_LOCALE = 'interface_locale'
    
    def __init__(self, dir: str, section: str = 'settings'):
        self.parser = ConfigParser()
        self.config_path = os.path.join(dir, 'tlum.ini')
        self.section = section
        self.parser.read(self.config_path)
        if not self.parser.has_section(self.section):
            self.parser.add_section(self.section)
        if not self.parser.has_option(self.section, self.INTERFACE_LOCALE):
            self.parser.set(self.section, self.INTERFACE_LOCALE, '')

    def get(self, key: str, default: str = '') -> str:
        try:
            value = self.parser.get(self.section, key)
        except Exception as e:
            value = default
        return value

    def save(self, key: str, value: str):
        try:
            self.parser.set(self.section, key, value)
            self.parser.write()
        except Exception as e:
            print(f"Warning: Could not save locale settings: {e}")
