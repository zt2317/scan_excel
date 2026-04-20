# Excel数据推送助手

## What This Is

一个Windows桌面应用程序，用于读取Excel文件中的物流数据（日期、发货人、提单号、入库未扫、出库未扫），并将数据格式化为Markdown后通过企业微信 webhook 推送到指定群组。

## Core Value

用户能够一键将Excel中的物流数据推送到企业微信，及时通知相关人员处理"入库未扫"和"出库未扫"的异常数据。

## Requirements

### Validated

( None yet — ship to validate )

### Active

- [ ] 支持选择Excel文件（.xlsx/.xls）
- [ ] 读取指定列：日期、发货人、提单号、入库未扫、出库未扫
- [ ] 将数据格式化为Markdown表格
- [ ] 通过企业微信 webhook 推送消息
- [ ] 消息过大时自动切片发送
- [ ] Windows可执行文件打包（在Mac开发，需确定交叉编译方案）

### Out of Scope

- 不支持Excel写入功能 — 纯读取工具
- 不集成其他IM工具（钉钉、飞书等） — 仅企业微信
- 不支持数据持久化存储 — 临时处理，不保存历史
- 不支持复杂Excel格式（合并单元格、图表等） — 仅简单表格数据

## Context

- **开发环境**: macOS
- **目标平台**: Windows 10/11
- **用户场景**: 物流/仓储人员需要快速分享Excel中的异常扫描数据给工作群组
- **企业微信限制**: 单条消息2048字符，需实现切片逻辑

## Constraints

- **打包方案**: 需在Mac上交叉编译Windows可执行文件，考虑PyInstaller+Wine或GitHub Actions方案
- **运行环境**: Windows用户可能没有Python环境，需打包为独立exe
- **Excel依赖**: 需兼容新旧版Excel格式（.xlsx和.xls）
- **网络依赖**: 企业微信推送需要网络连接，需处理超时和失败重试
- **数据隐私**: webhook配置和Excel文件必须保存在本地，不得提交到git
  - webhook URL存储在用户目录或应用目录的配置文件
  - 添加.gitignore排除敏感文件

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 技术栈：Python+Tkinter | 跨平台GUI，简单易用，打包成熟 | — Pending |
| Excel库：openpyxl | 支持.xlsx格式，维护活跃 | — Pending |
| 旧版Excel：xlrd | 兼容.xls格式（旧版） | — Pending |
| 打包方案：待确定 | Mac→Windows交叉编译，待调研 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-20 after initialization*
