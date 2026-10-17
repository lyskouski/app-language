# Clean Architecture Diagram

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
│                     (Frameworks & Drivers)                       │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  Kivy Screens  │  │  Kivy Widgets  │  │    Adapters      │  │
│  │   (UI Views)   │  │  (Components)  │  │ (Compatibility)  │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│                (Application Business Rules)                      │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐  │
│  │  Vocabulary  │  │    Settings     │  │    Resource      │  │
│  │   Service    │  │    Service      │  │    Service       │  │
│  └──────────────┘  └─────────────────┘  └──────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Localization Service                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                             │
│                 (Enterprise Business Rules)                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      USE CASES                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐│ │
│  │  │Load Vocabulary│  │Load Settings │  │Update Locale     ││ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘│ │
│  │  ┌──────────────┐  ┌──────────────┐                      │ │
│  │  │Shuffle       │  │Update Lang   │                      │ │
│  │  │Vocabulary    │  │Pair          │                      │ │
│  │  └──────────────┘  └──────────────┘                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      ENTITIES                              │ │
│  │  ┌──────────────────┐         ┌──────────────────┐        │ │
│  │  │ VocabularyItem   │         │  UserSettings    │        │ │
│  │  │  - origin        │         │  - locale        │        │ │
│  │  │  - translation   │         │  - locale_from   │        │ │
│  │  │  - sound         │         │  - locale_to     │        │ │
│  │  │  - image         │         └──────────────────┘        │ │
│  │  └──────────────────┘                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               REPOSITORY INTERFACES                        │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────┐ │ │
│  │  │IVocabularyRepo   │  │ISettingsRepo     │  │IResource││ │
│  │  │  - load_from_file│  │  - load()        │  │Repo     ││ │
│  │  │  - save_to_file  │  │  - save()        │  └─────────┘│ │
│  │  └──────────────────┘  └──────────────────┘              │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↑ (implements)
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
│                  (Frameworks & Drivers)                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              REPOSITORY IMPLEMENTATIONS                    │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────┐ │ │
│  │  │FileVocabulary    │  │IniSettings       │  │Kivy     ││ │
│  │  │Repository        │  │Repository        │  │Resource ││ │
│  │  └──────────────────┘  └──────────────────┘  │Repo     ││ │
│  │                                               └─────────┘│ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │          DEPENDENCY INJECTION CONTAINER                    │ │
│  │  - Creates and wires all dependencies                     │ │
│  │  - Manages singleton instances                            │ │
│  │  - Composition root                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Dependency Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPENDENCY RULE                               │
│                                                                  │
│  Dependencies point INWARD (toward the domain)                  │
│                                                                  │
│  Outer layers CAN depend on inner layers                        │
│  Inner layers CANNOT depend on outer layers                     │
│                                                                  │
│  Infrastructure → Application → Domain                          │
│  Presentation   → Application → Domain                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: Loading Vocabulary

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│   UI     │─calls──→│  Service │─calls──→│ Use Case │─calls──→│Repository│
│ (Screen) │         │          │         │          │         │Interface │
└──────────┘         └──────────┘         └──────────┘         └─────↑────┘
                                                                      │
                                                                implements
                                                                      │
                                                              ┌───────┴──────┐
                                                              │ File         │
                                                              │ Repository   │
                                                              └──────────────┘
     ┌──────────────────────────────────────────────────────────────────────┐
     │ 1. Screen calls vocabulary_service.load_vocabulary(path)             │
     │ 2. Service delegates to LoadVocabularyUseCase.execute(path)         │
     │ 3. Use case calls repository.load_from_file(path)                   │
     │ 4. Repository loads from file system                                │
     │ 5. Returns List[VocabularyItem] back up the chain                   │
     └──────────────────────────────────────────────────────────────────────┘
```

## Component Interaction

```
MainApp (Entry Point)
  │
  ├─→ Creates DependencyContainer
  │     │
  │     ├─→ Creates Repositories
  │     ├─→ Creates Use Cases (with injected repositories)
  │     ├─→ Creates Services (with injected use cases)
  │     └─→ Returns services to MainApp
  │
  ├─→ Uses Services for business operations
  │     ├─→ VocabularyService
  │     ├─→ SettingsService
  │     ├─→ ResourceService
  │     └─→ LocalizationService
  │
  └─→ Passes services/container to Screens
        └─→ Screens use services (not controllers)
