---
phase: 1
plan: 01-rename-cleanup
type: execute
wave: 1
depends_on: []
files_modified:
  - framework/settings.py
  - config.json
  - settings.json
  - app/urls.py
  - app/utils/GlobalUtils.py
  - app/utils/Config.py
  - app/utils/Logger.py
  - app/views/VersionView.py
  - app/views/InnerlView.py
  - templates/app/version/index.html
  - templates/app/base.html
  - templates/app/alarm/index.html
  - templates/app/system/config.html
  - .gitignore
  - requirements-linux.txt
  - language-zh.json
  - language-en.json
  - language-zh-hk.json
  - language-ko.json
  - language-es.json
  - language-ru.json
  - language-vi.json
  - zlm/bin.x86.windows10/rebucca_zlm.exe
  - zlm/bin.x86.gcc9.4/rebucca_zlm
  - zlm/bin.arm.gcc9.4/rebucca_zlm
  - static/images/rebucca_qq.jpg
autonomous: true
requirements: []
---

<objective>
Phase 1: 移除关于页和自动升级检测功能，全局重命名 rebucca → AI4Video，更新所有相关资源和配置。
</objective>

<tasks>

## Task 1: Remove about page and auto-upgrade detection

<read_first>
- `app/views/VersionView.py` — about page view and checkVersion API
- `app/urls.py:71-72` — version routes
- `app/utils/GlobalUtils.py:295-396` — CheckServerUtils class
- `app/views/InnerlView.py:320-345` — heartbeat thread
- `templates/app/version/index.html` — about page template
- `templates/app/system/config.html:341-352` — update popup toggle
- `templates/app/base.html:82-84` — nav link to about page
- `app/utils/Config.py:81` — isEnableUpdatePopup property
- `app/utils/Config.py:167` — to_dict isEnableUpdatePopup
- `app/utils/Config.py:216` — save_from_web bool_keys
- `config.json:21` — isEnableUpdatePopup field
</read_first>

<action>
1. Delete `app/views/VersionView.py` entirely
2. Delete `templates/app/version/index.html` entirely
3. In `app/urls.py`: remove lines 17 (`from .views import VersionView`), 71 (`path('version/openCheckVersion', ...)`), 72 (`path('version/index', ...)`)
4. In `app/utils/GlobalUtils.py`: delete the entire `CheckServerUtils` class (lines 295-396)
5. In `app/views/InnerlView.py`: in `t_init_thread()`, remove the heartbeat reporting loop (lines 332-337: `i = 0`, `report_count = 0`, `while True:`, `if i > 0 and i % 480 == 0:`, `report_count += 1`, `CheckServerUtils.reportHeart(...)`, `time.sleep(10)`, `i += 1`). Keep only the `autoAddStreamProxy` block. Remove `import CheckServerUtils` if present in the imports at top of file.
6. In `templates/app/base.html`: remove lines 82-84 (the `<a href="/version/index"` nav item for about page)
7. In `templates/app/system/config.html`: remove lines 341-352 (the `isEnableUpdatePopup` toggle group)
8. In `app/utils/Config.py`: remove `self.isEnableUpdatePopup = ...` from `_apply()` (line 81), remove `d["isEnableUpdatePopup"]` from `to_dict()` (line 167), remove `"isEnableUpdatePopup"` from `bool_keys` tuple in `save_from_web()` (line 216)
9. In `config.json`: remove the `"isEnableUpdatePopup": true,` line
</action>

<verify>
- `app/views/VersionView.py` does not exist
- `templates/app/version/index.html` does not exist
- `app/urls.py` contains no reference to `VersionView` or `version/`
- `app/utils/GlobalUtils.py` contains no `CheckServerUtils` class
- `app/views/InnerlView.py` contains no `CheckServerUtils` or `reportHeart` reference
- `templates/app/base.html` contains no `version/index` href
- `templates/app/system/config.html` contains no `isEnableUpdatePopup`
- `app/utils/Config.py` contains no `isEnableUpdatePopup`
- `config.json` contains no `isEnableUpdatePopup`
</verify>

