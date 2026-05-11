import random
import time
import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

# 配置基础日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RequestManager:
    def __init__(self):
        self.ua = UserAgent()
        # 免费代理IP池（此处预留接口，实际使用时填入购买或抓取的免费代理）
        self.proxies_list = [
            # "http://ip:port",
        ]

    def get_random_header(self):
        """生成随机的请求头"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://movie.douban.com/'
        }

    def get_random_proxy(self):
        """随机获取一个代理IP"""
        if not self.proxies_list:
            return None
        proxy = random.choice(self.proxies_list)
        return {"http": proxy, "https": proxy}

    def create_session(self):
        """创建带有自动重试机制的 requests Session"""
        session = requests.Session()
        # 遇到 403 (禁止访问), 429 (请求过多), 5xx (服务器错误) 时自动重试 3 次
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[403, 429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def random_sleep():
        """智能延时，模拟人类操作 (1-4秒)"""
        delay = random.uniform(1.0, 4.0)
        logging.info(f"休眠等待 {delay:.2f} 秒...")
        time.sleep(delay)