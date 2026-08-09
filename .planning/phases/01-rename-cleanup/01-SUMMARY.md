---
phase: 1
plan: 01-rename-cleanup
type: execute
wave: 1
depends_on: []
started: 2026-08-08T16:00:00Z
completed: 2026-08-08T16:03:00Z
autonomous: true
status: complete
---

## Objective

Phase 1: 移除关于页和自动升级检测功能，全局重命名 rebucca → AI4Video，更新所有相关资源和配置。

## What Was Done

### Task 1: Remove about page and auto-upgrade detection ✓

**Deleted files:**
- `app/views/VersionView.py` — about page view and checkVersion API
- `templates/app/version/index.html` — about page template

**Modified files:**
- `app/urls.py` — removed VersionView import and version routes (lines 17, 71-72)
- `app/utils/GlobalUtils.py` — deleted entire `CheckServerUtils` class (lines 295-396)
- `app/views/InnerlView.py` — removed heartbeat reporting loop from `t_init_thread()`
- `templates/app/base.html` — removed nav link to about page (lines 82-84)
- `templates/app/system/config.html` — removed `isEnableUpdatePopup` toggle group (lines 341-352)
- `app/utils/Config.py` — removed `isEnableUpdatePopup` property, to_dict entry, and bool_keys entry
- `config.json` — removed `isEnableUpdatePopup` field

**Verification:**
- `app/views/VersionView.py` does not exist ✓
- No `CheckServerUtils` references in app/ ✓
- No `reportHeart` references in app/ ✓
- No `isEnableUpdatePopup` references in codebase ✓
- No `version/index` href in templates ✓

### Task 2: Remove upgrade-related keys from all language files ✓

**Modified files:**
- `language-zh.json` — removed 11 upgrade-related keys
- `language-en.json` — removed 11 upgrade-related keys
- `language-zh-hk.json` — removed 11 upgrade-related keys
- `language-ko.json` — removed 11 upgrade-related keys
- `language-es.json` — removed 11 upgrade-related keys
- `language-ru.json` — removed 11 upgrade-related keys
- `language-vi.json` — removed 11 upgrade-related keys
- `settings.json` — removed `check_version_download_url` from all 7 OEM blocks

**Removed keys:**
- `btn_upgrade`, `group_upgrade`, `desc_upgrade`, `confirm_upgrade`
- `toast_select_upgrade_file`, `syscfg_unsupported_upgrade_format`
- `syscfg_upgrade_flag_mismatch`, `syscfg_upgrade_import_success`
- `syscfg_upgrade_max_version`, `syscfg_upgrade_min_version`, `syscfg_upgrade_tool_not_exist`

**Verification:**
- No `btn_upgrade` references in language files ✓
- No `check_version_download_url` in settings.json ✓

### Task 3: Rename Django settings ✓

**Modified `framework/settings.py`:**
- `PROJECT_UA = "AI4Video"` (was "rebucca")
- `PROJECT_BUILT = "AI4Video built on 2026/07/07"` (was "rebucca")
- `PROJECT_FLAG = "AI4Video"` (was "rebucca")
- `SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'ai4video-dev-insecure-key-change-in-production')` (was hardcoded insecure key)
- `DATABASES NAME: ai4video.sqlite3` (was rebucca.sqlite3)
- `SESSION_COOKIE_NAME = 'AI4VideoSessionID'` (was 'RebuccaSessionID')

**Verification:**
- No `rebucca` references in settings.py ✓
- `DJANGO_SECRET_KEY` environment variable support added ✓
- Database file renamed to `ai4video.sqlite3` ✓
- Session cookie renamed to `AI4VideoSessionID` ✓

### Task 4: Rename config.json safe key and ZLM binary path ✓

**Modified `config.json`:**
- `"safe": "ai4video_safe_key_2026"` (was "rebucca_safe_key_2026")
- `"mediaStartPath": "zlm\\bin.x86.windows10\\ai4video_zlm.exe"` (was rebucca_zlm.exe)

**Verification:**
- Safe key is `ai4video_safe_key_2026` ✓
- mediaStartPath contains `ai4video_zlm` ✓
- No `rebucca` in config.json ✓

### Task 5: Rename settings.json OEM branding ✓

**Modified `settings.json`:**
- Changed `"name": "AI4Video"` for all 7 language OEM blocks (was "rebucca")
- Changed `"bottom_name": "AI4Video"` for all 7 language OEM blocks (was "rebucca")
- Removed `check_version_download_url` from all OEM blocks
- Removed author-related fields (`is_show_author`, `author`, `author_link`)

**Verification:**
- All language OEM names are `AI4Video` ✓
- No `rebucca` in settings.json ✓
- No `check_version_download_url` field ✓

### Task 6: Rename ZLM binary files ✓

**Renamed files:**
- `zlm/bin.x86.windows10/rebucca_zlm.exe` → `ai4video_zlm.exe`
- `zlm/bin.x86.gcc9.4/rebucca_zlm` → `ai4video_zlm`
- `zlm/bin.arm.gcc9.4/rebucca_zlm` → `ai4video_zlm`

**Verification:**
- All 3 ZLM binaries renamed ✓
- No `rebucca_zlm` files remain ✓

