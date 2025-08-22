import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from typing import List
import numpy as np


def create_picture_directory():
    """创建picture目录（如果不存在）"""
    picture_dir = os.path.join(os.path.dirname(__file__), 'picture')
    if not os.path.exists(picture_dir):
        os.makedirs(picture_dir)
        print(f"创建目录: {picture_dir}")
    return picture_dir


def get_font_path():
    """获取字体文件路径"""
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    font_file = os.path.join(font_dir, 'zh-cn.ttf')
    
    if not os.path.exists(font_file):
        print(f"警告: 字体文件不存在 {font_file}")
        return None
    
    return font_file


def generate_wordcloud(processed_text: str, output_filename: str = None) -> str:
    """
    从预处理后的文本生成词云图片
    
    Args:
        processed_text: 预处理后的文本内容
        output_filename: 输出文件名（可选）
        
    Returns:
        str: 生成的图片文件路径
    """
    if not processed_text or not processed_text.strip():
        print("错误: 没有提供有效的文本内容")
        return None
    
    # 创建输出目录
    picture_dir = create_picture_directory()
    
    # 获取字体路径
    font_path = get_font_path()
    
    # 创建圆形遮罩
    def create_circle_mask(width, height):
        """创建圆形遮罩"""
        mask = np.zeros((height, width), dtype=np.uint8)
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y) - 10
        
        y, x = np.ogrid[:height, :width]
        mask_condition = (x - center_x) ** 2 + (y - center_y) ** 2 > radius ** 2
        mask[mask_condition] = 255
        return mask
    
    # 生成词云
    print("正在生成词云...")
    width, height = 1200, 1200  # 使用正方形画布以适配圆形
    circle_mask = create_circle_mask(width, height)
    
    # 自定义蓝色渐变颜色函数
    def blue_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        """蓝色渐变颜色函数：深蓝到浅蓝"""
        # 根据字体大小决定颜色深浅，字体越大颜色越深
        # 动态计算强度，不设置固定的最大字体大小限制
        intensity = min(font_size / 200.0, 1.0)  # 使用相对比例计算
        
        # 深蓝色 RGB(0, 51, 102) 到 浅蓝色 RGB(173, 216, 230)
        r = int(173 - 173 * intensity)
        g = int(216 - 165 * intensity) 
        b = int(230 - 128 * intensity)
        
        return f"rgb({r},{g},{b})"
    
    wordcloud_config = {
        'width': width,
        'height': height,
        'background_color': 'white',
        'max_words': 200,
        'relative_scaling': 0.5,
        'mask': circle_mask,
        'prefer_horizontal': 0.9,  # 优先水平排列
        'min_font_size': 10,
        'color_func': blue_color_func
    }
    
    # 如果有字体文件，使用中文字体
    if font_path:
        wordcloud_config['font_path'] = font_path
    
    try:
        wordcloud = WordCloud(**wordcloud_config).generate(processed_text)
        
        # 生成输出文件名
        if not output_filename:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"user_wordcloud_{timestamp}.png"
        
        # 确保文件名以.png结尾
        if not output_filename.endswith('.png'):
            output_filename += '.png'
        
        output_path = os.path.join(picture_dir, output_filename)
        
        # 保存词云图片
        plt.figure(figsize=(15, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 词云图片已保存到: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"生成词云时出错: {e}")
        return None


def main():
    """测试函数"""
    # 这里可以放一些测试代码
    test_text = "测试 视频 标题 描述 内容 推荐 热门 游戏 音乐 科技"
    result = generate_wordcloud(test_text, "test_wordcloud.png")
    if result:
        print(f"测试完成，生成的文件: {result}")


if __name__ == "__main__":
    main()