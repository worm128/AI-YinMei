# 绘画输出网页
import json
import requests
import io
import base64
from PIL import Image
from flask import Flask, render_template_string
import os

app = Flask(__name__)


@app.route("/img")
def index():
    url = "http://127.0.0.1:7860"
    payload = {"prompt": "puppy dog", "steps": 5}
    response = requests.post(url=f"{url}/sdapi/v1/txt2img", json=payload)
    r = response.json()
    # image = Image.open(io.BytesIO(base64.b64decode(r["images"][0])))
    # image.show()

    img_base64 = r["images"][0]
    img_url = f"data:image/jpeg;base64,{img_base64}"
    # 创建HTML页面并将图像URL设置为其src属性

    html = f"""<!DOCTYPE html>

    <html>

    <head>

    <title>OpenCV Image</title>

    </head>

    <body style="margin:0;padding:0">

    <img src="{img_url}" alt="Gray Image">

    </body>

    </html>"""

    return render_template_string(html)


if __name__ == "__main__":
    app.run()
