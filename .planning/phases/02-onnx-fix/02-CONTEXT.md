# Phase 2: ONNX 模型检测修复 - Context

**Gathered:** 2026-08-07
**Status:** Ready for planning

<domain>
## Phase Boundary

修复 ONNX 模型上传后检测报错的问题，包括 algorithm_type 自动检测、路径解析、输入尺寸匹配、标签文件发现。

</domain>

<decisions>
## Implementation Decisions

### algorithm_type 自动检测
- **D-01:** 上传时自动分析 ONNX 模型输出 shape，推断 yolo5/8/11/26 版本
- **D-02:** 检测逻辑：输出 shape 维度比较 — 列数 < 行数 → v5 格式，列数 > 行数 → v8+ 格式
- **D-03:** 推断结果回显给用户确认，用户可手动修改 algorithm_type
- **D-04:** 实现位置：`app/views/SmallModelView.py` 的 `smallmodel_openProbe()` 接口

### 错误处理与降级
- **D-05:** 输入尺寸不匹配时自动 resize 输入到模型期望尺寸，用户无感知
- **D-06:** 模型路径不存在时记录警告日志，返回空结果，不中断分析流程
- **D-07:** 推理过程中的异常捕获并记录详细日志（模型文件路径、provider 列表、input/output shape）

### 标签文件发现
- **D-08:** 查找顺序：模型同目录下 labels.txt → 模型同目录下 {model_name}.txt → static/labels/ 目录 → 空标签
- **D-09:** 找不到标签文件时使用空标签列表，不中断推理

### probe 接口返回值
- **D-10:** 新增 `algorithm_type_detected` 字段（自动推断结果）
- **D-11:** 新增 `input_size_inferred` 字段（从模型 input shape 读取）
- **D-12:** 保持现有字段不变，仅追加新字段

### the agent's Discretion
- `resolve_model_path()` 中增加路径不存在时的警告日志
- `onnx_engine.py` 的 `load()` 中增加更详细的错误日志
- `yolo_postprocess.py` 的 `_decode_detect()` 中增加输出 shape 与 algorithm_type 不匹配时的日志

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 核心文件
- `app/views/SmallModelView.py` — probe 接口，algorithm_type 默认值和自动检测实现位置
- `app/analysis/engines/onnx_engine.py` — ONNX 引擎，load() 和 detect() 方法
- `app/analysis/engines/yolo_postprocess.py` — YOLO 后处理，decode_outputs() 和 _decode_detect()
- `app/analysis/worker_pool.py` — resolve_model_path() 函数
- `app/analysis/engines/base.py` — BaseEngine 基类，_resolve_labels() 方法

### 参考文档
- `.planning/UPGRADE_PLAN.md` — Phase 2 完整修复方案
- `.planning/codebase/ARCHITECTURE.md` — 分析引擎架构
- `.planning/codebase/CONCERNS.md` — 已知问题

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `OnnxEngine.probe()` (onnx_engine.py:135-157) — 已有 input_shape/output_shape 推断逻辑
- `BaseEngine._resolve_labels()` (base.py) — 标签文件查找可复用
- `_is_v5()` (yolo_postprocess.py:60-61) — 已有 v5 判断函数

### Established Patterns
- 所有引擎继承 `BaseEngine`，实现 `load()`/`detect()`/`info()`/`probe()`
- 后处理统一通过 `decode_outputs()` 分发
- 错误处理使用 `logger.warning()` 记录并返回空结果

### Integration Points
- `SmallModelView.smallmodel_openProbe()` — 调用 OnnxEngine.probe() 返回给前端
- `worker_pool.resolve_model_path()` — 模型路径解析
- `inference_pool._resolve_model_path()` — 包装 resolve_model_path()

</code_context>

<specifics>
## Specific Ideas

无特殊要求 — 采用标准修复方法。

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 2-ONNX模型检测修复*
*Context gathered: 2026-08-07*