<acceptance_criteria>
- `python -c "from app.views import VersionView"` fails with ImportError
- `grep -r "CheckServerUtils" app/` returns empty
- `grep -r "reportHeart" app/` returns empty
- `grep -r "isEnableUpdatePopup" .` returns empty (excluding .planning/)
- `grep -r "version/index" templates/` returns empty
</acceptance_criteria>
</task>

## Task 2: Remove upgrade-related keys from all language files

<read_first>
- `language-zh.json` — contains `btn_upgrade`, `group_upgrade`, `desc_upgrade`, `confirm_upgrade`, `toast_select_upgrade_file`, `syscfg_unsupported_upgrade_format`, `syscfg_upgrade_flag_mismatch`, `syscfg_upgrade_import_success`, `syscfg_upgrade_max_version`, `syscfg_upgrade_min_version`, `syscfg_upgrade_tool_not_exist`
- `language-en.json` — same keys
- `language-zh-hk.json` — same keys
- `language-ko.json` — same keys
- `language-es.json` — same keys
- `language-ru.json` — same keys
- `language-vi.json` — same keys
</read_first>

<action>
For each of the 7 language files, remove these keys:
- `btn_upgrade`
- `group_upgrade`
- `desc_upgrade`
- `confirm_upgrade`
- `toast_select_upgrade_file`
- `syscfg_unsupported_upgrade_format`
- `syscfg_upgrade_flag_mismatch`
- `syscfg_upgrade_import_success`
- `syscfg_upgrade_max_version`
- `syscfg_upgrade_min_version`
- `syscfg_upgrade_tool_not_exist`

Also remove `check_version_download_url` from `settings.json` OEM blocks (all 7 languages).
</action>

<verify>
- `grep -r "btn_upgrade" language-*.json` returns empty
- `grep -r "check_version_download_url" settings.json` returns empty
</verify>

<acceptance_criteria>
- All 7 language files contain zero upgrade-related keys
- `settings.json` contains no `check_version_download_url`
</acceptance_criteria>
</task>

## Task 3: Rename Django settings (SECRET_KEY, DB, session cookie, project identifiers)

<read_first>
- `framework/settings.py` — lines 23-26 (PROJECT_*), 33 (SECRET_KEY), 96 (DATABASES NAME), 142 (SESSION_COOKIE_NAME)
</read_first>

<action>
1. Line 23: `PROJECT_UA = "rebucca"` → `PROJECT_UA = "AI4Video"`
2. Line 24: `PROJECT_BUILT = "rebucca built on 2026/07/07"` → `PROJECT_BUILT = "AI4Video built on 2026/07/07"`
3. Line 26: `PROJECT_FLAG = "rebucca"` → `PROJECT_FLAG = "AI4Video"`
4. Line 33: Replace `SECRET_KEY = 'rebucca-insecure-oam*2x=@ynuv5w*&$*yc-1cjsku-b2@$x*t9!swd+n0glv76'` with:
   `SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'ai4video-dev-insecure-key-change-in-production')`
5. Line 96: `'NAME': BASE_DIR / 'rebucca.sqlite3'` → `'NAME': BASE_DIR / 'ai4video.sqlite3'`
6. Line 142: `SESSION_COOKIE_NAME = 'RebuccaSessionID'` → `SESSION_COOKIE_NAME = 'AI4VideoSessionID'`
</action>

<verify>
- `framework/settings.py` contains no `rebucca` (case-insensitive)
- `framework/settings.py` contains `os.environ.get('DJANGO_SECRET_KEY'`
- `framework/settings.py` contains `ai4video.sqlite3`
- `framework/settings.py` contains `AI4VideoSessionID`
</verify>

<acceptance_criteria>
- `python -c "import re; c=open('framework/settings.py').read(); assert 'rebucca' not in c.lower()"` exits 0
- `python -c "import re; c=open('framework/settings.py').read(); assert 'DJANGO_SECRET_KEY' in c"` exits 0
</acceptance_criteria>
</task>

## Task 4: Rename config.json safe key and ZLM binary path

<read_first>
- `config.json` — line 2 (safe key), line 10 (mediaStartPath)
</read_first>

<action>
1. In `config.json`: change `"safe": "rebucca_safe_key_2026"` → `"safe": "ai4video_safe_key_2026"`
2. In `config.json`: change `"mediaStartPath": "zlm\\bin.x86.windows10\\rebucca_zlm.exe"` → `"mediaStartPath": "zlm\\bin.x86.windows10\\ai4video_zlm.exe"`
</action>

