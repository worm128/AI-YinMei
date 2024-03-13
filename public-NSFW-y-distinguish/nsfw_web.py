from flask import Flask, jsonify, request
import sys
import argparse
import tensorflow as tf
import traceback

from model import OpenNsfwModel, InputType
from image_utils import create_tensorflow_image_loader
from image_utils import create_yahoo_image_loader

import numpy as np

# ============= api web =====================
app = Flask(__name__)
# ============================================
model = OpenNsfwModel()
IMAGE_LOADER_TENSORFLOW = "tensorflow"
IMAGE_LOADER_YAHOO = "yahoo"

# http接口处理
@app.route("/input", methods=["POST"])
def input():
    data = request.get_json() # 获取JSON数据
    # print(f"data:{data}")
    image_loader=data["image_loader"]
    model_weights=data["model_weights"]
    input_type=data["input_type"]
    input_image = data["input_image"]
    # print(f"image:{input_image}")
    
    try:
        if input_image!="":
            with tf.Session() as sess:
                input_type = InputType[input_type.upper()]
                model.build(weights_path=model_weights, input_type=input_type)

                fn_load_image = None

                if input_type == InputType.TENSOR:
                    if image_loader == IMAGE_LOADER_TENSORFLOW:
                        fn_load_image = create_tensorflow_image_loader(tf.Session(graph=tf.Graph()))
                    else:
                        print(f"image_loader:{image_loader}")
                        fn_load_image = create_yahoo_image_loader()
                elif input_type == InputType.BASE64_JPEG:
                    import base64
                    #print(f"BASE64_JPEG:{input_type}")
                    fn_load_image = lambda input_image: np.array([base64.urlsafe_b64encode(base64.b64decode(input_image))])

                sess.run(tf.global_variables_initializer())

                image = fn_load_image(input_image)

                predictions = \
                    sess.run(model.predictions,
                            feed_dict={model.input: image})

                print("\tSFW score:\t{}\n\tNSFW score:\t{}".format(*predictions[0]))
                # 转换保留两位小数float
                num1 = np.float32(predictions[0][0])
                sfw = round(float(num1), 2)
                num2 = np.float32(predictions[0][1])
                nsfw = round(float(num2), 2)
                jsonStr={"status": "成功", "sfw": sfw, "nsfw": nsfw}
                print(jsonStr)
                return jsonify(jsonStr)
    except Exception as e:
        print(f"发生了异常：{e}")
        traceback.print_exc()
    jsonStr={"status": "失败"}
    return jsonify(jsonStr)

if __name__ == "__main__":
    # 开启web
    app.run(host="0.0.0.0", port=1801)