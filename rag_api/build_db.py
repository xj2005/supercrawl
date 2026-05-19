import pymysql
import chromadb
from openai import OpenAI

# 初始化大模型客户端 
client = OpenAI(
    api_key="sk-lorfgihajdxnclstjuujdkkkhxfjsvbsvkqcylhukgvagqaz", 
    base_url="https://api.siliconflow.cn/v1"
)

# 初始化本地 Chroma 向量数据库
chroma_client = chromadb.PersistentClient(path="./chroma_data")
# 创建或获取一个名为 douban_movies 的集合
collection = chroma_client.get_or_create_collection(name="douban_movies")

def get_embedding(text):
    """调用 API 获取文本向量"""
    response = client.embeddings.create(
        input=text,
        model="BAAI/bge-m3" 
    )
    return response.data[0].embedding

def build_vector_db():
    print("正在连接 MySQL 获取数据...")
    db = pymysql.connect(host='127.0.0.1', user='root', password='xj123456', database='movie', charset='utf8mb4')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    
    # 提取电影的中文名、简介和热门短评作为 RAG 的知识库
    cursor.execute("SELECT id, title_cn, genre, quote, hot_comments FROM douban_top250")
    movies = cursor.fetchall()
    
    print(f"共获取到 {len(movies)} 部电影，开始向量化入库...")
    
    for i, movie in enumerate(movies):
        # 将结构化与非结构化数据融合成一段富文本语料
        content = f"电影《{movie['title_cn']}》，类型：{movie['genre']}。简介：{movie['quote']}。影迷热门评价：{movie['hot_comments']}"
        
        # 获取向量
        vector = get_embedding(content)
        
        # 存入 ChromaDB
        collection.add(
            ids=[str(movie['id'])],
            embeddings=[vector],
            documents=[content],
            metadatas=[{"title": movie['title_cn']}]
        )
        print(f"已入库: {movie['title_cn']} ({i+1}/{len(movies)})")

    db.close()
    print("本地向量知识库构建完成！")

if __name__ == "__main__":
    build_vector_db()