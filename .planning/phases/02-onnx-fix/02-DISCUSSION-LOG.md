# Phase 2: ONNX 模型检测修复 - Discussion Log

**Date:** 2026-08-07

## Area 1: algorithm_type 自动检测策略

**Options presented:**
1. 自动检测 + 用户确认 (Recommended)
2. 全自动静默
3. 用户手动选择

**User selected:** 自动检测 + 用户确认

**Follow-up:** 检测逻辑
- Options: shape 维度比较 / obj 通道检测 / 组合检测
- **User selected:** shape 维度比较

## Area 2: 错误处理与降级策略

**Question 1:** 输入尺寸不匹配
- Options: 自动 resize / 拒绝并报错 / 自动 resize + 警告
- **User selected:** 自动 resize

**Question 2:** 路径不存在
- Options: 警告 + 跳过 / 抛出异常 / 自动搜索 + 警告
- **User selected:** 警告 + 跳过

## Area 3: 标签文件发现逻辑

**Options presented:**
1. 标准搜索链 (Recommended)
2. 仅模型目录
3. 强制要求

**User selected:** 标准搜索链

## Area 4: probe 接口返回值设计

**Options presented:**
1. 新增推断字段 (Recommended)
2. 保持现状
3. 丰富调试信息

**User selected:** 新增推断字段

## Deferred Ideas

None

---
