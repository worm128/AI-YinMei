import re
from duckduckgo_search import DDGS
from func.config.config_init import configInit
import datetime
from func.log.logger import Logger

class DuckduckgoTranslate:
    # 加载配置
    config = configInit("config-prod.yml", "utf-8").get_config()

    # 设置日志
    today = datetime.date.today().strftime("%Y-%m-%d")
    log = Logger(f"./logs/log_{today}.txt", "utf-8", "bilibili-live").getLogger()

    duckduckgo_proxies = config["proxies"]["DuckduckgoProxies"]

    # 翻译
    @staticmethod
    def translate(self, text, from_lanuage, to_lanuage):
        with DDGS(proxies=self.duckduckgo_proxies, timeout=20) as ddgs:
            try:
                r = ddgs.translate(text, from_=from_lanuage, to=to_lanuage)
                self.log.info(f"翻译：{r}")
                return r
            except Exception as e:
                self.log.info(f"translate信息回复异常{e}")
            return text
