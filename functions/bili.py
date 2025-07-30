# 用于分析bilibili的视频流推荐
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

class BilibiliNetworkCapture:
    """Bilibili网络请求捕获类，用于监听和收集推荐视频的API响应"""
    
    def __init__(self, page):
        """
        初始化网络捕获器
        
        Args:
            page: Playwright的page对象
        """
        self.page = page
        self.captured_responses = []
        self.target_url_pattern = "https://api.bilibili.com/x/web-interface/wbi/index/top/feed/rcmd?web_location"
        self.max_captures = 10
        
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
    
    async def scroll_and_collect(self) -> List[str]:
        """
        滚动页面并收集网络响应
        
        Returns:
            List[str]: 收集到的JSON响应字符串列表
        """
        print("开始滚动页面并收集网络响应...")
        
        # 等待页面加载完成
        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        scroll_count = 0
        max_scrolls = 50  # 最大滚动次数，防止无限滚动
        
        while len(self.captured_responses) < self.max_captures and scroll_count < max_scrolls:
            # 滚动到页面底部
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            print(f"执行第 {scroll_count + 1} 次滚动")
            
            # 等待新内容加载
            await asyncio.sleep(2)
            
            # 检查是否有新的网络请求
            await self.page.wait_for_load_state('networkidle', timeout=5000)
            
            scroll_count += 1
            
            # 如果连续多次滚动都没有新的响应，可能需要更长的等待时间
            if scroll_count % 5 == 0:
                print(f"已滚动 {scroll_count} 次，等待更长时间...")
                await asyncio.sleep(3)
        
        print(f"滚动完成，共收集到 {len(self.captured_responses)} 个响应")
        return self.captured_responses.copy()
    
    def capture_network_requests(self) -> List[str]:
        """
        同步方法：捕获网络请求
        
        Returns:
            List[str]: 收集到的JSON响应字符串列表
        """
        async def async_capture():
            await self.setup_network_listener()
            return await self.scroll_and_collect()
        
        # 在页面的上下文中运行异步函数
        return self.page.evaluate("""
            async () => {
                // 这里我们使用同步的方式来处理
                return new Promise((resolve) => {
                    setTimeout(() => resolve([]), 1000);
                });
            }
        """)
    
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
                    print(f"捕获到API响应: {response.url}")
                    self.captured_responses.append(response_text)
                    print(f"已捕获 {len(self.captured_responses)}/{self.max_captures} 个响应")
                except Exception as e:
                    print(f"处理响应时出错: {e}")
        
        # 监听响应
        self.page.on("response", handle_response)
        
        print("开始滚动页面收集数据...")
        scroll_count = 0
        max_scrolls = 30
        
        while len(self.captured_responses) < self.max_captures and scroll_count < max_scrolls:
            # 滚动页面
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            print(f"执行第 {scroll_count + 1} 次滚动")
            
            # 等待加载
            time.sleep(1)
            
            # 等待网络空闲
            try:
                self.page.wait_for_load_state('networkidle', timeout=5000)
            except:
                pass
            
            scroll_count += 1
            
            # 每5次滚动等待更长时间
            if scroll_count % 5 == 0:
                print(f"已滚动 {scroll_count} 次，等待更长时间...")
                time.sleep(2.1)
        
        print(f"数据收集完成，共获得 {len(self.captured_responses)} 个响应")
        return self.captured_responses.copy()

def parse_html_to_tag(html:str) -> list[str]:
    parsed_html = BeautifulSoup(html,'lxml')
    divs = parsed_html.find_all('div',attrs={'class':'ordinary-tag'})
    tags = [div.text.replace('\n','')  for div in divs]
    return tags


def extract_text_from_json_responses(json_responses: List[str]) -> str:
    """
    从JSON响应中提取文本内容
    
    Args:
        json_responses: JSON响应字符串列表
        
    Returns:
        str: 提取的所有文本内容
    """
    all_text = []
    all_urls = []
    for response_text in json_responses:
        try:
            # 解析JSON
            data = json.loads(response_text)
            
            # 提取视频流标签
            items = data.get('data',{}).get('item',[])
            for item in items:
                uri = item.get('uri',None)
                if uri:
                    all_urls.append(uri)
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            continue
        except Exception as e:
            print(f"提取文本时出错: {e}")
            continue
    # 访问推荐的视频链接，获取它的标签
    for url in tqdm(all_urls):
        headers = {
            'referer': 'https://www.bilibili.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
                }
        response = requests.get(url,headers=headers)
        tags = parse_html_to_tag(response.text)
        all_text += tags
        time.sleep(0.3)

    # 合并所有文本
    combined_text = ' '.join(all_text)
    print(f"提取到的文本长度: {len(combined_text)} 字符")
    
    return combined_text


def preprocess_text(text: str) -> str:
    """
    预处理文本，进行分词和清理
    
    Args:
        text: 原始文本
        
    Returns:
        str: 处理后的文本
    """
    # 使用jieba进行中文分词
    words = jieba.cut(text)
    
    # 过滤词汇
    filtered_words = []
    for word in words:
        word = word.strip()
        # 过滤条件：长度大于1，不是纯数字，不是标点符号
        if (len(word) > 1 and 
            not word.isdigit() and 
            not re.match(r'^[^\w\s]+$', word) and
            word not in ['的', '了', '在', '是', '有', '和', '就', '不', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '还', '把', '那', '这', '来', '很', '从', '被', '让', '给', '对', '向', '以', '所', '为', '而', '也', '都', '能', '下', '自己', '什么', '怎么', '可以', '如果', '因为', '所以', '但是', '然后', '现在', '已经', '一个', '这个', '那个', '我们', '他们', '她们', '它们']):
            filtered_words.append(word)
    
    # 统计词频，只保留出现频率较高的词
    word_freq = Counter(filtered_words)
    # 只保留出现次数大于1的词，或者总词数少于100时保留所有词
    if len(word_freq) > 100:
        filtered_words = [word for word, freq in word_freq.items() if freq > 1]
    
    result_text = ' '.join(filtered_words)
    print(f"分词后的文本长度: {len(result_text)} 字符")
    print(f"词汇数量: {len(filtered_words)}")
    
    return result_text

