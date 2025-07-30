# Tag Sniffer - 标签分析与词云生成工具

## 📖 项目简介

Tag Sniffer 是一个基于 Python 的多平台标签分析与词云生成工具，能够自动收集各种平台的推荐内容数据，提取标签信息，并生成可视化的词云图片。通过分析用户的内容消费习惯，帮助用户了解自己的兴趣偏好和内容趋势。

目前支持的平台：
- 🎬 **Bilibili** - 推荐视频标签分析
- 🔄 **更多平台** - 持续开发中...

## ✨ 主要功能

- 🌐 **多平台支持**：支持多个内容平台的数据收集和分析
- 🤖 **自动化浏览器控制**：使用 Playwright 自动控制浏览器访问目标平台
- 📡 **智能网络监听**：实时监听并捕获平台 API 的响应数据
- 🏷️ **标签提取分析**：从推荐内容中提取标签和关键词信息
- 🔤 **中文文本处理**：使用 jieba 进行中文分词和文本预处理
- ☁️ **词云可视化**：生成美观的词云图片，直观展示兴趣偏好
- 🔧 **多浏览器支持**：支持 Chrome、Edge、Firefox 等主流浏览器
- 💾 **登录状态保持**：保持浏览器登录状态，确保个性化推荐
- 📊 **数据分析**：提供详细的标签统计和趋势分析

## 🛠️ 技术栈

- **Python 3.12.3** - 核心开发语言
- **Playwright** - 浏览器自动化
- **jieba** - 中文分词
- **WordCloud** - 词云生成
- **matplotlib** - 图像处理
- **BeautifulSoup4** - HTML 解析
- **requests** - HTTP 请求
- **tqdm** - 进度条显示

## 📦 安装依赖

### 1. 克隆项目
```bash
git clone https://github.com/Because66666/tag_sniffer.git
cd tag_analyse
```

### 2. 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. 安装 Python 依赖

#### 方法一：使用 requirements.txt（推荐）
```bash
pip install -r requirements.txt
```

#### 方法二：手动安装
```bash
pip install playwright wordcloud jieba matplotlib beautifulsoup4 requests tqdm python-dotenv
```

### 4. 安装 Playwright 浏览器
```bash
playwright install
```

### 依赖包说明

| 包名 | 版本 | 用途 |
|------|------|------|
| playwright | 1.50.0 | 浏览器自动化控制 |
| wordcloud | 1.9.4 | 词云图片生成 |
| jieba | 0.42.1 | 中文分词处理 |
| matplotlib | 3.8.4 | 图像绘制和保存 |
| beautifulsoup4 | 4.12.3 | HTML 解析 |
| requests | 2.31.0 | HTTP 请求处理 |
| tqdm | 4.66.4 | 进度条显示 |
| python-dotenv | 1.0.1 | 环境变量管理 |

## ⚙️ 配置说明

### 环境变量配置

在项目根目录创建或编辑 `.env` 文件：

```env
# 支持的浏览器类型: chromium, chrome, edge, firefox
BROWSER_TYPE=edge

# 目标网页地址
TARGET_URL=https://www.bilibili.com
```

### 字体文件

项目需要中文字体文件来正确显示词云中的中文字符：
- 字体文件位置：`fonts/zh-cn.ttf`
- 如果字体文件不存在，词云将使用默认字体（可能无法正确显示中文）

## 🚀 使用方法

### 基本使用（以 Bilibili 为例）

1. **配置环境变量**：
   ```bash
   # 编辑 .env 文件，设置浏览器类型和目标URL
   BROWSER_TYPE=edge
   TARGET_URL=https://www.bilibili.com
   ```

2. **运行主程序**：
   ```bash
   python main.py
   ```

3. **程序执行流程**：
   - 自动启动指定浏览器
   - 访问目标平台网站
   - 开始监听网络请求
   - 自动滚动页面收集推荐数据
   - 提取标签信息
   - 生成词云图片

### 高级功能

#### 单独测试词云生成
```bash
python make_cloudword.py
```

#### 自定义配置
- 修改 `functions/bili.py` 中的 `max_captures` 参数调整收集的数据量
- 修改 `make_cloudword.py` 中的词云配置参数调整生成效果

## 📁 项目结构

```
tag_analyse/
├── .env                    # 环境变量配置文件
├── .gitignore             # Git 忽略文件配置
├── README.md              # 项目说明文档
├── requirements.txt       # Python 依赖包列表
├── main.py                # 主程序入口
├── make_cloudword.py      # 词云生成模块
├── close_edge.py          # Edge 浏览器进程管理
├── functions/             # 功能模块目录
│   └── bili.py           # Bilibili 数据收集和处理模块
├── fonts/                 # 字体文件目录
│   └── zh-cn.ttf         # 中文字体文件
└── picture/              # 生成的词云图片存储目录
    └── *.png             # 词云图片文件
```

## 🔧 核心模块说明

### main.py
- 程序主入口
- 浏览器启动和配置管理
- 整体流程控制和平台适配

### functions/bili.py
- `BilibiliNetworkCapture` 类：Bilibili 平台的网络请求监听和数据收集
- `extract_text_from_json_responses()` 函数：从 JSON 响应中提取文本内容
- `preprocess_text()` 函数：中文文本预处理和分词

### make_cloudword.py
- `generate_wordcloud()` 函数：词云图片生成
- `create_picture_directory()` 函数：输出目录管理
- `get_font_path()` 函数：字体文件路径获取

### 扩展性设计
- 模块化架构便于添加新平台支持
- 统一的数据处理接口
- 可配置的参数和设置

## 🎯 使用场景

1. **个人兴趣分析**：了解自己在各个平台上的兴趣偏好和内容消费习惯
2. **内容创作参考**：分析热门标签和趋势，为内容创作提供数据支持
3. **用户行为研究**：研究推荐算法和用户行为模式
4. **数据可视化**：将文本数据转换为直观的视觉表现
5. **趋势分析**：跟踪不同平台的内容趋势和热点变化
6. **竞品分析**：分析不同平台的内容特点和用户偏好

## ⚠️ 注意事项

1. **登录状态**：建议在运行前先手动登录目标平台账号，以获得个性化推荐
2. **网络稳定性**：确保网络连接稳定，避免数据收集中断
3. **浏览器冲突**：如果目标浏览器正在运行，程序会自动尝试关闭并重启
4. **数据收集时间**：完整的数据收集过程可能需要几分钟时间
5. **合规使用**：请遵守各平台的使用条款，合理使用本工具
6. **Python版本**：建议使用 Python 3.12.3 或更高版本以确保最佳兼容性

## 🐛 常见问题

### Q: 浏览器启动失败
A: 检查是否已安装 Playwright 浏览器：`playwright install`

### Q: 词云显示乱码
A: 确保 `fonts/zh-cn.ttf` 字体文件存在且可读

### Q: 无法收集到数据
A: 检查网络连接和目标平台网站访问状态，确保已登录账号

### Q: Edge 浏览器冲突
A: 程序会自动处理，或手动关闭所有 Edge 进程后重试

### Q: Python 版本兼容性问题
A: 建议使用 Python 3.12.3，如遇到兼容性问题请升级 Python 版本

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和平台使用条款。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📞 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

---

**免责声明**：本工具仅用于学习和研究目的，使用者需自行承担使用风险，并遵守相关平台的使用条款。