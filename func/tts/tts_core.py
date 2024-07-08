import uuid
import logging
import traceback
import re
import subprocess
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from func.log.default_log import DefaultLog
from func.vtuber.emote_oper import EmoteOper
from func.vtuber.action_oper import ActionOper
from func.tools.string_util import StringUtil
from func.translate.duckduckgo_translate import DuckduckgoTranslate
from func.llm.llm_core import LLmCore
from func.tts.gtp_vists import GtpVists
from func.tts.bert_vits2 import BertVis2
from func.tts.edge_tts_vits import EdgeTTs
from func.tts.player import MpvPlay
from func.obs.obs_init import ObsInit
from func.tools.singleton_mode import singleton
from func.gobal.data import TTsData
from func.gobal.data import LLmData
from func.gobal.data import SingData

@singleton
class TTsCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    llm = LLmCore()  # 大语言模型
    mpvPlay = MpvPlay()  # 播放器
    emoteOper = EmoteOper()  # 表情
    actionOper = ActionOper()  # 动作
    duckduckgoTranslate = DuckduckgoTranslate()  # 翻译

    ttsData = TTsData()  # tts数据
    llmData = LLmData()  # llm数据
    singData = SingData()  # 唱歌数据
    # 选择语音
    select_vists = ttsData.select_vists
    if select_vists == "GtpVists":
        vists = GtpVists()
    elif select_vists == "BertVis2":
        vists = BertVis2()
    elif select_vists == "EdgeTTs":
        vists = EdgeTTs()
    else:
        vists = GtpVists()


    def __init__(self):
        self.obs = ObsInit().get_ws()

    # 直接合成语音播放
    def tts_say(self,text):
        try:
            traceid = str(uuid.uuid4())
            json =  {"voiceType":"other","traceid":traceid,"chatStatus":"end","question":"","text":text,"lanuage":""}
            self.tts_say_do(json)
        except Exception as e:
            self.log.info(f"【tts_say】发生了异常：{e}")
            logging.error(traceback.format_exc())

    # 直接合成语音播放-聊天用
    def tts_chat_say(self,json):
        try:
            self.tts_say_do(json)
        except Exception as e:
            self.is_tts_ready = True
            self.llmData.is_stream_out = False
            self.log.info(f"【tts_chat_say】发生了异常：{e}")
            logging.error(traceback.format_exc())

    # 直接合成语音播放 {"question":question,"text":text,"lanuage":"ja"}
    def tts_say_do(self,json):

        self.ttsData.SayCount += 1
        filename = f"say{self.ttsData.SayCount}"

        question = json["question"]
        text = json["text"]
        replyText = text
        lanuage = json["lanuage"]
        voiceType = json["voiceType"]
        traceid = json["traceid"]
        chatStatus = json["chatStatus"]

        # 退出标识
        if text == "" and chatStatus == "end":
            self.ttsData.say_lock.acquire()
            replyText_json = {"traceid": traceid, "chatStatus": chatStatus, "text": ""}
            self.log.info(replyText_json)
            self.ttsData.ReplyTextList.put(replyText_json)
            self.llmData.is_stream_out = False
            self.ttsData.say_lock.release()
            return

        # 识别表情
        jsonstr = self.emoteOper.emote_content(text)
        self.log.info(f"[{traceid}]输出表情{jsonstr}")
        emotion = "happy"
        if len(jsonstr) > 0:
            emotion = jsonstr[0]["content"]

        # 感情值增加
        moodNum = self.emoteOper.mood(emotion)

        # 触发翻译日语
        if lanuage == "AutoChange":
            self.log.info(f"[{traceid}]当前感情值:{moodNum}")
            if re.search(".*日(文|语).*", question) or re.search(".*日(文|语).*说.*", text):
                trans_json = self.duckduckgoTranslate.translate(text, "zh-Hans", "ja")
                if StringUtil.has_field(trans_json, "translated"):
                    text = trans_json["translated"]
            elif re.search(".*英(文|语).*", question) or re.search(
                    ".*英(文|语).*说.*", text
            ):
                trans_json = self.duckduckgoTranslate.translate(text, "zh-Hans", "en")
                if StringUtil.has_field(trans_json, "translated"):
                    text = trans_json["translated"]
            elif moodNum > 270 or emotion == "angry":
                trans_json = self.duckduckgoTranslate.translate(text, "zh-Hans", "ja")
                if StringUtil.has_field(trans_json, "translated"):
                    text = trans_json["translated"]

        # 合成语音
        pattern = "(《|》)"  # 过滤特殊字符，这些字符会影响语音合成
        text = re.sub(pattern, "", text)
        status = self.vists.get_vists(filename, text, emotion)
        if status == 0:
            return
        if question != "":
            self.obs.show_text("状态提示", f'{self.llmData.Ai_Name}语音合成"{question}"完成')

        # 判断同序列聊天语音合成时候，其他语音合成任务等待
        # if voiceType!="chat":
        #     while self.llmData.is_stream_out==True:
        #         time.sleep(1)

        # ============ 【线程锁】播放语音【时间会很长】 ==================
        self.ttsData.say_lock.acquire()
        self.ttsData.is_tts_ready = False
        if chatStatus == "start":
            self.llmData.is_stream_out = True

        # 输出表情
        emote_thread = Thread(target=self.emoteOper.emote_show, args=(jsonstr,))
        emote_thread.start()

        # 输出回复字幕
        replyText_json = {"traceid": traceid, "chatStatus": chatStatus, "text": replyText}
        self.log.info(replyText_json)
        self.ttsData.ReplyTextList.put(replyText_json)

        # 循环摇摆动作
        yaotou_thread = Thread(target=self.actionOper.auto_swing)
        yaotou_thread.start()

        # 播放声音
        self.mpvPlay.mpv_play("mpv.exe", f".\output\{filename}.mp3", 100, "0")

        if chatStatus == "end":
            self.llmData.is_stream_out = False
        self.ttsData.is_tts_ready = True
        self.ttsData.say_lock.release()
        # ========================= end =============================

        # 删除语音文件
        subprocess.run(f"del /f .\output\{filename}.mp3 1>nul", shell=True)

    # 语音合成线程池
    tts_chat_say_pool = ThreadPoolExecutor(
        max_workers=ttsData.speech_max_threads, thread_name_prefix="tts_chat_say"
    )
    # 如果语音已经放完且队列中还有回复 则创建一个生成并播放TTS的线程
    def check_tts(self):
        if not self.llmData.AnswerList.empty():
            json = self.llmData.AnswerList.get()
            traceid = json["traceid"]
            text = json["text"]
            self.log.info(
                f"[{traceid}]text:{text},is_tts_ready:{self.ttsData.is_tts_ready},is_stream_out:{self.llmData.is_stream_out},SayCount:{self.ttsData.SayCount},is_singing:{self.singData.is_singing}")
            # 合成语音
            self.tts_chat_say_pool.submit(self.tts_chat_say, json)


    # http接口：聊天回复弹框处理
    def http_chatreply(self):
        status = "失败"
        if not self.ttsData.ReplyTextList.empty():
            json_str = self.ttsData.ReplyTextList.get()
            text = json_str["text"]
            traceid = json_str["traceid"]
            chatStatus = json_str["chatStatus"]
            status = "成功"
        jsonStr = "({\"traceid\": \"" + traceid + "\",\"chatStatus\": \"" + chatStatus + "\",\"status\": \"" + status + "\",\"content\": \"" + text.replace(
            "\"", "'").replace("\r", " ").replace("\n", "<br/>") + "\"})"
        return jsonStr