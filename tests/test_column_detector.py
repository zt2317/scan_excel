"""ColumnDetector 单元测试"""

import pytest
from src.core.column_detector import ColumnDetector


class TestColumnDetector:
    """测试 ColumnDetector 类"""

    @pytest.fixture
    def detector(self):
        return ColumnDetector()

    def test_detect_all_columns_exact_match(self, detector):
        """测试精确匹配所有列"""
        headers = ['日期', '发货人', '提单号', '入库未扫', '出库未扫']
        
        column_map = detector.detect(headers)
        
        assert 'date' in column_map
        assert 'shipper' in column_map
        assert 'tracking' in column_map
        assert 'inbound_pending' in column_map
        assert 'outbound_pending' in column_map
        assert len(column_map) == 5

    def test_detect_fuzzy_match(self, detector):
        """测试模糊匹配 per D-04"""
        # 使用变体列名
        headers = ['日期时间', '发货', '提单号码', '入库', '出库']
        
        column_map = detector.detect(headers)
        
        # 应该能匹配到所有列
        assert len(column_map) == 5
        assert column_map['date'] == 0  # 日期时间包含"日期"
        assert column_map['shipper'] == 1  # 发货匹配"发货"
        assert column_map['tracking'] == 2  # 提单号码包含"提单"

    def test_detect_partial_fuzzy_match(self, detector):
        """测试部分模糊匹配"""
        headers = ['日期', '发货人名称', '提单编号', '入库情况', '出库状态']
        
        column_map = detector.detect(headers)
        
        assert len(column_map) == 5
        # 验证每个列都正确映射
        for key in ['date', 'shipper', 'tracking', 'inbound_pending', 'outbound_pending']:
            assert key in column_map

    def test_missing_column_error(self, detector):
        """测试缺少列时报错 per D-09"""
        headers = ['日期', '发货人', '提单号', '入库未扫']  # 缺少 出库未扫
        
        with pytest.raises(ValueError) as exc_info:
            detector.detect(headers)
        
        # 验证中文错误消息
        error_msg = str(exc_info.value)
        assert "缺少必需的列" in error_msg
        assert "出库未扫" in error_msg

    def test_missing_multiple_columns(self, detector):
        """测试缺少多列时报错"""
        headers = ['日期', '发货人']  # 只提供2列
        
        with pytest.raises(ValueError) as exc_info:
            detector.detect(headers)
        
        error_msg = str(exc_info.value)
        assert "缺少必需的列" in error_msg

    def test_extract_data_normal(self, detector):
        """测试正常数据提取"""
        headers = ['日期', '发货人', '提单号', '入库未扫', '出库未扫']
        rows = [
            headers,
            ['2024-01-15', '张三', 'BL001', '5', '0'],
            ['2024-01-16', '李四', 'BL002', '0', '3'],
        ]
        
        column_map = detector.detect(headers)
        data = detector.extract_data(rows, column_map)
        
        assert len(data) == 2
        assert data[0]['date'] == '2024-01-15'
        assert data[0]['shipper'] == '张三'
        assert data[0]['tracking'] == 'BL001'
        assert data[0]['inbound_pending'] == '5'
        assert data[0]['outbound_pending'] == '0'

    def test_extract_data_null_handling(self, detector):
        """测试空值处理 per D-08"""
        headers = ['日期', '发货人', '提单号', '入库未扫', '出库未扫']
        rows = [
            headers,
            ['2024-01-15', None, 'BL001', '', '0'],
        ]
        
        column_map = detector.detect(headers)
        data = detector.extract_data(rows, column_map)
        
        # None 和空字符串应转为 "-"
        assert data[0]['shipper'] == '-'  # None -> "-"
        assert data[0]['inbound_pending'] == '-'  # '' -> "-"

    def test_format_value_null(self, detector):
        """测试 _format_value 空值处理"""
        assert detector._format_value(None) == '-'
        assert detector._format_value('') == '-'
        assert detector._format_value('   ') == '-'

    def test_format_value_normal(self, detector):
        """测试 _format_value 正常值"""
        assert detector._format_value('测试') == '测试'
        assert detector._format_value(123) == '123'
        assert detector._format_value('  值  ') == '值'  # 去除空格

    def test_extract_data_empty_rows(self, detector):
        """测试空数据行"""
        headers = ['日期', '发货人', '提单号', '入库未扫', '出库未扫']
        rows = [headers]  # 只有表头
        
        column_map = detector.detect(headers)
        data = detector.extract_data(rows, column_map)
        
        assert data == []

    def test_column_order_independence(self, detector):
        """测试列顺序无关性"""
        # 列顺序打乱
        headers = ['出库未扫', '日期', '入库未扫', '提单号', '发货人']
        
        column_map = detector.detect(headers)
        
        # 验证映射到正确的索引
        assert column_map['outbound_pending'] == 0
        assert column_map['date'] == 1
        assert column_map['inbound_pending'] == 2
        assert column_map['tracking'] == 3
        assert column_map['shipper'] == 4
