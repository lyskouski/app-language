# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen

class LoadingScreen(Screen):
    status = NumericProperty(0)
