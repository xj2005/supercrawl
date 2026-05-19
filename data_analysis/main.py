#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_analysis.data_cleaner import DataCleaner
from data_analysis.statistical_analysis import StatisticalAnalyzer
from data_analysis.sentiment_analyzer import SentimentAnalyzer
from data_analysis.visualizer import (
    plot_rating_histogram,
    plot_genre_pie_chart,
    plot_rating_scatter,
    plot_wordcloud,
    plot_time_trend,
    plot_top_movies_bar,
    plot_sentiment_pie  
)

def setup_directories():
    project_root = Path(__file__).parent.parent
    
    # 已有的输出目录
    raw_data_dir = project_root / 'output1' / 'raw_data'
    images_dir = project_root / 'output1' / 'images'
    
    # 新增的目录
    cleaned_data_dir = project_root / 'output3' / 'cleaned_data'
    analysis_dir = project_root / 'output3' / 'analysis'
    charts_dir = analysis_dir / 'charts'
    
    # 创建新目录
    cleaned_data_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        'raw_data_dir': raw_data_dir,
        'cleaned_data_dir': cleaned_data_dir,
        'images_dir': images_dir,
        'analysis_dir': analysis_dir,
        'charts_dir': charts_dir
    }

def find_latest_raw_data(raw_data_dir):
    """自动查找raw_data目录中最新的CSV文件"""
    csv_files = list(raw_data_dir.glob('*.csv'))
    if not csv_files:
        raise FileNotFoundError(f"在 {raw_data_dir} 中没有找到CSV文件")
    
    # 优先使用包含'movie'或'film'关键字的文件，否则使用最新的
    movie_files = [f for f in csv_files if 'movie' in f.stem.lower() or 'film' in f.stem.lower()]
    if movie_files:
        latest_file = max(movie_files, key=lambda f: f.stat().st_mtime)
    else:
        latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
    
    print(f"找到原始数据文件: {latest_file.name}")
    return latest_file

