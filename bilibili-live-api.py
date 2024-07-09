# b站AI直播对接
import datetime
import time
import uuid
import asyncio, aiohttp
import http.cookies
import func.blivedm as blivedm
import func.blivedm.models.open_live as open_models
import func.blivedm.models.web as web_models

from typing import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from threading import Thread
from flask import Flask, jsonify, request
from flask_apscheduler import APScheduler

from func.obs.obs_websocket import VideoStatus, VideoControl
from func.tools.string_util import StringUtil
from func.log.default_log import DefaultLog
from func.config.default_config import defaultConfig

from func.vtuber.vtuber_init import VtuberInit
from func.obs.obs_init import ObsInit
from func.vtuber.emote_oper import EmoteOper
from func.tts.tts_core import TTsCore
from func.llm.llm_core import LLmCore
from func.sing.sing_core import SingCore
from func.vtuber.action_oper import ActionOper
from func.draw.draw_core import DrawCore
from func.nsfw.nsfw_core import NsfwCore
from func.image.image_core import ImageCore
from func.search.search_core import SearchCore
from func.dance.dance_core import DanceCore
from func.cmd.cmd_core import CmdCore

from func.gobal.data import VtuberData
from func.gobal.data import TTsData
from func.gobal.data import LLmData
from func.gobal.data import SingData
from func.gobal.data import CommonData
from func.translate.duckduckgo_translate import DuckduckgoTranslate

# 加载配置
config = defaultConfig().get_config()
# 设置控制台日志
log = DefaultLog().getLogger()

commonData = CommonData()  #基础数据
Ai_Name = commonData.Ai_Name  # Ai名称

# 重定向print输出到日志文件
def print(*args, **kwargs):
    log.info(*args, **kwargs)

log.info("======================================")
log.warning(
    """                                                                                                                                      
                      ......                   .]]`         ,]].          
                     /@@@@@\                 =@@@@@^      ./@@@@@`        
   @@@@@@@@@@@      /@@@@@@@@.        ,]]]]]]]/@@@@@\]]]]]@@@@@@]]]]]]]]  
   @@@@@@@@@@@    ,@@@@@`@@@@@`       =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  
   @@@@^ =@@@@   /@@@@@`  \@@@@@`     ,[[[[[[[[[[[[[\@@@@@[[[[[[[[[[[[[[  
   @@@@^ =@@@@ /@@@@@/ .]` =@@@@@@`     .]]]]]]]]]]]/@@@@@]]]]]]]]]]]]    
   @@@@^ =@@@@@@@@@@`\@@@@` .\@@@@@@\.  .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    
   @@@@^ =@@@@@@@@`   \@@@@`  ,\@@@@`   .[[[[[[[[[[[\@@@@@[[[[[[[[[[[[    
   @@@@^ =@@@@.@`      \@@@/.   .\@`  OOOOOOOOOOOOOOO@@@@@OOOOOOOOOOOOOO^ 
   @@@@^ =@@@@          .             @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@^ 
   @@@@^ =@@@@ O@@@@@@@@@@@@@@@@@^    [[[[[[[[[[[[[[\OOOOO[[[[[[[[[[[[[[` 
   @@@@^ =@@@@ O@@@@@@@@@@@@@@@@@^    ,]]]]]]]]]]]]]@@@@@\]]]]]]]]]]]]]]. 
   @@@@^ =@@@@             /@@@@@`    =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@. 
   @@@@@@@@@@@           ./@@@@@.     ,[[[[[[[[[[[@@@@@@@@@@[[[[[[[[[[[[. 
   @@@@@@@@@@@          ,@@@@@/                ]@@@@@@@\@@@@@@\`          
   @@@@^ =@@@@         =@@@@@/         .,]]O@@@@@@@@@/  ,@@@@@@@@@@@\]]]` 
                     ./@@@@@`         O@@@@@@@@@@@/`       [@@@@@@@@@@@@. 
                     ,[@@@@`          .@@@@@@O[`              .[O@@@@@@.  
                         ..                                                                                                               
"""
)

