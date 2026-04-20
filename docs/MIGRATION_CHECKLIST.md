# Migration Checklist

## Completed ✅

### Core Architecture
- [x] Created domain layer structure
  - [x] Domain entities (`VocabularyItem`, `UserSettings`)
  - [x] Repository interfaces
  - [x] Use cases
  - [x] Domain services (`IVocabularyProfiler`, `IAudioComparator`)
- [x] Created application layer
  - [x] `VocabularyService`
  - [x] `SettingsService`
  - [x] `ResourceService`
  - [x] `LocalizationService`
  - [x] `MediaService`
  - [x] `RecorderService`
- [x] Created infrastructure layer
  - [x] Repository implementations
  - [x] Dependency injection container
  - [x] ML vocabulary profiler implementation
  - [x] Audio comparator implementation
- [x] Created presentation layer
  - [x] `StoreControllerAdapter` for backward compatibility
- [x] Refactored `MainApp` to use dependency injection
- [x] Documentation
  - [x] Clean Architecture guide
  - [x] SOLID principles explanation

### Controllers Migration
- [x] Migrated `vocabulary_profiler.py` to domain service
- [x] Migrated `audio_comparator.py` to infrastructure service
- [x] Migrated `media_controller.py` to application service
- [x] Migrated `recorder_controller.py` to application service
- [x] Updated `recorder_controller_desktop.py` to implement IRecorderController
- [x] Updated `recorder_controller_android.py` to implement IRecorderController
- [x] Updated `recorder_controller_ios.py` to implement IRecorderController

### Components Migration
- [x] Updated `main_screen.py` to use services directly
- [x] Updated `language_screen.py` to use services directly
- [x] Updated `structure_screen.py` to use services directly
- [x] Updated `store_update_screen.py` to use services directly
- [x] Updated `phonetics_widget.py` to use services directly
- [x] Updated `recorder_widget.py` to use services directly
- [x] `articulation_screen.py` - Simple screen, no migration needed
- [x] `card_screen.py`, `dictionary_screen.py` (already simple, no migration needed)

### Testing
- [x] Created comprehensive test suite for migrated services
- [x] Unit tests for ML vocabulary profiler
- [x] Unit tests for audio comparator
- [x] Unit tests for media service
- [x] Unit tests for recorder service
- [x] Integration tests for dependency injection container
- [x] Test coverage reporting (41 tests passing)

## In Progress 🚧

### Optional Enhancements
- [ ] Implement caching layer for resources
- [ ] Add error handling strategies
- [ ] Add logging service
- [ ] Add analytics service
- [ ] Performance profiling and optimization
- [ ] Set up continuous integration

## Pending ⏳

None - All migration work complete! ✅

### Cleanup
- [x] Legacy controllers properly wrapped with interfaces
- [x] Remove `StoreControllerAdapter` once all components verified
- [x] Removed all legacy controllers from `controller/_legacy/` directory:
  - [x] `audio_comparator.py` ❌ DELETED (replaced by `LibrosaAudioComparator`)
  - [x] `media_controller.py` ❌ DELETED (replaced by `MediaService`)
  - [x] `recorder_controller.py` ❌ DELETED (replaced by `RecorderService`)
  - [x] `store_controller.py` ❌ DELETED (replaced by `VocabularyService`)
  - [x] `vocabulary_profiler.py` ❌ DELETED (replaced by `MLVocabularyProfiler`)
  - [x] `store_controller_adapter.py` ❌ DELETED (no longer needed)
  - [x] Kept `README.md` for historical documentation
- [x] Platform-specific implementations remain active in `controller/`:
  - [x] `recorder_controller_desktop.py` ✅ ACTIVE - Implements `IRecorderController`
  - [x] `recorder_controller_android.py` ✅ ACTIVE - Implements `IRecorderController`
  - [x] `recorder_controller_ios.py` ✅ ACTIVE - Implements `IRecorderController`
- [x] All imports in migrated files are necessary and used
- [x] Code cleanup complete - zero legacy code remaining

## Migration Strategy

### Phase 1: Foundation ✅ (COMPLETED)
1. ✅ Set up Clean Architecture layers
2. ✅ Create core domain entities and repositories
3. ✅ Implement dependency injection
4. ✅ Create backward compatibility adapters
5. ✅ Update main application entry point

### Phase 2: Services & Controllers ✅ (COMPLETED)
1. ✅ Migrate vocabulary profiler to ML service
2. ✅ Migrate audio comparator to infrastructure
3. ✅ Migrate media controller to application service
4. ✅ Migrate recorder controllers with interface implementation
5. ✅ Update DI container with all new services

### Phase 3: Testing ✅ (COMPLETED)
1. ✅ Write unit tests for domain layer
2. ✅ Write unit tests for migrated services
3. ✅ Write integration tests for DI container
4. ✅ Add test coverage reporting (38 tests passing)
5. 🚧 Set up continuous integration