def run_full_analysis(input_file=None):
    """运行完整的数据分析与可视化流程"""
    
    # 设置目录结构
    dirs = setup_directories()
    
    # 确定输入文件路径
    if input_file is None:
        input_file = find_latest_raw_data(dirs['raw_data_dir'])
    else:
        input_file = Path(input_file)
    
    # 输出文件路径
    cleaned_file = dirs['cleaned_data_dir'] / f"{input_file.stem}_cleaned.csv"
    
    print("=" * 60)
    print("电影数据完整分析流程")
    print("=" * 60)
    print(f"数据源: {input_file}")
    print(f"清洗后数据输出: {cleaned_file}")
    print(f"图表输出目录: {dirs['charts_dir']}")
    print("=" * 60)
    
    # 步骤1: 数据清洗
    print("\n[1/5] 数据清洗...")
    cleaner = DataCleaner(str(input_file), str(cleaned_file))
    df_cleaned = cleaner.run_full_cleaning(missing_strategy='fill_zero')
    
    # 检查是否有数据
    if len(df_cleaned) == 0:
        print("❌ 错误: 清洗后没有数据，请检查原始数据")
        return
    
    # 步骤2: 统计分析 
    print("\n[2/5] 统计分析...")
    analyzer = StatisticalAnalyzer(df_cleaned)
    
    # 2.1 高分电影 Top 10
    top_movies = analyzer.get_top_movies(n=10)
    if top_movies is not None and len(top_movies) > 0:
        plot_top_movies_bar(top_movies, output_path=str(dirs['charts_dir'] / 'top_movies.png'))
    
    # 2.2 导演分布
    top_directors = analyzer.analyze_director_distribution(n=10)
    
    # 2.3 类型分布
    genre_counts = analyzer.analyze_genre_distribution()
    if genre_counts:
        plot_genre_pie_chart(genre_counts, 
                            output_path=str(dirs['charts_dir'] / 'genre_pie.png'),
                            plotly_output=str(dirs['charts_dir'] / 'genre_pie.html'))
    
    # 2.4 评分与评价人数相关性
    correlation = analyzer.analyze_correlation()
    if correlation:
        # 将相关性结果保存到分析目录
        correlation_df = pd.DataFrame([correlation])
        correlation_df.to_csv(dirs['analysis_dir'] / 'correlation_result.csv', index=False)
    
    # 2.5 时间趋势分析
    trend_data = analyzer.analyze_time_trend()
    if trend_data is not None and len(trend_data) > 0:
        plot_time_trend(trend_data,
                       output_path=str(dirs['charts_dir'] / 'time_trend.png'),
                       plotly_output=str(dirs['charts_dir'] / 'time_trend.html'))
        # 保存趋势数据
        trend_data.to_csv(dirs['analysis_dir'] / 'time_trend_data.csv', index=False)
    
    # 步骤3: 情感分析
    # print("\n[3/5] 情感分析...")
    # # 检查是否有评论列
    # comment_col = None
    # for col in ['comment', '热门短评', '短评']:
    #     if col in df_cleaned.columns:
    #         comment_col = col
    #         break
    
    # if comment_col:
    #     print(f"使用评论列: {comment_col}")
    #     sentiment_analyzer = SentimentAnalyzer(df_cleaned, comment_column=comment_col)
        
    #     # 获取情感分布
    #     sentiment_dist = sentiment_analyzer.get_sentiment_distribution()
        
    #     # 生成词云数据
    #     word_freq = sentiment_analyzer.generate_wordcloud_data(comment_column=comment_col)
        
    #     # 生成词云图
    #     if word_freq:
    #         plot_wordcloud(word_freq, output_path=str(dirs['charts_dir'] / 'wordcloud.png'))
            
    #         # 保存词频数据
    #         word_freq_df = pd.DataFrame(list(word_freq.items()), columns=['word', 'frequency'])
    #         word_freq_df.to_csv(dirs['analysis_dir'] / 'word_frequency.csv', index=False)
        
    #     # 导出情感分析结果
    #     sentiment_analyzer.export_sentiment_results(
    #         str(dirs['analysis_dir'] / 'sentiment_results.csv')
    #     )
    # else:
    #     print("未找到评论列，跳过情感分析")
    print("\n[3/5] 情感分析...")
    comment_col = None
    for col in ['comment', '热门短评', '短评']:
        if col in df_cleaned.columns:
            comment_col = col
            break
    
    if comment_col:
        print(f"使用评论列: {comment_col}")
        
        
        all_comments = []
        for text in df_cleaned[comment_col].dropna():
            split_comments = str(text).split(" | ") 
            for c in split_comments:
                if ":" in c:
                    # 提取冒号后面的纯评论，丢掉用户名和评分
                    pure_comment = c.split(":", 1)[1].strip()
                    if pure_comment:
                        all_comments.append(pure_comment)
                elif c.strip():
                    all_comments.append(c.strip())
                    
        print(f"成功从 250 部电影中提取出 {len(all_comments)} 条独立短评！")
        
        # 用拆分后的纯短评构建一个新的专用 DataFrame
        df_comments = pd.DataFrame({comment_col: all_comments})
        sentiment_analyzer = SentimentAnalyzer(df_comments, comment_column=comment_col)
        
        # 获取分布
        sentiment_dist = sentiment_analyzer.get_sentiment_distribution()
        
        # 画出情感分布饼图
        if sentiment_dist:
            plot_sentiment_pie(sentiment_dist, output_path=str(dirs['charts_dir'] / 'sentiment_pie.png'))
        
        # 生成词云数据 
        word_freq = sentiment_analyzer.generate_wordcloud_data(comment_column=comment_col)
        
        if word_freq:
            plot_wordcloud(word_freq, output_path=str(dirs['charts_dir'] / 'wordcloud.png'))
            word_freq_df = pd.DataFrame(list(word_freq.items()), columns=['word', 'frequency'])
            word_freq_df.to_csv(dirs['analysis_dir'] / 'word_frequency.csv', index=False)
            
        sentiment_analyzer.export_sentiment_results(str(dirs['analysis_dir'] / 'sentiment_results.csv'))
    else:
        print("⚠️未找到评论列，跳过情感分析")
    
    # 生成评分分布图
    print("\n[4/5] 生成评分分布直方图...")
    if 'rating' in df_cleaned.columns:
        plot_rating_histogram(df_cleaned, output_path=str(dirs['charts_dir'] / 'rating_histogram.png'))
    else:
        print("⚠️ 未找到评分列，跳过直方图生成")
    
    #  生成散点图 
    print("\n[5/5] 生成评分-评价人数散点图...")
    if 'rating' in df_cleaned.columns and 'rating_people' in df_cleaned.columns:
        plot_rating_scatter(df_cleaned, output_path=str(dirs['charts_dir'] / 'rating_scatter.png'))
    else:
        print("⚠️ 未找到评分或评价人数列，跳过散点图生成")
    
    # 生成分析摘要报告 
    print("\n生成分析摘要报告...")
    generate_summary_report(df_cleaned, dirs, input_file)
    
    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print(f"📊 清洗后数据: {cleaned_file}")
    print(f"📈 图表输出: {dirs['charts_dir']}")
    print(f"📄 分析数据: {dirs['analysis_dir']}")
    print("=" * 60)

