# Phase 3: GUI界面 - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

使用Tkinter构建简洁的用户界面。单窗口应用，包含文件选择、数据预览、webhook配置、发送按钮和状态栏。集成Phase 1的Excel读取和Phase 2的企业微信发送功能。

依赖Phase 1（ExcelReader、ColumnDetector、MarkdownFormatter）和Phase 2（ConfigStore、WeChatWorkClient）。

</domain>

<decisions>
## Implementation Decisions

### 界面布局设计
- **D-01:** 采用垂直流式布局，组件从上到下按操作流程排列
- **D-02:** 窗口尺寸：800x600固定大小，不可调整
- **D-03:** 区域顺序：文件选择区 → 数据预览区 → webhook配置区 → 发送按钮 → 状态栏
- **D-04:** 窗口启动时居中显示

### 线程处理策略
- **D-05:** Excel读取操作在后台线程执行，避免大文件阻塞界面
- **D-06:** 消息发送操作在后台线程执行，避免HTTP请求和1秒间隔阻塞界面
- **D-07:** 配置保存直接执行（无需后台线程，速度极快）
- **D-08:** 线程管理：每次操作新建线程，用完即弃（简单直接）
- **D-09:** UI更新：使用Tkinter的after()方法，主线程定时轮询检查后台状态
- **D-10:** 线程安全：通过队列或共享变量传递数据，主线程负责所有UI更新

### 数据预览表格
- **D-11:** 使用Tkinter.ttk.Treeview控件显示Excel数据
- **D-12:** 显示前20行数据（比Phase 1的10行更多，充分利用预览区）
- **D-13:** 列宽自适应内容（根据实际数据长度调整）
- **D-14:** 表格支持垂直滚动条，水平滚动条按需显示
- **D-15:** 表头显示列名（日期、发货人、提单号、入库未扫、出库未扫）
- **D-16:** 数据行交替背景色，提高可读性

### 错误提示方式
- **D-17:** 分级处理：严重错误弹窗，普通提示状态栏
- **D-18:** 弹窗场景：文件读取错误、列识别失败、配置错误、发送失败、发送成功
- **D-19:** 状态栏场景：文件选择成功、数据加载完成、操作进行中
- **D-20:** 弹窗类型：错误用messagebox.showerror()，成功用messagebox.showinfo()
- **D-21:** 错误消息延续Phase 1&2风格：简洁中文，用户友好

### 状态反馈设计
- **D-22:** 进度显示：使用ttk.Progressbar显示精确百分比（0-100%）
- **D-23:** Excel读取进度：基于已读取行数/总行数计算
- **D-24:** 消息发送进度：基于已发送片数/总片数计算
- **D-25:** 状态栏设计：多行显示，第1行状态文字，第2行进度条
- **D-26:** 状态文字使用颜色区分：默认（黑色）、进行中（蓝色）、成功（绿色）、失败（红色）
- **D-27:** 状态栏常驻显示，始终可见

### 控件细节
- **D-28:** 文件选择：使用ttk.Button + ttk.Entry，按钮文字"选择文件"
- **D-29:** webhook配置：使用ttk.Entry（单行输入），标签"Webhook地址"
- **D-30:** 发送按钮：ttk.Button，文字"发送消息"，默认禁用（未选文件时）
- **D-31:** 标签使用ttk.Label，按钮使用ttk.Button（统一使用ttk主题控件）
- **D-32:** 使用系统默认字体，不指定特定字体名（避免跨平台差异）

### 高分屏支持
- **D-33:** Windows启用DPI感知：使用ctypes.windll.shcore.SetProcessDpiAwareness(1)
- **D-34:** 打包时确保DPI设置生效（在PyInstaller spec中配置）

### the agent's Discretion
- 控件具体padding和间距（使用ttk.Style统一调整）
- 状态栏进度条的具体高度和颜色
- 表格交替行的背景色具体色值
- 窗口最小化/关闭行为（是否最小化到托盘）
- 快捷键设置（如Ctrl+O打开文件）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### GUI陷阱和最佳实践
- `.planning/research/PITFALLS.md` §4 — GUI陷阱：Tkinter界面冻结、字体差异、高DPI模糊