log.info(f"开始启动人工智能【{Ai_Name}】！")
log.info("源码地址：https://github.com/worm128/ai-yinmei")
log.info("整合包地址：https://www.bilibili.com/video/BV1zD421H76q/")
log.info("B站频道：程序猿的退休生活")
log.info("开发者：Winlone")
log.info("QQ群：27831318")

# 定时器
sched1 = AsyncIOScheduler(timezone="Asia/Shanghai")

# 1.b站直播间 2.api web
mode = config["mode"]

duckduckgoTranslate = DuckduckgoTranslate()  # 翻译
cmdCore = CmdCore()

# ============= LLM参数 =====================
llmData = LLmData()  # llm数据
llmCore = LLmCore()  # llm核心
# ============================================

# ============= 绘画参数 =====================
drawCore = DrawCore()
# ============================================

# ============= 搜图参数 =====================
imageCore = ImageCore()
# ============================================

# ============= 搜文参数 =====================
searchCore = SearchCore()
# ============================================

# ============= 唱歌参数 =====================
singData = SingData()  # 唱歌数据
singCore = SingCore()  # 唱歌核心
# ============================================

# ============= B站直播间 =====================
room_id = config["blivedm"]["room_id"]  # 输入直播间编号
# ******** blivedm ********
# b站直播身份验证：
SESSDATA = config["blivedm"]["sessdata"]
session: Optional[aiohttp.ClientSession] = None

# 在B站开放平台申请的开发者密钥
ACCESS_KEY_ID = config["blivedm"]["ACCESS_KEY_ID"]
ACCESS_KEY_SECRET = config["blivedm"]["ACCESS_KEY_SECRET"]
# 在B站开放平台创建的项目ID
APP_ID = config["blivedm"]["APP_ID"]
# 在B站主播身份码
ROOM_OWNER_AUTH_CODE = config["blivedm"]["ROOM_OWNER_AUTH_CODE"]
# ============================================

# ============= api web =====================
app = Flask(__name__, template_folder="./html")
sched1 = APScheduler()
sched1.init_app(app)
# ============================================

# ============= OBS直播软件控制 ================
# obs直播软件连接
obs = ObsInit().get_ws()
# vtuber皮肤连接
VtuberInit().get_ws()
# ============================================

# ============= 跳舞、表情视频 ================
danceCore = DanceCore()
# ============================================

# ============= 鉴黄 =====================
nsfwCore = NsfwCore()
# ============================================

# ============= 语音合成 =====================
ttsData = TTsData()  # 语音数据
ttsCore = TTsCore() # 语音核心
# ============================================

# ============= vtuber操作 =====================
vtuberData = VtuberData()  # vtuber数据
actionOper = ActionOper()  # 动作核心
emoteOper = EmoteOper() # 表情初始化
# ========================================

log.info("--------------------")
log.info("AI虚拟主播-启动成功！")
log.info("--------------------")
log.info("======================================")

# 执行指令
@app.route("/cmd", methods=["GET"])
def http_cmd():
    cmdstr = request.args["cmd"]
    log.info(f'执行指令："{cmdstr}"')
    cmdCore.cmd("all",cmdstr,"0", "http_cmd")
    return jsonify({"status": "成功"})

# http说话复读
@app.route("/say", methods=["POST"])
def http_say():
    text = request.data.decode("utf-8")
    tts_say_thread = Thread(target=ttsCore.tts_say, args=(text,))
    tts_say_thread.start()
    return jsonify({"status": "成功"})

# http人物表情输出
@app.route("/emote", methods=["POST"])
def http_emote():
    data = request.json
    text = data["text"]
    emote_thread1 = Thread(target=emoteOper.emote_ws, args=(1, 0.2, text))
    emote_thread1.start()
    return "ok"

# http唱歌接口处理
@app.route("/http_sing", methods=["GET"])
def http_sing():
    songname = request.args["songname"]
    username = "所有人"
    singCore.http_sing(songname,username)
    return jsonify({"status": "成功"})

