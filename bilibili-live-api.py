# b站AI直播对接text-generation-webui聚合文本LLM模型
import json
import datetime
import queue
import subprocess
import threading
import os
import time
import requests
import pyvirtualcam
import cv2
import base64
import numpy as np
import io
import random
import re
import traceback
import websocket
import crawler
import logging

from io import BytesIO
from PIL import Image
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bilibili_api import live, sync, Credential
from pynput.keyboard import Key, Controller
from duckduckgo_search import DDGS
from threading import Thread
from peft import PeftModel
from transformers import AutoTokenizer, AutoModel, AutoConfig
from urllib.parse import quote
from flask import Flask, jsonify, request, render_template
from flask_apscheduler import APScheduler
from urllib import parse

print("=====================================================================")
print("开始启动人工智能吟美！")
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(filename)s %(name)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(f"./logs/log_{today}.txt")])
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
mode=int(input("1.b站直播间 2.api web：") or "2")

#代理
proxies = {"http": "socks5://127.0.0.1:10806", "https": "socks5://127.0.0.1:10806"}
duckduckgo_proxies="socks5://127.0.0.1:10806"

#线程锁
create_song_lock = threading.Lock()
play_song_lock = threading.Lock()
say_lock = threading.Lock()
# ============= LLM参数 =====================
QuestionList = queue.Queue()  # 定义问题 用户名 回复 播放列表 四个先进先出队列
QuestionName = queue.Queue()
AnswerList = queue.Queue()
MpvList = queue.Queue()
EmoteList = queue.Queue()
LogsList = queue.Queue()
ReplyTextList = queue.Queue()
history = []
is_ai_ready = True  # 定义ai回复是否转换完成标志
is_tts_ready = True  # 定义语音是否生成完成标志
is_mpv_ready = True  # 定义是否播放完成标志
AudioCount = 0
SayCount = 0
enable_history = False  # 是否启用记忆
history_count = 2  # 定义最大对话记忆轮数,请注意这个数值不包括扮演设置消耗的轮数，只有当enable_history为True时生效
enable_role = False  # 是否启用扮演模式
# ============================================

# ============= 本地模型加载 =====================
is_local_llm = int(input("是否使用本地LLM模型(1.是 0.否): ") or "0")
tgwUrl = "192.168.2.58:5000"
if is_local_llm == 1:
    # AI基础模型路径
    model_path = "ChatGLM2/THUDM/chatglm2-6b"
    # 训练模型路径
    checkpoint_path = ("LLaMA-Factory/saves/ChatGLM2-6B-Chat/lora/yinmei-20231123-ok-last")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    # 导入chatglm 你可以换你喜欢的版本模型. 量化int8： .quantize(8)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).cuda()
    # lora加载训练模型
    model = PeftModel.from_pretrained(
        model,
        checkpoint_path,
    )
    model = model.merge_and_unload()
    model = model.eval()
# ============================================

# ============= 绘画参数 =====================
drawUrl = "192.168.2.58:7860"
is_drawing = 3  # 1.绘画中 2.绘画完成 3.绘画任务结束
width = 730  # 图片宽度
height = 470  # 图片高度
CameraOutList = queue.Queue()  # 输出图片队列
DrawQueueList = queue.Queue()  # 画画队列
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
    sessdata="1ced502b%2C1723631629%2C623dc%2A22CjA6SgwQcp5ff3r6qVhmtETy4JKuQHW9awMPfcWEW7X8JVfZNJIUIkFD10Ipab4a85gSVkppaEkycEZURXZVY3AtWUQ0NkVTb3pBRms5Yy0tTnlycXp2UnJtNEpMTXhIZjRzeThvaERZRWxsU05GVVRTRmpxQ0hqeG44VEt1UlFzV1p5eFBjdFZBIIEC",
    buvid3="C08180D1-DDCD-1766-0162-FB77DF0BDAE597566infoc",
    bili_jct="697ca0da24de503645c90a4f70856271",
    dedeuserid="333472479",
)
room_id = int(input("输入你的B站直播间编号: ") or "31814714")  # 输入直播间编号
room = live.LiveDanmaku(room_id, credential=cred)  # 连接弹幕服务器
sender = live.LiveRoom(room_id, credential=cred)  # 用来发送弹幕
# 自己的UID 可以手动填写也可以根据直播间号获取
my_uid = sync(sender.get_room_info())["room_info"]["uid"]
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
filterCh="屁股,奶子,乳房,乳胶,劈叉,走光,女优,男优,嫖娼,淫荡,性感,性爱,做爱,裸体,赤裸,肛门"
progress_limit=1   #绘图大于多少百分比进行鉴黄
nsfw_limit=0.2  #nsfw黄图值大于多少进行绘画屏蔽，值越大越是黄图
nsfw_progress_limit=0.2 #nsfw黄图-绘画进度鉴黄
nsfw_lock = threading.Lock()
# ============================================