<verify>
- `python -c "import json; d=json.load(open('config.json')); assert d['safe']=='ai4video_safe_key_2026'"` exits 0
- `python -c "import json; d=json.load(open('config.json')); assert 'rebucca' not in d['mediaStartPath']"` exits 0
</verify>

<acceptance_criteria>
- `config.json` safe key is `ai4video_safe_key_2026`
- `config.json` mediaStartPath contains `ai4video_zlm`
- No `rebucca` string in config.json
</acceptance_criteria>
</task>

## Task 5: Rename settings.json OEM branding

<read_first>
- `settings.json` — all OEM blocks for 7 languages
</read_first>

<action>
In `settings.json`, for each of the 7 language entries:
1. Change `"name": "rebucca"` → `"name": "AI4Video"`
2. Change `"bottom_name": "rebucca"` → `"bottom_name": "AI4Video"`
3. Remove the `"check_version_download_url"` key-value pair from each OEM block
4. Remove `"is_show_author": true` and the `"author"` / `"author_link"` fields (since author blocks are being removed per D-12)
</action>

<verify>
- `python -c "import json; d=json.load(open('settings.json')); [assert v['oem']['name']=='AI4Video' for v in d['languages'].values()]"` exits 0
- `grep -c "rebucca" settings.json` returns 0
- `grep -c "check_version_download_url" settings.json` returns 0
</verify>

<acceptance_criteria>
- `settings.json` contains no `rebucca` string
- All language OEM names are `AI4Video`
- No `check_version_download_url` field
</acceptance_criteria>
</task>

## Task 6: Rename ZLM binary files

<read_first>
- `zlm/bin.x86.windows10/rebucca_zlm.exe` — Windows binary
- `zlm/bin.x86.gcc9.4/rebucca_zlm` — Linux x86 binary
- `zlm/bin.arm.gcc9.4/rebucca_zlm` — Linux ARM binary
</read_first>

<action>
1. `Move-Item "zlm\bin.x86.windows10\rebucca_zlm.exe" "zlm\bin.x86.windows10\ai4video_zlm.exe"`
2. `Move-Item "zlm\bin.x86.gcc9.4\rebucca_zlm" "zlm\bin.x86.gcc9.4\ai4video_zlm"`
3. `Move-Item "zlm\bin.arm.gcc9.4\rebucca_zlm" "zlm\bin.arm.gcc9.4\ai4video_zlm"`
</action>

<verify>
- `Test-Path "zlm\bin.x86.windows10\ai4video_zlm.exe"` returns True
- `Test-Path "zlm\bin.x86.gcc9.4\ai4video_zlm"` returns True
- `Test-Path "zlm\bin.arm.gcc9.4\ai4video_zlm"` returns True
- No `rebucca_zlm` files exist in `zlm/`
</verify>

<acceptance_criteria>
- All 3 ZLM binaries renamed from `rebucca_zlm*` to `ai4video_zlm*`
- No `rebucca_zlm` files remain in `zlm/` directory
</acceptance_criteria>
</task>

## Task 7: Rename frontend localStorage keys and remove author blocks from templates

<read_first>
- `templates/app/base.html:23` — `rebucca_sidebar_expanded` localStorage key
- `templates/app/alarm/index.html:116` — `rebucca_alarm_auto_refresh_sec` localStorage key
- `templates/app/base.html:1-8` — author comment block
- `templates/app/version/index.html:1-8` — author comment block (already deleted in Task 1)
</read_first>

<action>
1. In `templates/app/base.html`: change `'rebucca_sidebar_expanded'` → `'ai4video_sidebar_expanded'` (line 23)
2. In `templates/app/alarm/index.html`: change `'rebucca_alarm_auto_refresh_sec'` → `'ai4video_alarm_auto_refresh_sec'` (line 116)
3. In `templates/app/base.html`: remove the author comment block (lines 1-8: `<!-- 作者：北小菜 ... -->`)
4. Also remove the default brand name `"Rebucca"` from template defaults in `base.html` (lines 17 and 44 — change `default:"Rebucca"` to `default:"AI4Video"`)
</action>

