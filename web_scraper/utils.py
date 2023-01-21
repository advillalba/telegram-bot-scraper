import time
from threading import Timer


def schedule(interval):
    def decorator(func):
        def wrapper_func(*args, **kwargs):
            next_execution = time.time() + interval
            func(*args, **kwargs)
            next_execution -= time.time()
            Timer(next_execution, schedule(interval)(func),
                  args=(*args,), kwargs={**kwargs}).start()

        return wrapper_func

    return decorator
