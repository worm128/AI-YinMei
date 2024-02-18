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

from io import BytesIO
from PIL import Image
from bilibili_api import live, sync, Credential
from pynput.keyboard import Key, Controller
from duckduckgo_search import DDGS
from threading import Thread
from peft import PeftModel
from transformers import AutoTokenizer, AutoModel, AutoConfig
from urllib.parse import quote
from flask import Flask, jsonify, request
from flask_apscheduler import APScheduler

print("=====================================================================")
print("开始启动人工智能吟美！")
print(
    "组成功能：LLM大语言模型+bilibili直播对接+TTS微软语音合成+MPV语音播放+VTube Studio人物模型+pynput表情控制+stable-diffusion-webui绘画"
)
print("源码地址：https://github.com/worm128/ai-yinmei")
print("开发者：Winlone")
print("=====================================================================")

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
proxies = {"http": "socks5://127.0.0.1:10806", "https": "socks5://127.0.0.1:10806"}
duckduckgo_proxies="socks5://127.0.0.1:10806"
create_song_lock = threading.Lock()
play_song_lock = threading.Lock()
app = Flask(__name__)
sched1 = APScheduler()
sched1.init_app(app)
# ============= LLM参数 =====================
QuestionList = queue.Queue(10)  # 定义问题 用户名 回复 播放列表 四个先进先出队列
QuestionName = queue.Queue(10)
AnswerList = queue.Queue()
MpvList = queue.Queue()
EmoteList = queue.Queue()
LogsList = queue.Queue()
history = []
is_ai_ready = True  # 定义ai回复是否转换完成标志
is_tts_ready = True  # 定义语音是否生成完成标志
is_mpv_ready = True  # 定义是否播放完成标志
AudioCount = 0
enable_history = False  # 是否启用记忆
history_count = 2  # 定义最大对话记忆轮数,请注意这个数值不包括扮演设置消耗的轮数，只有当enable_history为True时生效
enable_role = False  # 是否启用扮演模式
# ============================================

# ============= 本地模型加载 =====================
is_local_llm = int(input("是否使用本地LLM模型(1.是 0.否): ") or "0")
tgwUrl = "127.0.0.1:5000"
if is_local_llm == 1:
    # AI基础模型路径
    model_path = "ChatGLM2/THUDM/chatglm2-6b"
    # 训练模型路径
    checkpoint_path = (
        "LLaMA-Factory/saves/ChatGLM2-6B-Chat/lora/yinmei-20231123-ok-last"
    )
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
is_drawing = 2  # 1.绘画中 2.绘画完成
width = 730  # 图片宽度
height = 470  # 图片高度
CameraOutList = queue.Queue()  # 输出图片队列
DrawQueueList = queue.Queue()  # 画画队列
# ============================================

# ============= 搜图参数 =====================
SearchImgList = queue.Queue()
is_SearchImg = 2  # 1.搜图中 2.搜图完成
# ============================================

# ============= 唱歌参数 =====================
singUrl = "192.168.2.58:1717"
SongQueueList = queue.Queue()  # 唱歌队列
is_singing = 2  # 1.唱歌中 2.唱歌完成
is_creating_song = 2  # 1.生成中 2.生成完毕
# ============================================

# ============= Vtuber表情 =====================
def run_forever():
    ws.run_forever(ping_timeout=5)
def on_open(ws):
    auth()
ws = websocket.WebSocketApp("ws://127.0.0.1:8001",on_open = on_open)
# ============================================

print("--------------------")
print("AI虚拟主播-启动成功！")
print("--------------------")


