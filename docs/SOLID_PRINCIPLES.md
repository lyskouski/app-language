# SOLID Principles in the Refactored Architecture

This document explains how each SOLID principle is applied in the refactored codebase.

## 1. Single Responsibility Principle (SRP)

**"A class should have one, and only one, reason to change."**

### Before Refactoring

The `MainApp` class had multiple responsibilities:
- Application lifecycle management
- Configuration management
- Resource path management
- Localization
- Directory creation
- Store management

```python
# OLD: MainApp doing too much
class MainApp(App):
    def __init__(self):
        self.settings_config = IniConfigParser(home_dir)
        self.locale = self.settings_config.get(...)
        kivy.resources.resource_paths.insert(0, home_dir)
        # ... many more responsibilities
```

### After Refactoring

Each service has a single, well-defined responsibility:

**SettingsService** - Only manages settings:
```python
class SettingsService:
    def load_settings(self) -> UserSettings: ...
    def update_interface_locale(self, locale: str) -> None: ...
```

**ResourceService** - Only manages resources:
```python
class ResourceService:
    def find_resource(self, path: str) -> str: ...
    def get_audio_directory(self, locale: str) -> str: ...
```

**VocabularyService** - Only manages vocabulary:
```python
class VocabularyService:
    def load_vocabulary(self, file_path: str) -> None: ...
    def prepare_study_set(self, limit: int) -> List[VocabularyItem]: ...
```

**LocalizationService** - Only handles translations:
```python
class LocalizationService:
    def translate(self, key: str, locale: str) -> str: ...
```

## 2. Open/Closed Principle (OCP)

**"Software entities should be open for extension, but closed for modification."**

### Repository Pattern Example

The repository interfaces allow new storage implementations without modifying existing code:

```python
# Domain defines the interface (closed for modification)
class IVocabularyRepository(ABC):
    @abstractmethod
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        pass
```

**Adding new storage (open for extension):**

```python
# File-based implementation
class FileVocabularyRepository(IVocabularyRepository):
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        # File-based implementation
        ...

# Can add database implementation without changing domain
class DatabaseVocabularyRepository(IVocabularyRepository):
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        # Database implementation
        ...

# Can add API-based implementation
class ApiVocabularyRepository(IVocabularyRepository):
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        # API implementation
        ...
```

The `LoadVocabularyUseCase` doesn't need to change when adding new storage types:

```python
class LoadVocabularyUseCase:
    def __init__(self, repository: IVocabularyRepository):  # Works with any implementation
        self._repository = repository

    def execute(self, file_path: str) -> List[VocabularyItem]:
        return self._repository.load_from_file(file_path)
```

## 3. Liskov Substitution Principle (LSP)

**"Objects of a superclass should be replaceable with objects of a subclass without breaking the application."**

### Repository Substitution

Any implementation of `IVocabularyRepository` can be used interchangeably:

```python
# In tests, use a mock repository
class MockVocabularyRepository(IVocabularyRepository):
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        return [VocabularyItem("test", "prueba")]

# In production, use file repository
class FileVocabularyRepository(IVocabularyRepository):
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        # Real file loading
        ...

# Use case works with both
use_case = LoadVocabularyUseCase(MockVocabularyRepository())  # Testing
use_case = LoadVocabularyUseCase(FileVocabularyRepository())  # Production
```

### Entity Contracts

The `VocabularyItem` entity enforces contracts:

```python
@dataclass(frozen=True)
class VocabularyItem:
    origin: str
    translation: str
    sound: Optional[str] = None
    image: Optional[str] = None

    def __post_init__(self):
        if not self.origin or not self.translation:
            raise ValueError("Origin and translation are required")
```

Any code using `VocabularyItem` can rely on:
- `origin` and `translation` are always non-empty
- Objects are immutable (frozen)
- Methods like `has_audio()` behave consistently

## 4. Interface Segregation Principle (ISP)

**"Clients should not be forced to depend on interfaces they don't use."**

### Before Refactoring

The old `StoreController` had mixed responsibilities:

```python
class StoreController:
    def load_store(self, app, data_path): ...  # Data loading
    def mark_positive(self, item): ...         # Profiling
    def mark_negative(self, item): ...         # Profiling
    def set_limit(self, limit): ...            # Configuration
    def shuffle_store(self): ...               # Business logic
    def get(self): ...                         # Data access
```

