#!/usr/bin/env python3

# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Generate store screenshots for all devices and interface languages.

  python tools/capture_screenshots.py
  SCREENSHOT_DEVICES="iPhone 15 Pro,Pixel 7a" SCREENSHOT_LOCALES=EN,DE python tools/capture_screenshots.py
  SCREENSHOT_STEPS=2_language_pair SKIP_EXISTANT=true SCREENSHOT_WORKERS=4 python tools/capture_screenshots.py

Every screenshot starts the app with an empty profile, so personal data never leaks into the images.
"""

import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

from kivy_screenshot_generator import ScreenshotConfig, ScreenshotGenerator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / 'src'

sys.path.insert(0, str(SRC_DIR))
from l18n.labels import labels  # noqa: E402

_profile_dir = None


def init(device, config, locale):
    global _profile_dir
    _profile_dir = tempfile.mkdtemp(prefix='tlum_screenshot_')
    atexit.register(shutil.rmtree, _profile_dir, ignore_errors=True)


def get_app():
    # The app resolves templates and assets relative to `src`
    os.chdir(SRC_DIR)
    from main import MainApp

    class ScreenshotApp(MainApp):
        @property
        def user_data_dir(self):
            return _profile_dir

    app = ScreenshotApp()
    app.update_locale(gen.job.locale)
    return app


async def open_language_pair(tester):
    await tester.show_screen('language_pair_add_screen')
    await tester.tap(tester.find_by_id('from_language'))
    await tester.pump_and_settle()
    # The search field of the opened dropdown is focused automatically
    await tester.enter_text(tester.find(lambda w: getattr(w, 'focus', False)), 'en')


gen = ScreenshotGenerator(
    locales=list(labels),
    fn_init=init,
    fn_get_app=get_app,
    config=ScreenshotConfig(output_directory=str(PROJECT_ROOT / 'screenshots')),
)
gen.inject('1_main')
gen.inject('2_language_pair', before=open_language_pair)

if __name__ == '__main__':
    gen.run()