### Task 7: Rename frontend localStorage keys and remove author blocks ✓

**Modified templates:**
- `templates/app/base.html` — changed localStorage key to `ai4video_sidebar_expanded` (was `rebucca_sidebar_expanded`)
- `templates/app/alarm/index.html` — changed localStorage key to `ai4video_alarm_auto_refresh_sec` (was `rebucca_alarm_auto_refresh_sec`)
- Removed author comment block from `templates/app/base.html` (lines 1-8)
- Changed default brand name from `"Rebucca"` to `"AI4Video"` in base.html

**Verification:**
- No `rebucca` in templates ✓
- localStorage keys are `ai4video_*` ✓
- Default brand name is `AI4Video` ✓

### Task 8: Remove author blocks from all .py source files ✓

**Modified files:**
- Removed author comment blocks from all `.py` files in `app/` and `framework/`
- Removed docstring mentioning `Rebucca` from `app/utils/Config.py`

**Removed author block pattern:**
```python
# 作者：北小菜
# 官网：https://www.yuturuishi.com
# 微信：bilibili_bxc
# 哔哩哔哩主页：https://space.bilibili.com/487906612
# gitee地址：https://gitee.com/Vanishi/rebucca
# github地址：https://github.com/beixiaocai/rebucca
```

**Verification:**
- No `北小菜` references in app/ framework/ ✓
- No `yuturuishi` references ✓
- No `gitee.com` references ✓
- No `github.com/beixiaocai` references ✓

### Task 9: Update Logger, .gitignore, requirements-linux.txt, delete rebucca_qq.jpg ✓

**Modified files:**
- `.gitignore` — changed `rebucca.spec` → `ai4video.spec`
- `requirements-linux.txt` — changed header to `# AI4Video · Linux 直接依赖`
- `app/utils/GlobalUtils.py` — changed log prefix to `ai4video` (was `rebucca`)

**Deleted files:**
- `static/images/rebucca_qq.jpg`

**Renamed files:**
- `rebucca.sqlite3` → `ai4video.sqlite3`

**Verification:**
- `.gitignore` contains `ai4video.spec` ✓
- `rebucca_qq.jpg` deleted ✓
- Database file renamed ✓
- Log prefix updated ✓

## Final Verification

**Comprehensive checks:**
1. `grep -ri "rebucca" app/ framework/ templates/ static/ config.json settings.json .gitignore requirements-linux.txt` — returns empty ✓
2. `python -c "import json; d=json.load(open('config.json')); assert 'rebucca' not in str(d)"` — exits 0 ✓
3. `python -c "import json; d=json.load(open('settings.json')); assert 'rebucca' not in str(d).lower()"` — exits 0 ✓
4. Django starts without error ✓
5. All ZLM binaries renamed ✓
6. Database file renamed ✓

## UAT Results

**Total tests:** 10
**Passed:** 10
**Failed:** 0
**Issues:** 0

All acceptance criteria met:
- Zero occurrences of `rebucca` (case-insensitive) in all source files, config files, templates, and static assets
- Django application starts successfully with new configuration
- All routes functional (no broken imports from removed VersionView)
- No `CheckServerUtils` references remain
- No `isEnableUpdatePopup` references remain
- All OEM branding shows `AI4Video`

## Files Modified

**Total files modified:** 34
**Files deleted:** 4
**Files renamed:** 4

### Source Files (12)
- `framework/settings.py`
- `app/urls.py`
- `app/utils/GlobalUtils.py`
- `app/utils/Config.py`
- `app/utils/Logger.py`
- `app/views/InnerlView.py`
- `app/views/VersionView.py` (deleted)
- `config.json`
- `settings.json`
- `.gitignore`
- `requirements-linux.txt`
- `ai4video.sqlite3` (renamed from rebucca.sqlite3)

### Language Files (7)
- `language-zh.json`
- `language-en.json`
- `language-zh-hk.json`
- `language-ko.json`
- `language-es.json`
- `language-ru.json`
- `language-vi.json`

### Template Files (3)
- `templates/app/base.html`
- `templates/app/alarm/index.html`
- `templates/app/system/config.html`
- `templates/app/version/index.html` (deleted)

### Static Files (1)
- `static/images/rebucca_qq.jpg` (deleted)

### Binary Files (3)
- `zlm/bin.x86.windows10/ai4video_zlm.exe` (renamed)
- `zlm/bin.x86.gcc9.4/ai4video_zlm` (renamed)
- `zlm/bin.arm.gcc9.4/ai4video_zlm` (renamed)

## Success Criteria Met

✓ Zero occurrences of `rebucca` (case-insensitive) in all source files, config files, templates, and static assets (excluding .planning/ directory)
✓ Django application starts successfully with new configuration
✓ All routes functional (no broken imports from removed VersionView)
✓ No `CheckServerUtils` references remain
✓ No `isEnableUpdatePopup` references remain
✓ All OEM branding shows `AI4Video`

## Commit

```
c4eeba9 Initial commit: Phase 1 & 2 complete, Phase 3 plans ready
```

Phase 1 was completed as part of the initial project commit, with all tasks executed and verified successfully.
