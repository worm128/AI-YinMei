from func.tools.singleton_mode import singleton
import subprocess
import edge_tts
import asyncio


@singleton
class EdgeTTs:

    def __init__(self):
        pass

    async def generate(self, text, voice, filename):
        communicate = edge_tts.Communicate(text=text, voice=voice, rate="+20%", volume="+20%")
        await communicate.save(f"./output/{filename}.mp3")

    def get_vists(self, filename, text, emotion):
        asyncio.run(self.generate(text, "zh-CN-XiaoxiaoNeural", filename))
