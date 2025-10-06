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
try:
    import component.card_screen
    import component.loading_screen
    import component.main_screen
    import component.dictionary_screen
    import component.phonetics_screen
    import component.articulation_screen
    import component.store_update_screen
    import component.structure_screen
    import component.structure_update_screen
    print("Successfully imported screen components")
except Exception as e:
    print(f"Warning: Failed to import screen components: {e}")

try:
    import component.harmonica_widget
    import component.phonetics_widget
    import component.recorder_widget
    import component.card_layout_widget
    print("Successfully imported widget components")
except Exception as e:
    print(f"Warning: Failed to import widget components: {e}")

try:
    import controller.audio_comparator
    import controller.media_controller
    print("Successfully imported controllers")
except Exception as e:
    print(f"Warning: Failed to import controllers: {e}")

try:
    import l18n.labels
    print("Successfully imported labels")
except Exception as e:
    print(f"Warning: Failed to import labels: {e}")

if __name__ == '__main__':
    print("=== TLUM APP STARTING ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 paths

    try:
        print("Importing MainApp...")
        from main import MainApp
        print("MainApp imported successfully")

        print("Creating MainApp instance...")
        app = MainApp()
        print("MainApp instance created")

        print("Starting app.run()...")
        app.run()
        print("App finished running")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("=== APP CRASHED ===")

    print("=== TLUM APP ENDED ===")
