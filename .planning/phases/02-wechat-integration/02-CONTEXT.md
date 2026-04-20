# Phase 2: 企业微信集成 - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

实现企业微信webhook消息推送和切片发送。支持配置持久化（本地存储，不上传git），消息自动切片（<1800字符/片），顺序发送带间隔避免限流，成功/失败提示。

依赖Phase 1的Markdown格式化输出作为消息内容。

</domain>

<decisions>
## Implementation Decisions

### 配置存储策略
- **D-01:** 存储位置：应用目录下 `config/` 文件夹（与项目代码放在一起，不污染用户系统）
- **D-02:** 文件格式：JSON（与Phase 1数据格式保持一致）
- **D-03:** 安全措施：明文存储，依赖 `.gitignore` 排除配置文件，不提交到版本控制
- **D-04:** 存储内容：webhook URL、可选的默认文件夹路径（为未来功能预留）

### 消息切片策略
- **D-05:** 切分依据：按行数切分，保证Markdown表格完整性，避免半行
- **D-06:** 每片行数：15行数据（保守值，预留Markdown格式开销，企业微信限制2048字符）
- **D-07:** 多片标识：每片开头添加序号标记 "（第N/M片）"，最后一片加 "（完）"
- **D-08:** 表头处理：除第一片外，每片重复表头，方便阅读

### 发送策略
- **D-09:** 发送间隔：1秒（保守值，企业微信限制20条/秒）
- **D-10:** 失败处理：阻塞式重试——某一片失败时暂停发送后续，先重试该片
- **D-11:** 顺序保证：严格按片顺序发送（1→2→3），禁止并行
- **D-12:** 成功提示：每片发送成功更新状态，全部完成后显示汇总

### 重试机制
- **D-13:** 重试次数：总共3次尝试（1次原始请求 + 2次重试）
- **D-14:** 退避策略：指数退避——第1次重试等1秒，第2次等2秒，第3次等4秒
- **D-15:** 超时设置：每次HTTP请求30秒超时（宽松设置，避免误判）
- **D-16:** 可重试错误：仅网络超时、连接错误等临时错误触发重试，HTTP 4xx错误不重试

### 客户端架构
- **D-17:** 架构模式：类封装 `WeChatWorkClient`，包含配置、发送、切片、重试逻辑
- **D-18:** 实现方式：普通 `requests.post()`，不使用 Session（简化实现）
- **D-19:** 同步调用：不使用 async/await（GUI Phase中再用线程处理）
- **D-20:** 错误类型：定义自定义异常 `WeChatAPIError`、`NetworkError`、`ConfigError`

### the agent's Discretion
- 配置文件的精确路径处理（使用 `pathlib` 处理跨平台路径）
- 错误提示的具体文案设计（保持与Phase 1风格一致的中文提示）
- 日志记录级别和输出方式
- 重试时的日志输出格式

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 企业微信API限制
- `.planning/research/FEATURES.md` — 企业微信消息长度限制（2048字符）、频率限制（20条/秒）、Webhook JSON格式

### 风险与陷阱
- `.planning/research/PITFALLS.md` §3 — 企业微信推送陷阱：webhook泄露、频率限制、Markdown格式错误

### Phase 1 输出
- `src/core/formatter.py` — MarkdownFormatter输出格式，作为消息内容输入
- `.planning/phases/01-excel-processing/01-CONTEXT.md` — Phase 1决策继承（轻量级方案、中文错误提示）

### Requirements
- `.planning/REQUIREMENTS.md` — WX-01~06 详细需求定义

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **MarkdownFormatter** (`src/core/formatter.py`): Phase 1已实现，输出标准Markdown表格，作为消息内容源
- **项目结构**: `src/core/` 模块模式，WeChat客户端应放在 `src/core/` 或 `src/services/`

### Established Patterns
- **轻量级优先**: Phase 1选择轻量方案（openpyxl而非pandas），Phase 2保持一致——使用标准库+json+requests
- **中文错误提示**: Phase 1使用简洁中文错误消息，Phase 2延续此风格
- **直接报错退出**: Phase 1不实现复杂容错（列缺失直接退出），Phase 2对配置错误同样直接报错

### Integration Points
- **输入**: MarkdownFormatter生成的Markdown字符串 → WeChatWorkClient.send_markdown()
- **配置**: WeChatWorkClient读取本地JSON配置 → 获取webhook URL
- **输出**: 发送成功/失败状态 → 调用者（Phase 3 GUI或命令行）
- **文件**: 配置文件存储在项目目录 `config/webhook_config.json`（需创建并.gitignore）

</code_context>

<specifics>
## Specific Ideas

- 消息切片示例：
  ```
  （第1/3片）
  | 日期 | 发货人 | ... |
  | ... | ... | ... |
  （数据行1-15）
  ```

- 配置JSON示例：
  ```json
  {
    "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
    "last_folder": "/Users/xxx/Documents"
  }
  ```

- 错误提示风格（与Phase 1一致）：
  - ❌ "Connection timeout" → ✅ "网络连接超时，请检查网络后重试"
  - ❌ "Invalid webhook URL" → ✅ "webhook地址无效，请检查配置"

</specifics>

<deferred>
## Deferred Ideas

- **配置文件加密** — 当前阶段采用明文存储，未来可考虑keyring库或简单混淆
- **异步发送** — 当前使用同步请求，GUI Phase中考虑多线程避免阻塞
- **requests.Session** — 当前每次新建连接，未来大量消息时可优化为Session复用
- **动态行数计算** — 当前固定15行，未来可根据实际行长度动态调整
- **配置导入/导出** — GUI Phase功能，支持备份和迁移配置
- **发送历史记录** — v2需求，当前Phase不实现

</deferred>

---

*Phase: 02-wechat-integration*
*Context gathered: 2026-04-20*
