# Phase 5: test-infrastructure - Context

**Gathered:** 2026-08-09
**Status:** Ready for planning

<domain>
## Phase Boundary

建立 pytest 测试框架，创建测试用例覆盖核心模块，配置 GitHub Actions CI 自动运行测试和 lint。

</domain>

<decisions>
## Implementation Decisions

### Test Framework Choice
- **D-01:** 使用 pytest + pytest-django 作为测试框架
- **D-02:** 使用 pytest fixtures 处理测试 setup/teardown
- **D-03:** 函数级别数据库隔离（每个测试函数使用独立数据库）
- **D-04:** 启用并行测试执行（pytest-xdist）

### Coverage Targets
- **D-05:** 目标覆盖率 60%，优先覆盖核心工具、模型和安全修复
- **D-06:** 优先测试高优先级模块：Config、tracker、Utils、Models
- **D-07:** 覆盖率报告：HTML + 终端输出
- **D-08:** 在 CI 中强制执行覆盖率阈值

### Test Organization
- **D-09:** 测试文件放在项目根目录 `tests/` 目录
- **D-10:** 测试文件命名：`test_{module}.py`
- **D-11:** 扁平结构，不分子目录
- **D-12:** conftest.py 放在 `tests/conftest.py`

### CI/CD Integration
- **D-13:** 在每次 push 和 PR 时运行测试
- **D-14:** 测试 Python 3.11+ 版本
- **D-15:** CI 中同时运行 flake8 lint 和 pytest
- **D-16:** 缓存 pip 依赖以加速 CI

### the agent's Discretion
- 测试用例的具体实现细节
- fixtures 的具体设计
- mock 策略（基于 TESTING.md 建议）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 核心文件
- `.planning/ROADMAP.md` — Phase 5 目标和依赖关系
- `.planning/codebase/TESTING.md` — 测试现状分析、测试缺口优先级
- `.planning/codebase/CONVENTIONS.md` — 代码约定（测试需要遵循）
- `.planning/codebase/STRUCTURE.md` — 项目结构（测试目录位置）

### 参考文档
- `.planning/phases/03-architecture-upgrade/03-CONTEXT.md` — Phase 3 决策（ORM 迁移、BaseModel mixin）
- `.planning/phases/04-engineering-hardening/04-CONTEXT.md` — Phase 4 决策（安全修复、错误处理）

### 需要创建的文件
- `tests/conftest.py` — pytest fixtures 配置
- `pytest.ini` — pytest 配置
- `tests/test_config.py` — Config 模块测试
- `tests/test_tracker.py` — Tracker 模块测试
- `tests/test_utils.py` — Utils 模块测试
- `tests/test_models.py` — Models 测试
- `.github/workflows/test.yml` — GitHub Actions CI 配置

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/tests.py` — 空的测试文件，可删除或保留作为参考
- `app/utils/Config.py` — 配置解析逻辑，需要测试 `_bool`、`_int`、`_resolve_path`
- `app/analysis/tracker.py` — IoU 计算和跟踪逻辑，需要测试 `_iou`、`IoUTracker`
- `app/utils/Utils.py` — 分页助手和代码生成，需要测试 `buildPageLabels`、`group_by_field`
- `app/models.py` — Django 模型，需要测试字段验证和默认值

### Established Patterns
- 所有视图使用 `from app.views.ViewsBase import *` 通配导入
- 配置通过 `g_config` 全局单例访问
- JSON 响应统一使用 `f_responseJson()` 返回
- 错误处理使用 `logger.warning()` 记录

### Integration Points
- `app/utils/Config.py` — 配置解析（测试目标）
- `app/analysis/tracker.py` — 跟踪逻辑（测试目标）
- `app/utils/Utils.py` — 工具函数（测试目标）
- `app/models.py` — 数据模型（测试目标）

</code_context>

<specifics>
## Specific Ideas

无特殊要求 — 采用标准 pytest 测试框架配置方法。

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 5-test-infrastructure*
*Context gathered: 2026-08-09*
