from ark_client import unstream_judge  # 使用judge_kb
from prompts import  JUDGE_KB_PROMPT

def judge_need_kb(messages: list) -> str:
    """
    调用判断模型，决定是否需要使用知识库。
    返回知识库ID（如 "class_kb_01"），如果不需要则返回 "0"
    """
    system_prompt = JUDGE_KB_PROMPT
    filtered_messages = [msg for msg in messages if msg["role"] != "system"] # 过滤主对话的system消息
    model_messages = [{"role": "system", "content": system_prompt}] + filtered_messages # 添加知识库判断系统提示词

    try:
        response = unstream_judge(model_messages)
        return response
    
    except Exception as e:
        print(f"[JudgeKB 错误] {e}")
        return "0"