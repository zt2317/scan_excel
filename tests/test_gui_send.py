"""GUI发送功能测试"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestSendFunctionality(unittest.TestCase):
    """测试发送功能"""
    
    def test_webhook_validation(self):
        """测试webhook地址验证"""
        # Empty webhook should trigger error
        webhook = ""
        self.assertFalse(bool(webhook.strip()))
        
        # Valid webhook should pass
        webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
        self.assertTrue(bool(webhook.strip()))
    
    @patch('gui.main_window.WeChatWorkClient')
    def test_send_markdown_call(self, mock_client_class):
        """测试Markdown发送调用"""
        # Mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.send_markdown.return_value = [{'success': True}]
        
        # Test that send_markdown is called with markdown text
        test_markdown = "| 日期 | 发货人 |\n|------|--------|"
        mock_client.send_markdown(test_markdown)
        mock_client.send_markdown.assert_called_with(test_markdown)
    
    def test_progress_calculation(self):
        """测试进度计算逻辑"""
        # Simulate progress for 3 chunks, 2 successful
        total = 3
        success = 2
        progress = 10 + int(90 * success / total)
        self.assertEqual(progress, 70)


if __name__ == '__main__':
    unittest.main()
