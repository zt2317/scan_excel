"""列检测器

自动识别Excel中的目标列，支持模糊匹配
"""

from typing import List, Dict, Any, Optional


class ColumnDetector:
    """检测目标列并提取数据"""

    # 目标列配置：key -> 匹配关键词列表
    TARGET_COLUMNS = {
        'date': ['日期'],
        'shipper': ['发货人', '发货'],
        'tracking': ['提单号', '提单', '单号'],
        'inbound_pending': ['入库未扫', '入库'],
        'outbound_pending': ['出库未扫', '出库']
    }

    # 列显示名称（中文）
    COLUMN_NAMES = {
        'date': '日期',
        'shipper': '发货人',
        'tracking': '提单号',
        'inbound_pending': '入库未扫',
        'outbound_pending': '出库未扫'
    }

    def detect(self, headers: List[str]) -> Dict[str, int]:
        """检测目标列在表头中的位置

        Args:
            headers: 表头列表

        Returns:
            列名到索引的映射 {column_key: index}

        Raises:
            ValueError: 缺少必需列（中文错误消息）
        """
        column_map = {}
        matched_headers = set()

        # 遍历每个目标列
        for col_key, keywords in self.TARGET_COLUMNS.items():
            found = False
            for idx, header in enumerate(headers):
                if idx in matched_headers:
                    continue  # 跳过已匹配的列

                if self._match_column(header, keywords):
                    column_map[col_key] = idx
                    matched_headers.add(idx)
                    found = True
                    break

            if not found:
                # Per D-09: 所有列必须存在，否则报错
                col_name = self.COLUMN_NAMES.get(col_key, col_key)
                raise ValueError(f"缺少必需的列：{col_name}")

        return column_map

    def _match_column(self, header: str, keywords: List[str]) -> bool:
        """检查表头是否匹配关键词列表（模糊包含匹配）

        Per D-04: 如果表头包含任一关键词，即视为匹配
        """
        header_str = str(header).strip()
        for keyword in keywords:
            if keyword in header_str:
                return True
        return False

    def extract_data(self, rows: List[List[Any]], column_map: Dict[str, int]) -> List[Dict[str, str]]:
        """从行数据中提取目标列

        Args:
            rows: Excel数据行（包括表头）
            column_map: 列映射（来自 detect()）

        Returns:
            提取的数据列表，每项是字典
        """
        if not rows or len(rows) < 2:
            return []

        # 跳过表头，提取数据行
        data_rows = rows[1:]
        result = []

        for row in data_rows:
            row_data = {}
            for col_key, col_idx in column_map.items():
                value = row[col_idx] if col_idx < len(row) else None
                row_data[col_key] = self._format_value(value)
            result.append(row_data)

        return result

    def _format_value(self, value: Any) -> str:
        """格式化单元格值

        Per D-08: 空值转换为 "-"
        """
        if value is None:
            return "-"

        value_str = str(value).strip()

        # Per D-08: 空字符串也视为空值
        if not value_str:
            return "-"

        return value_str