print("--------------------")
print("AI虚拟主播-启动成功！")
print("--------------------")

# 用户进入直播间
@room.on("INTERACT_WORD")
async def in_liveroom(event):
    print(event)
    user_name = event["data"]["data"]["uname"]  # 获取用户昵称
    time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    print(f"{time1}:粉丝\033[36m[{user_name}]\033[0m进入了直播间")
    # 直接放到语音合成处理
    # tts_say(f"欢迎{user_name}来到吟美的直播间")
    # wenhou=[f"{user_name}，恭喜发财，龙年大吉",f"{user_name}，2024年是青龙守财库哦，守住自己的钱包",
    #         f"{user_name}，进来直播间把你的钱包交给我",
    #         f"{user_name}，来吧，交出你的利是钱，不然休想走出直播间",
    #         f"{user_name}，你来到吟美的直播间，2024年一定发大财",
    #         f"{user_name}，吟美祝你2024年美梦成真，找到你的另一半",
    #         f"{user_name}，吟美祝你2024年心想事成，如如得水"]
    # wenhou_num = random.randrange(0, len(wenhou))
    #tts_say(wenhou[wenhou_num])
    
    #判断游客的不进行绘画
    text = ["bili"]
    num = is_array_contain_string(text, user_name)
    if num==0:
        # 进入直播间根据用户名绘图
        draw_json = {"prompt": user_name, "username": user_name}
        # 加入绘画队列
        DrawQueueList.put(draw_json)

# B站弹幕处理
@room.on("DANMU_MSG")  # 弹幕消息事件回调函数
async def input_msg(event):
    # 发送者UID
    uid = event["data"]["info"][2][0]
    # 排除自己发送的弹幕
    if uid == my_uid:
        return
    
    query = event["data"]["info"][1]  # 获取弹幕内容
    user_name = event["data"]["info"][2][1]  # 获取用户昵称
    msg_deal(query,user_name)

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

# http接口处理
@app.route("/msg", methods=["POST"])
def input_msg():
    data = request.json
    query = data["msg"]  # 获取弹幕内容
    user_name = data["username"]  # 获取用户昵称
    msg_deal(query,user_name)
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
    str = "({\"status\": \""+status+"\",\"content\": \""+text+"\"})"
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

