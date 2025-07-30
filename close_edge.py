import subprocess
import time

def close_edge_processes():
    """关闭所有Edge浏览器进程"""
    try:
        print("正在关闭Edge浏览器进程...")
        
        # 关闭Edge主进程
        subprocess.run(['taskkill', '/F', '/IM', 'msedge.exe'], 
                      capture_output=True, text=True)
        
        # 等待进程完全关闭
        time.sleep(2)
        
        # 检查是否还有Edge进程在运行
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq msedge.exe'], 
                               capture_output=True, text=True)
        
        if 'msedge.exe' not in result.stdout:
            print("✅ Edge浏览器进程已成功关闭")
            return True
        else:
            print("⚠️ 仍有Edge进程在运行")
            return False
            
    except Exception as e:
        print(f"❌ 关闭Edge进程时出错: {e}")
        return False

if __name__ == "__main__":
    close_edge_processes()