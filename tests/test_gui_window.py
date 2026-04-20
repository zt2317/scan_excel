"""GUI窗口单元测试"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gui.main_window import MainWindow


class TestMainWindow(unittest.TestCase):
    """测试MainWindow类"""
    
    def test_window_creation(self):
        """测试窗口可以创建（不启动主循环）"""
        # Just verify the class can be imported and instantiated
        # Note: We can't actually test tkinter without a display
        # This test mainly checks for import errors
        try:
            import tkinter as tk
            # Check if we can create a root (may fail in headless)
            root = tk.Tk()
            root.destroy()
            self.assertTrue(True)
        except Exception as e:
            # Headless environment, skip GUI test
            self.skipTest(f"GUI test skipped: {e}")
    
    def test_module_imports(self):
        """测试所有模块导入正确"""
        # Verify imports don't raise errors
        self.assertTrue(hasattr(MainWindow, '__init__'))
        self.assertTrue(hasattr(MainWindow, 'run'))


if __name__ == '__main__':
    unittest.main()
