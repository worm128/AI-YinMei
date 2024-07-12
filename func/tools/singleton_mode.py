import threading

# 单实例
def singleton(cls):
    single_lock = threading.Lock()
    instances = {}
    def getInstance(*args, **kwargs):
        if cls not in instances:
            with single_lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    def delInstance():
        del instances[cls]
    getInstance.delInstance = delInstance
    return getInstance