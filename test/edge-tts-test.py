import subprocess
import edge_tts
import asyncio

#合成声音
# subprocess.run(
#             f"edge-tts --voice zh-CN-XiaoxiaoNeural --rate=+20% --text \"君不见黄河之水天上来\" --write-media ./output/1.mp3 2>ok.txt",
#             shell=True,
# )
async def amain():
    communicate = edge_tts.Communicate("君不见黄河之水天上来", "zh-CN-XiaoxiaoNeural")
    await communicate.save("./output/1.mp3")

if __name__ == "__main__":
    asyncio.run(amain())