# http接口处理
@app.route("/msg", methods=["POST"])
def input_msg():
    """
    处理消息
    """
    global QuestionList
    global QuestionName
    global LogsList

    data = request.json
    query = data["msg"]  # 获取弹幕内容
    user_name = data["username"]  # 获取用户昵称
    print(f"\033[36m[{user_name}]\033[0m:{query}")  # 打印弹幕信息
    if not QuestionList.full():
        #命令执行
        status = cmd(query)  
        if status==1:
            print(f"执行命令：{query}")
            return jsonify({"status": "成功"})
        
        # 说话不执行任务
        text = ["\\"]
        num = is_index_contain_string(text, query)  # 判断是不是需要搜索
        if num > 0:
            return jsonify({"status": "成功"})
        
        # 搜索引擎查询
        text = ["查询", "查一下", "搜索"]
        num = is_index_contain_string(text, query)  # 判断是不是需要搜索
        searchStr = ""
        if num > 0:
            queryExtract = query[num : len(query)]  # 提取提问语句
            print("搜索词：" + queryExtract)
            searchStr = web_search(queryExtract)
            if searchStr != "":
                # prompt = f'帮我在答案"{searchStr}"中提取"{queryExtract}"的信息'
                # print(f"重置提问:{prompt}")
                # is_query = True
                AnswerList.put(f"回复{user_name}：我搜索到的内容如下：{searchStr}")
                return jsonify({"status": "成功"})

        # 搜索图片
        text = ["搜图", "搜个图", "搜图片", "搜一下图片"]
        num = is_index_contain_string(text, query)  # 判断是不是需要搜索
        if num > 0:
            queryExtract = query[num : len(query)]  # 提取提问语句
            print("搜索图：" + queryExtract)
            img_search_json = {"prompt": queryExtract, "username": user_name}
            SearchImgList.put(img_search_json)
            return jsonify({"status": "成功"})

        # 绘画
        text = ["画画", "画一个", "画一下", "画个"]
        num = is_index_contain_string(text, query)
        if num > 0:
            queryExtract = query[num : len(query)]  # 提取提问语句
            print("绘画提示：" + queryExtract)
            draw_json = {"prompt": queryExtract, "username": user_name}
            # 加入绘画队列
            DrawQueueList.put(draw_json)
            return jsonify({"status": "成功"})

        # 唱歌
        text = ["唱一下", "唱一首", "唱歌", "唱"]
        num = is_index_contain_string(text, query)
        if num > 0:
            queryExtract = query[num : len(query)]  # 提取提问语句
            print("唱歌提示：" + queryExtract)
            song_json = {"prompt": queryExtract, "username": user_name}
            SongQueueList.put(song_json)
            return jsonify({"status": "成功"})
        
        #询问LLM
        QuestionName.put(user_name)  # 将用户名放入队列
        QuestionList.put(query)  # 将弹幕消息放入队列
        time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        LogsList.put(f"[{time1}] [{user_name}]：{query}")
        print("\033[32mSystem>>\033[0m已将该条弹幕添加入问题队列")
    else:
        print("\033[32mSystem>>\033[0m队列已满，该条弹幕被丢弃")
    
    return jsonify({"status": "成功"})


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
        "truncation_length": 4000,
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
        print(f"【{content}】信息回复异常{e}")
        return "我听不懂你说什么"
    assistant_message = response.json()["choices"][0]["message"]["content"]
    # history.append({"role": "assistant", "content": assistant_message})
    return assistant_message


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
        is_drawing = 2  # 1.绘画中 2.绘画完成
        is_ai_ready = True  # 定义ai回复是否转换完成标志
        is_tts_ready = True  # 定义语音是否生成完成标志
        is_mpv_ready = True  # 定义是否播放完成标志
        return 1
    #下一首歌
    if query=="\\next":
        os.system('taskkill /T /F /IM mpv.exe')
        is_singing = 2  # 1.唱歌中 2.唱歌完成
        is_creating_song = 2  # 1.生成中 2.生成完毕
        is_ai_ready = True  # 定义ai回复是否转换完成标志
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
        traceback.print_exc()
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
        print(f"ai_response发生了异常：{e}")
        traceback.print_exc()
        is_ai_ready=True

# LLM回复
def ai_response():
    """
    从问题队列中提取一条，生成回复并存入回复队列中
    :return:
    """
    global is_ai_ready
    global is_singing
    global is_creating_song
    global is_SearchImg
    global is_drawing
    global is_tts_ready
    global is_mpv_ready

    global QuestionList
    global AnswerList
    global QuestionName
    global LogsList
    global history

    global SearchImgList
    global DrawQueueList
    global SongQueueList

    query = QuestionList.get()
    user_name = QuestionName.get()
    ques = LogsList.get()
    prompt = query
    is_query = True  # 是否需要调用LLM True：需要  False：不需要

    # 询问LLM
    if is_query == True:
        # text-generation-webui
        if is_local_llm == 0:
            response = chat_tgw(prompt, "Aileen Voracious", "chat", "Winlone")
            response = response.replace("You", user_name)
        # 本地LLM
        elif is_local_llm == 1:
            response, history = model.chat(tokenizer, prompt, history=[])

    answer = f"回复{user_name}：{response}"
    # 加入回复列表，并且后续合成语音
    AnswerList.put(f"{query}" + "," + answer)
    current_question_count = QuestionList.qsize()
    print(f"\033[31m[AI回复]\033[0m{answer}")  # 打印AI回复信息
    print(
        f"\033[32mSystem>>\033[0m[{user_name}]的回复已存入队列，当前剩余问题数:{current_question_count}"
    )

    time2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("./logs.txt", "a", encoding="utf-8") as f:  # 将问答写入logs
        f.write(
            f"{ques}\n[{time2}] {answer}\n========================================================\n"
        )
    is_ai_ready = True  # 指示AI已经准备好回复下一个问题


