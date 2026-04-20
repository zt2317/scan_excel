"""ExcelReader 单元测试"""

import pytest
import os
import tempfile
from src.core.excel_reader import ExcelReader


class TestExcelReader:
    """测试 ExcelReader 类"""

    @pytest.fixture
    def reader(self):
        return ExcelReader()

    def test_read_xlsx(self, reader, tmp_path):
        """测试读取 .xlsx 文件"""
        # 创建临时 xlsx 文件
        try:
            import openpyxl
        except ImportError:
            pytest.skip("未安装 openpyxl")

        xlsx_file = tmp_path / "test.xlsx"
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['日期', '发货人'])
        sheet.append(['2024-01-15', '张三'])
        workbook.save(xlsx_file)

        # 读取
        data = reader.read(str(xlsx_file))

        # 验证
        assert len(data) == 2
        assert data[0] == ['日期', '发货人']
        assert data[1] == ['2024-01-15', '张三']

    def test_read_xls(self, reader, tmp_path):
        """测试读取 .xls 文件"""
        # 创建临时 xls 文件
        try:
            import xlwt
        except ImportError:
            pytest.skip("未安装 xlwt")

        xls_file = tmp_path / "test.xls"
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('test')
        sheet.write(0, 0, '日期')
        sheet.write(0, 1, '发货人')
        sheet.write(1, 0, '2024-01-15')
        sheet.write(1, 1, '张三')
        workbook.save(xls_file)

        # 读取
        data = reader.read(str(xls_file))

        # 验证
        assert len(data) == 2
        assert data[0] == ['日期', '发货人']
        assert data[1] == ['2024-01-15', '张三']

    def test_file_not_found(self, reader):
        """测试文件不存在时的错误处理"""
        with pytest.raises(FileNotFoundError) as exc_info:
            reader.read("/不存在的路径/文件.xlsx")
        
        # 验证中文错误消息
        assert "文件不存在" in str(exc_info.value)

    def test_invalid_extension(self, reader, tmp_path):
        """测试不支持的文件格式"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("这不是Excel文件")

        with pytest.raises(ValueError) as exc_info:
            reader.read(str(txt_file))
        
        # 验证中文错误消息
        assert "不支持的文件格式" in str(exc_info.value)

    def test_empty_file_handling(self, reader, tmp_path):
        """测试空单元格处理"""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("未安装 openpyxl")

        xlsx_file = tmp_path / "empty.xlsx"
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['日期', '发货人'])
        sheet.append(['2024-01-15', None])  # 空单元格
        workbook.save(xlsx_file)

        data = reader.read(str(xlsx_file))

        # 空单元格应转为空字符串
        assert data[1][1] == ""
