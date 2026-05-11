import csv
from bs4 import BeautifulSoup
import logging
from proxies import RequestManager
from selenium_handler import SeleniumScraper
from download_images import ImageDownloader

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_list_page(html):
    """解析列表页，提取基础信息和详情页链接"""
    soup = BeautifulSoup(html, 'lxml')
    movies = soup.select('.grid_view li')
    parsed_data = []
    image_tasks = []

    for item in movies:
        rank = item.select_one('.pic em').text
        detail_url = item.select_one('.info .hd a')['href']
        titles = [span.text for span in item.select('.info .hd span')]
        title_cn = titles[0]
        title_other = titles[1].replace('/', '').strip() if len(titles) > 1 else ""
        
        poster_url = item.select_one('.pic img')['src']
        
        rating = item.select_one('.rating_num').text
        rating_count = item.select_one('.star span:nth-child(4)').text.replace('人评价', '')
        
        # 简单提取信息留作备用，详细信息我们进详情页抓
        quote = item.select_one('.inq').text if item.select_one('.inq') else ""

        parsed_data.append({
            '排名': rank,
            '中文标题': title_cn,
            '外文标题': title_other,
            '评分': rating,
            '评价人数': rating_count,
            '简介': quote,
            '详情链接': detail_url
        })
        # 收集图片下载任务
        image_tasks.append((poster_url, f"{rank}_{title_cn}"))

    return parsed_data, image_tasks

def parse_detail_page(html):
    """解析详情页的额外维度数据"""
    soup = BeautifulSoup(html, 'lxml')
    
    # 获取上映年份
    year_tag = soup.select_one('.year')
    year = year_tag.text.strip('()') if year_tag else ""
    
    # 获取类型
    genres = [span.text for span in soup.select('span[property="v:genre"]')]
    genre_str = "/".join(genres)
    
    # 获取片长
    runtime_tag = soup.select_one('span[property="v:runtime"]')
    runtime = runtime_tag.text if runtime_tag else ""
    
    # 获取 IMDb 链接和评分需要进 IMDb 网站，这里按要求提取详情页内的 IMDb 号
    imdb_str = ""
    for pl in soup.select('#info .pl'):
        if 'IMDb' in pl.text:
            imdb_str = pl.next_sibling.strip()
            break

    return {
        '上映年份': year,
        '电影类型': genre_str,
        '片长': runtime,
        'IMDb编号': imdb_str
    }

def main():
    req_manager = RequestManager()
    session = req_manager.create_session()
    selenium_scraper = SeleniumScraper()
    image_downloader = ImageDownloader(save_dir="../output/images")
    
    # 准备 CSV 存储
    csv_file = open('../output/raw_data/douban_movies.csv', mode='w', encoding='utf-8-sig', newline='')
    fieldnames = ['排名', '中文标题', '外文标题', '评分', '评价人数', '简介', '详情链接', 
                  '上映年份', '电影类型', '片长', 'IMDb编号', '热门短评JSON']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # 循环 10 页
    for page in range(0, 250, 25):
        url = f'https://movie.douban.com/top250?start={page}&filter='
        logging.info(f"正在抓取列表页: {url}")
        
        # 1. 抓取列表页
        headers = req_manager.get_random_header()
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            movies_base_info, image_tasks = parse_list_page(response.text)
            
            # 异步下载本页海报
            image_downloader.download_batch(image_tasks)

            # 2. 遍历进入详情页
            for movie in movies_base_info:
                req_manager.random_sleep() # 进详情页前必须休眠
                detail_url = movie['详情链接']
                logging.info(f"正在深入抓取详情页: {movie['中文标题']}")
                
                # 获取详情页静态信息
                detail_headers = req_manager.get_random_header()
                detail_resp = session.get(detail_url, headers=detail_headers, timeout=10)
                detail_info = parse_detail_page(detail_resp.text)
                
                # 获取动态短评 (Selenium)
                req_manager.random_sleep()
                comments = selenium_scraper.get_hot_comments(detail_url)
                
                # 组合数据并写入
                final_data = {**movie, **detail_info}
                # 将评论列表转为字符串存储，方便后续清洗
                final_data['热门短评JSON'] = str(comments) 
                
                writer.writerow(final_data)
                
        except Exception as e:
            logging.error(f"页面抓取发生严重错误: {e}")
            
        req_manager.random_sleep() # 翻页前休眠

    # 清理资源
    csv_file.close()
    selenium_scraper.close()
    logging.info("豆瓣 Top250 全维度爬取完毕！")

if __name__ == '__main__':
    main()