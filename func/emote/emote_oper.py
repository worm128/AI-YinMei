from func.tools.string_util import StringUtil
import random
import time
import json
import datetime
import websocket
from threading import Thread
from func.log import logger

# 设置控制台日志
today = datetime.date.today().strftime("%Y-%m-%d")
log = logger.getLogger(f"./logs/log_{today}.txt", "bilibili-live")

class EmoteOper:
    def __init__(self, obs, config):
        self.obs = obs
        self.config= config
        vtuber_websocket = config["emote"]["vtuber_websocket"]
        ws = websocket.WebSocketApp(f"ws://{vtuber_websocket}", on_open=self.on_open)
        vtuber_pluginName = config["emote"]["vtuber_pluginName"]
        vtuber_pluginDeveloper = config["emote"]["vtuber_pluginDeveloper"]
        vtuber_authenticationToken = config["emote"]["vtuber_authenticationToken"]

    # ============= Vtuber表情 =====================
    def run_forever(self):
        ws.run_forever(ping_timeout=1)

    def on_open(self,ws):
        self.auth()

    # 授权Vtuber服务
    def auth(self):
        # 授权码
        authstr = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": self.vtuber_pluginName,
                "pluginDeveloper": self.vtuber_pluginDeveloper,
                "authenticationToken": self.vtuber_authenticationToken,
            },
        }
        data = json.dumps(authstr)
        ws.send(data)

    # ============================================

    # 文本识别表情内容
    # "content":语音情感,"key":按键名称,"num":执行,第几个字符开始执行表情,
    # "donum":循环表情次数 timesleep:和donum联动，等待n秒开始循环执行当前表情,"endwait":表情等待结束时间，一般和执行表情的时间一致
    def emote_content(self,response):
        jsonstr = []
        # =========== 随机动作 ==============
        # text = ["笑", "不错", "哈", "开心", "呵", "嘻", "画", "欢迎", "搜", "唱"]
        # num = StringUtil.is_index_nocontain_string(text, response)
        # if num > 0:
        #     press_arry = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        #     press = random.randrange(0, len(press_arry))
        #     jsonstr.append({"content":"happy","key":press_arry[press],"num":num})
        # ===============================

        # =========== 开心 ==============
        text = ["笑", "不错", "哈", "开心", "呵", "嘻", "画", "搜", "有趣"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "happy",
                    "key": "开心",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        # =========== 哭 ==============
        text = ["哭", "悲伤", "伤心", "凄惨", "好惨", "呜呜", "悲哀"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "sad",
                    "key": "哭",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        # =========== 招呼 ==============
        text = ["你好", "在吗", "干嘛", "名字", "欢迎", "我在", "玩笑", "逗"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            press1 = random.randrange(1, 3)
            if press1 == 1:
                jsonstr.append(
                    {
                        "content": "call",
                        "key": "捂嘴",
                        "num": num,
                        "timesleep": 0,
                        "donum": 0,
                        "endwait": 0,
                    }
                )
            else:
                jsonstr.append(
                    {
                        "content": "call",
                        "key": "拿扇子",
                        "num": num,
                        "timesleep": 0,
                        "donum": 0,
                        "endwait": 0,
                    }
                )
            press2 = random.randrange(1, 4)
            if press2 == 1:
                jsonstr.append(
                    {
                        "content": "call",
                        "key": "星星眼",
                        "num": num,
                        "timesleep": 0,
                        "donum": 0,
                        "endwait": 0,
                    }
                )
            elif press2 == 2:
                jsonstr.append(
                    {
                        "content": "call",
                        "key": "害羞",
                        "num": num,
                        "timesleep": 0,
                        "donum": 0,
                        "endwait": 0,
                    }
                )
            elif press2 == 3:
                jsonstr.append(
                    {
                        "content": "call",
                        "key": "米米",
                        "num": num,
                        "timesleep": 0,
                        "donum": 0,
                        "endwait": 0,
                    }
                )
        # =========== 有钱 ==============
        text = ["钱", "money", "有米"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "call",
                    "key": "米米",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        # =========== 温柔 ==============
        text = ["温柔", "抚摸", "抚媚", "骚", "唱歌"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            press1 = random.randrange(1, 3)
            if press1 == 1:
                jsonstr.append(
                    {
                        "content": "call",
                        "key": "左眼闭合",
                        "num": num,
                        "timesleep": 0,
                        "donum": 0,
                        "endwait": 0,
                    }
                )
            else:
                jsonstr.append(
                    {
                        "content": "call",
                        "key": "右眼闭合",
                        "num": num,
                        "timesleep": 0,
                        "donum": 0,
                        "endwait": 0,
                    }
                )
            press2 = random.randrange(1, 3)
            if press2 == 1:
                jsonstr.append(
                    {
                        "content": "call",
                        "key": "头左倾",
                        "num": num,
                        "timesleep": 0,
                        "donum": 0,
                        "endwait": 0,
                    }
                )
            else:
                jsonstr.append(
                    {
                        "content": "call",
                        "key": "头右倾",
                        "num": num,
                        "timesleep": 0,
                        "donum": 0,
                        "endwait": 0,
                    }
                )
        # =========== 生气 ==============
        text = ["生气", "不理你", "骂", "臭", "打死", "可恶", "白痴", "可恶"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "angry",
                    "key": "生气",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        # =========== 尴尬 ==============
        text = [
            "尴尬",
            "无聊",
            "无奈",
            "傻子",
            "郁闷",
            "龟蛋",
            "傻逼",
            "逗比",
            "逗逼",
            "忘记",
            "怎么可能",
            "调侃",
        ]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "blush",
                    "key": "尴尬",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        # =========== 认同 ==============
        text = ["认同", "点头", "嗯", "哦", "女仆"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "approve",
                    "key": "认同",
                    "num": num,
                    "timesleep": 0.002,
                    "donum": 5,
                    "endwait": 0,
                }
            )
        # =========== 汗颜 ==============
        text = ["汗颜", "流汗", "郁闷", "笑死", "白痴", "渣渣", "搞笑", "恶心"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "sweat",
                    "key": "汗颜",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        # =========== 晕 ==============
        text = ["晕", "头晕", "晕死", "呕"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "blush",
                    "key": "晕",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        # =========== 吐血 ==============
        text = ["吐血", "血"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "blood",
                    "key": "血",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        # =========== 可爱 ==============
        text = ["可爱", "害羞", "爱你", "天真", "搞笑", "喜欢", "全知全能"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "love",
                    "key": "可爱",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        # =========== 摸摸头 ==============
        text = ["摸摸头", "摸摸脑袋", "乖", "做得好"]
        num = StringUtil.is_index_nocontain_string(text, response)
        if num > 0:
            jsonstr.append(
                {
                    "content": "happy",
                    "key": "摸摸头",
                    "num": num,
                    "timesleep": 5,
                    "donum": 1,
                    "endwait": 0,
                }
            )
            jsonstr.append(
                {
                    "content": "blush",
                    "key": "晕",
                    "num": num,
                    "timesleep": 0,
                    "donum": 0,
                    "endwait": 0,
                }
            )
        return jsonstr

    # 表情加入:使用键盘控制VTube
    # key：表情按键  num:第几个字符开始执行表情 donum：循环表情次数 timesleep:和donum联动，等待n秒开始循环执行当前表情
    def emote_show(self,emote_content):
        for data in emote_content:
            key = data["key"]
            num = data["num"]
            timesleep = data["timesleep"]
            donum = data["donum"]
            self.emote_ws(num, 0.4, key)
            # 有需要结束的表情按钮
            while donum > 0:
                time.sleep(timesleep)
                self.emote_ws(1, 0, key)
                donum = donum - 1

    # ws协议：发送表情到Vtuber
    # num：表情第几个执行   interval：间隔秒数  key：按键
    def emote_ws(self,num, interval, key):
        global ws
        if num > 0:
            start = round(num * interval, 2)
            time.sleep(start)
            jstr = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "SomeID11",
                "messageType": "HotkeyTriggerRequest",
                "data": {"hotkeyID": key},
            }
            data = json.dumps(jstr)
            # vtuber执行表情展示
            try:
                ws.send(data)
            except Exception as e:
                error = f"【表情发送】发生了异常：{e}"
                log.info(error)
                if error in "Connection is already closed":
                    ws = websocket.WebSocketApp(f"ws://{self.vtuber_websocket}", on_open=self.on_open)
                    # ws服务心跳包
                    run_forever_thread = Thread(target=self.run_forever)
                    run_forever_thread.start()

    # 感情值判断
    def mood(self,emotion):
        global mood_num
        if emotion == "sad":
            mood_num = mood_num + 1
        if emotion == "happy":
            mood_num = mood_num + 2
        if emotion == "angry":
            mood_num = mood_num + 3
        if mood_num > 300:
            mood_num = 0
        return mood_num