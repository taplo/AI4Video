# AI4Video Project

**Last Updated:** 2026-08-12 after v1.0 milestone

## What This Is

AI4Video 是一个基于 Django 的视频分析平台，集成 ONNX/YOLO 推理引擎和 ZLMediaKit 流媒体服务器。

## Core Value

提供易用的 AI 视频分析能力，支持多种检测算法，通过 Web 界面管理视频流和分析结果。

## Requirements

### Validated

- ✓ 项目重命名 rebucca → AI4Video — v1.0
- ✓ ONNX 模型自动检测和输入自动 resize — v1.0
- ✓ 安全加固（认证绕过修复、DEBUG 环境控制、CSRF） — v1.0
- ✓ 测试体系建设（448 测试，pytest 框架） — v1.0
- ✓ 依赖升级（Django 5.2.17） — v1.0
- ✓ 审计日志和请求限流 — v1.0
- ✓ OpenAPI/Swagger API 文档 — v1.0
- ✓ 覆盖率门槛（30%） — v1.0
- ✓ CI 迁移漂移检查 — v1.0

### Active

- [ ] 提高测试覆盖率（目标 60%）
- [ ] GB28181 SIP 协议完善
- [ ] StreamView WebSocket 优化
- [ ] 性能监控和告警
- [ ] 多语言支持完善

### Out of Scope

- 移动端 APP — Web-first approach
- 云端部署 — 本地部署为主
- 实时视频流分析 — 使用 ZLMediaKit

## Context

Shipped v1.0 with 15,952 lines added across 115 files.
Tech stack: Django 5.2.17, ONNX Runtime, ZLMediaKit, SQLite (WAL mode).
Test coverage: 30% (448 tests passing).
CI: GitHub Actions with coverage gate and migration drift check.

## Key Decisions

| Decision | Outcome | Status |
|----------|---------|--------|
| Use pytest over Django TestCase | Better fixtures, mocking | ✓ Good |
| SQLite WAL mode | Concurrent read/write | ✓ Good |
| Environment variables for secrets | Security baseline | ✓ Good |
| Coverage threshold 29% | Hardware-dependent modules untestable | ⚠️ Revisit |
| makemigrations --check in CI | Migration drift prevention | ✓ Good |

## Constraints

- Hardware-dependent modules (GPU, SIP, ZLMediaKit) cannot be meaningfully mocked in CI
- GB28181SipServer requires SIP hardware for testing
- StreamView WebSocket complexity limits test coverage

---
*Last updated: 2026-08-12 after v1.0 milestone*
