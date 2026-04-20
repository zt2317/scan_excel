# Project State

**Project:** Excel数据推送助手
**Created:** 2026-04-20
**Status:** Initialized

## Current Phase

**Phase:** 2 (Executing)
**Status:** Wave 1 in progress ◆
**Next Action:** Executing Plan 02-01 (ConfigStore module)

### Phase 2 Context Decisions
- **配置存储**: 应用目录 + JSON + 明文（依赖.gitignore）
- **消息切片**: 15行/片 + 序号标记 + 表头重复
- **发送策略**: 1秒间隔 + 阻塞式重试失败片
- **重试机制**: 3次 + 指数退避(1s,2s,4s) + 30秒超时
- **客户端架构**: WeChatWorkClient类 + 普通requests

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-20)

**Core value:** 用户能够一键将Excel中的物流数据推送到企业微信，及时通知相关人员处理"入库未扫"和"出库未扫"的异常数据。

**Current focus:** Phase 1 Excel处理已完成，准备进入Phase 2 企业微信集成

## Completed Work

### Phase 1: Excel处理 ✓ (2026-04-20)
- [x] **Plan 01-01** - 项目结构：目录结构、requirements.txt、.gitignore
- [x] **Plan 01-02** - ExcelReader：支持.xlsx和.xls，中文错误消息
- [x] **Plan 01-03** - ColumnDetector：模糊匹配列名，空值→"-"
- [x] **Plan 01-04** - MarkdownFormatter：对齐表格、日期格式化、预览
- [x] **Tests** - 34 tests (33 passed, 1 skipped)

**Requirements Covered:**
- ✓ EXCL-01: 文件读取
- ✓ EXCL-02: 列识别
- ✓ EXCL-03: 模糊匹配
- ✓ EXCL-04: 数据预览
- ✓ EXCL-05: 空值处理
- ✓ MD-01~03: Markdown格式化

### Project Setup
- [x] PROJECT.md - 项目定义
- [x] config.json - 工作流配置
- [x] research/ - 领域研究完成
- [x] REQUIREMENTS.md - 需求定义
- [x] ROADMAP.md - 路线图
- [x] .gitignore - 敏感文件保护

## Pending Work

**Phase 1: Excel处理** (EXCL-01~05, MD-01~03)
- 创建项目结构和核心模块
- 实现Excel读取器（openpyxl + xlrd）
- 实现列识别逻辑
- 实现Markdown格式化器
- 单元测试

**Phase 2: 企业微信集成** (WX-01~06)
- 实现配置存储模块（本地，不上传git）
- 实现企业微信客户端
- 实现消息切片算法
- 添加重试机制

**Phase 3: GUI界面** (GUI-01~06)
- 设计界面布局
- 实现主窗口框架
- 实现各功能组件

**Phase 4: 错误处理** (ERR-01~03)
- 定义错误类型和消息
- 添加全局异常处理

**Phase 5: 打包发布**
- 创建GitHub Actions workflow
- 配置PyInstaller
- 测试Windows可执行

## Key Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-20 | Phase 2: 配置存储策略 | 应用目录+JSON+明文，简单直观，依赖.gitignore保护 |
| 2026-04-20 | Phase 2: 消息切片策略 | 15行/片保守值，保证表格完整性，带序号标记 |
| 2026-04-20 | Phase 2: 发送策略 | 1秒间隔安全值，阻塞式重试失败片 |
| 2026-04-20 | Phase 2: 重试机制 | 3次+指数退避(1s,2s,4s)+30秒超时，标准策略 |
| 2026-04-20 | Phase 2: 客户端架构 | WeChatWorkClient类封装，普通requests简化实现 |
| 2026-04-20 | 使用GitHub Actions打包 | Mac无法直接生成Windows exe，GitHub Actions Windows runner是最佳方案 |
| 2026-04-20 | webhook配置不上传git | 保护敏感信息，使用.gitignore排除 |
| 2026-04-20 | Excel文件不上传git | 用户数据隐私保护 |

## Notes

- 用户已确认：使用中文对话
- 已明确：webhook配置和Excel文件不提交到git
- 打包方案已确定：GitHub Actions Windows runner

---
*Last updated: 2026-04-20 after Phase 2 context discussion*
