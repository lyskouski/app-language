# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for SettingsService."""

import pytest
from unittest.mock import Mock

from domain.entities.user_settings import UserSettings
from domain.use_cases.settings_use_cases import (
    LoadSettingsUseCase,
    UpdateLocaleUseCase,
    UpdateLanguagePairUseCase
)
from application.services.settings_service import SettingsService


class TestSettingsService:
    """Test settings service."""

    @pytest.fixture
    def mock_use_cases(self):
        """Create mock use cases."""
        load = Mock(spec=LoadSettingsUseCase)
        update_locale = Mock(spec=UpdateLocaleUseCase)
        update_pair = Mock(spec=UpdateLanguagePairUseCase)
        return load, update_locale, update_pair

    @pytest.fixture
    def settings_service(self, mock_use_cases):
        """Create settings service instance."""
        load, update_locale, update_pair = mock_use_cases
        return SettingsService(load, update_locale, update_pair)

    def test_load_settings(self, settings_service, mock_use_cases):
        """Test loading settings."""
        load_use_case = mock_use_cases[0]
        expected_settings = UserSettings(interface_locale="EN")
        load_use_case.execute.return_value = expected_settings

        result = settings_service.load_settings()

        assert result == expected_settings
        assert settings_service.get_current_settings() == expected_settings
        load_use_case.execute.assert_called_once()

    def test_get_current_settings(self, settings_service):
        """Test getting current settings."""
        result = settings_service.get_current_settings()

        assert isinstance(result, UserSettings)

    def test_update_interface_locale(self, settings_service, mock_use_cases):
        """Test updating interface locale."""
        update_locale_use_case = mock_use_cases[1]

        settings_service.update_interface_locale("ES")

        update_locale_use_case.execute.assert_called_once_with("ES")
        assert settings_service.get_current_settings().interface_locale == "ES"

    def test_update_language_pair(self, settings_service, mock_use_cases):
        """Test updating language pair."""
        update_pair_use_case = mock_use_cases[2]

        settings_service.update_language_pair("EN", "ES")

        update_pair_use_case.execute.assert_called_once_with("EN", "ES")
        current = settings_service.get_current_settings()
        assert current.locale_from == "EN"
        assert current.locale_to == "ES"

    def test_should_show_language_selection(self, settings_service, mock_use_cases):
        """Test language selection screen logic."""
        # No locale configured
        assert settings_service.should_show_language_selection() is True

        # Locale configured
        settings_service.update_interface_locale("EN")
        assert settings_service.should_show_language_selection() is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
