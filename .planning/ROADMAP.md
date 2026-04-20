# Roadmap: Excel数据推送助手

**Created:** 2026-04-20
**Version:** v1.0

## Phase Overview

| # | Phase | Goal | Requirements | Status |
|---|-------|------|--------------|--------|
| 1 | Excel处理 | 读取并解析Excel数据 | EXCL-01~05, MD-01~03 | Pending |
| 2 | 企业微信集成 | 实现消息推送功能 | WX-01~06 | Pending |
| 3 | GUI界面 | 构建用户界面 | GUI-01~06 | Pending |
| 4 | 错误处理 | 健壮的错误处理 | ERR-01~03 | Pending |
| 5 | 打包发布 | Windows可执行文件 | - | Pending |

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
1. 能成功读取.xlsx和.xls文件
2. 正确提取5个目标列数据
3. 生成格式正确的Markdown表格
4. 预览显示正常

**Build Order:**
1. 创建项目结构和核心模块
2. 实现Excel读取器（openpyxl + xlrd）
3. 实现列识别逻辑
4. 实现Markdown格式化器
5. 单元测试

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
1. 能保存webhook URL到配置文件
2. 消息能正确切片（<1800字符/片）
3. 顺序发送多条消息
4. 网络错误时友好提示

**Build Order:**
1. 实现配置存储模块
2. 实现企业微信客户端
3. 实现消息切片算法
4. 添加重试机制
5. 集成测试

**Dependencies:** Phase 1

**Canonical refs:**
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

**Build Order:**
1. 设计界面布局
2. 实现主窗口框架
3. 实现文件选择组件
4. 实现数据预览表格
5. 实现配置和发送界面
6. 添加状态栏

**Dependencies:** Phase 1, Phase 2

**Canonical refs:**
- `.planning/research/PITFALLS.md` - GUI陷阱

---

## Phase 4: 错误处理

**Goal:** 健壮的错误处理和用户友好提示

**UI hint:** no

**Requirements:**
- ERR-01: Excel格式错误提示
- ERR-02: 网络超时重试
- ERR-03: webhook无效提示

**Success Criteria:**
1. 所有错误都有清晰的中文提示
2. 不暴露技术细节给用户
3. 提供解决建议
4. 异常情况应用不崩溃

**Build Order:**
1. 定义错误类型和消息
2. 包装Excel读取错误
3. 包装网络错误
4. 添加全局异常处理
5. 错误场景测试

**Dependencies:** Phase 1, Phase 2, Phase 3

---

## Phase 5: 打包发布

**Goal:** 使用GitHub Actions构建Windows可执行文件

**UI hint:** no

**Requirements:** None（构建阶段）

**Success Criteria:**
1. GitHub Actions配置正确
2. Windows exe成功生成
3. 单文件模式（--onefile）
4. 无控制台窗口（--windowed）
5. 在Windows环境测试通过

**Build Order:**
1. 创建GitHub Actions workflow
2. 配置PyInstaller spec文件
3. 添加应用图标
4. 测试打包流程
5. 验证Windows可执行

**Dependencies:** Phase 1-4

**Canonical refs:**
- `.planning/research/STACK.md` - 打包方案
- `.planning/research/PITFALLS.md` - 打包陷阱

---

## Traceability Matrix

| Requirement | Phase | Status |
|-------------|-------|--------|
| EXCL-01~05 | Phase 1 | Pending |
| MD-01~03 | Phase 1 | Pending |
| WX-01~06 | Phase 2 | Pending |
| GUI-01~06 | Phase 3 | Pending |
| ERR-01~03 | Phase 4 | Pending |

**Total Phases:** 5
**Total Requirements:** 15
**Coverage:** 100%

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

*Last updated: 2026-04-20 after initial roadmap creation*
