import pandas as pd
import numpy as np
from collections import Counter
import jieba
from snownlp import SnowNLP

class StatisticalAnalyzer:
    """统计分析类"""
    
    def __init__(self, df):
        self.df = df.copy()
        
    def check_column_exists(self, column, column_name_desc=""):
        """检查列是否存在"""
        if column not in self.df.columns:
            print(f"⚠️ 警告: 列 '{column}' 不存在 {column_name_desc}")
            print(f"   当前可用列: {self.df.columns.tolist()}")
            return False
        return True
    
    def get_top_movies(self, column='title', value_column='rating', n=10):
        """高分电影Top N"""
        # 检查列是否存在
        if not self.check_column_exists(column, "(电影名称列)"):
            return None
        if not self.check_column_exists(value_column, "(评分列)"):
            return None
        
        # 删除缺失值
        clean_df = self.df[[column, value_column]].dropna()
        
        if len(clean_df) == 0:
            print("❌ 错误: 没有找到有效的电影数据")
            return None
        
        top_movies = clean_df.sort_values(value_column, ascending=False).head(n)
        
        print(f"\n🏆 Top {n} 高分电影:")
        print("=" * 50)
        for idx, (idx_row, row) in enumerate(top_movies.iterrows(), 1):
            print(f"{idx}. {row[column]}: {row[value_column]}")
        print("=" * 50)
        
        return top_movies
    
    def analyze_director_distribution(self, column='director', n=10):
        """导演作品数量分布"""
        if not self.check_column_exists(column, "(导演列)"):
            return None
        
        # 处理导演可能包含多个的情况
        all_directors = []
        for directors in self.df[column].dropna():
            if isinstance(directors, str):
                # 处理多种分隔符，取第一个导演
                for sep in ['/', '、', ',', '，', '主演']:
                    if sep in directors:
                        directors = directors.split(sep)[0]
                        break
                # 移除可能的"主演"等后缀
                directors = directors.replace('主演', '').strip()
                if directors:  # 确保不为空
                    all_directors.append(directors)
        
        if not all_directors:
            print("❌ 错误: 没有找到有效的导演数据")
            return None
        
        director_counts = Counter(all_directors)
        top_directors = director_counts.most_common(n)
        
        print(f"\n🎬 Top {n} 导演及其作品数量:")
        print("=" * 50)
        for name, count in top_directors:
            print(f"{name}: {count} 部")
        print("=" * 50)
        
        return top_directors
    
    def analyze_genre_distribution(self, column='genre'):
        """电影类型分布分析"""
        if not self.check_column_exists(column, "(类型列)"):
            return None
        
        all_genres = []
        for genres in self.df[column].dropna():
            if isinstance(genres, str):
                # 处理多种分隔符
                for sep in ['/', '、', ',', '，', ' ']:
                    if sep in genres:
                        genres = genres.split(sep)
                        break
                if isinstance(genres, str):
                    genres = [genres]
                all_genres.extend([g.strip() for g in genres if g.strip()])
        
        if not all_genres:
            print("❌ 错误: 没有找到有效的类型数据")
            return None
        
        genre_counts = Counter(all_genres)
        
        print(f"\n🎭 电影类型分布:")
        print("=" * 50)
        for genre, count in genre_counts.most_common(15):
            print(f"{genre}: {count} 部 ({count/len(all_genres)*100:.1f}%)")
        print("=" * 50)
        
        return genre_counts
    
    def analyze_correlation(self, x_col='rating', y_col='rating_people'):
        """评分与评价人数的相关性分析"""
        if not self.check_column_exists(x_col, "(评分列)"):
            return None
        if not self.check_column_exists(y_col, "(评价人数列)"):
            return None
        
        # 删除缺失值
        clean_df = self.df[[x_col, y_col]].dropna()
        
        if len(clean_df) < 3:
            print("❌ 错误: 数据量不足，无法进行相关性分析")
            return None
        
        # 使用对数变换处理评价人数（通常呈长尾分布）
        clean_df['log_people'] = np.log1p(clean_df[y_col])
        
        # 计算皮尔逊相关系数
        pearson_corr = clean_df[x_col].corr(clean_df[y_col])
        log_corr = clean_df[x_col].corr(clean_df['log_people'])
        
        print(f"\n📊 相关性分析结果:")
        print("=" * 50)
        print(f"评分 vs 评价人数 (皮尔逊相关系数): {pearson_corr:.4f}")
        print(f"评分 vs Log(评价人数) (皮尔逊相关系数): {log_corr:.4f}")
        print()
        
        if abs(pearson_corr) > 0.5:
            print(f"📈 结论: 两者之间存在较强的{'正' if pearson_corr > 0 else '负'}相关关系")
        elif abs(pearson_corr) > 0.3:
            print(f"📉 结论: 两者之间存在一定的{'正' if pearson_corr > 0 else '负'}相关关系")
        else:
            print(f"🔍 结论: 两者之间相关关系较弱")
        print("=" * 50)
        
        return {'pearson_corr': pearson_corr, 'log_corr': log_corr, 'data_count': len(clean_df)}
    
    def analyze_time_trend(self, time_col='year', value_col='rating'):
        """时间趋势分析（按年份的平均评分趋势）"""
        if not self.check_column_exists(time_col, "(年份列)"):
            return None
        if not self.check_column_exists(value_col, "(评分列)"):
            return None
        
        # 按年份分组，计算平均评分和数量
        trend_data = (self.df[[time_col, value_col]]
                     .dropna()
                     .groupby(time_col)[value_col]
                     .agg(['mean', 'count', 'std'])
                     .reset_index())
        trend_data.columns = ['year', 'avg_rating', 'count', 'std']
        
        # 过滤掉样本太少的年份
        trend_data = trend_data[trend_data['count'] >= 2]
        
        if len(trend_data) == 0:
            print("❌ 错误: 没有足够的时间趋势数据")
            return None
        
        print(f"\n📅 时间趋势分析 (按年份):")
        print("=" * 60)
        print(f"{'年份':<8} {'平均评分':<10} {'电影数量':<8} {'评分标准差':<10}")
        print("-" * 60)
        for _, row in trend_data.iterrows():
            print(f"{int(row['year']):<8} {row['avg_rating']:<10.2f} {int(row['count']):<8} {row['std']:<10.2f}")
        print("=" * 60)
        
        # 计算整体趋势
        if len(trend_data) > 1:
            slope = np.polyfit(trend_data['year'], trend_data['avg_rating'], 1)[0]
            if slope > 0:
                print(f"📈 总体趋势: 评分呈上升趋势 (年均增长 {slope:.3f} 分)")
            elif slope < 0:
                print(f"📉 总体趋势: 评分呈下降趋势 (年均下降 {abs(slope):.3f} 分)")
            else:
                print(f"➡️ 总体趋势: 评分保持稳定")
        
        return trend_data
    
    def analyze_rating_distribution(self, rating_col='rating', bins=10):
        """评分分布统计"""
        if not self.check_column_exists(rating_col, "(评分列)"):
            return None
        
        ratings = self.df[rating_col].dropna()
        
        if len(ratings) == 0:
            print("❌ 错误: 没有有效的评分数据")
            return None
        
        print(f"\n⭐ 评分分布统计:")
        print("=" * 50)
        print(f"总电影数: {len(ratings)}")
        print(f"平均评分: {ratings.mean():.2f}")
        print(f"中位数评分: {ratings.median():.2f}")
        print(f"最高评分: {ratings.max():.1f}")
        print(f"最低评分: {ratings.min():.1f}")
        print(f"评分标准差: {ratings.std():.2f}")
        print()
        
        # 评分区间分布
        print("评分区间分布:")
        hist, bins_edges = np.histogram(ratings, bins=bins, range=(0, 10))
        for i, (count, edge) in enumerate(zip(hist, bins_edges[:-1])):
            print(f"  {edge:.1f}-{bins_edges[i+1]:.1f}: {count} 部 ({count/len(ratings)*100:.1f}%)")
        print("=" * 50)
        
        return {
            'mean': ratings.mean(),
            'median': ratings.median(),
            'max': ratings.max(),
            'min': ratings.min(),
            'std': ratings.std(),
            'histogram': (hist, bins_edges)
        }
    
    def get_summary_statistics(self):
        """获取数据集的总体统计摘要"""
        print(f"\n📊 数据集总体统计摘要")
        print("=" * 60)
        print(f"总数据量: {len(self.df)} 行")
        print(f"字段数量: {len(self.df.columns)} 列")
        print()
        
        # 数值型字段统计
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            print("数值型字段统计:")
            for col in numeric_cols:
                non_null = self.df[col].notna().sum()
                if non_null > 0:
                    print(f"  {col}:")
                    print(f"    有效数据: {non_null}/{len(self.df)} ({non_null/len(self.df)*100:.1f}%)")
                    print(f"    均值: {self.df[col].mean():.2f}")
                    print(f"    范围: {self.df[col].min():.2f} - {self.df[col].max():.2f}")
        print("=" * 60)


