"""
Excel数据推送助手 - 应用程序入口

提供图形界面用于：
1. 选择Excel文件
2. 预览数据
3. 配置企业微信webhook
4. 发送数据到企业微信

使用方法:
    python src/app.py

或打包后运行:
    excel_pusher.exe
"""

import sys
from pathlib import Path

# Add src to path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gui.main_window import MainWindow


def main():
    """应用程序主入口"""
    app = MainWindow()
    app.run()


if __name__ == '__main__':
    main()
