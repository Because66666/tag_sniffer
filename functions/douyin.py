# 用于分析抖音的视频流推荐
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

class DouyinNetworkCapture:
    """抖音网络请求捕获类，用于监听和收集推荐视频的API响应"""
    
    def __init__(self, page):
        """
        初始化网络捕获器
        
        Args:
            page: Playwright的page对象
        """
        self.page = page
        self.captured_responses = []
        self.target_url_pattern = "/aweme/v1/web/tab/feed"
        self.max_captures = 33  # 增加捕获数量以确保能获得220个caption
        
    async def setup_network_listener(self):
        """设置网络请求监听器"""
        async def handle_response(response):
            # 检查响应URL是否包含目标模式
            if self.target_url_pattern in response.url and response.request.method.upper() != 'OPTIONS':
                try:
                    # 获取响应内容
                    response_text = await response.text()
                    print(f"捕获到抖音API响应: {response.url}")
                    print(f"响应长度: {len(response_text)} 字符")
                    
                    # 将响应文本添加到列表中
                    self.captured_responses.append(response_text)
                    print(f"已捕获 {len(self.captured_responses)}/{self.max_captures} 个响应")
                    
                except Exception as e:
                    print(f"处理响应时出错: {e}")
        
        # 监听响应事件
        self.page.on("response", handle_response)
        print("抖音网络监听器已设置完成")
    
    def start_capture(self) -> List[str]:
        """
        开始捕获网络请求（同步接口）
        
        Returns:
            List[str]: 收集到的JSON响应字符串列表
        """
        print("开始设置抖音网络监听...")
        
        # 设置响应监听器
        def handle_response(response):
            if self.target_url_pattern in response.url:
                try:
                    response_text = response.text()
                    # print(f"捕获到抖音API响应: {response.url}")
                    self.captured_responses.append(response_text)
                    print(f"已捕获 {len(self.captured_responses)}/{self.max_captures} 个响应")
                except Exception as e:
                    print(f"处理响应时出错: {e}")
        
        # 监听响应
        self.page.on("response", handle_response)
        
        print("开始滚动抖音页面收集数据...")
        scroll_count = 0
        # 第一次下滑前等待其加载完毕。
        try:
            self.page.wait_for_load_state('networkidle', timeout=5000)
        except:
            pass
        while len(self.captured_responses) < self.max_captures:
            # 等待网络空闲

            try:
                # 方法1：使用键盘事件
                self.page.keyboard.press('ArrowDown')
                time.sleep(0.5)
                
                # # 方法2：鼠标滚轮
                # self.page.mouse.wheel(0, 800)
                # time.sleep(0.5)
                
                # # 方法3：DOM操作
                # self.page.evaluate("""
                #     // 尝试找到抖音的视频容器
                #     const containers = [
                #         '[data-e2e="recommend-list-container"]',
                #         '.recommend-container',
                #         '#douyin-right-container',
                #         '.video-container',
                #         'body'
                #     ];
                    
                #     for (let selector of containers) {
                #         const container = document.querySelector(selector);
                #         if (container) {
                #             container.scrollTop += 800;
                #             break;
                #         }
                #     }
                    
                #     // 同时尝试window滚动
                #     window.scrollBy(0, 800);
                # """)
                
                print(f"执行第 {scroll_count + 1} 次滚动")
            except Exception as e:
                print(f"滚动时出错: {e}，使用备用方法")
                # 备用方法
                self.page.evaluate("window.scrollBy(0, 1000)")
            
            # 等待加载
            time.sleep(0.7)
            
            # # 等待网络空闲
            # try:
            #     self.page.wait_for_load_state('networkidle', timeout=5000)
            # except:
            #     pass
            
            scroll_count += 1
            
            # 每5次滚动等待更长时间
            if scroll_count % 5 == 0:
                print(f"已滚动 {scroll_count} 次，等待更长时间...")
                time.sleep(2)
        
        print(f"抖音数据收集完成，共获得 {len(self.captured_responses)} 个响应")
        return self.captured_responses.copy()


def extract_captions_from_json_responses(json_responses: List[str]) -> List[str]:
    """
    从JSON响应中提取caption字段
    
    Args:
        json_responses: JSON响应字符串列表
        
    Returns:
        List[str]: 提取的caption字符串列表
    """
    all_captions = []
    # 对caption字符串处理
    def cut_from_first_hash(s):
        # 查找第一个#的位置
        first_hash_index = s.find('#')
        # 如果找到#，从该位置截取到结尾；否则返回空字符串
        if first_hash_index != -1:
            return s[first_hash_index:]
        else:
            return ""
        
    the_last_tips = []
    for response_text in json_responses:
        try:
            # 解析JSON
            data = json.loads(response_text)
            
            # 提取aweme_list
            aweme_list = data.get('aweme_list', [])
            
            for aweme in aweme_list:
                # 获取caption字段
                caption = aweme.get('caption', '')
                if caption and isinstance(caption, str) and caption.strip():
                    all_captions.append(caption.strip())
                    print(f"提取到caption: {caption}")
            
            # 对captions进行处理
            for caption in all_captions:            
                tips = cut_from_first_hash(caption).split('#')
                for tip in tips:
                    if tip:
                        the_last_tips.append(tip.strip())
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            continue
        except Exception as e:
            print(f"提取caption时出错: {e}")
            continue
    
    print(f"总共提取到 {len(the_last_tips)} 个视频标签")
    return the_last_tips


if __name__ == '__main__':
    # 测试代码
    aaa = []
    for i in range(1,4):
        with open(f'./functions/{i}.json', 'r', encoding='utf-8') as f:
            test_json = f.read()
        aaa.append(test_json)
    captions = extract_captions_from_json_responses(aaa)
    print(f"测试结果: {captions}")