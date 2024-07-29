from func.config.default_config import defaultConfig
from func.tools.singleton_mode import singleton
import requests
from urllib import parse

@singleton
class BertVis2:
    # 加载配置
    config = defaultConfig().get_config()

    # bert-vists
    bert_vists_url = config["speech"]["bert-vists"]["bert_vists_url"]
    speaker_name = config["speech"]["bert-vists"]["speaker_name"]
    sdp_ratio = config["speech"]["bert-vists"]["sdp_ratio"]  # SDP在合成时的占比，理论上此比率越高，合成的语音语调方差越大
    noise = config["speech"]["bert-vists"]["noise"]  # 控制感情变化程度，默认0.2
    noisew = config["speech"]["bert-vists"]["noisew"]  # 控制音节发音变化程度，默认0.9
    speed = config["speech"]["bert-vists"]["speed"]  # 语速

    def __init__(self):
        pass

    """
    bert-vits2语音合成
    filename：音频文件名
    text：说话文本
    emotion：情感描述
    """
    def get_vists(self, filename, text, emotion):
        save_path = f"./output/{filename}.mp3"
        text = parse.quote(text)
        response = requests.get(
            url=f"{self.bert_vists_url}/voice?text={text}&model_id=0&speaker_name={self.speaker_name}&sdp_ratio={self.sdp_ratio}&noise={self.noise}&noisew={self.noisew}&length={self.speed}&language=AUTO&auto_translate=false&auto_split=true&emotion={emotion}",
            timeout=(5, 60),
        )
        if response.status_code == 200:
            audio_data = response.content  # 获取音频数据
            with open(save_path, "wb") as file:
                filenum = file.write(audio_data)
                if filenum > 0:
                    return 1
        return 0
