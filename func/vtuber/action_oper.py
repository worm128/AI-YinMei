import threading
from threading import Thread
import time
import random
from func.log.default_log import DefaultLog
from func.vtuber.emote_oper import EmoteOper
from func.obs.obs_init import ObsInit
from func.obs.obs_websocket import ObsWebSocket,VideoStatus,VideoControl
from func.tools.string_util import StringUtil
from func.tools.singleton_mode import singleton
from func.gobal.data import VtuberData
from func.gobal.data import LLmData
from func.gobal.data import SingData
from func.gobal.data import TTsData

@singleton
class ActionOper:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    vtuberData = VtuberData()  # vtuber数据
    llmData = LLmData()  # llm数据
    singData = SingData()  # 唱歌数据
    ttsData = TTsData()  # 语音数据

    # 表情
    emoteOper = EmoteOper()

    def __init__(self):
        self.obs = ObsInit().get_ws()

    def auto_swing(self):
        self.vtuberData.auto_swing_lock.acquire()
        # 触发器-设置开始摇摆: 停止摇摆+（唱歌中 或者 聊天中）= 可以设置摇摆动作
        if self.vtuberData.swing_motion == 2 and (self.singData.is_singing == 1 or self.ttsData.is_tts_ready == False):
            self.log.info(f"进入摇摆状态:{self.vtuberData.swing_motion},{self.singData.is_singing},{self.ttsData.is_tts_ready}")
            self.vtuberData.swing_motion = 1
        else:
            self.vtuberData.auto_swing_lock.release()
            return
        # 监听停止摇摆线程
        stop_emote_thread = Thread(target=self.stop_motion)
        stop_emote_thread.start()
        self.vtuberData.auto_swing_lock.release()

        # 执行器-循环摇摆：唱歌中 或者 说话中 都会摇摆
        while self.vtuberData.swing_motion == 1 and (self.singData.is_singing == 1 or self.ttsData.is_tts_ready == False):
            jsonstr = []
            jsonstr.append({"content": "happy", "key": "摇摆1", "num": 1, "timesleep": 0, "donum": 0, "endwait": 24})
            jsonstr.append({"content": "happy", "key": "摇摆2", "num": 1, "timesleep": 0, "donum": 0, "endwait": 21})
            jsonstr.append({"content": "happy", "key": "摇摆3", "num": 1, "timesleep": 0, "donum": 0, "endwait": 30})
            jsonstr.append({"content": "happy", "key": "摇摆4", "num": 1, "timesleep": 0, "donum": 0, "endwait": 19})
            jsonstr.append({"content": "happy", "key": "摇摆5", "num": 1, "timesleep": 0, "donum": 0, "endwait": 30})
            jsonstr.append({"content": "happy", "key": "摇摆6", "num": 1, "timesleep": 0, "donum": 0, "endwait": 30})
            # 随机一个【摇摆动作】
            num = random.randrange(0, len(jsonstr))
            emote_show_json = []
            emote_show_json.append(jsonstr[num])
            # 执行【摇摆动作】
            self.log.info(f"执行摇摆：{emote_show_json}")
            emote_show_thread = Thread(target=self.emoteOper.emote_show, args=(emote_show_json,))
            emote_show_thread.start()
            # 当前【摇摆动作】等待结束时间
            endwait = emote_show_json[0]["endwait"]
            while endwait > 0:
                time.sleep(1)
                endwait = endwait - 1
                # 唱歌完毕并且聊天完毕：停止摇摆动作
                if self.singData.is_singing == 2 and self.ttsData.is_tts_ready == True:
                    self.vtuberData.swing_motion = 2
                    self.log.info(f"强制停止摇摆：{self.vtuberData.swing_motion}")
                    break
        self.vtuberData.swing_motion = 2
        self.log.info(f"结束摇摆：{emote_show_json}")

    # 停止动作
    def stop_motion(self):
        while self.vtuberData.swing_motion == 1:
            time.sleep(1)
        self.log.info(f"静止：{self.vtuberData.swing_motion}")
        self.emoteOper.emote_ws(1, 0, "静止")

    # 场景切换
    def changeScene(self,sceneName):
        if self.allow_scene(sceneName) == True:
            # 切换场景
            self.obs.change_scene(sceneName)
            # 背景乐切换
            if sceneName in self.vtuberData.song_background:
                song = self.vtuberData.song_background[sceneName]
                if self.obs.get_video_status("背景音乐") == VideoStatus.PAUSE.value:
                    self.obs.play_video("背景音乐", song)
                    time.sleep(1)
                    self.obs.control_video("背景音乐", VideoControl.PAUSE.value)
                else:
                    self.obs.play_video("背景音乐", song)
                return True
            else:
                self.llmData.AnswerList.put(f"晚上{self.llmData.Ai_Name}不敢过去{sceneName}哦")
        return False

    # 判断每一种时间段允许移动的场景
    def allow_scene(self,queryExtract):
        now_time = time.strftime("%H:%M:%S", time.localtime())
        # 晚上允许进入的场景
        night = ["神社", "粉色房间", "海岸花坊"]
        if "18:00:00" <= now_time <= "24:00:00" or "00:00:00" < now_time < "06:00:00":
            num = StringUtil.is_index_contain_string(night, queryExtract)
            if num <= 0:
                return False
        return True