import time
import hashlib
import requests
import urllib.parse

APP_ID = ""
APP_KEY = ""
ROBOT_ID = ""
ENDPOINT = ""

# 设定参数
score_threshold = 0.4  # 设定分数阈值
top_n = 5  # 设定返回的结果数量

def query_kb(kb_id: str, question: str) -> str:
    timestamp = str(int(time.time() * 1000))
    params = {
        "appId": APP_ID,
        "question": question,
        "robotId": ROBOT_ID,
        "timestamp": timestamp,
        "topK": 5,  # 返回前10个结果
    }

    # 按 ASCII 排序并拼接 param=value
    sorted_items = sorted(params.items())
    param_string = "".join([f"{k}={v}" for k, v in sorted_items])
    signature_raw = param_string + APP_KEY
    signature = hashlib.md5(signature_raw.encode('utf-8')).hexdigest()

    # 请求
    headers = {
        "Content-Type": "application/json",
        "signature": signature
    }

    # 确保处理的是字典类型
    try:
        response = requests.get(ENDPOINT, headers=headers, params=params, timeout=10)
        response.raise_for_status()      
        data = response.json()
        if not isinstance(data, dict):
            print("[QueryKB 错误] 返回数据格式异常：非 JSON 对象")
            return ""
        # 确保嵌套结构存在
        inner_data = data.get("data", {}).get("data", [])    
        results = []
        for item in inner_data:
            results.append({
                "content": item.get("pageContent", ""),
                "score": item.get("metadata", {}).get("score", 0)
            })

        # 过滤并排序
        #results = [r for r in results if r["score"] >= score_threshold]  
        #results.sort(key=lambda x: x["score"], reverse=True) # 按照分数降序排序
        #results = results[:top_n]  # 取前 top_n 个结果

        # 拼接为 section n 格式字符串
        sectioned = []
        for i, r in enumerate(results, 1):
            sectioned.append(f"section {i} start:\n{r['content']}\nsection {i} ends.")
        return results
        #return "\n".join(sectioned)
    except Exception as e:
        print(f"[QueryKB 错误] {e}")
        return results
    
def main():
    kb_id = "1"  # 假设的知识库ID
    question = "现代密码学"
    result = query_kb(kb_id, question)
    if result:
        print("查询结果：")
        print(result)
    else:
        print("未找到相关内容。")

if __name__ == "__main__":
    main()