from volcenginesdkarkruntime import Ark
import config

# 初始化Ark客户端
client = Ark(api_key=config.API_KEY)

# 普通模型流式对话
def stream_chat(messages, enable_tools=True):
    if enable_tools:
        stream = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            tools=config.TOOLS,
            stream=True,
            extra_body={
            "thinking": {
                "type": "disabled"
            }
        }
        )
    else:
        stream = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            stream=True,
            extra_body={
            "thinking": {
                "type": "disabled"
            }
        }   
        )
    return stream

# 深度思考流式对话
def stream_chat_reasoning(messages, enable_tools=True):
    if enable_tools:
        stream = client.chat.completions.create(
            model=config.MODEL_NAME_REASONING,
            messages=messages,
            tools=config.TOOLS,
            stream=True,     
        )
    else:
        stream = client.chat.completions.create(
            model=config.MODEL_NAME_REASONING,
            messages=messages,
            stream=True,     
        )
    return stream

# 知识库判定+问题改写 (非streaming)
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "kb_matching_output",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "matches": {
                    "type": "array",
                    "description": "匹配到的知识库与其改写问题的集合",
                    "items": {
                        "type": "object",
                        "properties": {
                            "knowledge_id": {
                                "type": "string",
                                "description": "匹配的知识库 ID"
                            },
                            "rewritten_queries": {
                                "type": "array",
                                "description": "该知识库对应的多个改写查询",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": ["knowledge_id", "rewritten_queries"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["matches"],
            "additionalProperties": False
        }
    }
}

# 知识库定位、查询改写
def unstream_judge(messages):
    judge_result = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=messages,
        response_format=response_format,
        extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
    )
    return judge_result.choices[0].message.content