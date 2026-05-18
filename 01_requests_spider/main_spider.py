import csv
import os
from bs4 import BeautifulSoup
import logging
from proxies import RequestManager
from selenium_handler import SeleniumScraper
from download_images import ImageDownloader
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

####
# def parse_list_page(html):
#     """解析列表页，提取基础信息和详情页链接"""
#     soup = BeautifulSoup(html, 'lxml')
#     movies = soup.select('.grid_view li')
#     parsed_data = []
#     image_tasks = []

#     for item in movies:
#         rank = item.select_one('.pic em').text
#         detail_url = item.select_one('.info .hd a')['href']
#         titles = [span.text for span in item.select('.info .hd span')]
#         title_cn = titles[0]
#         title_other = titles[1].replace('/', '').strip() if len(titles) > 1 else ""
        
#         poster_url = item.select_one('.pic img')['src']
        
#         rating = item.select_one('.rating_num').text
#         rating_count = item.select_one('.star span:nth-child(4)').text.replace('人评价', '')
        
#         # 简单提取信息留作备用，详细信息进详情页抓
#         quote = item.select_one('.inq').text if item.select_one('.inq') else ""

#         parsed_data.append({
#             '排名': rank,
#             '中文标题': title_cn,
#             '外文标题': title_other,
#             '评分': rating,
#             '评价人数': rating_count,
#             '简介': quote,
#             '详情链接': detail_url
#         })
#         # 收集图片下载任务
#         image_tasks.append((poster_url, f"{rank}_{title_cn}"))

#     return parsed_data, image_tasks
def parse_list_page(html):
    """解析列表页，提取基础信息和详情页链接"""
    soup = BeautifulSoup(html, 'lxml')
    movies = soup.select('.grid_view li')
    parsed_data = []
    image_tasks = []

    for item in movies:
        try:
            # 提取排名
            rank_tag = item.select_one('.pic em')
            rank = rank_tag.text if rank_tag else "未知"
            
            # 提取详情链接
            detail_tag = item.select_one('.info .hd a')
            detail_url = detail_tag['href'] if detail_tag else ""
            
            # 提取标题
            titles = [span.text for span in item.select('.info .hd span')]
            title_cn = titles[0] if len(titles) > 0 else "未知标题"
            title_other = titles[1].replace('/', '').strip() if len(titles) > 1 else ""
            
            # 提取海报链接
            poster_tag = item.select_one('.pic img')
            poster_url = poster_tag['src'] if poster_tag else ""
            
            # 提取评分
            rating_tag = item.select_one('.rating_num')
            rating = rating_tag.text if rating_tag else "无"
            
            # # 提取评价人数
            # star_spans = item.select('.star span')
            # rating_count = star_spans[-1].text.replace('人评价', '') if star_spans else "0"

            # 提取评价人数
            match = re.search(r'(\d+)人评价', item.text)
            rating_count = match.group(1) if match else "0"
            
            # 提取简介
            quote_tag = item.select_one('.inq')
            quote = quote_tag.text if quote_tag else ""

            # 提取 导演/主演 
            bd_p = item.select_one('.info .bd p')
            cast_info = bd_p.text.strip().split('\n')[0].strip() if bd_p else "未知"

            parsed_data.append({
                '排名': rank,
                '中文标题': title_cn,
                '外文标题': title_other,
                '导演/主演': cast_info,
                '评分': rating,
                '评价人数': rating_count,
                '简介': quote,
                '详情链接': detail_url
            })
            
            # 收集图片下载任务
            if poster_url:
                image_tasks.append((poster_url, f"{rank}_{title_cn}"))
                
        except Exception as e:
            logging.error(f"解析单部电影时出错: {e}")
            continue 

    return parsed_data, image_tasks

# def parse_detail_page(html):
#     """解析详情页的额外维度数据"""
#     soup = BeautifulSoup(html, 'lxml')
    
#     # 获取上映年份
#     year_tag = soup.select_one('.year')
#     year = year_tag.text.strip('()') if year_tag else ""
    
#     # 获取类型
#     genres = [span.text for span in soup.select('span[property="v:genre"]')]
#     genre_str = "/".join(genres)
    
#     # 获取片长
#     runtime_tag = soup.select_one('span[property="v:runtime"]')
#     runtime = runtime_tag.text if runtime_tag else ""
    
#     # 获取 IMDb IMDb 号
#     imdb_str = ""
#     for pl in soup.select('#info .pl'):
#         if 'IMDb' in pl.text:
#             imdb_str = pl.next_sibling.strip()
#             break

#     return {
#         '上映年份': year,
#         '电影类型': genre_str,
#         '片长': runtime,
#         'IMDb编号': imdb_str
#     }

def main():
    req_manager = RequestManager()
    session = req_manager.create_session()
    selenium_scraper = SeleniumScraper()
    image_downloader = ImageDownloader(save_dir="../output/images")

    if not os.path.exists('../output/raw_data'):
        os.makedirs('../output/raw_data')
    
    # 准备 CSV 存储
    csv_file = open('../output/raw_data/douban_movies.csv', mode='w', encoding='utf-8-sig', newline='')
    fieldnames = ['排名', '中文标题', '外文标题', '导演/主演', '评分', '评价人数', '简介', '详情链接', '年份', '片长', '类型', 'IMDb', '热门短评']
    
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # 循环 10 页
    for page in range(0, 250, 25):
    # 测试模式
    # for page in range(0, 25, 25):
        url = f'https://movie.douban.com/top250?start={page}&filter='
        logging.info(f"正在抓取列表页: {url}")
        
        # 1. 抓取列表页
        headers = req_manager.get_random_header()
        # proxy = req_manager.get_random_proxy()  # <--- 获取代理
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            movies_base_info, image_tasks = parse_list_page(response.text)
            
            # 异步下载本页海报
            image_downloader.download_batch(image_tasks)

            # 2. 遍历进入详情页
            for movie in movies_base_info:
                req_manager.random_sleep() 
                detail_url = movie['详情链接']
                logging.info(f"正在深入抓取详情页: {movie['中文标题']}")
           
                
                # 直接调用 Selenium 新方法，一次性拿到详情和 15 条评论
                movie_details, comments_data = selenium_scraper.get_details_and_comments(detail_url)
                
                # 把年份、片长、类型、IMDb 合并进基础信息字典里
                movie.update(movie_details)
                
                # 将 15 条评论拼接成一个清晰的字符串
                comments_str = " | ".join([f"{c['评论者']}({c['评分']}星): {c['内容']}" for c in comments_data])
                movie['热门短评'] = comments_str 
                
                # 写入完整数据
                writer.writerow(movie)
                
        except Exception as e:
            logging.error(f"页面抓取发生严重错误: {e}")
            
        req_manager.random_sleep() 

    # 清理资源
    csv_file.close()
    selenium_scraper.close()
    logging.info("豆瓣 Top250 全维度爬取完毕！")

if __name__ == '__main__':
    main()