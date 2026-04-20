# 架构研究

## 应用架构

### 整体结构

```
┌─────────────────────────────────────┐
│           GUI Layer (Tkinter)        │
│  - 文件选择对话框                     │
│  - 数据预览表格                       │
│  - 配置输入界面                       │
│  - 状态显示                           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Business Logic Layer         │
│  - Excel读取器 (openpyxl/xlrd)       │
│  - Markdown格式化器                   │
│  - 消息切片器                         │
│  - 企业微信客户端                      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           Config Layer               │
│  - webhook URL存储                    │
│  - 用户偏好设置                       │
│  - 列名映射配置                       │
└─────────────────────────────────────┘
```

### 模块设计

**main.py**
- 应用入口
- 初始化Tkinter主窗口
- 启动主循环

**gui/app.py**
- 主窗口布局
- 事件绑定
- 状态管理

**core/excel_reader.py**
- 读取Excel文件
- 列识别与映射
- 数据验证

**core/formatter.py**
- Markdown表格生成
- 格式化配置

**core/wechat_client.py**
- Webhook调用
- 消息切片与发送
- 错误处理

**core/config.py**
- 配置读写
- 持久化存储

## 数据流

```
1. 用户选择Excel文件
   ↓
2. ExcelReader读取数据
   ↓
3. 识别目标列（日期、发货人、提单号、入库未扫、出库未扫）
   ↓
4. 显示预览（前10行）
   ↓
5. 用户点击"发送"
   ↓
6. Formatter生成Markdown
   ↓
7. Slicer按长度切片
   ↓
8. WeChatClient依次发送
   ↓
9. 显示发送结果
```

## 文件结构

```
scan_excel/
├── main.py                 # 入口
├── requirements.txt        # 依赖
├── app.spec               # PyInstaller配置
├── .github/
│   └── workflows/
│       └── build.yml      # GitHub Actions打包
├── src/
│   ├── __init__.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app.py         # 主界面
│   │   └── widgets.py     # 自定义组件
│   ├── core/
│   │   ├── __init__.py
│   │   ├── excel_reader.py
│   │   ├── formatter.py
│   │   ├── wechat_client.py
│   │   └── config.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   └── test_*.py
└── assets/
    ├── icon.ico           # Windows图标
    └── icon.icns          # macOS图标
```

## 构建流程

### 本地开发（Mac）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行测试
python -m pytest tests/

# 3. 本地运行（功能测试）
python main.py
```

### CI构建（GitHub Actions → Windows）

```yaml
# 触发：push到main分支
# 环境：windows-latest
# 步骤：
#   1. Checkout代码
#   2. 安装Python 3.11
#   3. 安装依赖
#   4. PyInstaller打包
#   5. 上传Artifact
```

## 依赖关系

**运行时依赖：**
- openpyxl → 解析.xlsx
- xlrd → 解析.xls
- requests → HTTP调用

**开发依赖：**
- pytest → 测试
- pyinstaller → 打包

**无运行时依赖：**
- 打包后所有依赖都内置在exe中
- 用户无需安装Python

## 扩展性考虑

**插件化列映射**
- 配置文件中定义列名映射
- 支持不同Excel模板

**多语言支持（预留）**
- 界面文字抽离到配置文件
- 当前仅中文

**日志记录**
- 本地日志文件记录操作
- 便于问题排查

---
*研究完成: 2026-04-20*