```

## SOLID Principles Visualization

```
┌──────────────────────────────────────────────────────────────────┐
│ S - Single Responsibility                                        │
│ ─────────────────────────────────────────────────────────────────│
│   Each service has ONE reason to change:                         │
│   - VocabularyService: vocabulary operations only               │
│   - SettingsService: settings operations only                   │
│   - ResourceService: resource operations only                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ O - Open/Closed                                                  │
│ ─────────────────────────────────────────────────────────────────│
│   Can add new repository implementations without changing domain: │
│   IVocabularyRepository ← FileVocabularyRepository              │
│                        ← DatabaseVocabularyRepository (new)     │
│                        ← ApiVocabularyRepository (new)          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ L - Liskov Substitution                                          │
│ ─────────────────────────────────────────────────────────────────│
│   Any IVocabularyRepository can be used interchangeably:        │
│   LoadVocabularyUseCase(FileVocabularyRepository())            │
│   LoadVocabularyUseCase(MockVocabularyRepository())            │
│   LoadVocabularyUseCase(DatabaseVocabularyRepository())        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ I - Interface Segregation                                        │
│ ─────────────────────────────────────────────────────────────────│
│   Focused interfaces - clients only see what they need:          │
│   IVocabularyRepository: load/save vocabulary only              │
│   ISettingsRepository: load/save settings only                  │
│   IResourceRepository: resource paths only                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ D - Dependency Inversion                                         │
│ ─────────────────────────────────────────────────────────────────│
│   Domain defines interfaces, Infrastructure implements:          │
│                                                                  │
│   Domain Layer:           Infrastructure Layer:                  │
│   IVocabularyRepository ← FileVocabularyRepository              │
│   (interface)             (implementation)                      │
│                                                                  │
│   Use cases depend on interfaces, not implementations           │
└──────────────────────────────────────────────────────────────────┘
```

## Testing Strategy

```
┌──────────────────────────────────────────────────────────────────┐
│                        TESTING PYRAMID                           │
│                                                                  │
│                           ╱ ╲                                    │
│                          ╱   ╲         E2E Tests                │
│                         ╱     ╲        (Few)                    │
│                        ╱───────╲                                │
│                       ╱         ╲      Integration Tests        │
│                      ╱           ╲     (Some)                   │
│                     ╱─────────────╲                             │
│                    ╱               ╲   Unit Tests                │
│                   ╱                 ╲  (Many)                    │
│                  ╱───────────────────╲                           │
│                                                                  │
│  Unit Tests:         Test domain entities, use cases            │
│                      Fast, isolated, no dependencies            │
│                                                                  │
│  Integration Tests:  Test services with real repositories       │
│                      Test repository implementations            │
│                                                                  │
│  E2E Tests:          Test complete user workflows               │
│                      UI → Services → Repositories               │
└──────────────────────────────────────────────────────────────────┘
```

## File Organization

```
src/
├── domain/                          # Inner layer
│   ├── entities/                   # Business objects
│   │   ├── vocabulary_item.py     # ← Immutable, pure
│   │   └── user_settings.py       # ← No framework deps
│   ├── repositories/               # Interfaces only
│   │   ├── vocabulary_repository.py
│   │   ├── settings_repository.py
│   │   └── resource_repository.py
│   └── use_cases/                  # Business rules
│       ├── vocabulary_use_cases.py
│       └── settings_use_cases.py
│
├── application/                     # Middle layer
│   └── services/                   # Orchestration
│       ├── vocabulary_service.py
│       ├── settings_service.py
│       ├── resource_service.py
│       └── localization_service.py
│
├── infrastructure/                  # Outer layer
│   ├── persistence/                # Implementations
│   │   ├── file_vocabulary_repository.py
│   │   ├── ini_settings_repository.py
│   │   └── kivy_resource_repository.py
│   └── di/                         # Wiring
│       └── container.py            # ← Composition root
│
├── presentation/                    # Outer layer
│   └── adapters/                   # UI adapters
│       └── store_controller_adapter.py
│
└── main.py                         # ← Entry point
```

## Key Concepts

### Inversion of Control (IoC)
```
Traditional:
Component → Creates → Dependency

Clean Architecture:
Component ← Receives ← Dependency (from container)
```

### Dependency Injection
```
Without DI:
class Service:
    def __init__(self):
        self.repo = FileRepository()  # Hard-coded dependency

With DI:
class Service:
    def __init__(self, repo: IRepository):  # Injected dependency
        self.repo = repo
```

### Boundaries
```
Domain ─── Does NOT import ───> Infrastructure
Domain ─── Defines interfaces ──> IRepository
Infrastructure ─── Implements ──> FileRepository: IRepository
```
