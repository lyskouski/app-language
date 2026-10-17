# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.app import App
from kivy.factory import Factory
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput


class SearchableSpinner(Spinner):
    """Spinner whose opened dropdown starts with a search field narrowing the listed options."""

    def __init__(self, **kwargs):
        self._search_input = None
        super(SearchableSpinner, self).__init__(**kwargs)

    def _get_search_input(self):
        if self._search_input is None:
            app = App.get_running_app()
            search = TextInput(multiline=False, hint_text=app._('search', app.locale) if app else '')
            search.bind(text=self._update_dropdown)
            # Bound after the theme rule, so Enter picks the first match instead of jumping to the next form field
            search.bind(on_text_validate=self._select_first_match)
            self._search_input = search
        return self._search_input

    def _filtered_values(self):
        query = self._get_search_input().text.strip().lower()
        if not query:
            return list(self.values)
        return [value for value in self.values if query in value.lower()]

    def _update_dropdown(self, *largs):
        """Rebuild the options below the search field, keeping the field (and its focus) in place."""
        dp = self._dropdown
        if dp is None:
            return
        cls = self.option_cls
        if isinstance(cls, str):
            cls = Factory.get(cls)
        search = self._get_search_input()
        for child in dp.container.children[:]:
            if child is not search:
                dp.remove_widget(child)
        if search.parent is None:
            dp.add_widget(search)
        for value in self._filtered_values():
            item = cls(text=value)
            item.height = self.height if self.sync_height else item.height
            item.bind(on_release=lambda option: dp.select(option.text))
            dp.add_widget(item)

    def _update_dropdown_size(self, *largs):
        super(SearchableSpinner, self)._update_dropdown_size(*largs)
        if self._search_input is not None and self.sync_height:
            self._search_input.height = self.height

    def _select_first_match(self, *largs):
        matches = self._filtered_values()
        if matches:
            self._dropdown.select(matches[0])
        return True

    def on_is_open(self, instance, value):
        if value:
            # Every opening starts with the full list
            self._get_search_input().text = ''
        super(SearchableSpinner, self).on_is_open(instance, value)
