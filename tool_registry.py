from tools.get_attendance_rate import get_attendance_rate
from tools.weather import get_weather
from tools.time import get_current_time
from tools.create_live import create_live
from tools.notice import notice
from tools.publish_discussion import publish_discussion
from tools.create_practice_task import create_practice_task
from tools.get_components_property import get_components_property


FUNCTION_REGISTRY = {
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "create_live": create_live,
    "notice": notice,
    "get_attendance_rate":get_attendance_rate,
    "publish_discussion": publish_discussion,
    "create_practice_task": create_practice_task,
    "get_components_property": get_components_property
}