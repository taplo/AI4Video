# Phase 1: 项目重命名与清理 - Context

**Gathered:** 2026-08-05
**Status:** Ready for planning

<domain>
## Phase Boundary

移除关于页和自动升级检测功能，全局重命名 rebucca → AI4Video，更新所有相关资源和配置。

</domain>

<decisions>
## Implementation Decisions

### 数据库与配置迁移
- **D-01:** SQLite 数据库文件 `rebucca.sqlite3` 重命名为 `ai4video.sqlite3`，同步更新 `framework/settings.py` 的 DATABASES 配置
- **D-02:** `SECRET_KEY` 从环境变量 `DJANGO_SECRET_KEY` 读取，提供开发用默认值（不含 rebucca 字样）
- **D-03:** Session cookie 名称从 `RebuccaSessionID` 改为 `AI4VideoSessionID`
- **D-04:** `config.json` 中的 `safe` key 从 `rebucca_safe_key_2026` 改为 `ai4video_safe_key_2026`
- **D-05:** 不需要数据迁移脚本（系统中只有测试用户，直接重建）
- **D-06:** `settings.json` 中所有语言的 OEM 信息（`name`, `bottom_name`）改为 `AI4Video`，`check_version_download_url` 移除

### 外部 API 处理
- **D-07:** 完全删除 `CheckServerUtils.checkVersion()` 和相关调用（VersionView、InnerlView 心跳上报）
- **D-08:** 完全删除 `CheckServerUtils.reportHeart()` 和 InnerlView.py 中的守护线程心跳逻辑
- **D-09:** 完全移除 `config.json` 中的 `isEnableUpdatePopup` 配置项及 `templates/app/system/config.html` 中的更新提醒开关
- **D-10:** 从所有 `language-*.json` 中删除升级相关 key（`btn_upgrade`, `group_upgrade`, `desc_upgrade`, `confirm_upgrade`, `toast_select_upgrade_file`, `syscfg_unsupported_upgrade_format`, `syscfg_upgrade_flag_mismatch`, `syscfg_upgrade_import_success`, `syscfg_upgrade_max_version`, `syscfg_upgrade_min_version`, `syscfg_upgrade_tool_not_exist`）

### 前端 localStorage
- **D-11:** 直接重命名 localStorage keys：`rebucca_sidebar_expanded` → `ai4video_sidebar_expanded`，`rebucca_alarm_auto_refresh_sec` → `ai4video_alarm_auto_refresh_sec`（无老用户，无需迁移 JS）

### 源码注释与二进制
- **D-12:** 移除所有 `.py` 和 `.html` 文件开头的作者信息块（北小菜、yuturuishi.com、bilibili、gitee/github URL），共约 40+ 个文件
- **D-13:** 重命名 ZLM 二进制文件：`rebucca_zlm.exe` → `ai4video_zlm.exe`，`rebucca_zlm` → `ai4video_zlm`（所有平台），更新 `config.json` 中的 `mediaStartPath` 引用
- **D-14:** 日志文件名前缀从 `rebucca` 改为 `ai4video`（`log/ai4video<timestamp>.log`）
- **D-15:** 删除 `static/images/rebucca_qq.jpg`

### the agent's Discretion
- 语言文件中 `check_version_download_url` 的处理方式：移除整个字段
- `.gitignore` 中 `rebucca.spec` 的更新：改为 `ai4video.spec`
- `requirements-linux.txt` 头部注释中的 `rebucca`：移除或更新

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 项目配置
- `.planning/UPGRADE_PLAN.md` — 完整升级计划（Phase 1-6）
- `.planning/codebase/STACK.md` — 技术栈分析（依赖、配置文件位置）
- `.planning/codebase/ARCHITECTURE.md` — 架构分析（组件职责、入口点）
- `.planning/codebase/CONCERNS.md` — 已知问题（安全、性能、脆弱区域）

### 需要修改的核心文件
- `framework/settings.py` — SECRET_KEY, PROJECT_UA/BUILT/FLAG, DATABASES, SESSION_COOKIE_NAME
- `config.json` — safe key, mediaStartPath, isEnableUpdatePopup
- `settings.json` — 所有语言的 OEM 信息
- `app/utils/GlobalUtils.py:295-396` — CheckServerUtils 类（checkVersion + reportHeart）
- `app/views/VersionView.py` — 关于页视图
- `app/urls.py:71-72` — version 路由
- `app/views/InnerlView.py:320-345` — 守护线程心跳逻辑
- `templates/app/version/index.html` — 关于页模板
- `templates/app/system/config.html:341-352` — 更新提醒开关
- `templates/app/base.html:23` — localStorage key
- `templates/app/alarm/index.html:116` — localStorage key
- `app/utils/Logger.py` — 日志文件名前缀
- `.gitignore` — rebucca.spec 引用

### 语言文件
- `language-zh.json`, `language-en.json`, `language-zh-hk.json`, `language-ko.json`, `language-es.json`, `language-ru.json`, `language-vi.json` — 升级相关 key

### 二进制文件
- `zlm/bin.x86.windows10/rebucca_zlm.exe`
- `zlm/bin.x86.gcc9.4/rebucca_zlm`
- `zlm/bin.arm.gcc9.4/rebucca_zlm`

### 静态资源
- `static/images/rebucca_qq.jpg` — 删除

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/views/ViewsBase.py` — 通用视图工具函数（f_parseGetParams, f_responseJson 等），重命名不涉及
- `app/utils/Config.py` — 配置管理类，isEnableUpdatePopup 的移除需要修改 save_from_web() 和 to_dict()

### Established Patterns
- 所有 view 函数使用 `from app.views.ViewsBase import *` 通配导入
- 配置通过 `g_config` 全局单例访问
- JSON 响应统一使用 `f_responseJson()` 返回

### Integration Points
- `app/urls.py` — 移除 version 路由
- `app/middleware.py` — 不涉及（认证逻辑保持不变）
- `app/apps.py:42` — schema_upgrade 调用不涉及（与 rebucca 命名无关）

</code_context>

<specifics>
## Specific Ideas

无特殊要求 — 采用标准重命名和清理方法。

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 1-项目重命名与清理*
*Context gathered: 2026-08-05*
