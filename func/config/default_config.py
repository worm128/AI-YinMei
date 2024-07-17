from func.config.config_base import ConfigBase
from func.tools.singleton_mode import singleton

@singleton
class defaultConfig:
    def __init__(self):
        # 加载配置
        self.config = ConfigBase("config.yml", "utf-8").get_config()

    def get_config(self):
        return self.config