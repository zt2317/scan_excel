# Roadmap: Excel数据推送助手

**Created:** 2026-04-20
**Version:** v1.0

## Phase Overview

| # | Phase | Goal | Requirements | Status |
|---|---|---|-------|------|--------------|
| 1 | Excel处理 | 读取并解析Excel数据 | EXCL-01~05, MD-01~03 | **✓ Complete** |
| 2 | 企业微信集成 | 实现消息推送功能 | WX-01~06 | **✓ Complete** |
| 3 | GUI界面 | 构建用户界面 | GUI-01~06 | **✓ Complete** |
| 4 | 错误处理 | 健壮的错误处理 | ERR-01~03 | **✓ Complete** |
| 5 | 打包发布 | Windows可执行文件 | - | **✓ Complete** |

---

## Phase 1: Excel处理

**Goal:** 实现Excel文件的读取、列识别和Markdown格式化

**UI hint:** no

**Requirements:**
- EXCL-01: 选择Excel文件
- EXCL-02: 自动识别指定列
- EXCL-03: 列名模糊匹配
- EXCL-04: 数据预览
- EXCL-05: 空值处理
- MD-01~03: Markdown格式化

**Success Criteria:**
1. ✓ 能成功读取.xlsx和.xls文件
2. ✓ 正确提取5个目标列数据
3. ✓ 生成格式正确的Markdown表格
4. ✓ 预览显示正常

**Plans:** 4 plans | **Tests:** 34 (33 passed, 1 skipped)

**Plan List:**
- [x] **01-01** — Project setup and core module structure ([SUMMARY](phases/01-excel-processing/01-01-SUMMARY.md))
- [x] **01-02** — Excel reader implementation (openpyxl + xlrd) ([SUMMARY](phases/01-excel-processing/01-02-SUMMARY.md))
- [x] **01-03** — Column detection with fuzzy matching ([SUMMARY](phases/01-excel-processing/01-03-SUMMARY.md))
- [x] **01-04** — Markdown formatter and data preview ([SUMMARY](phases/01-excel-processing/01-04-SUMMARY.md))

**Dependencies:** None

**Canonical refs:**
- `.planning/research/STACK.md` - 技术栈选择
- `.planning/research/PITFALLS.md` - Excel解析陷阱

---

## Phase 2: 企业微信集成

**Goal:** 实现企业微信webhook消息推送和切片发送

**UI hint:** no

**Requirements:**
- WX-01: webhook配置
- WX-02: 配置持久化
- WX-03: 消息切片
- WX-04: 顺序发送
- WX-05: 成功提示
- WX-06: 失败提示

**Success Criteria:**
1. ✓ 能保存webhook URL到配置文件
2. ✓ 消息能正确切片（<1800字符/片）
3. ✓ 顺序发送多条消息
4. ✓ 网络错误时友好提示

**Plans:** 2 plans | **Tests:** 32 passed

**Plan List:**
- [x] **02-01** — Configuration storage module (JSON persistence, .gitignore protection) ([SUMMARY](phases/02-wechat-integration/02-01-SUMMARY.md))
- [x] **02-02** — WeChat client with slicing and retry (15 rows/chunk, 1s interval, exponential backoff) ([SUMMARY](phases/02-wechat-integration/02-02-SUMMARY.md))

**Wave Structure:**
- Wave 1: 02-01 (ConfigStore - no dependencies)
- Wave 2: 02-02 (WeChatWorkClient - depends on ConfigStore)

**Dependencies:** Phase 1

**Canonical refs:**
- `.planning/phases/02-wechat-integration/02-CONTEXT.md` - Phase 2决策
- `.planning/research/FEATURES.md` - 企业微信API限制
- `.planning/research/PITFALLS.md` - 推送陷阱

---

## Phase 3: GUI界面

**Goal:** 使用Tkinter构建简洁的用户界面

**UI hint:** yes

**Requirements:**
- GUI-01~06: 界面组件

**Success Criteria:**
1. 单窗口界面清晰
2. 文件选择、预览、配置一目了然
3. 操作反馈及时
4. 高DPI显示正常

**Plans:** 3 plans in 3 waves

**Plan List:**
- [ ] **03-01** — Main window framework (DPI awareness, 5-frame layout, thread queue) ([PLAN](phases/03-gui-interface/03-01-PLAN.md))
- [ ] **03-02** — File selection and preview (background thread, Treeview with 20 rows) ([PLAN](phases/03-gui-interface/03-02-PLAN.md))
- [ ] **03-03** — Config save and send (webhook persistence, message sending, status feedback) ([PLAN](phases/03-gui-interface/03-03-PLAN.md))

