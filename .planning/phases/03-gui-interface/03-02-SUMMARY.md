---
phase: 03-gui-interface
plan: 02
wave: 2
status: complete
completed: 2026-04-20
type: execute
---

# Phase 3, Plan 02: 文件选择和数据预览 - 执行总结

## 完成目标
实现文件选择功能和数据预览表格，包括后台线程读取Excel和Treeview数据显示。

## 实现内容

### 1. 文件选择功能 (_on_select_file)
**文件对话框 (D-28)**
- 使用`filedialog.askopenfilename()`打开选择对话框
- 过滤器配置：Excel文件、xlsx、xls、所有文件
- 标题："选择Excel文件"
- 初始目录：从ConfigStore获取上次目录，默认Documents

**路径处理**
- 更新`file_path_var`显示选中路径
- 存储`current_file`为Path对象
- 自动保存文件夹到配置：`config_store.set_last_folder()`

### 2. 后台线程加载 (_start_loading, _load_excel_thread)
**启动加载 (D-05)**
- `_start_loading()`: 设置处理状态，更新UI，启动后台线程
- 使用`threading.Thread(daemon=True)`创建后台线程

**加载流程**
1. **10%**: 开始读取Excel文件
2. **30%**: 读取完成，开始识别列
3. **50%**: 列识别完成，开始提取数据
4. **70%**: 数据提取中
5. **90%**: 准备预览
6. **100%**: 完成，发送`update_preview`信号

**错误处理 (D-17)**
- 空文件：弹窗提示"Excel文件为空或格式不正确"
- 读取异常：弹窗提示具体错误信息
- 所有错误通过`worker_queue`传递到主线程显示

### 3. Treeview预览表格
**列配置 (D-15)**
```python
columns = ["日期", "发货人", "提单号", "入库未扫", "出库未扫"]
```

**显示设置 (D-12)**
- 最多显示20行数据（比Phase 1的10行更多）
- 使用`height=10`控制Treeview显示行数

**滚动支持 (D-14)**
- 垂直滚动条：始终显示
- 水平滚动条：按需显示

**交替行颜色 (D-16)**
```python
self.preview_tree.tag_configure('even', background='#f0f0f0')
self.preview_tree.tag_configure('odd', background='white')
```
每行根据索引应用'even'或'odd'标签

**自适应列宽 (D-13)**
`_adjust_column_widths()`方法：
- 计算表头宽度：`len(col) * 15`
- 计算内容最大宽度：遍历所有单元格
- 设置列宽：`min(max_content_width + 20, 200)`（最大200像素限制）

### 4. 消息处理增强 (_handle_worker_message)
新增消息类型处理：
- `error`: 显示错误弹窗，重置进度和状态
- `update_preview`: 调用`_update_preview()`刷新表格
- `progress`和`status`: 更新进度条和状态文字
- `done`: 标记处理完成

### 5. 发送按钮状态 (_update_send_button)
启用条件检查（4个条件必须全部满足）：
1. `has_file`: `current_file is not None`
2. `has_data`: `len(self.current_data) > 0`
3. `has_webhook`: webhook地址已配置
4. `not_processing`: 当前没有后台操作

## 关键决策实现

| 决策ID | 描述 | 实现方式 |
|--------|------|----------|
| D-05 | Excel后台读取 | threading.Thread读取Excel，避免UI阻塞 |
| D-09 | UI更新轮询 | `_check_queue()`每100ms检查队列 |
| D-10 | 线程安全 | 所有UI更新通过worker_queue在主线程执行 |
| D-11 | Treeview控件 | ttk.Treeview显示数据表格 |
| D-12 | 20行预览 | `_update_preview()`限制max_rows=20 |
| D-13 | 自适应列宽 | `_adjust_column_widths()`计算内容宽度 |
| D-14 | 滚动条 | 垂直始终显示，水平按需 |
| D-15 | 5目标列 | 列名：日期、发货人、提单号、入库未扫、出库未扫 |
| D-16 | 交替背景色 | tag_configure('even', 'odd') |
| D-17 | 错误弹窗 | messagebox.showerror()显示严重错误 |
| D-28 | 文件对话框 | filedialog.askopenfilename() |

## 代码统计

| 文件 | 变更 | 说明 |
|------|------|------|
| src/gui/main_window.py | +225/-6 | 添加文件选择和预览功能 |
| tests/test_gui_file_selection.py | 73 | 集成测试 |
| **总计** | **+298** | |

## 方法清单

### 新增方法
- `_on_select_file()`: 处理文件选择按钮
- `_start_loading()`: 开始后台加载
- `_load_excel_thread()`: 后台线程读取Excel
- `_update_preview()`: 更新预览表格
- `_adjust_column_widths()`: 自适应调整列宽

### 更新方法
- `_handle_worker_message()`: 新增error和update_preview处理
- `_create_preview_frame()`: 配置Treeview列和样式
- `_update_send_button()`: 添加has_data检查

## 技术债务/待办

- [ ] `_on_send()` 在Plan 03中实现
- [ ] `_set_status_color()` 在Plan 03中实现（状态颜色）
- [ ] 配置保存按钮在Plan 03中实现

## 验证检查点

- [x] _on_select_file opens filedialog with correct filters
- [x] Last folder saved to config after selection
- [x] _load_excel_thread runs in background thread
- [x] Progress updates via worker_queue
- [x] Errors shown in messagebox (not status bar)
- [x] Treeview configured with 5 columns
- [x] Alternating row colors configured
- [x] _update_preview shows max 20 rows
- [x] Column widths adjusted based on content
- [x] Send button state correctly updated after loading

## Self-Check: PASSED

✓ 所有任务按规范完成
✓ 文件选择和预览功能完整
✓ 后台线程不阻塞UI
✓ 错误处理符合D-17要求
✓ 提交原子化
