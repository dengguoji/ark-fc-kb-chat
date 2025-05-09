from tools.weather import get_weather
from tools.time import get_current_time
from tools.meeting import meeting
from tools.notice import notice

FUNCTION_REGISTRY = {
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "meeting": meeting,
    "notice": notice
}