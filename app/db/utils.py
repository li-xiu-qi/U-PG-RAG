from datetime import datetime

import pytz

CHINA_TZ = pytz.timezone('Asia/Shanghai')


def get_current_time():
    return datetime.now(CHINA_TZ)
