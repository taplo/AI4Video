# Phase 1: 项目重命名与清理 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-05
**Phase:** 1-项目重命名与清理
**Areas discussed:** 数据库与配置迁移, 外部 API 处理策略, 前端 localStorage 兼容, 源码注释与二进制更新

---

## 数据库与配置迁移

| Option | Description | Selected |
|--------|-------------|----------|
| 重命名文件 | 物理重命名 SQLite + 更新配置 | ✓ |
| 保持文件名 | 只改显示名称 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 重命名文件
**Notes:** 没有老用户，系统中的用户都是测试用户，重新建立

---

| Option | Description | Selected |
|--------|-------------|----------|
| 环境变量 + 新密钥 | SECRET_KEY 从环境变量读取 | ✓ |
| 生成新硬编码密钥 | 替换为新的随机密钥 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 环境变量 + 新密钥
**Notes:** 无

---

| Option | Description | Selected |
|--------|-------------|----------|
| 改为 AI4VideoSessionID | 直接替换 | ✓ |
| 改为 avsid | 更短的名称 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 改为 AI4VideoSessionID
**Notes:** 无

---

| Option | Description | Selected |
|--------|-------------|----------|
| 改为 ai4video_safe_key_2026 | 简单替换 | ✓ |
| 改为随机生成的 key | 更安全 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 改为 ai4video_safe_key_2026
**Notes:** 无

---

| Option | Description | Selected |
|--------|-------------|----------|
| 全部改为 AI4Video | OEM 信息更新 | ✓ |
| 保留原样 | 只改代码层面引用 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 全部改为 AI4Video
**Notes:** 无

---

## 外部 API 处理策略

| Option | Description | Selected |
|--------|-------------|----------|
| 完全删除 | 移除 CheckServerUtils 类及相关调用 | ✓ |
| 保留但禁用 | 保留代码但默认关闭 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 完全删除 (checkVersion)
**Notes:** 无

---

| Option | Description | Selected |
|--------|-------------|----------|
| 完全删除 | 移除心跳上报和守护线程 | ✓ |
| 保留但改为本地健康检查 | 改为检查本地服务状态 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 完全删除 (reportHeart)
**Notes:** 无

---

| Option | Description | Selected |
|--------|-------------|----------|
| 完全移除 | 从 config.json 和 UI 中全部移除 | ✓ |
| 保留但隐藏 | 保留字段但不显示 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 完全移除
**Notes:** 无

---

| Option | Description | Selected |
|--------|-------------|----------|
| 全部删除 | 从语言文件中移除升级 key | ✓ |
| 保留但不使用 | 保留翻译 key | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 全部删除
**Notes:** 无

---

## 前端 localStorage 兼容

| Option | Description | Selected |
|--------|-------------|----------|
| 直接重命名 | 改为 ai4video_* keys | ✓ |
| 添加迁移 JS | 检测旧 key 并迁移 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 直接重命名
**Notes:** 没有老用户，无需兼容

---

## 源码注释与二进制更新

| Option | Description | Selected |
|--------|-------------|----------|
| 全部更新为 AI4Video | 更新项目信息 | ✓ |
| 保留原作者信息 | 只替换 URL | |
| 移除作者块 | 删除所有作者信息块 | ✓ |
| 你决定 | 让 agent 选择 | |

**User's choice:** 移除作者块
**Notes:** 无

---

| Option | Description | Selected |
|--------|-------------|----------|
| 重命名为 ai4video_zlm | 重命名所有平台二进制 | ✓ |
| 保持文件名 | 只改配置显示名称 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 重命名为 ai4video_zlm
**Notes:** 无

---

| Option | Description | Selected |
|--------|-------------|----------|
| 改为 ai4video<timestamp>.log | 更新日志前缀 | ✓ |
| 改为 app<timestamp>.log | 使用通用名称 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 改为 ai4video<timestamp>.log
**Notes:** 无

---

| Option | Description | Selected |
|--------|-------------|----------|
| 重命名为 ai4video_qq.jpg | 重命名文件 | |
| 删除 | 移除该图片 | ✓ |
| 保留 | 保持原样 | |
| 你决定 | 让 agent 选择 | |

**User's choice:** 删除
**Notes:** 无

---

## the agent's Discretion

无 — 所有决策由用户明确指定。

## Deferred Ideas

None — discussion stayed within phase scope
