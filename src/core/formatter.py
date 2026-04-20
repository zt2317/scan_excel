"""Markdown格式化器

将数据格式化为Markdown表格，支持对齐和日期格式化
"""

from typing import List, Dict, Any
from datetime import datetime
import re


class MarkdownFormatter:
    """格式化数据为Markdown表格 per D-10, D-11"""

    # 列显示名称（中文）per D-11
    COLUMN_DISPLAY = {
        'date': '日期',
        'shipper': '发货人',
        'tracking': '提单号',
        'inbound_pending': '入库未扫',
        'outbound_pending': '出库未扫'
    }

    # 列顺序（用于保持一致的输出顺序）
    COLUMN_ORDER = ['date', 'shipper', 'tracking', 'inbound_pending', 'outbound_pending']

    def format(self, data: List[Dict[str, Any]]) -> str:
        """将数据格式化为Markdown表格

        Per D-10: 对齐表格格式
        Per D-11: 加粗表头
        Per MD-01: 标准Markdown表格
        Per MD-02: 加粗表头

        Args:
            data: 数据列表，每项是字典

        Returns:
            Markdown表格字符串
        """
        if not data:
            return "暂无数据"

        # 确定要显示的列（取数据第一行的keys与COLUMN_ORDER的交集）
        available_cols = set(data[0].keys())
        columns = [col for col in self.COLUMN_ORDER if col in available_cols]

        if not columns:
            return "暂无数据"

        # 计算每列的最大宽度
        widths = self._calculate_column_widths(data, columns)

        lines = []

        # 表头（加粗）
        header_cells = [f"**{self.COLUMN_DISPLAY.get(col, col)}**" for col in columns]
        header_line = '| ' + ' | '.join(header_cells) + ' |'
        lines.append(header_line)

        # 分隔线
        separator_cells = ['-' * (widths[col] + 4) for col in columns]  # +4 for bold markers
        separator_line = '|' + '|'.join(separator_cells) + '|'
        lines.append(separator_line)

        # 数据行
        for row in data:
            row_cells = []
            for col in columns:
                value = row.get(col, '-')
                # 日期格式化 per MD-03
                if col == 'date':
                    value = self._format_date(value)
                # 确保是字符串
                value_str = str(value) if value is not None else '-'
                row_cells.append(value_str)
            row_line = '| ' + ' | '.join(row_cells) + ' |'
            lines.append(row_line)

        return '\n'.join(lines)

    def _calculate_column_widths(self, data: List[Dict[str, Any]], columns: List[str]) -> Dict[str, int]:
        """计算每列的最大宽度"""
        widths = {}

        for col in columns:
            # 表头长度
            header_len = len(self.COLUMN_DISPLAY.get(col, col))
            # 数据最大长度
            max_data_len = 0
            for row in data:
                value = row.get(col, '-')
                if col == 'date':
                    value = self._format_date(value)
                max_data_len = max(max_data_len, len(str(value)))
            widths[col] = max(header_len, max_data_len)

        return widths

    def _format_date(self, value: Any) -> str:
        """格式化日期为 YYYY-MM-DD per D-07, MD-03

        支持多种输入格式：
        - 2024-01-15
        - 2024/01/15
        - 15/01/2024
        - 15-Jan-2024
        - 2024年01月15日
        """
        if not value or value == '-':
            return '-'

        value_str = str(value).strip()

        # 已经是 YYYY-MM-DD 格式
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value_str):
            return value_str

        # 尝试多种格式解析
        date_formats = [
            # 标准格式
            '%Y-%m-%d',
            '%Y/%m/%d',
            # 日月年格式
            '%d/%m/%Y',
            '%d-%m-%Y',
            # 带中文
            '%Y年%m月%d日',
            '%Y年%m月%d',
            # 其他常见格式
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
