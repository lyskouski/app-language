# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for UserSettings entity."""

import pytest
from domain.entities.user_settings import UserSettings


class TestUserSettings:
    """Test domain entity UserSettings."""

    def test_create_user_settings(self):
        """Test creating user settings."""
        settings = UserSettings(
            interface_locale="EN",
            locale_from="EN",
            locale_to="ES"
        )

        assert settings.interface_locale == "EN"
        assert settings.locale_from == "EN"
        assert settings.locale_to == "ES"

    def test_has_locale_configured(self):
        """Test locale configuration check."""
        configured = UserSettings(interface_locale="EN")
        not_configured = UserSettings()

        assert configured.has_locale_configured() is True
        assert not_configured.has_locale_configured() is False

    def test_has_language_pair_configured(self):
        """Test language pair configuration check."""
        configured = UserSettings(locale_from="EN", locale_to="ES")
        partially_configured = UserSettings(locale_from="EN")
        not_configured = UserSettings()

        assert configured.has_language_pair_configured() is True
        assert partially_configured.has_language_pair_configured() is False
        assert not_configured.has_language_pair_configured() is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
