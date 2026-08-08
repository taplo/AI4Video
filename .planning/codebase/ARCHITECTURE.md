# Architecture

**Analysis Date:** 2026-08-05

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                      Web Interface                         │
│  Templates: templates/app/  |  Static: static/             │
├──────────────────┬──────────────────┬───────────────────────┤
│   User Views     │   Stream Views   │    Analysis Views     │
│  `app/views/`    │  `app/views/`    │   `app/views/`        │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  GlobalUtils  |  AnalysisManager  |  RecordingManager       │
│  `app/utils/` |  `app/analysis/`  |  `app/recording/`      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  External Services                                          │
│  ZLMediaKit  |  GB28181 SIP  |  AI/ML Engines              │
│  `app/utils/`|  `app/utils/` |  `app/analysis/engines/`    │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Data Layer                                                 │
│  SQLite (ai4video.sqlite3)  |  Django ORM                    │
│  `app/models.py`  |  `app/utils/Database.py`                │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Django Framework | Web framework, routing, middleware | `framework/` |
| App Views | HTTP request handlers, API endpoints | `app/views/` |
| Analysis Manager | Video analysis orchestration | `app/analysis/manager.py` |
| Camera Pipeline | Per-camera analysis pipeline | `app/analysis/pipeline.py` |
| AI/ML Engines | Object detection (YOLO, ONNX, OpenVINO) | `app/analysis/engines/` |
| GB28181 SIP Server | Chinese national standard video protocol | `app/utils/GB28181SipServer.py` |
| ZLMediaKit API | Media server integration | `app/utils/ZLMediaKitApi.py` |
| Database | SQLite operations with thread safety | `app/utils/Database.py` |
| Config | Runtime configuration management | `app/utils/Config.py` |
| Recording Manager | 24/7 video recording | `app/recording/manager.py` |
| Middleware | Authentication, session management | `app/middleware.py` |

## Pattern Overview

**Overall:** Django MVT (Model-View-Template) with custom service layer

**Key Characteristics:**
- Function-based views (not class-based views)
- Custom global singletons for configuration, logging, and services
- Thread-safe database operations with global lock
- Multiprocessing for video analysis pipelines
- Event-driven architecture for alarm generation
- Multi-language support via JSON translation files

## Layers

**Presentation Layer:**
- Purpose: User interface rendering and API responses
- Location: `templates/app/`, `static/`, `app/views/`
- Contains: HTML templates, CSS/JS assets, view functions
- Depends on: Service layer, Django template engine
- Used by: Web browsers, API clients

**View Layer:**
- Purpose: HTTP request handling, authentication, parameter parsing
- Location: `app/views/`
- Contains: View functions for each feature module
- Depends on: Service layer, models, utilities
- Used by: Django URL router

**Service Layer:**
- Purpose: Business logic orchestration, cross-cutting concerns
- Location: `app/utils/GlobalUtils.py`, `app/analysis/manager.py`, `app/recording/manager.py`
- Contains: Global utilities, analysis orchestration, recording management
- Depends on: Models, external integrations
- Used by: Views, background processes

**Data Layer:**
- Purpose: Data persistence and retrieval
- Location: `app/models.py`, `app/utils/Database.py`
- Contains: Django ORM models, raw SQL operations
- Depends on: SQLite database
- Used by: Service layer, views

**External Integration Layer:**
- Purpose: Communication with external services and protocols
- Location: `app/utils/ZLMediaKitApi.py`, `app/utils/GB28181SipServer.py`, `app/analysis/engines/`
- Contains: API clients, protocol implementations, AI/ML engines
- Depends on: External services, libraries
- Used by: Service layer

## Data Flow

### Primary Request Path

1. HTTP Request → Django Middleware (`app/middleware.py`)
2. URL Routing → View Function (`app/urls.py` → `app/views/`)
3. Authentication Check → Session Validation
4. Parameter Parsing → `f_parseGetParams()` or `f_parsePostParams()`
5. Business Logic → Service Layer (`app/utils/GlobalUtils.py`)
6. Data Access → Models (`app/models.py`) or Raw SQL (`app/utils/Database.py`)
7. JSON Response → `f_responseJson()`

### Video Analysis Flow

1. Stream Registration → `StreamModel` in database
2. Stream Proxy Creation → ZLMediaKit API (`app/utils/ZLMediaKitApi.py`)
3. Frame Capture → `FrameSource` (`app/analysis/frames.py`)
4. Motion Detection → `MotionDetector` (`app/analysis/motion.py`)
5. Object Detection → AI/ML Engines (`app/analysis/engines/`)
6. Object Tracking → `IoUTracker` (`app/analysis/tracker.py`)
7. Zone Analysis → Business Rules (`app/analysis/biz_rules.py`)
8. Alarm Generation → `AlarmModel` in database
9. Event Bridge → External notification system

