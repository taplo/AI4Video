# Codebase Structure

**Analysis Date:** 2026-08-05

## Directory Layout

```
AI4Video/
├── app/                    # Django application (main business logic)
│   ├── analysis/           # Video analysis pipeline and AI/ML engines
│   ├── recording/          # 24/7 video recording management
│   ├── services/           # Business services (alarm, algorithm testing)
│   ├── utils/              # Utility classes and global configuration
│   └── views/              # HTTP request handlers (view functions)
├── framework/              # Django project configuration
├── static/                 # Static assets (CSS, JS, images, fonts)
├── templates/              # Django HTML templates
├── zlm/                    # ZLMediaKit media server binaries
├── config.json             # Runtime configuration
├── settings.json           # Application settings
├── manage.py               # Django management script
├── ai4video.sqlite3         # SQLite database file
├── language-*.json         # Multi-language translation files
└── requirements-*.txt      # Python dependencies
```

## Directory Purposes

**`app/`:**
- Purpose: Main Django application containing all business logic
- Contains: Views, models, services, utilities, analysis pipeline
- Key files: `models.py`, `urls.py`, `middleware.py`, `context_processors.py`

**`app/analysis/`:**
- Purpose: Video analysis pipeline and AI/ML inference
- Contains: Pipeline orchestration, frame processing, detection engines
- Key files: `manager.py`, `pipeline.py`, `detector.py`, `tracker.py`

**`app/analysis/engines/`:**
- Purpose: AI/ML inference engine implementations
- Contains: YOLO, ONNX, OpenVINO engine adapters
- Key files: `base.py`, `factory.py`, `onnx_engine.py`, `pytorch_engine.py`

**`app/recording/`:**
- Purpose: 24/7 video recording and playback
- Contains: Recording manager, segment indexing
- Key files: `manager.py`

**`app/services/`:**
- Purpose: Business logic services
- Contains: Alarm service, algorithm testing, cross-camera tracking
- Key files: `alarm_service.py`, `algorithm_test_service.py`, `cross_camera_service.py`

**`app/utils/`:**
- Purpose: Utility classes and global configuration
- Contains: Database, logging, configuration, external integrations
- Key files: `GlobalUtils.py`, `Config.py`, `Database.py`, `ZLMediaKitApi.py`

**`app/views/`:**
- Purpose: HTTP request handlers (view functions)
- Contains: One file per feature module
- Key files: `StreamView.py`, `AnalysisView.py`, `AlgorithmView.py`

**`framework/`:**
- Purpose: Django project configuration
- Contains: Settings, URL routing, WSGI/ASGI configuration
- Key files: `settings.py`, `urls.py`

**`static/`:**
- Purpose: Static assets served by Django
- Contains: CSS, JavaScript, images, fonts, uploaded files
- Key files: `lib/`, `resource/`, `upload/`

**`templates/app/`:**
- Purpose: Django HTML templates for web interface
- Contains: One directory per feature module
- Key files: `base.html`, `index.html`, `stream/`, `analysis/`

**`zlm/`:**
- Purpose: ZLMediaKit media server binaries and configuration
- Contains: Platform-specific binaries, configuration files
- Key files: `bin.x86.windows10/`, `config.ini`

## Key File Locations

**Entry Points:**
- `manage.py`: Django management script (runserver, migrations, etc.)
- `app/urls.py`: URL routing configuration
- `app/views/IndexView.py`: Main dashboard view

**Configuration:**
- `framework/settings.py`: Django project settings
- `config.json`: Runtime configuration (ports, paths, features)
- `settings.json`: Application settings

**Core Logic:**
- `app/utils/GlobalUtils.py`: Global singletons and utilities
- `app/analysis/manager.py`: Video analysis orchestration
- `app/analysis/pipeline.py`: Per-camera analysis pipeline
- `app/utils/GB28181SipServer.py`: GB28181 protocol implementation

**Data Models:**
- `app/models.py`: Django ORM models (Stream, Algorithm, Zone, Alarm, etc.)

**Testing:**
- `app/tests.py`: Unit tests (currently minimal)

## Naming Conventions

**Files:**
- View files: `{Feature}View.py` (e.g., `StreamView.py`, `AnalysisView.py`)
- Utility files: `{Feature}.py` (e.g., `Config.py`, `Database.py`)
- Analysis files: Lowercase with underscores (e.g., `pipeline.py`, `detector.py`)
- Template files: Lowercase HTML (e.g., `index.html`, `online.html`)

**Directories:**
- Feature modules: Lowercase (e.g., `analysis/`, `recording/`)
- View files: PascalCase (e.g., `views/`)
- Templates: Lowercase (e.g., `templates/app/stream/`)

**Functions:**
- View functions: `api_open{Action}` for API endpoints
- Utility functions: `f_{Action}` prefix (e.g., `f_parseGetParams`)
- Private methods: `_` prefix (e.g., `_resolve_path`)

**Variables:**
- Global singletons: `g_` prefix (e.g., `g_config`, `g_zlm`)
- Constants: UPPER_SNAKE_CASE (e.g., `AUTH_WHITELIST_PREFIXES`)
- Instance variables: `_` prefix for private (e.g., `self._loaded`)

## Where to Add New Code

**New Feature Module:**
- Views: Create `app/views/{Feature}View.py`
- URLs: Add patterns to `app/urls.py`
- Templates: Create `templates/app/{feature}/`
- Models: Add to `app/models.py` if needed

**New API Endpoint:**
- View function: Add to appropriate `app/views/{Feature}View.py`
- URL pattern: Add to `app/urls.py`
- Template: Create HTML template if needed

**New AI/ML Engine:**
- Engine class: Create `app/analysis/engines/{engine}_engine.py`
- Factory: Update `app/analysis/engines/factory.py`
- Base class: Inherit from `app/analysis/engines/base.py:BaseEngine`

**New Utility Function:**
- Global utilities: Add to `app/utils/GlobalUtils.py`
- Feature-specific: Create `app/utils/{Feature}.py`

**New Business Service:**
- Service class: Create `app/services/{service}_service.py`
- Integration: Import in views or analysis pipeline

## Special Directories

**`static/upload/`:**
- Purpose: User-uploaded files (model weights, audio, etc.)
- Generated: Yes (at runtime)
- Committed: No (in .gitignore)

**`static/storage/`:**
- Purpose: Application-generated storage (alarms, snapshots, recordings)
- Generated: Yes (at runtime)
- Committed: No (in .gitignore)

**`log/`:**
- Purpose: Application log files
- Generated: Yes (at runtime)
- Committed: No (in .gitignore)

**`zlm/`:**
- Purpose: ZLMediaKit media server binaries
- Generated: No (pre-built binaries)
- Committed: Yes (platform-specific binaries)

---

*Structure analysis: 2026-08-05*