### Phase 1 输出（Excel处理）
- `src/core/excel_reader.py` — ExcelReader类，GUI中文件选择后调用
- `src/core/column_detector.py` — ColumnDetector类，识别列名
- `src/core/formatter.py` — MarkdownFormatter，格式化输出（预览显示原始数据）
- `src/core/preview.py` — generate_preview()，生成预览数据
- `.planning/phases/01-excel-processing/01-CONTEXT.md` — Phase 1决策继承（20行预览、中文错误）

### Phase 2 输出（企业微信）
- `src/core/config.py` — ConfigStore类，读取/保存webhook配置
- `src/core/wechat_client.py` — WeChatWorkClient类，发送消息
- `src/core/exceptions.py` — 异常类，GUI中捕获并显示友好提示
- `.planning/phases/02-wechat-integration/02-CONTEXT.md` — Phase 2决策继承（线程发送、D-19提及GUI线程）

### Requirements
- `.planning/REQUIREMENTS.md` — GUI-01~06 详细需求定义

### Tkinter参考
- 使用Python标准库tkinter和tkinter.ttk
- 不需要外部GUI库（轻量级原则，延续Phase 1&2）

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **ExcelReader** (`src/core/excel_reader.py`): 读取Excel文件，GUI中文件选择后调用
- **ColumnDetector** (`src/core/column_detector.py`): 列名识别，用于确认数据正确性
- **MarkdownFormatter** (`src/core/formatter.py`): 格式化Markdown，预览显示原始Excel数据
- **ConfigStore** (`src/core/config.py`): 读取/保存webhook配置，GUI配置区绑定
- **WeChatWorkClient** (`src/core/wechat_client.py`): 发送消息，GUI发送按钮触发

### Established Patterns
- **轻量级优先**: Phase 1&2使用标准库，GUI继续使用Tkinter（Python标准库）
- **中文错误提示**: 所有错误消息使用中文，用户友好
- **直接报错**: 不实现复杂容错，错误直接提示用户
- **配置分离**: 配置文件存储在config/目录，不污染代码

### Integration Points
- **文件选择** → ExcelReader.read() → ColumnDetector → 预览表格显示
- **配置输入** → ConfigStore.set_webhook_url() → 保存到config/webhook_config.json
- **发送按钮** → WeChatWorkClient.send_markdown() → 状态栏显示进度和结果
- **后台线程**: Excel读取和消息发送在新线程执行，通过after()更新UI

</code_context>

<specifics>
## Specific Ideas

- 界面流程：选文件 → 自动读取并显示预览 → 检查webhook配置 → 点击发送 → 显示进度 → 完成提示
- 文件选择后自动触发读取，无需额外点击"加载"按钮
- 发送按钮默认禁用，满足以下条件时启用：1)已选文件 2)文件读取成功 3)已配置webhook
- 状态栏文字示例：
  - "准备就绪"（初始状态）
  - "正在读取Excel文件..."（读取中）
  - "读取完成，共50行数据"（读取成功）
  - "正在发送消息（第1/3片）..."（发送中）
  - "消息发送成功！"（发送完成）
- 高分屏设置代码片段：
  ```python
  import ctypes
  try:
      ctypes.windll.shcore.SetProcessDpiAwareness(1)
  except:
      pass  # 非Windows或旧版本忽略
  ```

</specifics>

<deferred>
## Deferred Ideas

- **最小化到托盘** — 当前窗口直接关闭退出，未来可考虑系统托盘驻留
- **最近文件列表** — v2功能，显示最近打开的5个文件
- **配置向导** — 首次启动引导配置webhook，当前在配置区直接显示输入框
- **主题切换** — 浅色/深色主题，当前使用系统默认主题
- **表格排序** — 点击表头排序，当前按Excel原始顺序显示
- **数据过滤** — v2需求（仅显示异常数据），当前显示全部数据
- **快捷键** — Ctrl+O打开、Ctrl+Enter发送等，当前仅支持鼠标操作
- **日志窗口** — 显示详细操作日志，当前仅在状态栏显示

</deferred>

---

*Phase: 03-gui-interface*
*Context gathered: 2026-04-20*
