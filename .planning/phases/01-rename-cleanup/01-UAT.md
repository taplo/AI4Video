---
status: complete
phase: 01-rename-cleanup
source: 01-PLAN.md
started: 2026-08-07T12:00:00Z
updated: 2026-08-07T12:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Django Settings Renamed
expected: framework/settings.py has PROJECT_UA="AI4Video", PROJECT_FLAG="AI4Video", SECRET_KEY from os.environ.get('DJANGO_SECRET_KEY'), database "ai4video.sqlite3", session cookie "AI4VideoSessionID"
result: pass

### 2. Config.json Updated
expected: config.json has safe key "ai4video_safe_key_2026", mediaStartPath points to "ai4video_zlm.exe", no "isEnableUpdatePopup" key
result: pass

### 3. Settings.json OEM Updated
expected: settings.json has name="AI4Video" and bottom_name="AI4Video" for all 7 languages, no "check_version_download_url" in oem sections
result: pass

### 4. ZLM Binaries Renamed
expected: zlm/bin.x86.windows10/ai4video_zlm.exe, zlm/bin.x86.gcc9.4/ai4video_zlm, zlm/bin.arm.gcc9.4/ai4video_zlm exist; no rebucca_zlm files remain
result: pass

### 5. Frontend localStorage Renamed
expected: base.html uses "ai4video_sidebar_expanded", alarm/index.html uses "ai4video_alarm_auto_refresh_sec", app.js SIDEBAR_STORAGE_KEY="ai4video_sidebar_expanded"
result: pass

### 6. About Page Removed
expected: templates/app/version/ directory deleted, version routes removed from urls.py, VersionView import removed
result: pass

### 7. Upgrade Functionality Removed
expected: CheckServerUtils class deleted from GlobalUtils.py, isEnableUpdatePopup removed from Config.py and config.html, heartbeat report loop removed from InnerlView.py
result: pass

### 8. Author Blocks Removed
expected: No "# 作者：北小菜" comments in .py files, no author block in base.html sidebar footer, settings.json author fields cleared
result: pass

### 9. Logger and Misc Updated
expected: GlobalUtils.py log prefix "ai4video", .gitignore has "ai4video.spec", requirements-linux.txt header says "AI4Video", static/images/rebucca_qq.jpg deleted
result: pass

### 10. No Rebucca References in Source
expected: grep for "rebucca" (case-insensitive) in .py, .html, .js, .json, .css files returns zero matches (excluding .planning/ directory)
result: pass

## Summary

total: 10
passed: 10
issues: 0
pending: 0
skipped: 0

## Gaps

[none yet]
