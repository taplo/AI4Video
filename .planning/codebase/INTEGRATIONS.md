# External Integrations

**Analysis Date:** 2026-08-05

## APIs & External Services

**Media Streaming (ZLMediaKit):**
- ZLMediaKit - Core media server for stream proxy, transcoding, and distribution
  - HTTP API: `{mediaHttpHost}/index/api/*`
  - Endpoints: `addStreamProxy`, `delStreamProxy`, `close_streams`, `getMediaList`, `getMediaInfo`, `openRtpServer`, `closeRtpServer`, `getThreadsLoad`
  - SDK/Client: Custom `app/utils/ZLMediaKitApi.py`
  - Auth: `mediaSecret` parameter in requests
  - Config: `config.json` → `mediaHttpPort`, `mediaSecret`

**AI/ML Services (OpenAI-Compatible):**
- OpenAI-compatible API - Large Language Model inference for video analysis
  - Endpoint: Configurable via `LLMModel.api_url` (default: `https://api.openai.com/v1`)
  - SDK/Client: `openai` package (v2.0+)
  - Auth: API key stored in `av_llm.api_key` database field
  - Usage: Vision-based video content analysis via `app/utils/LLMUtils.py`

**Camera Protocols:**
- ONVIF - Camera discovery and RTSP stream URL retrieval
  - Protocol: WS-Discovery (UDP multicast to 239.255.255.250:3702)
  - SDK/Client: `onvif_zeep` package
  - Auth: Camera credentials (username/password)
  - Implementation: `app/services/onvif_discovery.py`

- GB28181 - Chinese national standard for video surveillance
  - Protocol: SIP signaling + RTP media
  - Implementation: `app/utils/GB28181SipServer.py`
  - Auth: SIP Digest authentication
  - Config: `config.json` → `sipServer` section

## Data Storage

**Databases:**
- SQLite (file-based)
  - Connection: `ai4video.sqlite3`
  - Client: Django ORM (`django.db.backends.sqlite3`)
  - Models: `app/models.py`
  - Tables: `av_stream`, `av_algorithm`, `av_biz_algorithm`, `av_zone`, `av_alarm`, `av_recording`, `av_llm`, `av_log`

**File Storage:**
- Local filesystem only
  - Upload directory: `static/upload/` (algorithm weights, audio files)
  - Storage directory: `static/storage/` (temp files, alarm snapshots, recordings)
  - Snapshots: `static/storage/snapshots/`
  - Recordings: `static/storage/record/`
  - Config: `config.json` → `uploadDir`, `storageDir`

**Caching:**
- None detected

## Authentication & Identity

**Auth Provider:**
- Custom session-based authentication
  - Implementation: Django built-in auth (`django.contrib.auth`)
  - Session cookie: `AI4VideoSessionID`
  - Session expiry: 7 days
  - Login captcha: Optional (configurable via `config.json` → `isEnableLoginCaptcha`)
  - Middleware: `app/middleware.py` → `SimpleMiddleware`

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- Custom logging via `app/utils/Logger.py` and `app/utils/LogUtils.py`
- Admin operation logs stored in `av_log` database table
- Debug mode: Configurable via `config.json` → `logDebug`

## CI/CD & Deployment

**Hosting:**
- Standalone executable (PyInstaller)
- Django development server (internal)
- ZLMediaKit media server (bundled)

**CI Pipeline:**
- Not detected

## Environment Configuration

**Required env vars:**
- None detected (all configuration via `config.json`)

**Secrets location:**
- `config.json` → `safe`, `mediaSecret`, `sipServer.sipServerPass`
- `av_llm.api_key` database field
- `framework/settings.py` → `SECRET_KEY` (hardcoded, insecure default)

## Webhooks & Callbacks

**Incoming:**
- `/inner/on_media_update_stream` - ZLMediaKit stream update callback
- `/inner/on_media_delete_stream` - ZLMediaKit stream delete callback
- `/inner/on_publish` - ZLMediaKit publish event callback
- `/inner/on_stream_not_found` - ZLMediaKit stream not found callback
- GB28181 SIP messages (REGISTER, INVITE, BYE, MESSAGE, NOTIFY)

**Outgoing:**
- ZLMediaKit HTTP API calls (stream proxy management)
- OpenAI-compatible LLM API calls (vision inference)
- ONVIF WS-Discovery multicast probes

## External Tool Integrations

**FFmpeg:**
- Purpose: Video transcoding, frame extraction, recording
- Config: `config.json` → `ffmpeg` (path to binary)
- Usage: Called via subprocess in various utility functions

**ZLMediaKit Binaries:**
- Purpose: Media streaming server
- Location: `zlm/bin.x86.windows10/`, `zlm/bin.x86.gcc9.4/`, `zlm/bin.arm.gcc9.4/`
- Config: `zlm/bin.x86.windows10/config.ini`
- Auto-start: Configurable via `config.json` → `autoStartMedia`

---

*Integration audit: 2026-08-05*
