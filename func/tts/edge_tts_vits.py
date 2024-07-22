from func.tools.singleton_mode import singleton
from func.config.default_config import defaultConfig
import subprocess
import edge_tts
import asyncio


@singleton
class EdgeTTs:
    # 加载配置
    config = defaultConfig().get_config()
    speaker_name = config["speech"]["edge-tts"]["speaker_name"]

    def __init__(self):
        pass

    # 生成语音
    async def generate(self, text, voice, filename):
        communicate = edge_tts.Communicate(text=text, voice=voice, rate="+20%", volume="+20%")
        await communicate.save(f"./output/{filename}.mp3")

    # 获取语音
    def get_vists(self, filename, text, emotion):
        asyncio.run(self.generate(text, self.speaker_name, filename))
