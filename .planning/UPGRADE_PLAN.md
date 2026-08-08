# AI4Video 项目升级计划

**创建日期：** 2026-08-05
**状态：** 规划中

## 升级概览

基于对现有代码库的全面分析，制定以下6个方面的升级方案。

---

## Phase 1: 项目重命名与清理（rebucca → AI4Video）

### 移除关于页和自动升级检测

**删除文件/代码：**
- `app/views/VersionView.py` — 删除 `index()` 和 `api_openCheckVersion()`
- `templates/app/version/index.html` — 删除模板
- `app/urls.py:71-72` — 移除 version 路由
- `app/utils/GlobalUtils.py:295-396` — 移除 `CheckServerUtils` 类（checkVersion + reportHeart）
- `app/views/InnerlView.py:337` — 移除心跳上报调用
- `config.json` — 移除 `isEnableUpdatePopup` 配置项
- `templates/app/system/config.html:341-352` — 移除更新提醒开关

**清理语言文件：**
- 所有 `language-*.json` — 移除升级相关 key（`btn_upgrade`, `group_upgrade`, `desc_upgrade`, `confirm_upgrade`, `toast_select_upgrade_file`, `syscfg_unsupported_upgrade_format` 等）

### 全局重命名 rebucca → AI4Video

**配置文件：**
- `framework/settings.py` — `PROJECT_UA`, `PROJECT_BUILT`, `PROJECT_FLAG`, `SECRET_KEY`, 数据库名 `rebucca.sqlite3` → `ai4video.sqlite3`, session cookie 名 `RebuccaSessionID` → `AI4VideoSessionID`
- `config.json` — `safe` key (`rebucca_safe_key_2026` → `ai4video_safe_key_2026`), ZLM 二进制路径 (`rebucca_zlm.exe` → `ai4video_zlm.exe`)
- `settings.json` — 所有语言的 `name`, `bottom_name`, `check_version_download_url`

**二进制文件：**
- `zlm/bin.x86.windows10/rebucca_zlm.exe` → `ai4video_zlm.exe`
- `zlm/bin.x86.gcc9.4/rebucca_zlm` → `ai4video_zlm`
- `zlm/bin.arm.gcc9.4/rebucca_zlm` → `ai4video_zlm`

**源代码注释：**
- 所有 `.py` 和 `.html` 文件中的 gitee/github URL 注释

**前端：**
- `templates/app/base.html:23` — localStorage key `rebucca_sidebar_expanded` → `ai4video_sidebar_expanded`
- `templates/app/alarm/index.html:116` — localStorage key `rebucca_alarm_auto_refresh_sec` → `ai4video_alarm_auto_refresh_sec`

**其他：**
- `rebucca.sqlite3` → `ai4video.sqlite3`
- `.gitignore` — `rebucca.spec` → `ai4video.spec`
- `requirements-linux.txt` — 头部注释
- `static/images/rebucca_qq.jpg` → `ai4video_qq.jpg`

---

## Phase 2: ONNX 模型检测修复

### 问题分析

ONNX 模型上传后检测报错，可能原因：
1. `algorithm_type` 默认为 `"yolo8"`，但模型可能是 YOLOv5/11/26，导致后处理格式不匹配
2. 模型文件路径解析失败（`resolve_model_path()` 返回空字符串）
3. 输入尺寸不匹配（配置的 input_size 与模型实际输入不一致）
4. 缺少标签文件导致空标签

### 修复方案

**`app/views/SmallModelView.py`：**
- 在 `smallmodel_openProbe()` 接口中自动检测 `algorithm_type`（通过分析 ONNX 模型输出 shape）

**`app/analysis/engines/onnx_engine.py`：**
- 在 `load()` 中增加更详细的错误日志（记录模型文件路径、provider 列表、input/output shape）
- 在 `detect()` 中增加输入尺寸不匹配时的自动 resize

**`app/analysis/worker_pool.py`：**
- 在 `resolve_model_path()` 中增加路径不存在时的警告日志

**`app/analysis/engines/yolo_postprocess.py`：**
- 在 `_decode_detect()` 中增加输出 shape 与 algorithm_type 不匹配时的自动降级逻辑（如 v5 格式自动检测）

---

## Phase 3: 架构升级

### 数据库层

**消除全局锁：**
- 将 `app/utils/Database.py` 的全局 `g_dbLock` 替换为 Django ORM 的 connection pooling
- 将所有 raw SQL 查询迁移到 Django ORM：
  - `app/views/StreamView.py:40,218,259,532,546,549,572,575,580,582,1089,1142`
  - `app/views/LLMView.py:38,42`
  - `app/views/ViewsBase.py:138`

