# 知识库功能
from func.log.default_log import DefaultLog
from func.config.default_config import defaultConfig
import time
import requests
from func.tools.singleton_mode import singleton
from func.gobal.data import CommonData

@singleton
class FastGpt:
    # 设置控制台日志
    log = DefaultLog().getLogger()
    # 加载配置
    config = defaultConfig().get_config()
    commonData = CommonData()

    # ai吟美【怒怼版】：fastgpt-5StPybD20P3Ymg2EDZpXe4nCjiP070TINQDRJTgBBWQhMLxDUck6W6Oeio4sx
    # ai吟美【女仆版】：fastgpt-yjuDaV7O4kyzK1DY7PuOGvOjqUJCSmdCENKowhDSAi6PwdoG4247bs2yL
    # openku-chatgpt3.5：fastgpt-ySHfeoltpvRV4lyqvGBqiUvJpzMiC0d3nOFaheT1dTHlk9KA4EHR6EujKzX
    fastgpt_url: str = config["llm"]["fastgpt"]["fastgpt_url"]
    fastgpt_authorization: str = config["llm"]["fastgpt"]["fastgpt_authorization"]
    chat_version: str = config["llm"]["chat_version"]

    # fastgpt知识库接口调用-LLM回复
    def chat(self,content, uid, username, character, relation):
        #url = f"{self.fastgpt_url}/api/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": self.fastgpt_authorization}
        #now = time.strftime("%Y%m%d", time.localtime())
        data = {
            "chatId": self.chat_version + uid,
            "stream": True,
            "detail": False,
            "variables": {"uid": uid, "username": username, "character":character, "relation":relation, "Ai_Name":self.commonData.Ai_Name},
            "messages": [{"content": content, "role": "user"}]
        }
        self.log.info(headers)
        self.log.info(data)
        response = None
        try:
            response = requests.post(
                self.fastgpt_url, headers=headers, json=data, verify=False, timeout=(20, 120), stream=True
            )
        except Exception as e:
            self.log.exception(f"【{content}】信息回复异常")
            return "我听不懂你说什么"

        return response