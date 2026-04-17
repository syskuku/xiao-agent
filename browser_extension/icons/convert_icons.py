#!/usr/bin/env python3
"""
图标转换脚本 - 将SVG转换为不同尺寸的PNG图标
"""

import os
import sys
from pathlib import Path

def convert_svg_to_png():
    """将SVG图标转换为PNG格式"""
    try:
        # 尝试导入cairosvg
        import cairosvg
        from PIL import Image
        import io
        
        # 图标尺寸
        sizes = [16, 48, 128]
        
        # 获取当前目录
        current_dir = Path(__file__).parent
        svg_file = current_dir / "icon.svg"
        
        if not svg_file.exists():
            print(f"错误: 找不到SVG文件 {svg_file}")
            return False
        
        print(f"正在转换图标: {svg_file}")
        
        # 读取SVG内容
        with open(svg_file, 'r', encoding='utf-8') as f:
            svg_data = f.read()
        
        # 转换为不同尺寸
        for size in sizes:
            output_file = current_dir / f"icon{size}.png"
            
            # 使用cairosvg转换
            png_data = cairosvg.svg2png(
                bytestring=svg_data.encode('utf-8'),
                output_width=size,
                output_height=size
            )
            
            # 保存PNG文件
            with open(output_file, 'wb') as f:
                f.write(png_data)
            
            print(f"已生成: {output_file}")
        
        # 创建连接状态图标
        connected_svg = svg_data.replace('#1a73e8', '#34a853')
        for size in [48]:  # 只需要48x48的连接状态图标
            output_file = current_dir / f"icon{size}_connected.png"
            
            png_data = cairosvg.svg2png(
                bytestring=connected_svg.encode('utf-8'),
                output_width=size,
                output_height=size
            )
            
            with open(output_file, 'wb') as f:
                f.write(png_data)
            
            print(f"已生成连接状态图标: {output_file}")
        
        print("图标转换完成!")
        return True
        
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install cairosvg Pillow")
        return False
    except Exception as e:
        print(f"转换失败: {e}")
        return False

def create_simple_icons():
    """创建简单的占位图标（当无法转换SVG时）"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        current_dir = Path(__file__).parent
        
        # 创建不同尺寸的图标
        sizes = [16, 48, 128]
        
        for size in sizes:
            # 创建蓝色背景
            img = Image.new('RGB', (size, size), color='#1a73e8')
            draw = ImageDraw.Draw(img)
            
            # 绘制简单的麦克风形状
            center = size // 2
            mic_width = size // 4
            mic_height = size // 2
            
            # 麦克风主体
            draw.ellipse([
                center - mic_width//2, 
                center - mic_height//2,
                center + mic_width//2, 
                center + mic_height//2
            ], fill='white')
            
            # 麦克风支架
            draw.line([
                center, center + mic_height//2,
                center, center + mic_height//2 + size//8
            ], fill='white', width=max(1, size//16))
            
            # 底座
            draw.line([
                center - size//6, center + mic_height//2 + size//8,
                center + size//6, center + mic_height//2 + size//8
            ], fill='white', width=max(1, size//16))
            
            # 保存图标
            output_file = current_dir / f"icon{size}.png"
            img.save(output_file, 'PNG')
            print(f"已生成占位图标: {output_file}")
        
        # 创建连接状态图标（绿色）
        for size in [48]:
            img = Image.new('RGB', (size, size), color='#34a853')
            draw = ImageDraw.Draw(img)
            
            center = size // 2
            mic_width = size // 4
            mic_height = size // 2
            
            draw.ellipse([
                center - mic_width//2, 
                center - mic_height//2,
                center + mic_width//2, 
                center + mic_height//2
            ], fill='white')
            
            draw.line([
                center, center + mic_height//2,
                center, center + mic_height//2 + size//8
            ], fill='white', width=max(1, size//16))
            
            draw.line([
                center - size//6, center + mic_height//2 + size//8,
                center + size//6, center + mic_height//2 + size//8
            ], fill='white', width=max(1, size//16))
            
            output_file = current_dir / f"icon{size}_connected.png"
            img.save(output_file, 'PNG')
            print(f"已生成连接状态图标: {output_file}")
        
        print("占位图标生成完成!")
        return True
        
    except ImportError:
        print("缺少PIL库，请运行: pip install Pillow")
        return False
    except Exception as e:
        print(f"生成占位图标失败: {e}")
        return False

if __name__ == "__main__":
    print("小爱音箱浏览器控制器 - 图标转换工具")
    print("=" * 40)
    
    # 首先尝试使用cairosvg转换
    if not convert_svg_to_png():
        print("\n尝试使用PIL生成占位图标...")
        if not create_simple_icons():
            print("\n无法生成图标，请手动创建图标文件")
            print("需要以下文件:")
            print("  - icon16.png (16x16)")
            print("  - icon48.png (48x48)")
            print("  - icon128.png (128x128)")
            print("  - icon48_connected.png (48x48, 绿色)")
            sys.exit(1)
    
    print("\n图标文件已准备就绪!")
    print("请将生成的图标文件复制到browser_extension/icons/目录")