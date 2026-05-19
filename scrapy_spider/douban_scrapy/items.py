# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# import scrapy


# class DoubanScrapyItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
    
#     pass

import scrapy

class MovieItem(scrapy.Item):
    # 电影主表字段
    movie_id = scrapy.Field()      # 豆瓣主键ID，用于外键关联
    rank = scrapy.Field()          # 排名
    title = scrapy.Field()         # 标题（中英）
    rating = scrapy.Field()        # 评分
    rating_count = scrapy.Field()  # 评价人数
    director_actors = scrapy.Field() # 导演/主演
    summary = scrapy.Field()       # 简介
    detail_url = scrapy.Field()    # 详情链接
    # 进阶详情字段
    year = scrapy.Field()          # 上映年份
    duration = scrapy.Field()      # 片长
    genres = scrapy.Field()        # 类型
    imdb_rating = scrapy.Field()   # IMDb评分

class CommentItem(scrapy.Item):
    # 短评从表字段
    movie_id = scrapy.Field()      # 外键，关联 MovieItem
    reviewer = scrapy.Field()      # 评论者
    rating = scrapy.Field()        # 评分
    content = scrapy.Field()       # 内容
    time = scrapy.Field()          # 时间
