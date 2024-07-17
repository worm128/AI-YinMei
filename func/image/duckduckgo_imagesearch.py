from duckduckgo_search import DDGS
from func.config.default_config import defaultConfig
from func.log.default_log import DefaultLog
from func.tools.singleton_mode import singleton
import random

@singleton
class DuckduckgoImagesearch:
    # 设置控制台日志
    log = DefaultLog().getLogger()
    # 加载配置
    config = defaultConfig().get_config()
    duckduckgo_proxies = config["proxies"]["DuckduckgoProxies"]
    # duckduckgo搜索引擎搜索
    textSearchNum = 5

    def __init__(self):
        pass

    # duckduckgo搜索引擎搜图片
    def web_search_img(self,query):
        imageNum = 10
        imgUrl = ""
        with DDGS(proxies=self.duckduckgo_proxies, timeout=20) as ddgs:
            try:
                ddgs_images_gen = ddgs.images(
                    query,
                    region="cn-zh",
                    safesearch="off",
                    size="Medium",
                    color="color",
                    type_image=None,
                    layout=None,
                    license_image=None,
                    max_results=imageNum,
                )
                i = 0
                random_number = random.randrange(0, imageNum)
                for r in ddgs_images_gen:
                    if i == random_number:
                        imgUrl = r["image"]
                        self.log.info(f"图片地址：{imgUrl},搜索关键字:{query}")
                        break
                    i = i + 1
            except Exception as e:
                self.log.exception(f"web_search_img信息回复异常：")
        return imgUrl
