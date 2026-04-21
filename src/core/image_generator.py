"""图片生成器

将数据表格生成为图片，支持企业微信发送
"""

from typing import List, Dict, Any, Tuple
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
    
    # 最小列宽配置（像素）
    MIN_COLUMN_WIDTHS = {
        'date': 100,
        'shipper': 80,
        'tracking': 120,
        'inbound_pending': 100,
        'outbound_pending': 100
    }
    
    # 样式配置
    HEADER_BG_COLOR = (68, 114, 196)  # 蓝色
    HEADER_TEXT_COLOR = (255, 255, 255)  # 白色
    ROW_BG_COLOR_EVEN = (255, 255, 255)  # 白色
    ROW_BG_COLOR_ODD = (240, 240, 240)  # 浅灰
    ROW_TEXT_COLOR = (0, 0, 0)  # 黑色
    BORDER_COLOR = (200, 200, 200)  # 灰色
    
    def __init__(self):
        self.header_height = 50
        self.row_height = 40
        self.padding = 10
        self.line_height = 22
        
    def _get_font(self):
        """获取字体"""
        try:
            # macOS 中文字体
            return ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc', 14)
        except:
            try:
                # 备选字体
                return ImageFont.truetype('/System/Library/Fonts/NotoSansCJK.ttc', 14)
            except:
                try:
                    # Windows 字体
                    return ImageFont.truetype('msyh.ttc', 14)
                except:
                    # 使用默认字体
                    return ImageFont.load_default()
    
    def _calculate_text_width(self, draw, text: str, font) -> int:
        """计算文字宽度"""
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    
    def _calculate_column_widths(self, data: List[Dict], columns: List[str], font) -> Dict[str, int]:
        """根据内容计算每列的实际宽度"""
        # 创建临时图片用于计算
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        column_widths = {}
        
        for col in columns:
            # 最小宽度
            min_width = self.MIN_COLUMN_WIDTHS.get(col, 100)
            max_width = min_width
            
            # 检查表头宽度
            header_text = self.COLUMN_DISPLAY.get(col, col)
            header_width = self._calculate_text_width(temp_draw, header_text, font) + 2 * self.padding
            max_width = max(max_width, header_width)
            
            # 检查所有数据行的宽度
            for row in data:
                value = row.get(col, '-')
                if col == 'date':
                    value = self._format_date(value)
                
                # 处理多行，取最长的一行
                lines = str(value).split('\n')
                for line in lines:
                    line_width = self._calculate_text_width(temp_draw, line, font) + 2 * self.padding
                    max_width = max(max_width, line_width)
            
            # 添加一些边距
            column_widths[col] = int(max_width) + 20
        
        return column_widths
    
    # 企业微信限制
    MAX_IMAGE_SIZE_MB = 2  # 2MB
    MAX_IMAGE_WIDTH = 1200  # 最大宽度
    ROWS_PER_IMAGE = 50  # 每批最多50行
    
    def __init__(self):
        self.header_height = 50
        self.row_height = 40
        self.padding = 10
        self.line_height = 22
        self.title_height = 60  # 标题区域高度
        
    def generate_table_images(self, data: List[Dict[str, Any]], sheet_name: str = "") -> List[bytes]:
        """生成表格图片（分批，每批最多50行）
        
        Args:
            data: 数据列表
            sheet_name: Excel sheet名称
            
        Returns:
            图片字节数据列表
        """
        if not data:
            return [self._generate_empty_image()]
        
        # 获取当前时间
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 分批处理
        images = []
        total_rows = len(data)
        total_batches = (total_rows + self.ROWS_PER_IMAGE - 1) // self.ROWS_PER_IMAGE
        
        for i in range(0, total_rows, self.ROWS_PER_IMAGE):
            batch = data[i:i + self.ROWS_PER_IMAGE]
            batch_num = i // self.ROWS_PER_IMAGE + 1
            image_bytes = self._generate_single_image(
                batch, 
                batch_num, 
                total_batches,
                sheet_name,
                current_time
            )
            images.append(image_bytes)
        
        return images
    
    def _generate_single_image(self, data: List[Dict[str, Any]], batch_num: int = 1, 
                               total_batches: int = 1, sheet_name: str = "", 
                               current_time: str = "") -> bytes:
        """生成单张图片"""
        if not data:
            return self._generate_empty_image()
        
        # 确定要显示的列
        available_cols = set(data[0].keys())
        columns = [col for col in self.COLUMN_ORDER if col in available_cols]
        
        # 获取字体
        font = self._get_font()
        
        # 计算列宽
        column_widths = self._calculate_column_widths(data, columns, font)
        
        # 计算总宽度
        total_width = sum(column_widths.values())
        
        # 限制最大宽度
        if total_width > self.MAX_IMAGE_WIDTH:
            scale = self.MAX_IMAGE_WIDTH / total_width
            for col in columns:
                column_widths[col] = int(column_widths[col] * scale)
            total_width = sum(column_widths.values())
        
        # 计算每行高度和总高度
        rows_height = []
        for row in data:
            row_height = self.row_height
            for col in columns:
                value = row.get(col, '-')
                if col == 'date':
                    value = self._format_date(value)
                lines = str(value).split('\n')
                needed_height = len(lines) * self.line_height + 2 * self.padding
                row_height = max(row_height, needed_height)
            rows_height.append(row_height)
        
        # 计算总高度（标题 + 表头 + 数据 + 底部边距）
        total_height = (self.title_height + self.header_height + sum(rows_height) + 30)
        
        # 创建图片
        img = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # 绘制标题（在最顶部）
        self._draw_title(draw, sheet_name, current_time, batch_num, total_batches, 
                        total_width, font)
        
        # 绘制表头（在标题下方）
        header_y = self.title_height
        x = 0
        for col in columns:
            width = column_widths[col]
            draw.rectangle([x, header_y, x + width, header_y + self.header_height], 
                         fill=self.HEADER_BG_COLOR)
            text = self.COLUMN_DISPLAY.get(col, col)
            self._draw_centered_text(draw, text, x, header_y, width, self.header_height, 
                                   font, self.HEADER_TEXT_COLOR)
            x += width
        
        # 绘制数据行
        y = header_y + self.header_height
        for i, row in enumerate(data):
            row_height = rows_height[i]
            bg_color = self.ROW_BG_COLOR_EVEN if i % 2 == 0 else self.ROW_BG_COLOR_ODD
            
            draw.rectangle([0, y, total_width, y + row_height], fill=bg_color)
            
            x = 0
            for col in columns:
                width = column_widths[col]
                value = row.get(col, '-')
                if col == 'date':
                    value = self._format_date(value)
                
                draw.rectangle([x, y, x + width, y + row_height], 
                             outline=self.BORDER_COLOR, width=1)
                
                text = str(value) if value is not None else '-'
                self._draw_text_left_aligned(draw, text, x + self.padding, y + self.padding,
                                            width - 2 * self.padding, row_height - 2 * self.padding,
                                            font, self.ROW_TEXT_COLOR)
                x += width
            
            y += row_height
        
        # 保存并压缩
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        # 检查大小，如果超过限制则压缩
        image_bytes = buffer.getvalue()
        max_size = self.MAX_IMAGE_SIZE_MB * 1024 * 1024
        
        if len(image_bytes) > max_size:
            buffer = io.BytesIO()
            img = img.convert('RGB')
            for quality in [85, 70, 50, 30]:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                if buffer.tell() < max_size:
                    break
            buffer.seek(0)
            image_bytes = buffer.getvalue()
        
        return image_bytes
    
    def _draw_title(self, draw, sheet_name: str, current_time: str, batch_num: int, 
                   total_batches: int, width: int, font):
        """绘制标题"""
        # 标题背景色
        title_bg_color = (240, 240, 240)
        
        # 绘制标题背景
        draw.rectangle([0, 0, width, self.title_height], fill=title_bg_color)
        
        # 构建标题文字
        if sheet_name:
            title_text = f"{sheet_name}"
        else:
            title_text = "Excel数据推送"
        
        # 添加时间和页码
        if total_batches > 1:
            subtitle = f"{current_time}  第{batch_num}/{total_batches}页"
        else:
            subtitle = current_time
        
        # 使用更大的字体（18号）
        try:
            title_font = ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc', 18)
        except:
            try:
                title_font = ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc', 18)
            except:
                title_font = font
        
        # 绘制主标题（加粗效果通过使用Medium字体）
        title_width = self._calculate_text_width(draw, title_text, title_font)
        title_x = (width - title_width) // 2
        title_y = 8
        draw.text((title_x, title_y), title_text, fill=(0, 0, 0), font=title_font)
        
        # 绘制副标题（时间和页码）
        subtitle_font = font  # 使用普通字体
        subtitle_width = self._calculate_text_width(draw, subtitle, subtitle_font)
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = 35
        draw.text((subtitle_x, subtitle_y), subtitle, fill=(100, 100, 100), font=subtitle_font)
        
        # 绘制数据行
        y = self.header_height
        for i, row in enumerate(data):
            row_height = rows_height[i]
            bg_color = self.ROW_BG_COLOR_EVEN if i % 2 == 0 else self.ROW_BG_COLOR_ODD
            
            draw.rectangle([0, y, total_width, y + row_height], fill=bg_color)
            
            x = 0
            for col in columns:
                width = column_widths[col]
                value = row.get(col, '-')
                if col == 'date':
                    value = self._format_date(value)
                
                draw.rectangle([x, y, x + width, y + row_height], 
                             outline=self.BORDER_COLOR, width=1)
                
                text = str(value) if value is not None else '-'
                self._draw_text_left_aligned(draw, text, x + self.padding, y + self.padding,
                                            width - 2 * self.padding, row_height - 2 * self.padding,
                                            font, self.ROW_TEXT_COLOR)
                x += width
            
            y += row_height
        
        # 添加批次标记（在表格下方空白区域）
        if total_batches > 1:
            batch_text = f"第{batch_num}/{total_batches}页"
            text_width = self._calculate_text_width(draw, batch_text, font)
            # 在表格结束后画页码（y位置 + 15像素间隔）
            page_y = self.header_height + sum(rows_height) + 15
            draw.text((total_width - text_width - 10, page_y), 
                     batch_text, fill=(100, 100, 100), font=font)
        
        # 保存并压缩
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        # 检查大小，如果超过限制则压缩
        image_bytes = buffer.getvalue()
        max_size = self.MAX_IMAGE_SIZE_MB * 1024 * 1024
        
        if len(image_bytes) > max_size:
            # 转换为JPEG并压缩
            buffer = io.BytesIO()
            img = img.convert('RGB')
            # 逐步降低质量直到满足大小要求
            for quality in [85, 70, 50, 30]:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                if buffer.tell() < max_size:
                    break
            buffer.seek(0)
            image_bytes = buffer.getvalue()
        
        return image_bytes
    
    def _draw_centered_text(self, draw, text, x, y, width, height, font, color):
        """绘制居中的文字"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x + (width - text_width) // 2
        text_y = y + (height - text_height) // 2
        draw.text((text_x, text_y), text, fill=color, font=font)
    
    def _draw_text_left_aligned(self, draw, text, x, y, max_width, max_height, font, color):
        """绘制左对齐的多行文字"""
        lines = text.split('\n')
        current_y = y
        
        for line in lines:
            if current_y + self.line_height > y + max_height:
                break
            draw.text((x, current_y), line, fill=color, font=font)
            current_y += self.line_height
    
    def _format_date(self, value: Any) -> str:
        """格式化日期"""
        if not value or value == '-':
            return '-'
        return str(value).strip()
    
    def _generate_empty_image(self) -> bytes:
        """生成空数据图片"""
        img = Image.new('RGB', (400, 100), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        font = self._get_font()
        draw.text((100, 40), "暂无数据", fill=(100, 100, 100), font=font)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()
    
    def to_base64(self, image_bytes: bytes) -> str:
        """将图片字节转换为base64字符串"""
        return base64.b64encode(image_bytes).decode('utf-8')
