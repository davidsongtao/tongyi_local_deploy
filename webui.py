"""
Description: 基于Streamlit和阿里通义大模型API实现推理对话机器人
    
-*- Encoding: UTF-8 -*-
@File     ：webui.py
@Author   ：King Songtao
@Time     ：2024/8/21 上午8:58
@Contact  ：king.songtao@gmail.com
"""
import time

import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.llms import Tongyi
from langchain.chains import ConversationChain


def get_response(prompt, memory, api_key):
    """通过API调用通义大模型"""
    model = Tongyi(
        model="qwen-max",
        api_key=api_key
    )
    chain = ConversationChain(llm=model, memory=memory)
    response = chain.invoke({"input": prompt})
    return response['response']
    # for char in response["response"]:
    #     yield char
    #     time.sleep(0.05)


def generate_res(res):
    """前端实现流式输出效果"""
    for char in res:
        yield char
        time.sleep(0.05)


def validate_api(api_key):
    """验证API-KEY是否合法"""
    try:
        model = Tongyi(
            model='qwen-max',
            api_key=api_key
        )
        st.info("正在验证API-KEY，请不要进行其他操作...")
        model.invoke("test api-key")
        return True
    except Exception as e:
        st.error("您输入的API-KEY有误，请重新检查！")
        return False


# >>> 构建前端页面 <<<
# 侧边导航条
if "api_key" not in st.session_state:
    with st.sidebar:
        api_key = st.text_input("请输入您的API-KEY", type="password")
        st.markdown("[获取通义API-KEY](https://bailian.console.aliyun.com/?apiKey=1#/api-key)")
        submitted = st.button("保存API-KEY")
        if api_key and submitted:
            if validate_api(api_key):
                st.session_state["api_key"] = api_key
                st.success("API-KEY已成功保存！")
        if not api_key and submitted:
            st.info("请输入您的API-KEY再点击保存哦~")

# 处理session_state
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(return_messages=True)
    st.session_state["messages"] = [
        {
            "role": "ai",
            "content": "你好，我是你的AI助手，有什么可以帮你的吗？如果需要对我进行提问，请在左侧输入您的API-KEY，保存后就可以开始对话啦👋"
        }
    ]

# 构建chat_message块儿遍历messages，读取其中所有的消息
for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])

# 下方输入条
prompt = st.chat_input("请输入您要提问的问题...")
if prompt:
    if "api_key" not in st.session_state:
        st.info("请输入您的API-KEY!")
        st.stop()
    user_message = {
        "role": "human",
        "content": prompt
    }

    # 将用户输入添加到会话中，并显示
    st.session_state['messages'].append(user_message)
    st.chat_message("human").write(prompt)

    # 与大模型交互，获取模型推理结果
    with st.spinner("AI正在思考中，请稍等..."):
        response = get_response(prompt, st.session_state["memory"], st.session_state["api_key"])

    # 获取流式输出结果
    stream_res = generate_res(response)

    # 将模型返回的消息放入会话中
    llm_message = {
        "role": "ai",
        "content": response
    }
    st.session_state["messages"].append(llm_message)

    # 前端显示模型推理结果
    st.chat_message("ai").write(stream_res)
