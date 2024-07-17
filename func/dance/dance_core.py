# 跳舞功能
from threading import Thread
import time
import random
from func.log.default_log import DefaultLog
from func.cmd.cmd_core import CmdCore
from func.tts.tts_core import TTsCore

from func.obs.obs_init import ObsInit
from func.obs.obs_websocket import ObsWebSocket,VideoStatus,VideoControl
from func.tools.string_util import StringUtil
from func.tools.singleton_mode import singleton

from func.gobal.data import SingData
from func.gobal.data import DanceData

@singleton
class DanceCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    singData = SingData()  # 唱歌数据
    danceData = DanceData()  # 跳舞数据

    ttsCore = TTsCore()  # tts语音
    cmdCore = CmdCore()  # cmd操作

    def __init__(self):
        self.obs = ObsInit().get_ws()

    # 跳舞任务
    def check_dance(self,sched1):
        if not self.danceData.DanceQueueList.empty() and self.danceData.is_dance == 2:
            self.danceData.is_dance = 1
            # 停止所有定时任务
            sched1.pause()
            # 停止所有在执行的任务
            self.cmdCore.cmd("all","\\dance","0", "check_dance")
            self.ttsCore.tts_say("开始跳舞了，大家嗨起来")
            dance_json = self.danceData.DanceQueueList.get()
            # 开始跳舞任务
            self.dance(dance_json)
            # 重启定时任务
            sched1.resume()
            self.danceData.is_dance = 2  # 跳舞完成

    # 跳舞操作
    def dance(self,dance_json):
        video_path = dance_json["video_path"]
        self.log.info(dance_json)
        self.obs.control_video("背景音乐", VideoControl.PAUSE.value)
        # ============== 跳舞视频 ==============
        # 第一次播放
        if video_path != self.danceData.dance_now_path:
            self.obs.play_video("video", video_path)
        else:
            self.obs.control_video("video", VideoControl.RESTART.value)
        # 赋值当前跳舞视频
        self.danceData.dance_now_path = video_path
        time.sleep(1)
        while self.obs.get_video_status("video") != VideoStatus.END.value and self.danceData.is_dance == 1:
            time.sleep(1)
        self.obs.control_video("video", VideoControl.STOP.value)
        # ============== end ==============
        self.obs.control_video("背景音乐", VideoControl.PLAY.value)

    # 唱歌跳舞
    def sing_dance(self,songname):
        # 提示语为空，随机视频
        self.danceData.video_path = ""
        if songname != "":
            matches_list = StringUtil.fuzzy_match_list(songname, self.danceData.dance_video)
            if len(matches_list) > 0:
                rnd_video = random.randrange(0, len(matches_list))
                video_path = matches_list[rnd_video]
        if self.danceData.video_path == "":
            return
        # 第一次播放
        if self.danceData.video_path != self.danceData.singdance_now_path:
            self.obs.play_video("唱歌视频", self.danceData.video_path)
        else:
            self.obs.control_video("唱歌视频", VideoControl.RESTART.value)
        # 赋值当前表情视频
        self.danceData.singdance_now_path = self.danceData.video_path
        time.sleep(1)
        while self.singData.is_singing == 1:
            # 结束循环重新播放
            if self.obs.get_video_status("唱歌视频") == VideoStatus.END.value:
                self.obs.control_video("唱歌视频", VideoControl.RESTART.value)
            time.sleep(1)

    # 表情播放[不用停止跳舞]
    def emote_play_nodance(self,eomte_path):
        self.danceData.emote_video_lock.acquire()
        self.log.info(f"播放表情:{eomte_path}")
        # 第一次播放
        if eomte_path != self.danceData.emote_now_path:
            self.obs.play_video("表情", eomte_path)
        else:
            self.obs.control_video("表情", VideoControl.RESTART.value)
        # 赋值当前表情视频
        self.danceData.emote_now_path = eomte_path
        time.sleep(1)
        # 20秒超时停止播放
        sec = 20
        while self.obs.get_video_status("表情") != VideoStatus.END.value and sec > 0:
            time.sleep(1)
            sec = sec - 1
        time.sleep(1)
        self.obs.control_video("表情", VideoControl.STOP.value)
        self.danceData.emote_video_lock.release()

    # 表情播放
    def emote_play(self,eomte_path):
        self.danceData.emote_video_lock.acquire()
        self.obs.control_video("video", VideoControl.PAUSE.value)
        self.log.info(f"播放表情:{eomte_path}")
        # 第一次播放
        if eomte_path != self.danceData.emote_now_path:
            self.obs.play_video("表情", eomte_path)
        else:
            self.obs.control_video("表情", VideoControl.RESTART.value)
        # 赋值当前表情视频
        self.danceData.emote_now_path = eomte_path
        time.sleep(1)
        # 20秒超时停止播放
        sec = 20
        while self.obs.get_video_status("表情") != VideoStatus.END.value and sec > 0:
            time.sleep(1)
            sec = sec - 1
        time.sleep(1)
        self.obs.control_video("表情", VideoControl.STOP.value)
        self.obs.control_video("video", VideoControl.PLAY.value)
        self.danceData.emote_video_lock.release()

    # 跳舞表情入口处理
    def msg_deal_emotevideo(self, traceid, query, uid, user_name):
        text = ["#"]
        is_contain = StringUtil.has_string_reg_list(f"^{text}", query)
        if is_contain is not None:
            num = StringUtil.is_index_contain_string(text, query)
            queryExtract = query[num: len(query)]  # 提取提问语句
            queryExtract = queryExtract.strip()
            self.log.info(f"[{traceid}]跳舞表情：" + queryExtract)
            video_path = ""
            if queryExtract == "rnd":
                rnd_video = random.randrange(0, len(self.danceData.emote_video))
                video_path = self.danceData.emote_video[rnd_video]
            else:
                matches_list = StringUtil.fuzzy_match_list(queryExtract, self.danceData.emote_video)
                if len(matches_list) > 0:
                    rnd_video = random.randrange(0, len(matches_list))
                    video_path = matches_list[rnd_video]
            # 第一次播放
            if video_path != "":
                if self.danceData.is_dance == 1:
                    emote_play_thread = Thread(target=self.emote_play, args=(video_path,))
                    emote_play_thread.start()
                else:
                    emote_play_thread = Thread(target=self.emote_play_nodance, args=(video_path,))
                    emote_play_thread.start()
            return True

        # 跳舞中不执行其他任务
        if self.danceData.is_dance == 1:
            return True

        return False

    # 跳舞入口处理
    def msg_deal_dance(self, traceid, query, uid, user_name):
        # 跳舞
        text = ["跳舞", "跳一下", "舞蹈"]
        is_contain = StringUtil.has_string_reg_list(f"^{text}", query)
        if is_contain is not None:
            num = StringUtil.is_index_contain_string(text, query)
            queryExtract = query[num: len(query)]  # 提取提问语句
            queryExtract = queryExtract.strip()
            self.log.info(f"[{traceid}]跳舞提示：" + queryExtract)
            video_path = ""
            # 提示语为空，随机视频
            if queryExtract == "":
                rnd_video = random.randrange(0, len(self.danceData.dance_video))
                video_path = self.danceData.dance_video[rnd_video]
            else:
                matches_list = StringUtil.fuzzy_match_list(queryExtract, self.danceData.dance_video)
                if len(matches_list) > 0:
                    rnd_video = random.randrange(0, len(matches_list))
                    video_path = matches_list[rnd_video]
            # 加入跳舞队列
            if video_path != "":
                dance_json = {"traceid": traceid, "prompt": queryExtract, "username": user_name,
                              "video_path": video_path}
                self.danceData.DanceQueueList.put(dance_json)
                return True
            else:
                self.log.info("跳舞视频不存在：" + queryExtract)
                return True
        return False
