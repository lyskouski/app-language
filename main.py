# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

# Entry point for Buildozer build for Android/iOS

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

os.chdir(src_dir)

## Load everything (for distribution) to avoid errors on start:
import component.card_screen
import component.loading_screen
import component.main_screen
import component.dictionary_screen
import component.phonetics_screen
import component.articulation_screen
import component.store_update_screen
import component.structure_screen
import component.structure_update_screen
import component.harmonica_widget
import component.phonetics_widget
import component.recorder_widget
import component.card_layout_widget
import controller.audio_comparator
import controller.media_controller
import l18n.labels

if __name__ == '__main__':
    from main import MainApp
    MainApp().run()
