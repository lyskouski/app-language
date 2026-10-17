# Clean Architecture Refactoring

## Overview

This project has been refactored to follow **SOLID principles** and **Clean Architecture** patterns. The new architecture provides better separation of concerns, testability, and maintainability.

## Architecture Layers

### 1. Domain Layer (`src/domain/`)
**Enterprise Business Rules** - Framework-independent business logic.

#### Entities (`domain/entities/`)
- `VocabularyItem`: Immutable domain entity representing a vocabulary item
- `UserSettings`: Domain entity for user preferences

#### Repositories (Interfaces) (`domain/repositories/`)
- `IVocabularyRepository`: Interface for vocabulary data access
- `ISettingsRepository`: Interface for settings persistence
- `IResourceRepository`: Interface for resource management

#### Use Cases (`domain/use_cases/`)
- `LoadVocabularyUseCase`: Load vocabulary from data source
- `ShuffleVocabularyUseCase`: Shuffle vocabulary items
- `LoadSettingsUseCase`: Load user settings
- `UpdateLocaleUseCase`: Update interface locale
- `UpdateLanguagePairUseCase`: Update language learning pair

### 2. Application Layer (`src/application/`)
**Application Business Rules** - Orchestrates use cases and defines application services.

#### Services (`application/services/`)
- `VocabularyService`: Coordinates vocabulary-related operations
- `SettingsService`: Manages user settings
- `ResourceService`: Handles resource paths and directories
- `LocalizationService`: Manages translations

### 3. Infrastructure Layer (`src/infrastructure/`)
**Frameworks & Drivers** - Implementation details and external dependencies.

#### Persistence (`infrastructure/persistence/`)
- `FileVocabularyRepository`: File-based vocabulary storage implementation
- `IniSettingsRepository`: INI file-based settings storage
- `KivyResourceRepository`: Kivy-based resource management

#### Dependency Injection (`infrastructure/di/`)
- `DependencyContainer`: Central composition root for dependency injection

### 4. Presentation Layer (`src/presentation/`)
**Interface Adapters** - UI and adapter patterns.

#### Adapters (`presentation/adapters/`)
- `StoreControllerAdapter`: Adapter for backward compatibility with existing UI components

## SOLID Principles Applied

### Single Responsibility Principle (SRP)
- Each class has one reason to change
- `VocabularyService` only handles vocabulary operations
- `SettingsService` only handles settings
- `ResourceService` only handles resources

### Open/Closed Principle (OCP)
- Classes are open for extension but closed for modification
- Repository interfaces allow new implementations without changing domain
- Use cases can be extended without modifying existing code

### Liskov Substitution Principle (LSP)
- Repository implementations can be substituted for their interfaces
- Any `IVocabularyRepository` implementation works with `LoadVocabularyUseCase`

### Interface Segregation Principle (ISP)
- Interfaces are focused and minimal
- Each repository interface defines only required operations
- Services expose only what clients need

### Dependency Inversion Principle (DIP)
- High-level modules (domain) don't depend on low-level modules (infrastructure)
- Both depend on abstractions (interfaces)
- Dependencies are injected through the `DependencyContainer`

## Benefits

### 1. Testability
- Domain logic is completely isolated from frameworks
- Use cases can be tested without Kivy or file system
- Repositories can be easily mocked for testing

### 2. Maintainability
- Clear separation of concerns
- Changes in one layer don't affect others
- Easy to understand and navigate

### 3. Flexibility
- Easy to swap implementations (e.g., file storage → database)
- Framework-agnostic business logic
- Can support multiple UIs (mobile, web, desktop)

### 4. Extensibility
- New features can be added without modifying existing code
- New use cases can be created by composing existing ones
- Repository implementations can be swapped

## Migration Guide

### For Existing Code

The refactoring maintains backward compatibility through adapters:

**Old way:**
```python
from controller.store_controller import StoreController

store_controller = StoreController()
store_controller.load_store(app, data_path)
```

**New way (via adapter):**
```python
# In MainApp.__init__
self._container = DependencyContainer(self.user_data_dir)
vocabulary_service = self._container.vocabulary_service(data_path)
self.store_controller = StoreControllerAdapter(vocabulary_service, resource_service)
```

