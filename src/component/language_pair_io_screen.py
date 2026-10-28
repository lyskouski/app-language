# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import importlib
import os
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.utils import platform

from application.services.language_pair_io_service import LanguagePairIOService
from infrastructure.ui import portal_file_chooser


def _get_download_dir() -> str:
    if platform == "android":
        storage = importlib.import_module("android.storage")
        return os.path.join(storage.primary_external_storage_path(), "Download")
    if platform == "ios" or portal_file_chooser.is_available():
        return App.get_running_app().user_data_dir
    return os.path.join(os.path.expanduser("~"), "Downloads")


def _get_app_files_dir() -> str:
    # App-specific external folder (/sdcard/Android/data/<package>/files) is readable without permissions
    if platform == "android":
        jnius = importlib.import_module("jnius")
        activity = jnius.autoclass("org.kivy.android.PythonActivity").mActivity
        files_dir = activity.getExternalFilesDir(None)
        if files_dir is not None:
            return files_dir.getAbsolutePath()
    return App.get_running_app().user_data_dir


def _get_service() -> LanguagePairIOService:
    app = App.get_running_app()
    return LanguagePairIOService(
        app._container.vocabulary_repository(),
        app._container.config_repository(),
    )


def _target_path(screen) -> str:
    return screen.app_file_path if screen.use_app_folder else screen.file_path


def _open_portal_chooser(screen, save_mode: bool):
    def on_result(path):
        if path:
            Clock.schedule_once(lambda dt: setattr(screen, "file_path", path), 0)

    if save_mode:
        default_name = os.path.basename(screen.file_path) or "language_pair.json"
        portal_file_chooser.save_file("Save file", default_name, on_result)
    else:
        portal_file_chooser.open_file("Choose file", on_result)


def _open_file_chooser(screen, dir_mode: bool, path_attr: str = "file_path", base_dir: str = ""):
    if path_attr == "file_path" and portal_file_chooser.is_available():
        _open_portal_chooser(screen, save_mode=dir_mode)
        return

    base_dir = base_dir or _get_download_dir()
    current = getattr(screen, path_attr)
    start_dir = os.path.dirname(current) if current else base_dir
    if not os.path.isdir(start_dir):
        start_dir = base_dir if os.path.isdir(base_dir) else os.path.expanduser("~")

    chooser = FileChooserListView(
        path=start_dir,
        dirselect=dir_mode,
        filters=[] if dir_mode else ["*.json"],
    )

    box = BoxLayout(orientation="vertical", spacing=4, padding=8)
    box.add_widget(chooser)

    btn_row = BoxLayout(size_hint_y=None, height=44, spacing=8)
    app = App.get_running_app()
    btn_cancel = Button(text=app._("button_cancel", app.locale))
    btn_select = Button(text=app._("button_select", app.locale))
    btn_row.add_widget(btn_cancel)
    btn_row.add_widget(btn_select)
    box.add_widget(btn_row)

    popup = Popup(
        title="Choose folder" if dir_mode else "Choose file",
        content=box,
        size_hint=(0.9, 0.85),
    )

    def on_select(_btn):
        selection = chooser.selection
        if selection:
            chosen = selection[0]
            if dir_mode:
                default_name = os.path.basename(current) or "language_pair.json"
                setattr(screen, path_attr, os.path.join(
                    chosen if os.path.isdir(chosen) else os.path.dirname(chosen),
                    default_name,
                ))
            else:
                setattr(screen, path_attr, chosen)
        popup.dismiss()

    btn_cancel.bind(on_release=lambda _: popup.dismiss())
    btn_select.bind(on_release=on_select)
    popup.open()


class LanguagePairExportScreen(Screen):
    locale_from = StringProperty("")
    locale_to = StringProperty("")
    pair_name = StringProperty("")
    file_path = StringProperty("")
    app_file_path = StringProperty("")
    use_app_folder = BooleanProperty(False)
    status_text = StringProperty("")
    is_busy = BooleanProperty(False)

    def on_enter(self):
        pair_tag = f"{self.locale_from}-{self.locale_to}" if (self.locale_from and self.locale_to) else "language_pair"
        if not self.file_path:
            self.file_path = os.path.join(_get_download_dir(), f"{pair_tag}.json")
        if not self.app_file_path:
            self.app_file_path = os.path.join(_get_app_files_dir(), f"{pair_tag}.json")
        self.status_text = ""

    def open_file_chooser(self):
        _open_file_chooser(self, dir_mode=True)

    def open_app_file_chooser(self):
        _open_file_chooser(self, dir_mode=True, path_attr="app_file_path", base_dir=_get_app_files_dir())

    def do_export(self):
        if self.is_busy:
            return
        self.is_busy = True
        self.status_text = ""
        Clock.schedule_once(lambda dt: self._run_export(), 0)

    def _run_export(self):
        try:
            target = _target_path(self)
            count = _get_service().export_language_pair(self.locale_from, self.locale_to, target)
            self.status_text = f"Exported {count} words to:\n{target}"
        except Exception as exc:
            self.status_text = f"Export failed: {exc}"
        finally:
            self.is_busy = False

    def go_back(self):
        App.get_running_app().next_screen("main_screen")


class LanguagePairImportScreen(Screen):
    file_path = StringProperty("")
    app_file_path = StringProperty("")
    use_app_folder = BooleanProperty(False)
    status_text = StringProperty("")
    is_busy = BooleanProperty(False)
    merge_import = BooleanProperty(False)

    def on_enter(self):
        if not self.file_path:
            self.file_path = os.path.join(_get_download_dir(), "language_pair.json")
        if not self.app_file_path:
            self.app_file_path = os.path.join(_get_app_files_dir(), "language_pair.json")
        self.status_text = ""

    def open_file_chooser(self):
        _open_file_chooser(self, dir_mode=False)

    def open_app_file_chooser(self):
        _open_file_chooser(self, dir_mode=False, path_attr="app_file_path", base_dir=_get_app_files_dir())

    def do_import(self):
        if self.is_busy:
            return
        self.is_busy = True
        self.status_text = ""
        Clock.schedule_once(lambda dt: self._run_import(), 0)

    def _run_import(self):
        try:
            result = _get_service().import_language_pair(_target_path(self), merge=self.merge_import)
            self.status_text = (
                f"Imported {result['vocabulary_imported']} words, "
                f"{result['categories_imported']} categories "
                f"({result['locale_from']}-{result['locale_to']})"
            )
        except Exception as exc:
            self.status_text = f"Import failed: {exc}"
        finally:
            self.is_busy = False

    def go_back(self):
        App.get_running_app().next_screen("main_screen")
