# Phase 06: other-upgrades - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-09
**Phase:** 06-other-upgrades
**Areas discussed:** Django升级策略, 请求限流配置, 审计日志范围, OpenAPI文档框架, Migrate自动运行, 前端资源优化

---

## Django升级策略

| Option | Description | Selected |
|--------|-------------|----------|
| 直接升级到5.2（推荐） | 5.2是LTS版本，长期支持，直接升级最简单 | ✓ |
| 逐步升级5.0→5.1→5.2 | 分步升级，每步验证，更安全但耗时 | |
| 你决定 | 根据代码库情况选择最合适的策略 | |

**User's choice:** 直接升级到5.2（推荐）
**Notes:** 5.2是LTS版本，长期支持

---

| Option | Description | Selected |
|--------|-------------|----------|
| 精确版本（推荐） | django==5.2.1，确保可重现构建 | ✓ |
| 兼容范围 | django>=5.2,<6.0，允许补丁升级 | |
| 你决定 | 根据项目需求选择 | |

**User's choice:** 精确版本（推荐）
**Notes:** 确保可重现构建

---

| Option | Description | Selected |
|--------|-------------|----------|
| 全部升级到最新稳定版（推荐） | 一次性升级所有依赖到最新稳定版 | ✓ |
| 只升级必需的 | 只升级有已知问题的依赖 | |
| 你决定 | 根据兼容性测试结果决定 | |

**User's choice:** 全部升级到最新稳定版（推荐）
**Notes:** 一次性升级所有依赖

---

| Option | Description | Selected |
|--------|-------------|----------|
| 运行现有测试套件（推荐） | 运行pytest，确保135个测试全部通过 | ✓ |
| 手动功能测试 | 手动测试关键功能（登录、流管理、分析） | |
| 两者都做 | 自动化测试+手动验证关键路径 | |

**User's choice:** 运行现有测试套件（推荐）
**Notes:** 135个测试全部通过即可

---

## 请求限流配置

| Option | Description | Selected |
|--------|-------------|----------|
| 按IP（推荐） | 简单有效，防止恶意请求，不需要用户系统 | ✓ |
| 按用户 | 需要登录用户，更精确但复杂 | |
| 按API-key | 适合API调用场景，需要key管理 | |
| 你决定 | 根据项目需求选择 | |

**User's choice:** 按IP（推荐）
**Notes:** 简单有效，不需要用户系统

---

| Option | Description | Selected |
|--------|-------------|----------|
| 100次/分钟（推荐） | 适合一般Web应用，平衡安全性和可用性 | |
| 50次/分钟 | 更严格，适合高安全场景 | |
| 200次/分钟 | 更宽松，适合内部系统 | ✓ |
| 你决定 | 根据实际需求设定 | |

**User's choice:** 200次/分钟
**Notes:** 适合内部系统

---

| Option | Description | Selected |
|--------|-------------|----------|
| 所有API端点（推荐） | 全面保护，包括登录、流管理、算法等 | ✓ |
| 仅认证端点 | 只保护登录、注册等敏感端点 | |
| 排除健康检查 | 所有端点限流，但排除/api/health | |
| 你决定 | 根据安全需求选择 | |

**User's choice:** 所有API端点（推荐）
**Notes:** 全面保护

---

| Option | Description | Selected |
|--------|-------------|----------|
| 429 + JSON错误（推荐） | 标准HTTP 429状态码，返回JSON错误信息 | ✓ |
| 429 + HTML页面 | 返回HTML错误页面，适合浏览器访问 | |
| 你决定 | 根据客户端类型选择 | |

**User's choice:** 429 + JSON错误（推荐）
**Notes:** 标准HTTP 429

---

| Option | Description | Selected |
|--------|-------------|----------|
| django-ratelimit（推荐） | ROADMAP中指定的库，简单易用 | ✓ |
| djangorestframework-throttling | 如果使用DRF，集成更好 | |
| 你决定 | 根据技术栈选择 | |

**User's choice:** django-ratelimit（推荐）
**Notes:** ROADMAP中指定的库

---

| Option | Description | Selected |
|--------|-------------|----------|
| 不限流（推荐） | 内部API由ZLM等服务调用，限流会影响正常工作 | ✓ |
| 也限流 | 统一限流策略，防止内部服务异常 | |
| 你决定 | 根据架构需求选择 | |

**User's choice:** 不限流（推荐）
**Notes:** 内部API不限流

---

| Option | Description | Selected |
|--------|-------------|----------|
| 相同比例（推荐） | 简化实现，统一200次/分钟 | ✓ |
| 登录用户更宽松 | 登录用户500次/分钟，匿名100次/分钟 | |
| 你决定 | 根据用户群体选择 | |

**User's choice:** 相同比例（推荐）
**Notes:** 简化实现

---

## 审计日志范围

| Option | Description | Selected |
|--------|-------------|----------|
| 认证+数据修改（推荐） | 记录登录/登出、数据增删改，平衡安全性和性能 | ✓ |
| 仅认证事件 | 只记录登录/登出/失败，最小化日志量 | |
| 所有操作 | 记录所有API调用，最全面但性能影响大 | |
| 你决定 | 根据安全需求选择 | |

**User's choice:** 认证+数据修改（推荐）
**Notes:** 平衡安全性和性能

---

