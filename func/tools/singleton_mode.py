def singleton(cls):
    instances = {}
    def getInstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    def delInstance():
        del instances[cls]
    getInstance.delInstance = delInstance
    return getInstance