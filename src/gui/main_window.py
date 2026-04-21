"""
Excel数据推送助手 - 主窗口模块 (PyQt6版本)

提供PyQt6-based主窗口，包含5个功能区域：
1. 文件选择区
2. 数据预览区
3. Webhook配置区
4. 发送按钮区
5. 状态栏区
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QProgressBar, QGroupBox, QFileDialog, QMessageBox,
    QHeaderView, QAbstractItemView, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor

# Import core modules
try:
    from core import (
        ExcelReader, ColumnDetector, MarkdownFormatter,
        generate_preview, ConfigStore, WeChatWorkClient
    )
    from core.exceptions import WeChatAPIError, NetworkError, ExcelFormatError
    from core.image_generator import ImageGenerator
except ImportError:
    # Fallback for relative imports when running as module
    from ..core import (
        ExcelReader, ColumnDetector, MarkdownFormatter,
        generate_preview, ConfigStore, WeChatWorkClient
    )
    from ..core.exceptions import WeChatAPIError, NetworkError, ExcelFormatError
    from ..core.image_generator import ImageGenerator


class WorkerThread(QThread):
    """后台工作线程基类"""
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str, str)  # title, message
    excel_error_signal = pyqtSignal(object)  # ExcelFormatError
    webhook_error_signal = pyqtSignal(object)  # WeChatAPIError
    network_error_signal = pyqtSignal(object)  # NetworkError
    completed_signal = pyqtSignal(bool, str, str)  # success, message, title
    done_signal = pyqtSignal()
    update_preview_signal = pyqtSignal(list)  # data
    
    def __init__(self):
        super().__init__()
        self._is_running = True
    
    def stop(self):
        self._is_running = False


class ExcelLoadThread(WorkerThread):
    """Excel加载后台线程"""
    
    def __init__(self, file_path: Path, excel_reader, column_detector):
        super().__init__()
        self.file_path = file_path
        self.excel_reader = excel_reader
        self.column_detector = column_detector
        self.extracted_data = []
    
    def run(self):
        try:
            self.progress_signal.emit(10)
            self.status_signal.emit('正在读取Excel文件...')
            
            # Read Excel
            raw_data = self.excel_reader.read(str(self.file_path))
            
            self.progress_signal.emit(30)
            self.status_signal.emit('正在识别列...')
            
            if not raw_data or len(raw_data) < 2:
                self.error_signal.emit('文件错误', 'Excel文件为空或格式不正确')
                return
            
            # Detect columns
            headers = raw_data[0]
            column_map = self.column_detector.detect(headers)
            
            self.progress_signal.emit(50)
            self.status_signal.emit('正在提取数据...')
            
            # Extract data
            self.extracted_data = self.column_detector.extract_data(raw_data, column_map)
            
            self.progress_signal.emit(90)
            self.status_signal.emit(f'读取完成，共{len(self.extracted_data)}行数据')
            
            # Pass data back via signal
            self.update_preview_signal.emit(self.extracted_data)
            self.progress_signal.emit(100)
            self.completed_signal.emit(True, f'成功读取{len(self.extracted_data)}行数据', '完成')
            
        except ExcelFormatError as e:
            self.excel_error_signal.emit(e)
        except Exception as e:
            self.error_signal.emit('读取错误', f'读取Excel文件失败：{str(e)}')
        finally:
            self.done_signal.emit()


class SendThread(WorkerThread):
    """发送消息后台线程"""
    
    def __init__(self, webhook_url: str, data: List[Dict], client_class):
        super().__init__()
        self.webhook_url = webhook_url
        self.data = data
        self.client_class = client_class
    
    def run(self):
        try:
            # Create client
            client = self.client_class(webhook_url=self.webhook_url)
            
            self.status_signal.emit('正在生成图片...')
            self.progress_signal.emit(10)
            
            # Generate images (batched)
            image_gen = ImageGenerator()
            image_bytes_list = image_gen.generate_table_images(self.data)
            total_images = len(image_bytes_list)
            
            self.status_signal.emit(f'生成{total_images}张图片，开始发送...')
            self.progress_signal.emit(20)
            
            # Send images one by one
            results = []
            for i, image_bytes in enumerate(image_bytes_list, 1):
                self.status_signal.emit(f'正在发送第{i}/{total_images}张图片...')
                progress = 20 + int(70 * i / total_images)
                self.progress_signal.emit(progress)
                
                result = client.send_image(image_bytes)
                results.append(result)
                
                if not result.get('success'):
                    error = result.get('error', '未知错误')
                    self.completed_signal.emit(
                        False,
                        f'第{i}张图片发送失败：{error}',
                        '发送失败'
                    )
                    return
                
                # Delay between images
                if i < total_images:
                    import time
                    time.sleep(1.0)
            
            self.progress_signal.emit(100)
            
            if total_images > 1:
                self.completed_signal.emit(
                    True, 
                    f'成功发送{total_images}张图片！',
                    '发送成功'
                )
            else:
                self.completed_signal.emit(
                    True, 
                    '图片发送成功！',
                    '发送成功'
                )
        
        except WeChatAPIError as e:
            self.webhook_error_signal.emit(e)
        
        except NetworkError as e:
            self.network_error_signal.emit(e)
        
        except Exception as e:
            self.completed_signal.emit(False, f'发送时出错：{str(e)}', '错误')
        
        finally:
            self.done_signal.emit()


class MainWindow(QMainWindow):
    """主窗口类 - Excel数据推送助手GUI (PyQt6版本)"""
    
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel数据推送助手")
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
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
        self.current_thread: Optional[WorkerThread] = None
        self.should_retry_send = False
        
        # Build UI
        self._create_widgets()
        
    def _center_window(self):
        """居中显示窗口"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.WINDOW_WIDTH) // 2
        y = (screen.height() - self.WINDOW_HEIGHT) // 2
        self.move(x, y)
    
    def _show_error(self, title: str, message: str, level: str = 'error', 
                    suggestion: str = None, show_retry: bool = False) -> bool:
        """显示错误信息
        
        Returns:
            True if user chose retry, False otherwise
        """
        full_message = message
        if suggestion:
            full_message = f"{message}\n\n解决建议：{suggestion}"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(full_message)
        
        if level == 'error':
            if show_retry:
                msg_box.setIcon(QMessageBox.Icon.Warning)
                retry_btn = msg_box.addButton("重试", QMessageBox.ButtonRole.AcceptRole)
                cancel_btn = msg_box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
                msg_box.exec()
                return msg_box.clickedButton() == retry_btn
            else:
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.exec()
                return False
        elif level == 'warning':
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
            return False
        else:
            # info级别显示在状态栏
            self.status_label.setText(full_message)
            self.status_label.setStyleSheet("color: red;")
            return False
    
    def _handle_network_error(self, error: NetworkError) -> bool:
        """处理网络错误，返回是否用户选择重试"""
        message = str(error)
        suggestion = "请检查网络连接，然后点击\"重新发送\"按钮重试。"
        
        if 'timeout' in message.lower():
            title = "网络超时"
            suggestion = "网络连接超时，请检查网络连接后点击\"重新发送\"按钮重试。"
        else:
            title = "网络错误"
        
        return self._show_error(title, message, level='error', 
                               suggestion=suggestion, show_retry=True)
    
    def _handle_webhook_error(self, error: WeChatAPIError):
        """处理webhook配置错误"""
        errcode = getattr(error, 'errcode', None)
        message = str(error)
        
        if errcode == 40013:
            title = "企业微信配置错误"
            suggestion = "webhook地址无效，请检查配置是否正确。可能的原因：\n1. key被复制错误\n2. 机器人已被删除\n3. 机器人被禁用"
        else:
            title = "发送失败"
            suggestion = "请检查企业微信机器人状态，或稍后重试。"
        
        self._show_error(title, message, level='error', suggestion=suggestion)
    
    def _handle_excel_error(self, error: ExcelFormatError):
        """处理Excel读取错误"""
        message = str(error)
        error_code = getattr(error, 'error_code', None)
        
        if error_code == 'PASSWORD_PROTECTED':
            title = "无法打开文件"
        elif error_code == 'CORRUPTED_FILE':
            title = "文件损坏"
        elif error_code == 'UNSUPPORTED_FORMAT':
            title = "格式不支持"
        else:
            title = "读取失败"
        
        self._show_error(title, message, level='error')
    
    def _create_widgets(self):
        """创建5个功能区域"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 1. File selection frame
        self._create_file_frame(main_layout)
        
        # 2. Preview frame
        self._create_preview_frame(main_layout)
        
        # 3. Send button frame (create before config to ensure send_btn exists)
        self._create_send_frame(main_layout)
        
        # 4. Config frame
        self._create_config_frame(main_layout)
        
        # 5. Status frame
        self._create_status_frame(main_layout)
    
    def _create_file_frame(self, parent_layout):
        """文件选择区域"""
        group = QGroupBox("文件选择")
        layout = QHBoxLayout(group)
        layout.setSpacing(5)
        
        self.file_path_label = QLabel("请选择Excel文件")
        self.file_path_label.setStyleSheet("color: gray;")
        layout.addWidget(self.file_path_label, stretch=1)
        
        select_btn = QPushButton("选择文件")
        select_btn.clicked.connect(self._on_select_file)
        layout.addWidget(select_btn)
        
        parent_layout.addWidget(group)
    
    def _create_preview_frame(self, parent_layout):
        """数据预览区域"""
        group = QGroupBox("数据预览")
        layout = QVBoxLayout(group)
        
        # Table widget - show all data with scroll
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(5)
        self.preview_table.setHorizontalHeaderLabels(
            ["日期", "发货人", "提单号", "入库未扫", "出库未扫"]
        )
        self.preview_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.preview_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.preview_table.verticalHeader().setVisible(False)
        # Enable scroll bars for all data
        self.preview_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.preview_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Enable word wrap for multiline content
        self.preview_table.setWordWrap(True)
        # Auto-adjust row height
        self.preview_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Set default row height
        self.preview_table.verticalHeader().setDefaultSectionSize(40)
        
        layout.addWidget(self.preview_table)
        parent_layout.addWidget(group, stretch=1)
    
    def _create_config_frame(self, parent_layout):
        """配置区域"""
        group = QGroupBox("企业微信配置")
        layout = QHBoxLayout(group)
        layout.setSpacing(5)
        
        layout.addWidget(QLabel("Webhook地址："))
        
        self.webhook_entry = QLineEdit()
        self.webhook_entry.setPlaceholderText("请输入企业微信机器人Webhook地址")
        self.webhook_entry.textChanged.connect(self._update_send_button)
        layout.addWidget(self.webhook_entry, stretch=1)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._on_save_config)
        save_btn.setFixedWidth(60)
        layout.addWidget(save_btn)
        
        # Load existing config
        existing_url = self.config_store.get_webhook_url()
        if existing_url:
            self.webhook_entry.setText(existing_url)
        
        parent_layout.addWidget(group)
    
    def _create_send_frame(self, parent_layout):
        """发送按钮区域"""
        frame = QWidget()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.send_btn = QPushButton("发送消息")
        self.send_btn.setEnabled(False)
        self.send_btn.clicked.connect(self._on_send)
        self.send_btn.setFixedWidth(100)
        layout.addStretch()
        layout.addWidget(self.send_btn)
        layout.addStretch()
        
        parent_layout.addWidget(frame)
    
    def _create_status_frame(self, parent_layout):
        """状态栏区域"""
        group = QGroupBox("状态")
        layout = QVBoxLayout(group)
        
        self.status_label = QLabel("准备就绪")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(group)
    
    def _update_send_button(self):
        """更新发送按钮状态"""
        has_file = self.current_file is not None
        has_data = len(self.current_data) > 0
        has_webhook = bool(self.webhook_entry.text().strip())
        not_processing = not self.is_processing
        
        self.send_btn.setEnabled(
            has_file and has_data and has_webhook and not_processing
        )
    
    def _set_status_color(self, state: str):
        """设置状态文字颜色"""
        colors = {
            'default': 'black',
            'processing': 'blue',
            'success': 'green',
            'error': 'red'
        }
        color = colors.get(state, 'black')
        self.status_label.setStyleSheet(f"color: {color};")
    
    def _on_select_file(self):
        """处理文件选择按钮点击"""
        last_folder = self.config_store.get_last_folder()
        if not last_folder or not Path(last_folder).exists():
            last_folder = str(Path.home() / "Documents")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Excel文件",
            last_folder,
            "Excel文件 (*.xlsx *.xls);;Excel 2007+ (*.xlsx);;Excel 97-2003 (*.xls);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        self.file_path_label.setText(file_path)
        self.file_path_label.setStyleSheet("color: black;")
        self.current_file = Path(file_path)
        
        self.config_store.set_last_folder(str(self.current_file.parent))
        
        self._start_loading()
    
    def _start_loading(self):
        """开始加载Excel文件"""
        self.is_processing = True
        self._update_send_button()
        self.status_label.setText("正在读取Excel文件...")
        self.status_label.setStyleSheet("color: blue;")
        self.progress_bar.setValue(0)
        
        # Create and start thread
        self.current_thread = ExcelLoadThread(
            self.current_file,
            self.excel_reader,
            self.column_detector
        )
        
        # Connect signals
        self.current_thread.progress_signal.connect(self.progress_bar.setValue)
        self.current_thread.status_signal.connect(self.status_label.setText)
        self.current_thread.error_signal.connect(self._on_error)
        self.current_thread.excel_error_signal.connect(self._on_excel_error)
        self.current_thread.update_preview_signal.connect(self._update_preview)
        self.current_thread.completed_signal.connect(self._on_task_completed)
        self.current_thread.done_signal.connect(self._on_task_done)
        
        self.current_thread.start()
    
    def _on_error(self, title: str, message: str):
        """处理错误信号"""
        self.is_processing = False
        self._update_send_button()
        self.progress_bar.setValue(0)
        self._set_status_color('error')
        QMessageBox.critical(self, title, message)
    
    def _on_excel_error(self, error):
        """处理Excel错误信号"""
        self.is_processing = False
        self._update_send_button()
        self.progress_bar.setValue(0)
        self._set_status_color('error')
        self._handle_excel_error(error)
    
    def _on_webhook_error(self, error):
        """处理webhook错误信号"""
        self.is_processing = False
        self._update_send_button()
        self.progress_bar.setValue(100)
        self._set_status_color('error')
        self._handle_webhook_error(error)
    
    def _on_network_error(self, error):
        """处理网络错误信号"""
        self.is_processing = False
        self._update_send_button()
        self.progress_bar.setValue(100)
        self._set_status_color('error')
        
        should_retry = self._handle_network_error(error)
        if should_retry:
            QTimer.singleShot(100, self._on_send)
    
    def _on_task_completed(self, success: bool, message: str, title: str):
        """处理任务完成信号"""
        self.is_processing = False
        self._update_send_button()
        self.progress_bar.setValue(100)
        
        if success:
            self._set_status_color('success')
            self.status_label.setText(message)
            QMessageBox.information(self, title, message)
        else:
            self._set_status_color('error')
            self.status_label.setText(message)
            QMessageBox.critical(self, title, message)
    
    def _on_task_done(self):
        """处理任务结束信号"""
        self.is_processing = False
        self._update_send_button()
        if self.current_thread:
            self.current_thread = None
    
    def _update_preview(self, data: list):
        """更新预览表格 - 显示所有数据"""
        # Store the data
        self.current_data = data
        
        # Clear table
        self.preview_table.setRowCount(0)
        
        if not self.current_data:
            self._update_send_button()
            return
        
        # Show ALL data (not just 20 rows)
        max_rows = len(self.current_data)
        self.preview_table.setRowCount(max_rows)
        
        # Map column keys from detector to display names
        column_mapping = {
            'date': '日期',
            'shipper': '发货人',
            'tracking': '提单号',
            'inbound_pending': '入库未扫',
            'outbound_pending': '出库未扫'
        }
        
        for i, row in enumerate(self.current_data):
            # Use English keys from detector (date, shipper, tracking, etc.)
            values = [
                row.get('date', '-'),
                row.get('shipper', '-'),
                row.get('tracking', '-'),
                row.get('inbound_pending', '-'),
                row.get('outbound_pending', '-')
            ]
            
            for j, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                # Alternating row colors
                if i % 2 == 0:
                    item.setBackground(QColor(240, 240, 240))
                self.preview_table.setItem(i, j, item)
        
        self._update_send_button()
    
    def _on_save_config(self):
        """保存webhook配置"""
        webhook_url = self.webhook_entry.text().strip()
        
        if not webhook_url:
            QMessageBox.warning(self, "配置错误", "请输入webhook地址")
            return
        
        try:
            self.config_store.set_webhook_url(webhook_url)
            self.status_label.setText("配置已保存")
            self._set_status_color('success')
            self._update_send_button()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存配置时出错：{str(e)}")
    
    def _on_send(self):
        """处理发送按钮点击"""
        webhook_url = self.webhook_entry.text().strip()
        
        if not webhook_url:
            QMessageBox.critical(self, "配置错误", "请先配置webhook地址")
            return
        
        if not self.current_data:
            QMessageBox.critical(self, "数据错误", "请先选择并加载Excel文件")
            return
        
        total_rows = len(self.current_data)
        reply = QMessageBox.question(
            self,
            "确认发送",
            f"确定要发送 {total_rows} 行数据到企业微信吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self._start_sending(webhook_url)
    
    def _start_sending(self, webhook_url: str):
        """开始发送消息"""
        self.is_processing = True
        self._update_send_button()
        self.progress_bar.setValue(0)
        self._set_status_color('processing')
        
        # Create and start thread
        self.current_thread = SendThread(
            webhook_url,
            self.current_data,
            WeChatWorkClient
        )
        
        # Connect signals
        self.current_thread.progress_signal.connect(self.progress_bar.setValue)
        self.current_thread.status_signal.connect(self.status_label.setText)
        self.current_thread.webhook_error_signal.connect(self._on_webhook_error)
        self.current_thread.network_error_signal.connect(self._on_network_error)
        self.current_thread.completed_signal.connect(self._on_task_completed)
        self.current_thread.done_signal.connect(self._on_task_done)
        
        self.current_thread.start()
