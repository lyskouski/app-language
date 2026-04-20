# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for DependencyContainer."""

import pytest

from infrastructure.di.container import DependencyContainer


class TestDependencyInjection:
    """Test dependency injection container."""

    @pytest.fixture
    def container(self, tmp_path):
        """Create a DI container instance for testing."""
        return DependencyContainer(str(tmp_path))

    def test_vocabulary_repository_singleton(self, container):
        """Test that vocabulary repository is a singleton."""
        repo1 = container.vocabulary_repository()
        repo2 = container.vocabulary_repository()

        assert repo1 is repo2

    def test_settings_service_singleton(self, container):
        """Test that settings service is a singleton."""
        service1 = container.settings_service()
        service2 = container.settings_service()

        assert service1 is service2

    def test_media_service_creates_new_instance(self, container):
        """Test that media service creates new instances."""
        service1 = container.media_service('en', '/path1')
        service2 = container.media_service('es', '/path2')

        # Different instances with different configs
        assert service1 is not service2

    def test_audio_comparator_available(self, container):
        """Test that audio comparator can be created."""
        comparator = container.audio_comparator()

        assert comparator is not None
        assert hasattr(comparator, 'compare_audio')

    def test_recorder_service_available(self, container):
        """Test that recorder service can be created."""
        service = container.recorder_service()

        assert service is not None
        assert hasattr(service, 'start_recording')
        assert hasattr(service, 'stop_recording')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
