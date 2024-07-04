import threading
import uuid
import datetime
import logging
import traceback
import queue
import re
import subprocess
from func.log import logger
from func.emote.emote_oper import EmoteOper
from threading import Thread
from func.tools.string_util import StringUtil
from func.obs.obs_websocket import ObsWebSocket, VideoStatus, VideoControl
from func.translate.duckduckgo_translate import DuckduckgoTranslate
from .gtp_vists import gtpVists
from .player import mpvPlay

def singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

@singleton
class ttsCore:
    # 设置控制台日志
    today = datetime.date.today().strftime("%Y-%m-%d")
    log = logger.getLogger(f"./logs/log_{today}.txt", "ttsCore")

    SayCount = 0
    say_lock = threading.Lock()
    ReplyTextList = queue.Queue()  # Ai回复框文本队列

    
    def __init__(self, obs, Ai_Name):
        self.obs = obs
        self.Ai_Name= Ai_Name

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
        global is_tts_ready
        global is_stream_out
        try:
            self.tts_say_do(json)
        except Exception as e:
            is_tts_ready = True
            is_stream_out = False
            self.log.info(f"【tts_chat_say】发生了异常：{e}")
            logging.error(traceback.format_exc())

    # 直接合成语音播放 {"question":question,"text":text,"lanuage":"ja"}
    def tts_say_do(self,json):
        global SayCount
        global is_tts_ready
        global is_stream_out
        SayCount += 1
        filename = f"say{SayCount}"

        question = json["question"]
        text = json["text"]
        replyText = text
        lanuage = json["lanuage"]
        voiceType = json["voiceType"]
        traceid = json["traceid"]
        chatStatus = json["chatStatus"]

        # 退出标识
        if text == "" and chatStatus == "end":
            self.say_lock.acquire()
            replyText_json = {"traceid": traceid, "chatStatus": chatStatus, "text": ""}
            self.log.info(replyText_json)
            self.ReplyTextList.put(replyText_json)
            is_stream_out = False
            self.say_lock.release()
            return

        # 识别表情
        jsonstr = EmoteOper.emote_content(text)
        self.log.info(f"[{traceid}]输出表情{jsonstr}")
        emotion = "happy"
        if len(jsonstr) > 0:
            emotion = jsonstr[0]["content"]

        # 感情值增加
        moodNum = EmoteOper.mood(emotion)

        # 触发翻译日语
        if lanuage == "AutoChange":
            self.log.info(f"[{traceid}]当前感情值:{moodNum}")
            if re.search(".*日(文|语).*", question) or re.search(".*日(文|语).*说.*", text):
                trans_json = DuckduckgoTranslate.translate(text, "zh-Hans", "ja")
                if StringUtil.has_field(trans_json, "translated"):
                    text = trans_json["translated"]
            elif re.search(".*英(文|语).*", question) or re.search(
                    ".*英(文|语).*说.*", text
            ):
                trans_json = DuckduckgoTranslate.translate(text, "zh-Hans", "en")
                if StringUtil.has_field(trans_json, "translated"):
                    text = trans_json["translated"]
            elif moodNum > 270 or emotion == "angry":
                trans_json = DuckduckgoTranslate.translate(text, "zh-Hans", "ja")
                if StringUtil.has_field(trans_json, "translated"):
                    text = trans_json["translated"]

        # 微软合成语音
        # with open(f"./output/{filename}.txt", "w", encoding="utf-8") as f:
        #     f.write(f"{text}")  # 将要读的回复写入临时文件
        # 合成声音
        # subprocess.run(
        #     f"edge-tts --voice zh-CN-XiaoxiaoNeural --rate=+20% --f .\output\{filename}.txt --write-media .\output\{filename}.mp3 2>nul",
        #     shell=True,
        # )

        # bert-vits2合成语音
        # status = bert_vits2(filename,text,emotion)

        # gtp-vists合成语音
        pattern = "(《|》)"  # 过滤特殊字符，这些字符会影响语音合成
        text = re.sub(pattern, "", text)
        status = gtpVists.gtp_vists(filename, text, emotion)
        if status == 0:
            return
        if question != "":
            self.obs.show_text("状态提示", f'{self.Ai_Name}语音合成"{question}"完成')

        # 判断同序列聊天语音合成时候，其他语音合成任务等待
        # if voiceType!="chat":
        #     while is_stream_out==True:
        #         time.sleep(1)

        # ============ 【线程锁】播放语音【时间会很长】 ==================
        self.say_lock.acquire()
        is_tts_ready = False
        if chatStatus == "start":
            is_stream_out = True

        # 输出表情
        emote_thread = Thread(target=EmoteOper.emote_show, args=(jsonstr,))
        emote_thread.start()

        # 输出回复字幕
        replyText_json = {"traceid": traceid, "chatStatus": chatStatus, "text": replyText}
        self.log.info(replyText_json)
        self.ReplyTextList.put(replyText_json)

        # 循环摇摆动作
        yaotou_thread = Thread(target=auto_swing)
        yaotou_thread.start()

        # 播放声音
        mpvPlay.mpv_play("mpv.exe", f".\output\{filename}.mp3", 100, "0")

        if chatStatus == "end":
            is_stream_out = False
        is_tts_ready = True
        self.say_lock.release()
        # ========================= end =============================

        # 删除语音文件
        subprocess.run(f"del /f .\output\{filename}.mp3 1>nul", shell=True)