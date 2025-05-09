# config.py
import time
import os

# API KEY
API_KEY = os.getenv("ARK_API_KEY")

# 模型接入点
MODEL_NAME = ""  # doubao-1.5-pro-32k

# Function Call的tools定义
TOOLS = [
    # 获取天气
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，比如北京、上海",
                    }
                },
                "required": ["city"],
            }
        }
    }
    ,
    # 获取当前时间
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称（全球范围，例如 New York、London、Beijing）"
                    }
                },
                "required": ["city"]
            }
        }
    }
    ,
    # 创建会议
    {
        "type": "function",
        "function": {
            "name": "meeting",
            "description": "创建直播,需要给入直播的标题、开始时间和结束时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "会议标题"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "会议开始时间，格式为YYYY-MM-DD HH:MM:SS"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "会议结束时间，格式为YYYY-MM-DD HH:MM:SS"
                    }
                },
                "required": ["title", "start_time", "end_time"]
            }
        }
    }
    ,
    # 发布通知
    {
        "type": "function",
        "function": {
            "name": "notice",
            "description": "发布通知，需要给入通知的对象、标题和内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "object": {
                        "type": "string",
                        "description": "通知对象"
                    },
                    "title": {
                        "type": "string",
                        "description": "通知标题"
                    },
                    "content": {
                        "type": "string",
                        "description": "通知内容"
                    }
                },
                "required": ["object","title", "content"]
            }
        }
    }
]