# http绘画接口处理
@app.route("/http_draw", methods=["GET"])
def http_draw():
    drawname = request.args["drawname"]
    drawcontent = request.args["drawcontent"]
    username = "所有人"
    drawCore.http_draw(drawname,drawcontent,username)
    return jsonify({"status": "成功"})

# http更换场景
@app.route("/http_scene", methods=["GET"])
def http_scene():
    scenename = request.args["scenename"]
    actionOper.changeScene(scenename)
    return jsonify({"status": "成功"})


# http接口处理
@app.route("/msg", methods=["POST"])
def input_msg():
    data = request.json
    query = data["msg"]  # 获取弹幕内容
    uid = data["uid"]  # 获取用户昵称
    user_name = data["username"]  # 获取用户昵称
    traceid = str(uuid.uuid4())
    msg_deal(traceid, query, uid, user_name)
    return jsonify({"status": "成功"})


# 聊天回复弹框处理
@app.route("/chatreply", methods=["GET"])
def chatreply():
    CallBackForTest = request.args.get("CallBack")
    jsonStr = ttsCore.http_chatreply()
    if CallBackForTest is not None:
        jsonStr = CallBackForTest + jsonStr
    return jsonStr

# 聊天
@app.route("/chat", methods=["POST", "GET"])
def chat():
    CallBackForTest = request.args.get("CallBack")
    uid = request.args.get("uid")
    username = request.args.get("username")
    text = request.args.get("text")
    jsonStr = llmCore.http_chat(text,uid,username)
    if CallBackForTest is not None:
        jsonStr = CallBackForTest + jsonStr
    return jsonStr


# 点播歌曲列表
@app.route("/songlist", methods=["GET"])
def songlist():
    CallBackForTest = request.args.get("CallBack")
    jsonstr = singCore.http_songlist(CallBackForTest)
    if CallBackForTest is not None:
        jsonstr = CallBackForTest + jsonstr
    return jsonstr


# blivedm弹幕监听
async def blivedm_start():
    await run_single_client()


# SessData会话监听
async def blivedm_start2():
    global session
    init_session()
    try:
        await run_single_client2()
    finally:
        await session.close()


def init_session():
    cookies = http.cookies.SimpleCookie()
    cookies["SESSDATA"] = SESSDATA
    cookies["SESSDATA"]["domain"] = "bilibili.com"

    global session
    session = aiohttp.ClientSession()
    session.cookie_jar.update_cookies(cookies)


# sessData方式监听
async def run_single_client2():
    """
    演示监听一个直播间
    """
    global session

    client = blivedm.BLiveClient(room_id, session=session)
    handler = MyHandler2()
    client.set_handler(handler)

    client.start()
    try:
        await client.join()
    finally:
        await client.stop_and_close()


# 开放平台方式监听
async def run_single_client():
    """
    演示监听一个直播间
    """
    client = blivedm.OpenLiveClient(
        access_key_id=ACCESS_KEY_ID,
        access_key_secret=ACCESS_KEY_SECRET,
        app_id=APP_ID,
        room_owner_auth_code=ROOM_OWNER_AUTH_CODE,
    )
    handler = MyHandler()
    client.set_handler(handler)

    client.start()
    try:
        await client.join()
    finally:
        await client.stop_and_close()


class MyHandler2(blivedm.BaseHandler):
    # 演示如何添加自定义回调
    _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()

    # 入场消息回调
    def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
        log.info(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
                 f" uname={command['data']['uname']}")
        user_name = command["data"]["uname"]  # 获取用户昵称
        user_id = command["data"]["uid"]  # 获取用户uid
        time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.info(f"{time1}:粉丝[{user_name}]进入了直播间")
        # 46130941：老爸  333472479：吟美
        if all([user_id != not_allow_userid for not_allow_userid in llmData.welcome_not_allow]):
            # 加入欢迎列表
            llmData.WelcomeList.append(user_name)

    _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
        log.info(f'[{client.room_id}] 心跳2')