# duckduckgo搜索引擎搜索
def web_search(query):
    content = ""
    with DDGS(proxies=duckduckgo_proxies, timeout=20) as ddgs:
        for r in ddgs.text(
            query,
            region="cn-zh",
            timelimit="d",
            backend="api",
            max_results=1,
        ):
            print("搜索内容：" + r["body"])
            content = content + r["body"]
    return content


# duckduckgo搜索引擎搜图片
def web_search_img(query):
    imageNum = 10
    imgUrl = ""
    with DDGS(proxies=duckduckgo_proxies, timeout=20) as ddgs:
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
        random_number = random.randrange(1, imageNum)
        for r in ddgs_images_gen:
            if i == random_number:
                imgUrl = r["image"]
                print(f"图片地址：{imgUrl},搜索关键字:{query}")
                break
            i = i + 1

    return imgUrl


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
def searchimg_output_camera(prompt):
    try:
        imgUrl = web_search_img(prompt)
        image = output_img(imgUrl)
        # 虚拟摄像头输出
        CameraOutList.put(image)
    except Exception as e:
        print(f"发生了异常：{e}")
        traceback.print_exc()
    return imgUrl

# 搜索引擎-搜图任务
def output_img_thead(img_search_json):
    global is_SearchImg
    global CameraOutList
    prompt = img_search_json["prompt"]
    username = img_search_json["username"]
    try:
        # 搜索并且输出图片到虚拟摄像头
        imgUrl = searchimg_output_camera(prompt)
        img_search_json2 = {"prompt": prompt, "username": username, "imgUrl": imgUrl}
        print(f"搜图内容:{img_search_json2}")
        # 加入回复列表，并且后续合成语音
        AnswerList.put(f"回复{username}：我给你搜了一张图《{prompt}》")
        time.sleep(10)  # 等待图片展示
    except Exception as e:
        print(f"发生了异常：{e}")
        traceback.print_exc()
    finally:
        print(f"{username}搜图《{prompt}》结束")


# 搜图输出虚拟摄像头
def output_img(imgUrl):
    response = requests.get(imgUrl, proxies=proxies)
    img_data = response.content
    # 读取二进制字节流
    img = Image.open(BytesIO(img_data))
    img = img.resize((width, height), Image.LANCZOS)
    # 字节流转换为cv2图片对象
    image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
    image = image[:, :, [2, 1, 0]]
    return image


# 检查LLM回复线程
def check_answer():
    """
    如果AI没有在生成回复且队列中还有问题 则创建一个生成的线程
    :return:
    """
    global is_ai_ready
    global QuestionList
    global AnswerList
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


# 从回复队列中提取一条，通过edge-tts生成语音对应AudioCount编号语音
def tts_generate():
    global is_tts_ready
    global AnswerList
    global MpvList
    global AudioCount
    response = AnswerList.get()
    with open("./output/output.txt", "w", encoding="utf-8") as f:
        f.write(f"{response}")  # 将要读的回复写入临时文件
    subprocess.run(
        f"edge-tts --voice zh-CN-XiaoxiaoNeural --rate=+20% --f .\output\output.txt --write-media .\output\output{AudioCount}.mp3 2>nul",
        shell=True,
    )  # 执行命令行指令
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


