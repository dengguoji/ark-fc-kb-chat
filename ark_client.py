# ark_client.py

from volcenginesdkarkruntime import Ark
import config

# 初始化Ark客户端
client = Ark(api_key=config.API_KEY)

# chat
def stream_chat(messages):
    """发起一次带流式输出的对话"""
    stream = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=messages,
        tools=config.TOOLS,
        stream=True,
    )
    return stream

# judge_kb
def unstream_judge(messages):
    """发起一次带流式输出的对话"""
    judge_result = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=messages,
        #tools=config.TOOLS,
        #stream=True,
    )
    return judge_result.choices[0].message.content

