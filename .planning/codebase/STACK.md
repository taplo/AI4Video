# Technology Stack

**Analysis Date:** 2026-08-05

## Languages

**Primary:**
- Python 3.x - Backend logic, video analysis, AI inference, web application

**Secondary:**
- HTML/CSS/JavaScript - Frontend templates and static assets

## Runtime

**Environment:**
- Python 3.x (no specific version pinned in requirements)

**Package Manager:**
- pip (requirements files)
- Lockfile: Not present

## Frameworks

**Core:**
- Django 5.0.4 - Web framework for admin panel and API endpoints
- ZLMediaKit (ai4video_zlm) - Media streaming server for RTSP/RTMP/HLS/FLV

**Testing:**
- Not detected (no test framework configured)

**Build/Dev:**
- PyInstaller 6.11.1 - Windows executable packaging
- FFmpeg - Video processing and transcoding

## Key Dependencies

**Critical:**
- opencv-python 4.10.0.84 - Video frame capture and processing
- ultralytics >=8.0.0 - YOLO model inference (YOLOv5, YOLOv8, YOLO11, YOLO26)
- torch >=2.0.0 - PyTorch backend for model inference
- onnxruntime 1.19.2 - ONNX model inference
- openvino >=2024.0.0 - Intel OpenVINO inference engine
- openai >=2.0.0 - OpenAI-compatible LLM API client

**Infrastructure:**
- onvif_zeep 0.2.12 - ONVIF camera discovery and control
- requests 2.28.2 - HTTP client for API calls
- cryptography 46.0.4 - Encryption utilities
- psutil 5.9.1 - System resource monitoring
- pillow 9.5.0 - Image processing
- numpy 1.26.4 - Numerical operations

## Configuration

**Environment:**
- `config.json` - Primary application configuration (ports, paths, SIP settings, analysis parameters)
- `settings.json` - UI language and OEM branding settings
- `.env` files: Not present

**Build:**
- `manage.spec` - PyInstaller specification file
- `manage.py` - Django management script

## Platform Requirements

**Development:**
- Windows 10+ (primary development target)
- Linux (supported via separate requirements file)
- ARM Linux (ZLMediaKit binary provided)

**Production:**
- Standalone executable (PyInstaller packaged)
- SQLite database (file-based, no external DB server)
- ZLMediaKit media server (bundled binaries in `zlm/` directory)

---

*Stack analysis: 2026-08-05*
