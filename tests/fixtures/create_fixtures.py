"""创建测试用的Excel文件

注意：.xlsx/.xls 文件不应提交到git，运行测试前执行此脚本生成
"""

import os


def create_xlsx_fixture(filepath: str):
    """创建 .xlsx 测试文件"""
    try:
        import openpyxl
    except ImportError:
        print("警告：未安装 openpyxl，无法创建 .xlsx 测试文件")
        return

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "物流数据"
    
    # 表头
    sheet.append(['日期', '发货人', '提单号', '入库未扫', '出库未扫'])
    
    # 测试数据
    sheet.append(['2024-01-15', '张三', 'BL001', 5, 0])
    sheet.append(['2024-01-16', '李四', 'BL002', 0, 3])
    sheet.append(['2024-01-17', '王五', 'BL003', 2, 1])
    
    workbook.save(filepath)
    print(f"创建：{filepath}")


def create_xls_fixture(filepath: str):
    """创建 .xls 测试文件"""
    try:
        import xlwt
    except ImportError:
        print("警告：未安装 xlwt，无法创建 .xls 测试文件")
        return

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('物流数据')
    
    # 表头
    headers = ['日期', '发货人', '提单号', '入库未扫', '出库未扫']
    for col, header in enumerate(headers):
        sheet.write(0, col, header)
    
    # 测试数据
    data = [
        ['2024-01-15', '张三', 'BL001', 5, 0],
        ['2024-01-16', '李四', 'BL002', 0, 3],
        ['2024-01-17', '王五', 'BL003', 2, 1],
    ]
    
    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, value in enumerate(row_data):
            sheet.write(row_idx, col_idx, value)
    
    workbook.save(filepath)
    print(f"创建：{filepath}")


if __name__ == "__main__":
    fixtures_dir = os.path.dirname(os.path.abspath(__file__))
    
    create_xlsx_fixture(os.path.join(fixtures_dir, 'sample.xlsx'))
    create_xls_fixture(os.path.join(fixtures_dir, 'sample.xls'))
    
    print("测试夹具生成完成！")