<verify>
- `grep -r "rebucca" templates/` returns empty (excluding .planning/)
- `templates/app/base.html` contains `ai4video_sidebar_expanded`
- `templates/app/alarm/index.html` contains `ai4video_alarm_auto_refresh_sec`
</verify>

<acceptance_criteria>
- No `rebucca` string in any template file
- localStorage keys are `ai4video_*`
- Default brand name is `AI4Video`
</acceptance_criteria>
</task>

## Task 8: Remove author blocks from all .py source files

<read_first>
- All `.py` files in `app/` and `framework/` — approximately 40+ files with author comment blocks at top
</read_first>

<action>
For every `.py` file under `app/` and `framework/`, remove the author comment block at the top of the file. The block typically looks like:
```python
# 作者：北小菜
# 官网：https://www.yuturuishi.com
# 微信：bilibili_bxc
# 哔哩哔哩主页：https://space.bilibili.com/487906612
# gitee地址：https://gitee.com/Vanishi/rebucca
# github地址：https://github.com/beixiaocai/rebucca
```

Remove these 6 lines from every `.py` file that contains them. Also remove the docstring in `app/utils/Config.py` line 7 that mentions `Rebucca`.
</action>

<verify>
- `grep -r "北小菜" app/ framework/` returns empty
- `grep -r "yuturuishi" app/ framework/` returns empty
- `grep -r "gitee.com" app/ framework/` returns empty
- `grep -r "github.com/beixiaocai" app/ framework/` returns empty
</verify>

<acceptance_criteria>
- No author attribution blocks remain in any `.py` file
- No `rebucca` URL references in `.py` files
</acceptance_criteria>
</task>

## Task 9: Update Logger, .gitignore, requirements-linux.txt, delete rebucca_qq.jpg, rename database file

<read_first>
- `app/utils/Logger.py` — log file naming (called from elsewhere, need to find caller)
- `.gitignore:26` — `rebucca.spec`
- `requirements-linux.txt:1` — header comment
- `static/images/rebucca_qq.jpg` — to delete
- `rebucca.sqlite3` — to rename
</read_first>

<action>
1. In `.gitignore`: change `rebucca.spec` → `ai4video.spec` (line 26)
2. In `requirements-linux.txt`: change line 1 `# rebucca · Linux 直接依赖` → `# AI4Video · Linux 直接依赖`
3. Delete `static/images/rebucca_qq.jpg`
4. Rename `rebucca.sqlite3` → `ai4video.sqlite3` (if it exists)
5. In `app/utils/GlobalUtils.py` line 39: change `__log_name = "%s%s.log" % ("rebucca", ...)` → `__log_name = "%s%s.log" % ("ai4video", ...)`
</action>

<verify>
- `.gitignore` contains `ai4video.spec`, not `rebucca.spec`
- `requirements-linux.txt` line 1 contains `AI4Video`
- `static/images/rebucca_qq.jpg` does not exist
- `rebucca.sqlite3` does not exist (if it existed before)
- `app/utils/GlobalUtils.py:39` contains `ai4video` not `rebucca`
</verify>

<acceptance_criteria>
- No `rebucca.spec` in `.gitignore`
- `rebucca_qq.jpg` deleted
- Database file renamed (if existed)
- Log prefix updated
</acceptance_criteria>
</task>

</tasks>

<verification>
1. `grep -ri "rebucca" app/ framework/ templates/ static/ config.json settings.json .gitignore requirements-linux.txt` returns empty
2. `python -c "import json; d=json.load(open('config.json')); assert 'rebucca' not in str(d)"` exits 0
3. `python -c "import json; d=json.load(open('settings.json')); assert 'rebucca' not in str(d).lower()"` exits 0
4. Django starts without error: `python manage.py check` exits 0
5. All ZLM binaries renamed
6. Database file renamed
</verification>

<success_criteria>
- Zero occurrences of `rebucca` (case-insensitive) in all source files, config files, templates, and static assets (excluding .planning/ directory)
- Django application starts successfully with new configuration
- All routes functional (no broken imports from removed VersionView)
- No `CheckServerUtils` references remain
- No `isEnableUpdatePopup` references remain
- All OEM branding shows `AI4Video`
</success_criteria>