### GB28181 Registration Flow

1. SIP Registration → `GB28181SipServer` (`app/utils/GB28181SipServer.py`)
2. Device Discovery → Camera device list
3. Stream Invitation → RTSP/RTP stream setup
4. Media Relay → ZLMediaKit integration
5. Stream Monitoring → Heartbeat management

**State Management:**
- Session-based user authentication (`request.session`)
- Global configuration singleton (`g_config`)
- Thread-safe database operations (`g_dbLock`)
- Process-safe analysis state (`AnalysisManager` singleton)

## Key Abstractions

**Stream Model:**
- Purpose: Represents a video stream/camera
- Examples: `app/models.py:StreamModel`
- Pattern: Django ORM model with custom manager

**Algorithm Model:**
- Purpose: AI/ML algorithm configuration
- Examples: `app/models.py:AlgorithmModel`
- Pattern: Django ORM model with engine type choices

**Business Algorithm Model:**
- Purpose: Composite analysis pipeline configuration
- Examples: `app/models.py:BizAlgorithmModel`
- Pattern: Django ORM model with flow type choices

**Base Engine:**
- Purpose: Abstract interface for AI/ML inference engines
- Examples: `app/analysis/engines/base.py:BaseEngine`
- Pattern: Template method pattern with abstract methods

**Camera Pipeline:**
- Purpose: Per-camera video analysis pipeline
- Examples: `app/analysis/pipeline.py:CameraPipeline`
- Pattern: Producer-consumer with thread separation

## Entry Points

**Django Application:**
- Location: `manage.py`
- Triggers: `python manage.py runserver`
- Responsibilities: Starts Django development server

**Analysis Manager:**
- Location: `app/analysis/manager.py:AnalysisManager`
- Triggers: API calls to start/stop analysis
- Responsibilities: Manages per-camera analysis processes

**GB28181 SIP Server:**
- Location: `app/utils/GB28181SipServer.py`
- Triggers: Application startup
- Responsibilities: Handles GB28181 device registration and streaming

**Media Server Manager:**
- Location: `app/utils/MediaServerManager.py`
- Triggers: Application startup
- Responsibilities: Manages ZLMediaKit process lifecycle

## Architectural Constraints

- **Threading:** Single-threaded Django request handling with thread pool for background tasks
- **Global state:** Module-level singletons (`g_config`, `g_zlm`, `g_database`, `g_gb28181SipServer`) in `app/utils/GlobalUtils.py`
- **Database:** SQLite with global thread lock (`g_dbLock`) for concurrent access
- **Processes:** Multiprocessing for video analysis to isolate CPU/GPU work
- **Memory:** Large file uploads supported (1.5GB limit) via `DATA_UPLOAD_MAX_MEMORY_SIZE`

## Anti-Patterns

### Global Singletons

**What happens:** Multiple global instances created at module import time in `app/utils/GlobalUtils.py`
**Why it's wrong:** Tight coupling, difficult testing, import-time side effects
**Do this instead:** Use dependency injection or lazy initialization with explicit lifecycle management

### Raw SQL Queries

**What happens:** Mix of Django ORM and raw SQL queries throughout codebase
**Why it's wrong:** Inconsistent data access patterns, SQL injection risk, harder maintenance
**Do this instead:** Standardize on Django ORM for all database operations

### Function-based Views

**What happens:** All views are function-based with repetitive authentication/parameter parsing
**Why it's wrong:** Code duplication, inconsistent error handling
**Do this instead:** Use class-based views with mixins for common functionality

## Error Handling

**Strategy:** Try-except with logging and JSON error responses

**Patterns:**
- View-level try-except with `g_logger.error()` logging
- Service-level error propagation with return codes
- Database operation error handling with rollback
- External service timeout and connection error handling

## Cross-Cutting Concerns

**Logging:** Custom logger (`g_logger`) writing to rotating log files in `log/` directory
**Validation:** Session-based authentication with CSRF protection for web forms
**Authentication:** Session-based with Safe header for internal API calls
**Internationalization:** Multi-language support via JSON translation files (`language-*.json`)
**Configuration:** JSON-based runtime configuration (`config.json`) with hot-reload capability

---

*Architecture analysis: 2026-08-05*