Clients using only data loading still had access to profiling methods.

### After Refactoring

Interfaces are focused and minimal:

**Vocabulary Repository** - Only data access:
```python
class IVocabularyRepository(ABC):
    @abstractmethod
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        pass

    @abstractmethod
    def save_to_file(self, file_path: str, items: List[VocabularyItem]) -> None:
        pass
```

**Settings Repository** - Only settings:
```python
class ISettingsRepository(ABC):
    @abstractmethod
    def load(self) -> UserSettings:
        pass

    @abstractmethod
    def save(self, settings: UserSettings) -> None:
        pass
```

**Resource Repository** - Only resources:
```python
class IResourceRepository(ABC):
    @abstractmethod
    def find_resource(self, path: str) -> Optional[str]:
        pass

    @abstractmethod
    def get_home_dir(self) -> str:
        pass
```

Each interface is minimal and focused. Clients only depend on what they need.

## 5. Dependency Inversion Principle (DIP)

**"High-level modules should not depend on low-level modules. Both should depend on abstractions."**

### Before Refactoring

Direct dependency on concrete implementation:

```python
class MainApp(App):
    def __init__(self):
        self.store_controller = StoreController()  # Direct dependency
        self.settings_config = IniConfigParser(home_dir)  # Direct dependency
```

Changes to `StoreController` or `IniConfigParser` force changes to `MainApp`.

### After Refactoring

**Domain layer defines abstractions:**

```python
# domain/repositories/vocabulary_repository.py
class IVocabularyRepository(ABC):  # Abstraction defined by domain
    @abstractmethod
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        pass
```

**Infrastructure implements abstractions:**

```python
# infrastructure/persistence/file_vocabulary_repository.py
class FileVocabularyRepository(IVocabularyRepository):  # Depends on abstraction
    def load_from_file(self, file_path: str) -> List[VocabularyItem]:
        # Implementation details
        ...
```

**Use cases depend on abstractions:**

```python
# domain/use_cases/vocabulary_use_cases.py
class LoadVocabularyUseCase:
    def __init__(self, repository: IVocabularyRepository):  # Depends on abstraction
        self._repository = repository
```

**Dependency Injection Container wires everything:**

```python
# infrastructure/di/container.py
class DependencyContainer:
    def vocabulary_repository(self) -> IVocabularyRepository:
        return FileVocabularyRepository()  # Injects concrete implementation

    def load_vocabulary_use_case(self) -> LoadVocabularyUseCase:
        return LoadVocabularyUseCase(self.vocabulary_repository())
```

### Dependency Flow

```
Before (violates DIP):
MainApp → StoreController → VocabularyProfiler
  ↓           ↓                    ↓
High      Medium                 Low
Level      Level                Level

After (follows DIP):
MainApp → Services → Use Cases → Repositories (interfaces)
                                       ↑
                                       |
                          Implementations (infrastructure)

All depend on abstractions!
```

## Summary

| Principle | Applied Through | Benefits |
|-----------|----------------|----------|
| **SRP** | Services with single responsibilities | Easier to maintain, test, and understand |
| **OCP** | Repository interfaces, Use cases | New features without modifying existing code |
| **LSP** | Interface contracts, Immutable entities | Substitutable implementations, predictable behavior |
| **ISP** | Focused repository interfaces | Clients only depend on what they use |
| **DIP** | Domain defines interfaces, Infrastructure implements | Flexible, testable, loosely coupled |

## Real-World Benefits

### 1. Easy Testing
```python
# Mock repository for testing
mock_repo = Mock(spec=IVocabularyRepository)
mock_repo.load_from_file.return_value = [test_item]
use_case = LoadVocabularyUseCase(mock_repo)  # Easy to test
```

### 2. Easy Extension
```python
# Add new storage without changing domain
class S3VocabularyRepository(IVocabularyRepository):
    def load_from_file(self, file_path: str):
        # Load from AWS S3
        ...
```

### 3. Easy Maintenance
- Change settings storage from INI to JSON? Only update `IniSettingsRepository`
- Add caching? Create a decorator around repository
- Switch UI framework? Domain and application layers remain unchanged

### 4. Clear Architecture
- New developers can understand responsibilities quickly
- Dependencies flow in one direction (toward abstractions)
- Business logic is isolated from framework details
