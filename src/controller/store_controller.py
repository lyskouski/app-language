# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import random
from typing import List, Optional
from model.store_item import StoreItem
from controller.vocabulary_profiler import VocabularyProfiler

class StoreController:
    store: List[StoreItem] = []
    limit: int = 25
    profiler: Optional[VocabularyProfiler] = None

    def load_store(self, app, data_path):
        path = app.find_resource(data_path)
        try:
            self.profiler = VocabularyProfiler(
                app.get_with_home_dir(f"{data_path}.json"),
                app.get_with_home_dir(f"{data_path}.pkl")
            )
        except Exception as e:
            print(f"⚠️  ML profiling disabled due to error: {e}")
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

    def mark_positive(self, item: StoreItem):
        if self.profiler:
            self.profiler.mark_positive(item)

    def mark_negative(self, item: StoreItem):
        if self.profiler:
            self.profiler.mark_negative(item)

    def set_limit(self, limit:int):
        self.limit = limit

    def shuffle_store(self):
        if self.profiler:
            self.store = self.profiler.get_prioritized_items(self.store, self.limit)
            random.shuffle(self.store)
        else:
            random.shuffle(self.store)
            self.store = self.store[:self.limit]

    def get(self) -> List[StoreItem]:
        return self.store
