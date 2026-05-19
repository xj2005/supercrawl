# 豆瓣电影全栈数据采集、分析与 RAG 智能问答系统 (SuperCrawl)

## 📑 项目简介

本项目是一个涵盖**数据采集、数据清洗与探索性分析、情感计算以及大语言模型 RAG问答**的全栈式综合工程。系统以豆瓣电影 Top250 及其衍生海量短评为业务支撑点，不仅构建了**双引擎（Requests + Scrapy）反爬虫抓取网络**，还打通了离线数据分析管线，并最终依托本地向量数据库ChromaDB与大语言模型DeepSeek-V3，构筑了具备上下文记忆与流式输出能力的交互式智能影迷问答助手。

---

## ✨ 核心特性与系统架构

### 1. 🕷️ 双引擎分布式网络爬虫
项目内置两套完全独立且功能互补的爬虫架构，以应对不同复杂度的反爬风控：
* **引擎 A：Requests + Selenium 动态渲染爬虫 (`requests_spider`)**
    * **动态突破拦截**：集成 Selenium 无头浏览器，并利用 Cookie 注入与异常重试机制，有效绕过豆瓣登录验证风控，动态抓取前 15 条热门短评与 IMDb 等深层属性。
    * **多线程并发下载**：配备 `ImageDownloader`，通过多线程支持海报图片的断点续传批量下载。
    * **结构化入库**：直接与本地 MySQL 数据库直连持久化，并同步备份一份至 CSV。
* **引擎 B：Scrapy 高并发异步爬虫 (`scrapy_spider`)**
    * **三层深度采集**：利用回调机制穿透 列表页 -> 详情页 -> 评论页，实现精准的三级网页数据提取。
    * **多态持久化管道 (Pipelines)**：单次抓取同时通过三条数据管道落地——SQLite (关系型关联)、JSON (备份)、CSV (通用)。
    * **动态反爬中间件 (Middlewares)**：内置随机 User-Agent 切换、代理 IP 池调度、延迟控制 (`DOWNLOAD_DELAY`)，最大限度降低封禁概率。

### 2. 📊 自动化数据管线与全维度可视化 (`data_analysis`)
* **数据清洗与策略填充**：自动寻址最新的抓取产物进行异常值清理与空值处理。
* **多维度洞察**：支持极高细粒度的分析维度，输出 Top10 榜单、评分/人数散点图、时间趋势图、类型饼图等。
* **短评 NLP 情感计算**：提纯数万条独立观众短评，计算情感极性（积极/中立/消极）分布，并生成电影口碑高频词云。

### 3. 🤖 高阶 RAG 智能对话服务 (`rag_api`)
* **知识库增强检索**：基于本地 ChromaDB 向量数据库，利用 `BAAI/bge-m3` 高效嵌入模型，将电影元数据与短评向量化。
* **流式输出与记忆机制**：基于 FastAPI 提供跨域服务，利用 Server-Sent Events (SSE) 协议实现类似于 ChatGPT 的打字机推流效果，且原生支持历史对话上下文串联。

---

## 📂 核心目录与产物说明

\`\`\`text
supercrawl/
├── requests_spider/     # 【采集】原生 Requests + Selenium 爬虫引擎 (面向 MySQL 与图片下载)
├── scrapy_spider/       # 【采集】Scrapy 异步爬虫框架 (面向 SQLite 与多形态文件备份)
├── data_analysis/       # 【分析】数据清洗、统计、情感分析与可视化核心模块
├── rag_api/             # 【问答】FastAPI RAG 后端服务、ChromaDB 数据及交互入口
├── requirements.txt     # Python 依赖清单
└── README.md            # 项目说明文档
\`\`\`

---

## ⚙️ 环境配置与依赖安装

### 1. 系统依赖
* **Python**: `>= 3.10`
* **数据库**: MySQL 
* **浏览器驱动**: Chrome 浏览器及配套版本 ChromeDriver (用于 Selenium 模块)

### 2. 依赖安装
强烈建议使用虚拟环境以隔离项目依赖：
\`\`\`bash
# 1. 创建并激活虚拟环境
conda create -n {your_env} python=3.10

# 2. 安装全套依赖
pip install -r requirements.txt
\`\`\`

---

## 🚀 系统全流程使用指南

本项目推荐按照 **采集 -> 分析 -> 服务** 的数据流向顺序依次运行。

### 阶段一：运行数据采集引擎 
**选项 A：运行 Requests + Selenium 爬虫 (含图片下载 & MySQL)**
> **注意**: 运行前请打开 `requests_spider/main_spider.py`，修改 `pymysql.connect` 中的本地 MySQL `host`, `user`, `password` 等配置。
\`\`\`bash
cd requests_spider
python main_spider.py
\`\`\`

**选项 B：运行 Scrapy 异步爬虫 (多管线导出)**
\`\`\`bash
cd scrapy_spider
scrapy crawl douban
\`\`\`

### 阶段二：运行数据清洗与可视化分析
自动寻找 `output/raw_data/` 下最新生成的 CSV 文件进行自动化处理。
\`\`\`bash
cd data_analysis
python main.py
\`\`\`

### 阶段三：启动高阶 RAG 智能问答后台
在项目根目录启动 FastAPI 接口服务：
\`\`\`bash
cd rag_api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

### 阶段四：启动 Web UI 交互界面
保持后端服务在运行状态，新开一个终端窗口：
\`\`\`bash
streamlit run rag_api/frontend.py 
\`\`\`

---

## ⚠️ 开发者必读与合规警告

1. **大模型密钥硬编码风险**：
   项目内的 `rag_api/main.py` 目前**硬编码了 API Key** (`sk-lorf...`)。在公开部署或合并至开源仓库前，**务必将其改为读取本地环境变量或 `.env` 配置文件**，以防额度被盗刷。
2. **Selenium Cookie 失效机制**：
   在 `requests_spider/selenium_handler.py` 中预设了长效 Cookie 以绕过豆瓣登录墙。若程序终端提示“🚨 预设的 Cookie 已失效”，请根据日志提示，在弹出的自动化浏览器内具有的 80 秒窗口期内扫码登录，程序将在验证成功后自动接管。
3. **爬虫礼仪与服务器负载保护**：
   * 豆瓣反爬机制极度敏锐。默认已在 `settings.py` 中配置了 `DOWNLOAD_DELAY = 4` 且关闭了 `ROBOTSTXT_OBEY`。
   * 切勿为了追求速度而过度调高 `CONCURRENT_REQUESTS` 兵发请求数，这会导致本地 IP 遭到无差别封禁。请合理使用并及时更新 `proxies.py` 里的代理池。
4. **免责声明 (Disclaimer)**：
   本项目全部代码及抓取产物仅用于学术探讨、大语言模型能力测试及 RAG 架构学习。请勿将本爬虫脚本用于大规模商业化数据窃取。对目标网站造成的一切不良影响需由执行者自行承担。
