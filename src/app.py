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
import tkinter as tk
from pathlib import Path

# Add src to path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gui.main_window import MainWindow


def setup_global_exception_handler(root):
    """设置全局异常处理器
    
    捕获所有未处理的Tkinter回调异常，防止应用崩溃。
    显示用户友好的中文错误消息，同时记录详细错误供调试。
    
    Args:
        root: Tk根窗口实例
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        import traceback
        
        # 记录完整错误信息（用于调试）
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"[未捕获异常] {error_msg}", file=sys.stderr)
        
        # 显示用户友好的错误消息（中文）
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "程序错误",
            "抱歉，程序遇到了意外错误。\n\n"
            "请尝试重新启动应用。如果问题持续存在，请联系技术支持。\n\n"
            f"错误类型：{exc_type.__name__}"
        )
    
    # 覆盖Tkinter的异常报告
    root.report_callback_exception = handle_exception


def main():
    """应用程序主入口"""
    # 创建Tk根窗口
    root = tk.Tk()
    
    # 设置全局异常处理
    setup_global_exception_handler(root)
    
    # 创建主窗口
    app = MainWindow(root)
    
    # 启动主循环
    root.mainloop()


if __name__ == '__main__':
    main()
