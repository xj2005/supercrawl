from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging

class SeleniumScraper:
    def __init__(self):
        chrome_options = Options()
        # 开启无头模式，不弹出实体浏览器窗口
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # 禁用图片加载以提高抓取速度
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 初始化 WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_hot_comments(self, url):
        """访问详情页并提取前 15 条热门短评"""
        comments_data = []
        try:
            self.driver.get(url)
            # 显式等待评论区加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "hot-comments"))
            )
            
            # 使用 BeautifulSoup 解析 Selenium 获取到的完整网页源码
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            comment_items = soup.select('#hot-comments .comment-item')[:15]
            
            for item in comment_items:
                user = item.select_one('.comment-info a').text.strip() if item.select_one('.comment-info a') else ""
                # 获取星级评分 (如 'allstar40' 代表 4 星)
                rating_class = item.select_one('.comment-info span.rating')
                rating = rating_class['class'][0].replace('allstar', '') if rating_class else "未评分"
                content = item.select_one('.short').text.strip() if item.select_one('.short') else ""
                time_str = item.select_one('.comment-time').text.strip() if item.select_one('.comment-time') else ""
                
                comments_data.append({
                    "评论者": user,
                    "评分": rating,
                    "内容": content,
                    "时间": time_str
                })
            logging.info(f"成功使用 Selenium 抓取到 {len(comments_data)} 条动态评论")
            
        except Exception as e:
            logging.error(f"Selenium 抓取短评失败: {e}")
            
        return comments_data

    def close(self):
        """关闭浏览器进程"""
        self.driver.quit()