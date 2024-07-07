import subprocess
from func.tools.singleton_mode import singleton

@singleton
class MpvPlay:
     def __init__(self):
         pass

     # 播放器播放
     def mpv_play(self, mpv_name, song_path, volume, start):
         # end：播放多少秒结束  volume：音量，最大100，最小0
         subprocess.run(
             f'{mpv_name} -vo null --volume={volume} --start={start} "{song_path}" 1>nul',
             shell=True,
         )