from playwright.sync_api import (sync_playwright)
import os
import subprocess
import time
from dotenv import load_dotenv
from functions.bili import BilibiliNetworkCapture, extract_text_from_json_responses, preprocess_text
from make_cloudword import generate_wordcloud

# 加载环境变量
load_dotenv()


def close_edge_processes():
    """关闭所有Edge浏览器进程以释放用户数据目录"""
    try:
        print("正在关闭Edge浏览器进程...")
        
        # 关闭Edge主进程
        result = subprocess.run(['taskkill', '/F', '/IM', 'msedge.exe'], 
                              capture_output=True, text=True)
        
        # 等待进程完全关闭
        time.sleep(3)
        
        # 检查是否还有Edge进程在运行
        check_result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq msedge.exe'], 
                                     capture_output=True, text=True)
        
        if 'msedge.exe' not in check_result.stdout:
            print("✅ Edge浏览器进程已成功关闭")
            return True
        else:
            print("⚠️ 仍有Edge进程在运行")
            return False
            
    except Exception as e:
        print(f"❌ 关闭Edge进程时出错: {e}")
        return False


def get_user_browser_path(browser_type):
    """获取不同操作系统上的用户浏览器数据目录"""
    if os.name == 'nt':  # Windows
        if browser_type in ['chromium', 'chrome']:
            return os.path.join(os.environ['USERPROFILE'],
                                'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        elif browser_type == 'edge':
            return os.path.join(os.environ['USERPROFILE'],
                                'AppData', 'Local', 'Microsoft', 'Edge', 'User Data')
        elif browser_type == 'firefox':
            return os.path.join(os.environ['USERPROFILE'],
                                'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
    elif os.name == 'posix':  # macOS/Linux
        if browser_type in ['chromium', 'chrome']:
            if 'darwin' in os.sys.platform:  # macOS
                return os.path.join(os.environ['HOME'],
                                    'Library', 'Application Support', 'Google', 'Chrome')
            else:  # Linux
                return os.path.join(os.environ['HOME'],
                                    '.config', 'google-chrome')
        elif browser_type == 'edge':
            if 'darwin' in os.sys.platform:  # macOS
                return os.path.join(os.environ['HOME'],
                                    'Library', 'Application Support', 'Microsoft Edge')
            else:  # Linux
                return os.path.join(os.environ['HOME'],
                                    '.config', 'microsoft-edge')
        elif browser_type == 'firefox':
            if 'darwin' in os.sys.platform:  # macOS
                return os.path.join(os.environ['HOME'],
                                    'Library', 'Application Support', 'Firefox', 'Profiles')
            else:  # Linux
                return os.path.join(os.environ['HOME'],
                                    '.mozilla', 'firefox')
    return None


def main():
    # 从环境变量获取浏览器类型和目标网页地址
    browser_type = os.getenv('BROWSER_TYPE', 'chromium').lower()
    target_url = os.getenv('TARGET_URL', 'https://www.baidu.com')
    supported_browsers = ['chromium', 'chrome', 'edge', 'firefox']

    # 验证浏览器类型是否支持
    if browser_type not in supported_browsers:
        print(f"不支持的浏览器类型: {browser_type}")
        print(f"支持的浏览器类型: {', '.join(supported_browsers)}")
        return

    # 获取用户浏览器数据目录
    user_data_dir = get_user_browser_path(browser_type)
    if not user_data_dir or not os.path.exists(user_data_dir):
        print(f"无法找到{browser_type}浏览器的用户数据目录: {user_data_dir}")
        return

    print(f"使用用户浏览器数据目录: {user_data_dir}")
    print(f"目标网页地址: {target_url}")

    # 启动Playwright
    with sync_playwright() as p:
        browser = None
        try:
            # 设置浏览器启动参数
            launch_options = {
                'headless': False,
                'args': [
                    '--no-first-run',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            }

            # 对于Edge浏览器，使用chromium引擎并指定edge通道
            if browser_type == 'edge':
                # 首先尝试使用真实的用户数据目录以保持登录状态
                print(f"尝试使用真实用户数据目录: {user_data_dir}")
                try:
                    browser = p.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        channel='msedge',
                        **launch_options
                    )
                    print("✅ 成功使用真实用户数据目录，应该保持登录状态")
                except Exception as e:
                    print(f"⚠️ 使用真实用户数据目录失败: {e}")
                    print("可能原因：Edge浏览器正在运行")
                    
                    # 询问用户是否要自动关闭Edge进程
                    print("\n选择处理方式：")
                    print("1. 自动关闭Edge进程并重试（推荐，保持登录状态）")
                    print("2. 使用临时目录继续（会丢失登录状态）")
                    print("3. 退出程序")
                    
                    # 自动选择选项1（关闭Edge进程）
                    choice = '1'
                    print(f"自动选择选项 {choice}: 关闭Edge进程并重试")
                    
                    if choice == '1':
                        # 自动关闭Edge进程
                        if close_edge_processes():
                            print("重新尝试使用真实用户数据目录...")
                            try:
                                browser = p.chromium.launch_persistent_context(
                                    user_data_dir=user_data_dir,
                                    channel='msedge',
                                    **launch_options
                                )
                                print("✅ 成功使用真实用户数据目录，应该保持登录状态")
                            except Exception as e2:
                                print(f"❌ 重试后仍然失败: {e2}")
                                print("回退到使用临时目录...")
                                import tempfile
                                temp_user_data = tempfile.mkdtemp(prefix='edge_temp_')
                                browser = p.chromium.launch_persistent_context(
                                    user_data_dir=temp_user_data,
                                    channel='msedge',
                                    **launch_options
                                )
                        else:
                            print("❌ 无法关闭Edge进程，使用临时目录...")
                            import tempfile
                            temp_user_data = tempfile.mkdtemp(prefix='edge_temp_')
                            browser = p.chromium.launch_persistent_context(
                                user_data_dir=temp_user_data,
                                channel='msedge',
                                **launch_options
                            )
                    elif choice == '2':
                        # 使用临时目录
                        import tempfile
                        temp_user_data = tempfile.mkdtemp(prefix='edge_temp_')
                        print(f"⚠️ 使用临时用户数据目录: {temp_user_data}")
                        print("⚠️ 注意：使用临时目录会丢失所有登录状态和Cookie")
                        
                        browser = p.chromium.launch_persistent_context(
                            user_data_dir=temp_user_data,
                            channel='msedge',
                            **launch_options
                        )
                    else:
                        print("退出程序...")
                        return
            elif browser_type == 'firefox':
                # Firefox使用不同的启动方式
                browser = p.firefox.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    **launch_options
                )
            else:
                # Chrome/Chromium
                browser = getattr(p, browser_type).launch_persistent_context(
                    user_data_dir=user_data_dir,
                    **launch_options
                )

            # 创建新页面
            page = browser.new_page()

            # 访问网站
            page.goto(target_url)
            print(f"当前页面标题: {page.title()}")

            # 检查是否是Bilibili网站，如果是则进行网络监听和数据收集
            if 'bilibili.com' in target_url:
                print("\n🎯 检测到Bilibili网站，开始进行网络监听和数据收集...")
                
                # 创建网络捕获器
                network_capture = BilibiliNetworkCapture(page)
                
                print("📡 开始监听网络请求并收集推荐视频数据...")
                print("请在浏览器中滚动页面，程序将自动收集推荐视频的API响应")
                print("目标：收集10个包含推荐视频信息的网络响应")
                
                # 开始捕获网络请求
                captured_responses = network_capture.start_capture()
                
                if captured_responses:
                    print(f"\n✅ 数据收集完成！共收集到 {len(captured_responses)} 个API响应")
                    
                    # 从JSON响应中提取文本
                    print("\n📝 正在从JSON响应中提取文本标签...")
                    text_content = extract_text_from_json_responses(captured_responses)
                    
                    if text_content.strip():
                        # 预处理文本
                        print("🔧 正在预处理文本...")
                        processed_text = preprocess_text(text_content)
                        
                        if processed_text.strip():
                            # 生成词云
                            print("\n🎨 开始生成词云图片...")
                            wordcloud_path = generate_wordcloud(processed_text)
                            
                            if wordcloud_path:
                                print(f"🎉 词云生成成功！")
                                print(f"📁 图片保存位置: {wordcloud_path}")
                                
                                # 询问用户是否要打开图片
                                try:
                                    choice = input("\n是否要打开生成的词云图片？(y/n): ").strip().lower()
                                    if choice in ['y', 'yes', '是']:
                                        os.startfile(wordcloud_path)  # Windows系统打开文件
                                except:
                                    pass
                            else:
                                print("❌ 词云生成失败")
                        else:
                            print("❌ 文本预处理后没有有效内容")
                    else:
                        print("❌ 没有从JSON响应中提取到有效文本")
                else:
                    print("❌ 没有收集到有效的网络响应数据")
                    print("💡 建议：")
                    print("   1. 确保页面已完全加载")
                    print("   2. 尝试手动滚动页面")
                    print("   3. 检查网络连接")
            

        except Exception as e:
            print(f"启动浏览器时出错: {e}")
            print("尝试使用备用方案...")
            
            # 备用方案：使用普通的launch方式而不是persistent_context
            try:
                if browser_type == 'edge':
                    browser_instance = p.chromium.launch(
                        headless=False,
                        channel='msedge',
                        args=launch_options['args']
                    )
                elif browser_type == 'firefox':
                    browser_instance = p.firefox.launch(
                        headless=False,
                        args=launch_options['args']
                    )
                else:
                    browser_instance = getattr(p, browser_type).launch(
                        headless=False,
                        args=launch_options['args']
                    )
                
                context = browser_instance.new_context()
                page = context.new_page()
                
                # 访问网站
                page.goto(target_url)
                print(f"当前页面标题: {page.title()}")
                
                
            except Exception as e2:
                print(f"备用方案也失败了: {e2}")
                print("建议:")
                print("1. 确保没有其他Edge浏览器实例正在运行")
                print("2. 尝试以管理员权限运行")
                print("3. 或者在.env文件中将BROWSER_TYPE改为chromium")
        
        finally:
            if browser:
                try:
                    browser.close()
                except:
                    pass


if __name__ == "__main__":
    main()
