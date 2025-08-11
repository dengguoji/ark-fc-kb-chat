# get_attendance_rate
import random
from datetime import datetime, timedelta

def get_attendance_rate(start_date: str, end_date: str, department_id: str) -> float:
    """
    模拟获取某院系在指定时间段内的签到率

    :param start_date: 开始日期 (格式: 'YYYY-MM-DD')
    :param end_date: 结束日期 (格式: 'YYYY-MM-DD')
    :param department_id: 院系ID
    :return: 签到率（0~1之间的浮点数）
    """

    # 解析日期
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta_days = (end - start).days + 1

    total_expected = 0
    total_actual = 0

    # 模拟每天的签到情况
    for day_offset in range(delta_days):
        current_date = start + timedelta(days=day_offset)
        
        # 模拟当天应到人数 (假设每天20~100人之间)
        expected = random.randint(20, 100)
        # 模拟当天实际签到人数 (不超过应到人数)
        actual = random.randint(0, expected)
        
        total_expected += expected
        total_actual += actual

        #print(f"{current_date.date()} 院系[{department_id}]的签到率为: {attendance_rate*100:.2f}%")

    attendance_rate = total_actual / total_expected if total_expected > 0 else 0.0
    result = (f"院系[{department_id}]的签到率为{attendance_rate*100:.2f}%")
    #print(f"总签到率: {attendance_rate*100:.2f}%")
    return result