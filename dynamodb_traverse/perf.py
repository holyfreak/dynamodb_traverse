
from datetime import datetime


def profile(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print(end - start)
    return wrapper


def time_in_millis(dt):
    return int((dt - datetime.utcfromtimestamp(0)).total_seconds() * 1000)


def now_in_milli():
    return time_in_millis(datetime.utcnow())