The adapter pattern allows existing UI components to work without changes while new components can use the clean architecture services directly.

### For New Features

When adding new features:

1. **Define domain entities** in `domain/entities/`
2. **Create repository interface** in `domain/repositories/`
3. **Implement use cases** in `domain/use_cases/`
4. **Create application service** in `application/services/`
5. **Implement repository** in `infrastructure/persistence/`
6. **Wire dependencies** in `infrastructure/di/container.py`
7. **Use in UI** through dependency injection

## Example: Adding New Feature

Let's say we want to add a "Favorites" feature:

### 1. Domain Entity
```python
# domain/entities/favorite.py
@dataclass(frozen=True)
class Favorite:
    vocabulary_item_id: str
    created_at: datetime
```

### 2. Repository Interface
```python
# domain/repositories/favorites_repository.py
class IFavoritesRepository(ABC):
    @abstractmethod
    def add_favorite(self, item_id: str) -> None:
        pass

    @abstractmethod
    def get_favorites(self) -> List[Favorite]:
        pass
```

### 3. Use Case
```python
# domain/use_cases/favorites_use_cases.py
class AddFavoriteUseCase:
    def __init__(self, repository: IFavoritesRepository):
        self._repository = repository

    def execute(self, item_id: str) -> None:
        self._repository.add_favorite(item_id)
```

### 4. Service
```python
# application/services/favorites_service.py
class FavoritesService:
    def __init__(self, add_favorite_use_case: AddFavoriteUseCase):
        self._add_favorite_use_case = add_favorite_use_case

    def mark_as_favorite(self, item_id: str) -> None:
        self._add_favorite_use_case.execute(item_id)
```

### 5. Infrastructure
```python
# infrastructure/persistence/file_favorites_repository.py
class FileFavoritesRepository(IFavoritesRepository):
    def add_favorite(self, item_id: str) -> None:
        # Implementation using file storage
        pass
```

### 6. Wire in Container
```python
# infrastructure/di/container.py
def favorites_service(self) -> FavoritesService:
    return self._get_or_create(
        'favorites_service',
        lambda: FavoritesService(self.add_favorite_use_case())
    )
```

## Testing

### Unit Testing Domain Layer
```python
def test_vocabulary_item_creation():
    item = VocabularyItem("hello", "hola")
    assert item.origin == "hello"
    assert item.translation == "hola"
```

### Testing Use Cases with Mocks
```python
def test_load_vocabulary_use_case():
    mock_repo = Mock(spec=IVocabularyRepository)
    mock_repo.load_from_file.return_value = [VocabularyItem("test", "prueba")]

    use_case = LoadVocabularyUseCase(mock_repo)
    result = use_case.execute("test.txt")

    assert len(result) == 1
    assert result[0].origin == "test"
```

### Integration Testing
```python
def test_vocabulary_service_integration():
    container = DependencyContainer("/tmp/test")
    service = container.vocabulary_service()

    service.load_vocabulary("test_data.txt")
    study_set = service.prepare_study_set(10)

    assert len(study_set) <= 10
```

## Directory Structure

```
src/
├── domain/                 # Enterprise Business Rules
│   ├── entities/          # Domain models
│   ├── repositories/      # Repository interfaces
│   └── use_cases/         # Application business rules
├── application/           # Application Layer
│   └── services/         # Application services
├── infrastructure/        # Frameworks & Drivers
│   ├── persistence/      # Repository implementations
│   └── di/               # Dependency injection
├── presentation/          # Interface Adapters
│   └── adapters/         # Backward compatibility adapters
├── component/            # Kivy UI components (legacy)
├── controller/           # Controllers (legacy)
├── model/                # Models (legacy)
└── main.py               # Composition root
```

## Next Steps

1. Migrate remaining controllers to use Clean Architecture
2. Update UI components to use services directly
3. Add comprehensive unit tests for domain layer
4. Add integration tests for services
5. Gradually remove legacy code as components are migrated

## References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