class MyHandler(blivedm.BaseHandler):
    # 心跳
    def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
        log.info(f'[{client.room_id}] 心跳1')

    # 弹幕获取
    def _on_open_live_danmaku(self, client: blivedm.OpenLiveClient, message: open_models.DanmakuMessage):
        log.info(f'{message.uname}：{message.msg}')
        traceid = str(uuid.uuid4())
        msg_deal(traceid, message.msg, message.msg_id, message.uname)

    # 赠送礼物
    def _on_open_live_gift(self, client: blivedm.OpenLiveClient, message: open_models.GiftMessage):
        coin_type = '金瓜子' if message.paid else '银瓜子'
        total_coin = message.price * message.gift_num
        log.info(f'[{message.room_id}] {message.uname} 赠送{message.gift_name}x{message.gift_num}'
                 f' （{coin_type}x{total_coin}）')
        username = message.uname
        giftname = message.gift_name
        num = message.gift_num
        text = f"谢谢‘{username}’赠送的{num}个{giftname}"
        log.info(text)
        tts_say_thread = Thread(target=ttsCore.tts_say, args=(text,))
        tts_say_thread.start()

    def _on_open_live_buy_guard(self, client: blivedm.OpenLiveClient, message: open_models.GuardBuyMessage):
        log.info(f'[{message.room_id}] {message.user_info.uname} 购买 大航海等级={message.guard_level}')
        username = message.user_info.uname
        level = message.guard_level
        text = f"非常谢谢‘{username}’购买 大航海等级{level},{Ai_Name}大小姐在这里给你跪下了"
        log.info(text)
        tts_say_thread = Thread(target=ttsCore.tts_say, args=(text,))
        tts_say_thread.start()

    def _on_open_live_super_chat(
            self, client: blivedm.OpenLiveClient, message: open_models.SuperChatMessage
    ):
        log.info(f'[{message.room_id}] 醒目留言 ¥{message.rmb} {message.uname}：{message.message}')
        username = message.uname
        rmb = message.rmb
        text = f"谢谢‘{username}’赠送的¥{rmb}元,她留言说\"{message.message}\""
        log.info(text)
        tts_say_thread = Thread(target=ttsCore.tts_say, args=(text,))
        tts_say_thread.start()

    def _on_open_live_super_chat_delete(
            self, client: blivedm.OpenLiveClient, message: open_models.SuperChatDeleteMessage
    ):
        log.info(f'[{message.room_id}] 删除醒目留言 message_ids={message.message_ids}')

    def _on_open_live_like(self, client: blivedm.OpenLiveClient, message: open_models.LikeMessage):
        log.info(f'{message.uname} 点赞')
        username = message.uname
        text = f"谢谢‘{username}’点赞,{Ai_Name}大小姐最爱你了"
        log.info(text)
        tts_say_thread = Thread(target=ttsCore.tts_say, args=(text,))
        tts_say_thread.start()


def msg_deal(traceid, query, uid, user_name):
    """
    处理弹幕消息
    """
    # traceid = str(uuid.uuid4())
    # 过滤特殊字符
    query = nsfwCore.str_filter(query)
    log.info(f"[{traceid}]弹幕捕获：[{user_name}]:{query}")  # 打印弹幕信息

    # 命令执行
    if cmdCore.cmd(traceid, query, uid, user_name):
        return

    # 说话不执行任务
    text = ["\\"]
    num = StringUtil.is_index_contain_string(text, query)  # 判断是不是需要搜索
    if num > 0:
        return

    # 跳舞表情
    if danceCore.msg_deal_emotevideo(traceid, query, uid, user_name):
        return

    # 搜索引擎查询
    if searchCore.msg_deal(traceid, query, uid, user_name):
        return

    # 搜索图片
    if imageCore.msg_deal(traceid, query, uid, user_name):
        return

    # 绘画
    if drawCore.msg_deal(traceid, query, uid, user_name):
        return

    # 唱歌
    if singCore.msg_deal(traceid, query, uid, user_name):
        return

    # 跳舞
    if danceCore.msg_deal_dance(traceid, query, uid, user_name):
        return

    # 换装
    if actionOper.msg_deal_clothes(traceid, query, uid, user_name):
        return

    # 切换场景
    if actionOper.msg_deal_scene(traceid, query, uid, user_name):
        return

    # 聊天入口处理
    llmCore.msg_deal(traceid, query, uid, user_name)


