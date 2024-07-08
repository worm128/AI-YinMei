from func.log.default_log import DefaultLog
from func.config.default_config import defaultConfig
import requests
from func.tools.singleton_mode import singleton

@singleton
class Tgw:
    # 设置控制台日志
    log = DefaultLog().getLogger()
    # 加载配置
    config = defaultConfig().get_config()

    tgw_url: str = config["llm"]["tgw_url"]
    history = []

    # text-generation-webui接口调用-LLM回复
    # mode:instruct/chat/chat-instruct  preset:Alpaca/Winlone(自定义)  character:角色卡Rengoku/Ninya
    def chat(self,content, character, mode, preset, username):
        url = f"http://{self.tgw_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        self.history.append({"role": "user", "content": content})
        data = {
            "mode": mode,
            "character": character,
            "your_name": username,
            "messages": self.history,
            "preset": preset,
            "do_sample": True,
            "max_new_tokens": 200,
            "seed": -1,
            "add_bos_token": True,
            "ban_eos_token": False,
            "skip_special_tokens": True,
            "instruction_template": "Alpaca",
        }
        try:
            response = requests.post(
                url, headers=headers, json=data, verify=False, timeout=(5, 60)
            )
        except Exception as e:
            self.log.exception(f"【{content}】信息回复异常")
            return "我听不懂你说什么"
        assistant_message = response.json()["choices"][0]["message"]["content"]
        # history.append({"role": "assistant", "content": assistant_message})
        return assistant_message