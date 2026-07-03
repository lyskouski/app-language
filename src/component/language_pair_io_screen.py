# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen

from application.services.language_pair_io_service import LanguagePairIOService


class LanguagePairIOScreen(Screen):
    """Screen for exporting / importing a language pair (categories + vocabulary)."""

    # Bound from the caller via app.next_screen
    locale_from = StringProperty('')
    locale_to = StringProperty('')
    pair_name = StringProperty('')

    # UI state
    file_path = StringProperty('')
    status_text = StringProperty('')
    is_busy = BooleanProperty(False)

    # True = export mode; False = import mode
    export_mode = BooleanProperty(True)

    # Merge flag for import (append vs replace)
    merge_import = BooleanProperty(False)

    def on_enter(self):
        """Populate default file path when the screen becomes active."""
        app = App.get_running_app()
        home = app.get_home_dir() if hasattr(app, 'get_home_dir') else os.path.expanduser('~')
        if not self.file_path:
            pair_tag = f'{self.locale_from}-{self.locale_to}' if (self.locale_from and self.locale_to) else 'language_pair'
            self.file_path = os.path.join(home, f'{pair_tag}.json')
        self.status_text = ''

    def _get_service(self) -> LanguagePairIOService:
        app = App.get_running_app()
        vocab_repo = app._container.vocabulary_repository()
        config_repo = app._container.config_repository()
        return LanguagePairIOService(vocab_repo, config_repo)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def do_export(self):
        if self.is_busy:
            return
        self.is_busy = True
        self.status_text = ''
        Clock.schedule_once(lambda dt: self._run_export(), 0)

    def _run_export(self):
        try:
            service = self._get_service()
            count = service.export_language_pair(self.locale_from, self.locale_to, self.file_path)
            self.status_text = f'Exported {count} words to:\n{self.file_path}'
        except Exception as exc:
            self.status_text = f'Export failed: {exc}'
        finally:
            self.is_busy = False

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def do_import(self):
        if self.is_busy:
            return
        self.is_busy = True
        self.status_text = ''
        Clock.schedule_once(lambda dt: self._run_import(), 0)

    def _run_import(self):
        try:
            service = self._get_service()
            result = service.import_language_pair(self.file_path, merge=self.merge_import)
            self.status_text = (
                f"Imported {result['vocabulary_imported']} words, "
                f"{result['categories_imported']} categories "
                f"({result['locale_from']}-{result['locale_to']})"
            )
        except Exception as exc:
            self.status_text = f'Import failed: {exc}'
        finally:
            self.is_busy = False

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def go_back(self):
        App.get_running_app().next_screen('main_screen')
