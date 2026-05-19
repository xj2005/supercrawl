import pandas as pd
import numpy as np
from snownlp import SnowNLP
import jieba
from collections import Counter

class SentimentAnalyzer:
    """短评情感倾向分析类"""
    
    def __init__(self, df, comment_column='comment'):
        self.df = df.copy()
        self.comment_column = comment_column
        self.sentiment_scores = None
        self.sentiment_analyzed = False  # 标记是否已进行情感分析
        
    def check_comment_column(self):
        """检查评论列是否存在"""
        if self.comment_column not in self.df.columns:
            print(f"⚠️ 警告: 列 '{self.comment_column}' 不存在")
            print(f"   当前可用列: {self.df.columns.tolist()}")
            return False
        return True
    
    def analyze_batch_sentiments(self, batch_size=100):
        """批量分析短评的情感倾向"""
        if not self.check_comment_column():
            return self.df
        
        # 获取非空的评论
        comments_data = self.df[self.df[self.comment_column].notna()]
        
        if len(comments_data) == 0:
            print("❌ 错误: 没有找到有效的评论数据")
            self.sentiment_analyzed = True
            # 创建默认的情感分数列
            self.df['sentiment_score'] = 0.5
            self.df['sentiment_label'] = '中性'
            return self.df
        
        comments = comments_data[self.comment_column].tolist()
        print(f"开始分析 {len(comments)} 条评论的情感倾向...")
        
        sentiment_scores = []
        
        for i, comment in enumerate(comments):
            try:
                if len(str(comment).strip()) == 0:
                    sentiment_scores.append(0.5)  # 中性
                    continue
                    
                s = SnowNLP(str(comment))
                score = s.sentiments  # 返回0-1之间的值，越高越积极
                sentiment_scores.append(score)
                
                # 显示进度
                if (i + 1) % 20 == 0 or (i + 1) == len(comments):
                    print(f"  进度: {i+1}/{len(comments)} ({ (i+1)/len(comments)*100:.1f}%)")
                
            except Exception as e:
                print(f"⚠️ 分析第{i+1}条评论时出错: {e}")
                sentiment_scores.append(0.5)
        
        # 将情感得分添加回DataFrame
        self.df['sentiment_score'] = 0.5  # 默认值
        self.df['sentiment_label'] = '中性'  # 默认标签
        
        # 只为有评论的行设置情感分数
        comment_indices = self.df[self.df[self.comment_column].notna()].index
        for idx, score in zip(comment_indices[:len(sentiment_scores)], sentiment_scores):
            self.df.loc[idx, 'sentiment_score'] = score
            # 添加情感标签
            if score <= 0.3:
                self.df.loc[idx, 'sentiment_label'] = '消极'
            elif score >= 0.7:
                self.df.loc[idx, 'sentiment_label'] = '积极'
            else:
                self.df.loc[idx, 'sentiment_label'] = '中性'
        
        self.sentiment_analyzed = True
        print(f"✅ 情感分析完成！")
        
        return self.df
    
    def get_sentiment_distribution(self, thresholds=(0.3, 0.7)):
        """获取情感倾向分布（自动进行情感分析如果尚未进行）"""
        # 如果还没有进行情感分析，先进行分析
        if not self.sentiment_analyzed or 'sentiment_score' not in self.df.columns:
            self.analyze_batch_sentiments()
        
        negative_threshold, positive_threshold = thresholds
        
        # 统计情感分布
        negative = (self.df['sentiment_score'] <= negative_threshold).sum()
        neutral = ((self.df['sentiment_score'] > negative_threshold) & 
                   (self.df['sentiment_score'] < positive_threshold)).sum()
        positive = (self.df['sentiment_score'] >= positive_threshold).sum()
        
        total = len(self.df[self.df[self.comment_column].notna()]) if self.comment_column in self.df.columns else len(self.df)
        
        if total == 0:
            print("❌ 错误: 没有有效的评论数据")
            return None
        
        distribution = {
            'negative': {'count': negative, 'percentage': negative / total * 100},
            'neutral': {'count': neutral, 'percentage': neutral / total * 100},
            'positive': {'count': positive, 'percentage': positive / total * 100}
        }
        
        print(f"\n💬 情感倾向分析结果:")
        print("=" * 50)
        print(f"😞 消极评论: {negative} 条 ({negative/total*100:.1f}%)")
        print(f"😐 中性评论: {neutral} 条 ({neutral/total*100:.1f}%)")
        print(f"😊 积极评论: {positive} 条 ({positive/total*100:.1f}%)")
        print("=" * 50)
        
        # 计算平均情感得分
        avg_score = self.df['sentiment_score'].mean()
        print(f"📊 平均情感得分: {avg_score:.3f} (0-1, 越高越积极)")
        
        return distribution
    
    def generate_wordcloud_data(self, comment_column='comment', top_n=100):
        """生成词云所需的数据 - 词频统计"""
        if not self.check_comment_column():
            return None
        
        # 使用 comment_column 参数
        comments = self.df[comment_column].dropna().tolist()
        
        if len(comments) == 0:
            print("❌ 错误: 没有找到有效的评论数据用于词云")
            return None
        
        print(f"开始分析 {len(comments)} 条评论的词频...")
        
        # 读取本地 stopwords.txt 作为停用词表
        import os
        stopwords = set()
        stopwords_path = 'stopwords.txt'
        
        if os.path.exists(stopwords_path):
            with open(stopwords_path, 'r', encoding='gbk') as f:
                # 逐行读取并去除空白字符，存入集合中
                stopwords = {line.strip() for line in f if line.strip()}
            print(f"成功加载外部停用词表，共引入 {len(stopwords)} 个过滤词")
        else:
            print("未找到 stopwords.txt，退回使用默认精简停用词")
            stopwords = {'的', '了', '是', '在', '和', '与', '就', '都', '也', '还'}
        
        word_counts = Counter()
        
        for comment in comments:
            if len(str(comment).strip()) == 0:
                continue
                
            # 使用jieba进行中文分词
            words = jieba.lcut(str(comment))
            for word in words:
                word = word.strip()
                # 过滤条件：长度>=2，不是停用词，不是纯数字/标点
                if (len(word) >= 2 and 
                    word not in stopwords and 
                    not word.isdigit() and 
                    not all(p in '，。！？；：“”‘’【】《》、' for p in word)):
                    word_counts[word] += 1
        
        # 返回Top N的高频词
        top_words = dict(word_counts.most_common(top_n))
        
        if len(top_words) == 0:
            print("❌ 错误: 没有提取到有效的词汇")
            return None
        
        print(f"✅ 共提取到 {len(word_counts)} 个不同的词")
        print(f"\n📝 Top 10 高频词:")
        print("=" * 40)
        for i, (word, count) in enumerate(list(word_counts.most_common(10)), 1):
            print(f"{i}. {word}: {count} 次")
        print("=" * 40)
        
        return top_words
    
    def get_sentiment_by_movie(self, movie_col='title'):
        """获取每部电影的平均情感得分"""
        if not self.sentiment_analyzed or 'sentiment_score' not in self.df.columns:
            self.analyze_batch_sentiments()
        
        if movie_col not in self.df.columns:
            print(f"⚠️ 警告: 列 '{movie_col}' 不存在，无法按电影统计情感")
            return None
        
        # 按电影分组计算平均情感得分
        sentiment_by_movie = (self.df.groupby(movie_col)['sentiment_score']
                             .agg(['mean', 'count'])
                             .sort_values('mean', ascending=False)
                             .head(10))
        
        print(f"\n🎬 情感得分最高的电影 Top 10:")
        print("=" * 50)
        for idx, row in sentiment_by_movie.iterrows():
            print(f"{idx}: {row['mean']:.3f} (基于 {int(row['count'])} 条评论)")
        print("=" * 50)
        
        return sentiment_by_movie
    
    def export_sentiment_results(self, output_path):
        """导出情感分析结果到CSV"""
        if not self.sentiment_analyzed or 'sentiment_score' not in self.df.columns:
            self.analyze_batch_sentiments()
        
        # 导出包含情感分数的数据
        export_cols = []
        if 'title' in self.df.columns:
            export_cols.append('title')
        if self.comment_column in self.df.columns:
            export_cols.append(self.comment_column)
        if 'sentiment_score' in self.df.columns:
            export_cols.append('sentiment_score')
        if 'sentiment_label' in self.df.columns:
            export_cols.append('sentiment_label')
        
        if export_cols:
            export_df = self.df[export_cols].dropna(subset=['sentiment_score'])
            export_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✅ 情感分析结果已导出至: {output_path}")
        
        return self.df

