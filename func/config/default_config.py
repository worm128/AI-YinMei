from func.config.config_base import ConfigBase

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

@singleton
class defaultConfig:
    def __init__(self):
        # 加载配置
        self.config = ConfigBase("config-prod.yml", "utf-8").get_config()

    def get_config(self):
        return self.config