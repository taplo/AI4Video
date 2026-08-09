# AI4Video Roadmap

**Created:** 2026-08-05
**Last Updated:** 2026-08-09
**Status:** Active

## Project Overview

AI4Video 是一个基于 Django 的视频分析平台，集成 ONNX/YOLO 推理引擎和 ZLMediaKit 流媒体服务器。本路线图规划从 rebucca 重命名到工程化升级的完整改造。

---

## Phase Overview

| # | Name | Status | Dependencies |
|---|------|--------|--------------|
| 01 | rename-cleanup | ✓ complete | — |
| 02 | onnx-fix | ✓ complete | — |
| 03 | architecture-upgrade | ✓ complete | Phase 04 |
| 04 | engineering-hardening | ✓ complete | Phase 01 |
| 05 | test-infrastructure | ○ pending | Phase 03 |
| 06 | other-upgrades | ○ pending | Phase 03 |

---

## Phase 01: rename-cleanup

**Goal:** 项目重命名 rebucca → AI4Video，移除自动升级检测功能

**Scope:**
- 删除 VersionView 和自动升级检测代码
- 全局重命名 rebucca → AI4Video（配置、二进制、前端、数据库）
- 清理语言文件中的升级相关 key

**Status:** ✓ complete

---

## Phase 02: onnx-fix

**Goal:** 修复 ONNX 模型上传后检测报错问题

**Scope:**
- 自动检测 algorithm_type（通过分析 ONNX 模型输出 shape）
- 增加输入尺寸不匹配时的自动 resize
- 增加输出 shape 与 algorithm_type 不匹配时的自动降级逻辑

**Status:** ✓ complete

---

## Phase 03: architecture-upgrade

**Goal:** 架构升级，消除全局锁，迁移到 Django ORM

**Scope:**
- 将全局 `g_dbLock` 替换为 Django ORM connection pooling
- 将所有 raw SQL 查询迁移到 Django ORM
- 实现 `BaseModel` mixin 消除重复的 `save()`/`delete()` 方法
- 将 config.json 敏感值迁移到环境变量
- 实现配置热重载的线程安全机制
- 将 AnalysisManager 的 multiprocessing 改为基于 `concurrent.futures` 的进程池
- 实现优雅关闭信号处理

**Dependencies:** Phase 04 (先完成工程化改造)

**Status:** ✓ complete

---

## Phase 04: engineering-hardening

**Goal:** 工程化改造，安全加固、异常处理、系统保活

**Scope:**
- 认证绕过修复、DEBUG 模式环境变量控制、ALLOWED_HOSTS 可配置
- 点击劫持防护、CSRF 豁免移除、路径遍历防护
- 结构化错误响应（统一 JSON 格式）
- 数据库连接失败重试机制
- OOM 保护和内存监控
- `/api/health` 端点
- MediaServerManager 自动重启
- Worker 健康检查和自动替换
- Cron-style 数据库备份

**Dependencies:** Phase 01

**Status:** ✓ complete

---

## Phase 05: test-infrastructure

**Goal:** 测试体系建设，建立 pytest 框架和测试用例

**Scope:**
- 建立 `pytest` 测试框架
- 创建 `conftest.py`、`pytest.ini`、`tests/` 目录
- 创建测试用例：
  - `test_auth.py` — 认证、登录、captcha、brute-force protection
  - `test_stream.py` — 流管理 CRUD、代理创建
  - `test_algorithm.py` — 算法模型 CRUD、引擎工厂
  - `test_onnx_engine.py` — ONNX 加载、推理、后处理
  - `test_analysis_pipeline.py` — 分析流水线生命周期
  - `test_middleware.py` — 中间件认证逻辑
  - `test_api.py` — API 端点集成测试
  - `test_config.py` — 配置管理、热重载
- 配置 GitHub Actions CI（自动运行测试、lint、类型检查）

**Dependencies:** Phase 03 (架构升级完成后才能编写测试)

**Status:** ○ pending

---

## Phase 06: other-upgrades

**Goal:** 依赖升级和功能增强

**Scope:**
- 依赖升级：
  - Django 5.0.4 → 5.2+
  - opencv-python 4.10.0.84 → 最新稳定版
  - torch >=2.0.0 → 最新稳定版
  - ultralytics >=8.0.0 → 最新稳定版
  - onnxruntime 1.19.2 → 最新稳定版
- 功能增强：
  - `manage.py` 的 `migrate` 命令自动运行
  - 请求限流（`django-ratelimit`）
  - 审计日志（记录所有认证尝试和数据修改）
  - 优化前端静态资源（压缩 CSS/JS）
  - OpenAPI/Swagger API 文档

**Dependencies:** Phase 03

**Plans:** 3 plans

Plans:
- [ ] 06-01-PLAN.md — 依赖升级、自动迁移、AuditLog 模型
- [ ] 06-02-PLAN.md — 限流中间件、审计中间件、OpenAPI、静态压缩
- [ ] 06-03-PLAN.md — 集成测试、全量回归验证

**Status:** ○ pending

---

## Execution Order

```
Phase 01 (rename-cleanup) ─────┐
                                ├─→ Phase 04 (engineering-hardening) ─→ Phase 03 (architecture-upgrade) ─┬─→ Phase 05 (test-infrastructure)
Phase 02 (onnx-fix) ───────────┘                                                                        └─→ Phase 06 (other-upgrades)
```

**建议：** Phase 01-04 已完成。接下来执行 Phase 05（测试体系建设），然后 Phase 06（依赖升级）。

---

*Last updated: 2026-08-09*
