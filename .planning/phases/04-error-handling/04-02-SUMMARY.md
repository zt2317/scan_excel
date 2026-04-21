---
phase: 04-error-handling
plan: 02
wave: 2
status: complete
completed: 2026-04-21
depends_on:
  - 04-01
requirements:
  - ERR-02
  - ERR-03
---

# Plan 04-02: GUI错误集成

## 目标
在GUI层集成错误处理，实现ERR-02（网络超时提示）和ERR-03（webhook无效提示），并添加全局异常处理。

## 已完成

### Task 1: 添加错误处理辅助方法
在 `src/gui/main_window.py` 中添加了四个错误处理辅助方法：

1. **`_show_error()`** - 分级错误显示方法
   - 支持三种级别：'error'（弹窗）、'warning'（弹窗）、'info'（状态栏）
   - 支持可选的解决建议（suggestion）
   - 支持重试按钮（show_retry）

2. **`_handle_network_error()`** - 网络错误处理
   - 检测超时错误并显示专门提示
   - 提供"重新发送"重试选项
   - 返回用户是否选择重试

3. **`_handle_webhook_error()`** - Webhook错误处理
   - 识别错误码40013（key无效）
   - 显示具体的配置建议
   - 列出可能的原因（key复制错误、机器人被删除、机器人被禁用）

4. **`_handle_excel_error()`** - Excel错误处理
   - 根据 error_code 显示对应的错误标题
   - 支持密码保护、文件损坏、格式不支持等类型

### Task 2: 更新现有错误处理
修改了后台线程的错误处理：

1. **`_load_excel_thread()`** - 添加 ExcelFormatError 捕获
   - 通过 worker_queue 传递 excel_error 类型消息
   - 在主线程使用 `_handle_excel_error()` 显示错误

2. **`_send_thread()`** - 更新 WeChatAPIError 和 NetworkError 处理
   - 通过 worker_queue 传递 webhook_error 和 network_error 类型消息
   - 在主线程使用对应的方法处理错误

3. **`_handle_worker_message()`** - 添加新消息类型处理
   - 处理 excel_error：调用 `_handle_excel_error()`
   - 处理 webhook_error：调用 `_handle_webhook_error()`
   - 处理 network_error：调用 `_handle_network_error()`，支持重试

### Task 3: 添加全局异常处理器
在 `src/app.py` 中添加了全局异常处理：

1. **`setup_global_exception_handler()`** - 设置全局异常处理器
   - 捕获所有未处理的 Tkinter 回调异常
   - 记录完整错误信息到 stderr（用于调试）
   - 显示用户友好的中文错误消息
   - 防止应用崩溃

2. **修改 `main()` 函数**
   - 先创建 Tk 根窗口
   - 设置全局异常处理器
   - 再创建 MainWindow 实例
   - 启动主循环

3. **修改 MainWindow 初始化**
   - 更新 `__init__` 接受可选的 root 参数
   - 如果提供了 root 则使用，否则创建新的 Tk 窗口

## Key Files Created/Modified

| File | Type | Description |
|------|------|-------------|
| `src/gui/main_window.py` | Modified | 添加错误处理辅助方法和更新错误处理 |
| `src/app.py` | Modified | 添加全局异常处理器 |

## Requirements Coverage

- ✓ ERR-02: 网络超时提示并可重试
- ✓ ERR-03: webhook URL无效时提示

## Verification

- [x] 网络超时显示弹窗并提供"重试"选项
- [x] 点击"重试"后重新执行发送操作
- [x] webhook无效错误显示具体的配置建议
- [x] Excel格式错误显示对应的中文消息
- [x] 任何未捕获异常都被全局处理器捕获
- [x] 全局异常显示"程序错误"标题和友好消息
- [x] 应用不会因未处理异常崩溃

## Self-Check: PASSED

- 代码符合项目编码规范
- 错误消息均为中文，符合 D-01 决策
- 不暴露技术细节，符合 D-02 决策
- 错误分级处理（严重弹窗/一般状态栏），符合 D-03 决策
- 每个错误都包含解决建议，符合 D-05 决策
- 全局异常处理确保应用不崩溃，符合 D-06 决策
