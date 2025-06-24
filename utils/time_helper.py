from datetime import datetime

def get_current_time_info():
    now = datetime.now()
    return {
        "datetime": now,
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "weekday": now.strftime("%A"),  # "Monday" など
        "hour": now.hour,
        "season": get_season(now.month),
    }

def get_season(month):
    if month in [12, 1, 2]:
        return "冬"
    elif month in [3, 4, 5]:
        return "春"
    elif month in [6, 7, 8]:
        return "夏"
    else:
        return "秋"