def msg_deal(query,user_name):
    """
    处理弹幕消息
    """
    global QuestionList
    global QuestionName
    global LogsList

    query=filter(query,filterCh)
    print(f"\033[36m[{user_name}]\033[0m:{query}")  # 打印弹幕信息
    if not QuestionList.full():
        #tts_say(query)
        #命令执行
        status = cmd(query)  
        if status==1:
            print(f"执行命令：{query}")
            return
        
        # 说话不执行任务
        text = ["\\"]
        num = is_index_contain_string(text, query)  # 判断是不是需要搜索
        if num > 0:
            return
        
        # 搜索引擎查询
        text = ["查询", "查一下", "搜索"]
        num = is_index_contain_string(text, query)  # 判断是不是需要搜索
        if num > 0:
            queryExtract = query[num : len(query)]  # 提取提问语句
            print("搜索词：" + queryExtract)
            # prompt = f'帮我在答案"{searchStr}"中提取"{queryExtract}"的信息'
            # print(f"重置提问:{prompt}")
            # is_query = True
            if queryExtract=="":
               return
            text_search_json = {"prompt": queryExtract, "username": user_name}
            SearchTextList.put(text_search_json)
            return

        # 搜索图片
        text = ["搜图", "搜个图", "搜图片", "搜一下图片"]
        num = is_index_contain_string(text, query)  # 判断是不是需要搜索
        if num > 0:
            queryExtract = query[num : len(query)]  # 提取提问语句
            print("搜索图：" + queryExtract)
            if queryExtract=="":
               return
            img_search_json = {"prompt": queryExtract, "username": user_name}
            SearchImgList.put(img_search_json)
            return

        # 绘画
        text = ["画画", "画一个", "画一下", "画个"]
        num = is_index_contain_string(text, query)
        if num > 0:
            queryExtract = query[num : len(query)]  # 提取提问语句
            print("绘画提示：" + queryExtract)
            if queryExtract=="":
               return
            draw_json = {"prompt": queryExtract, "username": user_name}
            # 加入绘画队列
            DrawQueueList.put(draw_json)
            return

        # 唱歌
        text = ["唱一下", "唱一首", "唱歌"]
        num = is_index_contain_string(text, query)
        if num > 0:
            queryExtract = query[num : len(query)]  # 提取提问语句
            print("唱歌提示：" + queryExtract)
            song_json = {"prompt": queryExtract, "username": user_name}
            SongQueueList.put(song_json)
            return
        
        #询问LLM
        # QuestionName.put(user_name)  # 将用户名放入队列
        # QuestionList.put(query)  # 将弹幕消息放入队列
        # 默认画画
        # queryExtract = query[num : len(query)]  # 提取提问语句
        # print("绘画提示：" + queryExtract)
        # draw_json = {"prompt": queryExtract, "username": user_name}
        # # 加入绘画队列
        # DrawQueueList.put(draw_json)

        time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        LogsList.put(f"[{time1}] [{user_name}]：{query}")
        print("\033[32mSystem>>\033[0m已将该条弹幕添加入问题队列")
    else:
        print("\033[32mSystem>>\033[0m队列已满，该条弹幕被丢弃")

# 命令控制：优先
def cmd(query):
    global is_ai_ready
    global is_singing
    global is_creating_song
    global is_SearchImg
    global is_drawing
    global is_tts_ready
    global is_mpv_ready

    # 停止所有任务
    if query=="\\stop":
        is_singing = 2  # 1.唱歌中 2.唱歌完成
        is_creating_song = 2  # 1.生成中 2.生成完毕
        is_SearchImg = 2  # 1.搜图中 2.搜图完成
        is_drawing = 3  # 1.绘画中 2.绘画完成 3.绘图任务结束
        is_ai_ready = True  # 定义ai回复是否转换完成标志
        is_tts_ready = True  # 定义语音是否生成完成标志
        is_mpv_ready = True  # 定义是否播放完成标志
        return 1
    #下一首歌
    if query=="\\next":
        os.system('taskkill /T /F /IM song.exe')
        is_singing = 2  # 1.唱歌中 2.唱歌完成
        # is_creating_song = 2  # 1.生成中 2.生成完毕
        # is_ai_ready = True  # 定义ai回复是否转换完成标志
        return 1
    return 0