# 表情加入:使用键盘控制VTube
def emote_show(response):
    # =========== 开心 ==============
    text = ["笑", "不错", "哈", "开心", "呵", "嘻", "画"]
    emote_thread1 = Thread(
        target=emote_ws, args=(text, response,  0.2, "开心")
    )
    emote_thread1.start()
    # =========== 招呼 ==============
    text = ["你好", "在吗", "干嘛", "名字", "欢迎", "搜"]
    emote_thread2 = Thread(
        target=emote_ws, args=(text, response,  0.2, "招呼")
    )
    emote_thread2.start()
    # =========== 生气 ==============
    text = ["生气", "不理你", "骂", "臭", "打死", "可恶", "白痴", "忘记"]
    emote_thread3 = Thread(
        target=emote_ws, args=(text, response,  0.2, "生气")
    )
    emote_thread3.start()
    # =========== 尴尬 ==============
    text = ["尴尬", "无聊", "无奈", "傻子", "郁闷", "龟蛋"]
    emote_thread4 = Thread(
        target=emote_ws, args=(text, response,  0.2, "尴尬")
    )
    emote_thread4.start()
    # =========== 认同 ==============
    text = ["认同", "点头", "嗯", "哦", "女仆", "唱"]
    emote_thread5 = Thread(
        target=emote_ws, args=(text, response,  0.2, "认同")
    )
    emote_thread5.start()


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

@app.route("/emote", methods=["POST"])
def emotehttp():
    data = request.json
    text=data["text"]
    emote_thread1 = Thread(target=emote_ws,args=(text, "开心",  0.2, "开心"))
    emote_thread1.start()
    return "ok"

# ws协议：发送表情到Vtuber
def emote_ws(text, response, startTime, key):
    num = is_array_contain_string(text, response)
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
        try:
            ws.send(data)
        except Exception as e:
            print(f"emote_ws发生了异常：{e}")
            traceback.print_exc()

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

        response = EmoteList.get()
        emote_thread = Thread(target=emote_show,args=(response,))
        emote_thread.start()

        print(
            f"\033[32mSystem>>\033[0m开始播放output{temp1}.mp3，当前待播语音数：{current_mpvlist_count}"
        )
        subprocess.run(
            f"mpv.exe -vo null --volume=100 .\output\output{temp1}.mp3 1>nul",
            shell=True,
        )
        # 执行命令行指令
        subprocess.run(f"del /f .\output\output{temp1}.mp3 1>nul", shell=True)
    is_mpv_ready = True