def generate_summary_report(df, dirs, input_file):
    """生成分析摘要报告"""
    report_path = dirs['analysis_dir'] / 'analysis_summary.txt'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("电影数据分析摘要报告\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"数据源文件: {input_file.name}\n")
        f.write(f"分析时间: {pd.Timestamp.now()}\n\n")
        
        f.write("【数据概览】\n")
        f.write(f"- 总记录数: {len(df)}\n")
        f.write(f"- 字段数量: {len(df.columns)}\n")
        
        if 'rating' in df.columns:
            f.write(f"- 评分范围: {df['rating'].min():.1f} - {df['rating'].max():.1f}\n")
            f.write(f"- 平均评分: {df['rating'].mean():.2f}\n\n")
        
        if 'rating_people' in df.columns:
            f.write("【热度分析】\n")
            f.write(f"- 平均评价人数: {df['rating_people'].mean():.0f}\n")
            f.write(f"- 最高评价人数: {df['rating_people'].max():.0f}\n\n")
        
        # 情感分析统计
        if 'sentiment_score' in df.columns:
            f.write("【情感分析】\n")
            f.write(f"- 平均情感得分: {df['sentiment_score'].mean():.3f}\n")
            positive = (df['sentiment_score'] >= 0.7).sum()
            neutral = ((df['sentiment_score'] >= 0.3) & (df['sentiment_score'] < 0.7)).sum()
            negative = (df['sentiment_score'] < 0.3).sum()
            f.write(f"- 积极评论: {positive} 条\n")
            f.write(f"- 中性评论: {neutral} 条\n")
            f.write(f"- 消极评论: {negative} 条\n\n")
        
        f.write("【生成的文件】\n")
        f.write("- 图表文件: output/analysis/charts/\n")
        f.write("  • rating_histogram.png - 评分分布直方图\n")
        f.write("  • genre_pie.html/png - 类型分布图\n")
        f.write("  • rating_scatter.png - 评分vs评价人数散点图\n")
        f.write("  • wordcloud.png - 短评词云图\n")
        f.write("  • time_trend.html/png - 时间趋势图\n")
        f.write("  • top_movies.png - Top10高分电影\n")
        f.write("- 数据文件: output/analysis/\n")
        f.write("  • correlation_result.csv - 相关性分析结果\n")
        f.write("  • time_trend_data.csv - 时间趋势数据\n")
        f.write("  • word_frequency.csv - 词频统计数据\n")
        f.write("  • sentiment_results.csv - 情感分析结果\n")
        f.write("- 清洗数据: output/cleaned_data/\n")
    
    print(f"📝 分析摘要报告已生成: {report_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='电影数据分析与可视化工具')
    parser.add_argument('--input', type=str, help='指定原始数据文件路径（可选，默认使用raw_data中的最新CSV）')
    args = parser.parse_args()
    
    try:
        run_full_analysis(args.input)
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        print("请确保 output/raw_data/ 目录中存在CSV文件")
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()