# text-generation-webui接口调用-LLM回复
# mode:instruct/chat/chat-instruct  preset:Alpaca/Winlone(自定义)  character:角色卡Rengoku/Ninya
def chat_tgw(content, character, mode, preset):
    url = f"http://{tgwUrl}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    history.append({"role": "user", "content": content})
    data = {
        "mode": mode,
        "character": character,
        "your_name": "Winlone",
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
            url, headers=headers, json=data, verify=False, timeout=60
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
    global QuestionName
    global history

    is_ai_ready = False
    prompt = QuestionList.get()
    user_name = QuestionName.get()

    # text-generation-webui
    if is_local_llm == 0:
        response = chat_tgw(prompt, "Aileen Voracious", "chat", "Winlone")
        response = response.replace("You", user_name)
    # 本地LLM
    elif is_local_llm == 1:
        response, history = model.chat(tokenizer, prompt, history=[])
    
    # 回复文本
    answer = f"回复{user_name}：{response}"
    # 加入回复列表，并且后续合成语音
    tts_say(f"{prompt}" + "," + answer)
    current_question_count = QuestionList.qsize()
    print(f"\033[31m[AI回复]\033[0m{answer}")  # 打印AI回复信息
    print(f"\033[32mSystem>>\033[0m[{user_name}]的回复已存入队列，当前剩余问题数:{current_question_count}")
    is_ai_ready = True  # 指示AI已经准备好回复下一个问题


# duckduckgo搜索引擎搜索
textSearchNum=5
def web_search(query):
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
            i = 0
            random_number = random.randrange(0, textSearchNum)
            for r in ddgs_text_gen:
                if i == random_number:
                    content = r["body"]
                    print(f"搜索内容：{content},搜索关键字:{query}")
                    break
                i = i + 1
        except Exception as e: 
            print(f"web_search信息回复异常{e}")
            logging.error(traceback.format_exc())
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
        img_text_json = SearchTextList.get()
        prompt = img_text_json["prompt"]
        username = img_text_json["username"]
        searchStr = web_search(prompt)
        out = f"回复{username}：我搜索到的内容如下：{searchStr}"
        print(out)
        tts_say(out)
        is_SearchText = 2  # 搜文完成

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
def searchimg_output_camera(img_search_json):
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
                CameraOutList.put(image)
                return 1
        return 0
    except Exception as e:
        print(f"【searchimg_output_camera】发生了异常：{e}")
        logging.error(traceback.format_exc())
        return 0


# 搜索引擎-搜图任务
def output_img_thead(img_search_json):
    global is_SearchImg
    global CameraOutList
    prompt = img_search_json["prompt"]
    username = img_search_json["username"]
    try:
        img_search_json = {"prompt": prompt, "username": username}
        # 搜索并且输出图片到虚拟摄像头
        status = searchimg_output_camera(img_search_json)
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
    response = requests.get(imgUrl)
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
    image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
    image = image[:, :, [2, 1, 0]]
    return image

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
            nsfw_stop_image()
            # 保存用户的黄图，留底观察
            img = Image.open(io.BytesIO(base64.b64decode(imgb64)))
            timestamp = time.time()
            img.save(f"./porn/{prompt}_{username}_{nsfw}_{timestamp}.jpg")
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
        tts_thread = Thread(target=tts_generate)
        tts_thread.start()

# bert-vits2语音合成
def bert_vits2(filename,text,emotion):
    save_path=f".\output\{filename}.mp3"
    text=parse.quote(text)
    response = requests.get(url=f"http://127.0.0.1:5000/voice?text={text}&model_id=0&speaker_name=珊瑚宫心海[中]&sdp_ratio=0.2&noise=0.2&noisew=0.9&length=1&language=AUTO&auto_translate=false&auto_split=true&emotion={emotion}")
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
        tts_say_do(text)
    except Exception as e:
        print(f"【tts_say】发生了异常：{e}")
        logging.error(traceback.format_exc())
    finally:
        say_lock.release()

# 直接合成语音播放
def tts_say_do(text):
    global SayCount
    filename=f"say{SayCount}"
    
    # 识别表情
    jsonstr = emote_content(text)
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
    # bert_vits2合成语音
    status = bert_vits2(filename,text,emotion)
    if status ==0:
       return

    # 输出表情
    emote_thread = Thread(target=emote_show,args=(jsonstr,))
    emote_thread.start()
    
    #输出回复字幕
    ReplyTextList.put(text)

    # 播放声音
    mpv_play(f".\output\{filename}.mp3",100)

    # 执行命令行指令
    subprocess.run(f"del /f .\output\say{SayCount}.mp3 1>nul", shell=True)
    # subprocess.run(f"del /f .\output\say{SayCount}.txt 1>nul", shell=True)
    SayCount += 1
    

# 从回复队列中提取一条，通过edge-tts生成语音对应AudioCount编号语音
def tts_generate():
    global is_tts_ready
    global AnswerList
    global MpvList
    global AudioCount
    response = AnswerList.get()
    filename=f"output{AudioCount}"

    # with open("./output/output.txt", "w", encoding="utf-8") as f:
    #     f.write(f"{response}")  # 将要读的回复写入临时文件
    # subprocess.run(
    #     f"edge-tts --voice zh-CN-XiaoxiaoNeural --rate=+20% --f .\output\output.txt --write-media .\output\{filename}.mp3 2>nul",
    #     shell=True,
    # )
    # bert_vits2合成语音
    status = bert_vits2(filename,response,"happy")
    if status ==0:
       return
    
    begin_name = response.find("回复")
    end_name = response.find("：")
    contain = response.find("来到吟美的直播")
    if contain > 0:
        # 欢迎语
        print(
            f"\033[32mSystem>>\033[0m对[{response}]的回复已成功转换为语音并缓存为output{AudioCount}.mp3"
        )
        # 表情加入:使用键盘控制VTube
        EmoteList.put(f"{response}")
    else:
        # 回复语
        name = response[begin_name + 2 : end_name]
        print(f"\033[32mSystem>>\033[0m对[{name}]的回复已成功转换为语音并缓存为output{AudioCount}.mp3")
        # 表情加入:使用键盘控制VTube
        emote = response[end_name : len(response)]
        EmoteList.put(f"{emote}")
    # 表情加入:使用键盘控制VTube
    emote = response[end_name : len(response)]
    EmoteList.put(f"{emote}")
    
    # 加入音频播放列表
    MpvList.put(AudioCount)
    AudioCount += 1
    is_tts_ready = True  # 指示TTS已经准备好回复下一个问题

# 文本识别表情内容
def emote_content(response):
    jsonstr = []
    # =========== 开心 ==============
    text = ["笑", "不错", "哈", "开心", "呵", "嘻", "画"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"happy","key":"开心","num":num})
    # =========== 招呼 ==============
    text = ["你好", "在吗", "干嘛", "名字", "欢迎", "搜"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"call","key":"招呼","num":num})
    # =========== 生气 ==============
    text = ["生气", "不理你", "骂", "臭", "打死", "可恶", "白痴", "忘记"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"angry","key":"生气","num":num})
    # =========== 尴尬 ==============
    text = ["尴尬", "无聊", "无奈", "傻子", "郁闷", "龟蛋"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"blush","key":"尴尬","num":num})
    # =========== 认同 ==============
    text = ["认同", "点头", "嗯", "哦", "女仆", "唱"]
    num = is_array_contain_string(text, response)
    if num > 0:
        jsonstr.append({"content":"approve","key":"认同","num":num})
    return jsonstr

