# config.py
import time
import os

# 方舟API KEY
API_KEY = os.getenv("ARK_API_KEY")

# 方舟模型节点
MODEL_NAME = "ep-20250611123221-wnqgm"  # seed 1.6 256K上下文 16K输出 disable reasoning
MODEL_NAME_REASONING = "ep-20250711162541-6znl7"  # seed 1.6 256K上下文 16K输出

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
                        "description": "城市名称，比如北京、上海，默认北京市",
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
    # 创建直播
    {
        "type": "function",
        "function": {
            "name": "create_live",
            "description": "创建直播,需要给入直播的标题、开始时间和结束时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "直播标题"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "直播开始时间，格式为YYYY-MM-DD HH:MM:SS"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "直播结束时间，格式为YYYY-MM-DD HH:MM:SS"
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
                        "description": "通知对象，默认全部班级"
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
    },
    # 查询签到率
    {
        "type": "function",
        "function": {
            "name": "get_attendance_rate",
            "description": "查询某院系在指定时间段内的签到率,单次只能查询一个院系且一个时间段",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "开始日期，格式为YYYY-MM-DD"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期，格式为YYYY-MM-DD"
                    },
                    "department_id": {
                        "type": "string",
                        "description": "院系ID"
                    }
                },
                "required": ["start_date", "end_date", "department_id"]
            }
        }
    },
    # 发布讨论
    {
        "type": "function",
        "function": {
            "name": "publish_discussion",
            "description": "发布讨论，需要给入讨论的标题和内容以及发布对象",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "讨论标题"
                    },
                    "content": {
                        "type": "string",
                        "description": "讨论内容"
                    },
                    "target": {
                        "type": "string",
                        "description": "发布对象，比如某个班级或院系，默认全部班级"
                    }

                },
                "required": ["title", "content","target"]
            }
        }
    },
    # 创建实践任务
    {
        "type": "function",
        "function": {
            "name": "create_practice_task",
            "description": "创建实践任务，需要给入任务的标题、内容、发布对象和截止时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "实践任务标题"
                    },
                    "content": {
                        "type": "string",
                        "description": "实践任务内容"
                    },
                    "target": {
                        "type": "string",
                        "description": "实践任务发布对象，比如某个班级或院系，默认全部班级"
                    },
                    "deadline": {
                        "type": "string",
                        "description": "实践任务截止时间，格式为YYYY-MM-DD HH:MM:SS"
                    }
                },
                "required": ["title", "content","target","deadline"]
            }
        }
    }

]

# ccdx
TOOLS_CCDX = [
    # 获取元件属性
    {
    "type": "function",
    "function": {
        "name": "get_components_property",
        "description": "根据一个或多个元件名称,返回对应元件的属性定义",
        "parameters": {
            "type": "object",
            "properties": {
                "names": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "要查询的元件名称列表，例如 [\"Cell\", \"Lamp\"]"
                }
            },
            "required": ["names"]
        }
    }
}
]