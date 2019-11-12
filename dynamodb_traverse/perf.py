
from datetime import datetime


def profile(func):
    """profiling a function"""
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print(end - start)
    return wrapper


def time_in_millis(dt):
    """convert a datetime into utc milliseconds"""
    return int((dt - datetime.utcfromtimestamp(0)).total_seconds() * 1000)


def now_in_milli():
    """return now in utc milliseconds"""
    return time_in_millis(datetime.utcnow())
