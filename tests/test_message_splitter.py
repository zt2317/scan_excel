"""消息拆分器单元测试"""

import pytest
from src.core.wechat_client import WeChatWorkClient


class TestMessageSplitter:
    """测试消息拆分逻辑"""

    @pytest.fixture
    def client(self):
        """创建WeChatWorkClient实例（用于访问_split_markdown_table）"""
        # 使用__new__绕过__init__，因为不需要真实的webhook_url
        return WeChatWorkClient.__new__(WeChatWorkClient)

    def test_single_chunk_for_small_table(self, client):
        """小表格（<15行）返回单一切片"""
        markdown = """| 日期 | 发货人 |
|---|---|
| 2024-01-01 | 张三 |
| 2024-01-02 | 李四 |"""
        
        chunks = client._split_markdown_table(markdown, rows_per_chunk=15)
        
        assert len(chunks) == 1
        assert "| 日期 | 发货人 |" in chunks[0]

    def test_multiple_chunks_for_large_table(self, client):
        """大表格拆分为多个切片"""
        # 创建20行数据的表格
        rows = ["| 日期 | 发货人 |", "|---|---|"]
        for i in range(20):
            rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1} |")
        
        markdown = "\n".join(rows)
        chunks = client._split_markdown_table(markdown, rows_per_chunk=5)
        
        # 20行 / 5行每片 = 4片
        assert len(chunks) == 4

    def test_header_preservation_in_chunks(self, client):
        """非第一片的切片包含表头"""
        rows = ["| 日期 | 发货人 |", "|---|---|"]
        for i in range(10):
            rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1} |")
        
        markdown = "\n".join(rows)
        chunks = client._split_markdown_table(markdown, rows_per_chunk=5)
        
        # 检查所有切片都包含表头
        for chunk in chunks:
            assert "| 日期 | 发货人 |" in chunk
            assert "|---|---|" in chunk

    def test_empty_input(self, client):
        """空输入返回空列表"""
        chunks = client._split_markdown_table("")
        assert chunks == []

    def test_whitespace_only_input(self, client):
        """只有空白字符返回空列表"""
        chunks = client._split_markdown_table("   \n   \n  ")
        assert chunks == []

    def test_non_table_markdown(self, client):
        """非表格markdown作为单一片返回"""
        markdown = "这是普通文本\n没有表格格式"
        chunks = client._split_markdown_table(markdown)
        
        assert len(chunks) == 1
        assert chunks[0] == markdown

    def test_header_only_table(self, client):
        """只有表头的表格返回单一切片"""
        markdown = """| 日期 | 发货人 |
|---|---|"""
        
        chunks = client._split_markdown_table(markdown)
        
        assert len(chunks) == 1
        assert "| 日期 | 发货人 |" in chunks[0]

    def test_chunk_row_count(self, client):
        """验证每片的数据行数"""
        rows = ["| 日期 | 发货人 |", "|---|---|"]
        for i in range(20):
            rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1} |")
        
        markdown = "\n".join(rows)
        chunks = client._split_markdown_table(markdown, rows_per_chunk=7)
        
        # 20行 / 7行每片 = 3片 (7+7+6)
        assert len(chunks) == 3
        
        # 检查最后一片的行数
        last_chunk_lines = chunks[2].strip().split('\n')
        # 最后一片：表头 + 分隔符 + 6行数据 = 8行
        assert len(last_chunk_lines) == 8

    def test_preserves_cell_formatting(self, client):
        """保留单元格格式"""
        markdown = """| **日期** | *发货人* |
|:---:|---:|
| **2024-01-01** | *张三* |
| 2024-01-02 | 李四 |"""
        
        chunks = client._split_markdown_table(markdown, rows_per_chunk=1)
        
        assert len(chunks) == 2
        # 检查格式保留
        assert "**2024-01-01**" in chunks[0]
        assert "*张三*" in chunks[0]

    def test_exact_boundary(self, client):
        """测试边界条件：恰好15行"""
        rows = ["| 日期 | 发货人 |", "|---|---|"]
        for i in range(15):
            rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1} |")
        
        markdown = "\n".join(rows)
        chunks = client._split_markdown_table(markdown, rows_per_chunk=15)
        
        # 恰好15行应该只有1片
        assert len(chunks) == 1

    def test_one_over_boundary(self, client):
        """测试边界条件：16行"""
        rows = ["| 日期 | 发货人 |", "|---|---|"]
        for i in range(16):
            rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1} |")
        
        markdown = "\n".join(rows)
        chunks = client._split_markdown_table(markdown, rows_per_chunk=15)
        
        # 16行应该分成2片 (15+1)
        assert len(chunks) == 2
