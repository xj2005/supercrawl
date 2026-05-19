import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import pandas as pd
import numpy as np
import os

import seaborn as sns
sns.set_style("whitegrid")
sns.set_palette("husl")

# 2. 再设置中文字体，强制覆盖 seaborn 的默认字体设置（Windows）
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

import matplotlib
print(f"✅ matplotlib 版本: {matplotlib.__version__}")
print(f"✅ 当前字体设置: {plt.rcParams['font.sans-serif']}")


def get_wordcloud_font_path():
    """获取词云使用的中文字体路径"""
    # Windows 系统字体路径
    font_paths = [
        'C:/Windows/Fonts/simhei.ttf',   # 黑体
        'C:/Windows/Fonts/msyh.ttc',     # 微软雅黑
        'C:/Windows/Fonts/simsun.ttc',   # 宋体
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"✅ 词云使用字体: {font_path}")
            return font_path
    
    print("⚠️ 未找到中文字体文件，词云可能无法显示中文")
    return None

# ============================================
# 图表函数
# ============================================

def plot_rating_histogram(df, rating_col='rating', output_path='charts/rating_histogram.png'):
    """绘制评分分布直方图"""
    plt.figure(figsize=(12, 6))
    
    ratings = df[rating_col].dropna()
    
    if len(ratings) == 0:
        print("⚠️ 没有有效的评分数据")
        return
    
    n, bins, patches = plt.hist(ratings, bins=20, edgecolor='black', alpha=0.7, 
                                 color='steelblue', rwidth=0.95)
    
    mean_rating = ratings.mean()
    median_rating = ratings.median()
    plt.axvline(mean_rating, color='red', linestyle='--', linewidth=2, 
                label=f'平均分: {mean_rating:.2f}')
    plt.axvline(median_rating, color='green', linestyle='--', linewidth=2, 
                label=f'中位数: {median_rating:.2f}')
    
    plt.xlabel('评分', fontsize=12)
    plt.ylabel('电影数量', fontsize=12)
    plt.title('电影评分分布直方图', fontsize=14)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"直方图已保存至: {output_path}")

def plot_genre_pie_chart(genre_counts, output_path='charts/genre_pie.png', plotly_output='charts/genre_pie.html'):
    """绘制电影类型饼图"""
    top_genres = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:8])
    other_count = sum([v for k, v in genre_counts.items() if k not in top_genres])
    if other_count > 0:
        top_genres['其他'] = other_count
    
    # Plotly 交互式图表（自动支持中文）
    fig = px.pie(
        values=list(top_genres.values()),
        names=list(top_genres.keys()),
        title='电影类型分布占比',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12
    )
    
    fig.update_layout(
        title_x=0.5,
        width=800,
        height=600
    )
    
    fig.write_html(plotly_output)
    fig.show()
    
    # matplotlib 静态图表
    plt.figure(figsize=(10, 10))
    plt.pie(list(top_genres.values()), 
            labels=list(top_genres.keys()),
            autopct='%1.1f%%',
            startangle=90,
            explode=[0.05] * len(top_genres),
            shadow=True)
    plt.title('电影类型分布占比', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"静态饼图已保存至: {output_path}")
    print(f"交互式饼图已保存至: {plotly_output}")