**Wave Structure:**
- Wave 1: 03-01 (MainWindow framework - no dependencies)
- Wave 2: 03-02 (File selection & preview - depends on 03-01)
- Wave 3: 03-03 (Config & send - depends on 03-01, 03-02)

**Dependencies:** Phase 1, Phase 2

**Canonical refs:**
- `.planning/phases/03-gui-interface/03-CONTEXT.md` - Phase 3决策
- `.planning/research/PITFALLS.md` - GUI陷阱
- `src/core/excel_reader.py` - Excel读取接口
- `src/core/config.py` - ConfigStore接口
- `src/core/wechat_client.py` - WeChatWorkClient接口

---

## Phase 4: 错误处理

**Goal:** 健壮的错误处理和用户友好提示

**UI hint:** no

**Requirements:**
- ERR-01: Excel格式错误提示
- ERR-02: 网络超时重试
- ERR-03: webhook无效提示

**Success Criteria:**
1. ✓ 所有错误都有清晰的中文提示
2. ✓ 不暴露技术细节给用户
3. ✓ 提供解决建议
4. ✓ 异常情况应用不崩溃

**Plans:** 2 plans | **Status:** Complete

**Plan List:**
- [x] **04-01** — Excel format error handling (ExcelFormatError class, Chinese error messages) ([SUMMARY](phases/04-error-handling/04-01-SUMMARY.md))
- [x] **04-02** — GUI error integration (Network retry, webhook validation, global exception handler) ([SUMMARY](phases/04-error-handling/04-02-SUMMARY.md))

**Wave Structure:**
- Wave 1: 04-01 (Error types - no dependencies)
- Wave 2: 04-02 (GUI integration - depends on 04-01)

**Dependencies:** Phase 1, Phase 2, Phase 3

**Canonical refs:**
- `.planning/phases/04-error-handling/04-CONTEXT.md` - Phase 4决策
- `src/core/exceptions.py` - 现有异常类
- `src/core/excel_reader.py` - Excel读取错误点
- `src/core/wechat_client.py` - 网络/API错误点
- `src/gui/main_window.py` - GUI错误显示

---

## Phase 5: 打包发布

**Goal:** 使用GitHub Actions构建Windows可执行文件

**UI hint:** no

**Requirements:** None（构建阶段）

**Success Criteria:**
1. ✓ GitHub Actions配置正确
2. ✓ Windows exe成功生成
3. ✓ 单文件模式（--onefile）
4. ✓ 无控制台窗口（--windowed）
5. 在Windows环境测试通过

**Plans:** 4 plans | **Status:** Complete

**Plan List:**
- [x] **05-01** — GitHub Actions workflow ([PLAN](phases/05-packaging-release/05-01-PLAN.md)) ([SUMMARY](phases/05-packaging-release/05-SUMMARY.md))
- [x] **05-02** — PyInstaller configuration ([PLAN](phases/05-packaging-release/05-02-PLAN.md)) ([SUMMARY](phases/05-packaging-release/05-SUMMARY.md))
- [x] **05-03** — Application icon resources ([PLAN](phases/05-packaging-release/05-03-PLAN.md)) ([SUMMARY](phases/05-packaging-release/05-SUMMARY.md))
- [x] **05-04** — Testing checklist and release template ([PLAN](phases/05-packaging-release/05-04-PLAN.md)) ([SUMMARY](phases/05-packaging-release/05-SUMMARY.md))

**Wave Structure:**
- Wave 1: 05-01, 05-02 (GitHub Actions + PyInstaller config - no dependencies)
- Wave 2: 05-03 (Icon generation - depends on nothing)
- Wave 3: 05-04 (Testing docs - depends on nothing)

**Dependencies:** Phase 1-4

**Canonical refs:**
- `.planning/research/STACK.md` - 打包方案
- `.planning/research/PITFALLS.md` - 打包陷阱

---

## Traceability Matrix

| Requirement | Phase | Status |
|-------------|-------|--------|
| EXCL-01~05 | Phase 1 | **✓ Complete** |
| MD-01~03 | Phase 1 | **✓ Complete** |
| WX-01~06 | Phase 2 | **✓ Complete** |
| GUI-01~06 | Phase 3 | **✓ Complete** |
| ERR-01~03 | Phase 4 | **✓ Complete** |

**Total Phases:** 5
**Total Phases Complete:** 5
**Total Requirements:** 15
**Requirements Coverage:** 100%

---

## Milestones

### v1.0 MVP
**包含Phase:** 1-5
**目标:** 可使用的Windows应用
**成功标准:**
- 能读取Excel并推送到企业微信
- 用户无需配置开发环境
- 单文件exe运行

---

*Last updated: 2026-04-21 after Phase 5 complete - v1.0 MVP finished*
