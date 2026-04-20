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
try:
    from core import (
        ExcelReader, ColumnDetector, MarkdownFormatter,
        generate_preview, ConfigStore, WeChatWorkClient
    )
    from core.exceptions import WeChatAPIError, NetworkError
except ImportError:
    # Fallback for relative imports when running as module
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
        
        # Define columns (D-15: 5 target columns)
        columns = ["日期", "发货人", "提单号", "入库未扫", "出库未扫"]
        
        self.preview_tree = ttk.Treeview(
            tree_frame, 
            show="headings",
            columns=columns,
            height=10  # Show ~10 rows at a time
        )
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure column headers and widths (D-13: adaptive column widths)
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=100, anchor="w")
        
        # Vertical scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.preview_tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.configure(yscrollcommand=vsb.set)
        
        # Horizontal scrollbar (D-14: as needed)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.preview_tree.xview)
        hsb.pack(fill=tk.X)
        self.preview_tree.configure(xscrollcommand=hsb.set)
        
        # Alternating row colors (D-16)
        self.preview_tree.tag_configure('even', background='#f0f0f0')
        self.preview_tree.tag_configure('odd', background='white')
    
    def _create_config_frame(self, parent):
        """配置区域 (GUI-04, D-28~D-29)"""
        frame = ttk.LabelFrame(parent, text="企业微信配置", padding="5")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Webhook地址：").pack(side=tk.LEFT)
        
        self.webhook_var = tk.StringVar()
        self.webhook_entry = ttk.Entry(frame, textvariable=self.webhook_var, width=50)
        self.webhook_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Add save button
        save_btn = ttk.Button(frame, text="保存", command=self._on_save_config, width=6)
        save_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Bind webhook change to update button state
        self.webhook_var.trace_add('write', self._on_webhook_changed)
        
        # Load existing config
        existing_url = self.config_store.get_webhook_url()
        if existing_url:
            self.webhook_var.set(existing_url)

    def _on_webhook_changed(self, *args):
        """webhook地址改变时更新按钮状态"""
        self._update_send_button()

    def _on_save_config(self):
        """保存webhook配置"""
        webhook_url = self.webhook_var.get().strip()
        
        if not webhook_url:
            messagebox.showwarning("配置错误", "请输入webhook地址")
            return
        
        try:
            self.config_store.set_webhook_url(webhook_url)
            self.status_var.set("配置已保存")
            self._set_status_color("success")  # D-26: green for success
            self._update_send_button()
        except Exception as e:
            messagebox.showerror("保存失败", f"保存配置时出错：{str(e)}")

    def _set_status_color(self, state: str):
        """设置状态文字颜色 (D-26: color-coded status)
        
        state: 'default' | 'processing' | 'success' | 'error'
        """
        colors = {
            'default': 'black',
            'processing': 'blue',
            'success': 'green',
            'error': 'red'
        }
        color = colors.get(state, 'black')
        
        # Update label foreground color
        self.status_label.configure(foreground=color)
    
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
        
        # Status text line 1 - Store reference to label
        self.status_var = tk.StringVar(value="准备就绪")
        self.status_label = ttk.Label(
            frame, 
            textvariable=self.status_var,
            foreground="black"  # D-26: default black
        )
        self.status_label.pack(anchor=tk.W)
        
        # Progress bar line 2 (D-22: determinate progress bar)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            frame, 
            variable=self.progress_var,
            mode='determinate',
            maximum=100,
            length=760
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
        """处理后台线程消息 (D-09: main thread handles UI updates)"""
        msg_type = msg.get('type')
        
        if msg_type == 'progress':
            self.progress_var.set(msg.get('value', 0))
        
        elif msg_type == 'status':
            self.status_var.set(msg.get('text', ''))
        
        elif msg_type == 'error':
            # Show error dialog (D-17: serious errors show popup)
            self.is_processing = False
            self._update_send_button()
            self.progress_var.set(0)
            self._set_status_color("error")  # D-26: red for error
            messagebox.showerror(
                msg.get('title', '错误'),
                msg.get('message', '发生未知错误')
            )
        
        elif msg_type == 'update_preview':
            # Update the preview tree
            self._update_preview()
            self._update_send_button()  # Re-check if send button should be enabled
        
        elif msg_type == 'send_complete':
            # Handle send completion
            self.is_processing = False
            self._update_send_button()
            self.progress_var.set(100)
            
            if msg.get('success'):
                # Success - show info dialog (D-18: popup for important status)
                self._set_status_color("success")  # D-26: green
                self.status_var.set(msg.get('message', '发送成功'))
                messagebox.showinfo(
                    msg.get('title', '完成'),
                    msg.get('message', '操作完成')
                )
            else:
                # Failure - show error dialog (D-17: popup for errors)
                self._set_status_color("error")  # D-26: red
                self.status_var.set(msg.get('message', '发送失败'))
                messagebox.showerror(
                    msg.get('title', '错误'),
                    msg.get('message', '发送失败')
                )
        
        elif msg_type == 'done':
            self.is_processing = False
            self._update_send_button()
    
    def _update_send_button(self):
        """更新发送按钮状态 (D-30: enable conditions)"""
        # Enable if: file selected AND data loaded AND webhook configured AND not processing
        has_file = self.current_file is not None
        has_data = len(self.current_data) > 0
        has_webhook = bool(self.webhook_var.get().strip())
        not_processing = not self.is_processing
        
        if has_file and has_data and has_webhook and not_processing:
            self.send_btn.config(state="normal")
        else:
            self.send_btn.config(state="disabled")
    
    def _on_select_file(self):
        """处理文件选择按钮点击 (D-28)"""
        # Get last folder from config
        last_folder = self.config_store.get_last_folder()
        if not last_folder or not Path(last_folder).exists():
            last_folder = str(Path.home() / "Documents")
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            initialdir=last_folder,
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("Excel 2007+", "*.xlsx"),
                ("Excel 97-2003", "*.xls"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return  # User cancelled
        
        # Update path display
        self.file_path_var.set(file_path)
        self.current_file = Path(file_path)
        
        # Save folder to config
        self.config_store.set_last_folder(str(self.current_file.parent))
        
        # Start background loading (D-05)
        self._start_loading()

    def _start_loading(self):
        """开始加载Excel文件"""
        self.is_processing = True
        self._update_send_button()
        self.status_var.set("正在读取Excel文件...")
        self.progress_var.set(0)
        self._set_status_color("processing")  # D-26: blue for processing
        
        # Start background thread (D-05, D-06)
        thread = threading.Thread(target=self._load_excel_thread, daemon=True)
        thread.start()

    def _load_excel_thread(self):
        """后台线程：读取Excel文件 (D-05)"""
        try:
            if not self.current_file:
                return
            
            # Update progress via queue
            self.worker_queue.put({'type': 'progress', 'value': 10})
            self.worker_queue.put({'type': 'status', 'text': '正在读取Excel文件...'})
            
            # Read Excel (Phase 1 component)
            raw_data = self.excel_reader.read(str(self.current_file))
            
            self.worker_queue.put({'type': 'progress', 'value': 30})
            self.worker_queue.put({'type': 'status', 'text': '正在识别列...'})
            
            if not raw_data or len(raw_data) < 2:
                self.worker_queue.put({
                    'type': 'error',
                    'message': 'Excel文件为空或格式不正确',
                    'title': '文件错误'
                })
                return
            
            # Detect columns (Phase 1 component)
            headers = raw_data[0]
            column_map = self.column_detector.detect(headers)
            
            self.worker_queue.put({'type': 'progress', 'value': 50})
            self.worker_queue.put({'type': 'status', 'text': '正在提取数据...'})
            
            # Extract data
            extracted = self.column_detector.extract_data(raw_data, column_map)
            
            self.worker_queue.put({'type': 'progress', 'value': 70})
            self.worker_queue.put({'type': 'status', 'text': '正在准备预览...'})
            
            # Store data
            self.current_data = extracted
            
            self.worker_queue.put({'type': 'progress', 'value': 90})
            self.worker_queue.put({
                'type': 'status', 
                'text': f'读取完成，共{len(extracted)}行数据'
            })
            
            # Signal to update preview
            self.worker_queue.put({'type': 'update_preview'})
            self.worker_queue.put({'type': 'progress', 'value': 100})
            
        except Exception as e:
            self.worker_queue.put({
                'type': 'error',
                'message': f'读取Excel文件失败：{str(e)}',
                'title': '读取错误'
            })
        finally:
            self.worker_queue.put({'type': 'done'})

    def _update_preview(self):
        """更新预览表格 (D-12: show 20 rows)"""
        # Clear existing data
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        if not self.current_data:
            return
        
        # Show up to 20 rows (D-12: increased from Phase 1's 10)
        max_rows = 20
        display_data = self.current_data[:max_rows]
        
        for i, row in enumerate(display_data):
            values = [
                row.get('日期', '-'),
                row.get('发货人', '-'),
                row.get('提单号', '-'),
                row.get('入库未扫', '-'),
                row.get('出库未扫', '-')
            ]
            
            # Alternating row colors (D-16)
            tag = 'even' if i % 2 == 0 else 'odd'
            self.preview_tree.insert('', 'end', values=values, tags=(tag,))
        
        # Adjust column widths based on content (D-13)
        self._adjust_column_widths()

    def _adjust_column_widths(self):
        """根据内容自适应调整列宽 (D-13)"""
        for col in self.preview_tree['columns']:
            # Get max width needed
            header_width = len(col) * 15  # Estimate header width
            
            max_content_width = header_width
            for item in self.preview_tree.get_children():
                cell_value = self.preview_tree.set(item, col)
                cell_width = len(str(cell_value)) * 10
                max_content_width = max(max_content_width, cell_width)
            
            # Set width with some padding
            self.preview_tree.column(col, width=min(max_content_width + 20, 200))

    def _on_send(self):
        """处理发送按钮点击 (D-06: background thread)"""
        webhook_url = self.webhook_var.get().strip()
        
        if not webhook_url:
            messagebox.showerror("配置错误", "请先配置webhook地址")
            return
        
        if not self.current_data:
            messagebox.showerror("数据错误", "请先选择并加载Excel文件")
            return
        
        # Confirm send
        total_rows = len(self.current_data)
        confirm = messagebox.askyesno(
            "确认发送",
            f"确定要发送 {total_rows} 行数据到企业微信吗？"
        )
        if not confirm:
            return
        
        # Start sending
        self._start_sending(webhook_url)

    def _start_sending(self, webhook_url: str):
        """开始发送消息"""
        self.is_processing = True
        self._update_send_button()
        self.progress_var.set(0)
        self._set_status_color("processing")  # D-26: blue for processing
        
        # Format data to markdown
        self.worker_queue.put({'type': 'status', 'text': '正在格式化数据...'})
        markdown = self.formatter.format(self.current_data)
        
        # Start background thread (D-06)
        thread = threading.Thread(
            target=self._send_thread,
            args=(webhook_url, markdown),
            daemon=True
        )
        thread.start()

    def _send_thread(self, webhook_url: str, markdown: str):
        """后台线程：发送消息到企业微信 (D-06)"""
        try:
            # Create client
            client = WeChatWorkClient(webhook_url=webhook_url)
            
            # Count chunks for progress (Phase 2 client splits automatically)
            # We need to estimate or get from client
            self.worker_queue.put({'type': 'status', 'text': '正在发送消息...'})
            self.worker_queue.put({'type': 'progress', 'value': 10})
            
            # Send message
            # Note: WeChatWorkClient.send_markdown handles splitting internally
            # and returns results for each chunk
            results = client.send_markdown(markdown)
            
            # Update progress based on results
            if results:
                success_count = sum(1 for r in results if r.get('success'))
                total_count = len(results)
                progress = 10 + int(90 * success_count / total_count) if total_count > 0 else 100
                self.worker_queue.put({'type': 'progress', 'value': progress})
            
            # Check results
            all_success = all(r.get('success') for r in results)
            
            if all_success:
                total_chunks = len(results)
                self.worker_queue.put({
                    'type': 'send_complete',
                    'success': True,
                    'message': f'消息发送成功！共发送{total_chunks}片消息',
                    'title': '发送成功'
                })
            else:
                # Find first error
                failed_results = [r for r in results if not r.get('success')]
                if failed_results:
                    first_error = failed_results[0].get('error', '未知错误')
                    self.worker_queue.put({
                        'type': 'send_complete',
                        'success': False,
                        'message': f'发送失败：{first_error}',
                        'title': '发送失败'
                    })
        
        except WeChatAPIError as e:
            self.worker_queue.put({
                'type': 'send_complete',
                'success': False,
                'message': f'企业微信API错误：{str(e)}',
                'title': '发送失败'
            })
        
        except NetworkError as e:
            self.worker_queue.put({
                'type': 'send_complete',
                'success': False,
                'message': f'网络错误：{str(e)}',
                'title': '网络错误'
            })
        
        except Exception as e:
            self.worker_queue.put({
                'type': 'send_complete',
                'success': False,
                'message': f'发送时出错：{str(e)}',
                'title': '错误'
            })
        
        finally:
            self.worker_queue.put({'type': 'progress', 'value': 100})
            self.worker_queue.put({'type': 'done'})
    
    def run(self):
        """启动主循环"""
        self.root.mainloop()