def plot_rating_scatter(df, rating_col='rating', people_col='rating_people', 
                        output_path='charts/rating_scatter.png'):
    """绘制评分与评价人数的散点图"""
    scatter_data = df[[rating_col, people_col]].dropna()
    
    if len(scatter_data) == 0:
        print("⚠️ 没有有效的散点图数据")
        return
    
    plt.figure(figsize=(12, 7))
    
    scatter_data['log_people'] = np.log1p(scatter_data[people_col])
    
    scatter = plt.scatter(scatter_data[rating_col], 
                          scatter_data['log_people'],
                          c=scatter_data[rating_col], 
                          cmap='RdYlBu_r', 
                          alpha=0.6, 
                          s=30)
    
    z = np.polyfit(scatter_data[rating_col], scatter_data['log_people'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(scatter_data[rating_col].min(), 
                          scatter_data[rating_col].max(), 100)
    plt.plot(x_trend, p(x_trend), "r--", linewidth=2, 
             label=f"趋势线 (斜率: {z[0]:.3f})")
    
    plt.colorbar(scatter, label='评分')
    plt.xlabel('电影评分', fontsize=12)
    plt.ylabel('评价人数 (对数尺度)', fontsize=12)
    plt.title('电影评分与评价人数的相关性分析', fontsize=14)
    plt.legend()
    plt.grid(alpha=0.3)
    
    corr = scatter_data[rating_col].corr(scatter_data['log_people'])
    plt.text(0.05, 0.95, f'相关系数: {corr:.4f}', 
             transform=plt.gca().transAxes, fontsize=12,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"散点图已保存至: {output_path}")

def plot_wordcloud(word_freq, output_path='charts/wordcloud.png'):
    """绘制短评词云"""
    font_path = get_wordcloud_font_path()
    
    if font_path:
        wordcloud = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            font_path=font_path,
            max_words=200,
            colormap='viridis',
            random_state=42,
            relative_scaling=0.5,
            prefer_horizontal=0.9,
            collocations=False
        ).generate_from_frequencies(word_freq)
    else:
        wordcloud = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            max_words=200,
            colormap='viridis',
            random_state=42,
            relative_scaling=0.5,
            prefer_horizontal=0.9,
            collocations=False
        ).generate_from_frequencies(word_freq)
    
    plt.figure(figsize=(14, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('短评高频词云图', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"词云图已保存至: {output_path}")

def plot_time_trend(trend_data, output_path='charts/time_trend.png', 
                    plotly_output='charts/time_trend.html'):
    """绘制时间趋势线图"""
    # Plotly 交互式图表
    fig = px.line(trend_data, x='year', y='avg_rating',
                  title='电影平均评分年度趋势',
                  labels={'year': '年份', 'avg_rating': '平均评分'},
                  markers=True)
    
    fig.update_traces(
        line=dict(color='royalblue', width=3),
        marker=dict(size=8, color='darkblue', symbol='circle')
    )
    
    fig.update_layout(
        title_x=0.5,
        width=900,
        height=550,
        hovermode='x unified',
        xaxis=dict(tickangle=45)
    )
    
    fig.add_trace(go.Scatter(
        x=trend_data['year'], 
        y=trend_data['count'] / trend_data['count'].max() * 5,
        name='电影数量(相对值)',
        line=dict(color='gray', width=1, dash='dot'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        yaxis2=dict(
            title="电影数量 (相对值)",
            overlaying='y',
            side='right'
        )
    )
    
    fig.write_html(plotly_output)
    fig.show()
    
    # matplotlib 静态图表
    fig_mpl, ax1 = plt.subplots(figsize=(12, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('年份', fontsize=12)
    ax1.set_ylabel('平均评分', color=color, fontsize=12)
    ax1.plot(trend_data['year'], trend_data['avg_rating'], 
             color=color, marker='o', linewidth=2, markersize=6)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)
    
    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('电影数量', color=color, fontsize=12)
    ax2.bar(trend_data['year'], trend_data['count'], color=color, alpha=0.3)
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('电影平均评分与产出数量年度趋势', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"静态趋势图已保存至: {output_path}")
    print(f"交互式趋势图已保存至: {plotly_output}")

def plot_top_movies_bar(top_movies, output_path='charts/top_movies.png'):
    """绘制Top 10高分电影条形图"""
    plt.figure(figsize=(12, 8))
    
    bars = plt.barh(top_movies['title'], top_movies['rating'], 
                    color=plt.cm.RdYlBu_r(top_movies['rating'] / 10))
    
    for i, (bar, rating) in enumerate(zip(bars, top_movies['rating'])):
        plt.text(rating + 0.05, bar.get_y() + bar.get_height()/2, 
                f'{rating:.1f}', va='center', fontsize=10)
    
    plt.xlabel('评分', fontsize=12)
    plt.ylabel('电影名称', fontsize=12)
    plt.title('高分电影 Top 10', fontsize=14)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"Top10电影图已保存至: {output_path}")

def plot_sentiment_pie(distribution, output_path='charts/sentiment_pie.png'):
    """绘制情感倾向分布饼图"""
    if not distribution:
        return
        
    labels = ['积极', '中性', '消极']
    sizes = [
        distribution['positive']['count'],
        distribution['neutral']['count'],
        distribution['negative']['count']
    ]
    
    # 设置饼图颜色：绿色代表积极，灰色代表中性，红色代表消极
    colors = ['#2ca02c', '#7f7f7f', '#d62728']
    
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
            startangle=140, shadow=True, explode=(0.05, 0, 0))
    plt.title(f"短评情感倾向真实分布", fontsize=16)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"情感分布饼图已保存至: {output_path}")