**模型层重构：**
- 实现 `BaseModel` mixin 消除所有 model 中重复的 `save()`/`delete()` 方法
- 涉及文件：`app/models.py:74-82,166-174,245-253,289-297,327-335,388-396,420-428`

### 配置管理

- 将 `config.json` 中的敏感值迁移到环境变量
- 实现配置热重载的线程安全机制

### 进程管理

- 将 `AnalysisManager` 的 multiprocessing 改为基于 `concurrent.futures` 的进程池
- 实现优雅关闭（graceful shutdown）信号处理

---

## Phase 4: 工程化改造

### 安全加固

| 问题 | 文件 | 修复方案 |
|------|------|---------|
| 认证绕过 | `app/middleware.py:44` | `'/open' in path` → `path.startswith('/open')` |
| DEBUG 模式 | `framework/settings.py:37` | `DEBUG = True` → 环境变量控制 |
| 全 HOSTS | `framework/settings.py:39` | `ALLOWED_HOSTS = ["*"]` → 可配置 |
| 点击劫持 | `framework/settings.py:149` | `X_FRAME_OPTIONS = 'ALLOWALL'` → `SAMEORIGIN` |
| 明文密码 | `app/models.py:34,380` | 使用 `django-fernet-fields` 加密存储 |
| CSRF 豁免 | `app/views/LLMView.py:266` | 移除 `@csrf_exempt` |
| 外部遥测 | `app/utils/GlobalUtils.py:307,369` | 移除或改为 opt-in |
| 路径遍历 | `app/views/StorageView.py:42-56` | 增加 `os.path.basename()` 验证 |

### 异常处理

- 在所有 view 函数中增加结构化错误响应（统一 JSON 格式：`{code, msg, detail, timestamp}`）
- 在 `app/utils/Database.py` 中增加连接失败重试机制
- 在 `app/analysis/pipeline.py` 中增加 OOM 保护和内存监控
- 在 background worker 中增加崩溃自动重启

### 系统保活

- 实现 `/api/health` 端点（检查 DB、ZLMediaKit、分析引擎状态）
- 实现 `MediaServerManager` 的自动重启
- 在 `InferencePool` 中增加 worker 健康检查和自动替换
- 实现 cron-style 的数据库备份

---

## Phase 5: 测试体系建设

### 测试框架

- 建立 `pytest` 测试框架
- 创建 `conftest.py`、`pytest.ini`、`tests/` 目录

### 测试用例

| 测试文件 | 覆盖范围 | 优先级 |
|---------|---------|-------|
| `test_auth.py` | 认证、登录、captcha、brute-force protection | 高 |
| `test_stream.py` | 流管理 CRUD、代理创建 | 高 |
| `test_algorithm.py` | 算法模型 CRUD、引擎工厂 | 高 |
| `test_onnx_engine.py` | ONNX 加载、推理、后处理 | 高 |
| `test_analysis_pipeline.py` | 分析流水线生命周期 | 中 |
| `test_middleware.py` | 中间件认证逻辑 | 高 |
| `test_api.py` | API 端点集成测试 | 中 |
| `test_config.py` | 配置管理、热重载 | 低 |

### CI 配置

- 建立 GitHub Actions 工作流
- 自动运行测试、lint、类型检查

---

## Phase 6: 其他实用升级

### 依赖升级

- Django 5.0.4 → 5.2+
- opencv-python 4.10.0.84 → 最新稳定版
- torch >=2.0.0 → 最新稳定版
- ultralytics >=8.0.0 → 最新稳定版
- onnxruntime 1.19.2 → 最新稳定版

### 功能增强

- 实现 `manage.py` 的 `migrate` 命令自动运行
- 增加请求限流（`django-ratelimit`）
- 增加审计日志（记录所有认证尝试和数据修改）
- 优化前端静态资源（压缩 CSS/JS）
- 增加 OpenAPI/Swagger API 文档

---

## 执行顺序

| Phase | 内容 | 预估工作量 | 风险 | 依赖 |
|-------|------|-----------|------|------|
| 1 | 重命名与清理 | 小 | 低 | 无 |
| 2 | ONNX 修复 | 中 | 中 | 无 |
| 4 | 工程化改造 | 大 | 中 | Phase 1 |
| 3 | 架构升级 | 大 | 高 | Phase 4 |
| 5 | 测试体系 | 大 | 低 | Phase 3 |
| 6 | 其他升级 | 中 | 低 | Phase 3 |

**建议：** 先执行 Phase 1（快速见效），然后 Phase 2（修复关键 bug），再按 4→3→5→6 的顺序推进。

---

*Last updated: 2026-08-05 after initial planning*
