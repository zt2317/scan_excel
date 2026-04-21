"""
Excel数据推送助手 - 应用程序入口 (PyQt6版本)

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
import traceback
from pathlib import Path

# Add src to path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow


def setup_global_exception_handler(app):
    """设置全局异常处理器
    
    捕获所有未处理的Qt异常，防止应用崩溃。
    显示用户友好的中文错误消息，同时记录详细错误供调试。
    
    Args:
        app: QApplication实例
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        # 记录完整错误信息（用于调试）
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"[未捕获异常] {error_msg}", file=sys.stderr)
        
        # 显示用户友好的错误消息（中文）
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("程序错误")
        msg_box.setText(
            "抱歉，程序遇到了意外错误。\n\n"
            "请尝试重新启动应用。如果问题持续存在，请联系技术支持。\n\n"
            f"错误类型：{exc_type.__name__}"
        )
        msg_box.exec()
    
    # 设置全局异常钩子
    sys.excepthook = handle_exception


def main():
    """应用程序主入口"""
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Excel数据推送助手")
    app.setApplicationVersion("1.0.0")
    
    # 设置全局异常处理
    setup_global_exception_handler(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
