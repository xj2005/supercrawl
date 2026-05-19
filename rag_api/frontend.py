import streamlit as st
import requests
import json

# 配置页面基础信息
st.set_page_config(page_title="豆瓣 Top250 影迷助手", page_icon="🎬", layout="centered")

st.title("🎬 豆瓣 Top250 影迷小助手")
st.caption("基于本地高维向量数据库与大语言模型构建的 RAG 问答系统")

# 初始化 session_state，用于保存网页刷新期间的对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 将历史对话渲染到界面上
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入框
if prompt := st.chat_input("说出你今天的心情，或者想看的电影类型..."):
    # 1. 把用户的输入上屏
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 准备发给后端 FastAPI 的数据
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 准备 payload
        payload = {
            "query": prompt,
            # 只取最近的4条历史记录，防止上下文过长
            "history": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1][-4:]]
        }

        # try:
        #     # 3. 发送请求给 FastAPI，并接收流式响应
        #     response = requests.post(
        #         "http://127.0.0.1:8000/chat_stream", 
        #         json=payload, 
        #         stream=True
        #     )
            
        #     # 解析流式数据并实现打字机效果
        #     for chunk in response.iter_content(chunk_size=1024):
        #         if chunk:
        #             # 解码 SSE 数据
        #             decoded_chunk = chunk.decode('utf-8')
        #             if decoded_chunk.startswith("data: "):
        #                 text = decoded_chunk.replace("data: ", "")
        #                 full_response += text
        #                 # 实时更新 UI 上的文字
        #                 message_placeholder.markdown(full_response + "▌")
            
        #     # 完成接收，去掉光标
        #     message_placeholder.markdown(full_response)
            
        #     # 将助手的回答也存入历史记录
        #     st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        # except Exception as e:
        #     st.error(f"无法连接到后端服务，请确认 FastAPI 正在运行：{e}")
        try:
            # 3. 发送请求给 FastAPI，并接收流式响应 
            response = requests.post(
                "http://127.0.0.1:8000/chat_stream", 
                json=payload, 
                stream=True
            )
            
            # 改用 iter_lines() 按行读取，自动剥离网络协议自带的换行符
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        # 去掉开头的 "data: " 标识符，剩下的就是纯净的文本
                        text = decoded_line[6:] 
                        full_response += text
                        # 实时更新 UI 上的文字
                        message_placeholder.markdown(full_response + "▌")
            
            # 完成接收，去掉光标
            message_placeholder.markdown(full_response)
            
            # 将助手的回答也存入历史记录
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"无法连接到后端服务，请确认 FastAPI 正在运行：{e}")