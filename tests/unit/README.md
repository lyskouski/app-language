# Unit Tests - Clean Architecture Organization

This directory contains unit tests organized by architectural layer, following Clean Architecture principles.

## Test Structure

### test_domain.py
Tests for the **Domain Layer** (core business logic):
- **Entities**: VocabularyItem, UserSettings
- **Use Cases**: LoadVocabularyUseCase, ShuffleVocabularyUseCase

Domain tests are pure unit tests with no external dependencies. They test the core business rules and entities.

### test_application.py
Tests for the **Application Layer** (orchestration):
- **Application Services**: VocabularyService, MediaService, RecorderService

Application tests verify that services correctly orchestrate domain use cases and coordinate business workflows.

### test_infrastructure.py
Tests for the **Infrastructure Layer** (implementations):
- **Persistence**: FileVocabularyRepository
- **Machine Learning**: MLVocabularyProfiler
- **Audio**: LibrosaAudioComparator
- **Dependency Injection**: DependencyContainer

Infrastructure tests verify concrete implementations of interfaces, external integrations, and framework-specific code.

## Running Tests

```bash
# Run all tests
pytest tests/unit/

# Run specific layer
pytest tests/unit/test_domain.py
pytest tests/unit/test_application.py
pytest tests/unit/test_infrastructure.py

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=term-missing
```

## Test Principles

1. **Independence**: Each layer's tests can run independently
2. **Clarity**: Test organization mirrors the source code architecture
3. **Maintainability**: Easy to locate tests for specific components
4. **SOLID**: Tests follow the same architectural principles as the code

## Migration Notes

Previous test files reorganized on April 20, 2026:
- `test_clean_architecture.py` → Split into `test_domain.py` and `test_application.py`
- `test_migrated_services.py` → Moved to `test_infrastructure.py`

This reorganization better reflects the Clean Architecture layering and makes it clearer which architectural layer each test targets.
