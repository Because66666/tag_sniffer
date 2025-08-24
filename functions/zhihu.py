# 用于分析知乎的推荐流分析
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

class ZhihuNetworkCapture:
    """知乎网络请求捕获类，用于监听和收集推荐链接的API响应"""
    
    def __init__(self, page):
        """
        初始化网络捕获器
        
        Args:
            page: Playwright的page对象
        """
        self.page = page
        self.captured_responses = []
        self.target_url_pattern = "feed/topstory/recommend"
        self.max_captures = 40
        
    async def setup_network_listener(self):
        """设置网络请求监听器"""
        async def handle_response(response):
            # 检查响应URL是否包含目标模式
            if self.target_url_pattern in response.url:
                try:
                    # 获取响应内容
                    response_text = await response.text()
                    # print(f"捕获到API响应: {response.url}")
                    print(f"响应长度: {len(response_text)} 字符")
                    
                    # 将响应文本添加到列表中
                    self.captured_responses.append(response_text)
                    print(f"已捕获 {len(self.captured_responses)}/{self.max_captures} 个响应")
                    
                except Exception as e:
                    print(f"处理响应时出错: {e}")
        
        # 监听响应事件
        self.page.on("response", handle_response)
        print("网络监听器已设置完成")
    
    
    def start_capture(self) -> List[str]:
        """
        开始捕获网络请求（同步接口）
        
        Returns:
            List[str]: 收集到的JSON响应字符串列表
        """
        print("开始设置网络监听...")
        
        # 设置响应监听器
        def handle_response(response):
            if self.target_url_pattern in response.url:
                try:
                    response_text = response.text()
                    # print(f"捕获到API响应: {response.url}")
                    self.captured_responses.append(response_text)
                    print(f"已捕获 {len(self.captured_responses)}/{self.max_captures} 个响应")
                except Exception as e:
                    print(f"处理响应时出错: {e}")
        
        # 监听响应
        self.page.on("response", handle_response)
        
        print("开始滚动页面收集数据...")
        scroll_count = 0
        
        while len(self.captured_responses) < self.max_captures:
            # 滚动页面
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            print(f"执行第 {scroll_count + 1} 次滚动")
            
            # 等待加载
            time.sleep(0.7)
            
            # 等待网络空闲
            try:
                self.page.wait_for_load_state('networkidle', timeout=5000)
            except:
                pass
            
            scroll_count += 1
            
            # 每5次滚动等待更长时间
            if scroll_count % 5 == 0:
                print(f"已滚动 {scroll_count} 次，等待更长时间...")
                time.sleep(2)
        
        print(f"数据收集完成，共获得 {len(self.captured_responses)} 个响应")
        return self.captured_responses.copy()
    
    def extract_tags_from_responses(self) -> str:
        """
        从知乎推荐API的JSON响应中提取标签内容
        
        Returns:
            str: 提取的所有标签文本内容
        """
        all_text = []
        all_urls = []
        for response_text in self.captured_responses:
            try:
                # 解析JSON
                data = json.loads(response_text)
                
                # 提取知乎推荐内容
                items = data.get('data',[])
                for item in items:
                    target = item.get('target',{})
                    if target.get('answer_type','') == 'normal':
                        question_id = target.get('id','')
                        author_id = target.get('question',{}).get('id','')
                        all_urls.append(f'https://www.zhihu.com/question/{author_id}/answer/{question_id}')
                
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                continue
            except Exception as e:
                print(f"提取文本时出错: {e}")
                continue
        
        # 使用Playwright页面访问知乎推荐的链接，获取它的标签
        for url in tqdm(all_urls):
            try:
                # 使用Playwright页面导航到URL
                self.page.goto(url)
                self.page.wait_for_timeout(1000)  # 等待页面加载
                
                # 获取页面HTML内容
                html_content = self.page.content()
                tags = parse_zhihu_html_to_tag(html_content)
                all_text += tags
                
                time.sleep(0.3)
            except Exception as e:
                print(f"访问URL {url} 时出错: {e}")
                continue
        
        # 合并所有文本
        combined_text = ' '.join(all_text)
        print(f"提取到的文本长度: {len(combined_text)} 字符")
        
        return combined_text

def parse_zhihu_html_to_tag(html:str) -> list[str]:
    """解析知乎页面HTML，提取标签信息"""
    parsed_html = BeautifulSoup(html,'lxml')
    tags = []
    
    # 尝试从meta标签获取关键词
    keywords_meta = parsed_html.find('meta',attrs={'name':'keywords'})
    if keywords_meta and keywords_meta.get('content'):
        keywords = keywords_meta['content']
        tags.extend(keywords.split(','))
    
    # 尝试从知乎特有的话题标签获取
    topic_tags = parsed_html.find_all('a', class_='TopicLink')
    for tag in topic_tags:
        if tag.text:
            tags.append(tag.text.strip())
    
    # 去重并过滤空标签
    tags = list(set([tag.strip() for tag in tags if tag.strip()]))
    return tags





if __name__ == '__main__':
    with open(r'D:\python\tag_analyse\functions\1.html','r',encoding='utf-8') as f:
        html = f.read()
    tags = parse_zhihu_html_to_tag(html)
    print(tags)

