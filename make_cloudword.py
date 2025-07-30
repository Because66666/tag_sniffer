import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from typing import List


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
    
    # 生成词云
    print("正在生成词云...")
    wordcloud_config = {
        'width': 1200,
        'height': 800,
        'background_color': 'white',
        'max_words': 200,
        'relative_scaling': 0.5,
        'colormap': 'viridis'
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