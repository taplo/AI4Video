# Phase 4: 工程化改造 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-09
**Phase:** 4-工程化改造
**Areas discussed:** 安全加固策略, 错误响应格式, 健康检查设计, 数据库备份

---

## 安全加固策略

| Option | Description | Selected |
|--------|-------------|----------|
| 一次性全部修复 | 在一个计划中修复所有8个漏洞，确保安全基线完整 | ✓ |
| 按风险分级修复 | 先修复高危（认证绕过、SQL注入），再修复中低危 | |
| 你决定 | 根据代码分析选择最合理的方案 | |

**User's choice:** 一次性全部修复 (Recommended)
**Notes:** 用户希望一次性修复所有安全漏洞，确保安全基线完整

---

| Option | Description | Selected |
|--------|-------------|----------|
| 环境变量控制 | DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true' | ✓ |
| .env 文件控制 | 在 .env 中设置 DEBUG=True/False | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 环境变量控制 (Recommended)
**Notes:** 使用环境变量控制 DEBUG 模式，便于不同环境配置

---

| Option | Description | Selected |
|--------|-------------|----------|
| 环境变量配置 | ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',') | ✓ |
| 保持通配符 * | ALLOWED_HOSTS = ['*'] 保持现状 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 环境变量配置 (Recommended)
**Notes:** 使用环境变量配置 ALLOWED_HOSTS，便于不同环境配置

---

| Option | Description | Selected |
|--------|-------------|----------|
| 完全移除 | 移除 yuturuishi.com 的遥测代码，不发送任何外部数据 | ✓ |
| 改为 opt-in | 默认禁用，用户可在设置中启用 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 完全移除 (Recommended)
**Notes:** 用户希望完全移除外部遥测代码，不发送任何外部数据

---

| Option | Description | Selected |
|--------|-------------|----------|
| 移除 @csrf_exempt | LLMView 的测试接口需要 CSRF token，更安全 | ✓ |
| 保留豁免 | LLM 测试接口保持豁免，方便调试 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 移除 @csrf_exempt (Recommended)
**Notes:** 用户希望移除 CSRF 豁免，要求所有请求提供 CSRF token

---

## 错误响应格式

| Option | Description | Selected |
|--------|-------------|----------|
| {code, msg, detail, timestamp} | 标准 REST API 错误格式，包含错误码、消息、详情、时间戳 | ✓ |
| {error, message, path, status} | 类似 Express.js 的错误格式 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** {code, msg, detail, timestamp} (Recommended)
**Notes:** 用户选择标准 REST API 错误格式

---

| Option | Description | Selected |
|--------|-------------|----------|
| HTTP 状态码 + 业务码 | 如 400 + 1001（参数错误）、401 + 2001（认证失败） | ✓ |
| 纯 HTTP 状态码 | 只使用 400/401/403/404/500 等标准状态码 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** HTTP 状态码 + 业务码 (Recommended)
**Notes:** 用户选择 HTTP 状态码 + 业务码的组合设计

---

| Option | Description | Selected |
|--------|-------------|----------|
| 指数退避重试 3 次 | 1s, 2s, 4s 重试，超过则返回 503 | ✓ |
| 固定间隔重试 5 次 | 每秒重试一次，最多 5 次 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 指数退避重试 3 次 (Recommended)
**Notes:** 用户选择指数退避重试策略，平衡重试效果和性能开销

---

| Option | Description | Selected |
|--------|-------------|----------|
| 内存监控 + 自动重启 | 定期检查内存使用，超过阈值自动重启 worker | ✓ |
| 仅日志警告 | 只记录内存使用情况，不自动处理 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 内存监控 + 自动重启 (Recommended)
**Notes:** 用户选择内存监控 + 自动重启的 OOM 保护策略

---

## 健康检查设计

| Option | Description | Selected |
|--------|-------------|----------|
| DB + ZLMediaKit + 分析引擎 | 检查数据库连接、流媒体服务、AI推理引擎状态 | ✓ |
| 仅 DB + ZLMediaKit | 只检查数据库和流媒体服务 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** DB + ZLMediaKit + 分析引擎 (Recommended)
**Notes:** 用户希望检查所有关键组件的状态

---

| Option | Description | Selected |
|--------|-------------|----------|
| 每 30 秒 | 平衡实时性和性能开销 | ✓ |
| 每 60 秒 | 更低的性能开销 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 每 30 秒 (Recommended)
**Notes:** 用户选择 30 秒间隔，平衡实时性和性能开销

---

| Option | Description | Selected |
|--------|-------------|----------|
| 检测到崩溃后自动重启 | 监控进程状态，崩溃后自动重启并记录日志 | ✓ |
| 仅日志警告 | 只记录 ZLMediaKit 崩溃，不自动重启 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 检测到崩溃后自动重启 (Recommended)
**Notes:** 用户希望 ZLMediaKit 崩溃后自动重启

---

| Option | Description | Selected |
|--------|-------------|----------|
| 心跳检测 + 自动替换 | 定期检查 worker 心跳，超时则替换无响应的 worker | ✓ |
| 仅日志警告 | 只记录 worker 状态，不自动处理 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 心跳检测 + 自动替换 (Recommended)
**Notes:** 用户希望 worker 心跳检测 + 自动替换策略

---

## 数据库备份

| Option | Description | Selected |
|--------|-------------|----------|
| 定时任务 | 使用 APScheduler 或类似库实现 cron-style 定时备份 | ✓ |
| 手动触发 | 提供管理命令手动执行备份 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 定时任务 (Recommended)
**Notes:** 用户选择定时任务自动触发备份

---

| Option | Description | Selected |
|--------|-------------|----------|
| 每天凌晨 2 点 | 在低峰期执行备份，减少对系统影响 | ✓ |
| 每小时 | 更频繁的备份，但增加 I/O 开销 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 每天凌晨 2 点 (Recommended)
**Notes:** 用户选择每天凌晨 2 点执行备份

---

| Option | Description | Selected |
|--------|-------------|----------|
| 保留最近 7 天 | 保留 7 天的备份，超过自动删除 | ✓ |
| 保留最近 30 天 | 保留 30 天的备份，更长的历史记录 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 保留最近 7 天 (Recommended)
**Notes:** 用户选择保留 7 天的备份

---

| Option | Description | Selected |
|--------|-------------|----------|
| 项目目录 backups/ | 在项目根目录下创建 backups/ 目录存储备份文件 | ✓ |
| 外部存储 | 备份到外部存储或云存储 | |
| 你决定 | 选择最合适的方案 | |

**User's choice:** 项目目录 backups/ (Recommended)
**Notes:** 用户选择在项目目录下存储备份文件

---

## the agent's Discretion

- 安全漏洞修复的具体实现顺序
- 错误码的具体数值分配
- 健康检查的具体实现细节
- 备份脚本的具体实现

## Deferred Ideas

None — discussion stayed within phase scope
