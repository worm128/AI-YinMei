from duckduckgo_search import DDGS
from func.log.default_log import DefaultLog
from func.tools.singleton_mode import singleton

@singleton
class DuckduckgoWebsearch:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    def __init__(self):
        pass

    def duckduckgo_web_search(self,query,textSearchNum):
        content = ""
        with DDGS(proxies=self.duckduckgo_proxies, timeout=20) as ddgs:
            try:
                ddgs_text_gen = ddgs.text(
                    query,
                    region="cn-zh",
                    timelimit="d",
                    backend="api",
                    max_results=textSearchNum,
                )
                for r in ddgs_text_gen:
                    content = r["body"] + ";" + content
            except Exception as e:
                self.log.exception(f"web_search信息回复异常：")
                #logging.error(traceback.format_exc())
        return content
