# Phase 4: 工程化改造 - Context

**Gathered:** 2026-08-09
**Status:** Ready for planning

<domain>
## Phase Boundary

安全加固（8个已知漏洞修复）、异常处理（结构化错误响应、重试机制、OOM保护）、系统保活（健康检查、自动重启、数据库备份）。

</domain>

<decisions>
## Implementation Decisions

### 安全加固
- **D-01:** 一次性修复所有8个安全漏洞，确保安全基线完整
- **D-02:** DEBUG 模式使用环境变量控制：`DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'`
- **D-03:** ALLOWED_HOSTS 使用环境变量配置：`ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')`
- **D-04:** 完全移除外部遥测代码（yuturuishi.com），不发送任何外部数据
- **D-05:** 移除 LLMView 的 `@csrf_exempt` 装饰器，要求 CSRF token
- **D-06:** 认证绕过修复：`'/open' in path` → `path.startswith('/open')`
- **D-07:** 点击劫持修复：`X_FRAME_OPTIONS = 'ALLOWALL'` → `'SAMEORIGIN'`
- **D-08:** 路径遍历修复：增加 `os.path.basename()` 验证

### 错误响应格式
- **D-09:** 统一 JSON 错误格式：`{code, msg, detail, timestamp}`
- **D-10:** 错误码设计：HTTP 状态码 + 业务码（如 400 + 1001）
- **D-11:** 数据库连接失败重试：指数退避重试 3 次（1s, 2s, 4s），超过返回 503
- **D-12:** OOM 保护：内存监控 + 自动重启 worker

### 健康检查设计
- **D-13:** `/api/health` 端点检查：DB + ZLMediaKit + 分析引擎状态
- **D-14:** 健康检查间隔：每 30 秒
- **D-15:** ZLMediaKit 自动重启：检测到崩溃后自动重启并记录日志
- **D-16:** Worker 健康检查：心跳检测 + 自动替换无响应 worker

### 数据库备份
- **D-17:** 备份触发方式：定时任务（APScheduler 或类似库）
- **D-18:** 备份频率：每天凌晨 2 点
- **D-19:** 备份保留策略：保留最近 7 天，超过自动删除
- **D-20:** 备份存储位置：项目目录 `backups/`

### the agent's Discretion
- 安全漏洞修复的具体实现顺序
- 错误码的具体数值分配
- 健康检查的具体实现细节
- 备份脚本的具体实现

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 核心文件
- `app/middleware.py:44` — 认证绕过漏洞（`'/open' in path`）
- `framework/settings.py:37,39,149` — DEBUG、ALLOWED_HOSTS、X_FRAME_OPTIONS
- `app/views/LLMView.py:266` — CSRF 豁免
- `app/utils/GlobalUtils.py:307,369` — 外部遥测代码
- `app/views/StorageView.py:42-56` — 路径遍历漏洞
- `app/utils/Database.py` — 数据库连接管理
- `app/analysis/pipeline.py` — OOM 保护
- `app/analysis/manager.py` — Worker 健康检查

### 参考文档
- `.planning/UPGRADE_PLAN.md` — Phase 4 完整升级方案
- `.planning/codebase/CONCERNS.md` — 已知安全问题和技术债务
- `.planning/phases/03-architecture-upgrade/03-CONTEXT.md` — Phase 3 决策（加密字段、环境变量）

### 需要修改的文件
- `app/middleware.py` — 认证绕过修复
- `framework/settings.py` — DEBUG、ALLOWED_HOSTS、X_FRAME_OPTIONS
- `app/views/LLMView.py` — 移除 @csrf_exempt
- `app/utils/GlobalUtils.py` — 移除外部遥测
- `app/views/StorageView.py` — 路径遍历修复
- `app/utils/Database.py` — 连接失败重试
- `app/analysis/pipeline.py` — OOM 保护
- `app/analysis/manager.py` — Worker 健康检查
- `app/urls.py` — 添加 /api/health 端点
- `app/views/HealthView.py` — 新建健康检查视图

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/utils/Database.py` — 数据库连接管理，可复用连接逻辑
- `app/analysis/manager.py` — AnalysisManager 核心逻辑，可复用分析流程
- `app/analysis/pipeline.py` — CameraPipeline 状态管理，可复用管道逻辑
- `app/views/ViewsBase.py` — 视图基类，可复用错误处理逻辑

### Established Patterns
- 所有视图使用 `from app.views.ViewsBase import *` 通配导入
- 配置通过 `g_config` 全局单例访问
- JSON 响应统一使用 `f_responseJson()` 返回
- 错误处理使用 `logger.warning()` 记录

### Integration Points
- `app/urls.py` — 路由配置（添加 /api/health）
- `app/middleware.py` — 认证中间件（修复绕过漏洞）
- `app/apps.py` — 应用启动逻辑（添加健康检查调度）

</code_context>

<specifics>
## Specific Ideas

无特殊要求 — 采用标准工程化改造方法。

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 4-工程化改造*
*Context gathered: 2026-08-09*
