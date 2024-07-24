import os
from func.log.default_log import DefaultLog
from func.vtuber.emote_oper import EmoteOper
from func.obs.obs_init import ObsInit
from func.tools.string_util import StringUtil
from func.tools.singleton_mode import singleton
from func.gobal.data import LLmData
from func.gobal.data import SingData
from func.gobal.data import TTsData
from func.gobal.data import DanceData
from func.gobal.data import SearchData
from func.gobal.data import ImageData
from func.gobal.data import DrawData

@singleton
class CmdCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    llmData = LLmData()  # llm数据
    singData = SingData()  # 唱歌数据
    ttsData = TTsData()  # 语音数据
    danceData = DanceData()  # 跳舞数据
    searchData = SearchData()  # 搜索数据
    imageData = ImageData()  # 搜图数据
    drawData = DrawData()  # 绘画数据

    # 表情
    emoteOper = EmoteOper()

    def __init__(self):
        self.obs = ObsInit().get_ws()

    # 命令控制：优先
    def cmd(self,traceid, query, uid, user_name):
        # 停止所有任务
        if query == "\\stop":
            self.singData.is_singing = 2  # 1.唱歌中 2.唱歌完成
            # is_creating_song = 2  # 1.生成中 2.生成完毕
            self.searchData.is_SearchText = 2  # 1.搜索中 2.搜索完毕
            self.imageData.is_SearchImg = 2  # 1.搜图中 2.搜图完成
            self.drawData.is_drawing = 3  # 1.绘画中 2.绘画完成 3.绘图任务结束
            self.llmData.is_ai_ready = True  # 定义ai回复是否转换完成标志
            self.ttsData.is_tts_ready = True  # 定义语音是否生成完成标志
            os.system("taskkill /T /F /IM song.exe")
            os.system("taskkill /T /F /IM accompany.exe")
            os.system("taskkill /T /F /IM mpv.exe")
            self.log.info(f"[{traceid}][{user_name}]执行命令：{query}")
            return True
        if query == "\\dance":
            os.system("taskkill /T /F /IM song.exe")
            os.system("taskkill /T /F /IM accompany.exe")
            os.system("taskkill /T /F /IM mpv.exe")
            self.log.info(f"[{traceid}][{user_name}]执行命令：{query}")
            return True
        # 下一首歌
        text = ["\\next", "下一首", "下首", "切歌", "next"]
        is_contain = StringUtil.has_string_reg_list(f"^{text}", query)
        if is_contain is not None:
            os.system("taskkill /T /F /IM song.exe")
            os.system("taskkill /T /F /IM accompany.exe")
            self.singData.is_singing = 2  # 1.唱歌中 2.唱歌完成
            self.log.info(f"[{traceid}][{user_name}]执行命令：{query}")
            return True
        # 停止学歌
        text = ["停止学歌"]
        is_contain = StringUtil.has_string_reg_list(f"^{text}", query)
        if is_contain is not None:
            self.singData.is_creating_song = 2  # 1.生成中 2.生成完毕
            self.log.info(f"[{traceid}][{user_name}]执行命令：{query}")
            return True
        # 停止跳舞
        text = ["\\停止跳舞", "停止跳舞", "不要跳舞", "stop dance"]
        is_contain = StringUtil.has_string_reg_list(f"^{text}", query)
        if is_contain is not None:
            self.danceData.is_dance = 2  # 1.正在跳舞 2.跳舞完成
            self.log.info(f"[{traceid}][{user_name}]执行命令：{query}")
            return True
        return False