# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import random
from typing import List

class StoreItem:
    origin = ''
    translation = ''
    sound = None
    image = None

    def __init__(self, origin, translation, sound=None, image=None):
        self.origin = origin
        self.translation = translation
        self.sound = sound
        self.image = image

class StoreController:
    store = []

    def load_store(self, app, data_path):
        path = app.find_resource(data_path)
        lines = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            pass
        parsed_data = []
        for line in lines:
            if ";" in line:
                parts = [p.strip() for p in line.strip().split(";")]
                if len(parts) == 4:
                    origin, trans, sound, image = parts
                elif len(parts) == 3:
                    origin, trans, sound = parts
                    image = None
                elif len(parts) == 2:
                    origin, trans = parts
                    sound = None
                    image = None
                else:
                    continue
                parsed_data.append(StoreItem(origin, trans, sound, image))
        self.store = parsed_data

    def shuffle_store(self):
        random.shuffle(self.store)

    def get(self, size: int = 25) -> List[StoreItem]:
        return self.store[:size]
