# Phase 1: Excel处理 - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

实现Excel文件的读取、列识别和Markdown格式化。支持.xlsx和.xls格式，自动识别5个目标列（日期、发货人、提单号、入库未扫、出库未扫），生成标准Markdown表格。

</domain>

<decisions>
## Implementation Decisions

### Excel读取策略
- **D-01:** 使用 `openpyxl` 读取.xlsx，使用 `xlrd` 读取.xls
- **D-02:** 采用一次性加载策略（非流式），适合常规Excel文件
- **D-03:** 轻量级方案，打包体积小

### 列识别策略
- **D-04:** 使用模糊包含匹配算法（如列名包含"日期"即匹配）
- **D-05:** 优先尝试自动识别，无法匹配时直接报错退出
- **D-06:** 不实现交互式列映射（超出当前phase范围）

### 数据验证与转换
- **D-07:** 日期智能识别：支持多种输入格式，统一输出为 YYYY-MM-DD
- **D-08:** 空值处理：显示为 "-"（短横线）
- **D-09:** 所有5个目标列必须存在，任一缺失则报错退出

### Markdown格式化
- **D-10:** 使用对齐表格格式（Markdown原生对齐语法）
- **D-11:** 表头加粗显示
- **D-12:** 数据预览显示前10行供用户确认

### 错误处理
- **D-13:** 使用简洁中文错误提示，用户友好
- **D-14:** Excel格式错误、列缺失等直接退出并提示修复方法
- **D-15:** 不实现部分处理或容错逻辑

### the agent's Discretion
- 具体错误提示文案设计
- 日期格式识别的具体实现细节（正则或dateutil）
- Markdown表格的对齐方式（居左/居中/居右）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Excel处理
- `.planning/research/STACK.md` — 技术栈选择和库版本要求
- `.planning/research/PITFALLS.md` — Excel解析常见陷阱

### Requirements
- `.planning/REQUIREMENTS.md` — Phase 1详细需求 (EXCL-01~05, MD-01~03)

### 外部资源
- No external specs — requirements fully captured in decisions above

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — this is a greenfield project, first phase

### Established Patterns
- None — no existing codebase

### Integration Points
- This phase creates the core Excel reading module
- Output (Markdown formatted data) consumed by Phase 2 (企业微信推送)
- Will be used by Phase 3 GUI interface

</code_context>

<specifics>
## Specific Ideas

- 日期格式常见变体：2024/1/15, 2024-01-15, 15/01/2024, 15-Jan-2024 等
- 模糊匹配关键词：
  - 日期 → 包含"日期"
  - 发货人 → 包含"发货"或"发货人"
  - 提单号 → 包含"提单"或"单号"
  - 入库未扫 → 包含"入库"
  - 出库未扫 → 包含"出库"

</specifics>

<deferred>
## Deferred Ideas

- 交互式列映射（选择Excel列名）— 属于Phase 3 GUI功能
- 流式读取大文件 — 如果后续遇到性能问题再考虑
- 部分列缺失时的容错处理 — 需求明确5列必须存在
- pandas方案 — 打包体积太大，当前轻量方案已满足需求

</deferred>

---

*Phase: 01-excel-processing*
*Context gathered: 2026-04-20*
