# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for settings use cases."""

import pytest
from unittest.mock import Mock

from domain.entities.user_settings import UserSettings
from domain.use_cases.settings_use_cases import (
    LoadSettingsUseCase,
    UpdateLocaleUseCase,
    UpdateLanguagePairUseCase
)
from domain.repositories.settings_repository import ISettingsRepository


class TestLoadSettingsUseCase:
    """Test LoadSettingsUseCase."""

    def test_execute_loads_from_repository(self):
        """Test loading settings from repository."""
        mock_repo = Mock(spec=ISettingsRepository)
        expected_settings = UserSettings(interface_locale="EN")
        mock_repo.load.return_value = expected_settings

        use_case = LoadSettingsUseCase(mock_repo)
        result = use_case.execute()

        assert result == expected_settings
        mock_repo.load.assert_called_once()


class TestUpdateLocaleUseCase:
    """Test UpdateLocaleUseCase."""

    def test_execute_updates_locale(self):
        """Test updating interface locale."""
        mock_repo = Mock(spec=ISettingsRepository)
        current_settings = UserSettings(interface_locale="EN")
        mock_repo.load.return_value = current_settings

        use_case = UpdateLocaleUseCase(mock_repo)
        use_case.execute("ES")

        mock_repo.load.assert_called_once()
        mock_repo.save.assert_called_once()
        saved_settings = mock_repo.save.call_args[0][0]
        assert saved_settings.interface_locale == "ES"


class TestUpdateLanguagePairUseCase:
    """Test UpdateLanguagePairUseCase."""

    def test_execute_updates_language_pair(self):
        """Test updating language pair."""
        mock_repo = Mock(spec=ISettingsRepository)
        current_settings = UserSettings()
        mock_repo.load.return_value = current_settings

        use_case = UpdateLanguagePairUseCase(mock_repo)
        use_case.execute("EN", "ES")

        mock_repo.load.assert_called_once()
        mock_repo.save.assert_called_once()
        saved_settings = mock_repo.save.call_args[0][0]
        assert saved_settings.locale_from == "EN"
        assert saved_settings.locale_to == "ES"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
