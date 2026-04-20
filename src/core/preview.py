"""数据预览生成器

生成用户友好的预览表格（纯文本格式）
"""

from typing import List, Dict, Any


def generate_preview(data: List[Dict[str, Any]], max_rows: int = 10) -> str:
    """生成数据预览（前N行）per D-12

    Args:
        data: 数据列表
        max_rows: 最大行数（默认10）

    Returns:
        格式化的预览文本
    """
    if not data:
        return "暂无数据可预览"

    # 列显示名称映射
    column_display = {
        'date': '日期',
        'shipper': '发货人',
        'tracking': '提单号',
        'inbound_pending': '入库未扫',
        'outbound_pending': '出库未扫'
    }

    # 确定要显示的列
    available_cols = set(data[0].keys())
    column_order = ['date', 'shipper', 'tracking', 'inbound_pending', 'outbound_pending']
    columns = [col for col in column_order if col in available_cols]

    if not columns:
        return "数据格式不正确"

    # 截取前 max_rows 行
    preview_data = data[:max_rows]
    total_rows = len(data)

    # 计算每列宽度
    widths = {}
    for col in columns:
        header = column_display.get(col, col)
        max_data_len = max(len(str(row.get(col, '-'))) for row in preview_data)
        widths[col] = max(len(header), max_data_len, 3)  # 最小宽度3

    lines = []

    # 表头
    header_cells = [column_display.get(col, col).center(widths[col]) for col in columns]
    lines.append(' | '.join(header_cells))

    # 分隔线
    separator_cells = ['-' * widths[col] for col in columns]
    lines.append('-+-'.join(separator_cells))

    # 数据行
    for row in preview_data:
        row_cells = []
        for col in columns:
            value = str(row.get(col, '-'))
            # 左对齐
            row_cells.append(value.ljust(widths[col]))
        lines.append(' | '.join(row_cells))

    # 添加行数信息
    if total_rows > max_rows:
        lines.append(f"\n... 共 {total_rows} 行，显示前 {max_rows} 行")

    return '\n'.join(lines)


def format_preview_table(data: List[Dict[str, Any]], max_rows: int = 10) -> str:
    """格式化预览表格（同 generate_preview，保持API一致）"""
    return generate_preview(data, max_rows)
