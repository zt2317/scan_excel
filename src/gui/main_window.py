"""
Excel数据推送助手 - 主窗口模块

提供Tkinter-based主窗口，包含5个功能区域：
1. 文件选择区
2. 数据预览区
3. Webhook配置区
4. 发送按钮区
5. 状态栏区
"""

# DPI Awareness (Windows)
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass  # Non-Windows or old version

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Dict, Any
import threading
import queue
from pathlib import Path

# Import core modules
from ..core import (
    ExcelReader, ColumnDetector, MarkdownFormatter,
    generate_preview, ConfigStore, WeChatWorkClient
)
from ..core.exceptions import WeChatAPIError, NetworkError


class MainWindow:
    """主窗口类 - Excel数据推送助手GUI"""
    
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Excel数据推送助手")
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.resizable(False, False)  # D-02: Fixed size
        
        # Center window
        self._center_window()
        
        # Core components
        self.config_store = ConfigStore()
        self.excel_reader = ExcelReader()
        self.column_detector = ColumnDetector()
        self.formatter = MarkdownFormatter()
        
        # State
        self.current_file: Optional[Path] = None
        self.current_data: List[Dict] = []
        self.is_processing = False
        
        # Threading
        self.worker_queue = queue.Queue()
        self._check_queue()
        
        # Build UI
        self._create_styles()
        self._create_widgets()
        
    def _center_window(self):
        """居中显示窗口 (D-04)"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.WINDOW_HEIGHT // 2)
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")
    
    def _create_styles(self):
        """创建ttk样式 (D-31)"""
        self.style = ttk.Style()
        # Use default theme, no custom font (D-32: system default font)
    
    def _create_widgets(self):
        """创建5个功能区域 (D-01~D-03)"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. File selection frame
        self._create_file_frame(main_frame)
        
        # 2. Preview frame
        self._create_preview_frame(main_frame)
        
        # 3. Config frame
        self._create_config_frame(main_frame)
        
        # 4. Send button frame
        self._create_send_frame(main_frame)
        
        # 5. Status frame
        self._create_status_frame(main_frame)
    
    def _create_file_frame(self, parent):
        """文件选择区域 (GUI-02)"""
        frame = ttk.LabelFrame(parent, text="文件选择", padding="5")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_path_var = tk.StringVar(value="请选择Excel文件")
        path_entry = ttk.Entry(frame, textvariable=self.file_path_var, state="readonly")
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        select_btn = ttk.Button(frame, text="选择文件", command=self._on_select_file)
        select_btn.pack(side=tk.RIGHT)
    
    def _create_preview_frame(self, parent):
        """数据预览区域 (GUI-03, D-11~D-16)"""
        frame = ttk.LabelFrame(parent, text="数据预览", padding="5")
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview with scrollbars
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_tree = ttk.Treeview(tree_frame, show="headings")
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.preview_tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.configure(yscrollcommand=vsb.set)
        
        # Horizontal scrollbar (D-14: as needed)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.preview_tree.xview)
        hsb.pack(fill=tk.X)
        self.preview_tree.configure(xscrollcommand=hsb.set)
    
    def _create_config_frame(self, parent):
        """配置区域 (GUI-04, D-28~D-29)"""
        frame = ttk.LabelFrame(parent, text="企业微信配置", padding="5")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Webhook地址：").pack(side=tk.LEFT)
        
        self.webhook_var = tk.StringVar()
        self.webhook_entry = ttk.Entry(frame, textvariable=self.webhook_var)
        self.webhook_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Load existing config
        existing_url = self.config_store.get_webhook_url()
        if existing_url:
            self.webhook_var.set(existing_url)
    
    def _create_send_frame(self, parent):
        """发送按钮区域 (GUI-05, D-30)"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        self.send_btn = ttk.Button(
            frame, 
            text="发送消息", 
            command=self._on_send,
            state="disabled"  # D-30: Disabled by default
        )
        self.send_btn.pack()
    
    def _create_status_frame(self, parent):
        """状态栏区域 (GUI-06, D-22~D-27)"""
        frame = ttk.LabelFrame(parent, text="状态", padding="5")
        frame.pack(fill=tk.X)
        
        # Status text line 1
        self.status_var = tk.StringVar(value="准备就绪")
        self.status_label = ttk.Label(frame, textvariable=self.status_var)
        self.status_label.pack(anchor=tk.W)
        
        # Progress bar line 2
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            frame, 
            variable=self.progress_var,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
    
    def _check_queue(self):
        """检查后台线程队列 (D-09: after() polling)"""
        try:
            while True:
                msg = self.worker_queue.get_nowait()
                self._handle_worker_message(msg)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._check_queue)  # Check every 100ms
    
    def _handle_worker_message(self, msg: Dict):
        """处理后台线程消息"""
        msg_type = msg.get('type')
        if msg_type == 'progress':
            self.progress_var.set(msg.get('value', 0))
        elif msg_type == 'status':
            self.status_var.set(msg.get('text', ''))
        elif msg_type == 'done':
            self.is_processing = False
            self._update_send_button()
    
    def _update_send_button(self):
        """更新发送按钮状态 (D-30: enable conditions)"""
        # Enable if: file selected AND data loaded AND webhook configured
        has_file = self.current_file is not None
        has_data = len(self.current_data) > 0
        has_webhook = bool(self.webhook_var.get().strip())
        not_processing = not self.is_processing
        
        if has_file and has_data and has_webhook and not_processing:
            self.send_btn.config(state="normal")
        else:
            self.send_btn.config(state="disabled")
    
    def _on_select_file(self):
        """处理文件选择 (D-05: background thread)"""
        # To be implemented in Plan 02
        pass
    
    def _on_send(self):
        """处理发送消息 (D-06: background thread)"""
        # To be implemented in Plan 03
        pass
    
    def run(self):
        """启动主循环"""
        self.root.mainloop()
