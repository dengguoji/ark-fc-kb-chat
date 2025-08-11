# create_practice_task.py

def create_practice_task(title: str, content: str, target: str, deadline: str) -> str:
    """
    创建实践任务，需要给入任务的标题、内容、发布对象和截止时间

    :param title: 实践任务标题
    :param content: 实践任务内容
    :param target: 发布对象（如院系、班级等）
    :param deadline: 实践任务截止时间，格式为YYYY-MM-DD HH:MM:SS
    :return: 创建结果信息
    """
    
    # 模拟创建实践任务的逻辑
    result = f"已创建实践任务：\n标题：{title}\n内容：{content}\n发布对象：{target}\n截止时间：{deadline}"
    
    return result