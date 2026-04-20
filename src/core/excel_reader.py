"""Excel文件读取器

支持 .xlsx (openpyxl) 和 .xls (xlrd) 格式
"""

import os
from typing import List, Any, Optional


class ExcelReader:
    """读取Excel文件并返回结构化数据"""

    def __init__(self):
        self.file_path: Optional[str] = None
        self.data: List[List[Any]] = []

    def read(self, file_path: str) -> List[List[Any]]:
        """读取Excel文件并返回数据列表

        Args:
            file_path: Excel文件路径

        Returns:
            数据列表，每行是一个列表

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")

        # 根据扩展名选择读取方法
        if file_path.lower().endswith('.xlsx'):
            return self._read_xlsx(file_path)
        elif file_path.lower().endswith('.xls'):
            return self._read_xls(file_path)
        else:
            raise ValueError("不支持的文件格式，请使用.xlsx或.xls")

    def _read_xlsx(self, file_path: str) -> List[List[Any]]:
        """使用 openpyxl 读取 .xlsx 文件"""
        try:
            import openpyxl
        except ImportError:
            raise ImportError("请安装 openpyxl: pip install openpyxl>=3.1.2")

        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            sheet = workbook.active
            
            data = []
            for row in sheet.iter_rows(values_only=True):
                # 将每个单元格转换为字符串
                row_data = [str(cell) if cell is not None else "" for cell in row]
                data.append(row_data)
            
            return data
        except Exception as e:
            raise ValueError(f"读取Excel失败：{e}")

    def _read_xls(self, file_path: str) -> List[List[Any]]:
        """使用 xlrd 读取 .xls 文件"""
        try:
            import xlrd
        except ImportError:
            raise ImportError("请安装 xlrd: pip install xlrd>=2.0.1")

        try:
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheet_by_index(0)
            
            data = []
            for row_idx in range(sheet.nrows):
                row = sheet.row_values(row_idx)
                # 将每个单元格转换为字符串
                row_data = [str(cell) if cell is not None else "" for cell in row]
                data.append(row_data)
            
            return data
        except Exception as e:
            raise ValueError(f"读取Excel失败：{e}")
