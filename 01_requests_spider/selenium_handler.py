from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import re

class SeleniumScraper:
    # def __init__(self):
    #     chrome_options = Options()
    #     # 开启无头模式，不弹出实体浏览器窗口
    #     # chrome_options.add_argument("--headless")
    #     chrome_options.add_argument("--disable-gpu")
    #     chrome_options.add_argument("--no-sandbox")

    #     # === 添加固定的电脑 User-Agent ===
    #     chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"')

    #     # ===让 Selenium 走你的本地代理 ===
    #     # chrome_options.add_argument("--proxy-server=http://127.0.0.1:7897")
    #     # 禁用图片加载以提高抓取速度
    #     prefs = {"profile.managed_default_content_settings.images": 2}
    #     chrome_options.add_experimental_option("prefs", prefs)
        
    #     # 初始化 WebDriver
    #     self.driver = webdriver.Chrome(options=chrome_options)

    def __init__(self):
        chrome_options = Options()
        
        # 隐藏 "Chrome 正受到自动测试软件的控制" 提示条
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 抹除底层的自动化特征 
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"')
        
        #不加载图片
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=chrome_options)    

    # def get_hot_comments(self, url):
    #     """访问详情页并提取前 15 条热门短评"""
    #     comments_data = []
    #     try:
    #         self.driver.get(url)
    #         # 显式等待评论区加载完成
    #         WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.ID, "hot-comments"))
    #         )
            
    #         # 使用 BeautifulSoup 解析 Selenium 获取到的完整网页源码
    #         soup = BeautifulSoup(self.driver.page_source, 'lxml')
    #         comment_items = soup.select('#hot-comments .comment-item')[:15]
            
    #         for item in comment_items:
    #             user = item.select_one('.comment-info a').text.strip() if item.select_one('.comment-info a') else ""
    #             # 获取星级评分
    #             rating_class = item.select_one('.comment-info span.rating')
    #             rating = rating_class['class'][0].replace('allstar', '') if rating_class else "未评分"
    #             content = item.select_one('.short').text.strip() if item.select_one('.short') else ""
    #             time_str = item.select_one('.comment-time').text.strip() if item.select_one('.comment-time') else ""
                
    #             comments_data.append({
    #                 "评论者": user,
    #                 "评分": rating,
    #                 "内容": content,
    #                 "时间": time_str
    #             })
    #         logging.info(f"成功使用 Selenium 抓取到 {len(comments_data)} 条动态评论")
            
    #     except Exception as e:
    #         logging.error(f"Selenium 抓取短评失败: {e}")
            
    #     return comments_data
    # def get_hot_comments(self, url):
    #     """访问详情页并提取前 15 条热门短评 (带 Cookie 突破拦截)"""
    #     comments_data = []
        
    #     cookie_str = 'bid=U6zXd3HTiJ4; dbcl2="295061929:OetKeB69RtE"; ck=IQw2; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1778597801%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_id.100001.4cf6=1c6d904bc6ef38fd.1778597801.; _pk_ses.100001.4cf6=1; __utma=30149280.473880293.1778597801.1778597801.1778597801.1; __utmc=30149280; __utmz=30149280.1778597801.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.1128929454.1778597801.1778597801.1778597801.1; __utmb=223695111.0.10.1778597801; __utmc=223695111; __utmz=223695111.1778597801.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0; __utmb=30149280.2.10.1778597801; __yadk_uid=olm3u1a77xeRIO1VbWOhM9xMF25RENnw'

    #     # try:
    #     #     # 必须先访问一次豆瓣域名，才能种下 Cookie
    #     #     self.driver.get("https://movie.douban.com/favicon.ico")
            
    #     #     # 循环添加 Cookie 给浏览器
    #     #     for item in cookie_str.split(';'):
    #     #         if '=' in item:
    #     #             key, value = item.strip().split('=', 1)
    #     #             self.driver.add_cookie({'name': key, 'value': value})
            
    #     #     # 带着合法身份，再次访问真正的详情页
    #     #     self.driver.get(url)
            
    #     #     WebDriverWait(self.driver, 10).until(
    #     #         EC.presence_of_element_located((By.CSS_SELECTOR, ".comment-item"))
    #     #     )
    #     try:
    #         # 必须先访问一次豆瓣域名，为了稳定，我们访问它相对没那么多风控的 robots.txt
    #         self.driver.get("https://movie.douban.com/robots.txt")
            
    #         # 安全地循环添加 Cookie 给浏览器
    #         for item in cookie_str.split(';'):
    #             if '=' in item:
    #                 key, value = item.strip().split('=', 1)
    #                 try:
    #                     self.driver.add_cookie({'name': key, 'value': value})
    #                 except Exception as e:
    #                     pass
            
    #         # 带着合法身份，再次访问真正的详情页
    #         self.driver.get(url)

    #         import time
    #         time.sleep(3)
            
    #         WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR, ".comment-item"))
    #         )
            
    #         # 使用 BeautifulSoup 解析源码
    #         soup = BeautifulSoup(self.driver.page_source, 'lxml')
    #         comment_items = soup.select('#hot-comments .comment-item')[:15]
            
    #         for item in comment_items:
    #             user = item.select_one('.comment-info a').text.strip() if item.select_one('.comment-info a') else ""
    #             rating_class = item.select_one('.comment-info span.rating')
    #             rating = rating_class['class'][0].replace('allstar', '') if rating_class else "未评分"
    #             content = item.select_one('.short').text.strip() if item.select_one('.short') else ""
    #             time_str = item.select_one('.comment-time').text.strip() if item.select_one('.comment-time') else ""
                
    #             comments_data.append({
    #                 "评论者": user,
    #                 "评分": rating,
    #                 "内容": content,
    #                 "时间": time_str
    #             })
    #         logging.info(f"成功使用 Selenium 抓取到 {len(comments_data)} 条动态评论")
            
    #     except Exception as e:
    #         logging.error(f"Selenium 抓取短评失败: {str(e)[:100]}...")
            
    #     return comments_data

    # def get_hot_comments(self, url):
    #     """访问详情页并提取前 15 条热门短评 """
    #     comments_data = []
        
    #     cookie_str = 'bid=U6zXd3HTiJ4; dbcl2="295061929:OetKeB69RtE"; ck=IQw2; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1778597801%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_id.100001.4cf6=1c6d904bc6ef38fd.1778597801.; _pk_ses.100001.4cf6=1; __utma=30149280.473880293.1778597801.1778597801.1778597801.1; __utmc=30149280; __utmz=30149280.1778597801.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.1128929454.1778597801.1778597801.1778597801.1; __utmb=223695111.0.10.1778597801; __utmc=223695111; __utmz=223695111.1778597801.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0; __utmb=30149280.2.10.1778597801; __yadk_uid=olm3u1a77xeRIO1VbWOhM9xMF25RENnw'

    #     try:
    #         # 第一级：直接尝试访问。如果之前已经注入过Cookie或人工登录过，这里会直接成功。
    #         self.driver.get(url)
            
    #         # 检查是否被拦到了登录页
    #         current_url = self.driver.current_url
    #         if "sec.douban" in current_url or "accounts.douban" in current_url:
    #             logging.info("检测到登录拦截，正在尝试自动注入预设 Cookie 破解...")
                
    #             # 第二级：注入 Cookie
    #             self.driver.get("https://movie.douban.com/favicon.ico") # 先访问域名以允许种Cookie
    #             for item in cookie_str.split(';'):
    #                 if '=' in item:
    #                     key, value = item.strip().split('=', 1)
    #                     try:
    #                         self.driver.add_cookie({'name': key, 'value': value})
    #                     except Exception:
    #                         pass 
                
    #             # 注入完成后，再次尝试访问目标网页
    #             self.driver.get(url)
    #             current_url = self.driver.current_url
                
    #             # 第三级：如果注入了 Cookie 还是被拦，说明 Cookie 已经过期！呼叫人工。
    #             if "sec.douban" in current_url or "accounts.douban" in current_url:
    #                 print("\n" + "="*60)
    #                 print("🚨 预设的 Cookie 已失效！请在弹出的浏览器中手动登录！")
    #                 print("⏱️ 程序已暂停，你有 60 秒的时间使用微信/豆瓣APP扫码登录...")
    #                 print("✅ 登录成功跳转后，程序会自动接管并继续抓取，请勿关闭窗口！")
    #                 print("="*60 + "\n")
                    
    #                 # 死等 60 秒直到 URL 变回电影详情页
    #                 WebDriverWait(self.driver, 60).until(
    #                     EC.url_contains("movie.douban.com/subject")
    #                 )
    #                 print("🎉 检测到人工登录成功！开始全自动高速抓取...")
    #             else:
    #                 logging.info("🎉 Cookie 注入成功！成功绕过拦截。")
            
    #         WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR, ".comment-item"))
    #         )
            
    #         # 使用 BeautifulSoup 解析源码
    #         soup = BeautifulSoup(self.driver.page_source, 'lxml')
    #         comment_items = soup.select('#hot-comments .comment-item')[:15]
            
    #         for item in comment_items:
    #             user = item.select_one('.comment-info a').text.strip() if item.select_one('.comment-info a') else ""
    #             rating_class = item.select_one('.comment-info span.rating')
    #             rating = rating_class['class'][0].replace('allstar', '') if rating_class else "未评分"
    #             content = item.select_one('.short').text.strip() if item.select_one('.short') else ""
    #             time_str = item.select_one('.comment-time').text.strip() if item.select_one('.comment-time') else ""
                
    #             comments_data.append({
    #                 "评论者": user,
    #                 "评分": rating,
    #                 "内容": content,
    #                 "时间": time_str
    #             })
    #         logging.info(f"成功使用 Selenium 抓取到 {len(comments_data)} 条动态评论")
            
    #     except Exception as e:
    #         logging.error(f"Selenium 抓取短评失败 (超时或验证未通过): {str(e)[:100]}...")
            
    #     return comments_data

    def get_details_and_comments(self, url):
        """访问详情页提取额外属性，并跳转短评页拿满15条评论 """
        #  准备存放新字段的字典
        movie_details = {"年份": "未知", "片长": "未知", "类型": "未知", "IMDb": "未知"}
        comments_data = []
        
        # 将你的 Cookie 字符串放在这里
        cookie_str = 'bid=U6zXd3HTiJ4; dbcl2="295061929:OetKeB69RtE"; ck=IQw2; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1778597801%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_id.100001.4cf6=1c6d904bc6ef38fd.1778597801.; _pk_ses.100001.4cf6=1; __utma=30149280.473880293.1778597801.1778597801.1778597801.1; __utmc=30149280; __utmz=30149280.1778597801.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.1128929454.1778597801.1778597801.1778597801.1; __utmb=223695111.0.10.1778597801; __utmc=223695111; __utmz=223695111.1778597801.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0; __utmb=30149280.2.10.1778597801; __yadk_uid=olm3u1a77xeRIO1VbWOhM9xMF25RENnw'

        try:
            self.driver.get(url)
            current_url = self.driver.current_url
            if "sec.douban" in current_url or "accounts.douban" in current_url:
                logging.info("检测到登录拦截，正在尝试自动注入预设 Cookie 破解...")
                self.driver.get("https://movie.douban.com/favicon.ico") 
                for item in cookie_str.split(';'):
                    if '=' in item:
                        key, value = item.strip().split('=', 1)
                        try:
                            self.driver.add_cookie({'name': key, 'value': value})
                        except Exception:
                            pass 
                
                self.driver.get(url)
                current_url = self.driver.current_url
                
                if "sec.douban" in current_url or "accounts.douban" in current_url:
                    print("\n" + "="*80)
                    print("🚨 预设的 Cookie 已失效！请在弹出的浏览器中手动登录！")
                    print("⏱️ 程序已暂停，你有 80 秒的时间使用微信/豆瓣APP扫码登录...")
                    print("✅ 登录成功跳转后，程序会自动接管并继续抓取，请勿关闭窗口！")
                    print("="*80 + "\n")
                    
                    WebDriverWait(self.driver, 80).until(
                        EC.url_contains("movie.douban.com/subject")
                    )
                    print("🎉 检测到人工登录成功！开始全自动高速抓取...")
                else:
                    logging.info("🎉 Cookie 注入成功！成功绕过拦截。")
            

            # 阶段 1：此时已经在电影主页了，先抓取详情属性！
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "info")))
            soup_main = BeautifulSoup(self.driver.page_source, 'lxml')
            
            year_tag = soup_main.select_one('.year')
            movie_details['年份'] = year_tag.text.strip('()') if year_tag else "未知"
            
            runtimes = [span.text for span in soup_main.select('span[property="v:runtime"]')]
            movie_details['片长'] = "/".join(runtimes) if runtimes else "未知"
            
            genres = [span.text for span in soup_main.select('span[property="v:genre"]')]
            movie_details['类型'] = "/".join(genres) if genres else "未知"
            
            info_text = soup_main.select_one('#info').text if soup_main.select_one('#info') else ""
            imdb_match = re.search(r'IMDb:\s*(tt\d+)', info_text)
            movie_details['IMDb'] = imdb_match.group(1) if imdb_match else "未知"

            # 阶段 2：跳转到专门的短评页拿满 15 条！

            comments_url = url + "comments?status=P"
            self.driver.get(comments_url)
 
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".comment-item"))
            )
            
            # 使用 BeautifulSoup 解析短评页源码
            soup_comments = BeautifulSoup(self.driver.page_source, 'lxml')
            comment_items = soup_comments.select('.comment-item')[:15] 
            
            for item in comment_items:
                user = item.select_one('.comment-info a').text.strip() if item.select_one('.comment-info a') else ""
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
            logging.info(f"✅ 成功抓取详情，并拿到 {len(comments_data)} 条短评！")
            
        except Exception as e:
            logging.error(f"Selenium 抓取短评失败 (超时或验证未通过): {str(e)[:100]}...")
            
        return movie_details, comments_data

    def close(self):
        """关闭浏览器进程"""
        self.driver.quit()