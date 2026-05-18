import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import pandas as pd
import numpy as np

# 全局配置matplotlib中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置seaborn样式
sns.set_style("whitegrid")
sns.set_palette("husl")

def plot_rating_histogram(df, rating_col='rating', output_path='charts/rating_histogram.png'):
    """绘制评分分布直方图"""
    plt.figure(figsize=(12, 6))
    
    # 移除缺失值
    ratings = df[rating_col].dropna()
    
    # 绘制直方图
    n, bins, patches = plt.hist(ratings, bins=20, edgecolor='black', alpha=0.7, 
                                 color='steelblue', rwidth=0.95)
    
    # 添加平均线和中位数线
    mean_rating = ratings.mean()
    median_rating = ratings.median()
    plt.axvline(mean_rating, color='red', linestyle='--', linewidth=2, 
                label=f'平均分: {mean_rating:.2f}')
    plt.axvline(median_rating, color='green', linestyle='--', linewidth=2, 
                label=f'中位数: {median_rating:.2f}')
    
    # 在每个柱子顶部添加数值
    for i, (count, bin_left) in enumerate(zip(n, bins[:-1])):
        if count > 0:
            plt.text(bin_left + (bins[1]-bins[0])/2, count + max(n)*0.01, 
                    str(int(count)), ha='center', va='bottom', fontsize=9)
    
    plt.xlabel('评分', fontsize=12)
    plt.ylabel('电影数量', fontsize=12)
    plt.title('电影评分分布直方图', fontsize=14)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.show()
    print(f"直方图已保存至: {output_path}")


def plot_genre_pie_chart(genre_counts, output_path='charts/genre_pie.png', plotly_output='charts/genre_pie.html'):
    """绘制电影类型饼图"""
    # 获取Top 8类型，其余归为"其他"
    top_genres = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:8])
    other_count = sum([v for k, v in genre_counts.items() if k not in top_genres])
    if other_count > 0:
        top_genres['其他'] = other_count

    # 使用Plotly绘制交互式饼图
    fig = px.pie(
        values=list(top_genres.values()),
        names=list(top_genres.keys()),
        title='电影类型分布占比',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.3  # 圆环图效果
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

    # 同时使用matplotlib保存静态版本
    plt.figure(figsize=(10, 10))
    plt.pie(list(top_genres.values()), 
            labels=list(top_genres.keys()),
            autopct='%1.1f%%',
            startangle=90,
            explode=[0.05] * len(top_genres),
            shadow=True)
    plt.title('电影类型分布占比', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.show()

    print(f"饼图已保存至: {output_path}")
    print(f"交互式饼图已保存至: {plotly_output}")


def plot_rating_scatter(df, rating_col='rating', people_col='rating_people', 
                        output_path='charts/rating_scatter.png'):
    """绘制评分与评价人数的散点图（含趋势线）"""
    # 准备数据
    scatter_data = df[[rating_col, people_col]].dropna()

    plt.figure(figsize=(12, 7))

    # 使用对数坐标处理评价人数
    scatter_data['log_people'] = np.log1p(scatter_data[people_col])

    # 绘制散点图
    scatter = plt.scatter(scatter_data[rating_col], 
                          scatter_data['log_people'],
                          c=scatter_data[rating_col], 
                          cmap='RdYlBu_r', 
                          alpha=0.6, 
                          s=30)

    # 添加趋势线
    z = np.polyfit(scatter_data[rating_col], scatter_data['log_people'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(scatter_data[rating_col].min(), 
                          scatter_data[rating_col].max(), 100)
    plt.plot(x_trend, p(x_trend), "r--", linewidth=2, 
             label=f"趋势线 (斜率: {z[0]:.3f})")

    plt.colorbar(scatter, label='评分')
    plt.xlabel('电影评分', fontsize=12)
    plt.ylabel('评价人数 (对数尺度: log₁₀(1+n))', fontsize=12)
    plt.title('电影评分与评价人数的相关性分析', fontsize=14)
    plt.legend()
    plt.grid(alpha=0.3)

    # 添加相关系数文本
    corr = scatter_data[rating_col].corr(scatter_data['log_people'])
    plt.text(0.05, 0.95, f'相关系数: {corr:.4f}', 
             transform=plt.gca().transAxes, fontsize=12,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.show()
    print(f"散点图已保存至: {output_path}")


def plot_wordcloud(word_freq, output_path='charts/wordcloud.png'):
    """绘制短评词云"""
    # 配置中文字体路径
    # Windows: 'C:/Windows/Fonts/simhei.ttf'
    # macOS: '/System/Library/Fonts/PingFang.ttc'
    # Linux: '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
    font_path = 'C:/Windows/Fonts/simhei.ttf'  # 请根据你的系统修改

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
        collocations=False  # 避免重复词组
    ).generate_from_frequencies(word_freq)

    plt.figure(figsize=(14, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('短评高频词云图', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.show()
    print(f"词云图已保存至: {output_path}")


def plot_time_trend(trend_data, output_path='charts/time_trend.png', 
                    plotly_output='charts/time_trend.html'):
    """绘制时间趋势线图"""
    # 使用Plotly绘制交互式趋势图
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

    # 添加评分数量作为次要信息
    fig.add_trace(go.Scatter(
        x=trend_data['year'], 
        y=trend_data['count'] / trend_data['count'].max() * 5,  # 归一化显示
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

    # 使用matplotlib绘制静态版本
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
    plt.savefig(output_path, dpi=150)
    plt.show()

    print(f"时间趋势图已保存至: {output_path}")
    print(f"交互式趋势图已保存至: {plotly_output}")


def plot_top_movies_bar(top_movies, output_path='charts/top_movies.png'):
    """绘制Top 10高分电影条形图"""
    plt.figure(figsize=(12, 8))

    bars = plt.barh(top_movies['title'], top_movies['rating'], 
                    color=plt.cm.RdYlBu_r(top_movies['rating'] / 10))

    # 在每个条形末尾添加评分
    for i, (bar, rating) in enumerate(zip(bars, top_movies['rating'])):
        plt.text(rating + 0.05, bar.get_y() + bar.get_height()/2, 
                f'{rating:.1f}', va='center', fontsize=10)

    plt.xlabel('评分', fontsize=12)
    plt.ylabel('电影名称', fontsize=12)
    plt.title('高分电影 Top 10', fontsize=14)
    plt.gca().invert_yaxis()  # 最高分在上方
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.show()
    print(f"Top10电影图已保存至: {output_path}")