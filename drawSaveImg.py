# 绘画保存本地硬盘
import pyvirtualcam
import cv2
import json
import requests
import io
import base64
from PIL import Image
from flask import Flask, render_template_string
import os
import numpy as np
import threading
import time

is_drawing = 0
steps = 35
width = 730  # 图片宽度
height = 460  # 图片高度


def draw(query, do):
    global is_drawing
    url = "http://127.0.0.1:7860"
    payload = {
        "prompt": query,
        "negative_prompt": "EasyNegative, (worst quality, low quality:1.4), [:(badhandv4:1.5):27],(nsfw:1.3)",
        "hr_checkpoint_name": "aingdiffusion_v13",
        "refiner_checkpoint": "aingdiffusion_v13",
        "sampler_index": "DPM++ SDE Karras",
        "steps": steps,
        "cfg_scale": 7,
        "seed": -1,
        "width": width,
        "height": height,
    }

    # stable-diffusion绘图
    is_drawing = 1
    response = requests.post(url=f"{url}/sdapi/v1/txt2img", json=payload)
    is_drawing = 2
    r = response.json()
    # 读取二进制字节流
    img = Image.open(io.BytesIO(base64.b64decode(r["images"][0])))
    img.save("./output/draw.png")


def progress():
    global is_drawing
    time.sleep(0.3)
    while True:
        # 绘画中：输出进度图
        if is_drawing == 1:
            url = "http://127.0.0.1:7860"
            # stable-diffusion绘图进度
            response = requests.get(url=f"{url}/sdapi/v1/progress")
            r = response.json()
            imgstr = r["current_image"]
            if imgstr != "" and imgstr is not None:
                print(f"输出进度：" + str(r["progress"]))
                # 读取二进制字节流
                img = Image.open(io.BytesIO(base64.b64decode(imgstr)))
                img = img.resize((width, height), Image.LANCZOS)
                img.save("./output/draw.png")
            time.sleep(1)
        # 绘画完成：退出
        elif is_drawing == 2:
            print(f"输出进度：100%")
            break


def is_index_contain_string(string_array, target_string):
    i = 0
    for s in string_array:
        i = i + 1
        if s in target_string:
            num = target_string.find(s)
            return num + len(s)
    return 0


if __name__ == "__main__":
    while True:
        query = input("输入你的问题: ")
        text = ["画画", "画一个", "画一下"]
        num = is_index_contain_string(text, query)
        if num > 0:
            queryExtract = query[num : len(query)]  # 提取提问语句
            print("搜索词：" + queryExtract)
            is_drawing = 0  # 初始化画画
            # 开始绘画
            answers_thread = threading.Thread(target=draw, args=(queryExtract, ""))
            answers_thread.start()
            # 绘画进度
            progress_thread = threading.Thread(target=progress)
            progress_thread.start()
