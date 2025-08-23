# 用于分析小红书的推荐内容
import json
import asyncio
from typing import List
import time
import re
import jieba
from collections import Counter
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

class XiaohongshuNetworkCapture:
    """小红书网络请求捕获类，用于监听和收集推荐内容的API响应"""
    
    def __init__(self, page):
        """
        初始化网络捕获器
        
        Args:
            page: Playwright的page对象
        """
        self.page = page
        self.captured_responses = []
        self.target_url_pattern = "/api/sns/web/v1/feed"
        self.max_captures = 240  # 目标抓包数量，设置多一些，因为有一些帖子没有标签。
        self.clicked_sections = set()  # 记录已点击的section的data-index
        
    def start_capture(self) -> List[str]:
        """
        开始捕获网络请求（同步接口）
        
        Returns:
            List[str]: 收集到的JSON响应字符串列表
        """
        print("开始设置小红书网络监听...")
        
        # 设置响应监听器
        def handle_response(response):
            if self.target_url_pattern in response.url and response.request.method.upper() != 'OPTIONS':
                try:
                    response_text = response.text()
                    self.captured_responses.append(response_text)
                    print(f"已捕获 {len(self.captured_responses)}/{self.max_captures} 个响应")
                except Exception as e:
                    print(f"处理响应时出错: {e}")
        
        # 监听响应
        self.page.on("response", handle_response)
        
        print("开始小红书页面交互和数据收集...")
        
        # 第一次加载等待
        try:
            self.page.wait_for_load_state('networkidle', timeout=5000)
        except:
            pass
        
        scroll_count = 0
        
        while len(self.captured_responses) < self.max_captures:
            # 获取当前页面所有section元素
            sections = self.page.query_selector_all('section')
            print(f"找到 {len(sections)} 个section元素")
            
            # 点击每个section元素
            for section in sections:
                try:
                    # 获取data-index属性
                    data_index = section.get_attribute('data-index')
                    
                    # 如果没有data-index或已经点击过，跳过
                    if not data_index or data_index in self.clicked_sections:
                        continue
                    
                    print(f"点击section元素，data-index: {data_index}")
                    
                    # 滚动到元素可见位置
                    section.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    
                    # 点击元素
                    section.click()
                    
                    # 记录已点击的data-index
                    self.clicked_sections.add(data_index)
                    
                    # 等待网络空闲
                    try:
                        self.page.wait_for_load_state('networkidle', timeout=3000)
                    finally:
                        time.sleep(1)
                    
                    # 按下ESC键
                    self.page.keyboard.press('Escape')
                    time.sleep(0.5)
                    
                    # 检查是否已达到目标数量
                    if len(self.captured_responses) >= self.max_captures:
                        break
                        
                except Exception as e:
                    print(f"点击section时出错: {e}")
                    continue
            
            # 如果还没达到目标数量，下滑屏幕
            if len(self.captured_responses) < self.max_captures:
                print(f"执行第 {scroll_count + 1} 次滚动")
                try:
                    # 使用键盘下箭头滚动
                    self.page.keyboard.press('ArrowDown')
                    time.sleep(1)
                    
                    # 等待新内容加载
                    try:
                        self.page.wait_for_load_state('networkidle', timeout=3000)
                    except:
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"滚动时出错: {e}")
                    # 备用滚动方法
                    self.page.evaluate("window.scrollBy(0, 1000)")
                    time.sleep(2)
                
                scroll_count += 1
                
                # 每5次滚动等待更长时间
                if scroll_count % 5 == 0:
                    print(f"已滚动 {scroll_count} 次，等待更长时间...")
                    time.sleep(3)
        
        print(f"小红书数据收集完成，共获得 {len(self.captured_responses)} 个响应")
        print(f"共点击了 {len(self.clicked_sections)} 个不同的section元素")
        return self.captured_responses.copy()


def extract_tags_from_json_responses(json_responses: List[str]) -> List[str]:
    """
    从JSON响应中提取标签
    
    Args:
        json_responses: JSON响应字符串列表
        
    Returns:
        List[str]: 提取的标签字符串列表
    """
    all_tags = []
    
    for response_text in json_responses:
        try:
            # 解析JSON
            data = json.loads(response_text)
            
            # 提取data.items
            items = data.get('data', {}).get('items', [])
            
            for item in items:
                # 获取note_card字段
                note_card = item.get('note_card', {})
                
                # 检查是否有tag_list
                tag_list = note_card.get('tag_list', [])
                
                if tag_list:
                    # 提取每个标签的name字段
                    for tag in tag_list:
                        tag_name = tag.get('name', '')
                        if tag_name and isinstance(tag_name, str) and tag_name.strip():
                            all_tags.append(tag_name.strip())
                            print(f"提取到标签: {tag_name}")
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            continue
        except Exception as e:
            print(f"提取标签时出错: {e}")
            continue
    
    print(f"总共提取到 {len(all_tags)} 个标签")
    return all_tags


if __name__ == '__main__':
    # 测试代码
    aaa = []
    for i in range(1,3):
        with open(f'./functions/{i}.json', 'r', encoding='utf-8') as f:
            test_json = f.read()
        aaa.append(test_json)
    tags = extract_tags_from_json_responses(aaa)
    print(f"测试结果: {tags}")