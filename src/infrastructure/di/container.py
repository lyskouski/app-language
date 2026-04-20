# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from typing import Optional
import kivy.resources
import os
import sys

from lib.ini_config_parser import IniConfigParser
from kivy.utils import platform

# Domain
from domain.repositories.vocabulary_repository import IVocabularyRepository
from domain.repositories.settings_repository import ISettingsRepository
from domain.repositories.resource_repository import IResourceRepository
from domain.services import IVocabularyProfiler
from domain.services.audio_comparator import IAudioComparator
from domain.use_cases.vocabulary_use_cases import LoadVocabularyUseCase, ShuffleVocabularyUseCase
from domain.use_cases.settings_use_cases import (
    LoadSettingsUseCase,
    UpdateLocaleUseCase,
    UpdateLanguagePairUseCase
)

# Application
from application.services.vocabulary_service import VocabularyService
from application.services.settings_service import SettingsService
from application.services.resource_service import ResourceService
from application.services.resource_service import LocalizationService
from application.services.media_service import MediaService
from application.services.recorder_service import RecorderService, IRecorderController

# Infrastructure
from infrastructure.persistence.file_vocabulary_repository import FileVocabularyRepository
from infrastructure.persistence.ini_settings_repository import IniSettingsRepository
from infrastructure.persistence.kivy_resource_repository import KivyResourceRepository
from infrastructure.ml.ml_vocabulary_profiler import MLVocabularyProfiler
from infrastructure.audio.librosa_audio_comparator import LibrosaAudioComparator


class DependencyContainer:
    """
    Dependency Injection Container - Composition Root.
    Follows Dependency Inversion Principle: wires dependencies at the outermost layer.

    This is the only place where concrete implementations are instantiated.
    """

    def __init__(self, user_data_dir: str):
        self._user_data_dir = user_data_dir
        self._instances = {}

    def _get_or_create(self, key: str, factory):
        """Get or create a singleton instance."""
        if key not in self._instances:
            self._instances[key] = factory()
        return self._instances[key]

    # Repositories
    def vocabulary_repository(self) -> IVocabularyRepository:
        """Get vocabulary repository instance."""
        return self._get_or_create(
            'vocabulary_repository',
            lambda: FileVocabularyRepository()
        )

    def settings_repository(self) -> ISettingsRepository:
        """Get settings repository instance."""
        return self._get_or_create(
            'settings_repository',
            lambda: IniSettingsRepository(self.config_parser())
        )

    def resource_repository(self) -> IResourceRepository:
        """Get resource repository instance."""
        return self._get_or_create(
            'resource_repository',
            lambda: KivyResourceRepository(self._user_data_dir)
        )

    # Infrastructure components
    def config_parser(self) -> IniConfigParser:
        """Get config parser instance."""
        return self._get_or_create(
            'config_parser',
            lambda: IniConfigParser(self.resource_repository().get_home_dir())
        )

    def vocabulary_profiler(self, data_path: str) -> Optional[IVocabularyProfiler]:
        """Get vocabulary profiler instance."""
        try:
            resource_repo = self.resource_repository()
            return MLVocabularyProfiler(
                resource_repo.get_path_with_home_dir(f"{data_path}.json"),
                resource_repo.get_path_with_home_dir(f"{data_path}.pkl")
            )
        except Exception as e:
            print(f"⚠️  ML profiling disabled due to error: {e}")
            return None

    def audio_comparator(self) -> IAudioComparator:
        """Get audio comparator instance."""
        return self._get_or_create(
            'audio_comparator',
            lambda: LibrosaAudioComparator()
        )

    def recorder_controller(self) -> IRecorderController:
        """Get platform-specific recorder controller."""
        if platform == 'android':
            from controller.recorder_controller_android import RecorderControllerAndroid
            return RecorderControllerAndroid()
        elif platform == 'ios':
            from controller.recorder_controller_ios import RecorderControllerIos
            return RecorderControllerIos()
        else:
            from controller.recorder_controller_desktop import RecorderControllerDesktop
            return RecorderControllerDesktop()

    # Use Cases
    def load_vocabulary_use_case(self) -> LoadVocabularyUseCase:
        """Get load vocabulary use case."""
        return self._get_or_create(
            'load_vocabulary_use_case',
            lambda: LoadVocabularyUseCase(self.vocabulary_repository())
        )

    def shuffle_vocabulary_use_case(self) -> ShuffleVocabularyUseCase:
        """Get shuffle vocabulary use case."""
        return self._get_or_create(
            'shuffle_vocabulary_use_case',
            lambda: ShuffleVocabularyUseCase()
        )

    def load_settings_use_case(self) -> LoadSettingsUseCase:
        """Get load settings use case."""
        return self._get_or_create(
            'load_settings_use_case',
            lambda: LoadSettingsUseCase(self.settings_repository())
        )

    def update_locale_use_case(self) -> UpdateLocaleUseCase:
        """Get update locale use case."""
        return self._get_or_create(
            'update_locale_use_case',
            lambda: UpdateLocaleUseCase(self.settings_repository())
        )

    def update_language_pair_use_case(self) -> UpdateLanguagePairUseCase:
        """Get update language pair use case."""
        return self._get_or_create(
            'update_language_pair_use_case',
            lambda: UpdateLanguagePairUseCase(self.settings_repository())
        )

    # Services
    def vocabulary_service(self, data_path: Optional[str] = None) -> VocabularyService:
        """Get vocabulary service instance."""
        profiler = None
        if data_path:
            profiler = self.vocabulary_profiler(data_path)

        return VocabularyService(
            self.load_vocabulary_use_case(),
            self.shuffle_vocabulary_use_case(),
            profiler
        )

    def settings_service(self) -> SettingsService:
        """Get settings service instance."""
        return self._get_or_create(
            'settings_service',
            lambda: SettingsService(
                self.load_settings_use_case(),
                self.update_locale_use_case(),
                self.update_language_pair_use_case()
            )
        )

    def media_service(self, lang: str = 'en', audio_dir: str = 'assets/data/EN/audio/') -> MediaService:
        """Get media service instance."""
        return MediaService(lang, audio_dir)

    def recorder_service(self) -> RecorderService:
        """Get recorder service instance."""
        return self._get_or_create(
            'recorder_service',
            lambda: RecorderService(self.recorder_controller())
        )

    def resource_service(self) -> ResourceService:
        """Get resource service instance."""
        return self._get_or_create(
            'resource_service',
            lambda: ResourceService(self.resource_repository())
        )

    def localization_service(self) -> LocalizationService:
        """Get localization service instance."""
        return self._get_or_create(
            'localization_service',
            lambda: LocalizationService()
        )

    def setup_kivy_resources(self):
        """Setup Kivy resource paths."""
        home_dir = self.resource_repository().get_home_dir()
        kivy.resources.resource_paths.insert(0, home_dir)
        kivy.resources.resource_add_path(os.getcwd())
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels from infrastructure/di to src
        src_dir = os.path.dirname(os.path.dirname(current_dir))
        kivy.resources.resource_add_path(src_dir)
        kivy.resources.resource_add_path(os.path.dirname(src_dir))
        if getattr(sys, 'frozen', False):
            kivy.resources.resource_add_path(sys._MEIPASS)
