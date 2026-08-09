# Phase 06: other-upgrades - Context

**Gathered:** 2026-08-09
**Status:** Ready for planning

<domain>
## Phase Boundary

依赖升级和功能增强：
- 升级 Django 5.0→5.2 及其他依赖（opencv, torch, ultralytics, onnxruntime）
- 实现 manage.py migrate 自动运行
- 添加请求限流（django-ratelimit）
- 实现审计日志（认证+数据修改）
- 优化前端静态资源（django-compress）
- 集成 OpenAPI/Swagger 文档（drf-spectacular）

</domain>

<decisions>
## Implementation Decisions

### Django升级策略
- **D-01:** 直接升级到 Django 5.2 LTS，不逐步升级
- **D-02:** 所有依赖使用精确版本固定（django==5.2.1 等）
- **D-03:** 全部依赖升级到最新稳定版（opencv, torch, ultralytics, onnxruntime）
- **D-04:** 升级后运行现有测试套件验证（135个测试）

### 请求限流配置
- **D-05:** 按 IP 维度限流
- **D-06:** 限流阈值 200次/分钟
- **D-07:** 所有 API 端点限流（排除 /inner/ 内部API）
- **D-08:** 触发限流返回 HTTP 429 + JSON 错误
- **D-09:** 使用 django-ratelimit 库
- **D-10:** 登录用户和匿名用户相同比例限流

### 审计日志范围
- **D-11:** 记录认证事件（登录/登出/失败）和数据修改事件
- **D-12:** 审计日志存储在数据库表中
- **D-13:** 审计日志保留 1年
- **D-14:** 记录字段：用户、IP、时间、操作、结果

### OpenAPI文档框架
- **D-15:** 使用 drf-spectacular 框架（支持 OpenAPI 3.0）
- **D-16:** 生成详细文档（描述、示例、错误码）
- **D-17:** 仅开发环境可访问（生产环境不暴露）
- **D-18:** 使用 Swagger UI 界面

### Migrate自动运行
- **D-19:** 每次 manage.py 启动时自动运行 migrate
- **D-20:** 在 manage.py 中实现，不在 AppConfig.ready()

### 前端资源优化
- **D-21:** 使用 django-compress 压缩 CSS/JS
- **D-22:** 基本压缩级别（去除空白和注释）
- **D-23:** 不使用 CDN（适合内网部署）
- **D-24:** 使用文件哈希进行缓存破坏

### the agent's Discretion
- 前端静态资源优化的具体实现方式由 agent 决定
- 审计日志模型的字段类型由 agent 决定
- OpenAPI 文档的 Schema 生成方式由 agent 决定

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Django升级
- `requirements.txt` — 当前依赖列表
- `framework/settings.py` — Django配置文件

### 请求限流
- `app/middleware.py` — 现有中间件结构
- `app/urls.py` — URL路由定义

### 审计日志
- `app/models.py` — 现有模型结构

### OpenAPI文档
- `app/views/` — 现有视图结构

No external specs — requirements fully captured in decisions above

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/middleware.py`: SimpleMiddleware 可扩展用于限流
- `app/utils/Database.py`: 数据库操作工具类
- `framework/settings.py`: Django配置管理

### Established Patterns
- 中间件模式：所有请求经过 SimpleMiddleware 处理
- 视图模式：所有视图继承 ViewsBase
- 配置模式：使用环境变量 + .env 文件

### Integration Points
- `app/middleware.py`: 添加限流中间件
- `app/models.py`: 添加审计日志模型
- `framework/settings.py`: 添加 drf-spectacular 配置
- `manage.py`: 添加 migrate 自动运行逻辑

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-other-upgrades*
*Context gathered: 2026-08-09*
