"""MarkdownFormatter 单元测试"""

import pytest
from src.core.formatter import MarkdownFormatter


class TestMarkdownFormatter:
    """测试 MarkdownFormatter 类"""

    @pytest.fixture
    def formatter(self):
        return MarkdownFormatter()

    def test_format_basic_table(self, formatter):
        """测试基本Markdown表格生成 per MD-01"""
        data = [
            {'date': '2024-01-15', 'shipper': '张三', 'tracking': 'BL001', 'inbound_pending': '5', 'outbound_pending': '0'}
        ]
        
        result = formatter.format(data)
        
        # 验证包含表格结构
        assert '| **日期** |' in result
        assert '| **发货人** |' in result
        assert '| 2024-01-15 |' in result
        assert '| 张三 |' in result

    def test_bold_headers(self, formatter):
        """测试加粗表头 per D-11, MD-02"""
        data = [{'date': '2024-01-15', 'shipper': '张三'}]
        
        result = formatter.format(data)
        
        # 验证表头有 **
        lines = result.split('\n')
        header_line = lines[0]
        assert '**日期**' in header_line
        assert '**发货人**' in header_line

    def test_date_formatting(self, formatter):
        """测试日期格式化为 YYYY-MM-DD per MD-03"""
        # 测试多种输入格式
        test_cases = [
            ('2024/01/15', '2024-01-15'),
            ('15/01/2024', '2024-01-15'),
            ('2024-01-15', '2024-01-15'),  # 已经是目标格式
        ]
        
        for input_date, expected in test_cases:
            data = [{'date': input_date, 'shipper': '张三'}]
            result = formatter.format(data)
            assert expected in result, f"日期 {input_date} 应格式化为 {expected}"

    def test_date_formatting_chinese(self, formatter):
        """测试中文日期格式"""
        data = [{'date': '2024年01月15日', 'shipper': '张三'}]
        result = formatter.format(data)
        assert '2024-01-15' in result

    def test_null_display(self, formatter):
        """测试空值显示为 -"""
        data = [{'date': '-', 'shipper': None}]
        result = formatter.format(data)
        assert '| - |' in result

    def test_empty_data(self, formatter):
        """测试空数据处理"""
        result = formatter.format([])
        assert result == "暂无数据"

    def test_multiple_rows(self, formatter):
        """测试多行数据"""
        data = [
            {'date': '2024-01-15', 'shipper': '张三', 'tracking': 'BL001', 'inbound_pending': '5', 'outbound_pending': '0'},
            {'date': '2024-01-16', 'shipper': '李四', 'tracking': 'BL002', 'inbound_pending': '0', 'outbound_pending': '3'},
        ]
        
        result = formatter.format(data)
        
        # 验证有两行数据
        lines = [l for l in result.split('\n') if '|' in l and '**' not in l and '---' not in l]
        assert len(lines) == 2
        assert '张三' in result
        assert '李四' in result

    def test_format_date_helper(self, formatter):
        """测试 _format_date 辅助方法"""
        assert formatter._format_date('2024/01/15') == '2024-01-15'
        assert formatter._format_date('2024-01-15') == '2024-01-15'
        assert formatter._format_date('15/01/2024') == '2024-01-15'
        assert formatter._format_date('2024年01月15日') == '2024-01-15'
        assert formatter._format_date('-') == '-'
        assert formatter._format_date(None) == '-'
        assert formatter._format_date('未知') == '未知'  # 无法解析的保持原样

    def test_partial_columns(self, formatter):
        """测试部分列存在的情况"""
        data = [
            {'date': '2024-01-15', 'shipper': '张三'},  # 只有两列
        ]
        
        result = formatter.format(data)
        
        # 应该只显示存在的列
        assert '| **日期** |' in result
        assert '| **发货人** |' in result
        assert '日期' in result
        assert '张三' in result