# 表情加入:使用键盘控制VTube
def emote_show(emote_content):
    for data in emote_content:
        key = data["key"]
        num = data["num"]
        emote_thread = Thread(
            target=emote_ws, args=(num, 0.2, key)
        )
        emote_thread.start()

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
def emote_ws(num, startTime, key):
    if num > 0:
        start = round(num * startTime, 2)
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
        ws.send(data)

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


# 播放器mpv线程
def check_mpv():
    """
    若mpv已经播放完毕且播放列表中有数据 则创建一个播放音频的线程
    :return:
    """
    global is_mpv_ready
    global MpvList
    if not MpvList.empty() and is_mpv_ready:
        is_mpv_ready = False
        tts_thread = threading.Thread(target=mpv_read)
        tts_thread.start()


# 播放器mpv播放任务
def mpv_read():
    """
    按照MpvList内的名单播放音频直到播放完毕
    :return:
    """
    global MpvList
    global is_mpv_ready
    while not MpvList.empty():
        temp1 = MpvList.get()
        current_mpvlist_count = MpvList.qsize()

        #输出表情
        response = EmoteList.get()

        # 识别表情
        jsonstr = emote_content(response)
        # 输出表情
        emote_thread = Thread(target=emote_show,args=(jsonstr,))
        emote_thread.start()

        print(
            f"\033[32mSystem>>\033[0m开始播放output{temp1}.mp3，当前待播语音数：{current_mpvlist_count}"
        )
        # 播放声音
        mpv_play(f".\output\output{temp1}.mp3",100)

        # 执行命令行指令
        subprocess.run(f"del /f .\output\output{temp1}.mp3 1>nul", shell=True)
    is_mpv_ready = True


