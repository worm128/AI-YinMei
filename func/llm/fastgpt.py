from func.log.default_log import DefaultLog
from func.config.default_config import defaultConfig
import time
import requests
from func.tools.singleton_mode import singleton

@singleton
class FastGpt:
    # 设置控制台日志
    log = DefaultLog().getLogger()
    # 加载配置
    config = defaultConfig().get_config()

    # ai吟美【怒怼版】：fastgpt-5StPybD20P3Ymg2EDZpXe4nCjiP070TINQDRJTgBBWQhMLxDUck6W6Oeio4sx
    # ai吟美【女仆版】：fastgpt-yjuDaV7O4kyzK1DY7PuOGvOjqUJCSmdCENKowhDSAi6PwdoG4247bs2yL
    # openku-chatgpt3.5：fastgpt-ySHfeoltpvRV4lyqvGBqiUvJpzMiC0d3nOFaheT1dTHlk9KA4EHR6EujKzX
    fastgpt_url: str = config["llm"]["fastgpt_url"]
    fastgpt_authorization: str = config["llm"]["fastgpt_authorization"]

    # fastgpt知识库接口调用-LLM回复
    def chat(self,content, uid, username, authorization):
        url = f"http://{self.fastgpt_url}/api/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": authorization}
        timestamp = int(time.time())
        data = {
            "chatId": timestamp,
            "stream": True,
            "detail": False,
            "variables": {"uid": uid, "name": username},
            "messages": [{"content": content, "role": "user"}]
        }
        response = None
        try:
            response = requests.post(
                url, headers=headers, json=data, verify=False, timeout=(5, 60), stream=True
            )
        except Exception as e:
            self.log.exception(f"【{content}】信息回复异常")
            return "我听不懂你说什么"

        return response