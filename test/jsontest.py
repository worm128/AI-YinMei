import json
import requests
import re
from datetime import datetime
# draw_json = []
# draw_json.append({"prompt": "1", "username": "1"})
# draw_json.append({"prompt": "2", "username": "2"})
# draw_json.append({"prompt": "3", "username": "3"})
# print(draw_json[0]["prompt"])
# headers = {
#         'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1'
#     }
# url = "https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&lm=7&fp=result&ie=utf-8&oe=utf-8&st=-1&face=0&width=800&height=600&word=234"
# response = requests.get(url, headers=headers)
# texts = re.findall("(?<=\"thumbURL\":\")[\\S\\s]+?(?=\")", response.text)
# print(texts)

import time

timestamp = time.time()
print("当前时间戳：", timestamp)