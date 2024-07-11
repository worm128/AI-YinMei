# 唱歌功能
from func.tools.singleton_mode import singleton
from func.log.default_log import DefaultLog
from func.gobal.data import SingData
from func.obs.obs_init import ObsInit
from func.tools.string_util import StringUtil

from func.tts.tts_core import TTsCore
from func.llm.llm_core import LLmData
from func.image.image_core import ImageCore

from func.obs.obs_websocket import ObsWebSocket,VideoStatus,VideoControl
from func.vtuber.emote_oper import EmoteOper
from func.vtuber.action_oper import ActionOper
from func.tts.player import MpvPlay

import requests
import json
import time
import os
import re
from threading import Thread

@singleton
class SingCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    singData = SingData()  # 唱歌数据
    llmData = LLmData()  # llm数据

    ttsCore = TTsCore()  # 语音核心
    imageCore = ImageCore()  # 图片核心
    emoteOper = EmoteOper()  # 表情
    actionOper = ActionOper()  # 动作
    mpvPlay = MpvPlay()  # 播放器

    def __init__(self):
        self.obs = ObsInit().get_ws()

    # 唱歌
    def singTry(self,songname, username):
        try:
            if songname != "":
                self.sing(songname, username)
        except Exception as e:
            self.log.exception(f"【singTry】发生了异常：{e}")
            self.singData.is_singing = 2
            self.singData.is_creating_song = 2

    # 唱歌
    def sing(self,songname, username):
        is_created = 0  # 1.已经生成过 0.没有生成过 2.生成失败

        query = songname  # 查询内容

        # =============== 开始-获取真实歌曲名称 =================
        musicJson = requests.get(url=f"http://{self.singData.singUrl}/musicInfo/{query}", timeout=(5, 10))
        music_json = json.loads(musicJson.text)
        id = music_json["id"]
        songname = music_json["songName"]
        # 前置信息说明
        font_text = ""
        if query.lower().replace(" ", "") != songname.lower().replace(" ", ""):
            font_text = f'根据"{query}"的信息，'

        if id == 0:
            outputTxt = f"{font_text}歌库不存在《{query}》这首歌曲哦"
            self.log.info(outputTxt)
            self.ttsCore.tts_say(outputTxt)
            return
        song_path = f"./output/{songname}/"
        # =============== 结束-获取真实歌曲名称 =================

        # =============== 开始-重复点播判断 =================
        if self.exist_song_queues(self.singData.SongMenuList, songname) == True:
            outputTxt = (
                f"回复{username}：{font_text}歌单里已经有歌曲《{songname}》，请勿重新点播"
            )
            self.ttsCore.tts_say(outputTxt)
            return
        # =============== 结束-重复点播判断 =================

        # =============== 开始-判断本地是否有歌 =================
        if os.path.exists(f"{song_path}/accompany.wav") or os.path.exists(
                f"{song_path}/vocal.wav"
        ):
            self.log.info(f"找到存在本地歌曲:{song_path}")
            outputTxt = f"回复{username}：{font_text}{self.llmData.Ai_Name}会唱《{songname}》这首歌曲哦"
            self.ttsCore.tts_say(outputTxt)
            is_created = 1
        # =============== 结束-判断本地是否有歌 =================
        else:
            # =============== 开始-调用已经转换的歌曲 =================
            # 下载歌曲：这里网易歌库返回songname和用户的模糊搜索可能歌名不同
            is_created = self.check_down_song(songname)
            if is_created == 1:
                # 下载伴奏
                self.down_song_file(songname, "get_accompany", "accompany", song_path)
                # 下载人声
                self.down_song_file(songname, "get_vocal", "vocal", song_path)
                self.log.info(f"找到服务已经转换的歌曲《{songname}》")
        # =============== 结束-调用已经转换的歌曲 =================

        # =============== 开始：如果不存在歌曲，生成歌曲 =================
        if is_created == 0:
            # 播报学习歌曲
            self.log.info(f"歌曲不存在，需要生成歌曲《{songname}》")
            outputTxt = f"回复{username}：{font_text}{self.llmData.Ai_Name}需要学唱歌曲《{songname}》，请耐心等待"
            self.ttsCore.tts_say(outputTxt)
            # 其他歌曲在生成的时候等待
            while self.singData.is_creating_song == 1:
                time.sleep(1)
            # 调用Ai学唱歌服务：生成歌曲
            is_created = self.create_song(songname, query, song_path, is_created)
        if is_created == 2:
            self.log.info(f"生成歌曲失败《{songname}》")
            return
        self.obs.show_text("状态提示", f"{self.llmData.Ai_Name}已经学会歌曲《{songname}》")
        # =============== 结束：如果不存在歌曲，生成歌曲 =================

        # 等待播放
        self.log.info(f"等待播放{username}点播的歌曲《{songname}》：{self.singData.is_singing}")
        # 加入播放歌单
        self.singData.SongMenuList.put({"username": username, "songname": songname, "is_created": is_created, "song_path": song_path,
                          "query": query})

    # 播放歌曲清单
    def check_playSongMenuList(self):
        if not self.singData.SongMenuList.empty() and self.singData.is_singing == 2:
            # 播放歌曲
            self.singData.play_song_lock.acquire()
            mlist = self.singData.SongMenuList.get()  # 取出歌单播放
            self.singData.SongNowName = mlist  # 赋值当前歌曲名称
            self.singData.is_singing = 1  # 开始唱歌
            # =============== 开始：播放歌曲 =================
            self.obs.control_video("背景音乐", VideoControl.PAUSE.value)
            self.play_song(mlist["is_created"], mlist["songname"], mlist["song_path"], mlist["username"], mlist["query"])
            if self.singData.SongMenuList.qsize() == 0:
                self.obs.control_video("背景音乐", VideoControl.PLAY.value)
            # =============== 结束：播放歌曲 =================
            self.singData.is_singing = 2  # 完成唱歌
            self.singData.SongNowName = {}  # 当前播放歌单清空
            self.singData.play_song_lock.release()

    # 开始生成歌曲
    def create_song(self,songname, query, song_path, is_created):
        try:
            # =============== 开始生成歌曲 =================
            self.singData.create_song_lock.acquire()
            self.singData.is_creating_song = 1
            status_json = {}
            is_download = False
            # =============== 开始-选择一、当前歌曲只下载不转换 =================
            match = re.search(self.singData.song_not_convert, songname)
            if match:
                self.log.info(f"当前歌曲只下载不转换《{songname}》")
                # 直接生成原始音乐
                jsonStr = requests.get(
                    url=f"http://{self.singData.singUrl}/download_origin_song/{songname}",
                    timeout=(5, 120),
                )
                status_json = json.loads(jsonStr.text)
                # 下载原始音乐
                self.down_song_file(status_json["songName"], "get_audio", "vocal", song_path)
                is_download = True
                return 1
            # =============== 结束-当前歌曲只下载不转换 =================

            # =============== 开始-选择二、学习唱歌任务 =================
            if is_download == False:
                # 生成歌曲接口
                jsonStr = requests.get(
                    url=f"http://{self.singData.singUrl}/append_song/{query}", timeout=(5, 10)
                )
                status_json = json.loads(jsonStr.text)
            # =============== 结束-学习唱歌任务 =================

            status = status_json["status"]  # status: "processing" "processed" "waiting"
            songname = status_json["songName"]
            self.log.info(f"准备生成歌曲内容：{status_json}")
            if status == "processing" or status == "processed" or status == "waiting":
                i = 0
                vocal_downfile = None
                accompany_downfile = None
                song_path = f"./output/{songname}/"
                while (
                        vocal_downfile is None or accompany_downfile is None
                ) and self.singData.is_creating_song == 1:
                    # 检查歌曲是否生成成功：这里网易歌库返回songname和用户的模糊搜索可能歌名不同
                    is_created = self.check_down_song(songname)
                    if is_created == 2:
                        break
                    # 检测文件生成后，进行下载
                    if is_created == 1:
                        # 下载伴奏
                        accompany_downfile = self.down_song_file(
                            songname, "get_accompany", "accompany", song_path
                        )
                        # 下载人声
                        vocal_downfile = self.down_song_file(
                            songname, "get_vocal", "vocal", song_path
                        )
                    i = i + 1
                    if i >= self.singData.create_song_timout:
                        is_created = 2
                        break
                    self.obs.show_text("状态提示", f"当前{self.llmData.Ai_Name}学唱歌曲《{songname}》第{i}秒")
                    self.log.info(f"生成《{songname}》歌曲第[{i}]秒,生成状态:{is_created}")
                    time.sleep(1)
            # =============== 结束生成歌曲 =================
        except Exception as e:
            self.log.exception(f"《{songname}》create_song异常{e}")
            is_created = 2
        finally:
            self.singData.is_creating_song = 2
            self.singData.create_song_lock.release()
        return is_created

    # 下载伴奏accompany/人声vocal
    def down_song_file(self,songname, interface_name, file_name, save_folder):
        # 下载
        downfile = requests.get(
            url=f"http://{self.singData.singUrl}/{interface_name}/{songname}", timeout=(5, 120)
        )
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
        save_path = save_folder + f"/{file_name}.wav"
        # 本地保存
        if downfile is not None:
            with open(save_path, "wb") as f:
                f.write(downfile.content)
        return downfile

    # 播放歌曲 1.成功 2.没有歌曲播放 3.异常
    def play_song(self,is_created, songname, song_path, username, query):
        try:
            # 播放歌曲
            if is_created == 1:
                self.log.info(f"准备唱歌《{songname}》,播放路径:{song_path}")
                # =============== 开始-触发搜图 =================
                img_search_json = {"prompt": query, "username": username}
                searchimg_output_thread = Thread(
                    target=self.imageCore.searchimg_output, args=(img_search_json,)
                )
                searchimg_output_thread.start()
                # =============== 结束-触发搜图 =================
                # 开始唱歌服装穿戴
                self.emoteOper.emote_ws(1, 0.2, "唱歌")
                # 播报唱歌文字
                self.ttsCore.tts_say(f"回复{username}：我准备唱一首歌《{songname}》")
                # 循环摇摆动作
                auto_swing_thread = Thread(target=self.actionOper.auto_swing)
                auto_swing_thread.start()
                # 唱歌视频播放
                # sing_dance_thread = Thread(target=sing_dance, args=(query,))
                # sing_dance_thread.start()
                # ============== 播放音乐 ================
                # 伴奏播放
                abspath = os.path.abspath(song_path + "accompany.wav")
                accompany_thread = Thread(target=self.obs.play_video, args=("伴奏", abspath))
                # 调用音乐播放器[人声播放]
                mpv_play_thread = Thread(
                    target=self.sing_play,
                    args=("song.exe", song_path + "vocal.wav", 100, "+0.08"),
                )
                accompany_thread.start()
                mpv_play_thread.start()
                # ================ end ==================
                # 循环等待唱歌结束标志
                time.sleep(3)
                while self.singData.sing_play_flag == 1:
                    time.sleep(1)
                # 伴奏停止
                self.obs.control_video("伴奏", VideoControl.STOP.value)
                # 停止唱歌视频播放
                # self.obs.control_video("唱歌视频",VideoControl.STOP.value)
                # 结束唱歌穿戴
                self.emoteOper.emote_ws(1, 0.2, "唱歌")
                return 1
            else:
                tip = f"已经跳过歌曲《{songname}》，请稍后再点播"
                self.log.info(tip)
                # 加入回复列表，并且后续合成语音
                self.ttsCore.tts_say(f"回复{username}：{tip}")
                return 2
        except Exception as e:
            self.log.exception(f"《{songname}》play_song异常{e}")
            return 3

    # 播放唱歌
    def sing_play(self, mpv_name, song_path, volume, start):
        self.singData.sing_play_flag = 1
        self.mpvPlay.mpv_play(mpv_name, song_path, volume, start)
        self.singData.sing_play_flag = 0

    # 唱歌线程
    def check_sing(self):
        if not self.singData.SongQueueList.empty():
            song_json = self.singData.SongQueueList.get()
            self.log.info(f"启动唱歌:{song_json}")
            # 启动唱歌
            sing_thread = Thread(
                target=self.singTry, args=(song_json["prompt"], song_json["username"])
            )
            sing_thread.start()

    # http接口：唱歌接口处理
    def http_sing(self,songname,username):
        self.log.info(f'http唱歌接口处理："{username}"点播歌曲《{songname}》')
        song_json = {"prompt": songname, "username": username}
        self.singData.SongQueueList.put(song_json)
        return

    # http接口：点播歌曲列表
    def http_songlist(self,CallBackForTest):
        jsonstr = []
        if len(self.singData.SongNowName) > 0:
            # 当前歌曲
            username = self.singData.SongNowName["username"]
            songname = self.singData.SongNowName["songname"]
            text = f"'{username}'点播《{songname}》"
            jsonstr.append({"songname": text})
        # 播放歌曲清单
        for i in range(self.singData.SongMenuList.qsize()):
            data = self.singData.SongMenuList.queue[i]
            username = data["username"]
            songname = data["songname"]
            text = f"'{username}'点播《{songname}》"
            jsonstr.append({"songname": text})
        str = '({"status": "成功","content": ' + json.dumps(jsonstr) + "})"
        return str

    # 唱歌入口处理
    def msg_deal(self, traceid, query, uid, user_name):
        # 唱歌
        text = ["唱一下", "唱一首", "唱歌", "点歌", "点播"]
        is_contain = StringUtil.has_string_reg_list(f"^{text}", query)
        if is_contain is not None:
            num = StringUtil.is_index_contain_string(text, query)
            queryExtract = query[num: len(query)]  # 提取提问语句
            queryExtract = queryExtract.strip()
            self.log.info(f"[{traceid}]唱歌提示：" + queryExtract)
            if queryExtract == "":
                return True
            song_json = {"traceid": traceid, "prompt": queryExtract, "username": user_name}
            self.singData.SongQueueList.put(song_json)
            return True
        return False

    # 判断字符是否存在歌曲此队列
    def exist_song_queues(self, queues, name):
        # 当前歌曲
        if "songname" in self.singData.SongNowName and self.singData.SongNowName["songname"] == name:
            return True
        # 歌单里歌曲
        for i in range(queues.qsize()):
            data = queues.queue[i]
            if data["songname"] == name:
                return True
        return False

    # 匹配已生成的歌曲，并返回字节流
    def check_down_song(self,songname):
        # 查看歌曲是否曾经生成
        status = requests.get(
            url=f"http://{self.singData.singUrl}/accompany_vocal_status", timeout=(5, 10)
        )
        converted_json = json.loads(status.text)
        converted_file = converted_json["converted_file"]  # 生成歌曲硬盘文件
        convertfail = converted_json["convertfail"]  # 生成歌曲硬盘文件
        is_created = 0  # 1.已经生成过 0.没有生成过 2.生成失败
        for filename in convertfail:
            if songname == filename:
                is_created = 2
                return is_created

        # 优先：精确匹配文件名
        for filename in converted_file:
            if songname == filename:
                is_created = 1
                return is_created

        return is_created