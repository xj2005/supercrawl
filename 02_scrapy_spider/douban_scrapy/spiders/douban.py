# import scrapy


# class DoubanSpider(scrapy.Spider):
#     name = "douban"
#     allowed_domains = ["movie.douban.com"]
#     start_urls = ["https://movie.douban.com"]

#     def parse(self, response):
#         pass

import scrapy
import re
from douban_scrapy.items import MovieItem, CommentItem

class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']
    # 起始 URL：Top250 第一页
    start_urls = ['https://movie.douban.com/top250']

    # 第一层：解析列表页 
    def parse(self, response):
        self.logger.info(f"正在抓取列表页: {response.url}")
        
        # 获取当前页的所有电影条目
        movies = response.css('.grid_view li')
        
        for item in movies:
            movie = MovieItem()
            
            # 1. 提取基础信息 
            movie['rank'] = item.css('.pic em::text').get()
            
            # 拼接中文和外文标题
            titles = item.css('.info .hd span::text').getall()
            movie['title'] = "".join(titles).replace('\xa0', '').strip()
            
            movie['rating'] = item.css('.rating_num::text').get()
            
            # 正则提取评价人数中的数字
            count_str = item.css('.star span:nth-child(4)::text').get()
            movie['rating_count'] = re.search(r'\d+', count_str).group() if count_str else '0'
            
            # 导演和主演通常在同一段文本中
            bd_p = item.css('.bd p:not([class])::text').getall()
            movie['director_actors'] = bd_p[0].strip() if bd_p else ''
            
            movie['summary'] = item.css('.inq::text').get(default='')
            
            # 获取详情页链接
            detail_url = item.css('.info .hd a::attr(href)').get()
            movie['detail_url'] = detail_url
            
            # 提取豆瓣的影片 ID 作为关系型数据库的主键/外键
            # 链接格式: https://movie.douban.com/subject/1292052/
            movie_id = detail_url.strip('/').split('/')[-1]
            movie['movie_id'] = movie_id

            # 异步请求进入第二层（详情页），通过 meta 将已抓取的基础信息传递过去
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                meta={'movie_item': movie}
            )

        # 智能分页：查找“后页”的链接，如果存在则继续爬取
        next_page = response.css('.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    # 第二层：解析详情页
    def parse_detail(self, response):
        # 接收第一层传过来的不完整 movie 对象
        movie = response.meta['movie_item']
        self.logger.info(f"正在抓取详情页: {movie['title']}")
        
        # 提取进阶信息
        # 年份 
        movie['year'] = response.css('h1 .year::text').re_first(r'\d+')
        # 片长
        movie['duration'] = response.css('span[property="v:runtime"]::text').get(default='')
        # 类型 
        movie['genres'] = " / ".join(response.css('span[property="v:genre"]::text').getall())
        
        # IMDb 提取：定位到 "IMDb:" 文本节点，获取其后面的同级文本
        imdb_text = response.xpath('//span[text()="IMDb:"]/following-sibling::text()[1]').get()
        movie['imdb_rating'] = imdb_text.strip() if imdb_text else ""

        yield movie

        # 构造第三层的 URL 并发起请求
        movie_id = movie['movie_id']
        comments_url = f"https://movie.douban.com/subject/{movie_id}/comments?status=P"
        
        yield scrapy.Request(
            url=comments_url,
            callback=self.parse_comments,
            # 将 movie_id 传过去作为短评表的外键
            meta={'movie_id': movie_id, 'use_selenium': True} 
        )

   
    # 第三层：解析短评页 
    
    def parse_comments(self, response):
        movie_id = response.meta['movie_id']
        self.logger.info(f"正在抓取短评页, Movie ID: {movie_id}")
        
        # 仅截取前 15 条短评
        comments = response.css('.comment-item')[:15]
        
        for item in comments:
            comment = CommentItem()
            
            # 🔑 写入外键，用于数据库两表关联
            comment['movie_id'] = movie_id
            comment['reviewer'] = item.css('.comment-info a::text').get()
            
            # 评分提取：class 属性如 "allstar50 rating"，提取出 "5"
            rating_class = item.css('.comment-info span.rating::attr(class)').get()
            if rating_class:
                match = re.search(r'allstar(\d)0', rating_class)
                comment['rating'] = match.group(1) if match else '未评分'
            else:
                comment['rating'] = '未评分'
                
            comment['content'] = item.css('.short::text').get(default='').strip()
            
            # 优先获取 title 属性里的精确时间，若无则取文本显示时间
            comment['time'] = item.css('.comment-time::attr(title)').get() or \
                              item.css('.comment-time::text').get(default='').strip()
            
            # yield 交给 Pipeline，保存入 MySQL 的评论子表
            yield comment