# 播放器播放
def song_read(song_path):
    global is_mpv_ready
    while is_mpv_ready:
        # end：播放多少秒结束  volume：音量，最大100，最小0
        subprocess.run(
            f'mpv.exe -vo null --volume=60 "{song_path}" 1>nul',
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
        print(f"发生了异常：{e}")
        traceback.print_exc()
        is_singing = 2
        is_creating_song=2

# 唱歌
def sing(songname, username):
    global is_singing
    global is_creating_song
    is_created = 0  # 1.已经生成过 0.没有生成过

    # =============== 开始-获取真实歌曲名称 =================
    musicJson = requests.get(url=f"http://{singUrl}/musicInfo/{songname}")
    music_json = json.loads(musicJson.text)
    songname = music_json["songName"]
    song_path = f"./output/{songname}.wav"
    # =============== 结束-获取真实歌曲名称 =================

    # =============== 开始-判断本地是否有歌 =================
    if os.path.exists(song_path):
        print(f"找到存在本地歌曲:{song_path}")
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
        print(f"歌曲不存在，需要生成歌曲《{songname}》")
        # 其他歌曲在生成的时候等待
        while is_creating_song == 1:
            time.sleep(1)
        is_created=create_song(songname,song_path,is_created,downfile)
    # =============== 结束：如果不存在歌曲，生成歌曲 =================

    #等待播放
    print(f"等待播放{username}点播的歌曲《{songname}》：{is_singing}")
    while is_singing == 1:
        time.sleep(1)
    # =============== 开始：播放歌曲 =================
    play_song(is_created,songname,song_path,username)
    # =============== 结束：播放歌曲 =================   

#开始生成歌曲
def create_song(songname,song_path,is_created,downfile):
        global is_creating_song
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
                # 本地保存歌曲
                if downfile is not None and is_created == 1:
                    with open(song_path, "wb") as f:
                        f.write(downfile.content)
                i = i + 1
                if i >= timout:
                    break
                print(f"生成《{songname}》歌曲第[{i}]秒,生成状态:{is_created}")
                time.sleep(1)
        is_creating_song = 2
        create_song_lock.release()
        # =============== 结束生成歌曲 =================
        return is_created

# 播放歌曲
def play_song(is_created,songname,song_path,username):
    global is_singing
    play_song_lock.acquire()
    # 播放歌曲
    is_singing = 1  # 开始唱歌
    if is_created == 1:
        print(f"准备唱歌《{songname}》,播放路径:{song_path}")
        # 加入回复列表，并且后续合成语音
        AnswerList.put(f"回复{username}：我准备唱一首歌《{songname}》")
        time.sleep(3)
        # =============== 开始-触发搜图 =================
        searchimg_output_camera_thread = Thread(target=searchimg_output_camera,args=(songname,))
        searchimg_output_camera_thread.start()
        # =============== 结束-触发搜图 =================
        # 调用mpv播放器
        song_read(song_path)
    else:
        tip=f"已经跳过歌曲《{songname}》，请稍后再点播"
        print(tip)
        # 加入回复列表，并且后续合成语音
        AnswerList.put(f"回复{username}：{tip}")
    is_singing = 2  # 完成唱歌
    play_song_lock.release()

# 匹配已生成的歌曲，并返回字节流
def check_down_song(songname):
    # 查看歌曲是否曾经生成
    status = requests.get(url=f"http://{singUrl}/status")
    converted_json = json.loads(status.text)
    converted_file = converted_json["converted_file"]  # 生成歌曲硬盘文件
    is_created = 0  # 1.已经生成过 0.没有生成过
    # 优先：精确匹配文件名
    for filename in converted_file:
        if songname == filename:
            is_created = 1
            break

    if is_created == 1:
        downfile = requests.get(url=f"http://{singUrl}/get_audio/{songname}")
        return downfile, is_created
    return None, is_created

#翻译
def translate(text):
    with DDGS(proxies=duckduckgo_proxies, timeout=20) as ddgs:
        keywords = text
        r = ddgs.translate(keywords,from_="zh-Hans", to="en")
        print(f"翻译：{r}")
        return r

#提示词
def draw_prompt(query):
    url="http://meilisearch-v1-6.civitai.com/multi-search"
    headers = {"Authorization": "Bearer 102312c2b83ea0ef9ac32e7858f742721bbfd7319a957272e746f84fd1e974af"}
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
                "limit": 5,
                "offset": 0,
                "q": query,
                "sort": ["stats.commentCountAllTime:desc","stats.collectedCountAllTime:desc"]
            }
        ]
    }
    try:
        response = requests.post(
            url, headers=headers, json=payload, verify=False, timeout=60, proxies=proxies
        )
        r = response.json()
        hits = r["results"][0]["hits"]
        count = len(hits)
        steps = 35
        sampler="DPM++ SDE Karras"
        seed=-1
        cfgScale=7
        prompt=query
        negativePrompt=""
        if count>0:
            num = random.randrange(1, count)
            prompt = hits[num]["meta"]["prompt"]
            if has_field(hits[num]["meta"],"negativePrompt"):
                negativePrompt = filter(hits[num]["meta"]["negativePrompt"])
            if has_field(hits[num]["meta"],"cfgScale"):
                cfgScale = hits[num]["meta"]["cfgScale"]
            if has_field(hits[num]["meta"],"steps"):
               steps = hits[num]["meta"]["steps"]
            if has_field(hits[num]["meta"],"sampler"):
               sampler = hits[num]["meta"]["sampler"]
            if has_field(hits[num]["meta"],"seed"):
               seed = hits[num]["meta"]["seed"]
            jsonStr = {"prompt":prompt,"negativePrompt":negativePrompt,"cfgScale":cfgScale,"steps":steps,"sampler":sampler,"seed":seed}
            # print(f"C站提示词:{jsonStr}")
            return jsonStr
    except Exception as e:
        print(f"draw_prompt信息回复异常{e}")
        traceback.print_exc()
        return ""
    return ""

def filter(text):
    filterate=["\n","huge breasts","breasts","breast","naked","adult"]
    for s in filterate:
        text=text.replace(s,"")
    return text
    

def isNone(text):
    if text is None:
       return ""
    return text

def has_field(json_data, field):
    return field in json_data

