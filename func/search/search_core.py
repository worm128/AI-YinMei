from func.config.default_config import defaultConfig
from func.log.default_log import DefaultLog
from func.tools.singleton_mode import singleton
from func.gobal.data import SearchData
from func.gobal.data import LLmData
from func.search.baidu_websearch import BaiduWebsearch
from func.tools.string_util import StringUtil

@singleton
class SearchCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()
    # 加载配置
    config = defaultConfig().get_config()

    searchData = SearchData()  #搜索数据
    llmData = LLmData()  # llm数据

    baiduWebsearch = BaiduWebsearch()

    def __init__(self):
        pass

    # 搜文任务
    def check_text_search(self):
        if not self.searchData.SearchTextList.empty() and self.searchData.is_SearchText == 2:
            self.searchData.is_SearchText = 1
            text_search_json = self.searchData.SearchTextList.get()
            prompt = text_search_json["prompt"]
            uid = text_search_json["uid"]
            username = text_search_json["username"]
            traceid = text_search_json["traceid"]
            # 搜索引擎搜索
            searchStr = self.baidu_web_search(prompt)
            # llm模型处理
            llm_prompt = f'[{traceid}]帮我在答案"{searchStr}"中提取"{prompt}"的信息'
            self.log.info(f"[{traceid}]重置提问:{llm_prompt}")
            # 询问LLM
            llm_json = {
                "traceid": traceid,
                "query": prompt,
                "prompt": llm_prompt,
                "uid": uid,
                "username": username,
            }
            self.llmData.QuestionList.put(llm_json)

            self.searchData.is_SearchText = 2  # 搜文完成

    # baidu搜索引擎搜索
    def baidu_web_search(self, query):
        content = ""
        results = self.baiduWebsearch.search(query, num_results=3, debug=0)
        if isinstance(results, list):
            self.log.info("search results：(total[{}]items.)".format(len(results)))
            for res in results:
                content = (res["abstract"].replace("\n", "").replace("\r", "") + ";" + content)
        return content

    # 搜索引擎查询
    def msg_deal(self, traceid, query, uid, user_name):
        text = ["查询", "查一下", "搜索"]
        is_contain = StringUtil.has_string_reg_list(f"^{text}", query)
        if is_contain is not None:
            num = StringUtil.is_index_contain_string(text, query)
            queryExtract = query[num: len(query)]  # 提取提问语句
            queryExtract = queryExtract.strip()
            self.log.info(f"[{traceid}]搜索词：" + queryExtract)
            if queryExtract == "":
                return True
            text_search_json = {"traceid": traceid, "prompt": queryExtract, "uid": uid, "username": user_name}
            self.searchData.SearchTextList.put(text_search_json)
            return True
        return False