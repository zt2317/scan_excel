"""Markdown格式化器

将数据格式化为美观的Markdown表格，支持对齐和日期格式化
"""

from typing import List, Dict, Any
from datetime import datetime
import re


class MarkdownFormatter:
    """格式化数据为Markdown表格"""

    # 列显示名称（中文）
    COLUMN_DISPLAY = {
        'date': '日期',
        'shipper': '发货人',
        'tracking': '提单号',
        'inbound_pending': '入库未扫',
        'outbound_pending': '出库未扫'
    }

    # 列顺序
    COLUMN_ORDER = ['date', 'shipper', 'tracking', 'inbound_pending', 'outbound_pending']

    # 列宽配置（企业微信显示优化）
    COLUMN_WIDTHS = {
        'date': 12,
        'shipper': 10,
        'tracking': 18,
        'inbound_pending': 14,
        'outbound_pending': 14
    }

    def format(self, data: List[Dict[str, Any]]) -> str:
        """将数据格式化为美观的Markdown表格

        Args:
            data: 数据列表，每项是字典

        Returns:
            Markdown表格字符串（支持HTML换行）
        """
        if not data:
            return "暂无数据"

        # 确定要显示的列
        available_cols = set(data[0].keys())
        columns = [col for col in self.COLUMN_ORDER if col in available_cols]

        if not columns:
            return "暂无数据"

        lines = []

        # 表头
        header_cells = [self.COLUMN_DISPLAY.get(col, col) for col in columns]
        header_line = '| ' + ' | '.join(header_cells) + ' |'
        lines.append(header_line)

        # 分隔线（自动宽度）
        separator_cells = ['---' for _ in columns]
        separator_line = '|' + '|'.join(separator_cells) + '|'
        lines.append(separator_line)

        # 数据行
        for row in data:
            row_cells = []
            for col in columns:
                value = row.get(col, '-')
                # 日期格式化
                if col == 'date':
                    value = self._format_date(value)
                # 处理值
                value_str = str(value) if value is not None else '-'
                # 保留换行，用<br>标签（企业微信支持HTML）
                value_str = value_str.replace('\n', '<br>').replace('\r', '')
                row_cells.append(value_str)
            row_line = '| ' + ' | '.join(row_cells) + ' |'
            lines.append(row_line)

        return '\n'.join(lines)

    def _pad_text(self, text: str, width: int) -> str:
        """将文本填充到指定宽度（处理中文宽度）"""
        # 计算实际显示宽度（中文字符算2个宽度）
        display_width = 0
        for char in text:
            if ord(char) > 127:  # 中文字符
                display_width += 2
            else:
                display_width += 1
        
        # 填充空格
        padding = width - display_width
        if padding > 0:
            return text + ' ' * padding
        return text

    def _format_date(self, value: Any) -> str:
        """格式化日期为 YYYY-MM-DD"""
        if not value or value == '-':
            return '-'

        value_str = str(value).strip()

        # 已经是 YYYY-MM-DD 格式
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value_str):
            return value_str

        # 尝试多种格式解析
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y年%m月%d日',
            '%Y年%m月%d',
            '%d-%b-%Y',
            '%d/%b/%Y',
            '%Y%m%d',
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(value_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # 无法解析，返回原值
        return value_str