# 绘画任务队列
def check_draw():
    global is_drawing
    global DrawQueueList
    if not DrawQueueList.empty() and is_drawing == 2:
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
    global AnswerList
    global CameraOutList
    
    drawName=prompt
    steps = 35
    sampler="DPM++ SDE Karras"
    seed=-1
    cfgScale=7
    negativePrompt=""
    jsonPrompt=""
    flag = 1 # 1.默认 2.特殊模型

    # 女孩
    text = ["漫画", "女"]
    num = is_index_contain_string(text, prompt)
    if num>0:
        checkpoint = "aingdiffusion_v13"
        prompt = prompt+","+f"<lora:{prompt}>"
        negativePrompt = "EasyNegative, (worst quality, low quality:1.4), [:(badhandv4:1.5):27],(nsfw:1.3)"
        flag = 2
    # 迪迦奥特曼
    text = ["迪迦", "奥特曼"]
    num = is_index_contain_string(text, prompt)
    if num>0:
        checkpoint = "chilloutmix_NiPrunedFp32Fix"
        prompt = f"{prompt},masterpiece, best quality, 1boy, alien, male focus, solo, 1boy, tokusatsu,full body, (giant), railing, glowing eyes, glowing, from below , white eyes,night,  <lora:tiga:1> ,city,building,(Damaged buildings:1.3),tiltshift,(ruins:1.4)"
        flag = 2

    # 绘画扩展提示词 {"prompt":prompt,"negativePrompt":negativePrompt,"cfgScale":cfgScale,"steps":steps,"sampler":sampler,"seed":seed}
    if flag == 1:
        trans_json = translate(prompt)  #翻译
        if has_field(trans_json,"translated"):
            prompt = trans_json["translated"]
            jsonPrompt = draw_prompt(prompt)  #C站抽取提示词
            print(f"绘画扩展提示词:{jsonPrompt}")
        # 默认模型
        checkpoint = "realvisxlV30Turbo_v30TurboBakedvae"
        if jsonPrompt!="":
            prompt = jsonPrompt["prompt"]+","+f"<lora:{prompt}>"
            negativePrompt = "breast,naked,adult,"+isNone(jsonPrompt["negativePrompt"])
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
    is_drawing = 1
    # 绘画进度
    progress_thread = Thread(target=progress)
    progress_thread.start()
    # 生成绘画
    response = requests.post(url=f"http://{drawUrl}/sdapi/v1/txt2img", json=payload)
    is_drawing = 2
    r = response.json()
    # 读取二进制字节流
    img = Image.open(io.BytesIO(base64.b64decode(r["images"][0])))
    img = img.resize((width, height), Image.LANCZOS)
    # 字节流转换为cv2图片对象
    image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
    image = image[:, :, [2, 1, 0]]
    # 虚拟摄像头输出
    CameraOutList.put(image)
    # 加入回复列表，并且后续合成语音
    AnswerList.put(f"回复{username}：我给你画了一张画《{drawName}》")


# 图片生成进度
def progress():
    global is_drawing
    time.sleep(0.3)
    while True:
        # 绘画中：输出进度图
        if is_drawing == 1:
            # stable-diffusion绘图进度
            response = requests.get(url=f"http://{drawUrl}/sdapi/v1/progress")
            r = response.json()
            imgstr = r["current_image"]
            if imgstr != "" and imgstr is not None:
                print(f"输出进度：" + str(round(r["progress"] * 100, 2)) + "%")
                # 读取二进制字节流
                img = Image.open(io.BytesIO(base64.b64decode(imgstr)))
                # 拉伸图片
                img = img.resize((width, height), Image.LANCZOS)
                # 字节流转换为cv2图片对象
                image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
                image = image[:, :, [2, 1, 0]]
                # 虚拟摄像头输出
                CameraOutList.put(image)
            time.sleep(1)
        # 绘画完成：退出
        elif is_drawing == 2:
            print(f"输出进度：100%")
            break


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
    # LLM回复
    sched1.add_job(func=check_answer, trigger="interval", seconds=1, id=f"answer", max_instances=4)
    # tts语音合成
    sched1.add_job(func=check_tts, trigger="interval", seconds=1, id=f"tts", max_instances=4)
    # MPV播放
    sched1.add_job(func=check_mpv, trigger="interval", seconds=1, id=f"mpv", max_instances=4)
    # 绘画
    sched1.add_job(func=check_draw, trigger="interval", seconds=1, id=f"draw", max_instances=4)
    # 搜图
    sched1.add_job(func=check_img_search, trigger="interval", seconds=1, id=f"img_search", max_instances=4)
    # 唱歌
    sched1.add_job(func=check_sing, trigger="interval", seconds=1, id=f"sing", max_instances=4)
    sched1.start()
    # 开启web
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
            "pluginName": "Cheers Bot",
            "pluginDeveloper": "winlone",
            "authenticationToken": "7dc9bb48d9efdfc88c6f49e1a2fdd51fa3a396681fb882b59e373428cea32413"
        }
    }
    data=json.dumps(authstr)
    ws.send(data)

if __name__ == "__main__":
    main()