def main():
    # 初始化衣服
    emoteOper.emote_ws(1, 0.2, "初始化")  # 解除当前衣服
    emoteOper.emote_ws(1, 0.2, "便衣")  # 穿上新衣服
    vtuberData.now_clothes = "便衣"

    # 跳舞表情
    # content = ""
    # for str in emote_list:
    #     content= content + str + ","
    # if content!="":
    #     obs.show_text("表情列表",content)

    # 停止所有视频播放
    obs.play_video("唱歌视频", "")
    obs.control_video("唱歌视频", VideoControl.STOP.value)
    obs.control_video("video", VideoControl.STOP.value)
    obs.control_video("表情", VideoControl.STOP.value)
    obs.play_video("伴奏", "")
    obs.control_video("伴奏", VideoControl.STOP.value)

    # 切换场景:初始化
    actionOper.init_scene()

    # 场景[白天黑夜]判断
    actionOper.check_scene_time()

    # 吟美状态提示:初始化清空
    obs.show_text("状态提示", "")

    if mode == 1 or mode == 2:
        # LLM回复
        sched1.add_job(func=llmCore.check_answer, trigger="interval", seconds=1, id="answer", max_instances=100)
        # tts语音合成
        sched1.add_job(func=ttsCore.check_tts, trigger="interval", seconds=1, id="tts", max_instances=1000)
        # 绘画
        sched1.add_job(func=drawCore.check_draw, trigger="interval", seconds=1, id="draw", max_instances=50)
        # 搜索资料
        sched1.add_job(func=searchCore.check_text_search, trigger="interval", seconds=1, id="text_search", max_instances=50)
        # 搜图
        sched1.add_job(func=imageCore.check_img_search, trigger="interval", seconds=1, id="img_search", max_instances=50)
        # 唱歌转换
        sched1.add_job(func=singCore.check_sing, trigger="interval", seconds=1, id="sing", max_instances=50)
        # 歌曲清单播放
        sched1.add_job(func=singCore.check_playSongMenuList, trigger="interval", seconds=1, id="playSongMenuList", max_instances=50)
        # 跳舞
        sched1.add_job(func=danceCore.check_dance, args=[sched1], trigger="interval", seconds=1, id="dance", max_instances=10)
        # 时间判断场景[白天黑夜切换]
        sched1.add_job(func=actionOper.check_scene_time, trigger="cron", hour="6,17,18", id="scene_time")
        # 欢迎语
        sched1.add_job(func=llmCore.check_welcome_room, trigger="interval", seconds=20, id="welcome_room", max_instances=50)
        sched1.start()

    if mode == 1 or mode == 2:
        # 开启web
        app_thread = Thread(target=apprun)
        app_thread.start()

    if mode == 1:
        # bilibili-api弹幕监听
        # sync(room.connect())
        # blivedm弹幕监听
        # asyncio.run(blivedm_start())
        asyncio.run(listen_blivedm_task())
    else:
        while True:
            time.sleep(10)
    log.info("结束")


# 监听B站直播间两个监听组合【开放平台+SessData会话】
async def listen_blivedm_task():
    task1 = asyncio.create_task(blivedm_start())
    task2 = asyncio.create_task(blivedm_start2())
    results = await asyncio.gather(task1, task2)


# http服务
def apprun():
    # 禁止输出日志
    app.logger.disabled = True
    # 启动web应用
    app.run(host="0.0.0.0", port=1800)

if __name__ == "__main__":
    main()
