from func.tools.singleton_mode import singleton
from threading import Thread
from func.log.default_log import DefaultLog
from func.gobal.data import DrawData
from func.gobal.data import NsfwData
from func.obs.obs_init import ObsInit
from func.tools.string_util import StringUtil

import requests
import json
import time
import io
import base64
from PIL import Image

@singleton
class NsfwCore:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    drawData = DrawData()  #绘画数据
    nsfwData = NsfwData()  #nsfw数据

    def __init__(self):
        self.obs = ObsInit().get_ws()

    # 鉴黄
    def nsfw_deal(self,imgb64):
        headers = {"Content-Type": "application/json"}
        data = {
            "image_loader": "yahoo",
            "model_weights": "data/open_nsfw-weights.npy",
            "input_type": "BASE64_JPEG",
            "input_image": imgb64,
        }
        nsfw = requests.post(
            url=f"http://{self.nsfwData.nsfw_server}/input",
            headers=headers,
            json=data,
            verify=False,
            timeout=(5, 10),
        )
        nsfwJson = nsfw.json()
        return nsfwJson

    # 图片鉴黄 返回值：1.通过 0.禁止 -1.异常
    def nsfw_fun(self, imgb64, prompt, username, retryCount, tip, nsfw_limit):
        try:
            self.nsfwData.nsfw_lock.acquire()
            nsfwJson = self.nsfw_deal(imgb64)
        except Exception as e:
            self.log.exception(f"《{prompt}》【nsfw】鉴黄{tip}发生了异常：{e}")
            return -1, -1
        finally:
            self.nsfwData.nsfw_lock.release()

        # ===============鉴黄判断====================
        self.log.info(f"《{prompt}》【nsfw】{tip}鉴黄结果:{nsfwJson}")
        status = nsfwJson["status"]
        if status == "失败":
            self.log.info(f"《{prompt}》【nsfw】【重试剩余{retryCount}次】{tip}鉴黄失败，图片不明确跳出")
            retryCount = retryCount - 1
            if retryCount > 0:
                self.nsfw_fun(imgb64, prompt, username, retryCount, tip, nsfw_limit)
            return -1, -1
        nsfw = nsfwJson["nsfw"]
        # 发现黄图
        try:
            if status == "成功" and nsfw > nsfw_limit:
                self.log.info(f"《{prompt}》【nsfw】{tip}完成，发现黄图:{nsfw},马上退出")
                # 摄像头显示禁止黄图标识
                self.obs.show_image("绘画图片", "J:\\ai\\ai-yinmei\\images\\黄图950.jpg")
                # 保存用户的黄图，留底观察
                img = Image.open(io.BytesIO(base64.b64decode(imgb64)))
                timestamp = int(time.time())
                img.save(f"./porn/{prompt}_{username}_porn_{nsfw}_{timestamp}.jpg")
                return 0, nsfw
            elif status == "成功":
                return 1, nsfw
            return -1, nsfw
        except Exception as e:
            self.log.exception(f"《{prompt}》【nsfw】鉴黄{tip}发生了异常：{e}")
            return -1, nsfw
        # ========================================================

    # 过滤特殊字符
    def str_filter(self,query):
        return StringUtil.filter(query, self.nsfwData.filterCh)