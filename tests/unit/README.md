# Unit Tests - Clean Architecture Organization

This directory contains unit tests organized with descriptive names that indicate the source module being tested, following Clean Architecture principles.

## Test Structure

Tests are organized with flat file structure but descriptive names that mirror the source code hierarchy:

### Domain Layer Tests
**Entities:**
- `test_domain_entities_vocabulary_item.py` → `src/domain/entities/vocabulary_item.py`
- `test_domain_entities_user_settings.py` → `src/domain/entities/user_settings.py`

**Use Cases:**
- `test_domain_use_cases_vocabulary.py` → `src/domain/use_cases/vocabulary_use_cases.py`
- `test_domain_use_cases_settings.py` → `src/domain/use_cases/settings_use_cases.py`

### Application Layer Tests
**Services:**
- `test_application_vocabulary_service.py` → `src/application/services/vocabulary_service.py`
- `test_application_media_service.py` → `src/application/services/media_service.py`
- `test_application_recorder_service.py` → `src/application/services/recorder_service.py`
- `test_application_settings_service.py` → `src/application/services/settings_service.py`
- `test_application_resource_service.py` → `src/application/services/resource_service.py`

### Infrastructure Layer Tests
**Persistence:**
- `test_infrastructure_vocabulary_repository.py` → `src/infrastructure/persistence/file_vocabulary_repository.py`
- `test_infrastructure_settings_repository.py` → `src/infrastructure/persistence/ini_settings_repository.py`

**Machine Learning:**
- `test_infrastructure_ml_profiler.py` → `src/infrastructure/ml/ml_vocabulary_profiler.py`

**Audio:**
- `test_infrastructure_audio_comparator.py` → `src/infrastructure/audio/librosa_audio_comparator.py`

**Dependency Injection:**
- `test_infrastructure_di_container.py` → `src/infrastructure/di/container.py`

### Localization Tests
- `test_l18n_labels.py` → `src/l18n/labels.py` (label validation and consistency tests)

## Running Tests

```bash
# Run all tests
pytest tests/unit/

# Run specific layer
pytest tests/unit/ -k "test_domain"
pytest tests/unit/ -k "test_application"
pytest tests/unit/ -k "test_infrastructure"
pytest tests/unit/ -k "test_l18n"

# Run specific module tests
pytest tests/unit/test_domain_entities_vocabulary_item.py
pytest tests/unit/test_application_vocabulary_service.py
pytest tests/unit/test_infrastructure_vocabulary_repository.py
pytest tests/unit/test_l18n_labels.py

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=term-missing
```

## Test Organization Benefits

1. **Easy Navigation**: Descriptive filenames make it obvious which source module is being tested
2. **No Import Issues**: Flat structure works reliably with pytest's import system
3. **Clear Naming**: File names follow pattern `test_{layer}_{module_path}.py`
4. **Maintainability**: When source code changes, test file name clearly indicates which test to update
5. **Discoverability**: grep/search by layer name quickly finds all relevant tests

## Test Principles

1. **Independence**: Each test file can run independently
2. **Clarity**: Test filenames clearly indicate the source module being tested
3. **Maintainability**: Easy to locate tests for specific source files
4. **SOLID**: Tests follow the same architectural principles as the code

## Finding Tests for Source Files

To find tests for a source file, use the naming pattern:
- Replace `src/` with `tests/unit/test_`
- Replace `/` with `_`
- Remove `.py` extension, add to the test prefix

Examples:
- `src/domain/entities/vocabulary_item.py` → `tests/unit/test_domain_entities_vocabulary_item.py`
- `src/application/services/vocabulary_service.py` → `tests/unit/test_application_vocabulary_service.py`
- `src/infrastructure/persistence/file_vocabulary_repository.py` → `tests/unit/test_infrastructure_vocabulary_repository.py`
- `src/l18n/labels.py` → `tests/unit/test_l18n_labels.py`

## Migration Notes

**April 20, 2026 - Test Reorganization:**
- **Initial**: Monolithic files by layer (test_domain.py, test_application.py, test_infrastructure.py) plus l18n subfolder
- **Attempted**: Nested directory structure mirroring src/ (domain/entities/, application/services/, etc.)
  - *Issue*: Pytest import system had difficulties with nested test structure due to namespace collisions with src/ packages
- **Final**: Fully flat structure with descriptive naming convention (all tests at tests/unit/ level)

The flat structure with descriptive names provides the best balance of:
- Clear organization and discoverability
- Reliable pytest imports
- Easy-to-understand mapping to source files
- Maintainability and searchability
