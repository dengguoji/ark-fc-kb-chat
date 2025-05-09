"""
tool_executor.py

职责：
- 动态加载 tools/ 文件夹下各个函数模块。
- 依据 tool_registry.py 的注册配置，匹配模型返回的函数名，调用本地实际函数。
"""

import json
from tool_registry import FUNCTION_REGISTRY

def execute_function_call(tool_call):
    """
    根据模型返回的单个 tool_call 执行本地函数。
    """
    function_name = tool_call["function"]["name"]
    arguments_str = tool_call["function"]["arguments"]

    try:
        arguments = json.loads(arguments_str)
    except Exception as e:
        return f"函数参数解析失败: {e}"

    func = FUNCTION_REGISTRY.get(function_name)

    if not func:
        return f"未找到对应的本地函数：{function_name}"

    try:
        result = func(**arguments)
        return result
    except Exception as e:
        return f"函数调用失败: {e}"