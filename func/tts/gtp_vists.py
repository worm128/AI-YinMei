from urllib import parse
from func.config.default_config import defaultConfig
import requests
from func.tools.singleton_mode import singleton

@singleton
class GtpVists:
    # 加载配置
    config = defaultConfig().get_config()
    # gpt-SoVITS
    gtp_vists_url = config["speech"]["gpt-sovits"]["gtp_vists_url"]

    def __init__(self):
        pass

    def get_vists(self, filename, text, emotion):
        save_path = f"./output/{filename}.mp3"
        text = parse.quote(text)
        response = requests.get(url=f"{self.gtp_vists_url}/?text={text}&text_language=auto", timeout=(5, 60))
        if response.status_code == 200:
            audio_data = response.content  # 获取音频数据
            with open(save_path, "wb") as file:
                filenum = file.write(audio_data)
                if filenum > 0:
                    return 1
        return 0
