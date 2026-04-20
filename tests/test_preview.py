"""Preview 单元测试"""

import pytest
from src.core.preview import generate_preview, format_preview_table


class TestPreview:
    """测试预览功能"""

    def test_preview_first_10_rows(self):
        """测试预览显示前10行 per D-12"""
        data = [
            {'date': f'2024-01-{i:02d}', 'shipper': f'发货人{i}', 'tracking': f'BL{i:03d}', 
             'inbound_pending': str(i), 'outbound_pending': '0'}
            for i in range(1, 20)  # 19行数据
        ]
        
        preview = generate_preview(data)
        
        # 验证只有10行数据（表头 + 10行 = 11行，但有分隔线）
        lines = [l for l in preview.split('\n') if '|' in l and '---' not in l]
        # 表头 + 10行数据 = 11行显示
        assert len(lines) == 11

    def test_preview_custom_count(self):
        """测试自定义行数预览"""
        data = [
            {'date': f'2024-01-{i:02d}', 'shipper': f'人{i}', 'tracking': f'BL{i:03d}', 
             'inbound_pending': str(i), 'outbound_pending': '0'}
            for i in range(1, 50)
        ]
        
        preview = generate_preview(data, max_rows=5)
        
        # 验证只有5行
        lines = [l for l in preview.split('\n') if '|' in l and '---' not in l]
        assert len(lines) == 6  # 表头 + 5行

    def test_preview_empty(self):
        """测试空数据预览"""
        preview = generate_preview([])
        assert preview == "暂无数据可预览"

    def test_preview_shows_total(self):
        """测试预览显示总行数"""
        data = [
            {'date': f'2024-01-{i:02d}', 'shipper': f'人{i}', 'tracking': f'BL{i:03d}', 
             'inbound_pending': str(i), 'outbound_pending': '0'}
            for i in range(1, 25)  # 24行
        ]
        
        preview = generate_preview(data, max_rows=10)
        
        # 验证显示行数信息
        assert "共 24 行" in preview
        assert "显示前 10 行" in preview

    def test_preview_columns_display(self):
        """测试预览列显示"""
        data = [
            {'date': '2024-01-15', 'shipper': '张三', 'tracking': 'BL001', 
             'inbound_pending': '5', 'outbound_pending': '0'}
        ]
        
        preview = generate_preview(data)
        
        # 验证显示中文列名
        assert '日期' in preview
        assert '发货人' in preview
        assert '提单号' in preview
        assert '入库未扫' in preview
        assert '出库未扫' in preview

    def test_preview_data_shown(self):
        """测试数据正确显示"""
        data = [
            {'date': '2024-01-15', 'shipper': '张三', 'tracking': 'BL001', 
             'inbound_pending': '5', 'outbound_pending': '0'}
        ]
        
        preview = generate_preview(data)
        
        # 验证数据行
        assert '2024-01-15' in preview
        assert '张三' in preview
        assert 'BL001' in preview
        assert '5' in preview

    def test_format_preview_table_alias(self):
        """测试 format_preview_table 是 generate_preview 的别名"""
        data = [{'date': '2024-01-15', 'shipper': '张三'}]
        
        preview1 = generate_preview(data)
        preview2 = format_preview_table(data)
        
        assert preview1 == preview2

    def test_preview_column_alignment(self):
        """测试列对齐"""
        data = [
            {'date': '2024-01-15', 'shipper': '张三', 'tracking': 'BL001', 
             'inbound_pending': '5', 'outbound_pending': '0'},
            {'date': '2024-01-16', 'shipper': '李四李四李四', 'tracking': 'BL002', 
             'inbound_pending': '100', 'outbound_pending': '999'},
        ]
        
        preview = generate_preview(data)
        
        # 验证有分隔线
        assert '-+-' in preview

    def test_preview_partial_columns(self):
        """测试部分列预览"""
        data = [
            {'date': '2024-01-15', 'shipper': '张三'},  # 只有两列
        ]
        
        preview = generate_preview(data)
        
        # 应该只显示存在的列
        assert '日期' in preview
        assert '发货人' in preview
        assert '张三' in preview
