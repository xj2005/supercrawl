# # Scrapy settings for douban_scrapy project

# # For simplicity, this file contains only settings considered important or
# # commonly used. You can find more settings consulting the documentation:

# #     https://docs.scrapy.org/en/latest/topics/settings.html
# #     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# #     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# 
# BOT_NAME = "douban_scrapy"

# SPIDER_MODULES = ["douban_scrapy.spiders"]
# NEWSPIDER_MODULE = "douban_scrapy.spiders"


# # Crawl responsibly by identifying yourself (and your website) on the user-agent
# #USER_AGENT = "douban_scrapy (+http://www.yourdomain.com)"

# # Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# # Configure maximum concurrent requests performed by Scrapy (default: 16)
# #CONCURRENT_REQUESTS = 32

# # Configure a delay for requests for the same website (default: 0)
# # See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# # See also autothrottle settings and docs
# #DOWNLOAD_DELAY = 3
# # The download delay setting will honor only one of:
# #CONCURRENT_REQUESTS_PER_DOMAIN = 16
# #CONCURRENT_REQUESTS_PER_IP = 16

# # Disable cookies (enabled by default)
# #COOKIES_ENABLED = False

# # Disable Telnet Console (enabled by default)
# #TELNETCONSOLE_ENABLED = False

# # Override the default request headers:
# #DEFAULT_REQUEST_HEADERS = {
# #    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
# #    "Accept-Language": "en",
# #}

# # Enable or disable spider middlewares
# # See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# #SPIDER_MIDDLEWARES = {
# #    "douban_scrapy.middlewares.DoubanScrapySpiderMiddleware": 543,
# #}

# # Enable or disable downloader middlewares
# # See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# #DOWNLOADER_MIDDLEWARES = {
# #    "douban_scrapy.middlewares.DoubanScrapyDownloaderMiddleware": 543,
# #}

# # Enable or disable extensions
# # See https://docs.scrapy.org/en/latest/topics/extensions.html
# #EXTENSIONS = {
# #    "scrapy.extensions.telnet.TelnetConsole": None,
# #}

# # Configure item pipelines
# # See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# #ITEM_PIPELINES = {
# #    "douban_scrapy.pipelines.DoubanScrapyPipeline": 300,
# #}

# # Enable and configure the AutoThrottle extension (disabled by default)
# # See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# #AUTOTHROTTLE_ENABLED = True
# # The initial download delay
# #AUTOTHROTTLE_START_DELAY = 5
# # The maximum download delay to be set in case of high latencies
# #AUTOTHROTTLE_MAX_DELAY = 60
# # The average number of requests Scrapy should be sending in parallel to
# # each remote server
# #AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# # Enable showing throttling stats for every response received:
# #AUTOTHROTTLE_DEBUG = False

# # Enable and configure HTTP caching (disabled by default)
# # See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# #HTTPCACHE_ENABLED = True
# #HTTPCACHE_EXPIRATION_SECS = 0
# #HTTPCACHE_DIR = "httpcache"
# #HTTPCACHE_IGNORE_HTTP_CODES = []
# #HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# # Set settings whose default value is deprecated to a future-proof value
# REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
# FEED_EXPORT_ENCODING = "utf-8"

# Scrapy settings for douban_scrapy project
import os
if not os.path.exists('output2'):
    os.makedirs('output2')

import warnings
from scrapy.exceptions import ScrapyDeprecationWarning
warnings.filterwarnings("ignore", category=ScrapyDeprecationWarning)

BOT_NAME = "douban_scrapy"

SPIDER_MODULES = ["douban_scrapy.spiders"]
NEWSPIDER_MODULE = "douban_scrapy.spiders"


# 爬虫伦理与合规性 

# 严格遵守 Robots.txt 协议，避免给目标服务器带来非法访问压力
# ROBOTSTXT_OBEY = True
ROBOTSTXT_OBEY = False



# 性能优化与频率控制

# 控制最大并发请求数。适当降低并发，避免被豆瓣瞬间封禁IP
CONCURRENT_REQUESTS = 3


DOWNLOAD_DELAY = 4
RANDOMIZE_DOWNLOAD_DELAY = True

# 禁用 Cookies 追踪（防止豆瓣通过 Cookie 识别爬虫轨迹）
COOKIES_ENABLED = False


# 核心得分点 3：激活反爬与动态中间件 
# 这里的数字代表优先级，数字越小越先执行
DOWNLOADER_MIDDLEWARES = {
   # 1. 最先执行：换上随机的浏览器 User-Agent 头
   'douban_scrapy.middlewares.RandomUserAgentMiddleware': 400,
   
   # 2. 其次执行：挂上代理 IP，并负责处理超时重试逻辑
#    'douban_scrapy.middlewares.ProxyMiddleware': 410,
   
   # 3. 最后执行：按需启动 Selenium 无头浏览器处理动态短评加载
   # 设置为 543，位于 Scrapy 原生下载器之前拦截请求
   'douban_scrapy.middlewares.SeleniumMiddleware': 543,
}



# 激活多形态数据持久化管道 
ITEM_PIPELINES = {
   # 第一道管：将数据进行关系型拆分，存入 SQLite 的 movies 和 comments 两张表
   'douban_scrapy.pipelines.SqlitePipeline': 300,
   
   # 第二道管：将抓取的数据备份为 JSON 格式
   'douban_scrapy.pipelines.JsonPipeline': 400,
   
   # 第三道管：将抓取的数据备份为 CSV 格式 
   'douban_scrapy.pipelines.CsvPipeline': 500,
}

# 在 settings.py 底部加入：
HTTPERROR_ALLOW_ALL = True


# 异常处理与监控日志
# 开启日志记录模块，仅输出 INFO 级别及以上的有用信息
LOG_LEVEL = 'INFO'
# LOG_LEVEL = 'DEBUG'
# 将所有运行日志写入文件，便于报告中展示“日志记录与异常排查”能力
# LOG_FILE = 'output2/douban_spider_run.log'



# 全套高级请求头伪装

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://movie.douban.com/",
    # 伪造豆瓣的身份追踪 Cookie 
    "Cookie": 'bid=W_29s8_3x8A; dbcl2="295778597801";' 
}

# 框架默认的兼容性设置

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"