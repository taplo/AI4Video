# Phase 3: 架构升级 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-08
**Phase:** 3-架构升级
**Areas discussed:** Database Migration, Model Layer, Configuration Security, Process Management

---

## Database Migration

| Option | Description | Selected |
|--------|-------------|----------|
| 继续 SQLite + WAL 模式 | 启用 WAL 模式，移除全局锁，使用 Django ORM connection pooling。适合单机部署，风险最低 | ✓ |
| 迁移到 PostgreSQL | 完整迁移到 PostgreSQL，支持并发读写。需要额外安装和配置 | |
| 迁移到 MySQL | 完整迁移到 MySQL。需要额外安装和配置 | |

**User's choice:** 继续 SQLite + WAL 模式 (Recommended)
**Notes:** 适合单机部署，风险最低

---

| Option | Description | Selected |
|--------|-------------|----------|
| 全部迁移到 ORM | 消除所有 raw SQL，统一使用 Django ORM。更安全，更易维护 | ✓ |
| 渐进式迁移 | 先迁移高风险的查询（StreamView、LLMView），其他后续处理 | |
| 保留关键查询 | 只迁移有 SQL 注入风险的查询，其他保持原样 | |

**User's choice:** 全部迁移到 ORM (Recommended)
**Notes:** 消除 SQL 注入风险，统一数据访问模式

---

| Option | Description | Selected |
|--------|-------------|----------|
| Django 默认连接管理 | 使用 Django 内置的数据库连接管理，启用 WAL 模式。简单可靠 | ✓ |
| 自定义连接池 | 实现自定义连接池（如 pgbouncer 风格）。更复杂，但控制更精细 | |

**User's choice:** Django 默认连接管理 (Recommended)
**Notes:** 简单可靠，适合 SQLite

---

| Option | Description | Selected |
|--------|-------------|----------|
| 完全移除 | 完全移除 g_dbLock，依赖 SQLite WAL 模式和 Django ORM 的连接管理 | ✓ |
| 保留但缩小范围 | 只在写操作时使用锁，读操作不加锁 | |

**User's choice:** 完全移除 (Recommended)
**Notes:** 依赖 WAL 模式和 Django ORM

---

## Model Layer

| Option | Description | Selected |
|--------|-------------|----------|
| BaseModel Mixin | 创建 BaseModel mixin，统一处理 save()/delete() 逻辑，所有模型继承它 | ✓ |
| 全局 Model 重写 | 重写 Django 的 Model 基类，添加自定义 save()/delete() | |
| 保持原样 | 不重构模型层，只移除 g_dbLock | |

**User's choice:** BaseModel Mixin (Recommended)
**Notes:** 统一处理模型持久化逻辑

---

| Option | Description | Selected |
|--------|-------------|----------|
| 不需要 | 只有测试用户，直接重建数据库即可 | ✓ |
| 需要迁移脚本 | 编写 Django migrations 处理模型变更 | |

**User's choice:** 不需要 (Recommended)
**Notes:** 只有测试用户，直接重建

---

| Option | Description | Selected |
|--------|-------------|----------|
| 使用 django-fernet-fields 加密 | 加密敏感字段（pull_stream_password、api_key），保持向后兼容 | ✓ |
| 暂时保留 | 不在本次升级中处理，留到 Phase 4 安全加固 | |

**User's choice:** 使用 django-fernet-fields 加密 (Recommended)
**Notes:** 加密敏感字段，保持向后兼容

---

| Option | Description | Selected |
|--------|-------------|----------|
| 继承 Model 并重写 save/delete | 创建 BaseModel(Model) 类，重写 save()/delete()，所有模型继承它 | ✓ |
| 使用 Mixin 类 | 创建 BaseModelMixin 类，通过多重继承使用 | |

**User's choice:** 继承 Model 并重写 save/delete (Recommended)
**Notes:** 简单直接，所有模型继承 BaseModel

---

## Configuration Security

| Option | Description | Selected |
|--------|-------------|----------|
| 环境变量 + .env 文件 | 使用 python-dotenv 加载 .env 文件，敏感值从环境变量读取 | ✓ |
| Django Settings + .env | 使用 django-environ 管理配置，敏感值从环境变量读取 | |
| 保持 JSON 但加密 | 敏感值在 JSON 中加密存储，运行时解密 | |

**User's choice:** 环境变量 + .env 文件 (Recommended)
**Notes:** 简单直接，使用 python-dotenv

---

| Option | Description | Selected |
|--------|-------------|----------|
| threading.RLock | 使用可重入锁保护配置读写，简单可靠 | ✓ |
| copy-on-write | 读取配置时创建副本，修改时替换整个对象。无锁但内存开销大 | |

**User's choice:** threading.RLock (Recommended)
**Notes:** 简单可靠，适合配置热重载

---

| Option | Description | Selected |
|--------|-------------|----------|
| 仅敏感值 | 只迁移 SECRET_KEY、safe key、media secret、SIP password 等敏感值 | ✓ |
| 所有可配置项 | 将所有 config.json 中的值都迁移到环境变量 | |

**User's choice:** 仅敏感值 (Recommended)
**Notes:** 只迁移敏感配置

---

| Option | Description | Selected |
|--------|-------------|----------|
| 项目根目录 | 放在 D:\projects\AI4Video\.env，与 manage.py 同级 | ✓ |
| config/ 目录 | 放在 D:\projects\AI4Video\config\.env | |

**User's choice:** 项目根目录 (Recommended)
**Notes:** 与 manage.py 同级，方便管理

---

## Process Management

| Option | Description | Selected |
|--------|-------------|----------|
| 完全重写 | 完全重写 AnalysisManager，使用 concurrent.futures 替换 multiprocessing，简化状态管理 | ✓ |
| 渐进式优化 | 保持现有架构，只添加优雅关闭和健康检查 | |

**User's choice:** 完全重写 (Recommended)
**Notes:** 使用 concurrent.futures 替换 multiprocessing

---

| Option | Description | Selected |
|--------|-------------|----------|
| ThreadPoolExecutor | 使用 ThreadPoolExecutor，适合 I/O 密集型任务，简单可靠 | ✓ |
| ProcessPoolExecutor | 使用 ProcessPoolExecutor，适合 CPU 密集型任务，但进程间通信复杂 | |

**User's choice:** ThreadPoolExecutor (Recommended)
**Notes:** 适合 I/O 密集型视频分析任务

---

| Option | Description | Selected |
|--------|-------------|----------|
| 信号处理器 + 超时 | 注册 SIGTERM/SIGINT 处理器，设置超时时间，超时后强制关闭 | ✓ |
| 仅信号处理器 | 只注册信号处理器，不设置超时 | |

**User's choice:** 信号处理器 + 超时 (Recommended)
**Notes:** 优雅关闭，超时强制关闭

---

| Option | Description | Selected |
|--------|-------------|----------|
| 定期心跳检查 | Worker 定期发送心跳，Manager 检测超时并替换无响应的 Worker | ✓ |
| 任务完成时检查 | 只在任务完成时检查 Worker 状态 | |

**User's choice:** 定期心跳检查 (Recommended)
**Notes:** 实时检测 Worker 健康状态

---

## the agent's Discretion

- 模型层重构的具体实现细节
- AnalysisManager 重写的状态管理简化策略
- 配置热重载的具体锁粒度

## Deferred Ideas

None — discussion stayed within phase scope
