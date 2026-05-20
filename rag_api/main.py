from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import chromadb
from openai import OpenAI
from sse_starlette.sse import EventSourceResponse 

app = FastAPI(title="豆瓣电影高阶 RAG 服务")

# 1. 配置跨域，允许前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化客户端
client = OpenAI(
    api_key="", 
    base_url="https://api.siliconflow.cn/v1"
)
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_collection(name="douban_movies")

# 2. 定义更复杂的数据模型：包含历史对话
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: List[Message] = []  

def get_embedding(text):
    response = client.embeddings.create(
        input=text, model="BAAI/bge-m3"
    )
    return response.data[0].embedding

@app.post("/chat_stream")
async def chat_stream_endpoint(request: ChatRequest):
    """支持上下文记忆与流式输出的接口"""
    user_query = request.query
    
    # RAG 检索
    query_vector = get_embedding(user_query)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=4  
    )
    context = "\n\n".join(results['documents'][0])
    
    # 组装系统提示词
    system_prompt = f"""你是一个懂电影的资深影迷助手。
    请结合以下(本地数据库资料)以及用户的(历史对话)来回答问题。
    回答要有温度，像朋友聊天一样，可以引用短评中的金句。
    
    (本地数据库资料)：
    {context}
    """
    
    # 组装完整的对话上下文（System + History + Current Query）
    messages = [{"role": "system", "content": system_prompt}]
    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_query})

    # 定义生成器，实现流式推流
    async def generate():
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", 
            messages=messages,
            stream=True 
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                # 按照 Server-Sent Events (SSE) 格式发送
                yield chunk.choices[0].delta.content

    return EventSourceResponse(generate())
