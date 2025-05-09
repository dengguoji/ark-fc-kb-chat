import datetime
# 实际返回时间
def get_current_time(city):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{city}当前时间：{now}"