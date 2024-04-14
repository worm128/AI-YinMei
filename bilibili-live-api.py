# b站AI直播对接text-generation-webui聚合文本LLM模型
import json
import datetime
import queue
import subprocess
import threading
import os
import time
import requests
import base64
import io
import random
import re
import traceback
import websocket
import logging

from func.obs.obs_websocket import ObsWebSocket,VideoStatus,VideoControl
from func.tools.file_util import FileUtil
from func.tools.string_util import StringUtil
from func.search import crawler,baidusearch
from io import BytesIO
from PIL import Image
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bilibili_api import live, sync, Credential
from duckduckgo_search import DDGS
from threading import Thread
from urllib.parse import quote
from flask import Flask, jsonify, request, render_template
from flask_apscheduler import APScheduler
from urllib import parse

Ai_Name="吟美"  #Ai名称
print("=====================================================================")
print(f"开始启动人工智能{Ai_Name}！")
print(
    "组成功能：LLM大语言模型+bilibili直播对接+TTS微软语音合成+MPV语音播放+VTube Studio人物模型+pynput表情控制+stable-diffusion-webui绘画"
)
print("源码地址：https://github.com/worm128/ai-yinmei")
print("开发者：Winlone")
print("QQ群：27831318")
print("=====================================================================")

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
sched1 = AsyncIOScheduler(timezone="Asia/Shanghai")
#设置控制台日志
today = datetime.date.today().strftime("%Y-%m-%d")
logging.basicConfig(level=logging.INFO, encoding="utf-8", format='%(asctime)s %(levelname)s %(filename)s %(name)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(filename=f"./logs/log_{today}.txt", encoding="utf-8")])
# 定时器只输出error
my_logging = logging.getLogger("apscheduler.executors.default")
my_logging.setLevel('ERROR')
#关闭页面访问日志
my_logging = logging.getLogger("werkzeug")
my_logging.setLevel('ERROR')
# 重定向print输出到日志文件
def print(*args, **kwargs):
    logging.info(*args, **kwargs)

#1.b站直播间 2.api web 3.双开
mode=int(input("1.b站直播间 2.api web：") or "1")

#代理
proxies = {"http": "socks5://127.0.0.1:10806", "https": "socks5://127.0.0.1:10806"}
duckduckgo_proxies="socks5://127.0.0.1:10806"

#线程锁
create_song_lock = threading.Lock()
play_song_lock = threading.Lock()
say_lock = threading.Lock()
# ============= LLM参数 =====================
QuestionList = queue.Queue()  # LLM回复问题
QuestionName = queue.Queue()  
AnswerList = queue.Queue()  #Ai回复队列
EmoteList = queue.Queue()  #表情队列
ReplyTextList = queue.Queue()   #Ai回复框文本队列
history = []
is_ai_ready = True  # 定义ai回复是否转换完成标志
is_tts_ready = True  # 定义语音是否生成完成标志
AudioCount = 0
SayCount = 0
history_count = 2  # 定义最大对话记忆轮数,请注意这个数值不包括扮演设置消耗的轮数，只有当enable_history为True时生效
enable_role = False  # 是否启用扮演模式
# ============================================

# ============= 本地模型加载 =====================
# 模型加载方式
local_llm_type = int(input("本地LLM模型类型(1.fastgpt 2.text-generation-webui): ") or "1")
tgw_url = "192.168.2.58:5000"
fastgpt_url = "192.168.2.198:3000"
fastgpt_authorization="Bearer fastgpt-5StPybD20P3Ymg2EDZpXe4nCjiP070TINQDRJTgBBWQhMLxDUck6W6Oeio4sx"
#ai吟美：fastgpt-5StPybD20P3Ymg2EDZpXe4nCjiP070TINQDRJTgBBWQhMLxDUck6W6Oeio4sx
#openku-chatgpt3.5：fastgpt-ySHfeoltpvRV4lyqvGBqiUvJpzMiC0d3nOFaheT1dTHlk9KA4EHR6EujKzX
# ============================================

# ============= 绘画参数 =====================
drawUrl = "192.168.2.58:7860"
is_drawing = 3  # 1.绘画中 2.绘画完成 3.绘画任务结束
width = 980  # 图片宽度
height = 500  # 图片高度
DrawQueueList = queue.Queue()  # 画画队列
physical_save_folder="J:\\ai\\ai-yinmei\\porn\\"  #绘画保存图片物理路径
# ============================================

# ============= 搜图参数 =====================
SearchImgList = queue.Queue()
is_SearchImg = 2  # 1.搜图中 2.搜图完成
# ============================================

# ============= 搜文参数 =====================
SearchTextList = queue.Queue()
is_SearchText = 2  # 1.搜文中 2.搜文完成
# ============================================

# ============= 唱歌参数 =====================
singUrl = "192.168.2.58:1717"
SongQueueList = queue.Queue()  # 唱歌队列
SongMenuList = queue.Queue()  # 唱歌显示
SongNowName={} # 当前歌曲
is_singing = 2  # 1.唱歌中 2.唱歌完成
is_creating_song = 2  # 1.生成中 2.生成完毕
# ============================================

# ============= B站直播间 =====================
# b站直播身份验证：
#实例化 Credential 类
cred = Credential(
    sessdata="f1e5bc7a%2C1728621982%2Ceea71%2A42CjBll5YCbc6qdfIDhUAiWftNX4EW36tuxARKyAmQ1za01VqxK_WIZPL79SJ9az0-gyASVnJ2NWJzRHo4Uk5la28tWlVrOFowZk5uNEpmd09VQTEzMkp0eUFJWFl3ZVpHM3VHaFpsZk5tN3RMSmNMdHc5V2tJQWZiSExNZnhLUEh3dk5NemE0d1hnIIEC",
    buvid3="C08180D1-DDCD-1766-0162-FB77DF0BDAE597566infoc"
)
room_id = int(input("输入你的B站直播间编号: ") or "31814714")  # 输入直播间编号
room = live.LiveDanmaku(room_id, credential=cred, debug=False)  # 连接弹幕服务器
#sender = live.LiveRoom(room_id, credential=cred)  # 用来发送弹幕
# 自己的UID 可以手动填写也可以根据直播间号获取
#my_uid = sync(sender.get_room_info())["room_info"]["uid"]
# ============================================

# ============= api web =====================
app = Flask(__name__,template_folder='./html')
if mode==1 or mode==2:
   sched1 = APScheduler()
   sched1.init_app(app)
# ============================================
   
# ============= Vtuber表情 =====================
def run_forever():
    ws.run_forever(ping_timeout=1)
def on_open(ws):
    auth()
ws = websocket.WebSocketApp("ws://127.0.0.1:8001",on_open = on_open)
vtuber_pluginName="winlonebot"
vtuber_pluginDeveloper="winlone"
vtuber_authenticationToken="4ae2f64ec9d1fe7bddc1b2edfb96292b28ab8b83554b50270a7fe83b3b3b8d05"
# ============================================

# ============= 鉴黄 =====================
filterEn="huge breasts,open clothes,topless,voluptuous,breast,prostitution,erotic,armpit,milk,leaking,spraying,woman,cupless latex,latex,tits,boobs,lingerie,chest,seductive,poses,pose,leg,posture,alluring,milf,on bed,mature,slime,open leg,full body,bra,lace,bikini,full nude,nude,bare,one-piece,navel,cleavage,swimsuit,naked,adult,nudity,beautiful breasts,nipples,sex,Sexual,vaginal,penis,large penis,pantie,leotards,anal"
filterCh="奶子,乳房"
progress_limit=1   #绘图大于多少百分比进行鉴黄
nsfw_limit=0.2  #nsfw黄图值大于多少进行绘画屏蔽，值越大越是黄图
nsfw_progress_limit=0.2 #nsfw黄图-绘画进度鉴黄
nsfw_lock = threading.Lock()
# ============================================

# ============= 语音合成 =====================
#bert-vists
bert_vists_url="192.168.2.58:5000"
speaker_name="珊瑚宫心海[中]"
sdp_ratio=0.2  #SDP在合成时的占比，理论上此比率越高，合成的语音语调方差越大
noise=0.2 #控制感情变化程度，默认0.2
noisew=0.9 #控制音节发音变化程度，默认0.9
speed=1  #语速
#gpt-SoVITS
gtp_vists_url="192.168.2.58:9880"

# ============================================

# ============= OBS直播软件控制 =====================
obs = ObsWebSocket(host="192.168.2.198",port=4455,password="123456")
dance_path = 'H:\\人工智能\\ai\\跳舞视频\\横屏'
dance_video = FileUtil.get_child_file_paths(dance_path)  #跳舞视频
emote_path = 'H:\\人工智能\\ai\\跳舞视频\\表情'
emote_font = 'H:\\人工智能\\ai\\跳舞视频\\表情\\表情符号'
emote_video = FileUtil.get_child_file_paths(emote_path)  #表情视频
emote_list = FileUtil.get_subfolder_names(emote_font) #表情清单显示
DanceQueueList = queue.Queue()  # 跳舞队列
is_dance = 2  #1.正在跳舞 2.跳舞完成
emote_video_lock = threading.Lock()
emote_now_path=""
dance_now_path=""
singdance_now_path=""
# ============================================

# ============= 服装 =====================
now_clothes=""  #当前服装穿着
# ========================================

# ============= 场景 =====================
song_background={"海岸花坊":"J:\\ai\\背景音乐\\海岸花坊.rm",
                 "神社":"J:\\ai\\背景音乐\\神社.mp3",
                 "清晨房间":"J:\\ai\\背景音乐\\清晨房间.mp3",
                 "粉色房间":"J:\\ai\\背景音乐\\粉色房间.rm",
                 "花房":"J:\\ai\\背景音乐\\花房.mp3"}
# ========================================

# ============= 欢迎列表 =====================
WelcomeList = []  # welcome欢迎列表
# ========================================

print("--------------------")
print("AI虚拟主播-启动成功！")
print("--------------------")

# 用户进入直播间
@room.on("INTERACT_WORD")
async def in_liveroom(event):
    user_name = event["data"]["data"]["uname"]  # 获取用户昵称
    user_id = event["data"]["data"]["uid"]  # 获取用户uid
    time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    print(f"{time1}:粉丝[{user_name}]进入了直播间")
    # 46130941：老爸  333472479：吟美
    if user_id!=46130941 and user_id!=333472479:
        # 加入欢迎列表
        WelcomeList.append(user_name)

# B站弹幕处理
@room.on("DANMU_MSG")  # 弹幕消息事件回调函数
async def input_msg(event):
    # 发送者UID
    uid = event["data"]["info"][2][0]
    # 排除自己发送的弹幕
    # if uid == my_uid:
    #     return
    
    query = event["data"]["info"][1]  # 获取弹幕内容
    user_name = event["data"]["info"][2][1]  # 获取用户昵称
    #消息处理分发
    msg_deal(query,uid,user_name)

# 收到礼物
@room.on('SEND_GIFT')
async def on_gift(event):
    username=event["data"]["data"]["uname"]
    giftname=event["data"]["data"]["giftName"]
    num=event["data"]["data"]["num"]
    text = f"谢谢‘{username}’赠送的{num}个{giftname}"
    print(text)
    tts_say_thread = Thread(target=tts_say,args=(text,))
    tts_say_thread.start()

# http唱歌接口处理
@app.route("/http_sing", methods=["GET"])
def http_sing():
    songname = request.args["songname"]
    username = "所有人"
    print(f"http唱歌接口处理：\"{username}\"点播歌曲《{songname}》")
    song_json = {"prompt": songname, "username": username}
    SongQueueList.put(song_json)

# http绘画接口处理
@app.route("/http_draw", methods=["GET"])
def http_draw():
    drawname = request.args["drawname"]
    drawcontent = request.args["drawcontent"]
    username = "所有人"
    print(f"http绘画接口处理：\"{username}\"绘画《{drawname}》，{drawcontent}")
    draw_json = {"prompt": drawname, "drawcontent":drawcontent, "username": username, "isExtend": False}
    DrawQueueList.put(draw_json)

# http绘画接口处理
@app.route("/http_scene", methods=["GET"])
def http_scene():
    scenename = request.args["scenename"]
    changeScene(scenename)

# http接口处理
@app.route("/msg", methods=["POST"])
def input_msg():
    data = request.json
    query = data["msg"]  # 获取弹幕内容
    uid = data["uid"]  # 获取用户昵称
    user_name = data["username"]  # 获取用户昵称
    msg_deal(query,uid,user_name)
    return jsonify({"status": "成功"})

# 聊天回复弹框处理
@app.route("/chatreply", methods=["GET"])
def chatreply():
    global ReplyTextList
    CallBackForTest=request.args.get('CallBack')
    text=""
    status="失败"
    if not ReplyTextList.empty():
        text = ReplyTextList.get();
        status = "成功"
    str = "({\"status\": \""+status+"\",\"content\": \""+text.replace("\"","'").replace("\r"," ").replace("\n","<br/>")+"\"})"
    if CallBackForTest is not None:
        str=CallBackForTest+str
    return str

# 点播歌曲列表
@app.route("/songlist", methods=["GET"])
def songlist():
    global SongMenuList
    global SongNowName
    jsonstr =[]
    CallBackForTest=request.args.get('CallBack')
    if len(SongNowName)>0:
        #当前歌曲
        username=SongNowName["username"]
        songname=SongNowName["songname"]
        text = f"'{username}'点播《{songname}》"
        jsonstr.append({"songname":text})
    #播放歌曲清单
    for i in range(SongMenuList.qsize()):
        data = SongMenuList.queue[i]
        username=data["username"]
        songname=data["songname"]
        text = f"'{username}'点播《{songname}》"
        jsonstr.append({"songname":text})
    str = "({\"status\": \"成功\",\"content\": "+json.dumps(jsonstr)+"})"
    if CallBackForTest is not None:
       temp = CallBackForTest+str
    return temp

def msg_deal(query,uid,user_name):
    """
    处理弹幕消息
    """
    query=filter(query,filterCh)
    print(f"[{user_name}]:{query}")  # 打印弹幕信息

    # 命令执行
    status = cmd(query)  
    if status==1:
        print(f"执行命令：{query}")
        return

    # 说话不执行任务
    text = ["\\"]
    num = is_index_contain_string(text, query)  # 判断是不是需要搜索
    if num > 0:
        return
    
    #跳舞表情
    text = ["#"]
    is_contain = has_string_reg_list(f"^{text}", query)
    if is_contain is not None:
        num = is_index_contain_string(text, query)
        queryExtract = query[num : len(query)]  # 提取提问语句
        queryExtract = queryExtract.strip()
        print("跳舞表情：" + queryExtract)
        video_path=""
        if queryExtract=="rnd":
            rnd_video = random.randrange(0, len(emote_video))
            video_path = emote_video[rnd_video]
        else:
            matches_list = StringUtil.fuzzy_match_list(queryExtract,emote_video)
            if len(matches_list)>0:
               rnd_video = random.randrange(0, len(matches_list))
               video_path = matches_list[rnd_video]
        # 第一次播放
        if video_path!="":
            if is_dance==1:
                emote_play_thread = Thread(target=emote_play,args=(video_path,))
                emote_play_thread.start()
            else:
                emote_play_thread = Thread(target=emote_play_nodance,args=(video_path,))
                emote_play_thread.start()
        return
    
    #跳舞中不执行其他任务
    if is_dance==1:
       return

    # 搜索引擎查询
    text = ["查询", "查一下", "搜索"]
    is_contain = has_string_reg_list(f"^{text}", query)
    if is_contain is not None:
        num = is_index_contain_string(text, query)
        queryExtract = query[num : len(query)]  # 提取提问语句
        queryExtract = queryExtract.strip()
        print("搜索词：" + queryExtract)
        if queryExtract=="":
           return
        text_search_json = {"prompt": queryExtract, "uid": uid, "username": user_name}
        SearchTextList.put(text_search_json)
        return

    # 搜索图片
    text = ["搜图", "搜个图", "搜图片", "搜一下图片"]
    is_contain = has_string_reg_list(f"^{text}", query)
    if is_contain is not None:
        num = is_index_contain_string(text, query)
        queryExtract = query[num : len(query)]  # 提取提问语句
        queryExtract = queryExtract.strip()
        print("搜索图：" + queryExtract)
        if queryExtract=="":
           return
        img_search_json = {"prompt": queryExtract, "username": user_name}
        SearchImgList.put(img_search_json)
        return

    # 绘画
    text = ["画画", "画一个", "画一下", "画个"]
    is_contain = has_string_reg_list(f"^{text}", query)
    if is_contain is not None:
        num = is_index_contain_string(text, query)
        queryExtract = query[num : len(query)]  # 提取提问语句
        queryExtract = queryExtract.strip()
        print("绘画提示：" + queryExtract)
        if queryExtract=="":
           return
        draw_json = {"prompt": queryExtract, "drawcontent":"", "username": user_name, "isExtend": True}
        # 加入绘画队列
        DrawQueueList.put(draw_json)
        return

    # 唱歌
    text = ["唱一下", "唱一首", "唱歌", "点歌", "点播"]
    is_contain = has_string_reg_list(f"^{text}", query)
    if is_contain is not None:
        num = is_index_contain_string(text, query)
        queryExtract = query[num : len(query)]  # 提取提问语句
        queryExtract = queryExtract.strip()
        print("唱歌提示：" + queryExtract)
        if queryExtract=="":
           return
        song_json = {"prompt": queryExtract, "username": user_name}
        SongQueueList.put(song_json)
        return

    # 跳舞
    text = ["跳舞", "跳一下", "舞蹈"]
    is_contain = has_string_reg_list(f"^{text}", query)
    if is_contain is not None:
       num = is_index_contain_string(text, query)
       queryExtract = query[num : len(query)]  # 提取提问语句
       queryExtract = queryExtract.strip()
       print("跳舞提示：" + queryExtract)
       video_path=""
       #提示语为空，随机视频
       if queryExtract=="":
           rnd_video = random.randrange(0, len(dance_video))
           video_path = dance_video[rnd_video]
       else:
           matches_list = StringUtil.fuzzy_match_list(queryExtract,dance_video)
           if len(matches_list)>0:
              rnd_video = random.randrange(0, len(matches_list))
              video_path = matches_list[rnd_video]
       #加入跳舞队列
       if video_path!="":
          dance_json = {"prompt": queryExtract, "username": user_name, "video_path": video_path}
          DanceQueueList.put(dance_json)
          return
       else:
          print("跳舞视频不存在：" + queryExtract)
          return

    # 换装
    global now_clothes
    text = ["换装", "换衣服", "穿衣服"]
    num = is_index_contain_string(text, query)
    if num > 0:
       queryExtract = query[num : len(query)]  # 提取提问语句
       queryExtract = queryExtract.strip()
       print("换装提示：" + queryExtract)
       # 开始唱歌服装穿戴
       emote_ws(1, 0, now_clothes)  #解除当前衣服
       emote_ws(1, 0, queryExtract)  #穿上新衣服
       now_clothes = queryExtract
       return
    
    # 切换场景
    text = ["切换", "进入"]
    num = is_index_contain_string(text, query)
    if num > 0:
       queryExtract = query[num : len(query)]  # 提取提问语句
       queryExtract = queryExtract.strip()
       print("切换场景：" + queryExtract)
       changeScene(queryExtract)
       return
    
    #询问LLM
    llm_json = {"prompt": query, "uid": uid, "username": user_name}
    QuestionList.put(llm_json)  # 将弹幕消息放入队列

# 场景切换
def changeScene(sceneName):
    if allow_scene(sceneName)==True:
        # 切换场景
        obs.change_scene(sceneName)
        # 背景乐切换
        if sceneName in song_background:
            song = song_background[sceneName]
            if obs.get_video_status("背景音乐")==VideoStatus.PAUSE.value:
                obs.play_video("背景音乐",song)
                time.sleep(1)
                obs.control_video("背景音乐",VideoControl.PAUSE.value)
            else:
                obs.play_video("背景音乐",song)
            return True
        else:
            AnswerList.put(f"晚上{Ai_Name}不敢过去{sceneName}哦")
    return False

# 判断每一种时间段允许移动的场景
def allow_scene(queryExtract):
    now_time = time.strftime("%H:%M:%S", time.localtime())
    # 晚上允许进入的场景
    night = ["神社", "粉色房间", "海岸花坊"]
    if "18:00:00" <= now_time <= "24:00:00" or "00:00:00" < now_time < "06:00:00":
        num = is_index_contain_string(night, queryExtract)
        if num <= 0:
           return False
    return True

#表情播放[不用停止跳舞]
def emote_play_nodance(eomte_path):
    emote_video_lock.acquire()
    global emote_now_path
    print(f"播放表情:{eomte_path}")
    # 第一次播放
    if eomte_path!=emote_now_path:
       obs.play_video("表情",eomte_path)
    else:
       obs.control_video("表情",VideoControl.RESTART.value)
    # 赋值当前表情视频
    emote_now_path = eomte_path
    time.sleep(1)
    # 20秒超时停止播放
    sec=20
    while obs.get_video_status("表情")!=VideoStatus.END.value and sec>0:
          time.sleep(1)
          sec = sec - 1
    time.sleep(1)
    obs.control_video("表情",VideoControl.STOP.value)
    emote_video_lock.release()

#表情播放
def emote_play(eomte_path):
    emote_video_lock.acquire()
    global emote_now_path
    obs.control_video("video",VideoControl.PAUSE.value)
    print(f"播放表情:{eomte_path}")
    # 第一次播放
    if eomte_path!=emote_now_path:
       obs.play_video("表情",eomte_path)
    else:
       obs.control_video("表情",VideoControl.RESTART.value)
    # 赋值当前表情视频
    emote_now_path = eomte_path
    time.sleep(1)
    # 20秒超时停止播放
    sec=20
    while obs.get_video_status("表情")!=VideoStatus.END.value and sec>0:
          time.sleep(1)
          sec = sec - 1
    time.sleep(1)
    obs.control_video("表情",VideoControl.STOP.value)
    obs.control_video("video",VideoControl.PLAY.value)
    emote_video_lock.release()

# 命令控制：优先
def cmd(query):
    global is_ai_ready
    global is_singing
    global is_creating_song
    global is_SearchText
    global is_SearchImg
    global is_drawing
    global is_tts_ready
    global is_dance

    # 停止所有任务
    if query=="\\stop":
        is_singing = 2  # 1.唱歌中 2.唱歌完成
        # is_creating_song = 2  # 1.生成中 2.生成完毕
        is_SearchText = 2 # 1.搜索中 2.搜索完毕
        is_SearchImg = 2  # 1.搜图中 2.搜图完成
        is_drawing = 3  # 1.绘画中 2.绘画完成 3.绘图任务结束
        is_ai_ready = True  # 定义ai回复是否转换完成标志
        is_tts_ready = True  # 定义语音是否生成完成标志
        os.system('taskkill /T /F /IM song.exe')
        os.system('taskkill /T /F /IM mpv.exe')
        return 1
    if query=="\\dance":
        os.system('taskkill /T /F /IM song.exe')
        os.system('taskkill /T /F /IM mpv.exe')
        return 1
    #下一首歌
    if query=="\\next":
        os.system('taskkill /T /F /IM song.exe')
        is_singing = 2  # 1.唱歌中 2.唱歌完成
        return 1
    #停止跳舞
    if query=="\\停止跳舞":
        is_dance = 2  #1.正在跳舞 2.跳舞完成
        return 1
    return 0

# fastgpt知识库接口调用-LLM回复
def chat_fastgpt(content, uid, username):
    url = f"http://{fastgpt_url}/api/v1/chat/completions"
    headers = {"Content-Type": "application/json","Authorization":fastgpt_authorization}
    timestamp = time.time()
    data={
            "chatId": timestamp,
            "stream": False,
            "detail": False,
            "variables": {
                "uid": uid,
                "name": username
            },
            "messages": [
                {
                    "content": content,
                    "role": "user"
                }
            ]
    }
    try:
        response = requests.post(
            url, headers=headers, json=data, verify=False, timeout=(3, 60)
        )
    except Exception as e:
        print(f"【{content}】信息回复异常")
        return "我听不懂你说什么"
    assistant_message = response.json()["choices"][0]["message"]["content"]
    return assistant_message


# text-generation-webui接口调用-LLM回复
# mode:instruct/chat/chat-instruct  preset:Alpaca/Winlone(自定义)  character:角色卡Rengoku/Ninya
def chat_tgw(content, character, mode, preset,username):
    url = f"http://{tgw_url}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    history.append({"role": "user", "content": content})
    data = {
        "mode": mode,
        "character": character,
        "your_name": username,
        "messages": history,
        "preset": preset,
        "do_sample": True,
        "max_new_tokens":200,
        "seed": -1,
        "add_bos_token": True,
        "ban_eos_token": False,
        "skip_special_tokens": True,
        "instruction_template": "Alpaca",
    }
    try:
        response = requests.post(
            url, headers=headers, json=data, verify=False, timeout=(3, 60)
        )
    except Exception as e:
        print(f"【{content}】信息回复异常")
        return "我听不懂你说什么"
    assistant_message = response.json()["choices"][0]["message"]["content"]
    # history.append({"role": "assistant", "content": assistant_message})
    return assistant_message

# LLM回复
def aiResponseTry():
    global is_ai_ready
    try:
        ai_response()
    except Exception as e:
        print(f"【ai_response】发生了异常：{e}")
        logging.error(traceback.format_exc())
        is_ai_ready=True

# LLM回复
def ai_response():
    """
    从问题队列中提取一条，生成回复并存入回复队列中
    :return:
    """
    global is_ai_ready
    global QuestionList
    global history

    is_ai_ready = False
    llm_json = QuestionList.get()
    #参数提取
    uid = llm_json["uid"]
    username = llm_json["username"]
    prompt = llm_json["prompt"]

    # 用户查询标题
    title = prompt
    # query有值是搜索任务，没有值是聊天任务
    if "query" in llm_json:
       #搜索任务的查询字符，在query字段
       title = llm_json["query"]
       obs.show_text("状态提示",f"{Ai_Name}搜索问题\"{title}\"")
    else:
       obs.show_text("状态提示",f"{Ai_Name}思考问题\"{title}\"")

    # 身份判定
    shenfen=""
    if username=="程序猿的退休生活":
       shenfen="老爸说:"
    elif uid==0:
       shenfen=""
    else:
       shenfen=f"\"{username}\"说:"
    
    # fastgpt
    if local_llm_type == 1:
        username_prompt = f"{shenfen}{prompt}"
        #username_prompt = f"###{shenfen}对你说：###\n\"{prompt}\"。"
        response = chat_fastgpt(username_prompt, uid, username)
    # text-generation-webui
    elif local_llm_type == 2:
        username_prompt = f"{shenfen}{prompt}"
        response = chat_tgw(username_prompt, "Aileen Voracious", "chat", "Winlone",username)
        response = response.replace("You", username)
    # 过滤表情<>或者()标签
    response = filter_html_tags(response)
    obs.show_text("状态提示",f"{Ai_Name}思考问题\"{title}\"完成")
    
    # 切换场景
    if "粉色" in response or "睡觉" in response or "粉红" in response:
       changeScene("粉色房间")
    elif "清晨" in response or "早" in response or "睡醒" in response:
       changeScene("清晨房间")
    elif "祭拜" in response or "神社" in response or "寺庙" in response:
       changeScene("神社")
    elif "花房" in response or "花香" in response:
       changeScene("花房")
    elif "岸" in response or "海" in response:
       changeScene("海岸花坊")

    # 回复文本
    answer = f"{response}"

    # 日志输出
    current_question_count = QuestionList.qsize()
    print(f"[AI回复]{answer}")
    print(f"System>>[{username}]的回复已存入队列，当前剩余问题数:{current_question_count}")
    is_ai_ready = True  # 指示AI已经准备好回复下一个问题

    # 加入回复列表，并且后续合成语音
    json = {"question":title,"text":response,"lanuage":"AutoChange"}
    AnswerList.put(json)

# 过滤html标签
def filter_html_tags(text):
    pattern = r'<.*?>|\(.*?\)'  # 匹配尖括号内的所有内容
    return re.sub(pattern, '', text)

# duckduckgo搜索引擎搜索
textSearchNum=5
def duckduckgo_web_search(query):
    content = ""
    with DDGS(proxies=duckduckgo_proxies, timeout=20) as ddgs:
        try:
            ddgs_text_gen = ddgs.text(
                query,
                region="cn-zh",
                timelimit="d",
                backend="api",
                max_results=textSearchNum,
            )
            for r in ddgs_text_gen:
                content = r["body"]+";"+content
        except Exception as e: 
            print(f"web_search信息回复异常{e}")
            logging.error(traceback.format_exc())
    return content

# baidu搜索引擎搜索
def baidu_web_search(query):
    content = ""
    results = baidusearch.search(query, num_results=3, debug=0)
    if isinstance(results, list):
        print("search results：(total[{}]items.)".format(len(results)))
        for res in results:
            content = res["abstract"].replace("\n","").replace("\r","")+";"+content
    return content


# duckduckgo搜索引擎搜图片
def web_search_img(query):
    imageNum = 10
    imgUrl = ""
    with DDGS(proxies=duckduckgo_proxies, timeout=20) as ddgs:
        try:
            ddgs_images_gen = ddgs.images(
                query,
                region="cn-zh",
                safesearch="off",
                size="Medium",
                color="color",
                type_image=None,
                layout=None,
                license_image=None,
                max_results=imageNum,
            )
            i = 0
            random_number = random.randrange(0, imageNum)
            for r in ddgs_images_gen:
                if i == random_number:
                    imgUrl = r["image"]
                    print(f"图片地址：{imgUrl},搜索关键字:{query}")
                    break
                i = i + 1
        except Exception as e: 
            print(f"web_search_img信息回复异常{e}")
            logging.error(traceback.format_exc())
    return imgUrl

# 百度搜图
def baidu_search_img(query):
    imageNum = 10
    # 第一次搜图
    img_search_json = {"query": query, "width": 800, "height": 600}
    images = crawler.baidu_get_image_url_regx(img_search_json,imageNum)
    count = len(images)
    print(f"1.搜图《{query}》数量：{count}")

    # 第二次搜图
    if count<imageNum:
       img_search_json = {"query": query, "width": 800, "height": 0}
       sec = crawler.baidu_get_image_url_regx(img_search_json,imageNum)
       sec_count = len(sec)
       count = count + sec_count
       images += sec
       print(f"2.搜图《{query}》数量：{sec_count}")

    if count>0:
        random_number = random.randrange(0, count)
        return images[random_number]
    return

# 搜文任务
def check_text_search():
    global is_SearchText
    if not SearchTextList.empty() and is_SearchText == 2:
        is_SearchText = 1
        text_search_json = SearchTextList.get()
        prompt = text_search_json["prompt"]
        uid = text_search_json["uid"]
        username = text_search_json["username"]

        #搜索引擎搜索
        searchStr = baidu_web_search(prompt)
        #llm模型处理
        llm_prompt = f'帮我在答案"{searchStr}"中提取"{prompt}"的信息'
        print(f"重置提问:{llm_prompt}")
        #询问LLM
        llm_json = {"query": prompt, "prompt": llm_prompt, "uid": uid, "username": username}
        QuestionList.put(llm_json)

        is_SearchText = 2  # 搜文完成

# 跳舞任务
def check_dance():
    global is_dance
    if not DanceQueueList.empty() and is_dance == 2:
        is_dance = 1
        # 停止所有定时任务
        sched1.pause()
        # 停止所有在执行的任务
        cmd("\\dance")
        tts_say("开始跳舞了，大家嗨起来")
        dance_json = DanceQueueList.get()
        # 开始搜图任务
        dance(dance_json)
        # 重启定时任务
        sched1.resume()
        is_dance = 2  # 跳舞完成

# 跳舞操作
def dance(dance_json):
    global dance_now_path
    video_path = dance_json["video_path"]
    print(dance_json)
    obs.control_video("背景音乐",VideoControl.PAUSE.value)
    # ============== 跳舞视频 ==============
    # 第一次播放
    if video_path!=dance_now_path:
       obs.play_video("video",video_path)
    else:
       obs.control_video("video",VideoControl.RESTART.value)
    # 赋值当前跳舞视频
    dance_now_path = video_path
    time.sleep(1)
    while obs.get_video_status("video")!=VideoStatus.END.value and is_dance==1:
          time.sleep(1)
    obs.control_video("video",VideoControl.STOP.value)
    # ============== end ==============
    obs.control_video("背景音乐",VideoControl.PLAY.value)

# 搜图任务
def check_img_search():
    global is_SearchImg
    if not SearchImgList.empty() and is_SearchImg == 2:
        is_SearchImg = 1
        img_search_json = SearchImgList.get()
        # 开始搜图任务
        output_img_thead(img_search_json)
        is_SearchImg = 2  # 搜图完成

# 输出图片到虚拟摄像头
def searchimg_output(img_search_json):
    try:
        prompt = img_search_json["prompt"]
        username = img_search_json["username"]
        # 百度搜图
        imgUrl = baidu_search_img(prompt)
        img_search_json2 = {"prompt": prompt, "username": username, "imgUrl": imgUrl}
        print(f"搜图内容:{img_search_json2}")
        if imgUrl is not None:
            image = output_search_img(imgUrl,prompt,username)
            # 虚拟摄像头输出
            if image is not None:
                # 保存图片
                timestamp = time.time()
                path = f"{physical_save_folder}{prompt}_{username}_{timestamp}.jpg"
                # 转换图像模式为RGB
                image_rgb = image.convert('RGB')
                image_rgb.save(path, 'JPEG')
                obs.show_image("绘画图片",path)
                return 1
        return 0
    except Exception as e:
        print(f"【searchimg_output】发生了异常：{e}")
        logging.error(traceback.format_exc())
        return 0


# 搜索引擎-搜图任务
def output_img_thead(img_search_json):
    prompt = img_search_json["prompt"]
    username = img_search_json["username"]
    try:
        img_search_json = {"prompt": prompt, "username": username}
        obs.show_text("状态提示",f"{Ai_Name}在搜图《{prompt}》")
        # 搜索并且输出图片到虚拟摄像头
        status = searchimg_output(img_search_json)
        obs.show_text("状态提示","")
        if status==1:
            # 加入回复列表，并且后续合成语音
            tts_say(f"回复{username}：我给你搜了一张图《{prompt}》")
        else:
            tts_say(f"回复{username}：搜索图片《{prompt}》失败")
    except Exception as e:
        print(f"【output_img_thead】发生了异常：{e}")
        logging.error(traceback.format_exc())
    finally:
        print(f"‘{username}’搜图《{prompt}》结束")


# 图片转换字节流
def output_search_img(imgUrl,prompt,username):
    response = requests.get(imgUrl,timeout=(5, 60))
    img_data = response.content

    imgb64 = base64.b64encode(img_data)
    #===============最终图片鉴黄====================
    status,nsfw = nsfw_fun(imgb64,prompt,username,5,"搜图",0.6)
    # 鉴黄失败
    if status==-1:
        outputTxt=f"回复{username}：搜图鉴黄失败《{prompt}》-nsfw:{nsfw}，禁止执行"
        print(outputTxt)
        tts_say(outputTxt)
        return
    # 黄图情况
    if status==0:
        outputTxt=f"回复{username}：搜图发现一张黄图《{prompt}》-nsfw:{nsfw}，禁止执行"
        print(outputTxt)
        tts_say(outputTxt)
        return
    outputTxt=f"回复{username}：搜图为绿色图片《{prompt}》-nsfw:{nsfw}，输出显示"
    print(outputTxt)
    #========================================================

    # 读取二进制字节流
    img = Image.open(BytesIO(img_data))
    img = img.resize((width, height), Image.LANCZOS)
    # 字节流转换为cv2图片对象
    # image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
    # image = image[:, :, [2, 1, 0]]
    return img

# 鉴黄：1.通过 0.禁止 -1.异常
    #===============图片鉴黄====================
def nsfw_fun(imgb64,prompt,username,retryCount,tip,nsfw_limit):
    try:
        nsfw_lock.acquire()
        nsfwJson = nsfw_deal(imgb64)
    except Exception as e:
        print(f"《{prompt}》【nsfw】鉴黄{tip}发生了异常：{e}")
        logging.error(traceback.format_exc())
        return -1,-1
    finally:
        nsfw_lock.release()

    #===============鉴黄判断====================
    print(f"《{prompt}》【nsfw】{tip}鉴黄结果:{nsfwJson}")
    status = nsfwJson["status"]
    if status=="失败":
        print(f"《{prompt}》【nsfw】【重试剩余{retryCount}次】{tip}鉴黄失败，图片不明确跳出")
        retryCount=retryCount-1
        if retryCount>0:
            nsfw_fun(imgb64,prompt,username,retryCount,tip,nsfw_limit)
        return -1,-1
    nsfw = nsfwJson["nsfw"]
    #发现黄图
    try:
        if status=="成功" and nsfw>nsfw_limit:
            print(f"《{prompt}》【nsfw】{tip}完成，发现黄图:{nsfw},马上退出")
            # 摄像头显示禁止黄图标识
            obs.show_image("绘画图片","J:\\ai\\ai-yinmei\\images\\黄图950.jpg")
            # 保存用户的黄图，留底观察
            img = Image.open(io.BytesIO(base64.b64decode(imgb64)))
            timestamp = time.time()
            img.save(f"./porn/{prompt}_{username}_porn_{nsfw}_{timestamp}.jpg")
            return 0,nsfw
        elif status=="成功":
            return 1,nsfw
        return -1,nsfw
    except Exception as e:
        print(f"《{prompt}》【nsfw】鉴黄{tip}发生了异常：{e}")
        logging.error(traceback.format_exc())
        return -1,nsfw
    #========================================================

# 检查LLM回复线程
def check_answer():
    """
    如果AI没有在生成回复且队列中还有问题 则创建一个生成的线程
    :return:
    """
    global is_ai_ready
    global QuestionList
    if not QuestionList.empty() and is_ai_ready:
        is_ai_ready = False
        answers_thread = Thread(target=aiResponseTry)
        answers_thread.start()


# 如果语音已经放完且队列中还有回复 则创建一个生成并播放TTS的线程
def check_tts():
    global is_tts_ready
    if not AnswerList.empty() and is_tts_ready:
        is_tts_ready = False
        tts_generate()
        is_tts_ready = True  # 指示TTS已经准备好回复下一个问题


'''
bert-vits2语音合成
filename：音频文件名
text：说话文本
emotion：情感描述
'''
def bert_vits2(filename,text,emotion):
    save_path=f".\output\{filename}.mp3"
    text=parse.quote(text)
    response = requests.get(url=f"http://{bert_vists_url}/voice?text={text}&model_id=0&speaker_name={speaker_name}&sdp_ratio={sdp_ratio}&noise={noise}&noisew={noisew}&length={speed}&language=AUTO&auto_translate=false&auto_split=true&emotion={emotion}",timeout=(3, 60))
    if response.status_code == 200:
       audio_data = response.content # 获取音频数据
       with open(save_path, 'wb') as file:
            filenum=file.write(audio_data)
            if filenum>0:
                return 1
    return 0

def gtp_vists(filename,text,emotion):
    save_path=f".\output\{filename}.mp3"
    text=parse.quote(text)
    response = requests.get(url=f"http://{gtp_vists_url}/?text={text}&text_language=auto",timeout=(3, 60))
    if response.status_code == 200:
       audio_data = response.content # 获取音频数据
       with open(save_path, 'wb') as file:
            filenum=file.write(audio_data)
            if filenum>0:
                return 1
    return 0

# 直接合成语音播放       
def tts_say(text):
    try:
        say_lock.acquire()
        json =  {"question":"","text":text,"lanuage":""}
        tts_say_do(json)
    except Exception as e:
        print(f"【tts_say】发生了异常：{e}")
        logging.error(traceback.format_exc())
    finally:
        say_lock.release()

# 直接合成语音播放-聊天用      
def tts_chat_say(json):
    try:
        say_lock.acquire()
        tts_say_do(json)
    except Exception as e:
        print(f"【tts_chat_say】发生了异常：{e}")
        logging.error(traceback.format_exc())
    finally:
        say_lock.release()

# 直接合成语音播放 {"question":question,"text":text,"lanuage":"ja"}
def tts_say_do(json):
    global SayCount
    filename=f"say{SayCount}"
    
    question = json["question"]
    text = json["text"]
    replyText = text
    lanuage = json["lanuage"]

    # 识别表情
    jsonstr = emote_content(text)
    print(f"输出表情{jsonstr}")
    emotion = "happy"
    if len(jsonstr)>0:
        emotion = jsonstr[0]["content"]

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
    
    # 感情值增加
    moodNum = mood(emotion)

    # 触发翻译日语
    if lanuage=="AutoChange":
        print(f"当前感情值:{moodNum}")
        if moodNum>90 or "日语" in question or emotion=="angry":
           trans_json = translate(text,"zh-Hans","ja")
           if has_field(trans_json,"translated"):
                text = trans_json["translated"]

    # gtp-vists合成语音
    status = gtp_vists(filename,text,emotion)
    if status == 0:
       return
    
    # 输出表情
    emote_thread = Thread(target=emote_show,args=(jsonstr,))
    emote_thread.start()
    
    # 输出回复字幕
    ReplyTextList.put(replyText)
    
    # 循环摇摆动作
    yaotou_thread = Thread(target=auto_swing)
    yaotou_thread.start()
    
    # 播放声音
    mpv_play("mpv.exe", f".\output\{filename}.mp3", 100)

    # 执行命令行指令
    subprocess.run(f"del /f .\output\say{SayCount}.mp3 1>nul", shell=True)
    SayCount += 1

mood_num=0
# 感情值判断
def mood(emotion):
    global mood_num
    if emotion=="sad":
        mood_num=mood_num+1
    if emotion=="happy":
        mood_num=mood_num+2
    if emotion=="angry":
        mood_num=mood_num+3
    if mood_num>100:
        mood_num=0
    return mood_num


# 从回复队列中提取一条，通过edge-tts生成语音对应AudioCount编号语音
def tts_generate():
    global AnswerList
    response = AnswerList.get()
    
    # 合成语音
    tts_chat_say(response)

# 摇摆
swing_motion = 2  #1.摇摆中 2.停止摇摆
auto_swing_lock = threading.Lock()
def auto_swing():
    auto_swing_lock.acquire()
    global swing_motion
    # 触发器-设置开始摇摆: 停止摇摆+（唱歌中 或者 聊天中）= 可以设置摇摆动作
    if swing_motion == 2 and (is_singing==1 or is_tts_ready==False):
       print(f"进入摇摆状态:{swing_motion},{is_singing},{is_tts_ready}")
       swing_motion = 1
    else:
       auto_swing_lock.release()
       return
    # 监听停止摇摆线程
    stop_emote_thread = Thread(target=stop_motion)
    stop_emote_thread.start()
    auto_swing_lock.release()

    # 执行器-循环摇摆：
    while swing_motion == 1 and (is_singing==1 or is_tts_ready==False):
        jsonstr = []
        jsonstr.append({"content":"happy","key":"摇摆1","num":1,"timesleep":0,"donum":0,"endwait":24})
        jsonstr.append({"content":"happy","key":"摇摆2","num":1,"timesleep":0,"donum":0,"endwait":21})
        jsonstr.append({"content":"happy","key":"摇摆3","num":1,"timesleep":0,"donum":0,"endwait":25})
        jsonstr.append({"content":"happy","key":"摇摆4","num":1,"timesleep":0,"donum":0,"endwait":19})
        num = random.randrange(0, len(jsonstr))
        emote_show_json = []
        emote_show_json.append(jsonstr[num])
        print(f"执行摇摆：{emote_show_json}")
        emote_show_thread = Thread(target=emote_show,args=(emote_show_json,))
        emote_show_thread.start()
        # 当前表情等待结束时间
        endwait = emote_show_json[0]["endwait"]
        while endwait>0:
           time.sleep(1)
           endwait=endwait-1
           # 唱歌完毕并且聊天完毕：停止摇摆动作
           if is_singing==2 and is_tts_ready==True:
              swing_motion=2
              print(f"强制停止摇摆：{swing_motion}")
              break
    swing_motion = 2
    print(f"结束摇摆：{emote_show_json}")    
    


# 停止动作
def stop_motion():
    while swing_motion==1:
        time.sleep(1)
    print(f"静止：{swing_motion}")
    emote_ws(1, 0, "静止")

# 文本识别表情内容
# "content":语音情感,"key":按键名称,"num":执行,第几个字符开始执行表情,
# "donum":循环表情次数 timesleep:和donum联动，等待n秒开始循环执行当前表情,"endwait":表情等待结束时间，一般和执行表情的时间一致
def emote_content(response):
    jsonstr = []
    # =========== 随机动作 ==============
    # text = ["笑", "不错", "哈", "开心", "呵", "嘻", "画", "欢迎", "搜", "唱"]
    # num = is_array_contain_string(text, response)
    # if num > 0:
    #     press_arry = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    #     press = random.randrange(0, len(press_arry))
    #     jsonstr.append({"content":"happy","key":press_arry[press],"num":num})
    # ===============================

    # =========== 开心 ==============
    text = ["笑", "不错", "哈", "开心", "呵", "嘻", "画", "搜", "有趣"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"happy","key":"开心","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 哭 ==============
    text = ["哭", "悲伤", "伤心", "凄惨", "好惨", "呜呜", "悲哀"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"sad","key":"哭","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 招呼 ==============
    text = ["你好", "在吗", "干嘛", "名字", "欢迎", "我在", "玩笑", "逗"]
    num = is_array_contain_string(text, response)
    if num > 0:
        press1 = random.randrange(1, 3)
        if press1==1:
           jsonstr.append({"content":"call","key":"捂嘴","num":num,"timesleep":0,"donum":0,"endwait":0})
        else:
           jsonstr.append({"content":"call","key":"拿扇子","num":num,"timesleep":0,"donum":0,"endwait":0})
        press2 = random.randrange(1, 4)
        if press2==1:
           jsonstr.append({"content":"call","key":"星星眼","num":num,"timesleep":0,"donum":0,"endwait":0})
        elif press2==2:
           jsonstr.append({"content":"call","key":"害羞","num":num,"timesleep":0,"donum":0,"endwait":0})
        elif press2==3:
           jsonstr.append({"content":"call","key":"米米","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 有钱 ==============
    text = ["钱", "money", "有米"]
    num = is_array_contain_string(text, response)
    if num > 0:
       jsonstr.append({"content":"call","key":"米米","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 温柔 ==============
    text = ["温柔", "抚摸", "抚媚", "骚", "唱歌"]
    num = is_array_contain_string(text, response)
    if num > 0:
        press1 = random.randrange(1, 3)
        if press1==1:
           jsonstr.append({"content":"call","key":"左眼闭合","num":num,"timesleep":0,"donum":0,"endwait":0})
        else:
           jsonstr.append({"content":"call","key":"右眼闭合","num":num,"timesleep":0,"donum":0,"endwait":0})
        press2 = random.randrange(1, 3)
        if press2==1:
           jsonstr.append({"content":"call","key":"头左倾","num":num,"timesleep":0,"donum":0,"endwait":0})
        else:
           jsonstr.append({"content":"call","key":"头右倾","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 生气 ==============
    text = ["生气", "不理你", "骂", "臭", "打死", "可恶", "白痴", "可恶"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"angry","key":"生气","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 尴尬 ==============
    text = ["尴尬", "无聊", "无奈", "傻子", "郁闷", "龟蛋", "傻逼", "逗比", "逗逼", "忘记", "怎么可能", "调侃"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"blush","key":"尴尬","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 认同 ==============
    text = ["认同", "点头", "嗯", "哦", "女仆"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"approve","key":"认同","num":num,"timesleep":0.002,"donum":5,"endwait":0})
    # =========== 汗颜 ==============
    text = ["汗颜", "流汗", "郁闷", "笑死", "白痴", "渣渣", "搞笑", "恶心"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"sweat","key":"汗颜","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 晕 ==============
    text = ["晕", "头晕", "晕死", "呕"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"blush","key":"晕","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 吐血 ==============
    text = ["吐血", "血"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"blood","key":"血","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 可爱 ==============
    text = ["可爱", "害羞", "爱你", "天真", "搞笑", "喜欢", "全知全能"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"love","key":"可爱","num":num,"timesleep":0,"donum":0,"endwait":0})
    # =========== 摸摸头 ==============
    text = ["摸摸头", "乖", "做得好"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"happy","key":"摸摸头","num":num,"timesleep":5,"donum":1,"endwait":0})
        jsonstr.append({"content":"blush","key":"晕","num":num,"timesleep":0,"donum":0,"endwait":0})
    return jsonstr

# 表情加入:使用键盘控制VTube
# key：表情按键  num:第几个字符开始执行表情 donum：循环表情次数 timesleep:和donum联动，等待n秒开始循环执行当前表情
def emote_show(emote_content):
    for data in emote_content:
        key = data["key"]
        num = data["num"]
        timesleep = data["timesleep"]
        donum = data["donum"]
        emote_ws(num, 0.4, key)
        # 有需要结束的表情按钮
        while donum>0:
            time.sleep(timesleep)
            emote_ws(1, 0, key)
            donum = donum - 1

# 键盘触发-带按键时长
def emote_do(text, response, keyboard, startTime, key):
    num = is_array_contain_string(text, response)
    if num > 0:
        start = round(num * startTime, 2)
        time.sleep(start)
        keyboard.press(key)
        time.sleep(1)
        keyboard.release(key)
        print(f"{response}:输出表情({start}){key}")

# ws协议：发送表情到Vtuber
# num：表情第几个执行   interval：间隔秒数  key：按键
def emote_ws(num, interval, key):
    global ws
    if num > 0:
        start = round(num * interval, 2)
        time.sleep(start)
        jstr={
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID11",
            "messageType": "HotkeyTriggerRequest",
            "data": {
                "hotkeyID": key
            }
        }
        data=json.dumps(jstr)
        # vtuber执行表情展示
        try:
            ws.send(data)
        except Exception as e:
            error = f"【表情发送】发生了异常：{e}"
            print(error)
            if error in "Connection is already closed":
                ws = websocket.WebSocketApp("ws://127.0.0.1:8001",on_open = on_open)
                # ws服务心跳包
                run_forever_thread = Thread(target=run_forever)
                run_forever_thread.start()

# 判断字符是否存在歌曲此队列
def exist_song_queues(queues,name):
    # 当前歌曲
    if "songname" in SongNowName and SongNowName["songname"] == name:
        return True
    # 歌单里歌曲
    for i in range(queues.qsize()):
        data = queues.queue[i]
        if data["songname"]==name:
            return True
    return False

# 正则判断
def has_string_reg(regx,s):
    return re.search(regx, s)

# 正则判断[集合判断]
def has_string_reg_list(regxlist,s):
    regx = regxlist.replace("[","(").replace("]",")").replace(",","|").replace("'","").replace(" ","")
    return re.search(regx, s)

# 判断字符位置（不含搜索字符）- 如，搜索“画画女孩”，则输出“女孩”位置
def is_index_contain_string(string_array, target_string):
    i = 0
    for s in string_array:
        i = i + 1
        if s in target_string:
            num = target_string.find(s)
            return num + len(s)
    return 0

# 判断字符位置（含搜索字符）- 如，搜索“画画女孩”，则输出“画画女孩”位置
def is_array_contain_string(string_array, target_string):
    i = 0
    for s in string_array:
        i = i + 1
        if s in target_string:
            return i
    return 0

# 播放器播放
def mpv_play(mpv_name, song_path, volume):
    # end：播放多少秒结束  volume：音量，最大100，最小0
    subprocess.run(
        f'{mpv_name} -vo null --volume={volume} "{song_path}" 1>nul',
        shell=True,
    )


# 唱歌线程
def check_sing():
    if not SongQueueList.empty():
        song_json = SongQueueList.get()
        print(f"启动唱歌:{song_json}")
        # 启动唱歌
        sing_thread = Thread(
            target=singTry, args=(song_json["prompt"], song_json["username"])
        )
        sing_thread.start()

# 唱歌
def singTry(songname, username):
    global is_creating_song
    global is_singing
    try:
        if songname!="":
           sing(songname, username)
    except Exception as e:
        print(f"【singTry】发生了异常：{e}")
        logging.error(traceback.format_exc())
        is_singing = 2
        is_creating_song=2

# 唱歌
def sing(songname, username):
    global is_creating_song
    global SongMenuList
    is_created = 0  # 1.已经生成过 0.没有生成过 2.生成失败
    
    query = songname # 查询内容
    
    # =============== 开始-获取真实歌曲名称 =================
    musicJson = requests.get(url=f"http://{singUrl}/musicInfo/{songname}",timeout=(3, 5))
    music_json = json.loads(musicJson.text)
    id = music_json["id"]
    songname = music_json["songName"]
    # 前置信息说明
    font_text=""
    if query!=songname:
       font_text = f"根据\"{query}\"的信息，"

    if id==0:
        outputTxt=f"{font_text}歌库不存在《{query}》这首歌曲哦"
        print(outputTxt)
        tts_say(outputTxt)
        return 
    song_path = f"./output/{songname}.wav"
    # =============== 结束-获取真实歌曲名称 =================
    
    # =============== 开始-重复点播判断 =================
    if exist_song_queues(SongMenuList,songname)==True:
       outputTxt=f"回复{username}：{font_text}歌单里已经有歌曲《{songname}》，请勿重新点播"
       tts_say(outputTxt)
    # =============== 结束-重复点播判断 =================

    # =============== 开始-判断本地是否有歌 =================
    if os.path.exists(song_path):
        print(f"找到存在本地歌曲:{song_path}")
        outputTxt=f"回复{username}：{font_text}{Ai_Name}会唱《{songname}》这首歌曲哦"
        tts_say(outputTxt)
        is_created = 1
    # =============== 结束-判断本地是否有歌 =================
    else:       
    # =============== 开始-调用已经转换的歌曲 =================
    # 下载歌曲：这里网易歌库返回songname和用户的模糊搜索可能歌名不同
        downfile, is_created = check_down_song(songname)
        if downfile is not None and is_created == 1:
            with open(song_path, "wb") as f:
                f.write(downfile.content)
                print(f"找到服务已经转换的歌曲《{songname}》")
    # =============== 结束-调用已经转换的歌曲 =================

    # =============== 开始：如果不存在歌曲，生成歌曲 =================
    if is_created == 0:
        # 播报学习歌曲
        print(f"歌曲不存在，需要生成歌曲《{songname}》")
        outputTxt=f"回复{username}：{font_text}{Ai_Name}需要学唱歌曲《{songname}》，请耐心等待"
        tts_say(outputTxt)
        # 其他歌曲在生成的时候等待
        while is_creating_song == 1:
            time.sleep(1)
        # 调用Ai学唱歌服务：生成歌曲
        is_created=create_song(songname,song_path,is_created,downfile)
    if is_created==2:
        print(f"生成歌曲失败《{songname}》")
        return
    obs.show_text("状态提示",f"{Ai_Name}已经学会歌曲《{songname}》")
    # =============== 结束：如果不存在歌曲，生成歌曲 =================

    #等待播放
    print(f"等待播放{username}点播的歌曲《{songname}》：{is_singing}")
    #加入播放歌单

    SongMenuList.put({"username": username, "songname": songname,"is_created":is_created,"song_path":song_path,"query":query})
  

# 播放歌曲清单
def check_playSongMenuList():
    global is_singing
    global SongNowName
    if not SongMenuList.empty() and is_singing == 2:
        #播放歌曲
        play_song_lock.acquire()
        mlist = SongMenuList.get() #取出歌单播放
        SongNowName = mlist  #赋值当前歌曲名称
        is_singing = 1  # 开始唱歌
        # =============== 开始：播放歌曲 =================
        obs.control_video("背景音乐",VideoControl.PAUSE.value)
        play_song(mlist["is_created"],mlist["songname"],mlist["song_path"],mlist["username"],mlist["query"])
        obs.control_video("背景音乐",VideoControl.PLAY.value)
        # =============== 结束：播放歌曲 =================
        is_singing = 2  # 完成唱歌
        SongNowName = {} #当前播放歌单清空
        play_song_lock.release()

song_not_convert=["三国演义\d+","粤剧","京剧","易经"]  #不需要学习的歌曲【支持正则】
#开始生成歌曲
def create_song(songname,song_path,is_created,downfile):
    global is_creating_song
    try:
        # =============== 开始生成歌曲 =================
        create_song_lock.acquire()
        is_creating_song = 1
        status_json={}
        is_download=False
        # =============== 开始-当前歌曲只下载不转换 =================
        for song_regx in song_not_convert:
            match = re.match(song_regx, songname)
            if match:
               print(f"当前歌曲只下载不转换《{songname}》")
               jsonStr = requests.get(url=f"http://{singUrl}/download_song/{songname}",timeout=(3, 120))
               status_json = json.loads(jsonStr.text)
               is_download=True
               break
        # =============== 结束-当前歌曲只下载不转换 =================
        
        # =============== 开始-学习唱歌任务 =================
        if is_download==False:
            # 生成歌曲接口
            jsonStr = requests.get(url=f"http://{singUrl}/append_song/{songname}",timeout=(3, 5))
            status_json = json.loads(jsonStr.text)
        # =============== 结束-学习唱歌任务 =================

        status = status_json["status"]  #status: "processing" "processed" "waiting"
        songname = status_json["songName"]
        print(f"准备生成歌曲内容：{status_json}")
        if status=="processing" or status=="processed" or status=="waiting":
            timout = 2400  # 生成歌曲等待时间
            i = 0
            while downfile is None and is_creating_song==1:
                # 检查歌曲是否生成成功：这里网易歌库返回songname和用户的模糊搜索可能歌名不同
                downfile, is_created = check_down_song(songname)
                if is_created == 2:
                    break
                # 本地保存歌曲
                if downfile is not None and is_created == 1:
                    with open(song_path, "wb") as f:
                        f.write(downfile.content)
                i = i + 1
                if i >= timout:
                    break
                obs.show_text("状态提示",f"当前{Ai_Name}学唱歌曲《{songname}》第{i}秒")
                print(f"生成《{songname}》歌曲第[{i}]秒,生成状态:{is_created}")
                time.sleep(1)
        # =============== 结束生成歌曲 =================
    except Exception as e:
        print(f"《{songname}》create_song异常{e}")
        return 2
    finally:
        is_creating_song = 2
        create_song_lock.release()
    return is_created

# 播放歌曲 1.成功 2.没有歌曲播放 3.异常 
def play_song(is_created,songname,song_path,username,query):
    try:
        # 播放歌曲
        if is_created == 1:
            print(f"准备唱歌《{songname}》,播放路径:{song_path}")
            # =============== 开始-触发搜图 =================
            img_search_json = {"prompt": query, "username": username}
            searchimg_output_thread = Thread(target=searchimg_output,args=(img_search_json,))
            searchimg_output_thread.start()
            # =============== 结束-触发搜图 =================
            # 开始唱歌服装穿戴
            emote_ws(1, 0.2, "唱歌")
            # 播报唱歌文字
            tts_say(f"回复{username}：我准备唱一首歌《{songname}》")
            # 循环摇摆动作
            auto_swing_thread = Thread(target=auto_swing)
            auto_swing_thread.start()
            # 唱歌视频播放
            sing_dance_thread = Thread(target=sing_dance, args=(query,))
            sing_dance_thread.start()
            # 调用音乐播放器
            mpv_play("song.exe", song_path, 80)
            # 停止唱歌视频播放
            obs.control_video("唱歌视频",VideoControl.STOP.value)
            # 结束唱歌穿戴
            emote_ws(1, 0.2, "唱歌")
            return 1
        else:
            tip=f"已经跳过歌曲《{songname}》，请稍后再点播"
            print(tip)
            # 加入回复列表，并且后续合成语音
            tts_say(f"回复{username}：{tip}")
            return 2
    except Exception as e:
        print(f"《{songname}》play_song异常{e}")
        return 3

# 唱歌跳舞
def sing_dance(songname):
    global singdance_now_path
    #提示语为空，随机视频
    video_path=""
    if songname!="":
        matches_list = StringUtil.fuzzy_match_list(songname,dance_video)
        if len(matches_list)>0:
           rnd_video = random.randrange(0, len(matches_list))
           video_path = matches_list[rnd_video]
    if video_path=="":
       return 
    # 第一次播放
    if video_path!=singdance_now_path:
       obs.play_video("唱歌视频",video_path)
    else:
       obs.control_video("唱歌视频",VideoControl.RESTART.value)
    # 赋值当前表情视频
    singdance_now_path = video_path
    time.sleep(1)
    while is_singing==1:
          # 结束循环重新播放
          if obs.get_video_status("唱歌视频")==VideoStatus.END.value:
             obs.control_video("唱歌视频",VideoControl.RESTART.value)
          time.sleep(1)
    

# 匹配已生成的歌曲，并返回字节流
def check_down_song(songname):
    # 查看歌曲是否曾经生成
    status = requests.get(url=f"http://{singUrl}/status",timeout=(3, 5))
    converted_json = json.loads(status.text)
    converted_file = converted_json["converted_file"]  # 生成歌曲硬盘文件
    convertfail = converted_json["convertfail"]  # 生成歌曲硬盘文件
    is_created = 0  # 1.已经生成过 0.没有生成过 2.生成失败
    for filename in convertfail:
        if songname == filename:
            is_created = 2
            return None, is_created

    # 优先：精确匹配文件名
    for filename in converted_file:
        if songname == filename:
            is_created = 1
            downfile = requests.get(url=f"http://{singUrl}/get_audio/{songname}",timeout=(3, 120))
            return downfile, is_created
    
    return None, is_created

#翻译
def translate(text,from_lanuage,to_lanuage):
    with DDGS(proxies=duckduckgo_proxies, timeout=20) as ddgs:
        try:
            r = ddgs.translate(text,from_=from_lanuage, to=to_lanuage)
            print(f"翻译：{r}")
            return r
        except Exception as e: 
            print(f"translate信息回复异常{e}")
            logging.error(traceback.format_exc())
        return text

# 抽取固定扩展提示词：limit:限制条数  num:抽取次数
def draw_prompt_do(query,limit,num):
    offset=0
    jsonEnd=[]
    for i in range(num):
        json = draw_prompt(query,0,100)
        jsonEnd=jsonEnd.append(json)
        if len(jsonEnd)>=limit:
           jsonEnd=json[:limit]
           return jsonEnd
        print(f"{query}抽取:"+len(jsonEnd))
        i=i+1
        offset=offset+limit
    return jsonEnd
        

# 扩展提示词
def draw_prompt(query,offset,limit):
    url="http://meilisearch-v1-6.civitai.com/multi-search"
    headers = {"Authorization": "Bearer 102312c2b83ea0ef9ac32e7858f742721bbfd7319a957272e746f84fd1e974af"}
    #排序："stats.commentCountAllTime:desc","stats.collectedCountAllTime:desc"
    payload = {
        "queries": [
            {
                "attributesToHighlight": [],
                "facets": [
                    "aspectRatio",
                    "baseModel",
                    "createdAtUnix",
                    "generationTool",
                    "tags.name",
                    "user.username"
                ],
                "filter": [
				    "nsfwLevel=1"
			    ],
                "highlightPostTag": "__/ais-highlight__",
                "highlightPreTag": "__ais-highlight__",
                "indexUid": "images_v4",
                "limit": limit,
                "offset": offset,
                "q": query
            }
        ]
    }
    try:
        offset=0
        response = requests.post(
            url, headers=headers, json=payload, verify=False, timeout=60, proxies=proxies
        )
        r = response.json()
        hits_temp = r["results"][0]["hits"]
        hits = []
        # ========== 过滤18禁提示词: ==========
        # 参数"txt2imgHiRes"是18禁图片，"txt2img"是绿色图片；nsfw为禁黄标识：None是安全
        for json in hits_temp:
            if json["generationProcess"]=="txt2img":
               hits.append(json)
        if len(hits)<=0:
           return ""
        # ===================================

        #条数处理
        count = len(hits)
        print(f"{query}>>条数：{count}")
        if count>limit:
            hits=hits[:limit]

        steps = 25
        sampler="DPM++ SDE Karras"
        seed=-1
        cfgScale=7
        prompt=query
        negativePrompt=""
        if count>0:
            num = random.randrange(0, count)
            prompt = filter(hits[num]["meta"]["prompt"],filterEn)
            if has_field(hits[num]["meta"],"negativePrompt"):
                negativePrompt = hits[num]["meta"]["negativePrompt"]
            if has_field(hits[num]["meta"],"cfgScale"):
                cfgScale = hits[num]["meta"]["cfgScale"]
            if has_field(hits[num]["meta"],"steps"):
               steps = hits[num]["meta"]["steps"]
            if has_field(hits[num]["meta"],"sampler"):
               sampler = hits[num]["meta"]["sampler"]
            if has_field(hits[num]["meta"],"seed"):
               seed = hits[num]["meta"]["seed"]
            jsonStr = {"prompt":isNone(prompt),"negativePrompt":isNone(negativePrompt),"cfgScale":cfgScale,"steps":steps,"sampler":isNone(sampler),"seed":seed}
            logstr = hits[num]
            print(f"C站提示词:{logstr}")
            return jsonStr
    except Exception as e:
        print(f"draw_prompt信息回复异常{e}")
        logging.error(traceback.format_exc())
        return ""
    return ""

# 过滤函数
def filter(text,filterPromptStr):
    fstr=filterPromptStr.replace("\\n","")
    fstr=fstr.lower()
    str = fstr.split(',')
    for s in str:
        text=text.lower().replace(s.lower(),"")
    return text
    
# 判断是否none
def isNone(text):
    if text is None:
       return ""
    return text

# 判断包含字符
def has_field(json_data, field):
    return field in json_data

# 绘画任务队列
def check_draw():
    global is_drawing
    global DrawQueueList
    if not DrawQueueList.empty() and is_drawing == 3:
        draw_json = DrawQueueList.get()
        print(f"启动绘画:{draw_json}")
        # 开始绘画
        draw_thread = Thread(target=draw, args=(draw_json["prompt"], draw_json["drawcontent"], draw_json["username"], draw_json["isExtend"]))
        draw_thread.start()

# 绘画
def draw(prompt, drawcontent, username, isExtend):
    global is_drawing
    is_drawing = 1

    drawName=prompt
    steps = 35
    sampler="DPM++ SDE Karras"
    seed=-1
    cfgScale=7
    negativePrompt=""
    jsonPrompt=""
    flag = 1 # 1.默认 2.特殊模型
    try:
        # 绘画标题
        if prompt!="":
            trans_json = translate(prompt,"zh-Hans","en")  #翻译
            if has_field(trans_json,"translated"):
                prompt = trans_json["translated"]
        # 绘画详细描述
        if drawcontent!="":
            trans_json2 = translate(drawcontent,"zh-Hans","en")  #翻译
            if has_field(trans_json2,"translated"):
                drawcontent = trans_json2["translated"]

        if isExtend==True:
            #C站抽取提示词：扩展提示词-扩大Ai想象力
            jsonPrompt = draw_prompt(prompt,0,50)
            if jsonPrompt=="":
               print(f"《{drawName}》没找到绘画扩展提示词")
               jsonPrompt = {"prompt":"","negativePrompt":"","cfgScale":cfgScale,"steps":steps,"sampler":sampler,"seed":seed}
            print(f"绘画扩展提示词:{jsonPrompt}")

        # 女孩
        # text = ["漫画", "女"]
        # num = is_index_contain_string(text, drawName)
        # if num>0:
        #     checkpoint = "aingdiffusion_v13"
        #     prompt = f"(({prompt})),"+jsonPrompt["prompt"]+f",{prompt},<lora:{prompt}>"
        #     if jsonPrompt!="":
        #         prompt=jsonPrompt["prompt"]+prompt
        #     negativePrompt = f"EasyNegative, (worst quality, low quality:1.4), [:(badhandv4:1.5):27],(nsfw:1.3)"
        #     flag = 2
            
        # 迪迦奥特曼
        # text = ["迪迦", "奥特曼"]
        # num = is_index_contain_string(text, drawName)
        # if num>0:
        #     checkpoint = "chilloutmix_NiPrunedFp32Fix"
        #     prompt = f"(({prompt})),masterpiece, best quality, 1boy, alien, male focus, solo, 1boy, tokusatsu,full body, (giant), railing, glowing eyes, glowing, from below , white eyes,night,  <lora:dijia:1> ,city,building,(Damaged buildings:1.3),tiltshift,(ruins:1.4),<lora:{prompt}>"
        #     if jsonPrompt!="":
        #         prompt=jsonPrompt["prompt"]+prompt
        #     flag = 2

        # 绘画扩展提示词 {"prompt":prompt,"negativePrompt":negativePrompt,"cfgScale":cfgScale,"steps":steps,"sampler":sampler,"seed":seed}
        if flag == 1:
            # 默认模型
            checkpoint = "realvisxlV30Turbo_v30TurboBakedvae"
            if jsonPrompt!="":
                prompt = f"(({prompt},{drawcontent})),"+jsonPrompt["prompt"]+","+f"<lora:{prompt}>"
                negativePrompt = isNone(jsonPrompt["negativePrompt"])
                cfgScale = jsonPrompt["cfgScale"]
                steps = jsonPrompt["steps"]
                sampler = jsonPrompt["sampler"]
                # seed = jsonPrompt["seed"]
            else:
                prompt = f"{prompt},{drawcontent}"+f"<lora:{prompt}>"
                negativePrompt = filterEn

        payload = {
            "prompt": prompt,
            "negative_prompt": negativePrompt,
            "hr_checkpoint_name": checkpoint,
            "refiner_checkpoint": checkpoint,
            "sampler_index": sampler,
            "steps": steps,
            "cfg_scale": cfgScale,
            "seed": seed,
            "width": width,
            "height": height,
        }
        print(f"画画参数：{payload}")
    
        # stable-diffusion绘图
        # 绘画进度
        progress_thread = Thread(target=progress,args=(drawName, username))
        progress_thread.start()
        # 生成绘画
        response = requests.post(url=f"http://{drawUrl}/sdapi/v1/txt2img", json=payload,timeout=(5, 60))
        is_drawing = 2
        r = response.json()
        #错误码跳出
        if(has_field(r, "error") and r["error"]!=""):
           print(f"绘画生成错误:{r}")
           return
        # 读取二进制字节流
        imgb64=r["images"][0]
        #===============最终图片鉴黄====================
        status,nsfw = nsfw_fun(imgb64,drawName,username,3,"绘画",nsfw_limit)
        # 鉴黄失败
        if status==-1:
            outputTxt=f"回复{username}：绘画鉴黄失败《{drawName}》，禁止执行"
            print(outputTxt)
            tts_say(outputTxt)
            return
        # 黄图情况
        if status==0:
            outputTxt=f"回复{username}：绘画发现一张黄图《{drawName}》，禁止执行"
            print(outputTxt)
            tts_say(outputTxt)
            return
        #========================================================

        # ============== PIL图片对象 ==============
        img = Image.open(io.BytesIO(base64.b64decode(imgb64)))
        img = img.resize((width, height), Image.LANCZOS)
        # 保存图片-留底观察
        timestamp = time.time()
        path = f"{physical_save_folder}{drawName}_{username}_{nsfw}_{timestamp}.jpg"
        img.save(path)
        # ================= end =================

        obs.show_image("绘画图片",path)
        # 播报绘画
        outputTxt=f"回复{username}：我给你画了一张画《{drawName}》"
        print(outputTxt)
        tts_say(outputTxt)
    except Exception as e:
        print(f"【draw】发生了异常：{e}")
        logging.error(traceback.format_exc())
    finally:
        is_drawing = 3


# 图片生成进度
def progress(prompt, username):
    global is_drawing
    while True:
        # 绘画中：输出进度图
        if is_drawing == 1:
            # stable-diffusion绘图进度
            response = requests.get(url=f"http://{drawUrl}/sdapi/v1/progress",timeout=(5, 60))
            r = response.json()
            imgb64 = r["current_image"]
            if imgb64 != "" and imgb64 is not None:
                p = round(r["progress"] * 100, 2)
                #===============鉴黄, 大于**%进度进行鉴黄====================
                try:
                    if p>progress_limit:
                        status,nsfw = nsfw_fun(imgb64,prompt,username,1,"绘画进度",nsfw_progress_limit)
                        #异常鉴黄
                        if status==-1:
                            print(f"《{prompt}》进度{p}%鉴黄失败，图片不明确跳出")
                            continue 
                        #发现黄图
                        if status==0:
                            print(f"《{prompt}》进度{p}%发现黄图-nsfw:{nsfw},进度跳过")
                            continue
                        print(f"《{prompt}》进度{p}%绿色图片-nsfw:{nsfw},输出进度图")
                        obs.show_text("状态提示",f"{Ai_Name}正在绘图《{prompt}》,进度{p}%")
                    else:
                        print(f"《{prompt}》输出进度：{p}%")
                except Exception as e:
                    print(f"【鉴黄】发生了异常：{e}")
                    logging.error(traceback.format_exc())
                    continue
                #========================================================
                # 读取二进制字节流
                img = Image.open(io.BytesIO(base64.b64decode(imgb64)))
                # 拉伸图片
                img = img.resize((width, height), Image.LANCZOS)
                # 保存图片
                timestamp = time.time()
                path = f"{physical_save_folder}{prompt}_{username}_{nsfw}_{timestamp}.jpg"
                img.save(path)
                obs.show_image("绘画图片",path)
            time.sleep(1)
        elif is_drawing >= 2:
            print(f"《{prompt}》输出进度：100%")
            obs.show_text("状态提示",f"{Ai_Name}绘图《{prompt}》完成")
            break    

# 鉴黄
def nsfw_deal(imgb64):
    headers = {"Content-Type": "application/json"}
    data={"image_loader":"yahoo","model_weights":"data/open_nsfw-weights.npy","input_type":"BASE64_JPEG","input_image":imgb64}
    nsfw = requests.post(url=f"http://192.168.2.198:1801/input", headers=headers, json=data, verify=False, timeout=(3, 5))
    nsfwJson = nsfw.json()
    return nsfwJson

# 进入直播间欢迎语
def check_welcome_room():
    count = len(WelcomeList)
    numstr = ""
    if count>1:
        numstr = f"{count}位"
    userlist = str(WelcomeList).replace("['","").replace("']","")
    if len(WelcomeList) > 0:
        text = f"欢迎一下\"{userlist}\"{numstr}同学来到直播间,跪求关注一下我的直播间"
        WelcomeList.clear()
        #询问LLM
        llm_json = {"prompt": text, "uid": 0, "username": Ai_Name}
        QuestionList.put(llm_json)  # 将弹幕消息放入队列

# 时间判断场景
def check_scene_time():
    now_time = time.strftime("%H:%M:%S", time.localtime())
    # 判断时间
    # 白天
    if "06:00:00" <= now_time <= "16:59:59":
        print("现在是白天") 
        obs.show_image("海岸花坊背景","J:\\ai\\vup背景\\海岸花坊\\白昼.jpg")
        obs.show_image("粉色房间背景","J:\\ai\\vup背景\\粉色房间\\白天.jpg")
        obs.show_image("粉色房间桌面","J:\\ai\\vup背景\\粉色房间\\白天桌子.png")
        obs.play_video("神社背景","J:\\ai\\vup背景\\神社白天\\日动态.mp4")
    
    # 黄昏
    if "17:00:00" <= now_time <= "17:59:59":
        print("现在是黄昏") 
        obs.show_image("粉色房间背景","J:\\ai\\vup背景\\粉色房间\\黄昏.jpg")
        obs.show_image("粉色房间桌面","J:\\ai\\vup背景\\粉色房间\\黄昏桌子.png")

    # 晚上
    if "18:00:00" <= now_time <= "24:00:00" or "00:00:00" < now_time < "06:00:00":
        print("现在是晚上") 
        obs.show_image("海岸花坊背景","J:\\ai\\vup背景\\海岸花坊\\夜晚.jpg")
        obs.show_image("粉色房间背景","J:\\ai\\vup背景\\粉色房间\\晚上开灯.jpg")
        obs.show_image("粉色房间桌面","J:\\ai\\vup背景\\粉色房间\\晚上开灯桌子.png")
        obs.play_video("神社背景","J:\\ai\\vup背景\\神社夜晚\\夜动态.mp4")

def main():
    # ws表情服务心跳包
    run_forever_thread = Thread(target=run_forever)
    run_forever_thread.start()

    # 连接obs
    obs.connect()

    #初始化衣服
    global now_clothes
    emote_ws(1, 0.2, "初始化")  #解除当前衣服
    emote_ws(1, 0.2, "便衣")  #穿上新衣服
    now_clothes = "便衣"
    
    # 跳舞表情
    # content = ""
    # for str in emote_list:
    #     content= content + str + ","
    # if content!="":
    #     obs.show_text("表情列表",content)
    
    # 停止所有视频播放
    obs.control_video("唱歌视频",VideoControl.STOP.value)
    obs.control_video("video",VideoControl.STOP.value)
    obs.control_video("表情",VideoControl.STOP.value)

    # 切换场景:初始化
    scene_name = "海岸花坊"
    obs.change_scene(scene_name)
    # 背景乐切换
    if scene_name in song_background:
       song = song_background[scene_name]
       obs.play_video("背景音乐",song)
       time.sleep(1)
       obs.control_video("背景音乐",VideoControl.RESTART.value)
    # 场景[白天黑夜]判断
    check_scene_time()

    # 吟美状态提示:初始化清空
    obs.show_text("状态提示","")

    if mode==1 or mode==2:
        # LLM回复
        sched1.add_job(func=check_answer, trigger="interval", seconds=1, id=f"answer", max_instances=10)
        # tts语音合成
        sched1.add_job(func=check_tts, trigger="interval", seconds=1, id=f"tts", max_instances=10)
        # 绘画
        sched1.add_job(func=check_draw, trigger="interval", seconds=1, id=f"draw", max_instances=10)
        # 搜索资料
        sched1.add_job(func=check_text_search, trigger="interval", seconds=1, id=f"text_search", max_instances=10)
        # 搜图
        sched1.add_job(func=check_img_search, trigger="interval", seconds=1, id=f"img_search", max_instances=10)
        # 唱歌转换
        sched1.add_job(func=check_sing, trigger="interval", seconds=1, id=f"sing", max_instances=50)
        # 歌曲清单播放
        sched1.add_job(func=check_playSongMenuList, trigger="interval", seconds=1, id=f"playSongMenuList", max_instances=50)
        # 跳舞
        sched1.add_job(func=check_dance, trigger="interval", seconds=1, id=f"dance", max_instances=10)
        # 时间判断场景[白天黑夜切换]
        sched1.add_job(func=check_scene_time, trigger="cron", hour="6,17,18", id=f"scene_time")
        # 欢迎语
        sched1.add_job(func=check_welcome_room, trigger="interval", seconds=8, id=f"welcome_room", max_instances=10)
        sched1.start()
    
    if mode==1 or mode==2:
        # 开启web
        app_thread = Thread(target=apprun)
        app_thread.start()
        
    if mode==1:
        # 开始监听弹幕流
        sync(room.connect())
    else:
        while True:
           time.sleep(10)

# b站直播间监听
def brun():
    sync(room.connect())

# http服务  
def apprun():
    # 禁止输出日志
    app.logger.disabled = True
    # 启动web应用
    app.run(host="0.0.0.0", port=1800)  

# 授权Vtuber服务
def auth():
    #授权码
    authstr={
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "SomeID",
        "messageType": "AuthenticationRequest",
        "data": {
            "pluginName": vtuber_pluginName,
            "pluginDeveloper": vtuber_pluginDeveloper,
            "authenticationToken": vtuber_authenticationToken
        }
    }
    data=json.dumps(authstr)
    ws.send(data)

if __name__ == "__main__":
    main()
