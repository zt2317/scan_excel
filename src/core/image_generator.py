"""图片生成器

将数据表格生成为图片，支持企业微信发送
"""

from typing import List, Dict, Any
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64


class ImageGenerator:
    """将数据表格生成为图片"""
    
    # 列显示名称
    COLUMN_DISPLAY = {
        'date': '日期',
        'shipper': '发货人',
        'tracking': '提单号',
        'inbound_pending': '入库未扫',
        'outbound_pending': '出库未扫'
    }
    
    # 列顺序
    COLUMN_ORDER = ['date', 'shipper', 'tracking', 'inbound_pending', 'outbound_pending']
    
    # 列宽配置（像素）
    COLUMN_WIDTHS = {
        'date': 120,
        'shipper': 100,
        'tracking': 160,
        'inbound_pending': 140,
        'outbound_pending': 140
    }
    
    # 样式配置
    HEADER_BG_COLOR = (68, 114, 196)  # 蓝色
    HEADER_TEXT_COLOR = (255, 255, 255)  # 白色
    ROW_BG_COLOR_EVEN = (255, 255, 255)  # 白色
    ROW_BG_COLOR_ODD = (240, 240, 240)  # 浅灰
    ROW_TEXT_COLOR = (0, 0, 0)  # 黑色
    BORDER_COLOR = (200, 200, 200)  # 灰色
    LINE_COLOR = (200, 200, 200)  # 分隔线颜色
    
    def __init__(self):
        self.header_height = 50
        self.row_height = 60
        self.padding = 10
        
    def generate_table_image(self, data: List[Dict[str, Any]]) -> bytes:
        """生成表格图片
        
        Args:
            data: 数据列表
            
        Returns:
            图片字节数据
        """
        if not data:
            return self._generate_empty_image()
        
        # 计算图片尺寸
        available_cols = set(data[0].keys())
        columns = [col for col in self.COLUMN_ORDER if col in available_cols]
        
        total_width = sum(self.COLUMN_WIDTHS.get(col, 100) for col in columns)
        total_height = self.header_height + len(data) * self.row_height + 20
        
        # 创建图片
        img = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            # macOS字体
            font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 14)
            header_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 16)
        except:
            try:
                # Windows字体
                font = ImageFont.truetype('msyh.ttc', 14)
                header_font = ImageFont.truetype('msyh.ttc', 16)
            except:
                # 使用默认字体
                font = ImageFont.load_default()
                header_font = ImageFont.load_default()
        
        # 绘制表头
        x = 0
        for col in columns:
            width = self.COLUMN_WIDTHS.get(col, 100)
            # 绘制表头背景
            draw.rectangle([x, 0, x + width, self.header_height], 
                         fill=self.HEADER_BG_COLOR)
            # 绘制表头文字
            text = self.COLUMN_DISPLAY.get(col, col)
            self._draw_centered_text(draw, text, x, 0, width, self.header_height, 
                                   header_font, self.HEADER_TEXT_COLOR)
            x += width
        
        # 绘制数据行
        y = self.header_height
        for i, row in enumerate(data):
            # 计算行高（根据多行内容）
            row_height = self.row_height
            for col in columns:
                value = row.get(col, '-')
                if col == 'date':
                    value = self._format_date(value)
                lines = str(value).split('\n')
                # 每行文字高度约20像素
                needed_height = max(len(lines) * 20 + 20, self.row_height)
                row_height = max(row_height, needed_height)
            
            # 绘制行背景
            bg_color = self.ROW_BG_COLOR_EVEN if i % 2 == 0 else self.ROW_BG_COLOR_ODD
            draw.rectangle([0, y, total_width, y + row_height], fill=bg_color)
            
            # 绘制单元格内容和边框
            x = 0
            for col in columns:
                width = self.COLUMN_WIDTHS.get(col, 100)
                value = row.get(col, '-')
                if col == 'date':
                    value = self._format_date(value)
                
                # 绘制单元格边框
                draw.rectangle([x, y, x + width, y + row_height], 
                             outline=self.BORDER_COLOR, width=1)
                
                # 绘制文字（支持多行）
                text = str(value) if value is not None else '-'
                self._draw_multiline_text(draw, text, x + self.padding, y + self.padding,
                                        width - 2 * self.padding, row_height - 2 * self.padding,
                                        font, self.ROW_TEXT_COLOR)
                x += width
            
            y += row_height
        
        # 保存为字节
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _draw_centered_text(self, draw, text, x, y, width, height, font, color):
        """绘制居中的文字"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x + (width - text_width) // 2
        text_y = y + (height - text_height) // 2
        draw.text((text_x, text_y), text, fill=color, font=font)
    
    def _draw_multiline_text(self, draw, text, x, y, max_width, max_height, font, color):
        """绘制多行文字"""
        lines = text.split('\n')
        line_height = 20
        current_y = y
        
        for line in lines:
            if current_y + line_height > y + max_height:
                break
            draw.text((x, current_y), line, fill=color, font=font)
            current_y += line_height
    
    def _format_date(self, value: Any) -> str:
        """格式化日期"""
        if not value or value == '-':
            return '-'
        
        value_str = str(value).strip()
        
        # 已经是 YYYY-MM-DD 格式
        if len(value_str) == 10 and value_str[4] == '-' and value_str[7] == '-':
            return value_str
        
        return value_str
    
    def _generate_empty_image(self) -> bytes:
        """生成空数据图片"""
        img = Image.new('RGB', (400, 100), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 16)
        except:
            try:
                font = ImageFont.truetype('msyh.ttc', 16)
            except:
                font = ImageFont.load_default()
        
        draw.text((100, 40), "暂无数据", fill=(100, 100, 100), font=font)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()
    
    def to_base64(self, image_bytes: bytes) -> str:
        """将图片字节转换为base64字符串"""
        return base64.b64encode(image_bytes).decode('utf-8')
