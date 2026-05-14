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
        # 免费代理IP池
        self.proxies_list = [
            # "http://ip:port",
            # "http://127.0.0.1:7897",
        ]

    def get_random_header(self):
        """生成随机的请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://movie.douban.com/',
            'Cookie': 'bid=U6zXd3HTiJ4; dbcl2="295061929:OetKeB69RtE"; ck=IQw2; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1778597801%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_id.100001.4cf6=1c6d904bc6ef38fd.1778597801.; _pk_ses.100001.4cf6=1; __utma=30149280.473880293.1778597801.1778597801.1778597801.1; __utmc=30149280; __utmz=30149280.1778597801.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.1128929454.1778597801.1778597801.1778597801.1; __utmb=223695111.0.10.1778597801; __utmc=223695111; __utmz=223695111.1778597801.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0; __utmb=30149280.2.10.1778597801; __yadk_uid=olm3u1a77xeRIO1VbWOhM9xMF25RENnw'
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
        # 遇到 403 (禁止访问), 429 (请求过多), 5xx  时自动重试 3 次
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