### Phase 4: Component Migration ✅ (COMPLETED)
1. ✅ Update main navigation screens
2. ✅ Update simple component screens
3. ✅ Identify and update complex components
4. ✅ Test each component thoroughly after migration
5. ✅ Remove adapter dependencies

### Phase 5: Cleanup & Optimization ✅ (COMPLETED - Core Tasks)
1. ✅ Remove adapter layer
2. ✅ Archive legacy code to _legacy directory
3. 🚧 Optimize dependency injection (optional)
4. 🚧 Add caching where appropriate (optional)
5. 🚧 Performance profiling and optimization (optional)

## How to Migrate a Component

### Example: Migrating a Screen Component

**Before:**
```python
from controller.store_controller import StoreController

class MyScreen(Screen):
    def __init__(self):
        self.store_controller = StoreController()

    def load_data(self):
        self.store_controller.load_store(app, path)
```

**After:**
```python
from kivy.app import App

class MyScreen(Screen):
    def __init__(self):
        # Get services from app's DI container
        app = App.get_running_app()
        self._vocabulary_service = app._container.vocabulary_service()

    def load_data(self):
        self._vocabulary_service.load_vocabulary(path)
```

### Example: Migrating a Controller

**Before:**
```python
# controller/my_controller.py
class MyController:
    def __init__(self):
        self.config = IniConfigParser(path)

    def do_something(self):
        # Mixed business logic and infrastructure
        value = self.config.get('key')
        # ... process value
```

**After:**

1. **Extract domain logic to use case:**
```python
# domain/use_cases/my_use_cases.py
class DoSomethingUseCase:
    def __init__(self, repository: IMyRepository):
        self._repository = repository

    def execute(self) -> Result:
        value = self._repository.get_value('key')
        # Pure business logic here
        return processed_value
```

2. **Create application service:**
```python
# application/services/my_service.py
class MyService:
    def __init__(self, use_case: DoSomethingUseCase):
        self._use_case = use_case

    def do_something(self) -> Result:
        return self._use_case.execute()
```

3. **Wire in DI container:**
```python
# infrastructure/di/container.py
def my_service(self) -> MyService:
    return self._get_or_create(
        'my_service',
        lambda: MyService(self.do_something_use_case())
    )
```

## Testing Guidelines

### Domain Layer Tests (Pure Unit Tests)
```python
def test_vocabulary_item_requires_origin_and_translation():
    with pytest.raises(ValueError):
        VocabularyItem("", "translation")
```

### Use Case Tests (with Mocks)
```python
def test_load_vocabulary_use_case(mock_repository):
    mock_repository.load_from_file.return_value = [test_item]
    use_case = LoadVocabularyUseCase(mock_repository)

    result = use_case.execute("test.txt")

    assert len(result) == 1
    mock_repository.load_from_file.assert_called_once()
```

### Service Tests (Integration Tests)
```python
def test_vocabulary_service_integration(tmp_path):
    container = DependencyContainer(str(tmp_path))
    service = container.vocabulary_service()

    # Create test data file
    test_file = tmp_path / "vocab.txt"
    test_file.write_text("hello;hola")

    service.load_vocabulary(str(test_file))
    study_set = service.prepare_study_set(10)

    assert len(study_set) == 1
```

## Common Pitfalls to Avoid

1. **Don't leak domain logic to infrastructure**
   - ❌ Bad: Business rules in repository implementations
   - ✅ Good: Business rules in use cases, repositories only handle data

2. **Don't create circular dependencies**
   - ❌ Bad: Domain importing from infrastructure
   - ✅ Good: Dependencies flow inward (infrastructure → application → domain)

3. **Don't skip the adapter layer during migration**
   - ❌ Bad: Breaking existing UI immediately
   - ✅ Good: Use adapters to maintain backward compatibility

4. **Don't couple use cases together**
   - ❌ Bad: One use case directly calling another
   - ✅ Good: Application services orchestrate multiple use cases

5. **Don't put framework code in domain**
   - ❌ Bad: Kivy properties in domain entities
   - ✅ Good: Pure Python dataclasses in domain

## Verification Checklist

After migrating a component, verify:

- [ ] No direct instantiation of concrete classes (use DI)
- [ ] No framework imports in domain layer
- [ ] Tests pass without requiring UI framework
- [ ] Business logic is in use cases, not in repositories
- [ ] Services coordinate use cases, don't contain business logic
- [ ] Dependencies point inward (toward domain)
- [ ] Code is more testable than before
- [ ] Single Responsibility Principle is followed

## Resources

- [docs/CLEAN_ARCHITECTURE.md](CLEAN_ARCHITECTURE.md) - Architecture overview
- [docs/SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md) - SOLID principles explained
- [src/domain/](../src/domain/) - Domain layer examples
- [src/application/](../src/application/) - Application layer examples
- [src/infrastructure/](../src/infrastructure/) - Infrastructure layer examples

## Questions?

If you have questions about the migration:
1. Check the documentation files
2. Look at existing migrated code as examples
3. Follow the dependency injection pattern
4. Keep business logic in the domain layer
