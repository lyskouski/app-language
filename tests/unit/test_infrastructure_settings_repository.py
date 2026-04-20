# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for IniSettingsRepository."""

import pytest
from unittest.mock import Mock

from domain.entities.user_settings import UserSettings
from infrastructure.persistence.ini_settings_repository import IniSettingsRepository
from lib.ini_config_parser import IniConfigParser


class TestIniSettingsRepository:
    """Test INI settings repository."""

    @pytest.fixture
    def mock_config_parser(self):
        """Create mock config parser."""
        parser = Mock(spec=IniConfigParser)
        parser.get.return_value = ""
        return parser

    @pytest.fixture
    def repository(self, mock_config_parser):
        """Create repository instance."""
        return IniSettingsRepository(mock_config_parser)

    def test_load_settings(self, repository, mock_config_parser):
        """Test loading settings."""
        mock_config_parser.get.side_effect = lambda key, default: {
            IniConfigParser.INTERFACE_LOCALE: "EN",
            "locale_from": "EN",
            "locale_to": "ES"
        }.get(key, default)

        settings = repository.load()

        assert settings.interface_locale == "EN"
        assert settings.locale_from == "EN"
        assert settings.locale_to == "ES"

    def test_save_settings(self, repository, mock_config_parser):
        """Test saving settings."""
        settings = UserSettings(
            interface_locale="ES",
            locale_from="ES",
            locale_to="EN"
        )

        repository.save(settings)

        assert mock_config_parser.save.call_count == 3
        calls = mock_config_parser.save.call_args_list
        assert calls[0][0] == (IniConfigParser.INTERFACE_LOCALE, "ES")
        assert calls[1][0] == ("locale_from", "ES")
        assert calls[2][0] == ("locale_to", "EN")

    def test_get_setting(self, repository, mock_config_parser):
        """Test getting a specific setting."""
        mock_config_parser.get.return_value = "value"

        result = repository.get_setting("key", "default")

        mock_config_parser.get.assert_called_once_with("key", "default")
        assert result == "value"

    def test_set_setting(self, repository, mock_config_parser):
        """Test setting a specific setting."""
        repository.set_setting("key", "value")

        mock_config_parser.save.assert_called_once_with("key", "value")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
