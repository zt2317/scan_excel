# 技术栈研究

## 项目背景
- 开发环境：macOS
- 目标平台：Windows 10/11
- 应用类型：Python GUI桌面应用

## 推荐技术栈

### 核心技术

**Python 3.11**
- 选择理由：稳定、性能好、支持最新特性
- PyInstaller打包兼容性：优秀

**GUI框架：Tkinter**
- 内置库，无需额外依赖
- 轻量级，打包体积小
- 跨平台原生支持
- Windows用户界面习惯

**Excel处理**

| 库 | 用途 | 版本 |
|----|------|------|
| `openpyxl` | 读取.xlsx文件 | 3.1.2+ |
| `xlrd` | 读取.xls文件（旧版） | 2.0.1+ |

**HTTP客户端**
- `requests` - 企业微信webhook调用
- 支持超时、重试机制

### 依赖清单

```
openpyxl>=3.1.2
xlrd>=2.0.1
requests>=2.31.0
pyinstaller>=6.0.0
```

## Mac→Windows打包方案对比

### 方案1：GitHub Actions（推荐）

**实现方式：**
- 使用GitHub Actions Windows runner
- 配置workflow自动打包
- 生成Windows可执行文件
- 下载到本地或发布Release

**优点：**
- 原生Windows环境编译，兼容性最佳
- 自动化，无需手动操作
- 免费（公开仓库）
- 可配置多版本Python测试

**缺点：**
- 需要网络连接
- 需要GitHub账号

**配置示例：**
```yaml
name: Build Windows EXE
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pyinstaller openpyxl xlrd requests
      - run: pyinstaller --onefile --windowed app.py
      - uses: actions/upload-artifact@v4
        with:
          name: windows-exe
          path: dist/
```

### 方案2：Wine + PyInstaller（不推荐）

**实现方式：**
- 在Mac安装Wine
- 安装Windows版Python
- 运行PyInstaller

**问题：**
- 配置复杂，容易出错
- 打包结果不稳定
- 某些库可能无法正常工作
- Wine兼容性有限

**适用场景：**
- 无网络环境
- 必须本地打包

### 方案3：虚拟机/远程Windows

**实现方式：**
- 本地虚拟机（Parallels/VMware）
- 或使用云Windows服务器

**优点：**
- 完全原生环境
- 调试方便

**缺点：**
- 需要Windows许可证
- 资源占用大

## 建议决策

**推荐方案：GitHub Actions**

理由：
1. 零配置成本，开箱即用
2. 官方原生Windows环境
3. 自动化CI/CD流程
4. 可随时重新打包
5. 团队协作友好

**备选方案：本地虚拟机**
- 当无法使用GitHub Actions时
- 需要频繁调试Windows特定问题时

## 打包配置建议

```bash
# 单文件模式，无控制台窗口
pyinstaller --onefile --windowed \
  --name "Excel数据推送助手" \
  --icon=app.ico \
  --add-data "config.json;." \
  main.py
```

**打包选项说明：**
- `--onefile`：打包为单个exe文件
- `--windowed`：不显示控制台窗口（GUI应用）
- `--icon`：应用图标
- `--add-data`：包含额外配置文件

## 风险提示

1. **PyInstaller不支持交叉编译**
   - 必须原生Windows环境
   - Mac无法直接生成Windows exe

2. **反病毒软件误报**
   - PyInstaller打包的exe可能被误报
   - 建议：代码签名（可选）

3. **依赖兼容性**
   - 某些库在Windows/Mac表现不同
   - 建议：在Windows环境充分测试

---
*研究完成: 2026-04-20*
