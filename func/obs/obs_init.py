from func.log.default_log import DefaultLog
from func.config.default_config import defaultConfig
from func.obs.obs_websocket import ObsWebSocket, VideoStatus, VideoControl
from func.tools.singleton_mode import singleton

@singleton
class ObsInit:
    # 设置控制台日志
    log = DefaultLog().getLogger()
    # 加载配置
    config = defaultConfig().get_config()

    def __init__(self):
        self.obs = ObsWebSocket(
            host=self.config["obs"]["url"],
            port=self.config["obs"]["port"],
            password=self.config["obs"]["password"],
            switch=self.config["obs"]["switch"],
        )
        self.obs.connect()

    def get_ws(self):
        return self.obs