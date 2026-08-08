# Phase 3: 架构升级 - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

数据库层现代化（消除全局锁、ORM 迁移）、模型层重构（BaseModel mixin）、配置管理安全化（环境变量迁移）、进程管理优化（AnalysisManager 重写）。

</domain>

<decisions>
## Implementation Decisions

### Database Migration
- **D-01:** 继续使用 SQLite + WAL 模式，启用 WAL 模式提升并发性能
- **D-02:** 全部 raw SQL 查询迁移到 Django ORM，消除 SQL 注入风险
- **D-03:** 使用 Django 默认连接管理，简单可靠
- **D-04:** 完全移除 `g_dbLock`，依赖 SQLite WAL 模式和 Django ORM 连接管理

### Model Layer
- **D-05:** 使用 BaseModel mixin（继承 Model 并重写 save/delete），统一处理模型持久化逻辑
- **D-06:** 不需要数据迁移脚本，只有测试用户，直接重建数据库
- **D-07:** 使用 `django-fernet-fields` 加密敏感字段（`pull_stream_password`、`api_key`）
- **D-08:** 创建 `BaseModel(Model)` 类，所有模型继承它，消除重复的 save()/delete() 方法

### Configuration Security
- **D-09:** 使用环境变量 + .env 文件管理敏感配置
- **D-10:** 使用 `threading.RLock` 保护配置读写，实现线程安全的热重载
- **D-11:** 仅迁移敏感值（SECRET_KEY、safe key、media secret、SIP password）
- **D-12:** .env 文件放在项目根目录（`D:\projects\AI4Video\.env`）

### Process Management
- **D-13:** 完全重写 AnalysisManager，使用 `concurrent.futures` 替换 `multiprocessing`
- **D-14:** 使用 `ThreadPoolExecutor`，适合 I/O 密集型视频分析任务
- **D-15:** 信号处理器 + 超时的优雅关闭策略（注册 SIGTERM/SIGINT，设置超时强制关闭）
- **D-16:** 定期心跳检查 Worker 健康，检测超时并替换无响应的 Worker

### the agent's Discretion
- 模型层重构的具体实现细节
- AnalysisManager 重写的状态管理简化策略
- 配置热重载的具体锁粒度

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 核心文件
- `app/utils/Database.py` — 全局锁 `g_dbLock`，raw SQL 查询
- `app/models.py` — 重复的 save()/delete() 方法
- `app/analysis/manager.py` — AnalysisManager 单例，multiprocessing 使用
- `app/analysis/pipeline.py` — CameraPipeline，进程间通信
- `framework/settings.py` — SECRET_KEY, DATABASES 配置
- `config.json` — 敏感配置值

### 参考文档
- `.planning/UPGRADE_PLAN.md` — Phase 3 完整升级方案
- `.planning/codebase/ARCHITECTURE.md` — 架构分析（组件职责、入口点）
- `.planning/codebase/CONCERNS.md` — 已知问题（全局锁、raw SQL、模型重复）
- `.planning/phases/02-onnx-fix/02-CONTEXT.md` — Phase 2 决策（algorithm_type 自动检测）

### 需要修改的文件
- `app/utils/Database.py` — 移除 `g_dbLock`，启用 WAL 模式
- `app/models.py` — 创建 BaseModel，重构所有模型
- `app/views/StreamView.py` — raw SQL 迁移到 ORM
- `app/views/LLMView.py` — raw SQL 迁移到 ORM
- `app/views/ViewsBase.py` — raw SQL 迁移到 ORM
- `app/analysis/manager.py` — AnalysisManager 重写
- `framework/settings.py` — SECRET_KEY 从环境变量读取
- `config.json` — 敏感值迁移到 .env
- `.env` — 新建敏感配置文件

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/utils/Database.py` — 数据库连接管理，可复用连接逻辑
- `app/models.py` — 现有模型定义，可复用字段和关系
- `app/analysis/manager.py` — AnalysisManager 核心逻辑，可复用分析流程
- `app/analysis/pipeline.py` — CameraPipeline 状态管理，可复用管道逻辑

### Established Patterns
- 所有视图使用 `from app.views.ViewsBase import *` 通配导入
- 配置通过 `g_config` 全局单例访问
- JSON 响应统一使用 `f_responseJson()` 返回
- 错误处理使用 `logger.warning()` 记录

### Integration Points
- `app/urls.py` — 路由配置
- `app/middleware.py` — 认证中间件
- `app/apps.py` — 应用启动逻辑

</code_context>

<specifics>
## Specific Ideas

无特殊要求 — 采用标准架构升级方法。

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 3-架构升级*
*Context gathered: 2026-08-08*
