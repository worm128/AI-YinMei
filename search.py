# 搜索测试
# from duckduckgo_search import DDGS
import pyvirtualcam
import cv2
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import requests
import time
from urllib.parse import quote
from duckduckgo_search import DDGS

width = 730  # 图片宽度
height = 470  # 图片高度

proxies = {"http": "socks5://127.0.0.1:10806", "https": "socks5://127.0.0.1:10806"}

# with DDGS(proxies="socks5://localhost:10806", timeout=20) as ddgs:
#     for r in ddgs.text(
#         "明天广州天气",
#         region="cn-zh",
#         timelimit="d",
#         backend="api",
#         max_results=1,
#     ):
#         print(r["body"])

# with DDGS(proxies="socks5://localhost:10806", timeout=20) as ddgs:
#     keywords = "华为手机"
#     ddgs_videos_gen = ddgs.videos(
#         keywords,
#         region="wt-wt",
#         safesearch="off",
#         timelimit="w",
#         resolution="high",
#         duration="medium",
#         max_results=1,
#     )
#     for r in ddgs_videos_gen:
#         print(r)

with DDGS(proxies="socks5://localhost:10806", timeout=20) as ddgs:
    keywords = "华为手机"
    ddgs_images_gen = ddgs.images(
        keywords,
        region="cn-zh",
        safesearch="off",
        size=None,
        color="color",
        type_image=None,
        layout=None,
        license_image=None,
        max_results=3,
    )
    for r in ddgs_images_gen:
        print(r)

with DDGS(proxies="socks5://localhost:10806", timeout=20) as ddgs:
    keywords = '炭治郎'
    r = ddgs.translate(keywords,from_="zh-Hans", to="en")
    print(r)

# with DDGS(proxies="socks5://localhost:10806", timeout=20) as ddgs:
#     with pyvirtualcam.Camera(width, height, device="OBS Virtual Camera", fps=20) as cam:
#         print(f"输出虚拟摄像头: {cam.device}")
#         keywords = "华为"  # Ultraman Huawei phones 华为手机
#         ddgs_images_gen = ddgs.images(
#             keywords,
#             region="wt-wt",
#             safesearch="off",
#             size="Medium",
#             color="color",
#             type_image=None,
#             layout="Wide",
#             license_image=None,
#             max_results=10,
#         )
#         for r in ddgs_images_gen:
#             imgUrl = r["image"]
#             print(f"图片地址:{imgUrl},keywords:{keywords}")
#             response = requests.get(imgUrl, proxies=proxies)
#             img_data = response.content
#             # 读取二进制字节流
#             img = Image.open(BytesIO(img_data))
#             img = img.resize((width, height), Image.LANCZOS)
#             # 字节流转换为cv2图片对象
#             image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
#             # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
#             image = image[:, :, [2, 1, 0]]
#             cam.send(image)
#             cam.sleep_until_next_frame()
#             time.sleep(600)


# def baidu_search(query):
#     url = "https://www.baidu.com/s"

#     params = {"wd": query}  # 将查询关键字作为参数传入URL中

#     response = requests.get(url, params=params)

#     if response.status_code == 200:
#         return response.text
#     else:
#         print("Error occurred while searching on Baidu.")


# # 测试函数
# result = baidu_search("Python")
# print(result)