| Option | Description | Selected |
|--------|-------------|----------|
| 数据库表（推荐） | Django ORM管理，方便查询和导出 | ✓ |
| 文件日志 | 写入文件，性能更好但查询不便 | |
| 两者都存 | 数据库+文件，双保险但复杂 | |
| 你决定 | 根据查询需求选择 | |

**User's choice:** 数据库表（推荐）
**Notes:** 方便查询和导出

---

| Option | Description | Selected |
|--------|-------------|----------|
| 永久保留（推荐） | 简单，不需要清理逻辑，适合中小规模 | |
| 90天 | 定期清理，节省存储空间 | |
| 1年 | 平衡安全和存储 | ✓ |
| 你决定 | 根据合规需求选择 | |

**User's choice:** 1年
**Notes:** 平衡安全和存储

---

| Option | Description | Selected |
|--------|-------------|----------|
| 用户+IP+时间+操作+结果（推荐） | 记录who/when/where/what/outcome，满足基本审计需求 | ✓ |
| 加上请求详情 | 额外记录请求参数和响应码，更详细但存储大 | |
| 你决定 | 根据审计需求选择 | |

**User's choice:** 用户+IP+时间+操作+结果（推荐）
**Notes:** 满足基本审计需求

---

## OpenAPI文档框架

| Option | Description | Selected |
|--------|-------------|----------|
| drf-spectacular（推荐） | 现代、维护活跃、支持OpenAPI 3.0，与DRF集成好 | ✓ |
| drf-yasg | 老牌、稳定，但只支持Swagger 2.0 | |
| 你决定 | 根据技术栈选择 | |

**User's choice:** drf-spectacular（推荐）
**Notes:** 现代、维护活跃

---

| Option | Description | Selected |
|--------|-------------|----------|
| 基本文档（推荐） | 自动生成端点、参数、响应，足够日常使用 | |
| 详细文档 | 添加描述、示例、错误码说明 | ✓ |
| 你决定 | 根据API复杂度选择 | |

**User's choice:** 详细文档
**Notes:** 添加描述、示例、错误码说明

---

| Option | Description | Selected |
|--------|-------------|----------|
| 仅开发环境（推荐） | 生产环境不暴露API文档，安全考虑 | ✓ |
| 所有环境 | 方便调试，但有安全风险 | |
| 需要认证 | 登录后可访问，平衡安全和便利 | |
| 你决定 | 根据安全需求选择 | |

**User's choice:** 仅开发环境（推荐）
**Notes:** 生产环境不暴露

---

| Option | Description | Selected |
|--------|-------------|----------|
| Swagger UI（推荐） | 交互式测试，开发者熟悉 | ✓ |
| Redoc | 更美观，但交互性差 | |
| 两者都提供 | 两个URL，满足不同需求 | |
| 你决定 | 根据使用场景选择 | |

**User's choice:** Swagger UI（推荐）
**Notes:** 交互式测试

---

## Migrate自动运行

| Option | Description | Selected |
|--------|-------------|----------|
| 每次启动时（推荐） | 确保数据库schema始终最新 | ✓ |
| 仅开发环境 | 生产环境手动执行，更安全 | |
| 你决定 | 根据部署策略选择 | |

**User's choice:** 每次启动时（推荐）
**Notes:** 确保数据库schema始终最新

---

| Option | Description | Selected |
|--------|-------------|----------|
| manage.py启动时（推荐） | 在manage.py中添加migrate命令 | ✓ |
| Django AppConfig.ready() | 在应用启动时执行 | |
| 你决定 | 根据项目结构选择 | |

**User's choice:** manage.py启动时（推荐）
**Notes:** 在manage.py中实现

---

## 前端资源优化

| Option | Description | Selected |
|--------|-------------|----------|
| django-compress（推荐） | Django原生支持，简单易用 | ✓ |
| django-webpack-loader | Webpack集成，功能强大但复杂 | |
| 你决定 | 根据项目复杂度选择 | |

**User's choice:** django-compress（推荐）
**Notes:** Django原生支持

---

| Option | Description | Selected |
|--------|-------------|----------|
| 基本压缩（推荐） | 去除空白和注释，平衡大小和性能 | ✓ |
| 深度压缩 | 变量名替换、死代码消除，更小但可能有风险 | |
| 你决定 | 根据性能需求选择 | |

**User's choice:** 基本压缩（推荐）
**Notes:** 去除空白和注释

---

| Option | Description | Selected |
|--------|-------------|----------|
| 不使用CDN（推荐） | 保持简单，适合内网部署 | ✓ |
| 使用CDN | 加速静态资源加载，但增加复杂度 | |
| 你决定 | 根据部署环境选择 | |

**User's choice:** 不使用CDN（推荐）
**Notes:** 适合内网部署

---

| Option | Description | Selected |
|--------|-------------|----------|
| 文件哈希（推荐） | 文件名添加版本哈希，自动失效旧缓存 | ✓ |
| 时间戳查询参数 | URL添加?v=timestamp，简单但不优雅 | |
| 你决定 | 根据部署策略选择 | |

**User's choice:** 文件哈希（推荐）
**Notes:** 自动失效旧缓存

---

## the agent's Discretion

- 前端静态资源优化的具体实现方式由 agent 决定
- 审计日志模型的字段类型由 agent 决定
- OpenAPI 文档的 Schema 生成方式由 agent 决定

## Deferred Ideas

None — discussion stayed within phase scope
