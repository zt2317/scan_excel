#!/usr/bin/env python3
"""Generate application icon for Windows executable"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_icon(size=256):
    """Create a simple Excel-themed icon"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions
    padding = size // 8
    corner_radius = size // 8
    
    # Draw Excel green background (rounded rectangle)
    bg_color = (33, 115, 70)  # Excel green
    
    # Draw rounded rectangle manually
    x1, y1 = padding, padding
    x2, y2 = size - padding, size - padding
    
    # Main rectangle
    draw.rectangle([x1 + corner_radius, y1, x2 - corner_radius, y2], fill=bg_color)
    draw.rectangle([x1, y1 + corner_radius, x2, y2 - corner_radius], fill=bg_color)
    
    # Corners
    draw.ellipse([x1, y1, x1 + corner_radius * 2, y1 + corner_radius * 2], fill=bg_color)
    draw.ellipse([x2 - corner_radius * 2, y1, x2, y1 + corner_radius * 2], fill=bg_color)
    draw.ellipse([x1, y2 - corner_radius * 2, x1 + corner_radius * 2, y2], fill=bg_color)
    draw.ellipse([x2 - corner_radius * 2, y2 - corner_radius * 2, x2, y2], fill=bg_color)
    
    # Draw grid pattern (spreadsheet-like)
    line_color = (255, 255, 255, 200)
    line_width = max(1, size // 64)
    
    # Horizontal lines
    grid_y_positions = [y1 + (y2 - y1) * i // 5 for i in range(1, 5)]
    for y in grid_y_positions:
        draw.line([(x1 + corner_radius, y), (x2 - corner_radius, y)], 
                 fill=line_color, width=line_width)
    
    # Vertical lines
    grid_x_positions = [x1 + (x2 - x1) * i // 4 for i in range(1, 4)]
    for x in grid_x_positions:
        draw.line([(x, y1 + corner_radius), (x, y2 - corner_radius)], 
                 fill=line_color, width=line_width)
    
    return img


def save_ico(sizes=[16, 32, 48, 256]):
    """Save icon in multiple sizes for Windows"""
    images = []
    
    for size in sizes:
        img = create_icon(size)
        images.append(img)
    
    # Save as ICO
    output_path = 'assets/icon.ico'
    os.makedirs('assets', exist_ok=True)
    
    # Save with multiple sizes
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes]
    )
    
    print(f"Icon saved to {output_path}")
    print(f"Sizes: {sizes}")


if __name__ == '__main__':
    save_ico()
