---
phase: 04-error-handling
plan: 01
wave: 1
status: complete
completed: 2026-04-21
requirements:
  - ERR-01
---

# Plan 04-01: Excel格式错误处理

## 目标
创建Excel格式错误处理体系，为ERR-01提供完整的错误类型和中文消息支持。

## 已完成

### Task 1: 添加 ExcelFormatError 异常类
- 在 `src/core/exceptions.py` 中添加了 `ExcelFormatError` 类
- 支持 6 种错误代码：FILE_NOT_FOUND, UNSUPPORTED_FORMAT, CORRUPTED_FILE, EMPTY_FILE, PASSWORD_PROTECTED, DEPENDENCY_MISSING
- 包含 `message`, `error_code`, `suggestion` 三个属性
- 实现了自定义的 `__str__` 方法，自动组合消息和建议
- 更新了 `__all__` 列表以导出新类

### Task 2: 包装 ExcelReader 错误消息
- 在 `src/core/excel_reader.py` 中导入 `ExcelFormatError`
- 将所有错误转换为中文消息并附带解决建议：
  - 文件不存在 → "文件不存在：{path}。请确认文件路径是否正确。"
  - 不支持格式 → "不支持的文件格式"{ext}"。请使用.xlsx或.xls格式的Excel文件。"
  - 文件损坏 → "无法读取Excel文件，文件可能已损坏。请尝试用Excel打开并另存为新文件。"
  - 文件为空 → "Excel文件为空。请确保文件包含数据行（不仅是空表头）。"
  - 密码保护 → "无法打开受密码保护的Excel文件。请先移除密码保护。"
  - 依赖缺失 → "缺少必要的依赖库：openpyxl。请运行命令安装：pip install openpyxl>=3.1.2"

## Key Files Created/Modified

| File | Type | Description |
|------|------|-------------|
| `src/core/exceptions.py` | Modified | 添加 ExcelFormatError 异常类 |
| `src/core/excel_reader.py` | Modified | 包装所有错误为中文消息 |

## Requirements Coverage

- ✓ ERR-01: Excel格式错误时友好提示

## Verification

- [x] ExcelFormatError类可正常导入和使用
- [x] 所有Excel读取错误都显示中文消息
- [x] 每个错误消息包含具体的解决建议
- [x] 不暴露Python异常类型或堆栈信息给用户

## Self-Check: PASSED

- 代码符合项目编码规范
- 错误消息均为中文，符合 D-01 决策
- 不暴露技术细节，符合 D-02 决策
- 每个错误都包含解决建议，符合 D-05 决策