# 播放器播放
def mpv_play(song_path,volume):
    global is_mpv_ready
    while is_mpv_ready:
        # end：播放多少秒结束  volume：音量，最大100，最小0
        subprocess.run(
            f'song.exe -vo null --volume={volume} "{song_path}" 1>nul',
            shell=True,
        )
        return


# 唱歌线程
def check_sing():
    global is_singing
    global SongQueueList
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
    global is_singing
    global is_creating_song
    global SongMenuList
    is_created = 0  # 1.已经生成过 0.没有生成过 2.生成失败
    
    query = songname # 查询内容
    # =============== 开始-获取真实歌曲名称 =================
    musicJson = requests.get(url=f"http://{singUrl}/musicInfo/{songname}")
    music_json = json.loads(musicJson.text)
    id = music_json["id"]
    if id==0:
        outputTxt=f"歌库不存在《{songname}》这首歌曲哦"
        print(outputTxt)
        tts_say(outputTxt)
        return 
    songname = music_json["songName"]
    song_path = f"./output/{songname}.wav"
    # =============== 结束-获取真实歌曲名称 =================

    # =============== 开始-判断本地是否有歌 =================
    if os.path.exists(song_path):
        print(f"找到存在本地歌曲:{song_path}")
        outputTxt=f"回复{username}：吟美会唱《{songname}》这首歌曲哦"
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
        # 播报绘画
        print(f"歌曲不存在，需要生成歌曲《{songname}》")
        outputTxt=f"回复{username}：吟美需要学唱歌曲《{songname}》，请耐心等待"
        tts_say(outputTxt)
        # 其他歌曲在生成的时候等待
        while is_creating_song == 1:
            time.sleep(1)
        # 调用Ai学唱歌服务：生成歌曲
        is_created=create_song(songname,song_path,is_created,downfile)
    if is_created==2:
        print(f"生成歌曲失败《{songname}》")
        return
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
        play_song(mlist["is_created"],mlist["songname"],mlist["song_path"],mlist["username"],mlist["query"])
        # =============== 结束：播放歌曲 =================
        is_singing = 2  # 完成唱歌
        SongNowName = {} #当前播放歌单清空
        play_song_lock.release()
        
#开始生成歌曲
def create_song(songname,song_path,is_created,downfile):
    global is_creating_song
    try:
        # =============== 开始生成歌曲 =================
        create_song_lock.acquire()
        is_creating_song = 1
        # 生成歌曲接口
        jsonStr = requests.get(url=f"http://{singUrl}/append_song/{songname}")
        status_json = json.loads(jsonStr.text)
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
            searchimg_output_camera_thread = Thread(target=searchimg_output_camera,args=(img_search_json,))
            searchimg_output_camera_thread.start()
            # =============== 结束-触发搜图 =================
            # 播报唱歌文字
            tts_say(f"回复{username}：我准备唱一首歌《{songname}》")
            # 调用mpv播放器
            mpv_play(song_path,80)
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

# 匹配已生成的歌曲，并返回字节流
def check_down_song(songname):
    # 查看歌曲是否曾经生成
    status = requests.get(url=f"http://{singUrl}/status")
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
            downfile = requests.get(url=f"http://{singUrl}/get_audio/{songname}")
            return downfile, is_created
    
    return None, is_created

