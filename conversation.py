import ark_client
from tool_executor import execute_function_call
from judge_kb import judge_need_kb
from query_kb import query_kb
from prompts import *

def process_messages(messages):
    stream = ark_client.stream_chat(messages)
    current_assistant_content = ""
    current_reasoning_content = ""
    current_tool_calls = {}

    print("\n\n====== ASSISTANT ======\n", end="", flush=True)

    for chunk in stream:
        if not chunk.choices:
            continue
        choice = chunk.choices[0]
        delta = choice.delta

        # reasoning_content 流式输出
        if hasattr(delta, "reasoning_content") and delta.reasoning_content:
            if current_reasoning_content == "":
                print("\n\n[reasoning_content] ", end="\n", flush=True)
            print(delta.reasoning_content, end="", flush=True)
            current_reasoning_content += delta.reasoning_content

        # content 流式输出
        if getattr(delta, "content", None):
            if current_assistant_content == "":
                print("\n\n[content] ", end="", flush=True)
            print(delta.content, end="", flush=True)
            current_assistant_content += delta.content

        # 工具调用逻辑保持不变
        if delta.tool_calls:
            for tool_call in delta.tool_calls:
                index = tool_call.index
                if index not in current_tool_calls:
                    current_tool_calls[index] = {
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": ""
                        },
                        "type": tool_call.type,
                        "id": tool_call.id
                    }
                current_tool_calls[index]["function"]["arguments"] += tool_call.function.arguments or ""

    # 判断是否有工具调用
    if current_tool_calls:
        tool_calls_list = []
        for call in current_tool_calls.values():
            tool_calls_list.append({
                "id": call["id"],
                "type": call["type"],
                "function": {
                    "name": call["function"]["name"],
                    "arguments": call["function"]["arguments"]
                }
            })

        messages.append({
            "role": "assistant",
            "content": current_assistant_content.strip(),
            "tool_calls": tool_calls_list
        })

        for call in current_tool_calls.values():
            try:
                execution_result = execute_function_call(call)
            except Exception as e:
                execution_result = f"工具执行异常: {str(e)}"
            print(f"\n\n====== TOOL ({call['function']['name']}) ======\n{execution_result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": execution_result
            })

        process_messages(messages)

    else:
        if current_assistant_content.strip():
            messages.append({
                "role": "assistant",
                "content": current_assistant_content.strip()
            })
        print("\n" + "-"*50)
def chat_loop(enable_kb=True):
    messages = [
        {
            "role": "system",
            "content": f"{TIME_PREFIX}\n{MAIN_SYSTEM_PROMPT}\n{MARKDOWN_PROMPT}\n{RULE_KB_PROMPT}",
        },
    ]
    print("欢迎使用终端聊天，输入 Q 或 q 回车可退出。\n")

    while True:
        # 1. 用户输入
        print("\n\n====== USER ======\n", end="", flush=True)
        pure_user_input = input()  # 构造临时消息
        if pure_user_input.strip().lower() == "q":
            print("结束对话。")
            break

        user_input = pure_user_input  # 默认不拼接知识库

        # 2. 可选知识库判断
        if enable_kb:
            temp_messages = messages + [{"role": "user", "content": pure_user_input}] # 构造临时上下文，用于知识库判断
            kb_id = judge_need_kb(temp_messages)
            if kb_id != "0":
                print(f"[知识库触发] 需要使用知识库 {kb_id}")
                kb_content = query_kb(kb_id, pure_user_input)
                if kb_content:
                    # print(f"[知识库内容]:\n{kb_content}")
                    user_input = f"{RECALL_KB_PROMPT_START}\n{kb_content}\n{RECALL_KB_PROMPT_END}\n{pure_user_input}" # 构造结合知识库增强后的用户提示词
                else:
                    print("[知识库内容]: 无相关内容")

        # 记录插入位置
        insert_index = len(messages)

        # 插入增强 user_input（含知识库内容）
        messages.insert(insert_index, {"role": "user", "content": user_input})

        # 执行推理，模型输出的 assistant/tool 会直接写入 messages
        try:
            process_messages(messages)
        except Exception as e:
            print("\n发生错误:", str(e))

        # 删除增强 user_input
        messages.pop(insert_index)

        # 原地插入纯净用户输入，保持历史顺序一致
        messages.insert(insert_index, {"role": "user", "content": pure_user_input})