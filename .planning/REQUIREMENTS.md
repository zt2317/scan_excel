# Requirements: Excel数据推送助手

**Defined:** 2026-04-20
**Core Value:** 用户能够一键将Excel中的物流数据推送到企业微信，及时通知相关人员处理"入库未扫"和"出库未扫"的异常数据。

## v1 Requirements

### Excel处理

- [ ] **EXCL-01**: 用户可以选择.xlsx或.xls格式的Excel文件
- [ ] **EXCL-02**: 自动识别列：日期、发货人、提单号、入库未扫、出库未扫
- [ ] **EXCL-03**: 列名不匹配时支持模糊匹配或手动映射
- [ ] **EXCL-04**: 显示数据预览（前10行）供用户确认
- [ ] **EXCL-05**: 处理空值单元格（显示为"-"）

### Markdown格式化

- [ ] **MD-01**: 将数据格式化为标准Markdown表格
- [ ] **MD-02**: 表头使用加粗显示
- [ ] **MD-03**: 日期格式统一为YYYY-MM-DD

### 企业微信推送

- [ ] **WX-01**: 用户可以配置企业微信webhook URL
- [ ] **WX-02**: webhook URL持久化保存到本地配置文件（不上传git）
- [ ] **WX-03**: 消息自动切片（每片<1800字符）
- [ ] **WX-04**: 切片消息顺序发送，间隔0.5秒避免限流
- [ ] **WX-05**: 发送成功显示确认提示
- [ ] **WX-06**: 发送失败显示错误信息

### GUI界面

- [ ] **GUI-01**: 单窗口应用，界面简洁
- [ ] **GUI-02**: 文件选择按钮 + 路径显示
- [ ] **GUI-03**: 数据预览表格
- [ ] **GUI-04**: webhook配置输入框
- [ ] **GUI-05**: 发送按钮
- [ ] **GUI-06**: 状态栏显示操作状态

### 错误处理

- [ ] **ERR-01**: Excel格式错误时友好提示
- [ ] **ERR-02**: 网络超时提示并可重试
- [ ] **ERR-03**: webhook URL无效时提示

## v2 Requirements

### 配置增强

- **CONF-01**: 支持配置默认文件夹路径
- **CONF-02**: 支持自定义列名映射

### 数据过滤

- **FILT-01**: 仅推送异常数据（入库未扫或出库未扫不为空）
- **FILT-02**: 按日期范围筛选

### 发送历史

- **HIST-01**: 记录发送日志
- **HIST-02**: 显示最近5条发送记录

## Out of Scope

| Feature | Reason |
|---------|--------|
| Excel写入功能 | 仅读取工具，不修改源文件 |
| 其他IM工具支持 | 仅企业微信，钉钉/飞书需额外适配 |
| 数据持久化存储 | 临时处理，不保存历史 |
| 复杂Excel格式 | 不支持合并单元格、图表等 |
| 多语言支持 | 仅中文界面 |
| 数据编辑功能 | 在Excel中编辑，本工具仅推送 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| EXCL-01 | Phase 1 | Pending |
| EXCL-02 | Phase 1 | Pending |
| EXCL-03 | Phase 1 | Pending |
| EXCL-04 | Phase 1 | Pending |
| EXCL-05 | Phase 1 | Pending |
| MD-01 | Phase 1 | Pending |
| MD-02 | Phase 1 | Pending |
| MD-03 | Phase 1 | Pending |
| WX-01 | Phase 2 | Pending |
| WX-02 | Phase 2 | Pending |
| WX-03 | Phase 2 | Pending |
| WX-04 | Phase 2 | Pending |
| WX-05 | Phase 2 | Pending |
| WX-06 | Phase 2 | Pending |
| GUI-01 | Phase 3 | Pending |
| GUI-02 | Phase 3 | Pending |
| GUI-03 | Phase 3 | Pending |
| GUI-04 | Phase 3 | Pending |
| GUI-05 | Phase 3 | Pending |
| GUI-06 | Phase 3 | Pending |
| ERR-01 | Phase 4 | Pending |
| ERR-02 | Phase 4 | Pending |
| ERR-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-20*
*Last updated: 2026-04-20 after initial definition*