#翻译
def translate(text):
    with DDGS(proxies=duckduckgo_proxies, timeout=20) as ddgs:
        try:
            r = ddgs.translate(text,from_="zh-Hans", to="en")
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
                "highlightPostTag": "__/ais-highlight__",
                "highlightPreTag": "__ais-highlight__",
                "indexUid": "images_v3",
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
            if json["generationProcess"]=="txt2img" and json["nsfw"]=="None":
               hits.append(json)
        if len(hits)<=0:
           return ""
        # ===================================

        #条数处理
        count = len(hits)
        print(f"{query}>>条数：{count}")
        if count>limit:
            hits=hits[:limit]

        steps = 35
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
        answers_thread = Thread(
            target=draw, args=(draw_json["prompt"], draw_json["username"])
        )
        answers_thread.start()

# 绘画
def draw(prompt, username):
    global is_drawing
    global CameraOutList
    
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
        trans_json = translate(prompt)  #翻译
        if has_field(trans_json,"translated"):
            prompt = trans_json["translated"]
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
                prompt = f"(({prompt})),"+jsonPrompt["prompt"]+","+f"<lora:{prompt}>"
                negativePrompt = isNone(jsonPrompt["negativePrompt"])
                cfgScale = jsonPrompt["cfgScale"]
                steps = jsonPrompt["steps"]
                sampler = jsonPrompt["sampler"]
                # seed = jsonPrompt["seed"]

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
        response = requests.post(url=f"http://{drawUrl}/sdapi/v1/txt2img", json=payload)
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
        img.save(f"./porn/{drawName}_{username}_{nsfw}_{timestamp}.jpg")
        # ================= end =================

        # ============== cv2图片对象 ==============
        # 字节流转换为cv2图片对象
        image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
        image = image[:, :, [2, 1, 0]]
        # ================= end =================

        # 虚拟摄像头输出
        CameraOutList.put(image)
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
            response = requests.get(url=f"http://{drawUrl}/sdapi/v1/progress")
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
                # 字节流转换为cv2图片对象
                image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
                image = image[:, :, [2, 1, 0]]
                # 虚拟摄像头输出
                CameraOutList.put(image)
            time.sleep(1)
        elif is_drawing >= 2:
            print(f"《{prompt}》输出进度：100%")
            break    

# 鉴黄提示图片输出
def nsfw_stop_image():
    # 读取二进制字节流
    img = Image.open("./images/黄图.jpg")
    # 拉伸图片
    img = img.resize((width, height), Image.LANCZOS)
    # 字节流转换为cv2图片对象
    image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
    image = image[:, :, [2, 1, 0]]
    # 虚拟摄像头输出
    CameraOutList.put(image)

# 鉴黄
def nsfw_deal(imgb64):
    headers = {"Content-Type": "application/json"}
    data={"image_loader":"yahoo","model_weights":"data/open_nsfw-weights.npy","input_type":"BASE64_JPEG","input_image":imgb64}
    nsfw = requests.post(url=f"http://192.168.2.198:1801/input", headers=headers, json=data, verify=False, timeout=60)
    nsfwJson = nsfw.json()
    return nsfwJson

# 输出图片流到虚拟摄像头
def outCamera():
    global CameraOutList
    with pyvirtualcam.Camera(width, height, device="OBS Virtual Camera", fps=20) as cam:
        print(f"输出虚拟摄像头: {cam.device}")
        while True:
            if not CameraOutList.empty():
                image = CameraOutList.get()
                cam.send(image)
                cam.sleep_until_next_frame()
                time.sleep(1)


def main():
    # ws服务心跳包
    run_forever_thread = Thread(target=run_forever)
    run_forever_thread.start()

    # 唤起虚拟摄像头
    outCamera_thread = Thread(target=outCamera)
    outCamera_thread.start()

    if mode==1 or mode==2:
        # LLM回复
        sched1.add_job(func=check_answer, trigger="interval", seconds=1, id=f"answer", max_instances=10)
        # tts语音合成
        sched1.add_job(func=check_tts, trigger="interval", seconds=1, id=f"tts", max_instances=10)
        # MPV播放
        sched1.add_job(func=check_mpv, trigger="interval", seconds=1, id=f"mpv", max_instances=50)
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

def brun():
    sync(room.connect())
    
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
