import pandas as pd
import re

class DataCleaner:
    """数据清洗类"""
    
    def __init__(self, input_path, output_path=None):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None
        # 中文到英文的列名映射
        self.column_mapping = {
            '中文标题': 'title',
            '评分': 'rating',
            '评价人数': 'rating_people',
            '类型': 'genre',
            '导演/主演': 'director',
            '年份': 'year',
            '热门短评': 'comment',
            '排名': 'rank',
            '外文标题': 'foreign_title',
            '简介': 'summary',
            '详情链接': 'url',
            '片长': 'duration',
            'IMDb': 'imdb_id'
        }
        
    def load_data(self):
        """加载数据并映射列名"""
        self.df = pd.read_csv(self.input_path)
        print(f"原始数据形状: {self.df.shape}")
        print(f"原始列名: {self.df.columns.tolist()}")
        
        # 重命名列
        self.rename_columns()
        
        print(f"映射后列名: {self.df.columns.tolist()}")
        return self.df
    
    def rename_columns(self):
        """将中文列名映射为英文列名"""
        rename_dict = {old: new for old, new in self.column_mapping.items() 
                      if old in self.df.columns}
        if rename_dict:
            self.df = self.df.rename(columns=rename_dict)
            print(f"已映射列: {rename_dict}")
        else:
            print("警告: 没有找到可映射的列名")
        return self.df
    
    def check_missing_values(self):
        """检查缺失值"""
        missing = self.df.isnull().sum()
        missing_percent = (missing / len(self.df)) * 100
        missing_df = pd.DataFrame({
            '缺失数量': missing, 
            '缺失百分比': missing_percent
        })
        print("缺失值统计:\n", missing_df[missing_df['缺失数量'] > 0])
        return missing_df
    
    def handle_missing_values(self, strategy='drop'):
        """处理缺失值"""
        if strategy == 'drop':
            # 只删除关键列缺失的行
            essential_cols = ['title', 'rating']
            existing_essential = [col for col in essential_cols if col in self.df.columns]
            if existing_essential:
                before = len(self.df)
                self.df = self.df.dropna(subset=existing_essential)
                print(f"删除关键列缺失值后: {before} -> {len(self.df)} 行")
            else:
                self.df = self.df.dropna()
        elif strategy == 'fill_zero':
            self.df = self.df.fillna(0)
        elif strategy == 'fill_mean':
            numeric_cols = self.df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                self.df[col] = self.df[col].fillna(self.df[col].mean())
        elif strategy == 'fill_forward':
            self.df = self.df.fillna(method='ffill')
        
        print(f"处理缺失值后数据形状: {self.df.shape}")
        return self.df
    
    def remove_duplicates(self, subset=None):
        """删除重复值"""
        before = len(self.df)
        if subset and subset in self.df.columns:
            self.df = self.df.drop_duplicates(subset=subset)
        else:
            self.df = self.df.drop_duplicates()
        print(f"删除重复行: {before} -> {len(self.df)} (删除了 {before - len(self.df)} 行)")
        return self.df
    
    def convert_types(self):
        """数据类型转换"""
        # 评分转浮点数
        if 'rating' in self.df.columns:
            self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce')
            
        # 评价人数转整数
        if 'rating_people' in self.df.columns:
            if self.df['rating_people'].dtype == 'object':
                self.df['rating_people'] = (
                    self.df['rating_people']
                    .astype(str)
                    .str.replace(',', '')
                    .str.extract(r'(\d+)')[0]
                )
            self.df['rating_people'] = pd.to_numeric(self.df['rating_people'], errors='coerce').fillna(0).astype(int)
            
        # 年份转整数
        if 'year' in self.df.columns:
            self.df['year'] = pd.to_numeric(self.df['year'], errors='coerce')
            
        print("数据类型转换完成")
        print(self.df.dtypes)
        return self.df
    
    def extract_genres(self):
        """处理类型字段"""
        if 'genre' in self.df.columns:
            self.df['genre'] = self.df['genre'].fillna('未知')
        return self.df
    
    def clean_text_fields(self):
        """文本字段清洗"""
        if 'comment' in self.df.columns:
            self.df['comment'] = (
                self.df['comment']
                .fillna('')
                .astype(str)
                .str.strip()
                .str.replace('\n', ' ')
                .str.replace('\r', ' ')
                .str.replace(r'\s+', ' ', regex=True)
            )
        return self.df
    
    def save_cleaned_data(self):
        """保存清洗后的数据"""
        if self.output_path and len(self.df) > 0:
            self.df.to_csv(self.output_path, index=False, encoding='utf-8-sig')
            print(f"清洗后的数据已保存至: {self.output_path}")
        elif len(self.df) == 0:
            print("警告: 清洗后无数据，未保存文件")
        return self.df
    
    def run_full_cleaning(self, missing_strategy='fill_zero'):  # 改为 fill_zero
        """运行完整的数据清洗流程"""
        self.load_data()
        self.check_missing_values()
        self.handle_missing_values(strategy=missing_strategy)
        self.remove_duplicates(subset='title')  # 根据标题去重
        self.convert_types()
        self.extract_genres()
        self.clean_text_fields()
        self.save_cleaned_data()
        return self.df